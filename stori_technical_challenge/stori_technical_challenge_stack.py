from aws_cdk import (
    Stack,
    Duration,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_s3_notifications as s3n,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigw,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_events,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam


)
from constructs import Construct

class StoriTechnicalChallengeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 bucket
        data_bucket = s3.Bucket(self, "DataBucket")

        # Create SQS queue
        queue = sqs.Queue(self, "CSVTrigger")

        # Add SQS as destination for the S3 event notification
        data_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            # s3n.LambdaDestination(etl_lambda), # Add an event notification to the S3 bucket to trigger the Lambda function on object creation
            s3n.SqsDestination(queue)
        )

        # Create a ETL Lambda function
        etl_lambda = _lambda.Function(
            self, "ETLLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda_etl.zip"),
            timeout=Duration.seconds(6)
        )

        # Grant the Lambda function read permissions to the S3 bucket
        data_bucket.grant_read(etl_lambda)

        # Create a Dynamodb TableV2 to store processed data
        results_table = dynamodb.TableV2(
            self, "ResultsTable",
            partition_key=dynamodb.Attribute(
                name="user_id", 
                type=dynamodb.AttributeType.STRING
            ),
            billing= dynamodb.Billing.on_demand()
        )

        # Create Storage Lambda function for DynamoDB insertion
        storage_lambda = _lambda.Function(
            self, "StorageLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="storage_lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda_storage"),
            environment={"TABLE_NAME": results_table.table_name}
        )

        # Grant the Lambda function write permissions to the DynamoDB table
        results_table.grant_write_data(storage_lambda)

        # Create Step Functions Task to activate etl_lambda
        etl_task = tasks.LambdaInvoke(
            self, "ETL Task",
            lambda_function=etl_lambda,
            output_path="$.Payload"
        )

        # Create Step Functions Task to activate storage_lambda
        storage_task = tasks.LambdaInvoke(
            self, "Storage Task",
            lambda_function=storage_lambda,
            input_path="$.processed_data"
        )

        # Combine tasks into a state machine definition
        definition = etl_task.next(storage_task)

        # Create a Step Function
        state_machine = sfn.StateMachine(
            self, "CSVProcessingStateMachine",
            definition=definition,
            timeout=Duration.minutes(5)
        )

        # Create a Lambda function to start the Step Function execution
        start_sf_lambda = _lambda.Function(
            self, "StartSFLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="start_sf_lambda.lambda_handler",
            code=_lambda.Code.from_asset("lambda_sf"),
            environment={
                "STATE_MACHINE_ARN": state_machine.state_machine_arn
            }
        )

        # Grant the Lambda function permission to start execution of the Step Function
        start_sf_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["states:StartExecution"],
            resources=[state_machine.state_machine_arn]
        ))

        # Grant the Lambda function permission to read messages from the SQS queue
        queue.grant_consume_messages(start_sf_lambda)

        # Add SQS as event source for the ETL Lambda function
        start_sf_lambda.add_event_source(lambda_events.SqsEventSource(queue))

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