"""Shared code for device login, API requests, and preview files."""

import base64
import hashlib
import io
import json
import re
import secrets
import time
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit

import requests
from dotenv import dotenv_values


# Only these fields can appear in notebook output.
PUBLIC_KEYS = (
    "ENVIRONMENT", "OIDC_ISSUER", "EOAPI_CLIENT_ID", "WORKSPACE_CLIENT_ID",
    "OIDC_SCOPE", "STAC_ENDPOINT", "WORKSPACE_API_ENDPOINT", "WORKSPACE_DATA_DOMAIN",
)


def require_value(config, key):
    value = config.get(key, "")
    if not value or "CHANGE_ME" in value:
        raise ValueError(f"Set {key} in the settings file.")
    return value


def require_https(value):
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment):
        raise ValueError("Service URLs must use HTTPS without credentials, query, or fragment.")
    return value.rstrip("/")


def load_config(path, service):
    """Load settings without substituting environment variables."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    config = dict(dotenv_values(path, interpolate=False))
    config = {key: value or "" for key, value in config.items()}
    keys = {
        "eoapi": ("EOAPI_CLIENT_ID", "STAC_ENDPOINT"),
        "workspace": ("WORKSPACE_CLIENT_ID", "WORKSPACE_API_ENDPOINT", "WORKSPACE_DATA_DOMAIN"),
    }[service]
    for key in ("ENVIRONMENT", "OIDC_ISSUER", "OIDC_SCOPE", *keys):
        require_value(config, key)
    for key in ("OIDC_ISSUER", keys[1]):
        config[key] = require_https(config[key])
    if config["OIDC_ISSUER"].endswith("/.well-known/openid-configuration"):
        raise ValueError("Set OIDC_ISSUER to the discovery document's issuer value, without /.well-known/openid-configuration.")
    return config


def print_config(config):
    print(json.dumps({key: config.get(key, "") for key in PUBLIC_KEYS}, indent=2))
    issuer = config["OIDC_ISSUER"]
    print(f"OIDC discovery: {issuer}/.well-known/openid-configuration")


def token_via_device(config, service, timeout=300):
    """Wait for the user to complete device login in the browser."""
    issuer = config["OIDC_ISSUER"]
    response = requests.get(f"{issuer}/.well-known/openid-configuration",
                            timeout=30, allow_redirects=False)
    response.raise_for_status()
    metadata = response.json()
    if metadata.get("issuer") != issuer:
        advertised_issuer = require_https(metadata.get("issuer", ""))
        raise ValueError(
            f"OIDC_ISSUER is {issuer}, but discovery reports {advertised_issuer}. "
            f"Set OIDC_ISSUER={advertised_issuer} and rerun the settings cell."
        )
    if not metadata.get("device_authorization_endpoint"):
        raise ValueError("The issuer does not advertise device login support.")
    device_endpoint = require_https(metadata["device_authorization_endpoint"])
    token_endpoint = require_https(metadata["token_endpoint"])
    client_id = config[f"{service.upper()}_CLIENT_ID"]
    # Keycloak supports PKCE for device login. Keep the verifier in memory.
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    response = requests.post(device_endpoint,
                             data={"client_id": client_id, "scope": config["OIDC_SCOPE"],
                                   "code_challenge": code_challenge,
                                   "code_challenge_method": "S256"},
                             timeout=30, allow_redirects=False)
    if response.status_code != 200:
        raise RuntimeError(f"Device login failed (HTTP {response.status_code}). Enable Device Authorization Grant for this client.")
    device = response.json()
    print(f"Open {device['verification_uri']} and enter code: {device['user_code']}")
    interval = max(1, float(device.get("interval", 5)))
    deadline = time.monotonic() + min(float(device["expires_in"]), timeout)
    while time.monotonic() + interval < deadline:
        time.sleep(interval)
        response = requests.post(token_endpoint, data={
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": client_id, "device_code": device["device_code"],
            "code_verifier": code_verifier,
        }, timeout=30, allow_redirects=False)
        if response.status_code not in (200, 400):
            raise RuntimeError(f"Device login failed (HTTP {response.status_code}).")
        result = response.json()
        error = result.get("error")
        if error == "authorization_pending":
            continue
        if error == "slow_down":
            interval += 5
            continue
        if error:
            raise RuntimeError("Device login was denied or expired. Start login again.")
        if (response.status_code != 200 or not result.get("access_token")
                or result.get("token_type", "").lower() != "bearer"):
            raise RuntimeError("The token response has no Bearer access token.")
        print("Login complete. Tokens remain in kernel memory.")
        return result
    raise TimeoutError("Device login timed out. Start login again.")


class ApiSession(requests.Session):
    """Use a request timeout and stop redirects for API calls."""

    def request(self, method, url, **kwargs):
        kwargs.setdefault("timeout", 30)
        kwargs["allow_redirects"] = False
        return super().request(method, url, **kwargs)


def workspace_data_url(domain, workspace_name):
    """Build the workspace's permanent Data URL."""
    base = urlsplit(require_https(f"https://{domain}"))
    if base.path or base.port:
        raise ValueError("WORKSPACE_DATA_DOMAIN must be a hostname.")
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", workspace_name):
        raise ValueError("The workspace name must be a DNS label.")
    return f"https://{workspace_name}.{base.hostname}"


