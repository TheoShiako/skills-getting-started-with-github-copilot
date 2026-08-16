from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_signup_and_unregister_participant():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200, signup_response.text
    assert email in signup_response.json()["message"]

    activities = client.get("/activities")
    assert email in activities.json()[activity_name]["participants"]

    unregister_response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )
    assert unregister_response.status_code == 200, unregister_response.text
    assert "unregistered" in unregister_response.json()["message"].lower()

    updated_activities = client.get("/activities")
    assert email not in updated_activities.json()[activity_name]["participants"]


def test_unregistering_missing_participant_returns_404():
    activity_name = "Basketball Team"
    email = "missingstudent@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
