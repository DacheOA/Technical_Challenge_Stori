from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_s3_notifications as s3n,
    # aws_sqs as sqs,
)
from constructs import Construct

class StoriTechnicalChallengeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 bucket
        data_bucket = s3.Bucket(self, "DataBucket")

        # Create a Lambda function
        etl_lambda = _lambda.Function(
            self, "ETLLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda_etl.zip")
        )

        # Grant the Lambda function read permissions to the S3 bucket
        data_bucket.grant_read(etl_lambda)

        data_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(etl_lambda),
        )