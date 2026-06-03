import logging
from app.core.database.supabase import get_supabase_client
from supabase import Client

logger = logging.getLogger(__name__)

class DBService:
    """Service to handle Supabase Database operations."""
    
    def __init__(self):
        # Initialize client here so if the server starts without env vars, 
        # it doesn't immediately crash unless the database is actually called.
        self.client: Client = get_supabase_client()

    def upsert_user(self, spotify_id: str, username: str):
        """
        Inserts a new user or updates their profile if they already exist.
        Matches the 'users' table from migrations.
        """
        data = {
            "spotify_id": spotify_id,
            "username": username
        }
        
        try:
            result = self.client.table('users').upsert(data, on_conflict='spotify_id').execute()
            return result.data
        except Exception as e:
            logger.error(f"Failed to upsert user in Supabase: {e}")
            raise e

    def upsert_user_tokens(self, user_id: str, access_token: str, refresh_token: str, expires_at: str, scope: str = ""):
        """
        Stores the Spotify OAuth tokens. Matches the 'user_tokens' table from migrations.
        """
        data = {
            "user_id": user_id, # This is the UUID from 'users' table
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "scope": scope
        }
        
        try:
            result = self.client.table('user_tokens').upsert(data, on_conflict='user_id').execute()
            return result.data
        except Exception as e:
            logger.error(f"Failed to upsert user tokens: {e}")
            raise e

    def get_user_tokens(self, user_id: str):
        """
        Fetch user tokens from the database.
        """
        try:
            result = self.client.table('user_tokens').select('*').eq('user_id', user_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to fetch user tokens: {e}")
            raise e

    def get_user_by_id(self, spotify_id: str):
        """
        Fetch a user from the database.
        """
        try:
            result = self.client.table('users').select('*').eq('spotify_id', spotify_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to fetch user: {e}")
            raise e

    def save_playlist(self, spotify_id: str, playlist_name: str, track_ids: list[str]):
        """
        Logs a generated playlist into the database for history/analytics.
        """
        data = {
            "user_id": spotify_id,
            "playlist_name": playlist_name,
            "tracks": track_ids  # Supabase supports JSON/Array columns!
        }
        try:
            result = self.client.table('playlists').insert(data).execute()
            return result.data
        except Exception as e:
            logger.error(f"Failed to save playlist: {e}")
            raise e
