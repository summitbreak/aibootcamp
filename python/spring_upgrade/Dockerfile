# Use AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.11

# Copy function code
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the Lambda function
CMD ["lambda_handler.lambda_handler"]
