#!/bin/bash
# Okta Configuration Example for JWT Authorizer
# Copy this file to okta-config.sh and fill in your Okta details
# Run: source okta-config.sh before deploying

# Your Okta domain (e.g., dev-12345678.okta.com)
export OKTA_DOMAIN="dev-12345678.okta.com"

# Authorization Server (default or custom)
# For default authorization server: /oauth2/default
# For custom authorization server: /oauth2/{authServerId}
export AUTH_SERVER="default"

# JWKS URL - Public keys endpoint
export JWKS_URL="https://${OKTA_DOMAIN}/oauth2/${AUTH_SERVER}/v1/keys"

# JWT Issuer - Must match the issuer claim in your tokens
export JWT_ISSUER="https://${OKTA_DOMAIN}/oauth2/${AUTH_SERVER}"

# JWT Audience - Must match the audience claim in your tokens
# Common values:
# - api://default (Okta default audience)
# - Your custom audience configured in Okta
export JWT_AUDIENCE="api://default"

# AWS Configuration
export S3_BUCKET="s3-spring-upgrade"
export AWS_REGION="us-east-1"
export STACK_NAME="jwt-api-gateway"
export STAGE_NAME="prod"

echo "Okta Configuration Loaded:"
echo "  Okta Domain: $OKTA_DOMAIN"
echo "  JWKS URL: $JWKS_URL"
echo "  JWT Issuer: $JWT_ISSUER"
echo "  JWT Audience: $JWT_AUDIENCE"
echo ""
echo "Ready to deploy!"
echo "Run: ./deploy.sh"
