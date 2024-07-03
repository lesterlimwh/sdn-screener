from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_single_person_screening(single_person_fixture):
    screening = single_person_fixture[0]

    assert screening['id'] == 1
    assert screening['name_match']
    assert screening['dob_match']
    assert screening['country_match']

def test_multiple_people_screening(multiple_people_fixture):
    screenings = multiple_people_fixture

    first_person = screenings[0]
    second_person = screenings[1]

    assert first_person['id'] == 1
    assert first_person['name_match']
    assert not first_person['dob_match']
    assert first_person['country_match']

    assert second_person['id'] == 2
    assert second_person['name_match']
    assert second_person['dob_match']
    assert second_person['country_match']

def test_unprocessable_entity():
    person_data = [
        {
            "id": 1
        }
    ]
    response = client.post('/api/v1/screen/', json=person_data)
    assert response.status_code == 422
