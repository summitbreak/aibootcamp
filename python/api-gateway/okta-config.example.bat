@echo off
REM Okta Configuration Example for JWT Authorizer
REM Copy this file to okta-config.bat and fill in your Okta details
REM Run: okta-config.bat before deploying

REM Your Okta domain (e.g., dev-12345678.okta.com)
set OKTA_DOMAIN=dev-12345678.okta.com

REM Authorization Server (default or custom)
REM For default authorization server: /oauth2/default
REM For custom authorization server: /oauth2/{authServerId}
set AUTH_SERVER=default

REM JWKS URL - Public keys endpoint
set JWKS_URL=https://%OKTA_DOMAIN%/oauth2/%AUTH_SERVER%/v1/keys

REM JWT Issuer - Must match the issuer claim in your tokens
set JWT_ISSUER=https://%OKTA_DOMAIN%/oauth2/%AUTH_SERVER%

REM JWT Audience - Must match the audience claim in your tokens
REM Common values:
REM - api://default (Okta default audience)
REM - Your custom audience configured in Okta
set JWT_AUDIENCE=api://default

REM AWS Configuration
set S3_BUCKET=s3-spring-upgrade
set AWS_REGION=us-east-1
set STACK_NAME=jwt-api-gateway
set STAGE_NAME=prod

echo Okta Configuration Loaded:
echo   Okta Domain: %OKTA_DOMAIN%
echo   JWKS URL: %JWKS_URL%
echo   JWT Issuer: %JWT_ISSUER%
echo   JWT Audience: %JWT_AUDIENCE%
echo.
echo Ready to deploy!
echo Run: deploy.bat
