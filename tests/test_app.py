import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_for_activity():
    email = "testuser@mergington.edu"
    activity = "Chess Club"
    # Remove if already present
    client.post(f"/activities/{activity}/remove?email={email}")
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert f"Signed up {email} for {activity}" in response.json()["message"]
    # Try duplicate signup
    response2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert response2.status_code == 400
    # Clean up
    client.post(f"/activities/{activity}/remove?email={email}")

def test_remove_participant():
    email = "removeuser@mergington.edu"
    activity = "Programming Class"
    # Ensure user is not present
    client.post(f"/activities/{activity}/remove?email={email}")
    # Add user
    client.post(f"/activities/{activity}/signup?email={email}")
    # Check user is present
    activities_resp = client.get("/activities")
    participants = activities_resp.json()[activity]["participants"]
    assert email in participants, f"{email} not in participants after signup: {participants}"
    # Remove user
    response = client.post(f"/activities/{activity}/remove?email={email}")
    if response.status_code != 200:
        # Print debug info
        activities_resp = client.get("/activities")
        print("Participants after failed remove:", activities_resp.json()[activity]["participants"])
    assert response.status_code == 200
    assert f"Removed {email} from {activity}" in response.json()["message"]
    # Try removing again
    response2 = client.post(f"/activities/{activity}/remove?email={email}")
    assert response2.status_code == 404

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=foo@bar.com")
    assert response.status_code == 404

def test_remove_activity_not_found():
    response = client.post("/activities/Nonexistent/remove?email=foo@bar.com")
    assert response.status_code == 404
