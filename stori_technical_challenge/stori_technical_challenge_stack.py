from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_s3_notifications as s3n,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigw,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_events
)
from constructs import Construct

class StoriTechnicalChallengeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 bucket
        data_bucket = s3.Bucket(self, "DataBucket")

        # Create a Dynamodb TableV2 to store processed data
        results_table = dynamodb.TableV2(
            self, "ResultsTable",
            partition_key=dynamodb.Attribute(
                name="user_id", 
                type=dynamodb.AttributeType.STRING
            ),
            billing= dynamodb.Billing.on_demand()
        )

        # Create a Lambda function
        etl_lambda = _lambda.Function(
            self, "ETLLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda_etl.zip"),
            environment= {"TABLE_NAME": results_table.table_name}
        )

        # Grant the Lambda function read permissions to the S3 bucket
        data_bucket.grant_read(etl_lambda)

        # Grant the Lambda function write permissions to the DynamoDB table
        results_table.grant_write_data(etl_lambda)

        # Create an API Gateway to expose the data in the DynamoDB table
        api_lambda = _lambda.Function(
            self, "APIFunction",
            runtime = _lambda.Runtime.PYTHON_3_9,
            handler= "main.handler",
            code= _lambda.Code.from_asset("api.zip"),
            environment= {"TABLE_NAME": results_table.table_name}
        )

        # Grant the API Lambda function read permissions to the DynamoDB table
        results_table.grant_read_data(api_lambda)

        # Create an API Gateway REST API
        api = apigw.LambdaRestApi(
            self, "APIGateway",
            handler= api_lambda,
            deploy_options= apigw.StageOptions(stage_name= "dev")
        )

        # Create SQS queue
        queue = sqs.Queue(self, "CSVTrigger")

        # Add SQS as destination for the S3 event notification
        data_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            # s3n.LambdaDestination(etl_lambda), # Add an event notification to the S3 bucket to trigger the Lambda function on object creation
            s3n.SqsDestination(queue)
        )

        # Add SQS as event source for the ETL Lambda function
        etl_lambda.add_event_source(lambda_events.SqsEventSource(queue))