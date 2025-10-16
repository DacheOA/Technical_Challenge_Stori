import boto3
import os
import json

# Initialize the Step Functions client
sf_client = boto3.client('stepfunctions')

# Get the State Machine ARN from environment variables
STATE_MACHINE_ARN = os.environ['STATE_MACHINE_ARN']

def lambda_handler(event, context):
    for record in event['Records']:
        record = event['Records'][0]
        s3_event = json.loads(record['body'])
        
        try:
            # Get the bucket name and object key from the S3 event
            bucket = s3_event['Records'][0]['s3']['bucket']['name']
            key = s3_event['Records'][0]['s3']['object']['key']

            # Start execution of the Step Function
            response = sf_client.start_execution(
                stateMachineArn=STATE_MACHINE_ARN,
                input=json.dumps({
                    "bucket": bucket,
                    "key": key
                })
            )
            print(f"Started SF: {response['executionArn']}")
        except Exception as e:
            print(f"Error processing S3 event: {e}")