import pytest
import io
from lambda_etl.lambda_function import lambda_handler

def test_etl_process(mocker):
    mock_boto3 = mocker.patch('lambda_etl.lambda_function.boto3')
    mock_s3_client = mock_boto3.client.return_value

    mock_s3_client.get_object.return_value = {
        'Body': io.BytesIO(b'user_id,amount,timestamp,status\n1,100.0,2021-01-01,approved\n2,50,2021-01-02,pending')
    }

    event = {
        'bucket': 'test-bucket',
        'key': 'test.csv'
    }

    result = lambda_handler(event, None)

    processed = result['processed_data']
    assert isinstance(processed, list)
    assert processed[0]['user_id'] == '1'
    assert processed[0]['transactions_count'] == 1
    assert processed[0]['total_amount'] == '100.0'