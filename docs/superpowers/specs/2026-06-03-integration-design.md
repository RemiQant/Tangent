# SonicPro × Tangent Backend — Integration Design Spec

**Date:** 2026-06-03
**Approach:** Monorepo (fe/ + be/) · BE as single Spotify gateway · Login required

---

## 1. Overview

Wire the existing SonicPro Next.js frontend to the Tangent FastAPI + KNN backend. The FE stops using mock data and talks exclusively to the BE. The BE adds one new endpoint for Spotify song search so the FE never needs its own Spotify credentials.

**Result:** A working end-to-end flow — user logs in with Spotify, searches a song, gets AI-curated recommendations, and can export them back to Spotify.

---

## 2. Monorepo Structure

Create a new root at `Tangent-Monorepo/` (or rename current working dir). Move FE files into `fe/`, copy BE into `be/`.

```
Tangent-Monorepo/
├── fe/                          ← Next.js 14 app (moved from Tangent/)
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   ├── tests/
│   ├── .env.local               ← NEXT_PUBLIC_API_URL=http://localhost:8080
│   ├── package.json
│   ├── tailwind.config.ts
│   └── ...
├── be/                          ← FastAPI backend (from Tangent-backend/backend/)
│   ├── app/
│   │   ├── api/
│   │   │   └── routers/
│   │   │       ├── auth.py
│   │   │       ├── generate_songs.py
│   │   │       ├── playlists.py
│   │   │       ├── search.py    ← NEW
│   │   │       └── users.py
│   │   ├── ml/
│   │   ├── services/
│   │   └── ...
│   ├── models/
│   │   └── knn_model.pkl
│   ├── data/processed/
│   │   └── spotify_features_scaled.csv
│   ├── main.py
│   ├── pyproject.toml
│   └── .env/.env.development    ← Spotify + Supabase secrets
├── .gitignore
└── README.md
```

**Dev ports:**
- FE: `http://localhost:3000`
- BE: `http://localhost:8080`

---

## 3. Backend Changes

### 3.1 New Endpoint: Song Search

```
GET /api/v1/search/songs?q=<query>&limit=5
Authorization: Bearer <JWT>
```

**Implementation:** BE calls Spotify Search API using the authenticated user's access token (retrieved via `get_user_spotify_token` dependency — already used in other routes). Searches `type=track`. Returns simplified results.

**Response `200`:**
```json
[
  {
    "song_id": "4iV5W9uYEdYUVa79Axb7Rh",
    "name": "Neon",
    "artists": "John Mayer",
    "album_art_url": "https://i.scdn.co/image/..."
  }
]
```

**Errors:**
- `401` — missing/invalid JWT or Spotify token not refreshable
- `400` — empty query string
- `422` — Spotify API returned no results
- `429` — rate limited

**File:** `be/app/api/routers/search.py`
**Schema:** `SongSearchResult` Pydantic model in `be/app/ml/schemas/`
**Rate limit:** 10/minute per IP (via `slowapi`, same pattern as generate_songs)

### 3.2 Wire search router into app factory

In `be/app/api/routers/__init__.py`, include the new search router under `/api/v1/search`.

### 3.3 No other BE changes

Auth, recommendations, playlists, users, health — all unchanged.

---

## 4. Frontend Changes

### 4.1 Environment

`fe/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8080
```

### 4.2 New Types (`fe/lib/types.ts` additions)

```typescript
export interface SongResult {
  song_id: string
  name: string
  artists: string
  album_art_url: string
}

export interface SongRecommendation {
  song_id: string
  name: string
  artists: string
  distance_score: number
  danceability: number
  energy: number
  speechiness: number
  acousticness: number
  instrumentalness: number
  liveness: number
  valence: number
  tempo: number
}

export interface RecommendationResponse {
  seed_song_id: string
  total_recommendations: number
  recommendations: SongRecommendation[]
}

export interface ExportResult {
  message: string
  playlist_id: string
  spotify_url: string
}
```

### 4.3 Auth Helpers (`fe/lib/auth.ts`)

```typescript
const TOKEN_KEY = 'sonicpro_jwt'

export function getToken(): string | null
export function setToken(jwt: string): void
export function clearToken(): void
export function isAuthenticated(): boolean
// Parse token from URL on callback redirect, call setToken, redirect to /
export function handleAuthCallback(): void
```

### 4.4 API Client (`fe/lib/api.ts`)

Single typed client. Base URL from `process.env.NEXT_PUBLIC_API_URL`.
All requests auto-attach `Authorization: Bearer <token>`.
On `401` response: clear token + redirect to `/login`.

```typescript
const api = {
  search: {
    songs(q: string, limit = 5): Promise<SongResult[]>
  },
  recommendations: {
    getSongs(songId: string, maxDistance?: number): Promise<RecommendationResponse>
  },
  playlists: {
    export(name: string, trackIds: string[]): Promise<ExportResult>
  },
}

export default api
```

### 4.5 Auth Flow

```
/login page
  → "Connect with Spotify" button
  → window.location.href = `${API_URL}/api/v1/auth/login`
  → Spotify OAuth (BE handles everything)
  → BE redirects to: http://localhost:3000/?token=<JWT>
  → FE root reads ?token, calls setToken(jwt), strips URL param, shows app
```

