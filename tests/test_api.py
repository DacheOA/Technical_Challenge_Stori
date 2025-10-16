from fastapi.testclient import TestClient
from api.main import app
import os
from decimal import Decimal

client = TestClient(app)

def test_get_user_404():

    resp = client.get("/user/123")
    assert resp.status_code == 404  


def test_get_user_200(mocker):

    os.environ['TABLE_NAME'] = 'test-table'

    mock_table = mocker.MagicMock()

    mock_table.get_item.return_value = {
        "Item": {
            "user_id": "1",
            "transactions_count": 2,
            "total_amount": Decimal(str(989.91))
        }
    }

    mocker.patch('api.main.get_table', return_value=mock_table)

    client = TestClient(app)
    resp = client.get("/user/1")
    assert resp.status_code == 200
    assert resp.json()["user_id"] == "1"
