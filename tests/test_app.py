import uuid

from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity check for an expected activity
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    activity = "Chess Club"

    # ensure email not already present (clean up if needed)
    activities = app_module.activities
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert f"Signed up {email}" in resp.json().get("message", "")

    # verify appears in activities
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert email in data[activity]["participants"]

    # unregister
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert f"Unregistered {email}" in resp.json().get("message", "")

    # verify removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]


def test_unregister_nonexistent_returns_404():
    email = f"notfound-{uuid.uuid4().hex[:8]}@example.com"
    resp = client.delete(f"/activities/Chess Club/participants?email={email}")
    assert resp.status_code == 404
