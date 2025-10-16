import pytest
import os
from lambda_storage import storage_lambda_function
from decimal import Decimal

def test_insert_data(mocker):

    os.environ['TABLE_NAME'] = 'test-table'

    mock_put = mocker.MagicMock()
    mock_table = mocker.MagicMock()
    mock_table.put_item = mock_put
    mocker.patch("lambda_storage.storage_lambda_function.dynamodb.Table", return_value=mock_table)
    #mocker.patch('storage_lambda.table', mock_table)

    event = [
        {"user_id": "1", "transactions_count": 2,"total_amount": "989.91"},
        #{"user_id": "2", "transactions_count": 3,"total_amount": "1289.91"}
    ]
    
    # Call the function to test
    response = storage_lambda_function.lambda_handler(event, None)

    # Assert the expected behavior
    mock_put.assert_called_once_with(Item={
        "user_id": "1",
        "transactions_count": 2,
        "total_amount": Decimal(str(989.91))
    })

    #assert mock_put.call_count == 2

    assert response == {"status": "success"}