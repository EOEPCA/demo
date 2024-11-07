import requests
import time
#import webbrowser

def exec_device_flow(keycloak_url : str, client_id : str, client_secret : str = None, realm : str = "eoepca"):
    """Initiates a Device authentication flow and waits for it to complete.

    This method initiates a device flow and prints out the login URL.
    It then expects a user to log into Keycloak via that URL.
    When a user has logged in, the method returns a corresponding token.
    Waiting is performed by polling the token endpoint every 10 seconds.
    It times out when the login URL expires or after 3 minutes, whichever occurs first.

    :param keycloak_url: the base URL of the Keycloak service to use
    :param client_id: the ID of the client for which the login is performed
    :param client_secret: the client secret; may be omitted if the client is public
    :param realm: the realm name
    :return: a structure containing the resulting access token, accompanied by a refresh token and metadata
    """
    params = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    base_url = keycloak_url + "/realms/" + realm + "/protocol/openid-connect/"
    auth_url = base_url + "auth/device"
    response = requests.post(auth_url, data=params)
    resp_json = response.json()
    device_code = resp_json["device_code"]
    verification_uri = resp_json["verification_uri_complete"]
    expires_in = resp_json["expires_in"]
    if expires_in > 180:
        expires_in = 180
    print("Please open this URI to log in: " + verification_uri)
    #webbrowser.open(verification_uri);
    params["device_code"] = device_code
    params["grant_type"] = "urn:ietf:params:oauth:grant-type:device_code"
    token_url = base_url + "token"
    while expires_in > 0:
        time.sleep(10)
        expires_in -= 10
        response = requests.post(token_url, data=params)
        #print(response.text)
        if "access_token" in response.json():
            return response.json()

class DeviceAuthAccount:
    """Represents a user account that uses Device flow for authentication.
    Keeps track of token expiry and triggers a token refresh or a full authentication flow when needed.
    """
    def __init__(self, keycloak_url : str, client_id : str, client_secret : str, realm : str = "eoepca", message : str = None):
        self.keycloak_url = keycloak_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.realm = realm
        self.message = message
        self.token = None
        self.token_expiry_time = 0
        self.refresh_expiry_time = 0

    def _set_token(self, token):
        cur_time = time.time()
        self.token = token
        self.token_expiry_time = cur_time + token["expires_in"] - 10
        self.refresh_expiry_time = cur_time + token["refresh_expires_in"] - 10

    def get_token(self):
        """Returns an access token.
        Internally triggers a token refresh or Device authentication flow if needed.
        In the latter case this method blocks until authentication has completed or timed out.

        :return: a valid access token
        """
        cur_time = time.time()
        if self.token is None or (cur_time > self.token_expiry_time and cur_time > self.refresh_expiry_time):
            # Log in
            print("Requesting login...")
            if (self.message is not None):
                print(self.message)
            self._set_token(exec_device_flow(self.keycloak_url, self.client_id, self.client_secret, self.realm))
        elif cur_time > self.token_expiry_time:
            # Refresh token
            print("Refreshing token...")
            params = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self.token["refresh_token"],
            }
            token_url = self.keycloak_url + "/realms/" + self.realm + "/protocol/openid-connect/token"
            response = requests.post(token_url, data=params)
            if "access_token" in response.json():
                self._set_token(response.json())
            else:
                print("Token refresh failed: " + response.text)
        return self.token["access_token"]
