import boto3
import os
from decimal import Decimal
import json

# # Initialize DynamoDB resource and reference the table using the name from environment variables
dynamodb = boto3.resource('dynamodb')
def get_table():
    TABLE_NAME = os.environ['TABLE_NAME']
    return dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    print("Event:", json.dumps(event))
    
    data_items = event
    for item in data_items:
        user_id = str(item['user_id'])
        count = int(item['transactions_count'])
        amount = item['total_amount']

        try:
            amount_decimal = Decimal(amount)
        except:
            amount_decimal = Decimal(0)
        
        # Insert each item into the DynamoDB table
        get_table().put_item(
            Item={
                'user_id': user_id,
                'transactions_count': count,
                'total_amount': amount_decimal
            }
        )
    return {"status": "success"}