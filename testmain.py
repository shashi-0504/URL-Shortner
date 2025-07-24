import pytest
from app.main import app
import json

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_shorten_url(client):
    response = client.post("/api/shorten", json={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.get_json()
    assert "short_code" in data
    assert "short_url" in data

def test_invalid_url(client):
    response = client.post("/api/shorten", json={"url": "not_a_url"})
    assert response.status_code == 400

def test_redirect_and_stats(client):
    response = client.post("/api/shorten", json={"url": "https://example.com"})
    short_code = response.get_json()["short_code"]

    for _ in range(3):
        redirect = client.get(f"/{short_code}")
        assert redirect.status_code == 302

    stats = client.get(f"/api/stats/{short_code}").get_json()
    assert stats["clicks"] == 3
    assert stats["url"] == "https://example.com"

def test_404_on_invalid_code(client):
    assert client.get("/invalid123").status_code == 404
    assert client.get("/api/stats/invalid123").status_code == 404
