import json
import requests
from keycloak import KeycloakOpenID, KeycloakOpenIDConnection, KeycloakAdmin
from keycloak.exceptions import raise_error_from_response, KeycloakGetError
from robot.api.deco import library, keyword
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
        keycloak_admin_connection = KeycloakOpenIDConnection(
            server_url=server_url,
            username=admin_username,
            password=admin_password,
            realm_name=realm,
            verify=True)
        keycloak_admin = KeycloakAdmin(connection=keycloak_admin_connection)
        self.client = self.__create_client(keycloak_admin)
        keycloak_admin_connection = KeycloakOpenIDConnection(
            server_url=server_url,
            realm_name=realm,
            username=admin_username,
            password=admin_password,
            client_id=self.client.get('clientId'),
            client_secret_key=self.client.get('secret'),
            verify=True)
        self.keycloak_admin = KeycloakAdmin(connection=keycloak_admin_connection)
        self.keycloak_openid = KeycloakOpenID(server_url=server_url,
                                              realm_name=realm,
                                              client_id=self.client.get('clientId'),
                                              client_secret_key=self.client.get('secret'))

    def __create_client(self, keycloak_admin):
        payload = {
            'clientId': 'demo',
            'serviceAccountsEnabled': True,
            'directAccessGrantsEnabled': True
        }
        client_id = keycloak_admin.create_client(payload=payload, skip_exists=True)
        client = keycloak_admin.get_client(client_id)
        print('> Created client:\n' + str(client))
        user = self.__get_service_account_user(keycloak_admin, client.get('id'))
        user_id = user.get('id')
        print('> Created service account user:\n' + str(user))
        role = keycloak_admin.get_realm_role('admin')
        print('> Assigning admin role to service account user:\n' + str(role))
        keycloak_admin.assign_realm_roles(user_id=user_id, roles=[role])
        return client


    def __get_service_account_user(self, keycloak_admin, clientId):
        data_raw = keycloak_admin.connection.raw_get(self.server_url + '/admin/realms/' + self.realm + '/clients/' + clientId + '/service-account-user')
        return raise_error_from_response(data_raw, KeycloakGetError)

    def trace(self, prefix, message):
        """Debug function to log a trace of execution flow (e.g. for UMA flow)
        """
        if self.debug_flow:
            print(f"[{prefix}] {message}")

    def http_request(self, method, url, **kwargs):
        """Wrapper for requests.session.request() to optionally include logging of the request details
        """
        if self.debug_requests:
            print(f"[Request] {method} => {url}")
        return self.session.request(method, url, **kwargs)

    # ---------------------------------------------------------------------------
    # USER MANAGEMENT
    # ---------------------------------------------------------------------------

    @keyword(name='Create user account')
    def create_user(self, username, password):
        payload = {"username": username, "password": password, "enabled": True}
        user_id = self.keycloak_admin.create_user(payload, exist_ok=True)
        print('Created user: ' + str(user_id))
        self.keycloak_admin.set_user_password(user_id, password, temporary=False)

    @keyword(name='Get Client Credentials')
    def get_client_credentials(self):
        """Returns the client credentials (client_id/secret)

        Performs client registration if needed.
        """
        if not "client_id" in self.state:
            self.register_client()
        return self.state["client_id"], self.state["client_secret"]

    @keyword(name='Get User Token')
    def get_user_token(self, username, password):
        """Gets a user token using username/password authentication.
        """
        return self.keycloak_openid.token(username, password, scope="profile")

    # ---------------------------------------------------------------------------
    # Dummy Service
    # ---------------------------------------------------------------------------

    # @keyword(name='Dummy Service Call')
    # def call_dummy_service(self, service_base_url, id_token=None, access_token=None):
    #     """Call the 'Dummy Service' endpoint
    #     """
    #     headers = {"Accept": "application/json"}
    #     r, access_token = self.uma_http_request("GET", service_base_url, headers=headers, id_token=id_token,
    #                                             access_token=access_token)
    #     print(f"[Dummy Service] = {r.status_code} ({r.reason})")
    #     return r, access_token