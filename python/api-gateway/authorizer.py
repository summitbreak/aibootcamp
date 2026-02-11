import json
import os
import jwt
from jwt import PyJWKClient

# Configuration
JWKS_URL = os.environ.get('JWKS_URL', '')
JWT_ISSUER = os.environ.get('JWT_ISSUER', '')
JWT_AUDIENCE = os.environ.get('JWT_AUDIENCE', '')


def lambda_handler(event, context):
    """
    AWS Lambda authorizer function for JWT token validation
    """
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

        # Extract principal ID (subject from token)
        principal_id = decoded_token.get('sub', 'user')

        # Generate IAM policy
        policy = generate_policy(principal_id, 'Allow', method_arn, decoded_token)

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
