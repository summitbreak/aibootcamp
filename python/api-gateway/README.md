# JWT Authorizer API Gateway Project

A complete AWS serverless project featuring API Gateway with JWT token-based authentication using Lambda authorizers. Configured for Okta integration with Python 3.13.

## Project Structure

```
.
├── authorizer.py              # JWT authorizer Lambda function
├── example_backend.py         # Example backend Lambda function
├── requirements.txt           # Python dependencies
├── template.yaml              # CloudFormation/SAM template
├── deploy.sh                  # Deployment script (Linux/Mac)
├── deploy.bat                 # Deployment script (Windows)
├── generate_test_token.py     # Test token generator
├── okta-config.example.sh     # Okta configuration example (Linux/Mac)
├── okta-config.example.bat    # Okta configuration example (Windows)
└── README.md                  # This file
```

## Components

### 1. JWT Authorizer Lambda (`authorizer.py`)
- Validates JWT tokens from Authorization header
- Supports JWKS-based validation for production
- Returns IAM policy for API Gateway
- Passes user context to backend functions

### 2. Backend Lambda (`example_backend.py`)
- Example protected endpoint
- Receives user information from authorizer context
- Returns JSON response with user details

### 3. CloudFormation Template (`template.yaml`)
- **Lambda Functions**: JWT authorizer and backend
- **IAM Roles**: Separate roles for each Lambda with least privilege
- **API Gateway**: REST API with custom authorizer
- **API Gateway Authorizer**: TOKEN-based authorizer using JWT Lambda
- **API Resources & Methods**: Protected endpoints

### 4. IAM Roles

#### JWT Authorizer Role
- Basic Lambda execution permissions
- CloudWatch Logs access

#### Backend Function Role
- Basic Lambda execution permissions

#### API Gateway Authorizer Role
- Permission to invoke the JWT authorizer Lambda

## Prerequisites

- AWS CLI installed and configured
- Python 3.13+
- AWS account with appropriate permissions
- S3 bucket for deployment artifacts
- Okta account (for JWT token generation)

## Configuration

### Okta Configuration

This project is configured to work with Okta as the JWT provider. You need to set up an Okta application first:

1. **Create an Okta Application**:
   - Log in to your Okta admin console
   - Go to Applications → Create App Integration
   - Choose "API Services" for machine-to-machine or "SPA/Native" for user authentication
   - Note your Client ID and configure allowed grant types
   - In created Application uncheck "Proof of possession"/DRoP
   - In Security-API-Scopes add new api_scope (or any name)
   - Add new Access Policy and Rule to it

2. **Get Okta Configuration Values**:
   - **Okta Domain**: Found in your Okta admin console (e.g., `dev-12345678.okta.com`)
   - **Authorization Server**: Default is `default`, or use custom auth server ID
   - **JWKS URL**: `https://{your-okta-domain}/oauth2/{authServer}/v1/keys`
   - **Issuer**: `https://{your-okta-domain}/oauth2/{authServer}`
   - **Audience**: Usually `api://default` or your custom audience claim

3. **Configure Environment Variables**:

Copy and customize the Okta configuration file:

**Linux/Mac:**
```bash
cp okta-config.example.sh okta-config.sh
# Edit okta-config.sh with your Okta details
source okta-config.sh
```

**Windows:**
```batch
copy okta-config.example.bat okta-config.bat
REM Edit okta-config.bat with your Okta details
okta-config.bat
```

Or set variables manually:

```bash
# Required
export S3_BUCKET=s3-spring-upgrade

# Okta JWT Configuration
export JWKS_URL=https://dev-12345678.okta.com/oauth2/default/v1/keys
export JWT_ISSUER=https://dev-12345678.okta.com/oauth2/default
export JWT_AUDIENCE=api://default

# Optional
export STACK_NAME=jwt-api-gateway        # Default: jwt-api-gateway
export AWS_REGION=us-east-1              # Default: us-east-1
export STAGE_NAME=prod                   # Default: prod
```

