@echo off
REM Deploy script for JWT Authorizer API Gateway (Windows)

setlocal EnableDelayedExpansion

REM Configuration
if "%STACK_NAME%"=="" set STACK_NAME=jwt-api-gateway
if "%S3_BUCKET%"=="" set S3_BUCKET=s3-spring-upgrade
if "%AWS_REGION%"=="" set AWS_REGION=us-east-1
if "%STAGE_NAME%"=="" set STAGE_NAME=prod

REM Okta JWT Configuration (optional)
REM Example: https://dev-12345678.okta.com/oauth2/default/v1/keys
REM Example: https://dev-12345678.okta.com/oauth2/default
REM Example: api://default

echo ========================================
echo JWT API Gateway Deployment Script
echo ========================================
echo.

REM Check if AWS CLI is installed
where aws >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: AWS CLI is not installed
    exit /b 1
)

REM Check if S3 bucket is provided
if "%S3_BUCKET%"=="" (
    echo Error: S3_BUCKET environment variable is not set
    echo Usage: set S3_BUCKET=my-bucket ^& deploy.bat
    exit /b 1
)

echo Configuration:
echo   Stack Name: %STACK_NAME%
echo   S3 Bucket: %S3_BUCKET%
echo   Region: %AWS_REGION%
echo   Stage: %STAGE_NAME%
if not "%JWKS_URL%"=="" echo   JWKS URL: %JWKS_URL%
if not "%JWT_ISSUER%"=="" echo   JWT Issuer: %JWT_ISSUER%
if not "%JWT_AUDIENCE%"=="" echo   JWT Audience: %JWT_AUDIENCE%
echo.

REM Install Python dependencies
echo [1/6] Installing Python dependencies...
if not exist package mkdir package

pip install -r requirements.txt -t package\ --quiet
copy authorizer.py package\
copy example_backend.py package\

echo Dependencies installed successfully
echo.

REM Package the CloudFormation template
echo [2/6] Packaging CloudFormation template...
aws cloudformation package ^
    --template-file template.yaml ^
    --s3-bucket %S3_BUCKET% ^
    --output-template-file packaged-template.yaml ^
    --region %AWS_REGION%

if %ERRORLEVEL% NEQ 0 (
    echo Error packaging template
    exit /b 1
)

echo Template packaged successfully
echo.

REM Validate CloudFormation template
echo [3/6] Validating packaged CloudFormation template...
aws cloudformation validate-template ^
    --template-body file://packaged-template.yaml ^
    --region %AWS_REGION% >nul

if %ERRORLEVEL% NEQ 0 (
    echo Template validation failed
    exit /b 1
)

echo Template validation successful
echo.

REM Build parameters
set PARAMS=StageName=%STAGE_NAME%
if not "%JWKS_URL%"=="" set PARAMS=%PARAMS% JWKSUrl=%JWKS_URL%
if not "%JWT_ISSUER%"=="" set PARAMS=%PARAMS% JWTIssuer=%JWT_ISSUER%
if not "%JWT_AUDIENCE%"=="" set PARAMS=%PARAMS% JWTAudience=%JWT_AUDIENCE%

REM Deploy the CloudFormation stack
echo [4/6] Deploying CloudFormation stack...
aws cloudformation deploy ^
    --template-file packaged-template.yaml ^
    --stack-name %STACK_NAME% ^
    --parameter-overrides %PARAMS% ^
    --capabilities CAPABILITY_NAMED_IAM ^
    --region %AWS_REGION% ^
    --no-fail-on-empty-changeset

if %ERRORLEVEL% NEQ 0 (
    echo Error deploying stack
    exit /b 1
)

echo Stack deployed successfully
echo.

REM Get stack outputs
echo [5/6] Retrieving stack outputs...
for /f "delims=" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --region %AWS_REGION% --query "Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue" --output text') do set API_URL=%%i
for /f "delims=" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --region %AWS_REGION% --query "Stacks[0].Outputs[?OutputKey==`AuthorizerFunctionArn`].OutputValue" --output text') do set AUTHORIZER_ARN=%%i

echo Outputs retrieved successfully
echo.

REM Cleanup
echo [6/6] Cleaning up...
rmdir /s /q package
echo Cleanup completed
echo.

REM Display results
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo API Gateway URL:
echo   %API_URL%
echo.
echo Authorizer Function ARN:
echo   %AUTHORIZER_ARN%
echo.
echo Test the API:
echo   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" %API_URL%/hello
echo.
echo View logs:
echo   aws logs tail /aws/lambda/%STACK_NAME%-jwt-authorizer --follow --region %AWS_REGION%
echo   aws logs tail /aws/lambda/%STACK_NAME%-backend --follow --region %AWS_REGION%
echo.

endlocal
