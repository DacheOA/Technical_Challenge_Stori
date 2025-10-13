import aws_cdk as core
import aws_cdk.assertions as assertions

from stori_technical_challenge.stori_technical_challenge_stack import StoriTechnicalChallengeStack

# example tests. To run these tests, uncomment this file along with the example
# resource in stori_technical_challenge/stori_technical_challenge_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = StoriTechnicalChallengeStack(app, "stori-technical-challenge")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
