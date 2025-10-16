import boto3
import os
from fastapi import FastAPI, HTTPException
from mangum import Mangum

# Initialize the FastAPI app
app = FastAPI()

# Get the DynamoDB table name from environment variables
dynamodb = boto3.resource('dynamodb')
def get_table():
    table_name = os.environ.get("TABLE_NAME", "StoriTechnicalChallengeStack-ResultsTableF0B5BF22-1M54DNQLRZ7YM")
    return dynamodb.Table(table_name)

# Define a route to get user data by user_id with optional filtering by min_amount
@app.get("/user/{user_id}")
def get_user_data(user_id: str, min_amount: float = None):
    response = get_table().get_item(Key={"user_id": user_id})
    item = response.get("Item")

    if item is None:
        raise HTTPException(status_code= 404, detail= "User not found")
    
    if min_amount is not None:
        if item["total_amount"] < min_amount:
            raise HTTPException(status_code= 404, detail= "No entries match the filter")
    
    return item

# Create a Mangum handler for AWS Lambda
handler = Mangum(app)