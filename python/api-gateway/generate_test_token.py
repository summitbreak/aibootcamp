#!/usr/bin/env python3
"""
Generate a test JWT token for local testing
NOTE: This is for TESTING ONLY - do not use in production!
"""

import jwt
from datetime import datetime, timedelta
import sys

def generate_test_token(
    user_id="test-user-123",
    email="test@example.com",
    username="testuser",
    expiry_hours=24
):
    """
    Generate a test JWT token (unsigned - for testing only!)
    """

    # Create token payload
    payload = {
        'sub': user_id,
        'email': email,
        'username': username,
        'preferred_username': username,
        'iss': 'https://test-issuer.example.com',
        'aud': 'test-audience',
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=expiry_hours),
        'scope': 'openid profile email'
    }

    # Generate unsigned token (none algorithm - for testing ONLY!)
    # This will only work if JWKS_URL is not set in the authorizer
    token = jwt.encode(payload, '', algorithm='none')

    return token


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage: python generate_test_token.py [user_id] [email] [username]")
        print("\nExample:")
        print("  python generate_test_token.py")
        print("  python generate_test_token.py user-456 admin@example.com admin")
        return

    # Get arguments or use defaults
    user_id = sys.argv[1] if len(sys.argv) > 1 else "test-user-123"
    email = sys.argv[2] if len(sys.argv) > 2 else "test@example.com"
    username = sys.argv[3] if len(sys.argv) > 3 else "testuser"

    token = generate_test_token(user_id, email, username)

    print("\n" + "="*80)
    print("TEST JWT TOKEN GENERATED (UNSIGNED - FOR TESTING ONLY!)")
    print("="*80)
    print("\nToken Payload:")
    print(f"  User ID: {user_id}")
    print(f"  Email: {email}")
    print(f"  Username: {username}")
    print(f"  Expiry: 24 hours from now")
    print("\nToken:")
    print(token)
    print("\nTest Command:")
    print(f'curl -H "Authorization: Bearer {token}" YOUR_API_URL/hello')
    print("\nNOTE: This token is UNSIGNED and will only work if JWKS_URL is not")
    print("      configured in your Lambda authorizer. For production, use proper")
    print("      JWT tokens from your identity provider (Cognito, Auth0, etc.)")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
