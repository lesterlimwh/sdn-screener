from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test(single_person_fixture):
    screening = single_person_fixture[0]

    assert screening['id'] == 1
    assert screening['name_match']
    assert screening['dob_match']
    assert screening['country_match']
