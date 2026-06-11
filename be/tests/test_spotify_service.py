import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.spotify import SpotifyService


def test_get_artist_genres_logs_warning_on_non_200(caplog):
    service = SpotifyService(access_token="fake-token")

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_http = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_http
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.text = "Too Many Requests"
        mock_http.get = AsyncMock(return_value=mock_resp)

        with caplog.at_level("WARNING"):
            result = asyncio.run(service.get_artist_genres(["artist1"]))

    assert result == {}
    assert any("get_artist_genres failed" in rec.message for rec in caplog.records)
    assert any("429" in rec.message for rec in caplog.records)


def test_get_track_artists_logs_warning_on_non_200(caplog):
    service = SpotifyService(access_token="fake-token")

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_http = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_http
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        mock_http.get = AsyncMock(return_value=mock_resp)

        with caplog.at_level("WARNING"):
            result = asyncio.run(service.get_track_artists(["track1"]))

    assert result == {}
    assert any("get_track_artists failed" in rec.message for rec in caplog.records)
    assert any("401" in rec.message for rec in caplog.records)


def test_get_artist_genres_returns_partial_data_on_mixed_responses():
    service = SpotifyService(access_token="fake-token")
    artist_ids = [f"a{i}" for i in range(60)]  # forces 2 chunks (50 + 10)

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_http = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_http

        ok_resp = MagicMock()
        ok_resp.status_code = 200
        ok_resp.json.return_value = {"artists": [{"id": "a0", "genres": ["edm"]}]}

        fail_resp = MagicMock()
        fail_resp.status_code = 500
        fail_resp.text = "Internal Server Error"

        mock_http.get = AsyncMock(side_effect=[ok_resp, fail_resp])

        result = asyncio.run(service.get_artist_genres(artist_ids))

    assert result == {"a0": ["edm"]}
