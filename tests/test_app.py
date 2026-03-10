import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


# copy of original activities to reset state
_original_activities = {
    name: details.copy()
    for name, details in activities.items()
}


def reset_state():
    activities.clear()
    activities.update({name: details.copy() for name, details in _original_activities.items()})


@pytest.fixture(autouse=True)
def auto_reset():
    reset_state()


def test_get_activities():
    # Arrange
    # Act
    resp = client.get("/activities")
    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success_and_duplicate():
    # Arrange
    email = "tester@example.com"
    # Act
    r1 = client.post("/activities/Chess Club/signup", params={"email": email})
    # Assert
    assert r1.status_code == 200
    assert r1.json() == {"message": f"Signed up {email} for Chess Club"}

    # Act duplicate
    r2 = client.post("/activities/Chess Club/signup", params={"email": email})
    assert r2.status_code == 400
    assert r2.json()["detail"] == "Student already signed up"


def test_signup_nonexistent_activity():
    # Arrange
    # Act
    r = client.post("/activities/NoSuch/signup", params={"email": "x"})
    # Assert
    assert r.status_code == 404
    assert r.json()["detail"] == "Activity not found"


def test_unregister_success_and_errors():
    # Arrange
    email = "remove@example.com"
    client.post("/activities/Chess Club/signup", params={"email": email})

    # Act success
    r1 = client.delete("/activities/Chess Club/unregister", params={"email": email})
    # Assert
    assert r1.status_code == 200
    assert r1.json() == {"message": f"Unregistered {email} from Chess Club"}

    # Act error not signed
    r2 = client.delete("/activities/Chess Club/unregister", params={"email": email})
    assert r2.status_code == 400
    assert r2.json()["detail"] == "Student not signed up for this activity"

    # Act nonexistent activity
    r3 = client.delete("/activities/Unknown/unregister", params={"email": email})
    assert r3.status_code == 404
    assert r3.json()["detail"] == "Activity not found"


def test_unregister_nonexistent_activity():
    # Arrange
    # Act
    r = client.delete("/activities/Nonexistent/unregister", params={"email": "foo"})
    # Assert
    assert r.status_code == 404
    assert r.json()["detail"] == "Activity not found"