# Handoff: Tangent Backend & ML Engine

## Project Context
*   **Role:** Senior Software & AI Engineer
*   **Application:** Spotify Playlist Recommender System (Tangent)
*   **Architecture:** FastAPI Monolith (Backend + ML integrated)
*   **Core Stack:** Python (FastAPI), Supabase (PostgreSQL Database), Scikit-Learn/FAISS (KNN Model).
*   **Data Flow:** Seed Song -> KNN Math (finds 100 closest acoustic matches) -> Spotify API (Hydrates Artist/Genre data) -> Genre Filter (Prunes down to max 30 songs that match seed's genres) -> User Exports to Spotify.

## What Has Been Completed ✅
1.  **Architecture & Database Setup:** Python FastAPI monolith with Supabase integration. Migrations applied for `users`, `user_tokens`, and playlist history tables.
2.  **ML + Spotify Orchestration:** 
    *   `app/services/spotify.py` dynamically fetches Artist/Genre data in chunks.
    *   `app/services/filter.py` filters raw KNN math logic down to only matching genres.
3.  **Authentication & Local JWT (Phase 1 Completed):** 
    *   Full Spotify OAuth2 flow built in `app/api/routers/auth.py`. 
    *   Fetches the user's Spotify profile, upserts user data to Supabase exactly matching DB schemas.
    *   Exchanges Spotify tokens and stores them in `user_tokens` table.
    *   Issues a secure **local JWT Session Token** back to the client to keep native Spotify tokens hidden.
4.  **Secure Token Passing & Refresh (Phase 1 Completed):** 
    *   `get_user_spotify_token` dependency added to routes.
    *   Securely decodes the local JWT `Bearer` token to identify the user.
    *   Automatically fetches their real Spotify token from Supabase, and transparently interacts with Spotify's `refresh_token` endpoint if the access token has < 5 minutes until expiration.
5.  **Playlist Export Endpoint (Phase 2 Completed):**
    *   New isolated router at `app/api/routers/playlists.py`.
    *   `POST /api/v1/playlists/export` endpoint created.
    *   Fetches current user profile, uses `spotify.py` to create a Spotify Playlist natively on the user's account, and bulk-adds track IDs using Spotify URIs.
    *   Logs the exported playlist metadata back into Supabase for analytics using `DBService.save_playlist`.
    *   Test scripts (`test_auth.py`, `test_token.py`, `test_playlist.py`) were successfully run leveraging mocks.

## Current API Endpoints
*   `GET /api/v1/auth/login` - Redirects to Spotify OAuth page.
*   `GET /api/v1/auth/callback` - Spotify callback, returns the JWT.
*   `POST /api/v1/recommendations/songs` - Takes a seed song, returns KNN + genre filtered tracks. (Requires `Authorization: Bearer <JWT>`)
*   `POST /api/v1/playlists/export` - Takes array of track IDs, creates a playlist on the user's real Spotify account. (Requires `Authorization: Bearer <JWT>`)

## Next Steps (Start Here in New Chat) 🚀

**1. Spotify App Configuration (Prerequisite)**
*   Go to Spotify Developer Dashboard, create an app, and set the Redirect URI to `http://localhost:8080/api/v1/auth/callback`.
*   Populate `backend/.env/.env.development` with: 
    *   `SPOTIFY_CLIENT_ID`
    *   `SPOTIFY_CLIENT_SECRET`
    *   `SPOTIFY_REDIRECT_URI`
    *   `SECRET_KEY` (Random string for JWT signing)
    *   `ALGORITHM=HS256`

**2. Frontend Integration**
*   The Backend is officially complete. Transition to building the Frontend (React, Next.js, Vue, etc.).
*   Connect the Frontend to `GET /api/v1/auth/login`. Extract the JWT from the `/callback` JSON response and store it securely (localStorage, HttpOnly cookies, etc.).
*   Pass the JWT in the `Authorization: Bearer <token>` header for `/recommendations/songs` and `/playlists/export`.

**3. Model & Feature Tuning (Optional)**
*   The ML model currently returns max 100 songs before genre filtering pruning it to max 30. Test if accuracy is strong enough or if hyperparameters require adjusting.

## Quick CLI Reference
*   **Start Server:** `cd backend && export $(cat .env/.env.development | xargs) && uv run uvicorn main:app --port 8080 --reload`