### Alternative: AWS Cognito Configuration

If you prefer AWS Cognito instead of Okta:

```bash
export JWKS_URL=https://cognito-idp.us-east-1.amazonaws.com/us-east-1_XXXXXXXXX/.well-known/jwks.json
export JWT_ISSUER=https://cognito-idp.us-east-1.amazonaws.com/us-east-1_XXXXXXXXX
export JWT_AUDIENCE=your-app-client-id
```

## Deployment

The deployment script now includes template validation before deployment.

### Linux/Mac

```bash
# Make script executable
chmod +x deploy.sh

# Option 1: Use Okta configuration file
source okta-config.sh
./deploy.sh

# Option 2: Set variables and deploy
S3_BUCKET=s3-spring-upgrade \
JWKS_URL=https://dev-12345678.okta.com/oauth2/default/v1/keys \
JWT_ISSUER=https://dev-12345678.okta.com/oauth2/default \
JWT_AUDIENCE=api://default \
./deploy.sh
```

### Windows

```batch
REM Option 1: Use Okta configuration file
okta-config.bat
deploy.bat

REM Option 2: Set variables and deploy
set S3_BUCKET=s3-spring-upgrade
set JWKS_URL=https://dev-12345678.okta.com/oauth2/default/v1/keys
set JWT_ISSUER=https://dev-12345678.okta.com/oauth2/default
set JWT_AUDIENCE=api://default
deploy.bat
```

### Deployment Steps

The deployment script performs the following steps:

1. **Installs Python dependencies** - Downloads PyJWT and cryptography
2. **Packages template** - Uploads code to S3 bucket
3. **Validates packaged CloudFormation template** - Checks syntax and structure
4. **Deploys CloudFormation stack** - Creates all AWS resources
5. **Retrieves outputs** - Gets API URL and Lambda ARNs
6. **Cleans up** - Removes temporary package directory

### Manual Deployment

If you prefer manual deployment:

```bash
# 1. Install dependencies
pip install -r requirements.txt -t package/
cp authorizer.py package/
cp example_backend.py package/

# 2. Package template
aws cloudformation package \
    --template-file template.yaml \
    --s3-bucket s3-spring-upgrade \
    --output-template-file packaged-template.yaml \
    --region us-east-1

# 3. Validate packaged template
aws cloudformation validate-template \
    --template-body file://packaged-template.yaml \
    --region us-east-1

# 4. Deploy stack
aws cloudformation deploy \
    --template-file packaged-template.yaml \
    --stack-name jwt-api-gateway \
    --capabilities CAPABILITY_NAMED_IAM \
    --region us-east-1 \
    --parameter-overrides \
        StageName=prod \
        JWKSUrl=https://dev-12345678.okta.com/oauth2/default/v1/keys \
        JWTIssuer=https://dev-12345678.okta.com/oauth2/default \
        JWTAudience=api://default
```

## Testing

### Get JWT Token from Okta

There are several ways to get a JWT token from Okta:

#### Option 1: Using Okta OAuth 2.0 Token Endpoint (Client Credentials)

```bash
# For machine-to-machine authentication
OKTA_DOMAIN="dev-12345678.okta.com"
CLIENT_ID="your-client-id"
CLIENT_SECRET="your-client-secret"
AUTH_SERVER="default"

echo "OKTA_DOMAIN: ${OKTA_DOMAIN} AUTH_SERVER: ${AUTH_SERVER}"
echo "CLIENT_ID: ${CLIENT_ID} CLIENT_SECRET: ${CLIENT_SECRET}"
# Get access token
export JWT_TOKEN=$(curl -s -X POST "https://${OKTA_DOMAIN}/oauth2/${AUTH_SERVER}/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}" \
  -d "scope=api_access" | jq -r '.access_token')

echo "Token: $JWT_TOKEN"
```

#### Option 2: Using Okta Authorization Code Flow (User Authentication)

