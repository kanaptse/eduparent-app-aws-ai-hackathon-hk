import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "EduParent API", "status": "running"}


def test_health():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_daily_feed():
    """Test daily feed endpoint"""
    response = client.get("/api/feed/daily")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "streak" in data
    assert len(data["items"]) == 3


def test_calculator():
    """Test calculator endpoint"""
    response = client.post("/api/calculator/add", json={"a": 5.0, "b": 3.0})
    assert response.status_code == 200
    assert response.json() == {"result": 8.0}


def test_survey_goals():
    """Test survey goals endpoint"""
    response = client.get("/api/survey/goals")
    assert response.status_code == 200
    data = response.json()
    assert "goals" in data
    assert len(data["goals"]) == 4


def test_survey_submit():
    """Test survey submission"""
    survey_data = {
        "goal": "Improve study habits",
        "note": "Test note"
    }
    response = client.post("/api/survey/submit", json=survey_data)
    assert response.status_code == 200
    data = response.json()
    assert data["goal"] == "Improve study habits"
    assert data["note"] == "Test note"
    assert "recommendation" in data
    assert "tiny_actions" in data