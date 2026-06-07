import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request
import httpx
from app.api.routers.generate_songs import get_user_spotify_token
from app.middleware.rate_limit import limiter
from app.ml.schemas.search_schema import SongSearchResult

logger = logging.getLogger(__name__)

router = APIRouter()

# Spotify rejects this app's requests with "Invalid limit" when an explicit
# `limit` is sent, so each page returns its default size (20). We page through
# `offset` instead to widen the candidate pool for filtering against the dataset.
SPOTIFY_PAGE_SIZE = 20
SPOTIFY_SEARCH_PAGES = 3


async def _fetch_search_page(client: httpx.AsyncClient, q: str, offset: int, token: str) -> httpx.Response:
    return await client.get(
        "https://api.spotify.com/v1/search",
        params={"q": q, "type": "track", "offset": offset},
        headers={"Authorization": f"Bearer {token}"},
    )


@router.get("/songs", response_model=list[SongSearchResult])
@limiter.limit("10/minute")
async def search_songs(
    request: Request,
    q: str = Query(..., description="Search query string"),
    limit: int = Query(5, ge=1, le=20),
    spotify_token: str = Depends(get_user_spotify_token),
):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' cannot be empty")

    offsets = [page * SPOTIFY_PAGE_SIZE for page in range(SPOTIFY_SEARCH_PAGES)]
    async with httpx.AsyncClient() as client:
        responses = await asyncio.gather(
            *(_fetch_search_page(client, q, offset, spotify_token) for offset in offsets)
        )

    for response in responses:
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Spotify session expired. Please log in again.")
        if response.status_code == 429:
            raise HTTPException(status_code=429, detail="Spotify rate limit reached")
        if response.status_code != 200:
            logger.warning(
                "Spotify search failed: status=%s url=%s body=%s",
                response.status_code,
                response.request.url,
                response.text[:500],
            )
            raise HTTPException(
                status_code=502,
                detail=f"Spotify search failed (upstream status {response.status_code})",
            )

    seen_ids: set[str] = set()
    items = []
    for response in responses:
        for item in response.json().get("tracks", {}).get("items", []):
            if item["id"] not in seen_ids:
                seen_ids.add(item["id"])
                items.append(item)

    if not items:
        raise HTTPException(status_code=422, detail="No tracks found for the given query")

    dataset_ids: set[str] = getattr(request.app.state, "dataset_ids", set())

    results = [
        SongSearchResult(
            song_id=item["id"],
            name=item["name"],
            artists=", ".join(a["name"] for a in item["artists"]),
            album_art_url=item["album"]["images"][0]["url"] if item["album"]["images"] else "",
        )
        for item in items
        if not dataset_ids or item["id"] in dataset_ids
    ]

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No matching songs found in our recommendation database. Try a different search.",
        )

    return results[:limit]
