from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from vmware.vapi.lib.connect import get_requests_connector
from com.vmware.vcenter.identity_client import Providers
from com.vmware.vcenter.tokenservice_client import TokenExchange
from vmware.vapi.security.oauth import create_oauth_security_context
import base64
from lxml import etree
import uuid

# Constants
HTTP_ENDPOINT = "https://{}/api"
AUTHORIZATION_CODE = "authorization_code"
CLIENT_CREDENTIALS = "client_credentials"
REFRESH_TOKEN = "refresh_token"
PASSWORD = "password"
OAUTH2_CONFIG_TYPE = "oauth2"
OIDC_CONFIG_TYPE = "oidc"


def get_identity_provider(server, session):
    '''
    Get the identity provider for the given vc/server
    Sample can be found at
    https://github.com/vmware/vsphere-automation-sdk-python/blob/master/samples/vsphere/oauth/list_external_identity_providers.py
    '''
    stub_config = StubConfigurationFactory.new_std_configuration(
                                            get_requests_connector(
                                                session=session,
                                                url=HTTP_ENDPOINT.format(
                                                    server)))
    id_client = Providers(stub_config)
    providers = id_client.list()
    identity_provider = ""
    for provider in providers:
        if provider.is_default:
            identity_provider = provider
            break
    return identity_provider


def get_saml_assertion(server, session, access_token, id_token=None):
    """
    Exchange access token to saml token to connect to VC
    Sample can be found at
    https://github.com/vmware/vsphere-automation-sdk-python/blob/master/samples/vsphere/oauth/exchange_access_id_token_for_saml.py
    """
    stub_config = StubConfigurationFactory.new_std_configuration(
        get_requests_connector(
            session=session,
            url=HTTP_ENDPOINT.format(server)
        )
    )

    oauth_security_context = create_oauth_security_context(access_token)
    stub_config.connector.set_security_context(oauth_security_context)
    token_exchange = TokenExchange(stub_config)
    exchange_spec = token_exchange.ExchangeSpec(
        grant_type=token_exchange.TOKEN_EXCHANGE_GRANT,
        subject_token_type=token_exchange.ACCESS_TOKEN_TYPE,
        actor_token_type=token_exchange.ID_TOKEN_TYPE,
        requested_token_type=token_exchange.SAML2_TOKEN_TYPE,
        actor_token=id_token, subject_token=access_token)
    response = token_exchange.exchange(exchange_spec)
    saml_token = response.access_token

    # convert saml token to saml assertion
    samlAssertion = etree.tostring(
                        etree.XML(base64.decodebytes(
                            bytes(saml_token, 'utf-8')
                        ))
                    ).decode('utf-8')
    return samlAssertion


def get_endpoints(identity_provider):
    """
    Extract different ednpoints from the identity provider object
    Note that the endpoint naming convention might vary for different providers
    Currently, support is provided for
    oauth2 -> Cloud Service Provider (CSP)
    oidc -> Microssoft ADFS
    """
    if identity_provider.auth_query_params is not None:
        auth_query_params = identity_provider.auth_query_params
    else:
        auth_query_params = {}

    if identity_provider.config_tag.lower() == OAUTH2_CONFIG_TYPE:
        auth_endpoint = identity_provider.oauth2.auth_endpoint
        token_endpoint = identity_provider.oauth2.token_endpoint
        auth_query_params.update(identity_provider.oauth2.auth_query_params)
    if identity_provider.config_tag.lower() == OIDC_CONFIG_TYPE:
        auth_endpoint = identity_provider.oidc.discovery_endpoint
        token_endpoint = identity_provider.oidc.auth_endpoint
        auth_query_params.update(identity_provider.oidc.auth_query_params)
    return [auth_endpoint, token_endpoint, auth_query_params]


def get_basic_auth_string(id, secret):
    """
    Return authorization string
    """
    auth_string = id + ":" + secret
    auth_string = "Basic " + base64.b64encode(auth_string.encode()).decode()
    return auth_string


def login_using_client_credentials(server, session, client_id, client_secret):
    """
    Get access token when grant_type is client_credentials
    """
    identity_provider = get_identity_provider(server, session)
    [discovery_endpoint, token_endpoint, auth_query_params] = \
        get_endpoints(identity_provider)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': get_basic_auth_string(client_id, client_secret),
        'Accept': 'application/json'
    }
    data = {
        'grant_type': CLIENT_CREDENTIALS
    }
    response = session.post(token_endpoint, headers=headers, data=data).json()
    access_token = response['access_token']
    return get_saml_assertion(server, session, access_token)


def login_using_authorization_code(
        server,
        session,
        client_id,
        client_secret,
        redirect_uri,
        callback):
    """
    Get access token when grant_type is authorization_code
    """
    identity_provider = get_identity_provider(server, session)
    [auth_endpoint, token_endpoint, auth_query_params] = \
        get_endpoints(identity_provider)
    state = uuid.uuid1()

    auth_endpoint += "?client_id=" + client_id + "&redirect_uri=" + \
        redirect_uri + "&state=" + str(state)
    for key, value in auth_query_params.items():
        auth_endpoint += "&" + key + "="
        if isinstance(value, list):
            auth_endpoint += value[0]

    [code, state] = callback(auth_endpoint)

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": get_basic_auth_string(client_id, client_secret),
        "Accept": "application/json"
    }

    data = {
        "grant_type": AUTHORIZATION_CODE,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "code": code,
        "state": state
    }

    response = session.post(token_endpoint, headers=headers, data=data).json()
    access_token = response['access_token']
    return get_saml_assertion(server, session, access_token)


def login_using_refresh_token(
        server,
        session,
        client_id,
        client_secret,
        refresh_token):
    """
    Get access token when grant_type is refresh_token
    """
    identity_provider = get_identity_provider(server, session)
    [auth_endpoint, token_endpoint, auth_query_params] = \
        get_endpoints(identity_provider)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": get_basic_auth_string(client_id, client_secret),
        "Accept": "application/json"
    }
    data = {
        "grant_type": REFRESH_TOKEN,
        "refresh_token": refresh_token
    }
    response = session.post(token_endpoint, headers=headers, data=data).json()
    access_token = response['access_token']
    return get_saml_assertion(server, session, access_token)


def login_using_password(server, session, username, password):
    """
    Get access token when grant_type is password
    """
    identity_provider = get_identity_provider(server, session)
    [auth_endpoint, token_endpoint, auth_query_params] = \
        get_endpoints(identity_provider)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": get_basic_auth_string(username, password),
        "Accept": "application/json"
    }
    data = {
        "grant_type": PASSWORD,
        "username": username,
        "password": password
    }
    response = session.post(token_endpoint, headers=headers, data=data).json()
    print(response)
    access_token = response['access_token']
    return get_saml_assertion(server, session, access_token)
