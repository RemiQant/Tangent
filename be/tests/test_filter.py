import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.filter import filter_songs_by_genre


def test_empty_seed_genres_returns_unfiltered_with_flag_false():
    result = filter_songs_by_genre(
        generated_track_ids=["t1", "t2", "t3"],
        seed_genres=[],
        track_to_artist={"t1": "a1", "t2": "a2", "t3": "a3"},
        artist_genres={"a1": ["death metal"], "a2": ["edm"], "a3": ["pop"]},
        max_songs=30,
    )
    assert result.genre_filtered is False
    assert result.track_ids == ["t1", "t2", "t3"]
    assert result.track_genre_families == {}


def test_edm_seed_filters_out_metal_candidates():
    result = filter_songs_by_genre(
        generated_track_ids=["edm1", "metal1", "edm2"],
        seed_genres=["edm"],
        track_to_artist={"edm1": "a1", "metal1": "a2", "edm2": "a3"},
        artist_genres={
            "a1": ["electro house"],
            "a2": ["death metal"],
            "a3": ["melodic dubstep"],
        },
        max_songs=30,
    )
    assert result.genre_filtered is True
    assert result.track_ids == ["edm1", "edm2"]
    assert "metal1" not in result.track_ids


def test_industrial_bridging_case_full_pipeline():
    # Seed: EDM artist tagged with bare "industrial".
    # Candidate A (industrial metal) must NOT match.
    # Candidate B (industrial techno) must match.
    result = filter_songs_by_genre(
        generated_track_ids=["metal_track", "edm_track"],
        seed_genres=["edm", "industrial"],
        track_to_artist={"metal_track": "a1", "edm_track": "a2"},
        artist_genres={
            "a1": ["industrial metal"],
            "a2": ["industrial techno"],
        },
        max_songs=30,
    )
    assert "metal_track" not in result.track_ids
    assert "edm_track" in result.track_ids


def test_max_songs_limit_respected():
    track_ids = [f"t{i}" for i in range(50)]
    track_to_artist = {tid: f"a{i}" for i, tid in enumerate(track_ids)}
    artist_genres = {f"a{i}": ["edm"] for i in range(50)}

    result = filter_songs_by_genre(
        generated_track_ids=track_ids,
        seed_genres=["edm"],
        track_to_artist=track_to_artist,
        artist_genres=artist_genres,
        max_songs=10,
    )
    assert len(result.track_ids) == 10


def test_missing_track_to_artist_entries_are_skipped():
    result = filter_songs_by_genre(
        generated_track_ids=["t1", "t2"],
        seed_genres=["edm"],
        track_to_artist={"t1": "a1"},
        artist_genres={"a1": ["edm"]},
        max_songs=30,
    )
    assert result.track_ids == ["t1"]
    assert "t2" not in result.track_ids


def test_genre_data_attached_to_returned_tracks():
    result = filter_songs_by_genre(
        generated_track_ids=["t1"],
        seed_genres=["edm"],
        track_to_artist={"t1": "a1"},
        artist_genres={"a1": ["electro house", "edm"]},
        max_songs=30,
    )
    assert result.track_genres["t1"] == ["electro house", "edm"]
    assert result.track_genre_families["t1"] == ["EDM"]


def test_seed_genres_with_no_known_family_falls_back_unfiltered():
    result = filter_songs_by_genre(
        generated_track_ids=["t1", "t2"],
        seed_genres=["some-totally-unmapped-tag"],
        track_to_artist={"t1": "a1", "t2": "a2"},
        artist_genres={"a1": ["edm"], "a2": ["death metal"]},
        max_songs=30,
    )
    assert result.genre_filtered is False
    assert result.track_ids == ["t1", "t2"]