For user-based authentication, you'll need to:
1. Redirect user to Okta authorization endpoint
2. Handle the callback with authorization code
3. Exchange code for access token

```bash
# Authorization endpoint (open in browser)
https://{your-okta-domain}/oauth2/default/v1/authorize?
  client_id={client-id}&
  response_type=code&
  scope=openid%20profile%20email&
  redirect_uri={your-redirect-uri}&
  state=random-state-string

# After redirect, exchange code for token
curl -X POST "https://${OKTA_DOMAIN}/oauth2/${AUTH_SERVER}/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}" \
  -d "code=${AUTH_CODE}" \
  -d "redirect_uri=${REDIRECT_URI}"
```

#### Option 3: Using Okta Admin Console (Testing Only)

1. Go to Okta Admin Console → Security → API
2. Select your Authorization Server
3. Go to "Token Preview" tab
4. Select your OAuth client
5. Select grant type and scopes
6. Click "Preview Token"
7. Copy the generated token

### Test the API

```bash
# Get API URL from stack outputs
export API_URL=$(aws cloudformation describe-stacks \
    --stack-name jwt-api-gateway \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text)

echo $API_URL
# Test with JWT token
curl -H "Authorization: Bearer $JWT_TOKEN" ${API_URL}/info

curl -X POST  ${API_URL}/upgrade-project \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  --aws-sigv4 "aws:amz:region:execute-api" \
  --data-raw '{"github_url": "https://github.com/summitbreak/aibootcamp, "spring_version": "Spring boot 2.7"}'

curl -H "Authorization: Bearer $JWT_TOKEN" -H "Content-Type:
  application/json" -X POST "${API_URL}/upgrade-project" -d '{"github_url":
  "git@github.com:summitbreak/webjava8sb23.git", "repo_api_url":
  "https://api.github.com/repos/summitbreak/webjava8sb23", "pom_path":
  "webjava8sb23/pom.xml", "spring_version": "Spring boot 2.7"}'

CloudWatch: https://us-east-1.signin.aws.amazon.com/oauth?client_id=arn%3Aaws%3Asignin%3A%3A%3Aconsole%2Fcloudwatch&code_challenge=9J8J10d7lj9ZO5Q8lwe8hpQ3DIsH8WEvnU1W15LrQds&code_challenge_method=SHA-256&response_type=code&redirect_uri=https%3A%2F%2Fus-east-1.console.aws.amazon.com%2Fcloudwatch%2Fhome%3Fca-oauth-flow-id%3D2c6d%26hashArgs%3D%2523logsV2%253Alogs-insights%25243FqueryDetail%25243D%257E%2528end%257E0%257Estart%257E-10800%257EtimeType%257E%2527RELATIVE%257Etz%257E%2527UTC%257Eunit%257E%2527seconds%257EeditorString%257E%2527fields*20*40timestamp*2c*20*40entity.Attributes.Lambda.Function*2c*20*40message*0a*23*7c*20filter*20message*20like*20*2fUse*20JWKS*20for*20valid*2f*0a*7c*20sort*20*40timestamp*20desc*0a*7c*20limit*2010000%257EqueryId%257E%25275c3acc4f-6305-4bbf-a4b7-57f8ec7fc336%257Esource%257E%2528%257E%2527arn*3aaws*3alogs*3aus-east-1*3a049451948798*3alog-group*3a*2faws*2flambda*2fjwt-api-gateway-backend%257E%2527arn*3aaws*3alogs*3aus-east-1*3a049451948798*3alog-group*3a*2faws*2flambda*2fjwt-api-gateway-jwt-authorizer%2529%257Elang%257E%2527CWLI%257ElogClass%257E%2527STANDARD%257EqueryBy%257E%2527logGroupName%2529%26isauthcode%3Dtrue%26oauthStart%3D1771969132408%26region%3Dus-east-1%26state%3DhashArgsFromTB_us-east-1_8af2299d4104763f

```

