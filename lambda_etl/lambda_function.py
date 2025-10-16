import boto3
import pandas as pd
import io
from decimal import Decimal, InvalidOperation

def lambda_handler(event, context):

    s3 = boto3.client('s3')

    # Get the S3 bucket and object key from the event
    bucket = event['bucket']
    key = event['key']

    # Read the CSV file from S3 into a pandas DataFrame
    csv_file = s3.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(io.BytesIO(csv_file['Body'].read()))
    
    # Normalize dates to timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Filter transactions with status = approved
    df_approved = df[df['status'] == 'approved']

    # Group by user_id the number of transactions and the total amount
    grouped = df_approved.groupby('user_id').agg(
        transactions_count=pd.NamedAgg(column='user_id', aggfunc='size'),
        total_amount=pd.NamedAgg(column='amount', aggfunc='sum')
    ).reset_index()
    
    result_list = []
    # Insert the processed data into a the result list
    for _, row in grouped.iterrows():
        id = str(int(row['user_id']))
        count = int(row['transactions_count'])
        amount = row['total_amount']
        
        try:
            amount_decimal = Decimal(str(amount))
        except InvalidOperation:
            amount_decimal = Decimal(0)

        result_list.append({
            "user_id": id,
            "transactions_count": count,
            "total_amount": str(amount_decimal)
        })

    return {
        "processed_data": result_list
    }