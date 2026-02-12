import json
import os
import jwt
import logging
from jwt import PyJWKClient

# Configuration
JWKS_URL = os.environ.get('JWKS_URL', '')
JWT_ISSUER = os.environ.get('JWT_ISSUER', '')
JWT_AUDIENCE = os.environ.get('JWT_AUDIENCE', '')

def get_logger():
    """Configure a logger compatible with local python interpreter and Lambda."""
    if len(logging.getLogger().handlers) > 0:
        # The Lambda environment pre-configures a handler logging to stderr. If a handler is already configured,
        # `.basicConfig` does not execute. Thus we set the level directly.
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)
    return logging.getLogger()

logger = get_logger()

def lambda_handler(event, context):
    """
    AWS Lambda authorizer function for JWT token validation
    """
    logger.info("Authorizer start")
    try:
        # Extract token from Authorization header
        token = event.get('authorizationToken', '')

        if not token:
            raise Exception('Unauthorized: No token provided')

        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]

        # Get method ARN for policy generation
        method_arn = event['methodArn']

        # Validate JWT token
        decoded_token = validate_jwt(token)
        logger.info(f"decoded_token: {decoded_token}")

        # Extract principal ID (subject from token)
        principal_id = decoded_token.get('sub', 'user')

        # Generate IAM policy
        policy = generate_policy(principal_id, 'Allow', method_arn, decoded_token)
        logger.info(f"policy: {policy}")

        return policy

    except jwt.ExpiredSignatureError:
        print("Token has expired")
        raise Exception('Unauthorized: Token expired')
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {str(e)}")
        raise Exception('Unauthorized: Invalid token')
    except Exception as e:
        print(f"Authorization error: {str(e)}")
        raise Exception('Unauthorized')


def validate_jwt(token):
    """
    Validate JWT token using JWKS
    """
    if JWKS_URL:
        # Use JWKS for validation (recommended for production)
        jwks_client = PyJWKClient(JWKS_URL)
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
            options={"verify_exp": True}
        )
    else:
        # For testing: decode without verification (NOT for production!)
        decoded = jwt.decode(
            token,
            options={"verify_signature": False}
        )

    return decoded


def generate_policy(principal_id, effect, resource, context=None):
    """
    Generate IAM policy document
    """
    auth_response = {
        'principalId': principal_id
    }

    if effect and resource:
        policy_document = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
        auth_response['policyDocument'] = policy_document

    # Add context information to be passed to backend
    if context:
        auth_response['context'] = {
            'email': context.get('email', ''),
            'username': context.get('username', context.get('preferred_username', '')),
            'user_id': context.get('sub', ''),
            'scope': context.get('scope', '')
        }

    return auth_response

if __name__ == "__main__":

    class MockContext:
        email = "test@kc.frb.org"
        username = "testusername",
        scope = "api_access"
    lambda_handler({
        "authorizationToken": "Bearer " + os.getenv('JWT_TOKEN', "eyJraWQiOiI5S3NQUkhJajMzbjQ3b1Z5NkdrVjZQRC1wb3labnpYbWpJVkVJWDgyWDRjIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULmg1eXdpNGtQVTBnT1pPWlU4c0tRWXdUTVNiQ09oUFNhMWR1TFZhM0lxZ3MiLCJpc3MiOiJodHRwczovL2ludGVncmF0b3ItNzYwMDExOC5va3RhLmNvbS9vYXV0aDIvZGVmYXVsdCIsImF1ZCI6ImFwaTovL2RlZmF1bHQiLCJpYXQiOjE3NzA5MDc2MjksImV4cCI6MTc3MDkxMTIyOSwiY2lkIjoiMG9hMTAwanBhZjJ0RDFEWlc2OTgiLCJzY3AiOlsiYXBpX2FjY2VzcyJdLCJzdWIiOiIwb2ExMDBqcGFmMnREMURaVzY5OCJ9.S7p2I1W6wBAHQdsy2rOKV3dEG9FynOPHuLAsbwLy73TXXgwKycOfv351sm42nt2jZB2GQ9VKpQmJEB9Fa44-Jqs5n1UGd_pAg9ih7w1oTbzDqT-UqzL2ikCQiUN55VF5BDjtvpN3GOvj5i-n0CFArTPaWApKYUvyV6y6aDA_I8rKj6taHvLVtv62iqOItqcLbCvnlux3CqFAWpwhelp9iTvDZsERQJXWa96G2nayjIe1WvCdinhEbSi1xDol0jWeoTXgNvpKRks8cHgPYaybFiMaK5Cge9tSPArz3ATzL_rF2kD8vwb8B0L_ZK2OuBPQrcz3lIvIRyOpVKcT1lGJQw"),
        "methodArn": "info"
        },
        MockContext()
#        {
#        "email": "test@kc.frb.org",
#        "username": "testusername",
#        "scope": "api_access"
#        }
    )
