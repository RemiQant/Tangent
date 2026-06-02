from fastapi import APIRouter, Request, Depends, HTTPException, Header
from app.ml import generate_similar_songs, PredictRequest, PredictResponse
from app.core.exceptions import LoadError
from app.middleware.rate_limit import limiter
from app.services.spotify import SpotifyService
from app.services.filter import filter_songs_by_genre
from app.services.db_service import DBService
import os
import jwt
import httpx
from datetime import datetime, timezone, timedelta

router = APIRouter()

JWT_SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-for-dev")
JWT_ALGORITHM = os.getenv("ALGORITHM", "HS256")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

async def get_user_spotify_token(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid session token")

    db = DBService()
    user_tokens = db.get_user_tokens(user_id)
    if not user_tokens:
        raise HTTPException(status_code=401, detail="Spotify tokens not found for user")

    access_token = user_tokens.get("access_token")
    refresh_token = user_tokens.get("refresh_token")
    expires_at_str = user_tokens.get("expires_at")
    
    if expires_at_str:
        # Supabase returns ISO format strings like "2026-05-27T10:00:00+00:00"
        try:
            expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
        except ValueError:
            expires_at = datetime.min.replace(tzinfo=timezone.utc)
            
        # Refresh if expiring in less than 5 minutes
        if datetime.now(timezone.utc) >= expires_at - timedelta(minutes=5):
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://accounts.spotify.com/api/token",
                    data={"grant_type": "refresh_token", "refresh_token": refresh_token},
                    auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                if resp.status_code == 200:
                    token_data = resp.json()
                    access_token = token_data.get("access_token")
                    new_refresh = token_data.get("refresh_token", refresh_token)
                    new_expires_at = (datetime.now(timezone.utc) + timedelta(seconds=token_data.get("expires_in", 3600))).isoformat()
                    db.upsert_user_tokens(user_id, access_token, new_refresh, new_expires_at, user_tokens.get("scope", ""))
                else:
                    raise HTTPException(status_code=401, detail="Failed to refresh Spotify token")

    return access_token


@router.post("/songs", response_model=PredictResponse)
@limiter.limit("5/minute")
async def get_song_recommendations(
    payload: PredictRequest, 
    request: Request,
    spotify_token: str = Depends(get_user_spotify_token)
):
    model = getattr(request.app.state, "knn_model", None)
    df = getattr(request.app.state, "music_df", None)

    if model is None or df is None:
        raise LoadError(f"Model or dataset is not loaded. song_id={payload.song_id}")

    # 1. Get the Top 100 mathematical recommendations from KNN
    knn_response = generate_similar_songs(
        song_id=payload.song_id,
        model=model,
        df=df,
        max_distance=payload.max_distance
    )
    
    # Extract just the IDs from the KNN recommendations
    knn_track_ids = [rec.song_id for rec in knn_response.recommendations]
    
    # 2. Initialize Spotify Service
    spotify = SpotifyService(access_token=spotify_token)
    
    # 3. Get the Seed Track's Artist and Genres
    seed_track_artist_map = await spotify.get_track_artists([payload.song_id])
    seed_artist_id = seed_track_artist_map.get(payload.song_id)
    
    seed_genres = []
    if seed_artist_id:
        seed_artist_genre_map = await spotify.get_artist_genres([seed_artist_id])
        seed_genres = seed_artist_genre_map.get(seed_artist_id, [])
    
    # 4. Get Artists and Genres for the 100 KNN predictions
    track_to_artist = await spotify.get_track_artists(knn_track_ids)
    
    # Unique artist IDs to avoid hitting Spotify API multiple times for the same artist
    unique_artist_ids = list(set(track_to_artist.values()))
    artist_genres = await spotify.get_artist_genres(unique_artist_ids)
    
    # 5. Filter the mathematically similar songs by the seed song's genres
    filtered_track_ids = filter_songs_by_genre(
        generated_track_ids=knn_track_ids,
        seed_genres=seed_genres,
        track_to_artist=track_to_artist,
        artist_genres=artist_genres,
        max_songs=30
    )
    
    # 6. Re-map the filtered IDs back to the rich SongRecommendation objects
    # to maintain the original PredictResponse schema format
    final_recommendations = [
        rec for rec in knn_response.recommendations 
        if rec.song_id in filtered_track_ids
    ]
    
    # Fail-safe just in case extreme genre filtering removes too many songs
    if len(final_recommendations) < 10:
        raise HTTPException(
            status_code=422, 
            detail="Not enough songs left after genre filtering. Try a different seed track."
        )
    
    # Return the clean, filtered response
    return PredictResponse(
        seed_song_id=payload.song_id,
        total_recommendations=len(final_recommendations),
        recommendations=final_recommendations
    )
