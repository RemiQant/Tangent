import asyncio
from unittest.mock import patch, AsyncMock
from app.api.routers.playlists import export_playlist, ExportPlaylistRequest

async def run_test():
    with patch("app.api.routers.playlists.SpotifyService") as mock_spotify_cls, \
         patch("app.api.routers.playlists.DBService") as mock_db_cls:
         
        mock_spotify = mock_spotify_cls.return_value
        mock_spotify.get_current_user_profile = AsyncMock(return_value={"id": "test_spotify_id"})
        mock_spotify.create_playlist = AsyncMock(return_value="new_playlist_id")
        mock_spotify.add_items_to_playlist = AsyncMock(return_value=None)
        
        mock_db = mock_db_cls.return_value
        
        payload = ExportPlaylistRequest(
            playlist_name="My Cool Playlist",
            track_ids=["trk1", "trk2", "trk3"]
        )
        
        result = await export_playlist(payload=payload, spotify_token="valid_spotify_token")
        
        assert result["playlist_id"] == "new_playlist_id"
        assert result["message"] == "Playlist exported successfully"
        mock_spotify.add_items_to_playlist.assert_awaited_once_with(
            playlist_id="new_playlist_id", 
            track_ids=["trk1", "trk2", "trk3"]
        )
        mock_db.save_playlist.assert_called_once_with(
            spotify_id="test_spotify_id",
            playlist_name="My Cool Playlist",
            track_ids=["trk1", "trk2", "trk3"]
        )
        print("Playlist export logic tested successfully!")

if __name__ == "__main__":
    asyncio.run(run_test())
