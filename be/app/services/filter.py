import logging
from dataclasses import dataclass, field
from typing import Dict, List

from app.services.genre_classifier import classify_genres

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GenreFilterResult:
    """Result of applying genre-family filtering to KNN candidates."""

    track_ids: List[str]
    genre_filtered: bool
    track_genres: Dict[str, List[str]] = field(default_factory=dict)
    track_genre_families: Dict[str, List[str]] = field(default_factory=dict)


def filter_songs_by_genre(
    generated_track_ids: List[str],
    seed_genres: List[str],
    track_to_artist: Dict[str, str],
    artist_genres: Dict[str, List[str]],
    max_songs: int = 30,
) -> GenreFilterResult:
    """Filters KNN candidates down to those sharing a genre family with the seed.

    Args:
        generated_track_ids: The list of tracks from the KNN engine.
        seed_genres: The raw Spotify genre tags of the seed song's artist.
        track_to_artist: A map of track_id -> artist_id.
        artist_genres: A map of artist_id -> [genre1, genre2, ...].
        max_songs: Maximum number of songs to return (default 30).

    Returns:
        A GenreFilterResult with the (possibly filtered) track IDs, a
        genre_filtered flag (False when no genre-based filtering could be
        applied), and per-track genre/genre-family info for display.
    """
    seed_families = classify_genres(seed_genres)

    if not seed_genres:
        logger.info(
            "No Spotify genres found for seed artist; returning top %d "
            "KNN matches unfiltered (genre_filtered=False)",
            max_songs,
        )
        return GenreFilterResult(
            track_ids=generated_track_ids[:max_songs],
            genre_filtered=False,
        )

    if not seed_families:
        logger.warning(
            "Seed genres %s did not map to any known genre family; "
            "returning top %d KNN matches unfiltered (genre_filtered=False)",
            seed_genres, max_songs,
        )
        return GenreFilterResult(
            track_ids=generated_track_ids[:max_songs],
            genre_filtered=False,
        )

    filtered_tracks: List[str] = []
    track_genres: Dict[str, List[str]] = {}
    track_genre_families: Dict[str, List[str]] = {}

    for track_id in generated_track_ids:
        artist_id = track_to_artist.get(track_id)
        if not artist_id:
            logger.debug("Skipping track %s: no artist mapping found", track_id)
            continue

        genres_for_artist = artist_genres.get(artist_id, [])
        candidate_families = classify_genres(genres_for_artist)

        if seed_families & candidate_families:
            filtered_tracks.append(track_id)
            track_genres[track_id] = list(genres_for_artist)
            track_genre_families[track_id] = sorted(candidate_families)

        if len(filtered_tracks) >= max_songs:
            break

    logger.info(
        "Genre filter: seed_families=%s -> %d/%d candidates kept",
        sorted(seed_families), len(filtered_tracks), len(generated_track_ids),
    )

    return GenreFilterResult(
        track_ids=filtered_tracks,
        genre_filtered=True,
        track_genres=track_genres,
        track_genre_families=track_genre_families,
    )
