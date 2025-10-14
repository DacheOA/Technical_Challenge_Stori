import boto3
import pandas as pd
import io
from decimal import Decimal, InvalidOperation
import os

table_name = os.environ.get("TABLE_NAME", "El nombre de la tabla")
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):

    # Get the S3 bucket and object key from the event
    s3 = boto3.client('s3')
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Read the CSV file from S3 into a pandas DataFrame
    csv_file = s3.get_object(Bucket = bucket, Key = key)
    df = pd.read_csv(io.BytesIO(csv_file['Body'].read()))
    #print('df head: ', df.head())

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

    #print('grouped: ', grouped)

    # Insert the processed data into DynamoDB
    for _, row in grouped.iterrows():
        id = str(int(row['user_id']))
        count = int(row['transactions_count'])
        amount = row['total_amount']

        try:
            amount_decimal = Decimal(str(amount))
        except InvalidOperation:
            amount_decimal = Decimal(0)

        table.put_item(
            Item = {
                'user_id': id,
                'transactions_count': count,
                'total_amount': amount_decimal
            }
        )
    print('Ok')

    return {
        'statusCode': 200,
        'body': 'Data successfull inserted into DynamoDB'
    }