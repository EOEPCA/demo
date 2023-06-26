import json

import requests
from keycloak import KeycloakOpenID, KeycloakOpenIDConnection, KeycloakAdmin, KeycloakUMA, ConnectionManager, \
    urls_patterns
from keycloak.exceptions import raise_error_from_response, KeycloakGetError, KeycloakPostError
from robot.api.deco import library
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


# Useful documentation: https://www.puppeteers.net/blog/keycloak-authorization-services-rest-api-paths-and-payload/

@library
class DemoKeycloakClient:
    """Example client for Keycloak
    """

    def __init__(self, server_url, realm, admin_username, admin_password):
        """Initialise client session with provided server url, realm, admin_username, admin_password, client_id and client_secret
        """
        self.server_url = server_url
        self.realm = realm
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

    def register_resources(self, resources):
        client_id = self.resources_client.get('id')
        for resource in resources:
            response = self.keycloak_admin.create_client_authz_resource(client_id=client_id, payload=resource,
                                                                        skip_exists=True)
            print('Created resource:\n' + json.dumps(resource, indent=2))
            print('Response: ' + str(response))

    def __register_policy(self, policy, register_f):
        client_id = self.resources_client.get('id')
        print("Creating policy:\n" + json.dumps(policy, indent=2))
        response = register_f(client_id=client_id, payload=policy, skip_exists=True)
        print("Response: " + str(response))

    def __register_policy_send_post(self, policy_type, client_id, payload, skip_exists):
        params_path = {"realm-name": self.realm, "id": client_id}
        url = urls_patterns.URL_ADMIN_CLIENT_AUTHZ + "/policy/" + policy_type + "?max=-1"
        data_raw = self.keycloak_uma_openid.connection.raw_post(url.format(**params_path), data=json.dumps(payload))
        return raise_error_from_response(
            data_raw, KeycloakPostError, expected_codes=[201], skip_exists=skip_exists
        )

    def __register_aggregated_policy(self, client_id, payload, skip_exists):
        self.__register_policy_send_post("aggregate", client_id, payload, skip_exists)

    def register_aggregated_policy(self, name, policies, strategy):
        # strategy: UNANIMOUS | AFFIRMATIVE | CONSENSUS
        if not isinstance(policies, list):
            policies = [policies]
        policy = {
            "type": "aggregate",
            "logic": "POSITIVE",
            "decisionStrategy": strategy,
            "name": name,
            "policies": policies,
            "description": ""
        }
        self.__register_policy(policy, self.__register_aggregated_policy)

    def register_client_policy(self, policy):
        self.__register_policy(policy, self.keycloak_admin.create_client_authz_client_policy)

    def __register_client_scope_policy(self, client_id, payload, skip_exists):
        self.__register_policy_send_post("client-scope", client_id, payload, skip_exists)

    def register_client_scope_policy(self, policy):
        self.__register_policy(policy, self.__register_client_scope_policy)

    def __register_group_policy(self, client_id, payload, skip_exists):
        self.__register_policy_send_post("group", client_id, payload, skip_exists)

    def register_group_policy(self, name, groups, groups_claim):
        # groups: [{"id": str, "path": str}]
        policy = {
            "type": "group",
            "logic": "POSITIVE",
            "decisionStrategy": "UNANIMOUS",
            "name": name,
            "groups": groups,
            "groupsClaim": groups_claim,
            "description": ""
        }
        self.__register_policy(policy, self.__register_group_policy)

    def __register_regex_policy(self, client_id, payload, skip_exists):
        self.__register_policy_send_post("regex", client_id, payload, skip_exists)

    def register_regex_policy(self, name, regex, target_claim):
        policy = {
            "type": "regex",
            "logic": "POSITIVE",
            "decisionStrategy": "UNANIMOUS",
            "name": name,
            "pattern": regex,
            "targetClaim": target_claim,
            "description": ""
        }
        self.__register_policy(policy, self.__register_regex_policy)

    def register_role_policy(self, name, roles):
        if not isinstance(roles, list):
            roles = [roles]
        policy = {
            "type": "role",
            "logic": "POSITIVE",
            "decisionStrategy": "UNANIMOUS",
            "name": name,
            "roles": [
                {
                    "id": role,
                    "required": False
                } for role in roles
            ]
        }
        self.__register_policy(policy, self.keycloak_admin.create_client_authz_role_based_policy)

    def __register_time_policy(self, client_id, payload, skip_exists):
        self.__register_policy_send_post("time", client_id, payload, skip_exists)

    def register_time_policy(self, name, time):
        # time can be one of:
        # "notAfter":"1970-01-01 00:00:00"
        # "notBefore":"1970-01-01 00:00:00"
        # "dayMonth":<day-of-month>
        # "dayMonthEnd":<day-of-month>
        # "month":<month>
        # "monthEnd":<month>
        # "year":<year>
        # "yearEnd":<year>
        # "hour":<hour>
        # "hourEnd":<hour>
        # "minute":<minute>
        # "minuteEnd":<minute>
        policy = {
            "type": "time",
            "logic": "POSITIVE",
            "decisionStrategy": "UNANIMOUS",
            "name": name,
            "description": ""
        }
        policy.update(time)
        self.__register_policy(policy, self.__register_time_policy)

    def __register_user_policy(self, client_id, payload, skip_exists):
        self.__register_policy_send_post("user", client_id, payload, skip_exists)

    def register_user_policy(self, name, users):
        if not isinstance(users, list):
            users = [users]
        policy = {
            "type": "user",
            "logic": "POSITIVE",
            "decisionStrategy": "UNANIMOUS",
            "name": name,
            "users": users,
            "description": ""
        }
        self.__register_policy(policy, self.__register_user_policy)

    def assign_resources_permissions(self, permissions):
        if not isinstance(permissions, list):
            permissions = [permissions]
        client_id = self.resources_client.get('id')
        for permission in permissions:
            response = self.keycloak_admin.create_client_authz_resource_based_permission(client_id=client_id,
                                                                                         payload=permission,
                                                                                         skip_exists=True)
            print("Creating resource permission: " + json.dumps(permission, indent=2))
            print("Response: " + str(response))

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

    def get_user_token(self, username="", password=""):
        """Gets a user token using username/password authentication.
        """
        return self.keycloak_admin_openid.token(username, password, scope="openid profile")

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

    def get_resource_id(self, name: str = "",
                        exact_name: bool = False,
                        uri: str = "",
                        owner: str = "",
                        resource_type: str = "",
                        scope: str = "",
                        first: int = 0,
                        maximum: int = -1, ) -> [str]:
        """Gets a resource id from attributes
        """
        return self.keycloak_uma.resource_set_list_ids(name=name, exact_name=exact_name, uri=uri, owner=owner,
                                                       resource_type=resource_type, scope=scope, first=first,
                                                       maximum=maximum)

    def create_permission_ticket(self, resources: [str]):
        payload = [
            {"resource_id": resource} for resource in resources
        ]
        data = self.keycloak_uma.connection.raw_post(
            f"https://keycloak.develop.eoepca.org/realms/{self.realm}/authz/protection/permission",
            data=json.dumps(payload)
        )
        return raise_error_from_response(data, KeycloakPostError)

    def get_rpt(self, access_token, ticket):
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