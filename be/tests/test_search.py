import sys
from unittest.mock import MagicMock

# Pre-mock heavy ML dependencies that are not installed in the test environment
# before any app module is imported
for _mod in ("joblib", "pandas", "numpy", "sklearn", "sklearn.neighbors", "seaborn", "matplotlib"):
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

MOCK_ENV = {
    "SPOTIFY_CLIENT_ID": "test_id",
    "SPOTIFY_CLIENT_SECRET": "test_secret",
    "SPOTIFY_REDIRECT_URI": "http://localhost:8080/api/v1/auth/callback",
    "SECRET_KEY": "test_secret_key",
    "SUPABASE_URL": "http://fake-supabase",
    "SUPABASE_KEY": "fake_key",
}

MOCK_SPOTIFY_RESPONSE = {
    "tracks": {
        "items": [
            {
                "id": "4iV5W9uYEdYUVa79Axb7Rh",
                "name": "Neon",
                "artists": [{"name": "John Mayer"}],
                "album": {"images": [{"url": "https://i.scdn.co/image/abc"}]},
            }
        ]
    }
}


def _make_client():
    from app.app_factory import create_app
    return TestClient(create_app(), raise_server_exceptions=False)


@patch.dict(os.environ, MOCK_ENV)
@patch("app.api.routers.generate_songs.DBService")
@patch("app.api.routers.generate_songs.jwt.decode")
def test_search_songs_returns_results(mock_jwt, mock_db_class):
    mock_jwt.return_value = {"sub": "user-123"}
    mock_db = MagicMock()
    mock_db_class.return_value = mock_db
    mock_db.get_user_tokens.return_value = {
        "access_token": "sp_access",
        "refresh_token": "sp_refresh",
        "expires_at": "2099-01-01T00:00:00+00:00",
        "scope": "user-read-private",
    }

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_http = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_http
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = MOCK_SPOTIFY_RESPONSE
        mock_http.get = AsyncMock(return_value=mock_resp)

        client = _make_client()
        response = client.get(
            "/api/v1/search/songs?q=Neon",
            headers={"Authorization": "Bearer fake.jwt.token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["song_id"] == "4iV5W9uYEdYUVa79Axb7Rh"
    assert data[0]["name"] == "Neon"
    assert data[0]["artists"] == "John Mayer"


@patch.dict(os.environ, MOCK_ENV)
@patch("app.api.routers.generate_songs.DBService")
@patch("app.api.routers.generate_songs.jwt.decode")
def test_search_songs_empty_query(mock_jwt, mock_db_class):
    mock_jwt.return_value = {"sub": "user-123"}
    mock_db = MagicMock()
    mock_db_class.return_value = mock_db
    mock_db.get_user_tokens.return_value = {
        "access_token": "sp_access",
        "refresh_token": "sp_refresh",
        "expires_at": "2099-01-01T00:00:00+00:00",
        "scope": "user-read-private",
    }

    client = _make_client()
    response = client.get(
        "/api/v1/search/songs?q=%20",
        headers={"Authorization": "Bearer fake.jwt.token"},
    )
    assert response.status_code == 400


@patch.dict(os.environ, MOCK_ENV)
def test_search_songs_requires_auth():
    client = _make_client()
    response = client.get("/api/v1/search/songs?q=Neon")
    assert response.status_code == 401
