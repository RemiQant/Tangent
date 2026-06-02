import asyncio
from unittest.mock import patch, MagicMock
from app.api.routers.generate_songs import get_user_spotify_token
import os
import jwt
from datetime import datetime, timezone, timedelta

os.environ["SECRET_KEY"] = "fallback-secret-for-dev"
os.environ["ALGORITHM"] = "HS256"

async def run_test():
    with patch("app.api.routers.generate_songs.DBService") as mock_db, \
         patch("httpx.AsyncClient.post") as mock_post:
        
        # Valid JWT
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(days=1)}
        valid_jwt = jwt.encode(payload, "fallback-secret-for-dev", algorithm="HS256")
        
        # Scenario 1: Token valid and not expired
        mock_db_instance = mock_db.return_value
        future_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        mock_db_instance.get_user_tokens.return_value = {
            "access_token": "valid_spotify_token",
            "refresh_token": "valid_refresh",
            "expires_at": future_time
        }
        
        token = await get_user_spotify_token(authorization=f"Bearer {valid_jwt}")
        assert token == "valid_spotify_token", f"Got: {token}"
        print("Scenario 1 passed")

        # Scenario 2: Token needs refresh
        past_time = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        mock_db_instance.get_user_tokens.return_value = {
            "access_token": "expired_spotify_token",
            "refresh_token": "valid_refresh",
            "expires_at": past_time
        }
        
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 200
        mock_post_resp.json.return_value = {
            "access_token": "new_refreshed_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_post_resp
        
        token2 = await get_user_spotify_token(authorization=f"Bearer {valid_jwt}")
        assert token2 == "new_refreshed_token", f"Got: {token2}"
        mock_db_instance.upsert_user_tokens.assert_called_once()
        print("Scenario 2 passed")

if __name__ == "__main__":
    asyncio.run(run_test())
