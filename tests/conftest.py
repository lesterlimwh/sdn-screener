import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

@pytest.fixture(scope='module')
def single_person_fixture():
    person_data = [
        {
            "id": 1,
            "name": "Abu Abbas",
            "dob": "1948-12-10",
            "country": "Yemen"
        }
    ]
    response = client.post('/api/v1/screen/', json=person_data)
    assert response.status_code == 200
    return response.json()

@pytest.fixture(scope='module')
def multiple_people_fixture():
    person_data = [
        {
            "id": 1,
            "name": "Ubaidullah Akhund Sher Mohammed",
            "dob": "1950-01-01",
            "country": "Afghanistan"
        },
        {
            "id": 2,
            "name": "Abu Abbas",
            "dob": "1948-12-10",
            "country": "Yemen"
        }
    ]
    response = client.post('/api/v1/screen/', json=person_data)
    assert response.status_code == 200
    return response.json()