### Expected Response

```json
{
  "message": "Hello from protected API!",
  "user": {
    "user_id": "sub-from-token",
    "email": "user@example.com",
    "username": "username"
  },
  "path": "/hello",
  "httpMethod": "GET"
}
```

### Test without token (should fail)

```bash
curl ${API_URL}/hello
# Response: {"Message":"Unauthorized"}
```

## Monitoring

### View Lambda Logs

```bash
# Authorizer logs
aws logs tail /aws/lambda/jwt-api-gateway-jwt-authorizer --follow

# Backend logs
aws logs tail /aws/lambda/jwt-api-gateway-backend --follow
```

### CloudWatch Metrics

Monitor in AWS Console:
- Lambda invocations and errors
- API Gateway 4XX/5XX errors
- Authorizer cache hit rate

## Security Best Practices

1. **Always use JWKS in production** - Set the JWKS_URL parameter
2. **Rotate secrets regularly** - Update JWT signing keys periodically
3. **Enable CloudWatch Logs** - Monitor authentication attempts
4. **Use HTTPS only** - API Gateway enforces this by default
5. **Set appropriate token expiration** - Configure in your IdP
6. **Enable API throttling** - Protect against abuse
7. **Use least privilege IAM roles** - Roles follow principle of least privilege

## JWT Token Format

The authorizer expects JWT tokens with these claims:

```json
{
  "sub": "user-id",              // Subject (user identifier)
  "email": "user@example.com",   // User email (optional)
  "username": "username",        // Username (optional)
  "iss": "issuer-url",          // Issuer
  "aud": "audience",            // Audience
  "exp": 1234567890,            // Expiration timestamp
  "iat": 1234567890             // Issued at timestamp
}
```

## Customization

### Add More Endpoints

Edit `template.yaml`:

```yaml
# Add new resource
NewResource:
  Type: AWS::ApiGateway::Resource
  Properties:
    RestApiId: !Ref ApiGateway
    ParentId: !GetAtt ApiGateway.RootResourceId
    PathPart: newpath

# Add new method
NewMethod:
  Type: AWS::ApiGateway::Method
  Properties:
    RestApiId: !Ref ApiGateway
    ResourceId: !Ref NewResource
    HttpMethod: POST
    AuthorizationType: CUSTOM
    AuthorizerId: !Ref ApiAuthorizer
    Integration:
      Type: AWS_PROXY
      IntegrationHttpMethod: POST
      Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${BackendFunction.Arn}/invocations'
```

### Customize Authorizer Policy

Modify `generate_policy()` in `authorizer.py` to:
- Add more context fields
- Implement custom authorization logic
- Add resource-based permissions

### Add CORS Support

Add to method in `template.yaml`:

```yaml
MethodResponses:
  - StatusCode: 200
    ResponseParameters:
      method.response.header.Access-Control-Allow-Origin: true
```

## Cleanup

Delete the CloudFormation stack:

```bash
aws cloudformation delete-stack --stack-name jwt-api-gateway
```

## Troubleshooting

### "Unauthorized" Error

1. Check token is valid and not expired
2. Verify JWKS_URL is correct
3. Check issuer and audience match
4. View authorizer logs for details

### "Internal Server Error"

1. Check Lambda function logs
2. Verify IAM roles have correct permissions
3. Ensure dependencies are packaged correctly

### Deployment Fails

1. Verify S3 bucket exists and is accessible
2. Check IAM permissions for CloudFormation
3. Ensure stack name is unique

## Cost Estimation

Monthly costs (approximate, us-east-1):
- API Gateway: $3.50 per million requests
- Lambda: Free tier covers 1M requests/month
- CloudWatch Logs: $0.50/GB ingested

For most development use, this stays within AWS free tier.

## Resources

- [AWS Lambda Authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)
- [JWT.io](https://jwt.io/) - JWT token debugger
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)

## License

MIT License - feel free to use this project as a template for your own applications.