**Auth guard in `fe/app/(app)/layout.tsx`:**
- On mount: check `isAuthenticated()`
- If false: `router.replace('/login')`
- If true: render children

### 4.6 New / Changed Pages & Components

#### New: Login Page (`fe/app/(auth)/login/page.tsx`)
- Dark glassmorphism, SonicPro brand
- Single CTA: "Connect with Spotify" (green primary button)
- No sidebar (outside `(app)` route group)

#### Changed: Generator Dashboard (`fe/app/(app)/page.tsx`)
- Remove `PlaylistInput` (URL field)
- Add `SongSearchInput` component — debounced text field (300ms), calls `api.search.songs()`, shows dropdown
- Results replace mock `PlaylistCard[]` with `SongRecommendationCard[]`
- Button label: "Find Similar Songs"

#### New: `fe/components/ui/SongSearchInput.tsx`
- Text input with search icon
- Debounce 300ms
- While searching: skeleton dropdown
- Results dropdown: album art (40×40) + song name + artist
- Selected state: shows selected song chip, clears on ×

#### New: `fe/components/ui/SongRecommendationCard.tsx`
- Glass panel card
- Album art placeholder (no art from BE — show music note icon)
- Song name + artist
- Match score badge (`distance_score` → 0–100 inverted: lower distance = higher match)
- Mini bar chart row: Energy · Dance · Valence (3 bars, colored)
- "Add to playlist" button (calls export endpoint)

#### Changed: History, Favorites, Stats pages
- History: real call to `GET /api/v1/playlists` (BE returns user's `generated_playlists`)

  > Note: BE currently has no `GET /playlists` endpoint — only `POST /playlists/export`. History page will show locally cached results from the current session (sessionStorage) until a proper history endpoint is added in a future iteration. A TODO comment is added to the page.

- Favorites: session-local favorites (starred recommendations), persisted to `localStorage`
- Stats page: session-local stats (count of searches, average match score) — real Supabase stats via a future BE endpoint

#### Unchanged components
GlassPanel, AtmosphericOrb, TextGradient, StatCard, SkeletonCard, Toast, Sidebar, NavItem, BottomTabBar, charts — all unchanged.

---

## 5. Data Flow: Happy Path

```
1. User → GET /login → clicks "Connect with Spotify"
2. FE → redirect to BE GET /api/v1/auth/login
3. BE → redirect to Spotify OAuth
4. Spotify → BE GET /api/v1/auth/callback?code=...
5. BE → store tokens in Supabase, issue JWT → redirect to FE/?token=<JWT>
6. FE → setToken(JWT), strip URL → show Generator Dashboard

7. User types "Neon" in search bar
8. FE (debounced 300ms) → GET /api/v1/search/songs?q=Neon
9. BE → Spotify Search API → return SongResult[]
10. FE → show dropdown, user picks "Neon - John Mayer" (song_id = 4iV5W9...)

11. User clicks "Find Similar Songs"
12. FE → POST /api/v1/recommendations/songs { song_id, max_distance: 0.5 }
13. BE → KNN → Spotify genre filter → return RecommendationResponse
14. FE → render SongRecommendationCard[] with stagger animation

15. User clicks "Add to Spotify Playlist"
16. FE → POST /api/v1/playlists/export { playlist_name, track_ids }
17. BE → Spotify API creates playlist → return spotify_url
18. FE → Toast "Playlist exported!" + open Spotify URL
```

---

## 6. Error Handling

| Scenario | FE behavior |
|---|---|
| 401 on any request | Clear JWT, redirect to /login |
| 422 INSUFFICIENT_RECOMMENDATIONS | Toast "Not enough similar songs found. Try a different track or increase search radius." |
| 422 SONG_NOT_FOUND | Toast "This song isn't in our database yet." |
| 429 rate limit | Toast "Too many requests. Wait a moment and try again." |
| Network error | Toast "Connection error. Check your internet and try again." |
| Search returns 0 results | Dropdown shows "No songs found" empty state |

---

## 7. Environment Variables

### FE (`fe/.env.local`)
```
NEXT_PUBLIC_API_URL=http://localhost:8080
```

### BE (`be/.env/.env.development`)
```
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_REDIRECT_URI=http://localhost:8080/api/v1/auth/callback
SECRET_KEY=...
ALGORITHM=HS256
SUPABASE_URL=...
SUPABASE_KEY=...
PORT=8080
ALLOWED_ORIGINS=http://localhost:3000
RATE_LIMIT=5/minute
```

---

## 8. Out of Scope (future iterations)

- Real history endpoint on BE (`GET /api/v1/playlists/history`)
- Real stats endpoint on BE (`GET /api/v1/stats`)
- `max_distance` slider UI (expose to user)
- Persistent favorites in Supabase
- Refresh token handling (currently BE auto-refreshes; FE just re-redirects on 401)

---

## 9. Implementation Order

1. Create monorepo structure (move FE → `fe/`, copy BE → `be/`)
2. Add search endpoint to BE + wire router
3. Add `fe/lib/auth.ts` + `fe/lib/api.ts`
4. Add login page + auth guard
5. Add `SongSearchInput` component
6. Add `SongRecommendationCard` component
7. Replace mock data in Generator Dashboard with real API calls
8. Replace Unified Generator with real API calls
9. Update History/Favorites/Stats pages (session-local)
10. End-to-end smoke test
