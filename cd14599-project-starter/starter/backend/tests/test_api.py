import pytest
from backend.app import app, in_memory_storage

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    in_memory_storage.clear()
    with app.test_client() as client:
        yield client

def test_add_order_api_success(client):
    order_data = {
        "order_id": "API001", "item_name": "API Laptop", "quantity": 1, "customer_id": "APICUST001"
    }
    response = client.post('/api/orders', json=order_data)
    assert response.status_code == 201
    assert response.json['order_id'] == "API001"

def test_get_order_api_success(client):
    client.post('/api/orders', json={
        "order_id": "GET001", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    })
    response = client.get('/api/orders/GET001')
    assert response.status_code == 200
    assert response.json['order_id'] == "GET001"

def test_get_order_api_not_found(client):
    response = client.get('/api/orders/NONEXISTENT')
    assert response.status_code == 404

def test_update_order_status_api_success(client):
    client.post('/api/orders', json={
        "order_id": "UPDATE001", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    })
    response = client.put('/api/orders/UPDATE001/status', json={"new_status": "shipped"})
    assert response.status_code == 200
    assert response.json['status'] == "shipped"

def test_list_all_orders_api_with_data(client):
    client.post('/api/orders', json={"order_id": "LST001", "item_name": "Item A", "quantity": 1, "customer_id": "C1"})
    client.post('/api/orders', json={"order_id": "LST002", "item_name": "Item B", "quantity": 2, "customer_id": "C2"})
    response = client.get('/api/orders')
    assert response.status_code == 200
    assert len(response.json) == 2

def test_list_orders_by_status_api_matching(client):
    client.post('/api/orders', json={"order_id": "S001", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "pending"})
    client.post('/api/orders', json={"order_id": "S002", "item_name": "B", "quantity": 2, "customer_id": "C2", "status": "shipped"})
    response = client.get('/api/orders?status=pending')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['order_id'] == "S001"


# --- Additional integration tests: error paths and response contract ---

VALID_ORDER = {"order_id": "E001", "item_name": "Item", "quantity": 1, "customer_id": "C1"}


def test_add_order_api_defaults_status_to_pending(client):
    response = client.post('/api/orders', json=VALID_ORDER)
    assert response.json['status'] == "pending"


def test_add_order_api_returns_all_five_keys(client):
    response = client.post('/api/orders', json=VALID_ORDER)
    assert set(response.json) == {"order_id", "item_name", "quantity", "customer_id", "status"}


def test_add_order_api_duplicate_returns_409(client):
    client.post('/api/orders', json=VALID_ORDER)
    response = client.post('/api/orders', json=VALID_ORDER)
    assert response.status_code == 409
    assert response.json == {"error": "Order with ID 'E001' already exists."}


def test_add_order_api_invalid_quantity_returns_400(client):
    response = client.post('/api/orders', json={**VALID_ORDER, "quantity": 0})
    assert response.status_code == 400
    assert response.json == {"error": "Quantity must be a positive integer."}


def test_add_order_api_missing_field_returns_400(client):
    body = {k: v for k, v in VALID_ORDER.items() if k != "item_name"}
    response = client.post('/api/orders', json=body)
    assert response.status_code == 400
    assert response.json == {"error": "Item name must be a non-empty string."}


def test_add_order_api_invalid_status_returns_400(client):
    response = client.post('/api/orders', json={**VALID_ORDER, "status": "lost"})
    assert response.status_code == 400


def test_add_order_api_non_json_body_returns_400(client):
    response = client.post('/api/orders', data="not json")
    assert response.status_code == 400
    assert response.json == {"error": "Request body must be a JSON object."}


def test_add_order_api_duplicate_does_not_overwrite_original(client):
    client.post('/api/orders', json=VALID_ORDER)
    client.post('/api/orders', json={**VALID_ORDER, "item_name": "Other"})
    assert client.get('/api/orders/E001').json['item_name'] == "Item"


def test_get_order_api_not_found_returns_error_message(client):
    response = client.get('/api/orders/NOPE')
    assert response.json == {"error": "Order with ID 'NOPE' not found."}


def test_update_order_status_api_not_found_returns_404(client):
    response = client.put('/api/orders/NOPE/status', json={"new_status": "shipped"})
    assert response.status_code == 404
    assert response.json == {"error": "Order with ID 'NOPE' not found."}


def test_update_order_status_api_invalid_status_returns_400(client):
    client.post('/api/orders', json=VALID_ORDER)
    response = client.put('/api/orders/E001/status', json={"new_status": "lost"})
    assert response.status_code == 400


def test_update_order_status_api_missing_new_status_returns_400(client):
    client.post('/api/orders', json=VALID_ORDER)
    response = client.put('/api/orders/E001/status', json={})
    assert response.status_code == 400


def test_update_order_status_api_persists_change(client):
    client.post('/api/orders', json=VALID_ORDER)
    client.put('/api/orders/E001/status', json={"new_status": "delivered"})
    assert client.get('/api/orders/E001').json['status'] == "delivered"


def test_list_all_orders_api_empty_returns_empty_list(client):
    response = client.get('/api/orders')
    assert response.status_code == 200
    assert response.json == []


def test_list_orders_by_status_api_no_match_returns_empty_list(client):
    client.post('/api/orders', json=VALID_ORDER)
    response = client.get('/api/orders?status=delivered')
    assert response.status_code == 200
    assert response.json == []


def test_list_orders_by_status_api_invalid_status_returns_400(client):
    response = client.get('/api/orders?status=bogus')
    assert response.status_code == 400
    assert "Invalid status 'bogus'" in response.json["error"]
