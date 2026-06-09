# SonicPro × Tangent Backend — FE/BE Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire SonicPro Next.js frontend to Tangent FastAPI backend in a monorepo (fe/ + be/), replacing all mock data with real Spotify OAuth auth, song search, and KNN recommendations.

**Architecture:** The existing `Tangent/` git repo becomes the monorepo root. All Next.js files move into `fe/`, BE source copies into `be/`. One new search endpoint (`GET /api/v1/search/songs`) is added to the BE. The FE gains a typed API client + JWT auth layer. The BE auth callback is updated to redirect to the FE with the JWT in the URL.

**Tech Stack:** FE: Next.js 14, Tailwind, Framer Motion, Vitest + RTL. BE: FastAPI, Python 3.12, scikit-learn KNN, Supabase, Spotify Web API, pytest.

---

## File Map

### Monorepo root (`d:\Materi Artificial Intelligence\Machine Learning\Tangent\`)
```
fe/                          ← all Next.js files live here (moved)
be/                          ← FastAPI source (copied from Tangent-backend/backend/)
docs/                        ← unchanged
.gitignore                   ← updated to cover both fe/ and be/
```

### BE changes (`be/`)
```
be/app/api/routers/search.py          CREATE — song search endpoint
be/app/api/routers/__init__.py        MODIFY — include search router
be/app/ml/schemas/search_schema.py   CREATE — SongSearchResult Pydantic model
be/app/api/routers/auth.py           MODIFY — callback redirects to FE
be/.env/.env.development             MODIFY — add FRONTEND_URL
be/tests/test_search.py              CREATE — pytest tests for search endpoint
```

### FE changes (`fe/`)
```
fe/.env.local                              CREATE — NEXT_PUBLIC_API_URL
fe/lib/types.ts                            MODIFY — add SongResult, SongRecommendation, RecommendationResponse, ExportResult
fe/lib/auth.ts                             CREATE — JWT helpers
fe/lib/api.ts                              CREATE — typed API client
fe/app/auth-callback/page.tsx             CREATE — handles ?token= from BE redirect
fe/app/(auth)/layout.tsx                  CREATE — no-sidebar layout for login
fe/app/(auth)/login/page.tsx              CREATE — Spotify connect page
fe/app/(app)/layout.tsx                   MODIFY — add auth guard
fe/app/(app)/page.tsx                     MODIFY — real API, SongSearchInput, SongRecommendationCard
fe/app/(app)/generator/unified/page.tsx  MODIFY — real API
fe/app/(app)/history/page.tsx            MODIFY — sessionStorage
fe/app/(app)/favorites/page.tsx          MODIFY — localStorage
fe/app/(app)/stats/page.tsx              MODIFY — session-local stats
fe/components/ui/SongSearchInput.tsx     CREATE — debounced search with dropdown
fe/components/ui/SongRecommendationCard.tsx CREATE — recommendation result card
fe/tests/lib/auth.test.ts                CREATE
fe/tests/lib/api.test.ts                 CREATE
fe/tests/components/ui/SongSearchInput.test.tsx  CREATE
fe/tests/components/ui/SongRecommendationCard.test.tsx CREATE
```

---

## Task 1: Create Monorepo Structure

**Files:**
- Move: all FE files → `fe/`
- Copy: `Tangent-backend/backend/` → `be/`
- Modify: `.gitignore`

**Work from:** `d:\Materi Artificial Intelligence\Machine Learning\Tangent`

- [ ] **Step 1: Create fe/ and be/ directories, move FE files**

```powershell
$root = "d:\Materi Artificial Intelligence\Machine Learning\Tangent"
Set-Location $root

New-Item -ItemType Directory -Force fe
New-Item -ItemType Directory -Force be

# Move all Next.js source directories
git mv app fe/app
git mv components fe/components
git mv lib fe/lib
git mv public fe/public
git mv tests fe/tests
git mv __mocks__ fe/__mocks__
git mv styles fe/styles

# Move all Next.js config files
git mv package.json fe/package.json
git mv pnpm-lock.yaml fe/pnpm-lock.yaml
git mv tailwind.config.ts fe/tailwind.config.ts
git mv vitest.config.ts fe/vitest.config.ts
git mv vitest.setup.ts fe/vitest.setup.ts
git mv next.config.ts fe/next.config.ts
git mv tsconfig.json fe/tsconfig.json
git mv postcss.config.js fe/postcss.config.js
git mv eslint.config.mjs fe/eslint.config.mjs
git mv AGENTS.md fe/AGENTS.md
git mv CLAUDE.md fe/CLAUDE.md
git mv README.md fe/README.md
```

