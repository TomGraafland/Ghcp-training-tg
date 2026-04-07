"""
Backend tests for FastAPI app using the AAA (Arrange-Act-Assert) pattern.

Arrange: Set up test client and data
Act:     Make the API call
Assert:  Check the response and side effects
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_list_activities():
    # Arrange
    # (No special setup needed, just use the test client)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_for_activity():
    # Arrange
    email = "testuser@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert f"Signed up {email}" in data["message"] or f"{email} is already signed up" in data["message"]
    # Confirm participant is in the list
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    # Arrange
    email = "duplicate@mergington.edu"
    activity = "Programming Class"
    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]
    # Confirm only one instance in participants
    activities = client.get("/activities").json()
    assert activities[activity]["participants"].count(email) == 1


def test_unregister_participant():
    # Arrange
    email = "remove@mergington.edu"
    activity = "Gym Class"
    # Ensure participant is signed up
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert f"Removed {email}" in data["message"]
    # Confirm participant is removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_participant():
    # Arrange
    email = "notfound@mergington.edu"
    activity = "Art Studio"

    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Participant not found" in data["detail"]


def test_signup_nonexistent_activity():
    # Arrange
    email = "ghost@mergington.edu"
    activity = "Nonexistent Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]
