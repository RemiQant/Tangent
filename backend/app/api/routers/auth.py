from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
import os
import httpx
import jwt
from datetime import datetime, timedelta, timezone
from app.services.db_service import DBService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
JWT_SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-for-dev")
JWT_ALGORITHM = os.getenv("ALGORITHM", "HS256")

@router.get("/login")
async def login_to_spotify():
    """
    Redirects the user to Spotify's OAuth2 login page.
    """
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Spotify credentials are not configured.")
    
    # Spotify authorization Scopes needed
    scopes = "user-read-private user-read-email playlist-modify-public playlist-modify-private"
    
    spotify_auth_url = (
        f"https://accounts.spotify.com/authorize?"
        f"response_type=code&"
        f"client_id={SPOTIFY_CLIENT_ID}&"
        f"scope={scopes}&"
        f"redirect_uri={SPOTIFY_REDIRECT_URI}"
    )
    
    return RedirectResponse(spotify_auth_url)

@router.get("/callback")
async def spotify_callback(code: str = Query(...)):
    """
    Callback handler for after the user logs in. 
    Spotify sends back an authorization check 'code', which we exchange for an access token.
    """
    async with httpx.AsyncClient() as client:
        token_url = "https://accounts.spotify.com/api/token"
        
        response = await client.post(
            token_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": SPOTIFY_REDIRECT_URI,
            },
            auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to retrieve Spotify tokens")
            
        token_data = response.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")
        scope = token_data.get("scope", "")

        # 1. Fetch user's Spotify profile using the access token
        profile_response = await client.get(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if profile_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to retrieve Spotify profile")
            
        profile = profile_response.json()
        spotify_id = profile.get("id")
        username = profile.get("display_name") or spotify_id

        # 2. Save the user and the refresh_token to Supabase
        db = DBService()
        user_data = db.upsert_user(spotify_id=spotify_id, username=username)
        # Assuming upsert returns a list of inserted records
        user_id = user_data[0]["id"] if isinstance(user_data, list) and len(user_data) > 0 else None
        
        if not user_id:
            raise HTTPException(status_code=500, detail="Failed to create or retrieve user from database")

        expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()
        db.upsert_user_tokens(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            scope=scope
        )

        # 3. Issue a local session/JWT to the frontend
        jwt_payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(days=7)
        }
        session_token = jwt.encode(jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        
        return {
            "message": "Successfully authenticated with Spotify!",
            "token": session_token
        }
