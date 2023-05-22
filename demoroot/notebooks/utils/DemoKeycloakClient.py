import json
from typing import Iterable

import requests
from keycloak import KeycloakOpenID, KeycloakOpenIDConnection, KeycloakAdmin, KeycloakUMA, ConnectionManager, \
    urls_patterns
from keycloak.exceptions import raise_error_from_response, KeycloakGetError, KeycloakPostError
from keycloak.uma_permissions import UMAPermission
from robot.api.deco import library
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


@library
class DemoKeycloakClient:
    """Example client for Keycloak
    """

    def __init__(self, server_url, realm, admin_username, admin_password):
        """Initialise client session with provided server url, realm, admin_username, admin_password, client_id and client_secret
        """
        self.server_url = server_url
        self.realm = realm
        self.session = requests.Session()
        self.session.verify = False
        self.debug_flow = False
        self.debug_requests = True
        openid_connection = KeycloakOpenIDConnection(
            server_url=server_url,
            username=admin_username,
            password=admin_password,
            realm_name=realm,
            verify=True)
        self.keycloak_admin = KeycloakAdmin(connection=openid_connection)
        self.admin_client = self.__create_admin_client()
        self.resources_client = self.__create_resources_client()
        openid_connection = KeycloakOpenIDConnection(
            server_url=server_url,
            realm_name=realm,
            username=admin_username,
            password=admin_password,
            client_id=self.admin_client.get('clientId'),
            client_secret_key=self.admin_client.get('secret'),
            verify=True)
        self.keycloak_admin = KeycloakAdmin(connection=openid_connection)
        self.keycloak_admin_openid = KeycloakOpenID(server_url=server_url,
                                                    realm_name=realm,
                                                    client_id=self.admin_client.get('clientId'),
                                                    client_secret_key=self.admin_client.get('secret'))
        self.keycloak_uma = KeycloakUMA(connection=KeycloakOpenIDConnection(
            server_url=server_url,
            realm_name=realm,
            username=admin_username,
            password=admin_password,
            client_id=self.resources_client.get('clientId'),
            client_secret_key=self.resources_client.get('secret'),
            verify=True))
        self.keycloak_uma_openid = KeycloakOpenID(server_url=server_url,
                                                  realm_name=realm,
                                                  client_id=self.resources_client.get('clientId'),
                                                  client_secret_key=self.resources_client.get('secret'))

    def register_resources(self):
        client_id = self.resources_client.get('id')
        resources = [
            {
                'name': 'Protected Resource',
                'icon_uri': '/protected/*',
            },
            {
                "name": "Premium Resource",
                "uri": "/protected/premium/*"
            },
            {
                "name": "Default Resource",
                "uri": "/*"
            },
            {
                "name": "User Resource",
                "type": "user-resource"
            }
        ]
        for resource in resources:
            response = self.keycloak_admin.create_client_authz_resource(client_id=client_id, payload=resource,
                                                                        skip_exists=True)
            print('Created resource:\n' + json.dumps(resource, indent=2))
            print('Response: ' + str(response))

    def register_policies(self):
        client_id = self.resources_client.get('id')
        roles_policies = [
            {
                "name": "Default Policy",
                "description": "A policy that grants access only for users within this realm",
                "type": "role",
                "logic": "POSITIVE",
                "decisionStrategy": "AFFIRMATIVE",
                "roles": [
                    {
                        "id": "user",
                        "required": False
                    }
                ]
            },
            {
                "name": "Only Premium User Policy",
                "type": "role",
                "logic": "POSITIVE",
                "decisionStrategy": "UNANIMOUS",
                "roles": [
                    {
                        "id": "user-premium",
                        "required": False
                    }
                ]
            },
            {
                "name": "Only User Policy",
                "type": "role",
                "logic": "POSITIVE",
                "decisionStrategy": "UNANIMOUS",
                "roles": [
                    {
                        "id": "user",
                        "required": False
                    }
                ]
            },
        ]

        for policy in roles_policies:
            print("Creating policy:\n" + json.dumps(policy, indent=2))
            response = self.keycloak_admin.create_client_authz_role_based_policy(client_id=client_id, payload=policy,
                                                                                 skip_exists=True)
            print("Response: " + str(response))

    def assign_resources_permissions(self):
        client_id = self.resources_client.get('id')
        resources_permissions = [
            {
                "name": "Default Resource Permission",
                "type": "resource",
                "logic": "POSITIVE",
                "decisionStrategy": "UNANIMOUS",
                "resources": [
                    "Default Resource"
                ],
                "policies": [
                    "Default Policy"
                ]
            },
            {
                "name": "Premium Resource Permission",
                "type": "resource",
                "logic": "POSITIVE",
                "decisionStrategy": "UNANIMOUS",
                "resources": [
                    "Premium Resource"
                ],
                "policies": [
                    "Only Premium User Policy"
                ]
            },
            {
                "name": "Protected Resource Permission",
                "type": "resource",
                "logic": "POSITIVE",
                "decisionStrategy": "UNANIMOUS",
                "resources": [
                    "Protected Resource"
                ],
                "policies": [
                    "Only User Policy"
                ]

            }
        ]

        for permission in resources_permissions:
            response = self.keycloak_admin.create_client_authz_resource_based_permission(client_id=client_id,
                                                                                         payload=permission,
                                                                                         skip_exists=True)
            print("\n Creating resource permission: " + json.dumps(permission, indent=2))
            print("\nResponse: " + str(response))

    def create_user(self, username, password, realm_roles) -> str:
        payload = {
            "username": username,
            "realmRoles": realm_roles,
            "enabled": True
        }
        user_id = self.keycloak_admin.create_user(payload, exist_ok=True)
        print('Created user: ' + str(user_id))
        self.keycloak_admin.set_user_password(user_id, password, temporary=False)
        return user_id

    def get_client_credentials(self) -> (str, str):
        """Returns the client credentials (client_id/secret)

        Performs client registration if needed.
        """
        if "client_id" not in self.state:
            self.register_client()
        return self.state["client_id"], self.state["client_secret"]

    def get_user_token(self, username, password, openid):
        """Gets a user token using username/password authentication.
        """
        return openid.token(username, password, scope="openid profile")

    def generate_protection_pat(self):
        """Generate a personal access token
        """
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.resources_client.get('clientId'),
            "client_secret": self.resources_client.get('secret'),
        }
        connection = ConnectionManager(self.keycloak_uma.connection.base_url)
        connection.add_param_headers("Content-Type", "application/x-www-form-urlencoded")
        data_raw = connection.raw_post(self.keycloak_uma.uma_well_known["token_endpoint"], data=payload)
        return raise_error_from_response(data_raw, KeycloakPostError)

    def get_resource_id_from_name(self, name) -> [str]:
        """Gets a resource id from name
        """
        return self.keycloak_uma.resource_set_list_ids(name=name, exact_name=True)

    def get_resource_id_from_uri(self, uri) -> [str]:
        """Gets a resource id from uri
        """
        return self.keycloak_uma.resource_set_list_ids(uri=uri, exact_name=True)

    def create_permission_ticket(self, resources: [str]):
        payload = [
            {"resource_id": resource} for resource in resources
        ]
        data = self.keycloak_uma.connection.raw_post(
            f"https://keycloak.develop.eoepca.org/realms/{self.realm}/authz/protection/permission",
            data=json.dumps(payload)
        )
        return raise_error_from_response(data, KeycloakPostError)

    def get_uma_token(self, access_token, ticket):
        payload = {
            "claim_token_format": "http://openid.net/specs/openid-connect-core-1_0.html#IDToken",
            "grant_type": "urn:ietf:params:oauth:grant-type:uma-ticket",
            "claim_token": access_token,
            "ticket": ticket,
            "client_id": self.resources_client.get('clientId'),
            "client_secret": self.resources_client.get('secret')
        }
        params_path = {
            "realm-name": self.realm
        }
        connection = ConnectionManager(self.keycloak_uma.connection.base_url)
        connection.add_param_headers("Content-Type", "application/x-www-form-urlencoded")
        data = connection.raw_post(urls_patterns.URL_TOKEN.format(**params_path), data=payload)
        return raise_error_from_response(data, KeycloakPostError)

    def get_user_id(self, username) -> str:
        return self.keycloak_admin.get_user_id(username)

    def create_realm_role(self, role: str) -> str:
        payload = {
            "name": role,
            "clientRole": False
        }
        return self.keycloak_admin.create_realm_role(payload=payload, skip_exists=True)

    def assign_realm_role_to_user(self, user_id: str, role: str):
        role = self.keycloak_admin.get_realm_role(role)
        print('\nAssigning role to user ' + user_id + ':\n' + json.dumps(role, indent=2))
        self.keycloak_admin.assign_realm_roles(user_id=user_id, roles=[role])

    def create_client_role(self, client_id: str, role: str) -> str:
        payload = {
            "name": role,
            "clientRole": True
        }
        return self.keycloak_admin.create_client_role(client_role_id=client_id, payload=payload, skip_exists=True)

    def __create_admin_client(self):
        payload = {
            'clientId': 'admin-demo',
            'serviceAccountsEnabled': True,
            'directAccessGrantsEnabled': True,
            'authorizationServicesEnabled': True
        }
        client_id = self.keycloak_admin.create_client(payload=payload, skip_exists=True)
        client = self.keycloak_admin.get_client(client_id)
        print('Created admin client:\n' + json.dumps(client, indent=2))
        user = self.__get_service_account_user(client.get('id'))
        user_id = user.get('id')
        print('\nCreated service account user:\n' + json.dumps(user, indent=2))
        self.assign_realm_role_to_user(user_id, 'admin')
        return client

    def __create_resources_client(self):
        payload = {
            'clientId': 'resources-demo',
            'secret': 'secret',
            'serviceAccountsEnabled': True,
            'directAccessGrantsEnabled': True,
            'authorizationServicesEnabled': True,
            'authorizationSettings': {
                'allowRemoteResourceManagement': True,
                'policyEnforcementMode': 'ENFORCING'
            },
            "bearerOnly": False,
            'adminUrl': 'http://localhost:8080',
            'baseUrl': 'http://localhost:8080',
            'redirectUris': [
                'http://localhost:8080/*'
            ]
        }
        client_id = self.keycloak_admin.create_client(payload=payload, skip_exists=True)
        client = self.keycloak_admin.get_client(client_id)
        print('\nCreated resources client:\n' + json.dumps(client, indent=2))
        user = self.__get_service_account_user(client.get('id'))
        print('\nCreated service account user:\n' + json.dumps(user, indent=2))
        role = self.create_client_role(client_id=client_id, role="uma_protection")
        print('\nAssigned role to resources client:\n' + str(role))

        return client

    def __get_service_account_user(self, client_id):
        data_raw = self.keycloak_admin.connection.raw_get(
            self.server_url + '/admin/realms/' + self.realm + '/clients/' + client_id + '/service-account-user')
        return raise_error_from_response(data_raw, KeycloakGetError)

    def __trace(self, prefix, message):
        """Debug function to log a trace of execution flow (e.g. for UMA flow)
        """
        if self.debug_flow:
            print(f"[{prefix}] {message}")

    def __http_request(self, method, url, **kwargs):
        """Wrapper for requests.session.request() to optionally include logging of the request details
        """
        if self.debug_requests:
            print(f"[Request] {method} => {url}")
        return self.session.request(method, url, **kwargs)