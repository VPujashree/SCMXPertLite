from fastapi.testclient import TestClient
from app import app  # Assuming your app is in app.py

client = TestClient(app)

def test_signup():
    response = client.post("/signup", data={
        "full_name": "John Doe",
        "email": "john@example.com",
        "username": "johndoe",
        "password": "secret123",
        "confirm_password": "secret123"
    })
    assert response.status_code == 303  # Redirect to login after signup

def test_login():
    response = client.post("/token", data={
        "username": "johndoe",
        "password": "secret123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_dashboard():
    login_response = client.post("/token", data={
        "username": "johndoe",
        "password": "secret123"
    })
    token = login_response.json()["access_token"]
    response = client.get("/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
