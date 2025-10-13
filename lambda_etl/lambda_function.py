import boto3
import pandas as pd
import io
from decimal import Decimal, InvalidOperation

def lambda_handler(event, context):

    # Get the S3 bucket and object key from the event
    s3 = boto3.client('s3')
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Read the CSV file from S3 into a pandas DataFrame
    csv_file = s3.get_object(Bucket = bucket, Key = key)
    df = pd.read_csv(io.BytesIO(csv_file['Body'].read()))
    print('df: ', df)

    # Normalize dates to timestamp
    #df['timestamp'] = pd.to_datetime(df['timestamp']).astype(int) // 10**9
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    #Filter transactions with status = approved
    df_approved = df[df['status'] == 'approved']

    #Group by user_id the number of transactions and the total amount
    grouped = df_approved.groupby(['user_id']).agg(
        transactions_count = pd.NamedAgg(column= 'user_id', aggfunc= 'size'),
        total_amount = pd.NamedAgg(column= 'amount', aggfunc= 'sum')
    ).reset_index()

    print('grouped: ', grouped)