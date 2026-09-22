import os
import subprocess
import sys
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


def test_phase_13_minimal_functional_scenarios():
    migration_dir = os.path.join('alembic', 'versions')
    assert os.path.isdir(migration_dir)
    migration_files = os.listdir(migration_dir)
    assert any('create_devices_and_loans_tables' in name for name in migration_files)

    history = subprocess.run(
        [sys.executable, '-m', 'alembic', 'history'],
        capture_output=True,
        text=True,
        cwd='.',
    )
    assert history.returncode == 0, history.stderr or history.stdout
    assert 'create devices and loans tables' in history.stdout

    user_email = f'pytest_user_{uuid4().hex[:8]}@example.com'
    user_response = client.post('/users', json={
        'name': 'Usuario Prueba',
        'email': user_email,
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

    second_user = client.post('/users', json={
        'name': 'Usuario Bloqueado',
        'email': f'pytest_user_{uuid4().hex[:8]}@example.com',
        'role': 'user',
        'is_active': True,
    })
    assert second_user.status_code == 201, second_user.text
    second_user_id = second_user.json()['id']

    unavailable_response = client.post('/loans', json={
        'user_id': second_user_id,
        'device_id': device_id,
        'status': 'active',
        'loan_date': '2026-09-16T12:00:00',
    })
    assert unavailable_response.status_code == 409, unavailable_response.text
    assert 'no está disponible' in unavailable_response.json()['detail']

    loans_response = client.get('/loans')
    assert loans_response.status_code == 200, loans_response.text
    loans_payload = loans_response.json()
    assert isinstance(loans_payload, list)
    assert any(item.get('user', {}).get('id') == user_id for item in loans_payload)
    assert any(item.get('device', {}).get('id') == device_id for item in loans_payload)

    details_response = client.get('/loans/details')
    assert details_response.status_code == 200, details_response.text
    details_payload = details_response.json()
    assert isinstance(details_payload, list)
    assert any(item.get('id') == loan_id for item in details_payload)
    current_loan_detail = next(item for item in details_payload if item['id'] == loan_id)
    assert current_loan_detail['user']['email'] == user_email
    assert current_loan_detail['device']['id'] == device_id

    active_response = client.get('/loans?status=active')
    assert active_response.status_code == 200, active_response.text
    active_payload = active_response.json()
    assert all(item['status'] == 'active' for item in active_payload)

    laptop_response = client.get('/loans?device_type=laptop')
    assert laptop_response.status_code == 200, laptop_response.text
    laptop_payload = laptop_response.json()
    assert all(item['device']['device_type'] == 'laptop' for item in laptop_payload)

    user_loans_response = client.get(f'/users/{user_id}/loans')
    assert user_loans_response.status_code == 200, user_loans_response.text
    user_loans_payload = user_loans_response.json()
    assert any(item['id'] == loan_id for item in user_loans_payload)

    returned = client.patch(f'/loans/{loan_id}/return')
    assert returned.status_code == 200, returned.text
    assert returned.json()['status'] == 'returned'

    device_after_return = client.get(f'/devices/{device_id}')
    assert device_after_return.status_code == 200, device_after_return.text
    assert device_after_return.json()['is_available'] is True

    device_history = client.get(f'/devices/{device_id}/loans')
    assert device_history.status_code == 200, device_history.text
    assert isinstance(device_history.json(), list)
    assert any(item['id'] == loan_id for item in device_history.json())
