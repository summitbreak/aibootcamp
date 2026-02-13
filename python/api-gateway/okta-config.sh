#!/bin/bash
# Run: source okta-config.sh before deploying

# Your Okta domain (e.g., dev-12345678.okta.com)
export OKTA_DOMAIN="integrator-7600118.okta.com"

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

export CLIENT_ID=0oa100jpaf2tD1DZW698
export CLIENT_SECRET=RmLuQH3Eca77O9ZDx9sT4u3lXknLojPW1Yu0t2vSmcBQqiiEufJrmdvJAjOt8EWZ
export API_URL=https://3egshvb1z7.execute-api.us-east-1.amazonaws.com/prod

echo "Okta Configuration Loaded:"
echo "  Okta Domain: $OKTA_DOMAIN"
echo "  JWKS URL: $JWKS_URL"
echo "  JWT Issuer: $JWT_ISSUER"
echo "  JWT Audience: $JWT_AUDIENCE"
echo "  API_URL: $API_URL"
echo ""
echo "Ready to deploy!"
echo "Run: ./deploy.sh"
