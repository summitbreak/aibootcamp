#!/bin/bash

# Deploy script for JWT Authorizer API Gateway
set -e

# Configuration
STACK_NAME="${STACK_NAME:-jwt-api-gateway}"
S3_BUCKET="${S3_BUCKET:-s3-spring-upgrade}"
REGION="${AWS_REGION:-us-east-1}"
STAGE_NAME="${STAGE_NAME:-prod}"

# Okta JWT Configuration (optional - set these for Okta integration)
# Example: https://dev-12345678.okta.com/oauth2/default/v1/keys
JWKS_URL="${JWKS_URL:-}"
# Example: https://dev-12345678.okta.com/oauth2/default
JWT_ISSUER="${JWT_ISSUER:-}"
# Example: api://default or your custom audience
JWT_AUDIENCE="${JWT_AUDIENCE:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}JWT API Gateway Deployment Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    exit 1
fi

# Check if S3 bucket exists
if [ -z "$S3_BUCKET" ]; then
    echo -e "${RED}Error: S3_BUCKET environment variable is not set${NC}"
    echo "Usage: S3_BUCKET=my-bucket ./deploy.sh"
    exit 1
fi

echo -e "${YELLOW}Configuration:${NC}"
echo "  Stack Name: $STACK_NAME"
echo "  S3 Bucket: $S3_BUCKET"
echo "  Region: $REGION"
echo "  Stage: $STAGE_NAME"
echo "  JWKS_URL: $JWKS_URL"
if [ -n "$JWKS_URL" ]; then
    echo "  JWKS URL: $JWKS_URL"
fi
if [ -n "$JWT_ISSUER" ]; then
    echo "  JWT Issuer: $JWT_ISSUER"
fi
if [ -n "$JWT_AUDIENCE" ]; then
    echo "  JWT Audience: $JWT_AUDIENCE"
fi
echo ""

# Install Python dependencies
echo -e "${GREEN}[1/6] Installing Python dependencies...${NC}"
if [ ! -d "package" ]; then
    mkdir package
fi

pip install -r requirements.txt -t package/ --quiet \
    --platform manylinux2014_x86_64 \
    --implementation cp \
    --python-version 3.13 \
    --only-binary=:all: --upgrade
cp authorizer.py package/
cp example_backend.py package/

echo -e "${GREEN}Dependencies installed successfully${NC}"
echo ""

# Package the CloudFormation template
echo -e "${GREEN}[2/6] Packaging CloudFormation template...${NC}"
cp template.yaml package/
cd package
#Solve issue with Windows flavour of library. Runtime.ImportModuleError: Unable to import module 'authorizer': cannot import name 'ObjectIdentifier' from 'cryptography.hazmat.bindings._rust'
#pip install \
#    --platform manylinux2014_x86_64 \
#    --target . \
#    --implementation cp \
#    --python-version 3.13 \
#    --only-binary=:all: --upgrade \
#    cryptography
aws cloudformation package \
    --template-file template.yaml \
    --s3-bucket "$S3_BUCKET" \
    --output-template-file ../packaged-template.yaml \
    --region "$REGION"

echo -e "${GREEN}Template packaged successfully${NC}"
echo ""
cd ..

# Validate CloudFormation template
echo -e "${GREEN}[3/6] Validating packaged CloudFormation template...${NC}"
aws cloudformation validate-template \
    --template-body file://packaged-template.yaml \
    --region "$REGION" > /dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Template validation successful${NC}"
else
    echo -e "${RED}Template validation failed${NC}"
    exit 1
fi
echo ""

# Deploy the CloudFormation stack
echo -e "${GREEN}[4/6] Deploying CloudFormation stack...${NC}"
PARAMS=""

if [ -n "$JWKS_URL" ]; then
    PARAMS="$PARAMS JWKSUrl=$JWKS_URL"
fi

if [ -n "$JWT_ISSUER" ]; then
    PARAMS="$PARAMS JWTIssuer=$JWT_ISSUER"
fi

if [ -n "$JWT_AUDIENCE" ]; then
    PARAMS="$PARAMS JWTAudience=$JWT_AUDIENCE"
fi

PARAMS="$PARAMS StageName=$STAGE_NAME"

aws cloudformation deploy \
    --template-file packaged-template.yaml \
    --stack-name "$STACK_NAME" \
    --parameter-overrides $PARAMS \
    --capabilities CAPABILITY_NAMED_IAM \
    --region "$REGION" \
    --no-fail-on-empty-changeset

echo -e "${GREEN}Stack deployed successfully${NC}"
echo ""

# Get stack outputs
echo -e "${GREEN}[5/6] Retrieving stack outputs...${NC}"
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text)

AUTHORIZER_ARN=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`AuthorizerFunctionArn`].OutputValue' \
    --output text)

echo -e "${GREEN}Outputs retrieved successfully${NC}"
echo ""

# Cleanup
echo -e "${GREEN}[6/6] Cleaning up...${NC}"
rm -rf package
echo -e "${GREEN}Cleanup completed${NC}"
echo ""

# Display results
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}API Gateway URL:${NC}"
echo "  $API_URL"
echo ""
echo -e "${YELLOW}Authorizer Function ARN:${NC}"
echo "  $AUTHORIZER_ARN"
echo ""
echo -e "${YELLOW}Test the API:${NC}"
echo "  curl -H \"Authorization: Bearer YOUR_JWT_TOKEN\" $API_URL/hello"
echo ""
echo -e "${YELLOW}View logs:${NC}"
echo "  aws logs tail /aws/lambda/$STACK_NAME-jwt-authorizer --follow --region $REGION"
echo "  aws logs tail /aws/lambda/$STACK_NAME-backend --follow --region $REGION"
echo ""
