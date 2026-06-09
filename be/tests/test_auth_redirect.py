import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@patch.dict(os.environ, {
    "SPOTIFY_CLIENT_ID": "test_id",
    "SPOTIFY_CLIENT_SECRET": "test_secret",
    "SPOTIFY_REDIRECT_URI": "http://localhost:8080/api/v1/auth/callback",
    "SECRET_KEY": "test_secret_key",
    "FRONTEND_URL": "http://localhost:3000/auth-callback",
    "SUPABASE_URL": "http://fake-supabase",
    "SUPABASE_KEY": "fake_key",
})
@patch("app.api.routers.auth.DBService")
def test_callback_redirects_to_frontend(mock_db_class):
    mock_db = MagicMock()
    mock_db_class.return_value = mock_db
    mock_db.upsert_user.return_value = [{"id": "user-uuid-123"}]
    mock_db.upsert_user_tokens.return_value = None

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        token_resp = MagicMock()
        token_resp.status_code = 200
        token_resp.json.return_value = {
            "access_token": "sp_access",
            "refresh_token": "sp_refresh",
            "expires_in": 3600,
            "scope": "user-read-private",
        }
        profile_resp = MagicMock()
        profile_resp.status_code = 200
        profile_resp.json.return_value = {"id": "spotify_user", "display_name": "Test User"}

        mock_client.post = AsyncMock(return_value=token_resp)
        mock_client.get = AsyncMock(return_value=profile_resp)

        from app.app_factory import create_app
        app = create_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/v1/auth/callback?code=test_code", follow_redirects=False)

    assert response.status_code == 302
    assert "http://localhost:3000/auth-callback?token=" in response.headers["location"]
