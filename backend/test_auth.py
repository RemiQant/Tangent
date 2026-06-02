import asyncio
from unittest.mock import patch, MagicMock
from app.api.routers.auth import spotify_callback
from app.services.db_service import DBService
import os

os.environ["SECRET_KEY"] = "test-secret"
os.environ["ALGORITHM"] = "HS256"

async def run_test():
    with patch("httpx.AsyncClient.post") as mock_post, \
         patch("httpx.AsyncClient.get") as mock_get, \
         patch.object(DBService, 'upsert_user') as mock_upsert_user, \
         patch.object(DBService, 'upsert_user_tokens') as mock_upsert_tokens:
        
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 200
        mock_post_resp.json.return_value = {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "expires_in": 3600,
            "scope": "user-read-private"
        }
        mock_post.return_value = mock_post_resp
        
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = {
            "id": "test_spotify_user",
            "display_name": "Test User"
        }
        mock_get.return_value = mock_get_resp

        mock_upsert_user.return_value = [{"id": "123e4567-e89b-12d3-a456-426614174000"}]
        mock_upsert_tokens.return_value = None
        
        result = await spotify_callback(code="dummy_code")
        print("Test resulted in:", result)
        assert "token" in result
        assert result["message"] == "Successfully authenticated with Spotify!"
        print("Auth logic tested successfully!")

if __name__ == "__main__":
    asyncio.run(run_test())
