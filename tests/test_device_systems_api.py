from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_swagger_docs_available():
    response = client.get('/docs')
    assert response.status_code == 200


def test_users_endpoint_lists_users():
    response = client.get('/users')
    assert response.status_code == 200
    payload = response.json()
    assert 'users' in payload
    assert 'total' in payload


def test_device_and_loan_flow():
    email = f'pytest_user_{uuid4().hex[:8]}@example.com'
    user_response = client.post('/users', json={
        'name': 'Usuario Prueba',
        'email': email,
        'role': 'user',
        'is_active': True,
    })
    assert user_response.status_code == 201, user_response.text
    user_id = user_response.json()['id']

    device_response = client.post('/devices', json={
        'name': 'Laptop Prueba',
        'serial_number': f'TEST-SERIAL-{uuid4().hex[:8].upper()}',
        'device_type': 'laptop',
        'brand': 'Lenovo',
        'is_available': True,
    })
    assert device_response.status_code == 201, device_response.text
    device_id = device_response.json()['id']

    loan_response = client.post('/loans', json={
        'user_id': user_id,
        'device_id': device_id,
        'status': 'active',
        'loan_date': '2026-09-15T10:00:00',
    })
    assert loan_response.status_code == 201, loan_response.text
    loan_id = loan_response.json()['id']

    returned = client.patch(f'/loans/{loan_id}/return')
    assert returned.status_code == 200, returned.text
    payload = returned.json()
    assert payload['status'] == 'returned'

    lookup = client.get(f'/users/{user_id}/loans')
    assert lookup.status_code == 200, lookup.text
    assert isinstance(lookup.json(), list)

    device_details = client.get(f'/devices/{device_id}/loans')
    assert device_details.status_code == 200, device_details.text
    assert isinstance(device_details.json(), list)
