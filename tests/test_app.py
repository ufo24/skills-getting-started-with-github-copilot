import pytest
from copy import deepcopy
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: preserve the initial state and reset after each test
    original_state = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_state)


def test_root_redirects_to_static_index():
    # Arrange
    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert "/static/index.html" in str(response.url)



def test_get_activities_returns_all_activities():
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Programming Class" in payload
    assert isinstance(payload["Chess Club"], dict)


def test_signup_for_activity_success():
    # Arrange
    activity_name = "Tennis Team"
    email = "newuser@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_already_signed_up():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_activity_not_found():
    # Arrange
    activity_name = "NonExistentClub"
    email = "someone@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity_success():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    assert email in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_from_activity_not_registered():
    # Arrange
    activity_name = "Tennis Team"
    email = "nonmember@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"


def test_unregister_from_activity_not_found():
    # Arrange
    activity_name = "GhostClub"
    email = "someone@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
