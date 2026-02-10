import logging
import os
import time

import jwt


LOGGER = logging.getLogger()


BASE_ISSUER_URL = os.environ.get("OKTA_ISSUER_URL") # "https://dev-ry3ox2071omep7y1.us.auth0.com/"
JWKS_URL = f"{BASE_ISSUER_URL}/v1/keys"

VALID_TOKEN_USE = ["id"]

# Get auth token from event, decode, ad=bd validate audience and expiry
def lambda_handler(event, context):
    # configure python logger for Lambda
    _configure_logger()
    # silence chatty libraries for better logging
    _silence_noisy_loggers()

    auth_token = event.get("authorizationToken")
    if not auth_token:
        LOGGER.error("No authorizationToken passed in")
        return generate_deny('user', event.methodArn)

    token_string = auth_token.replace("Bearer ", "")
    if not token_string:
        LOGGER.error("empty token provided")
        return generate_deny('user', event.methodArn)
    
    LOGGER.info("Attempting to extract headers from the token string")
    try:
        token_header = jwt.get_unverified_header(token_string)
    except jwt.exceptions.DecodeError as err:
        LOGGER.error(
            f"Unable to extracat headers from the token string: {err}")
        return generate_deny('user', event.methodArn)

    LOGGER.info(f"Initializing jwks client for: {JWKS_URL}")
    jwks_client = jwt.PyJWKClient(JWKS_URL)

    LOGGER.info("Trying to get the signing key from the token header")
    try:
        key = jwks_client.get_signing_key(token_header["kid"]).key
    except jwt.exceptions.PyJWKSetError as err:
        LOGGER.error(f"Unable to fetch keys: {err}")
        return generate_deny('user', event.methodArn)
    except jwt.exceptions.PyJWKClientError as err:
        LOGGER.error(f"No matching key found: {err}")
        return generate_deny('user', event.methodArn)
    
    algorithm = token_header.get("alg")
    if not algorithm:
        LOGGER.error("Token header did not contain the alg key")
        return generate_deny('user', event.methodArn)
    
    audience_client = "ai-spring-upgrade-dev"
    LOGGER.info(f"Trying to decode the token string for client: {audience_client}")
    try:
        decoded_token = jwt.decode(
            token_string, 
            key, 
            [algorithm], 
            audience=audience_client
        )
    except jwt.exceptions.DecodeError as err:
        LOGGER.error(f"Unable to decode token string: {err}")
        return generate_deny('user', event.methodArn)
    except jwt.exceptions.MissingRequiredClaimError as err:
        LOGGER.error(f"Unable to decode token: {err}")
        return generate_deny('user', event.methodArn)
    except jwt.exceptions.ExpiredSignatureError as err:
        LOGGER.error(f"Signature has expired: {err}")
        return generate_deny('user', event.methodArn)
    
    if not _valid_token(decoded_token, audience_client):
        return generate_deny('user', event.methodArn)
    
    tmp = event.methodArn.split(':')
    apiGatewayArnTmp = tmp[5].split('/')
    # awsAccountId = tmp[4]
    # region = tmp[3]
    # restApiId = apiGatewayArnTmp[1]
    # method = apiGatewayArnTmp[2]
    resource = '/' # root resource
    if (apiGatewayArnTmp[3]):
        resource += apiGatewayArnTmp[3]

    
    return generate_allow('me', decoded_token.sub)       

def generate_allow(principalId, resource):
    return generate_policy(principalId, 'Allow', resource)

def generate_deny(principalId, resource):
    return generate_policy(principalId, 'Deny', resource)

def generate_policy(principalId, effect, resource):
    auth_response = {}
    
    auth_response.principalId = principalId
    if (effect and resource):
        policyDocument = {}
        policyDocument.Version = '2012-10-17'
        policyDocument.Statement = []
        statementOne = {}
        statementOne.Action = 'execute-api:Invoke'
        statementOne.Effect = effect
        statementOne.Resource = resource
        policyDocument.Statement[0] = statementOne
        auth_response.policyDocument = policyDocument
    
    # Optional output with custom properties of the String, Number or Boolean type.
    # auth_response.context = {
    #     "stringKey": "stringval",
    #     "numberKey": 123,
    #     "booleanKey": True
    # }
    return auth_response
    

def _silence_noisy_loggers():
    """Silence chatty libraries for better logging"""
    for logger in ['boto3', 'botocore',
                   'botocore.vendored.requests.packages.urllib3']:
        logging.getLogger(logger).setLevel(logging.WARNING)


def _configure_logger():
    """Configure python logger for lambda function"""
    default_log_args = {
        "level": logging.DEBUG if os.environ.get("VERBOSE", False) else logging.INFO,
        "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        "datefmt": "%d-%b-%y %H:%M",
        "force": True,
    }
    logging.basicConfig(**default_log_args)


def _valid_token(token, audience):
    """Check JWT token parameters' validity

    :param token: Dictionary
    :param audience: String

    :rtype: Boolean
    """
    expiry_time = token.get("exp")
    if not expiry_time:
        LOGGER.error("Token does not contain 'exp' key")
        return False
    
    if int(time.time()) > expiry_time:
        LOGGER.error("Token has expired")
        return False

    aud = token.get("aud")
    if not aud:
        LOGGER.error("Missing 'aud' key in token")
        return False
    
    if aud != audience:
        LOGGER.error(f"Audience client {aud} does not match")
        return False
    
    iss = token.get("iss")
    if not iss:
        LOGGER.error("Missing 'iss' key in token")
        return False
    
    if iss != BASE_ISSUER_URL:
        LOGGER.error(f"Issuer URL {iss} did not match")
        return False

    token_use = token.get("token_use")
    if not token_use:
        LOGGER.error("token_use missing from token")
        return False
    
    if token_use not in VALID_TOKEN_USE:
        LOGGER.error(f"token_use {token_use} is not a valid option")
        return False
    
    LOGGER.info("Decoded token is verified to be valid")
    return True
