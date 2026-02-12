import json
import logging

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
    Example backend Lambda function protected by JWT authorizer
    """
    # Get user information from authorizer context
    authorizer_context = event.get('requestContext', {}).get('authorizer', {})
    logger.info(f"authorizer_context: {authorizer_context}")

    user_info = {
        'user_id': authorizer_context.get('user_id', 'unknown'),
        'email': authorizer_context.get('email', 'unknown'),
        'username': authorizer_context.get('username', 'unknown')
    }

    response_body = {
        'message': 'Hello from protected API!',
        'user': user_info,
        'path': event.get('path', '/'),
        'httpMethod': event.get('httpMethod', 'GET')
    }

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response_body)
    }

