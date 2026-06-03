from fastapi import APIRouter, Depends, HTTPException, Body
from app.api.routers.generate_songs import get_user_spotify_token
from app.services.spotify import SpotifyService
from app.services.db_service import DBService
from pydantic import BaseModel
from typing import List
import httpx

router = APIRouter(
    prefix="/playlists",
    tags=["Playlists"],
)

class ExportPlaylistRequest(BaseModel):
    playlist_name: str
    track_ids: List[str]

@router.post("/export")
async def export_playlist(
    payload: ExportPlaylistRequest,
    spotify_token: str = Depends(get_user_spotify_token)
):
    if not payload.track_ids:
        raise HTTPException(status_code=400, detail="No track IDs provided")

    db = DBService()
    spotify = SpotifyService(access_token=spotify_token)
    
    try:
        # 1. Fetch user's profile to get Spotify ID
        profile = await spotify.get_current_user_profile()
        spotify_id = profile.get("id")
        
        if not spotify_id:
            raise HTTPException(status_code=400, detail="Could not retrieve Spotify ID")

        # 2. Create the playlist on Spotify
        playlist_id = await spotify.create_playlist(
            spotify_user_id=spotify_id, 
            name=payload.playlist_name
        )
        
        # 3. Add tracks to the new playlist
        await spotify.add_items_to_playlist(
            playlist_id=playlist_id, 
            track_ids=payload.track_ids
        )
        
        # 4. Save the playlist record in the database
        db.save_playlist(
            spotify_id=spotify_id,
            playlist_name=payload.playlist_name,
            track_ids=payload.track_ids
        )
        
        return {
            "message": "Playlist exported successfully",
            "playlist_id": playlist_id,
            "spotify_url": f"https://open.spotify.com/playlist/{playlist_id}"
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Spotify API error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