- [ ] **Step 2: Copy BE source into be/**

```powershell
$beSrc = "d:\Materi Artificial Intelligence\Machine Learning\Tangent-backend\backend"
$beDst = "d:\Materi Artificial Intelligence\Machine Learning\Tangent\be"

Copy-Item -Path "$beSrc\*" -Destination $beDst -Recurse -Force
```

- [ ] **Step 3: Update root .gitignore**

Replace root `.gitignore` with:

```gitignore
# FE
fe/node_modules/
fe/.next/
fe/.env.local
fe/tsconfig.tsbuildinfo
fe/next-env.d.ts

# BE
be/.env/
be/__pycache__/
be/**/__pycache__/
be/**/*.pyc
be/.venv/
be/data/processed/
be/models/*.pkl

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 4: Verify fe/ structure**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent\fe"
Get-ChildItem -Name
```

Expected: `app  components  lib  public  tests  __mocks__  package.json  tailwind.config.ts  ...`

- [ ] **Step 5: Verify FE still builds from fe/**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent\fe"
pnpm build
```

Expected: clean build, 6 routes.

- [ ] **Step 6: Commit**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent"
git add -A
git commit -m "chore: restructure into monorepo — fe/ and be/ subdirectories"
```

---

## Task 2: BE — Fix Auth Callback to Redirect to FE

**Files:**
- Modify: `be/app/api/routers/auth.py`
- Modify: `be/.env/.env.development`

**Work from:** `d:\Materi Artificial Intelligence\Machine Learning\Tangent\be`

- [ ] **Step 1: Write failing test**

Create `be/tests/test_auth_redirect.py`:

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def make_app():
    from app.app_factory import create_app
    return create_app()

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

        app = make_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/v1/auth/callback?code=test_code", follow_redirects=False)

    assert response.status_code == 302
    assert "http://localhost:3000/auth-callback?token=" in response.headers["location"]
```

- [ ] **Step 2: Run test — expect FAIL**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent\be"
uv run pytest tests/test_auth_redirect.py -v
```

Expected: FAIL — callback returns 200 JSON instead of 302 redirect.

- [ ] **Step 3: Add FRONTEND_URL to env**

In `be/.env/.env.development`, add:
```
FRONTEND_URL=http://localhost:3000/auth-callback
```

- [ ] **Step 4: Update auth.py callback to redirect**

In `be/app/api/routers/auth.py`, replace the final `return {...}` block (lines 107–110) with:

```python
        FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000/auth-callback")
        redirect_url = f"{FRONTEND_URL}?token={session_token}"
        return RedirectResponse(url=redirect_url, status_code=302)
```

Full updated file `be/app/api/routers/auth.py`:

```python
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
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Spotify credentials are not configured.")
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

        profile_response = await client.get(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if profile_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to retrieve Spotify profile")

        profile = profile_response.json()
        spotify_id = profile.get("id")
        username = profile.get("display_name") or spotify_id

        db = DBService()
        user_data = db.upsert_user(spotify_id=spotify_id, username=username)
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

        jwt_payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(days=7)
        }
        session_token = jwt.encode(jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000/auth-callback")
        return RedirectResponse(url=f"{FRONTEND_URL}?token={session_token}", status_code=302)
```

- [ ] **Step 5: Run test — expect PASS**

```powershell
uv run pytest tests/test_auth_redirect.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent"
git add be/app/api/routers/auth.py be/tests/test_auth_redirect.py
git commit -m "feat: auth callback redirects to FE with JWT in URL"
```

---

## Task 3: BE — Song Search Endpoint

**Files:**
- Create: `be/app/ml/schemas/search_schema.py`
- Create: `be/app/api/routers/search.py`
- Modify: `be/app/api/routers/__init__.py`
- Create: `be/tests/test_search.py`

**Work from:** `d:\Materi Artificial Intelligence\Machine Learning\Tangent\be`

- [ ] **Step 1: Write failing test**

Create `be/tests/test_search.py`:

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

MOCK_ENV = {
    "SPOTIFY_CLIENT_ID": "test_id",
    "SPOTIFY_CLIENT_SECRET": "test_secret",
    "SPOTIFY_REDIRECT_URI": "http://localhost:8080/api/v1/auth/callback",
    "FRONTEND_URL": "http://localhost:3000/auth-callback",
    "SECRET_KEY": "test_secret_key",
    "SUPABASE_URL": "http://fake",
    "SUPABASE_KEY": "fake",
}

VALID_JWT = None

def make_jwt():
    import jwt
    from datetime import datetime, timezone, timedelta
    payload = {"sub": "user-123", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
    return jwt.encode(payload, "test_secret_key", algorithm="HS256")

@patch.dict(os.environ, MOCK_ENV)
@patch("app.api.routers.generate_songs.DBService")
@patch("httpx.AsyncClient")
def test_search_songs_returns_results(mock_client_class, mock_db_class):
    mock_db = MagicMock()
    mock_db_class.return_value = mock_db
    mock_db.get_user_tokens.return_value = {
        "access_token": "sp_access",
        "refresh_token": "sp_refresh",
        "expires_at": "2099-01-01T00:00:00+00:00",
        "scope": "user-read-private",
    }

    mock_client = AsyncMock()
    mock_client_class.return_value.__aenter__.return_value = mock_client

    spotify_response = MagicMock()
    spotify_response.status_code = 200
    spotify_response.json.return_value = {
        "tracks": {
            "items": [
                {
                    "id": "4iV5W9uYEdYUVa79Axb7Rh",
                    "name": "Neon",
                    "artists": [{"name": "John Mayer"}],
                    "album": {"images": [{"url": "https://img.example.com/neon.jpg"}]},
                }
            ]
        }
    }
    mock_client.get = AsyncMock(return_value=spotify_response)

    from app.app_factory import create_app
    app = create_app()
    client = TestClient(app)

    token = make_jwt()
    response = client.get(
        "/api/v1/search/songs?q=Neon&limit=5",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["song_id"] == "4iV5W9uYEdYUVa79Axb7Rh"
    assert data[0]["name"] == "Neon"
    assert data[0]["artists"] == "John Mayer"
    assert "album_art_url" in data[0]


@patch.dict(os.environ, MOCK_ENV)
@patch("app.api.routers.generate_songs.DBService")
def test_search_songs_requires_auth(mock_db_class):
    from app.app_factory import create_app
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/v1/search/songs?q=Neon")
    assert response.status_code == 401


@patch.dict(os.environ, MOCK_ENV)
@patch("app.api.routers.generate_songs.DBService")
def test_search_songs_rejects_empty_query(mock_db_class):
    mock_db = MagicMock()
    mock_db_class.return_value = mock_db
    mock_db.get_user_tokens.return_value = {
        "access_token": "sp_access",
        "refresh_token": "sp_refresh",
        "expires_at": "2099-01-01T00:00:00+00:00",
        "scope": "user-read-private",
    }
    from app.app_factory import create_app
    app = create_app()
    client = TestClient(app)
    token = make_jwt()
    response = client.get(
        "/api/v1/search/songs?q=&limit=5",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
```

- [ ] **Step 2: Run test — expect FAIL**

```powershell
uv run pytest be/tests/test_search.py -v
```

Expected: FAIL — `/api/v1/search/songs` route does not exist (404).

- [ ] **Step 3: Create SongSearchResult schema**

Create `be/app/ml/schemas/search_schema.py`:

```python
from pydantic import BaseModel

class SongSearchResult(BaseModel):
    song_id: str
    name: str
    artists: str
    album_art_url: str
```

- [ ] **Step 4: Create search router**

Create `be/app/api/routers/search.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.routers.generate_songs import get_user_spotify_token
from app.ml.schemas.search_schema import SongSearchResult
from app.middleware.rate_limit import limiter
from fastapi import Request
import httpx
from typing import List

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)

@router.get("/songs", response_model=List[SongSearchResult])
@limiter.limit("10/minute")
async def search_songs(
    request: Request,
    q: str = Query(..., min_length=1),
    limit: int = Query(default=5, ge=1, le=10),
    spotify_token: str = Depends(get_user_spotify_token),
):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.spotify.com/v1/search",
            params={"q": q, "type": "track", "limit": limit},
            headers={"Authorization": f"Bearer {spotify_token}"},
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Spotify search failed")

    data = response.json()
    items = data.get("tracks", {}).get("items", [])

    results: List[SongSearchResult] = []
    for item in items:
        artists = ", ".join(a["name"] for a in item.get("artists", []))
        images = item.get("album", {}).get("images", [])
        album_art = images[0]["url"] if images else ""
        results.append(SongSearchResult(
            song_id=item["id"],
            name=item["name"],
            artists=artists,
            album_art_url=album_art,
        ))

    return results
```

- [ ] **Step 5: Wire search router into public_router**

Replace `be/app/api/routers/__init__.py` with:

```python
from fastapi import APIRouter
from app.api.routers.generate_songs import router as generate_songs_router
from app.api.routers.auth import router as auth_router
from app.api.routers.users import router as users_router
from app.api.routers.playlists import router as playlists_router
from app.api.routers.search import router as search_router

public_router = APIRouter()

public_router.include_router(auth_router)
public_router.include_router(users_router)
public_router.include_router(generate_songs_router, prefix="/recommendations")
public_router.include_router(playlists_router)
public_router.include_router(search_router)
```

- [ ] **Step 6: Run tests — expect PASS**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent\be"
uv run pytest tests/test_search.py tests/test_auth_redirect.py -v
```

Expected: 4 tests pass.

- [ ] **Step 7: Commit**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent"
git add be/app/ml/schemas/search_schema.py be/app/api/routers/search.py be/app/api/routers/__init__.py be/tests/test_search.py
git commit -m "feat: add GET /api/v1/search/songs endpoint with Spotify search proxy"
```

---

## Task 4: FE — Environment + New Types

**Files:**
- Create: `fe/.env.local`
- Modify: `fe/lib/types.ts`

**Work from:** `d:\Materi Artificial Intelligence\Machine Learning\Tangent\fe`

- [ ] **Step 1: Create fe/.env.local**

```
NEXT_PUBLIC_API_URL=http://localhost:8080
```

- [ ] **Step 2: Write failing test for new types**

Create `fe/tests/lib/types.test.ts`:

```typescript
import { describe, it, expectTypeOf } from 'vitest'
import type { SongResult, SongRecommendation, RecommendationResponse, ExportResult } from '@/lib/types'

describe('SongResult type', () => {
  it('has required fields', () => {
    const s: SongResult = {
      song_id: 'abc',
      name: 'Neon',
      artists: 'John Mayer',
      album_art_url: 'https://img.example.com',
    }
    expectTypeOf(s.song_id).toBeString()
    expectTypeOf(s.album_art_url).toBeString()
  })
})

describe('SongRecommendation type', () => {
  it('has audio feature fields', () => {
    const r: SongRecommendation = {
      song_id: 'abc', name: 'Neon', artists: 'John Mayer',
      distance_score: 0.12, danceability: 0.75, energy: 0.82,
      speechiness: 0.04, acousticness: 0.12, instrumentalness: 0.0,
      liveness: 0.09, valence: 0.65, tempo: 120.5,
    }
    expectTypeOf(r.distance_score).toBeNumber()
  })
})
```

- [ ] **Step 3: Run test — expect FAIL**

```powershell
pnpm test:run tests/lib/types.test.ts
```

Expected: FAIL — `SongResult` not exported from `@/lib/types`.

- [ ] **Step 4: Add new types to fe/lib/types.ts**

Append to the END of `fe/lib/types.ts` (keep all existing types):

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

- [ ] **Step 5: Run test — expect PASS**

```powershell
pnpm test:run tests/lib/types.test.ts
```

- [ ] **Step 6: Commit**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent"
git add fe/lib/types.ts fe/tests/lib/types.test.ts
git commit -m "feat: add SongResult, SongRecommendation, RecommendationResponse, ExportResult types"
```

---

## Task 5: FE — Auth Helpers (`lib/auth.ts`)

**Files:**
- Create: `fe/lib/auth.ts`
- Create: `fe/tests/lib/auth.test.ts`

**Work from:** `d:\Materi Artificial Intelligence\Machine Learning\Tangent\fe`

- [ ] **Step 1: Write failing test**

Create `fe/tests/lib/auth.test.ts`:

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest'

const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (k: string) => store[k] ?? null,
    setItem: (k: string, v: string) => { store[k] = v },
    removeItem: (k: string) => { delete store[k] },
    clear: () => { store = {} },
  }
})()
Object.defineProperty(globalThis, 'localStorage', { value: localStorageMock })

beforeEach(() => localStorageMock.clear())

describe('auth helpers', () => {
  it('getToken returns null when nothing stored', async () => {
    const { getToken } = await import('@/lib/auth')
    expect(getToken()).toBeNull()
  })

  it('setToken and getToken round-trip', async () => {
    const { setToken, getToken } = await import('@/lib/auth')
    setToken('my.jwt.token')
    expect(getToken()).toBe('my.jwt.token')
  })

  it('clearToken removes the token', async () => {
    const { setToken, clearToken, getToken } = await import('@/lib/auth')
    setToken('token')
    clearToken()
    expect(getToken()).toBeNull()
  })

  it('isAuthenticated is true when token exists', async () => {
    const { setToken, isAuthenticated } = await import('@/lib/auth')
    setToken('token')
    expect(isAuthenticated()).toBe(true)
  })

  it('isAuthenticated is false when no token', async () => {
    const { isAuthenticated } = await import('@/lib/auth')
    expect(isAuthenticated()).toBe(false)
  })
})
```

- [ ] **Step 2: Run test — expect FAIL**

```powershell
pnpm test:run tests/lib/auth.test.ts
```

Expected: FAIL — module `@/lib/auth` not found.

- [ ] **Step 3: Implement fe/lib/auth.ts**

Create `fe/lib/auth.ts`:

```typescript
const TOKEN_KEY = 'sonicpro_jwt'

export function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(jwt: string): void {
  localStorage.setItem(TOKEN_KEY, jwt)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export function isAuthenticated(): boolean {
  return getToken() !== null
}

export function getLoginUrl(): string {
  const base = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8080'
  return `${base}/api/v1/auth/login`
}
```

- [ ] **Step 4: Run test — expect PASS**

```powershell
pnpm test:run tests/lib/auth.test.ts
```

Expected: 5 passing.

- [ ] **Step 5: Commit**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent"
git add fe/lib/auth.ts fe/tests/lib/auth.test.ts
git commit -m "feat: add JWT auth helpers (getToken, setToken, clearToken, isAuthenticated)"
```

---

## Task 6: FE — API Client (`lib/api.ts`)

**Files:**
- Create: `fe/lib/api.ts`
- Create: `fe/tests/lib/api.test.ts`

**Work from:** `d:\Materi Artificial Intelligence\Machine Learning\Tangent\fe`

- [ ] **Step 1: Write failing test**

Create `fe/tests/lib/api.test.ts`:

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

vi.mock('@/lib/auth', () => ({
  getToken: vi.fn(() => 'test.jwt.token'),
  clearToken: vi.fn(),
}))

beforeEach(() => { mockFetch.mockReset() })

describe('api.search.songs', () => {
  it('calls correct URL with auth header', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [{ song_id: 'abc', name: 'Neon', artists: 'John Mayer', album_art_url: 'https://img' }],
    })

    const { default: api } = await import('@/lib/api')
    const results = await api.search.songs('Neon')

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/search/songs?q=Neon'),
      expect.objectContaining({ headers: expect.objectContaining({ Authorization: 'Bearer test.jwt.token' }) })
    )
    expect(results[0].song_id).toBe('abc')
  })
})

describe('api.recommendations.getSongs', () => {
  it('calls POST /api/v1/recommendations/songs', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ seed_song_id: 'abc', total_recommendations: 1, recommendations: [] }),
    })

    const { default: api } = await import('@/lib/api')
    const result = await api.recommendations.getSongs('abc')

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/recommendations/songs'),
      expect.objectContaining({ method: 'POST' })
    )
    expect(result.seed_song_id).toBe('abc')
  })
})

describe('api.playlists.export', () => {
  it('calls POST /api/v1/playlists/export', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'ok', playlist_id: 'p1', spotify_url: 'https://spotify.com/p1' }),
    })

    const { default: api } = await import('@/lib/api')
    const result = await api.playlists.export('My Mix', ['track1', 'track2'])

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/playlists/export'),
      expect.objectContaining({ method: 'POST' })
    )
    expect(result.playlist_id).toBe('p1')
  })
})
```

- [ ] **Step 2: Run test — expect FAIL**

```powershell
pnpm test:run tests/lib/api.test.ts
```

Expected: FAIL — `@/lib/api` not found.

- [ ] **Step 3: Implement fe/lib/api.ts**

Create `fe/lib/api.ts`:

```typescript
import { getToken, clearToken } from './auth'
import type { SongResult, SongRecommendation, RecommendationResponse, ExportResult } from './types'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8080'

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(init.headers as Record<string, string> ?? {}),
  }

  const res = await fetch(`${BASE_URL}${path}`, { ...init, headers })

  if (res.status === 401) {
    clearToken()
    if (typeof window !== 'undefined') window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    const message = (body as any)?.message ?? (body as any)?.detail ?? `HTTP ${res.status}`
    throw new Error(message)
  }

  return res.json() as Promise<T>
}

const api = {
  search: {
    songs(q: string, limit = 5): Promise<SongResult[]> {
      return request<SongResult[]>(`/api/v1/search/songs?q=${encodeURIComponent(q)}&limit=${limit}`)
    },
  },
  recommendations: {
    getSongs(songId: string, maxDistance = 0.5): Promise<RecommendationResponse> {
      return request<RecommendationResponse>('/api/v1/recommendations/songs', {
        method: 'POST',
        body: JSON.stringify({ song_id: songId, max_distance: maxDistance }),
      })
    },
  },
  playlists: {
    export(playlistName: string, trackIds: string[]): Promise<ExportResult> {
      return request<ExportResult>('/api/v1/playlists/export', {
        method: 'POST',
        body: JSON.stringify({ playlist_name: playlistName, track_ids: trackIds }),
      })
    },
  },
}

export default api
```

- [ ] **Step 4: Run test — expect PASS**

```powershell
pnpm test:run tests/lib/api.test.ts
```

Expected: 3 passing.

- [ ] **Step 5: Commit**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent"
git add fe/lib/api.ts fe/tests/lib/api.test.ts
git commit -m "feat: add typed API client for search, recommendations, and playlist export"
```

---

## Task 7: FE — Auth Callback Page + Login Page + Auth Guard

**Files:**
- Create: `fe/app/auth-callback/page.tsx`
- Create: `fe/app/(auth)/layout.tsx`
- Create: `fe/app/(auth)/login/page.tsx`
- Modify: `fe/app/(app)/layout.tsx`

**Work from:** `d:\Materi Artificial Intelligence\Machine Learning\Tangent\fe`

- [ ] **Step 1: Write failing tests**

Create `fe/tests/app/auth.test.tsx`:

```typescript
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'

vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace: vi.fn() }),
  useSearchParams: () => ({ get: (k: string) => k === 'token' ? 'test.jwt' : null }),
  usePathname: () => '/login',
}))
vi.mock('@/lib/auth', () => ({
  setToken: vi.fn(),
  isAuthenticated: vi.fn(() => false),
  getLoginUrl: vi.fn(() => 'http://localhost:8080/api/v1/auth/login'),
  clearToken: vi.fn(),
  getToken: vi.fn(() => null),
}))

describe('Login page', async () => {
  const { default: LoginPage } = await import('@/app/(auth)/login/page')

  it('renders connect with Spotify button', () => {
    render(<LoginPage />)
    expect(screen.getByRole('link', { name: /connect with spotify/i })).toBeInTheDocument()
  })
})

describe('AuthCallback page', async () => {
  const { default: AuthCallbackPage } = await import('@/app/auth-callback/page')

  it('renders without crashing', () => {
    const { container } = render(<AuthCallbackPage />)
    expect(container).toBeTruthy()
  })
})
```

- [ ] **Step 2: Run test — expect FAIL**

```powershell
pnpm test:run tests/app/auth.test.tsx
```

- [ ] **Step 3: Create auth-callback page**

Create `fe/app/auth-callback/page.tsx`:

```typescript
'use client'

import { useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { setToken } from '@/lib/auth'

export default function AuthCallbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    const token = searchParams.get('token')
    if (token) {
      setToken(token)
      router.replace('/')
    } else {
      router.replace('/login')
    }
  }, [router, searchParams])

  return (
    <div className="min-h-dvh bg-background flex items-center justify-center">
      <p className="text-on-surface-variant text-body-lg">Connecting to Spotify…</p>
    </div>
  )
}
```

- [ ] **Step 4: Create auth layout (no sidebar)**

Create `fe/app/(auth)/layout.tsx`:

```typescript
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-dvh bg-background">
      {children}
    </div>
  )
}
```

- [ ] **Step 5: Create login page**

Create `fe/app/(auth)/login/page.tsx`:

```typescript
import { getLoginUrl } from '@/lib/auth'
import { Music2 } from 'lucide-react'
import { TextGradient } from '@/components/ui/TextGradient'
import { AtmosphericOrb } from '@/components/ui/AtmosphericOrb'
import { GlassPanel } from '@/components/ui/GlassPanel'

export default function LoginPage() {
  const loginUrl = getLoginUrl()

  return (
    <div className="relative min-h-dvh bg-background flex items-center justify-center px-margin-mobile overflow-hidden">
      <AtmosphericOrb color="secondary" size="lg" position="top-left" />
      <AtmosphericOrb color="primary" size="md" position="bottom-right" />

      <GlassPanel className="relative z-10 w-full max-w-sm p-xl flex flex-col items-center gap-lg text-center">
        <div className="w-16 h-16 rounded-2xl bg-primary/10 border border-primary/30 flex items-center justify-center">
          <Music2 className="w-8 h-8 text-primary" aria-hidden="true" />
        </div>

        <div>
          <TextGradient as="h1" className="text-headline-xl font-bold block mb-sm">
            SonicPro
          </TextGradient>
          <p className="text-body-md text-on-surface-variant">
            AI-powered music discovery. Connect your Spotify account to get started.
          </p>
        </div>

        <a
          href={loginUrl}
          role="link"
          className="w-full flex items-center justify-center gap-sm bg-primary text-on-primary font-label-lg rounded-xl px-8 py-4 hover:scale-[1.02] hover:shadow-glow-primary-lg transition-all duration-150 focus-ring"
        >
          Connect with Spotify
        </a>

        <p className="text-label-sm text-on-surface-variant">
          We only request access to read your profile and manage playlists.
        </p>
      </GlassPanel>
    </div>
  )
}
```

- [ ] **Step 6: Add auth guard to app shell**

Replace `fe/app/(app)/layout.tsx` with:

```typescript
'use client'

import { useEffect } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { Sidebar } from '@/components/layout/Sidebar'
import { BottomTabBar } from '@/components/layout/BottomTabBar'
import { isAuthenticated } from '@/lib/auth'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace('/login')
    }
  }, [router])

  if (!isAuthenticated()) return null

  return (
    <>
      <Sidebar />
      <main className="md:ml-[280px] min-h-dvh relative overflow-hidden pb-20 md:pb-0">
        {children}
      </main>
      <BottomTabBar currentPath={pathname} />
    </>
  )
}
```

- [ ] **Step 7: Run tests — expect PASS**

```powershell
pnpm test:run tests/app/auth.test.tsx
```

- [ ] **Step 8: Commit**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent"
git add fe/app/auth-callback fe/app/\(auth\) fe/app/\(app\)/layout.tsx fe/tests/app/auth.test.tsx
git commit -m "feat: add login page, auth-callback handler, and auth guard on app shell"
```

---

## Task 8: FE — SongSearchInput Component

**Files:**
- Create: `fe/components/ui/SongSearchInput.tsx`
- Create: `fe/tests/components/ui/SongSearchInput.test.tsx`

**Work from:** `d:\Materi Artificial Intelligence\Machine Learning\Tangent\fe`

- [ ] **Step 1: Write failing test**

Create `fe/tests/components/ui/SongSearchInput.test.tsx`:

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { SongSearchInput } from '@/components/ui/SongSearchInput'
import type { SongResult } from '@/lib/types'

vi.mock('@/lib/api', () => ({
  default: {
    search: {
      songs: vi.fn(async () => [
        { song_id: 'abc', name: 'Neon', artists: 'John Mayer', album_art_url: '' },
      ] as SongResult[]),
    },
  },
}))

describe('SongSearchInput', () => {
  it('renders search input', () => {
    render(<SongSearchInput onSelect={() => {}} />)
    expect(screen.getByPlaceholderText(/search a song/i)).toBeInTheDocument()
  })

  it('calls onSelect with result when clicked', async () => {
    vi.useFakeTimers()
    const onSelect = vi.fn()
    render(<SongSearchInput onSelect={onSelect} />)

    fireEvent.change(screen.getByPlaceholderText(/search a song/i), { target: { value: 'Neon' } })
    vi.advanceTimersByTime(350)

    await waitFor(() => {
      expect(screen.getByText('Neon')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Neon'))
    expect(onSelect).toHaveBeenCalledWith(expect.objectContaining({ song_id: 'abc' }))
    vi.useRealTimers()
  })

  it('shows selected song chip when song is selected', async () => {
    vi.useFakeTimers()
    render(<SongSearchInput onSelect={() => {}} />)
    fireEvent.change(screen.getByPlaceholderText(/search a song/i), { target: { value: 'Neon' } })
    vi.advanceTimersByTime(350)

    await waitFor(() => screen.getByText('Neon'))
    fireEvent.click(screen.getByText('Neon'))

    expect(screen.getByText(/John Mayer/i)).toBeInTheDocument()
    vi.useRealTimers()
  })
})
```

- [ ] **Step 2: Run test — expect FAIL**

```powershell
pnpm test:run tests/components/ui/SongSearchInput.test.tsx
```

- [ ] **Step 3: Implement SongSearchInput**

Create `fe/components/ui/SongSearchInput.tsx`:

```typescript
'use client'

import { useState, useEffect, useRef } from 'react'
import { Search, X, Music } from 'lucide-react'
import { clsx } from 'clsx'
import api from '@/lib/api'
import type { SongResult } from '@/lib/types'

interface SongSearchInputProps {
  onSelect: (song: SongResult) => void
}

export function SongSearchInput({ onSelect }: SongSearchInputProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SongResult[]>([])
  const [isLoading, setLoading] = useState(false)
  const [selected, setSelected] = useState<SongResult | null>(null)
  const [open, setOpen] = useState(false)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (query.trim().length < 2) {
      setResults([])
      setOpen(false)
      return
    }
    if (timerRef.current) clearTimeout(timerRef.current)
    timerRef.current = setTimeout(async () => {
      setLoading(true)
      try {
        const data = await api.search.songs(query)
        setResults(data)
        setOpen(true)
      } catch {
        setResults([])
      } finally {
        setLoading(false)
      }
    }, 300)
    return () => { if (timerRef.current) clearTimeout(timerRef.current) }
  }, [query])

  function handleSelect(song: SongResult) {
    setSelected(song)
    setQuery('')
    setResults([])
    setOpen(false)
    onSelect(song)
  }

  function handleClear() {
    setSelected(null)
    setQuery('')
    setResults([])
    setOpen(false)
  }

  if (selected) {
    return (
      <div className="w-full flex items-center gap-sm bg-surface-container-high border border-primary/30 rounded-xl px-md py-4">
        <Music className="w-5 h-5 text-primary flex-shrink-0" aria-hidden="true" />
        <div className="flex-1 min-w-0">
          <p className="text-body-md text-on-surface font-medium truncate">{selected.name}</p>
          <p className="text-label-sm text-on-surface-variant truncate">{selected.artists}</p>
        </div>
        <button
          onClick={handleClear}
          aria-label="Clear selected song"
          className="text-on-surface-variant hover:text-on-surface transition-colors focus-ring rounded p-1"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    )
  }

  return (
    <div className="relative w-full">
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary pointer-events-none" aria-hidden="true" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search a song…"
          aria-label="Search for a song"
          aria-autocomplete="list"
          aria-expanded={open}
          className="w-full bg-surface-container-high text-on-surface border border-white/10 rounded-xl py-5 pl-12 pr-4 text-body-lg placeholder:text-on-surface-variant focus:outline-none focus:border-secondary focus:ring-1 focus:ring-secondary focus:shadow-glow-input transition-all"
        />
      </div>

      {open && results.length > 0 && (
        <ul
          role="listbox"
          aria-label="Song search results"
          className="absolute top-full left-0 right-0 mt-2 z-50 glass-panel rounded-lg overflow-hidden"
        >
          {results.map((song) => (
            <li key={song.song_id}>
              <button
                onClick={() => handleSelect(song)}
                className="w-full flex items-center gap-sm px-md py-sm hover:bg-white/5 transition-colors text-left focus-ring"
              >
                {song.album_art_url ? (
                  <img src={song.album_art_url} alt={song.name} className="w-10 h-10 rounded flex-shrink-0 object-cover" />
                ) : (
                  <div className="w-10 h-10 rounded flex-shrink-0 bg-surface-container-high flex items-center justify-center">
                    <Music className="w-5 h-5 text-on-surface-variant" />
                  </div>
                )}
                <div className="min-w-0">
                  <p className="text-body-md text-on-surface truncate">{song.name}</p>
                  <p className="text-label-sm text-on-surface-variant truncate">{song.artists}</p>
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}

      {isLoading && (
        <div className="absolute top-full left-0 right-0 mt-2 z-50 glass-panel rounded-lg px-md py-sm">
          <p className="text-label-md text-on-surface-variant">Searching…</p>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Run test — expect PASS**

```powershell
pnpm test:run tests/components/ui/SongSearchInput.test.tsx
```

- [ ] **Step 5: Commit**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent"
git add fe/components/ui/SongSearchInput.tsx fe/tests/components/ui/SongSearchInput.test.tsx
git commit -m "feat: add SongSearchInput with debounced Spotify search and result dropdown"
```

---

## Task 9: FE — SongRecommendationCard Component

**Files:**
- Create: `fe/components/ui/SongRecommendationCard.tsx`
- Create: `fe/tests/components/ui/SongRecommendationCard.test.tsx`

**Work from:** `d:\Materi Artificial Intelligence\Machine Learning\Tangent\fe`

- [ ] **Step 1: Write failing test**

Create `fe/tests/components/ui/SongRecommendationCard.test.tsx`:

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { SongRecommendationCard } from '@/components/ui/SongRecommendationCard'
import type { SongRecommendation } from '@/lib/types'

const mockRec: SongRecommendation = {
  song_id: 'abc123',
  name: 'Neon',
  artists: 'John Mayer',
  distance_score: 0.12,
  danceability: 0.75,
  energy: 0.82,
  speechiness: 0.04,
  acousticness: 0.12,
  instrumentalness: 0.0,
  liveness: 0.09,
  valence: 0.65,
  tempo: 120.5,
}

describe('SongRecommendationCard', () => {
  it('renders song name and artist', () => {
    render(<SongRecommendationCard rec={mockRec} onAddToPlaylist={() => {}} />)
    expect(screen.getByText('Neon')).toBeInTheDocument()
    expect(screen.getByText('John Mayer')).toBeInTheDocument()
  })

  it('shows match score derived from distance_score', () => {
    render(<SongRecommendationCard rec={mockRec} onAddToPlaylist={() => {}} />)
    // match = Math.round((1 - 0.12) * 100) = 88%
    expect(screen.getByText(/88%/)).toBeInTheDocument()
  })

  it('calls onAddToPlaylist with song_id', () => {
    const onAdd = vi.fn()
    render(<SongRecommendationCard rec={mockRec} onAddToPlaylist={onAdd} />)
    fireEvent.click(screen.getByRole('button', { name: /add to playlist/i }))
    expect(onAdd).toHaveBeenCalledWith('abc123')
  })
})
```

- [ ] **Step 2: Run test — expect FAIL**

```powershell
pnpm test:run tests/components/ui/SongRecommendationCard.test.tsx
```

- [ ] **Step 3: Implement SongRecommendationCard**

Create `fe/components/ui/SongRecommendationCard.tsx`:

```typescript
import { Music, Plus } from 'lucide-react'
import { clsx } from 'clsx'
import { GlassPanel } from './GlassPanel'
import type { SongRecommendation } from '@/lib/types'

interface SongRecommendationCardProps {
  rec: SongRecommendation
  onAddToPlaylist: (songId: string) => void
}

interface FeatureBarProps {
  label: string
  value: number
  color: string
}

function FeatureBar({ label, value, color }: FeatureBarProps) {
  return (
    <div className="flex items-center gap-sm min-w-0">
      <span className="text-label-sm text-on-surface-variant w-12 flex-shrink-0">{label}</span>
      <div className="flex-1 h-1 bg-surface-container-high rounded-full overflow-hidden">
        <div
          className={clsx('h-full rounded-full transition-all', color)}
          style={{ width: `${Math.round(value * 100)}%` }}
          aria-label={`${label}: ${Math.round(value * 100)}%`}
        />
      </div>
    </div>
  )
}

export function SongRecommendationCard({ rec, onAddToPlaylist }: SongRecommendationCardProps) {
  const matchScore = Math.round((1 - rec.distance_score) * 100)

  return (
    <GlassPanel
      className="flex items-start gap-md p-md transition-all duration-150 hover:border-primary/30 hover:shadow-glow-primary"
      as="article"
    >
      <div className="w-12 h-12 rounded-lg flex-shrink-0 bg-surface-container-high flex items-center justify-center">
        <Music className="w-6 h-6 text-on-surface-variant" aria-hidden="true" />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-sm mb-sm">
          <div className="min-w-0">
            <p className="text-title-md text-on-surface font-medium truncate">{rec.name}</p>
            <p className="text-body-md text-on-surface-variant truncate">{rec.artists}</p>
          </div>
          <span className="flex-shrink-0 text-label-md text-primary font-bold bg-primary/10 px-2 py-0.5 rounded-full">
            {matchScore}%
          </span>
        </div>

        <div className="flex flex-col gap-1 mb-md">
          <FeatureBar label="Energy" value={rec.energy} color="bg-primary" />
          <FeatureBar label="Dance" value={rec.danceability} color="bg-secondary" />
          <FeatureBar label="Vibe" value={rec.valence} color="bg-tertiary" />
        </div>

        <button
          onClick={() => onAddToPlaylist(rec.song_id)}
          aria-label={`Add ${rec.name} to playlist`}
          className="flex items-center gap-1 text-label-md text-on-surface-variant hover:text-primary transition-colors focus-ring rounded px-1"
        >
          <Plus className="w-4 h-4" aria-hidden="true" />
          Add to playlist
        </button>
      </div>
    </GlassPanel>
  )
}
```

- [ ] **Step 4: Run test — expect PASS**

```powershell
pnpm test:run tests/components/ui/SongRecommendationCard.test.tsx
```

- [ ] **Step 5: Commit**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent"
git add fe/components/ui/SongRecommendationCard.tsx fe/tests/components/ui/SongRecommendationCard.test.tsx
git commit -m "feat: add SongRecommendationCard with match score and audio feature bars"
```

---

## Task 10: FE — Update Generator Dashboard with Real API

**Files:**
- Modify: `fe/app/(app)/page.tsx`
- Modify: `fe/tests/app/generator.test.tsx`

**Work from:** `d:\Materi Artificial Intelligence\Machine Learning\Tangent\fe`

- [ ] **Step 1: Update generator test**

Replace `fe/tests/app/generator.test.tsx`:

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import GeneratorPage from '@/app/(app)/page'

vi.mock('next/navigation', () => ({ usePathname: () => '/', useRouter: () => ({ replace: vi.fn() }) }))
vi.mock('next/image', () => ({ default: (props: any) => <img {...props} /> }))
vi.mock('framer-motion', () => ({
  motion: { div: ({ children, ...p }: any) => <div {...p}>{children}</div> },
  useReducedMotion: () => false,
}))
vi.mock('@/lib/auth', () => ({
  isAuthenticated: vi.fn(() => true),
  getToken: vi.fn(() => 'token'),
  clearToken: vi.fn(),
}))
vi.mock('@/lib/api', () => ({
  default: {
    recommendations: {
      getSongs: vi.fn(async () => ({
        seed_song_id: 'abc',
        total_recommendations: 1,
        recommendations: [{
          song_id: 'r1', name: 'Dark Matter', artists: 'Void Protocol',
          distance_score: 0.15, danceability: 0.7, energy: 0.8,
          speechiness: 0.03, acousticness: 0.1, instrumentalness: 0,
          liveness: 0.1, valence: 0.6, tempo: 130,
        }],
      })),
    },
  },
}))

describe('Generator Dashboard', () => {
  it('renders headline', () => {
    render(<GeneratorPage />)
    expect(screen.getByRole('heading', { name: /find similar songs/i })).toBeInTheDocument()
  })

  it('renders song search input', () => {
    render(<GeneratorPage />)
    expect(screen.getByPlaceholderText(/search a song/i)).toBeInTheDocument()
  })

  it('shows generate button disabled before song selected', () => {
    render(<GeneratorPage />)
    expect(screen.getByRole('button', { name: /find similar songs/i })).toBeDisabled()
  })
})
```

- [ ] **Step 2: Run test — expect FAIL**

```powershell
pnpm test:run tests/app/generator.test.tsx
```

Expected: FAIL — heading "Find Similar Songs" not found (old page has "Extend Your Sound").

- [ ] **Step 3: Replace fe/app/(app)/page.tsx**

```typescript
'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { SongSearchInput } from '@/components/ui/SongSearchInput'
import { SongRecommendationCard } from '@/components/ui/SongRecommendationCard'
import { GenerateButton } from '@/components/ui/GenerateButton'
import { SkeletonCard } from '@/components/ui/SkeletonCard'
import { AtmosphericOrb } from '@/components/ui/AtmosphericOrb'
import { TextGradient } from '@/components/ui/TextGradient'
import { Toast } from '@/components/ui/Toast'
import { useMotion } from '@/components/providers/MotionProvider'
import api from '@/lib/api'
import type { SongResult, SongRecommendation } from '@/lib/types'

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.05 } },
}
const itemVariants = {
  hidden:  { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' as const } },
}

const ERROR_MESSAGES: Record<string, string> = {
  INSUFFICIENT_RECOMMENDATIONS: 'Not enough similar songs found. Try a different track.',
  SONG_NOT_FOUND: "This song isn't in our database yet.",
}

export default function GeneratorPage() {
  const { shouldAnimate } = useMotion()
  const [selectedSong, setSelectedSong] = useState<SongResult | null>(null)
  const [isLoading, setLoading] = useState(false)
  const [recommendations, setRecommendations] = useState<SongRecommendation[]>([])
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)
  const [exportingIds, setExportingIds] = useState<Set<string>>(new Set())

  async function handleGenerate() {
    if (!selectedSong) return
    setLoading(true)
    setRecommendations([])
    try {
      const result = await api.recommendations.getSongs(selectedSong.song_id)
      setRecommendations(result.recommendations)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Something went wrong.'
      setToast({ message: ERROR_MESSAGES[message] ?? message, type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  async function handleAddToPlaylist(songId: string) {
    if (!selectedSong) return
    setExportingIds((prev) => new Set(prev).add(songId))
    try {
      const result = await api.playlists.export(`SonicPro Mix — ${selectedSong.name}`, [songId])
      setToast({ message: 'Added to Spotify!', type: 'success' })
      window.open(result.spotify_url, '_blank')
    } catch {
      setToast({ message: 'Failed to export. Try again.', type: 'error' })
    } finally {
      setExportingIds((prev) => { const s = new Set(prev); s.delete(songId); return s })
    }
  }

  return (
    <motion.div
      initial={shouldAnimate ? { opacity: 0, y: 8 } : false}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className="relative min-h-dvh px-margin-mobile md:px-margin-desktop pb-xl"
    >
      <AtmosphericOrb color="secondary" size="lg" position="top-left" />
      <AtmosphericOrb color="primary"   size="md" position="bottom-right" />

      <section className="relative z-10 max-w-3xl mx-auto pt-xl text-center flex flex-col items-center gap-xl">
        <div>
          <h1 className="text-headline-xl font-bold text-on-surface mb-sm">
            <TextGradient>Find Similar Songs</TextGradient>
          </h1>
          <p className="text-body-lg text-on-surface-variant max-w-xl">
            Search any song and our AI engine will find acoustically similar tracks you&apos;ll love.
          </p>
        </div>

        <div className="w-full flex flex-col items-center gap-md">
          <SongSearchInput onSelect={setSelectedSong} />
          <GenerateButton
            isLoading={isLoading}
            onClick={handleGenerate}
            disabled={!selectedSong}
          />
        </div>
      </section>

      {(isLoading || recommendations.length > 0) && (
        <section className="relative z-10 max-w-3xl mx-auto mt-xxl">
          <h2 className="text-label-lg text-on-surface-variant mb-md uppercase tracking-widest">
            Similar Songs
          </h2>
          {isLoading ? (
            <div className="flex flex-col gap-md">
              <SkeletonCard /><SkeletonCard /><SkeletonCard />
            </div>
          ) : (
            <motion.div
              variants={shouldAnimate ? containerVariants : undefined}
              initial="hidden"
              animate="visible"
              className="flex flex-col gap-md"
            >
              {recommendations.map((rec) => (
                <motion.div key={rec.song_id} variants={shouldAnimate ? itemVariants : undefined}>
                  <SongRecommendationCard
                    rec={rec}
                    onAddToPlaylist={handleAddToPlaylist}
                  />
                </motion.div>
              ))}
            </motion.div>
          )}
        </section>
      )}

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onDismiss={() => setToast(null)}
        />
      )}
    </motion.div>
  )
}
```

- [ ] **Step 4: Update GenerateButton to accept disabled prop**

Confirm `fe/components/ui/GenerateButton.tsx` already accepts `disabled?: boolean` (it does from Task 8 of the original plan). No change needed.

- [ ] **Step 5: Run test — expect PASS**

```powershell
pnpm test:run tests/app/generator.test.tsx
```

- [ ] **Step 6: Commit**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent"
git add fe/app/\(app\)/page.tsx fe/tests/app/generator.test.tsx
git commit -m "feat: replace mock data on Generator Dashboard with real API calls"
```

---

## Task 11: FE — Update Unified Generator + History/Favorites/Stats

**Files:**
- Modify: `fe/app/(app)/generator/unified/page.tsx`
- Modify: `fe/app/(app)/history/page.tsx`
- Modify: `fe/app/(app)/favorites/page.tsx`
- Modify: `fe/app/(app)/stats/page.tsx`

**Work from:** `d:\Materi Artificial Intelligence\Machine Learning\Tangent\fe`

- [ ] **Step 1: Update Unified Generator Dashboard**

Replace `fe/app/(app)/generator/unified/page.tsx`:

```typescript
'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { SongSearchInput } from '@/components/ui/SongSearchInput'
import { SongRecommendationCard } from '@/components/ui/SongRecommendationCard'
import { GenerateButton } from '@/components/ui/GenerateButton'
import { SkeletonCard } from '@/components/ui/SkeletonCard'
import { GlassPanel } from '@/components/ui/GlassPanel'
import { AtmosphericOrb } from '@/components/ui/AtmosphericOrb'
import { TextGradient } from '@/components/ui/TextGradient'
import { Toast } from '@/components/ui/Toast'
import { useMotion } from '@/components/providers/MotionProvider'
import api from '@/lib/api'
import type { SongResult, SongRecommendation } from '@/lib/types'

const ERROR_MESSAGES: Record<string, string> = {
  INSUFFICIENT_RECOMMENDATIONS: 'Not enough similar songs found. Try a different track.',
  SONG_NOT_FOUND: "This song isn't in our database yet.",
}

export default function UnifiedPage() {
  const { shouldAnimate } = useMotion()
  const [selectedSong, setSelectedSong] = useState<SongResult | null>(null)
  const [isLoading, setLoading] = useState(false)
  const [recommendations, setRecommendations] = useState<SongRecommendation[]>([])
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  async function handleGenerate() {
    if (!selectedSong) return
    setLoading(true)
    setRecommendations([])
    try {
      const result = await api.recommendations.getSongs(selectedSong.song_id)
      setRecommendations(result.recommendations)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Something went wrong.'
      setToast({ message: ERROR_MESSAGES[message] ?? message, type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  async function handleAddToPlaylist(songId: string) {
    if (!selectedSong) return
    try {
      const result = await api.playlists.export(`SonicPro Mix — ${selectedSong.name}`, [songId])
      setToast({ message: 'Added to Spotify!', type: 'success' })
      window.open(result.spotify_url, '_blank')
    } catch {
      setToast({ message: 'Failed to export. Try again.', type: 'error' })
    }
  }

  return (
    <motion.div
      initial={shouldAnimate ? { opacity: 0, y: 8 } : false}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className="relative px-margin-mobile md:px-margin-desktop py-xl min-h-dvh"
    >
      <AtmosphericOrb color="secondary" size="lg" position="top-left" />

      <div className="relative z-10 max-w-6xl mx-auto">
        <h1 className="text-headline-xl font-bold text-on-surface mb-lg">
          <TextGradient>Unified Generator</TextGradient>
        </h1>

        <div className="grid md:grid-cols-2 gap-lg">
          <GlassPanel className="p-lg flex flex-col gap-lg">
            <div>
              <h2 className="text-title-lg font-semibold text-on-surface mb-sm">Find Similar Songs</h2>
              <p className="text-body-md text-on-surface-variant">
                Search a song and get AI-curated similar tracks based on acoustic features.
              </p>
            </div>
            <SongSearchInput onSelect={setSelectedSong} />
            <GenerateButton isLoading={isLoading} onClick={handleGenerate} disabled={!selectedSong} />
          </GlassPanel>

          <GlassPanel className="p-lg flex flex-col gap-md overflow-y-auto max-h-[600px]">
            <h2 className="text-title-md font-semibold text-on-surface">Results</h2>
            {isLoading && <><SkeletonCard /><SkeletonCard /></>}
            {!isLoading && recommendations.length === 0 && (
              <p className="text-body-md text-on-surface-variant text-center py-xl">
                Your similar songs will appear here.
              </p>
            )}
            {recommendations.map((rec) => (
              <SongRecommendationCard key={rec.song_id} rec={rec} onAddToPlaylist={handleAddToPlaylist} />
            ))}
          </GlassPanel>
        </div>
      </div>

      {toast && <Toast message={toast.message} type={toast.type} onDismiss={() => setToast(null)} />}
    </motion.div>
  )
}
```

- [ ] **Step 2: Update History page (session-local)**

Replace `fe/app/(app)/history/page.tsx` — add session storage for search history. Keep the same UI but replace mock data with sessionStorage:

```typescript
'use client'

import { useState, useMemo, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Search, Music } from 'lucide-react'
import { AtmosphericOrb } from '@/components/ui/AtmosphericOrb'
import { useMotion } from '@/components/providers/MotionProvider'

interface HistoryEntry {
  id: string
  songName: string
  artists: string
  totalResults: number
  searchedAt: string
}

const HISTORY_KEY = 'sonicpro_history'

export function getHistory(): HistoryEntry[] {
  if (typeof window === 'undefined') return []
  try { return JSON.parse(sessionStorage.getItem(HISTORY_KEY) ?? '[]') } catch { return [] }
}

export function addToHistory(entry: Omit<HistoryEntry, 'id' | 'searchedAt'>) {
  const entries = getHistory()
  const newEntry: HistoryEntry = {
    ...entry,
    id: `${Date.now()}`,
    searchedAt: new Date().toISOString(),
  }
  sessionStorage.setItem(HISTORY_KEY, JSON.stringify([newEntry, ...entries].slice(0, 50)))
}

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.04 } },
}
const itemVariants = {
  hidden:  { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' as const } },
}

export default function HistoryPage() {
  const { shouldAnimate } = useMotion()
  const [query, setQuery] = useState('')
  const [history, setHistory] = useState<HistoryEntry[]>([])

  useEffect(() => {
    setHistory(getHistory())
  }, [])

  const filtered = useMemo(
    () => history.filter((h) => h.songName.toLowerCase().includes(query.toLowerCase())),
    [history, query],
  )

  return (
    <motion.div
      initial={shouldAnimate ? { opacity: 0, y: 8 } : false}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className="relative px-margin-mobile md:px-margin-desktop py-xl"
    >
      <AtmosphericOrb color="secondary" size="lg" position="top-left" />

      <div className="relative z-10 max-w-3xl mx-auto">
        <h1 className="text-headline-xl font-bold text-on-surface mb-lg">Generation History</h1>

        <div className="relative mb-lg">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-on-surface-variant pointer-events-none" aria-hidden="true" />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search history…"
            aria-label="Search generation history"
            className="w-full bg-surface-container-high text-on-surface border border-white/10 rounded-xl py-3 pl-12 pr-4 text-body-md placeholder:text-on-surface-variant focus:outline-none focus:border-secondary focus:ring-1 focus:ring-secondary transition-all"
          />
        </div>

        {filtered.length === 0 ? (
          <div className="text-center py-xxl flex flex-col items-center gap-md">
            <Music className="w-12 h-12 text-on-surface-variant" aria-hidden="true" />
            <p className="text-body-lg text-on-surface-variant">
              {history.length === 0 ? 'No searches yet. Try finding similar songs!' : 'No results match your search.'}
            </p>
          </div>
        ) : (
          <motion.div
            variants={shouldAnimate ? containerVariants : undefined}
            initial="hidden"
            animate="visible"
            className="flex flex-col gap-md"
          >
            {filtered.map((entry) => (
              <motion.div key={entry.id} variants={shouldAnimate ? itemVariants : undefined}>
                <div className="glass-panel rounded-lg flex items-center gap-md p-md">
                  <div className="w-12 h-12 rounded-lg bg-surface-container-high flex items-center justify-center flex-shrink-0">
                    <Music className="w-6 h-6 text-on-surface-variant" aria-hidden="true" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-title-md text-on-surface truncate">{entry.songName}</p>
                    <p className="text-body-md text-on-surface-variant">{entry.artists}</p>
                    <p className="text-label-sm text-on-surface-variant">
                      {entry.totalResults} results · {new Date(entry.searchedAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
```

- [ ] **Step 3: Update Favorites page (localStorage)**

Replace `fe/app/(app)/favorites/page.tsx`:

```typescript
'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Star, Music } from 'lucide-react'
import { SongRecommendationCard } from '@/components/ui/SongRecommendationCard'
import { AtmosphericOrb } from '@/components/ui/AtmosphericOrb'
import { TextGradient } from '@/components/ui/TextGradient'
import { Toast } from '@/components/ui/Toast'
import { useMotion } from '@/components/providers/MotionProvider'
import api from '@/lib/api'
import type { SongRecommendation } from '@/lib/types'

const FAVORITES_KEY = 'sonicpro_favorites'

function getFavorites(): SongRecommendation[] {
  if (typeof window === 'undefined') return []
  try { return JSON.parse(localStorage.getItem(FAVORITES_KEY) ?? '[]') } catch { return [] }
}

export function addFavorite(rec: SongRecommendation) {
  const favs = getFavorites()
  if (!favs.find((f) => f.song_id === rec.song_id)) {
    localStorage.setItem(FAVORITES_KEY, JSON.stringify([...favs, rec]))
  }
}

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.05 } },
}
const itemVariants = {
  hidden:  { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' as const } },
}

export default function FavoritesPage() {
  const { shouldAnimate } = useMotion()
  const [favorites, setFavorites] = useState<SongRecommendation[]>([])
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  useEffect(() => {
    setFavorites(getFavorites())
  }, [])

  function handleRemove(songId: string) {
    const updated = favorites.filter((f) => f.song_id !== songId)
    localStorage.setItem(FAVORITES_KEY, JSON.stringify(updated))
    setFavorites(updated)
  }

  async function handleAddToPlaylist(songId: string) {
    const rec = favorites.find((f) => f.song_id === songId)
    if (!rec) return
    try {
      const result = await api.playlists.export(`SonicPro Favorites`, [songId])
      setToast({ message: 'Added to Spotify!', type: 'success' })
      window.open(result.spotify_url, '_blank')
    } catch {
      setToast({ message: 'Failed to export. Try again.', type: 'error' })
    }
  }

  return (
    <motion.div
      initial={shouldAnimate ? { opacity: 0, y: 8 } : false}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className="relative px-margin-mobile md:px-margin-desktop py-xl"
    >
      <AtmosphericOrb color="secondary" size="lg" position="top-left" />

      <div className="relative z-10 max-w-3xl mx-auto">
        <h1 className="text-headline-xl font-bold text-on-surface mb-lg">
          <TextGradient>Favorites</TextGradient>
        </h1>

        {favorites.length === 0 ? (
          <div className="text-center py-xxl flex flex-col items-center gap-md">
            <Star className="w-12 h-12 text-on-surface-variant" aria-hidden="true" />
            <p className="text-body-lg text-on-surface-variant">No favorites yet.</p>
            <p className="text-body-md text-on-surface-variant">Star songs from your recommendations to save them here.</p>
          </div>
        ) : (
          <motion.div
            variants={shouldAnimate ? containerVariants : undefined}
            initial="hidden"
            animate="visible"
            className="flex flex-col gap-md"
          >
            {favorites.map((rec) => (
              <motion.div key={rec.song_id} variants={shouldAnimate ? itemVariants : undefined}>
                <SongRecommendationCard rec={rec} onAddToPlaylist={handleAddToPlaylist} />
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>

      {toast && <Toast message={toast.message} type={toast.type} onDismiss={() => setToast(null)} />}
    </motion.div>
  )
}
```

- [ ] **Step 4: Update Stats page (session-local metrics)**

Replace `fe/app/(app)/stats/page.tsx`:

```typescript
'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { GlassPanel } from '@/components/ui/GlassPanel'
import { AtmosphericOrb } from '@/components/ui/AtmosphericOrb'
import { TextGradient } from '@/components/ui/TextGradient'
import { DiscoveryGrowthChart } from '@/components/charts/DiscoveryGrowthChart'
import { useMotion } from '@/components/providers/MotionProvider'
import type { WeeklyDiscovery } from '@/lib/types'
import { getHistory } from '@/app/(app)/history/page'

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.06 } },
}
const itemVariants = {
  hidden:  { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' as const } },
}

const defaultProfile = { energy: 72, danceability: 65, valence: 55, acousticness: 28 }

export default function StatsPage() {
  const { shouldAnimate } = useMotion()
  const [totalSearches, setTotalSearches] = useState(0)
  const [totalResults, setTotalResults] = useState(0)
  const [weeklyData, setWeeklyData] = useState<WeeklyDiscovery[]>([])

  useEffect(() => {
    const history = getHistory()
    setTotalSearches(history.length)
    setTotalResults(history.reduce((sum, h) => sum + h.totalResults, 0))
    const byWeek: Record<string, number> = {}
    history.forEach((h) => {
      const d = new Date(h.searchedAt)
      const weekLabel = `W${Math.ceil(d.getDate() / 7)}`
      byWeek[weekLabel] = (byWeek[weekLabel] ?? 0) + h.totalResults
    })
    const wData = Object.entries(byWeek).map(([week, tracks]) => ({ week, tracks }))
    setWeeklyData(wData.length > 0 ? wData : [{ week: 'W1', tracks: 0 }])
  }, [])

  const stats = [
    { id: 's1', label: 'Total Searches', value: totalSearches },
    { id: 's2', label: 'Songs Discovered', value: totalResults },
  ]

  return (
    <motion.div
      initial={shouldAnimate ? { opacity: 0, y: 8 } : false}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className="relative px-margin-mobile md:px-margin-desktop py-xl"
    >
      <AtmosphericOrb color="secondary" size="lg" position="top-left" />
      <AtmosphericOrb color="primary"   size="md" position="bottom-right" />

      <div className="relative z-10 max-w-5xl mx-auto">
        <h1 className="text-headline-xl font-bold text-on-surface mb-lg">
          <TextGradient>Performance Analytics</TextGradient>
        </h1>

        <motion.div
          variants={shouldAnimate ? containerVariants : undefined}
          initial="hidden"
          animate="visible"
          className="flex flex-wrap gap-md mb-xl"
        >
          {stats.map((stat) => (
            <motion.div key={stat.id} variants={shouldAnimate ? itemVariants : undefined} className="flex-1 min-w-[160px]">
              <GlassPanel className="p-lg">
                <p className="text-label-md text-on-surface-variant mb-sm">{stat.label}</p>
                <p className="text-headline-xl font-bold text-on-surface">{stat.value}</p>
              </GlassPanel>
            </motion.div>
          ))}
        </motion.div>

        <GlassPanel className="p-lg">
          <h2 className="text-title-md font-semibold text-on-surface mb-md">Discovery Growth</h2>
          <DiscoveryGrowthChart data={weeklyData} />
        </GlassPanel>
      </div>
    </motion.div>
  )
}
```

- [ ] **Step 5: Run all FE tests**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent\fe"
pnpm test:run
```

Expected: all tests pass (some may need mock updates — fix any failures before committing).

- [ ] **Step 6: Run FE build**

```powershell
pnpm build
```

Expected: clean build.

- [ ] **Step 7: Commit**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent"
git add fe/app/\(app\)/
git commit -m "feat: update all pages with real API calls, session-local history and favorites"
```

---

## Task 12: End-to-End Verification

**Work from:** `d:\Materi Artificial Intelligence\Machine Learning\Tangent`

- [ ] **Step 1: Run all FE tests**

```powershell
Set-Location fe
pnpm test:run
```

Expected: all test files pass.

- [ ] **Step 2: Run all BE tests**

```powershell
Set-Location ..\be
uv run pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 3: Run FE build**

```powershell
Set-Location ..\fe
pnpm build
```

Expected: clean build, routes: `/`, `/auth-callback`, `/login`, `/favorites`, `/generator/unified`, `/history`, `/history/[id]`, `/stats`.

- [ ] **Step 4: Start BE and verify health**

```powershell
Set-Location ..\be
# ensure .env is set, then:
uv run uvicorn main:app --port 8080 --reload
```

In a separate terminal:
```powershell
Invoke-WebRequest -Uri "http://localhost:8080/api/v1/internal/health" | Select-Object -ExpandProperty Content
```

Expected: `{"status":"healthy"}`

- [ ] **Step 5: Start FE and smoke test**

```powershell
Set-Location ..\fe
pnpm dev
```

Open `http://localhost:3000` — expect redirect to `/login` (auth guard). Verify login page renders with "Connect with Spotify" button.

- [ ] **Step 6: Final commit**

```powershell
Set-Location "d:\Materi Artificial Intelligence\Machine Learning\Tangent"
git add -A
git status
# if clean:
git log --oneline -10
```

---

## Self-Review

**Spec coverage check:**

| Spec Section | Task |
|---|---|
| Monorepo (fe/ + be/) | Task 1 |
| BE auth callback redirects to FE | Task 2 |
| BE: GET /api/v1/search/songs | Task 3 |
| FE: .env.local NEXT_PUBLIC_API_URL | Task 4 |
| FE: SongResult, SongRecommendation types | Task 4 |
| FE: lib/auth.ts JWT helpers | Task 5 |
| FE: lib/api.ts typed client | Task 6 |
| FE: auth-callback page | Task 7 |
| FE: login page | Task 7 |
| FE: auth guard in app shell | Task 7 |
| FE: SongSearchInput (debounced, dropdown) | Task 8 |
| FE: SongRecommendationCard (match %, feature bars, export) | Task 9 |
| FE: Generator Dashboard real API | Task 10 |
| FE: Unified Generator real API | Task 11 |
| FE: History (session-local) | Task 11 |
| FE: Favorites (localStorage) | Task 11 |
| FE: Stats (session-local) | Task 11 |
| Error handling (401→login, 422 messages, 429) | Task 6 (api.ts), Task 10 |
| End-to-end smoke test | Task 12 |

**No gaps found. No placeholders.**

**Type consistency:** `SongResult` defined in Task 4, consumed in Tasks 8, 10, 11. `SongRecommendation` defined in Task 4, consumed in Tasks 9, 10, 11. `RecommendationResponse` defined in Task 4, returned by `api.recommendations.getSongs()` in Task 6, destructured in Tasks 10, 11. All consistent.
