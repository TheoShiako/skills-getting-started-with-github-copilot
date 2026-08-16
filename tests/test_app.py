from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_activity_catalog():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200, response.text
    body = response.json()
    assert expected_activity in body
    assert "participants" in body[expected_activity]
    assert isinstance(body[expected_activity]["participants"], list)


def test_signup_for_activity_registers_new_student():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200, response.text
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_for_existing_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400, response.text
    assert "already signed up" in response.json()["detail"].lower()


def test_unregistering_participant_removes_them_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    activities[activity_name]["participants"].append(email)

    # Act
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200, response.text
    assert "unregistered" in response.json()["message"].lower()
    assert email not in activities[activity_name]["participants"]


def test_unregistering_missing_participant_returns_404():
    # Arrange
    activity_name = "Basketball Team"
    email = "missingstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404, response.text
    assert "not found" in response.json()["detail"].lower()


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    activity_name = "Unknown Activity"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404, response.text
    assert "not found" in response.json()["detail"].lower()
