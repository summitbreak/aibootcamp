import json


def lambda_handler(event, context):
    """
    Example backend Lambda function protected by JWT authorizer
    """
    # Get user information from authorizer context
    authorizer_context = event.get('requestContext', {}).get('authorizer', {})

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