def wait_for_data(session, data_url, timeout=600, interval=10):
    """Wait for the public Data route after storage is ready."""
    deadline = time.monotonic() + timeout
    print("Waiting for the Data endpoint...")
    while time.monotonic() < deadline:
        try:
            response = session.get(f"{data_url}/share/public/", timeout=15,
                                   allow_redirects=False)
            if response.status_code == 200:
                print("Data endpoint ready.")
                return
            # The gateway can redirect while the HTTPS route is still starting.
            if response.status_code not in {301, 404, 502, 503, 504}:
                raise RuntimeError(f"Data endpoint returned HTTP {response.status_code}.")
        except (requests.ConnectionError, requests.Timeout):
            pass
        time.sleep(min(interval, max(0, deadline - time.monotonic())))
    raise TimeoutError("Data endpoint did not become ready. Check its workload and route.")


def expect_status(response, expected):
    if response.status_code != expected:
        raise RuntimeError(f"Expected HTTP {expected}; received HTTP {response.status_code}.")
    print(f"PASS (HTTP {expected})")


def wait_for_workspace(api, url, headers, timeout=600, interval=10):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = api.get(url, headers=headers)
        response.raise_for_status()
        if response.status_code != 200:
            raise RuntimeError(f"Unexpected workspace status: HTTP {response.status_code}.")
        status = response.json().get("status")
        print(f"Workspace status: {status}")
        if status == "ready":
            return response.json()
        if status in {"failed", "error"}:
            raise RuntimeError(f"Workspace creation stopped with status: {status}.")
        time.sleep(min(interval, max(0, deadline - time.monotonic())))
    raise TimeoutError("Workspace creation did not finish. Check the workspace before you retry.")


def image_type(content):
    from PIL import Image

    with Image.open(io.BytesIO(content)) as image:
        media_type = Image.MIME.get(image.format)
        image.verify()
    if media_type not in {"image/png", "image/jpeg", "image/webp", "image/gif"}:
        raise ValueError("Unsupported preview image format.")
    return media_type


def get_shared(session, url):
    """Follow redirects without a workspace token or a browser session."""
    if urlsplit(url).scheme != "https":
        raise ValueError("Use an HTTPS download URL.")
    response = session.get(url, timeout=90, allow_redirects=True)
    if response.status_code != 200:
        raise RuntimeError(f"Download failed (HTTP {response.status_code}).")
    if any(urlsplit(hop.url).scheme != "https" for hop in [*response.history, response]):
        raise ValueError("The download left HTTPS.")
    return response


def preview_assets(rows, session):
    """Download previews and thumbnails, or report why a file was skipped."""
    extensions = {"image/png": ".png", "image/jpeg": ".jpg",
                  "image/webp": ".webp", "image/gif": ".gif"}
    for index, item in enumerate(rows):
        assets = item.get("assets") or {}
        self_url = next((link["href"] for link in item.get("links") or []
                         if link.get("rel") == "self"), None)
        refreshed = None
        refresh_failed = False
        for kind in ("rendered_preview", "thumbnail"):
            asset = assets.get(kind) or {}
            href = asset.get("href", "")
            error = "Asset is missing."
            content = None
            for attempt in range(2):
                try:
                    if attempt or not urlsplit(href).scheme:
                        if refreshed is None and self_url and not refresh_failed:
                            try:
                                refreshed = get_shared(session, self_url).json()
                            except (ValueError, RuntimeError, OSError):
                                refresh_failed = True
                        current = ((refreshed or {}).get("assets") or {}).get(kind) or {}
                        href = current.get("href") or href
                    if not href:
                        break
                    if not urlsplit(href).scheme:
                        href = urljoin(self_url or "", href)
                    content = get_shared(session, href).content
                    media_type = image_type(content)
                    break
                except (ValueError, RuntimeError, OSError) as exc:
                    content = None
                    error = str(exc) if isinstance(exc, RuntimeError) else "Cannot read the preview image."
            result = {"item": item["id"], "asset": kind}
            if content is None:
                yield {**result, "error": error}
                continue
            slug = re.sub(r"[^A-Za-z0-9_-]+", "-", str(item["id"]))[:100]
            filename = f"{index:03d}-{slug}-{kind}{extensions[media_type]}"
            yield {**result, "filename": filename, "content": content, "type": media_type}


def public_file_url(base_url, filename):
    base_url = require_https(base_url)
    return (f"{base_url.rstrip('/')}/api/public/share/public/"
            f"{quote(filename, safe='')}?presign=true&followRedirect=true")


def verify_download(response, expected_digest):
    if hashlib.sha256(response.content).hexdigest() != expected_digest:
        raise ValueError("The shared file differs from the uploaded file.")
