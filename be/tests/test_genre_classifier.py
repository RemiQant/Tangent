import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.genre_classifier import classify_genres, classify_single_genre


def test_edm_subgenres_all_map_to_edm_family():
    for genre in ["edm", "electro house", "melodic dubstep", "techno", "future bass", "trance"]:
        assert "EDM" in classify_single_genre(genre)


def test_metal_subgenres_all_map_to_metal_family():
    for genre in ["metal", "death metal", "black metal", "nu metal", "heavy metal"]:
        assert "Metal" in classify_single_genre(genre)


def test_bare_industrial_is_neutral():
    families = classify_single_genre("industrial")
    assert families == frozenset({"Industrial"})
    assert "EDM" not in families
    assert "Metal" not in families


def test_industrial_metal_maps_to_metal_only():
    families = classify_single_genre("industrial metal")
    assert families == frozenset({"Metal"})


def test_industrial_techno_maps_to_edm_only():
    families = classify_single_genre("industrial techno")
    assert families == frozenset({"EDM"})


def test_edm_seed_with_bare_industrial_does_not_match_industrial_metal_candidate():
    seed_families = classify_genres(["edm", "industrial"])
    candidate_families = classify_genres(["industrial metal"])
    assert not (seed_families & candidate_families)


def test_metal_seed_matches_industrial_metal_candidate():
    seed_families = classify_genres(["heavy metal"])
    candidate_families = classify_genres(["industrial metal"])
    assert seed_families & candidate_families


def test_edm_seed_matches_industrial_techno_candidate():
    seed_families = classify_genres(["edm"])
    candidate_families = classify_genres(["industrial techno"])
    assert seed_families & candidate_families


def test_multi_family_genre_electronic_rock():
    families = classify_single_genre("electronic rock")
    assert families == frozenset({"EDM", "Rock"})


def test_unknown_genre_returns_empty_set():
    assert classify_single_genre("shoegaze") == frozenset()


def test_classify_genres_unions_across_multiple_tags():
    families = classify_genres(["k-pop", "edm", "shoegaze"])
    assert families == frozenset({"Pop", "EDM"})


def test_classify_genres_empty_input():
    assert classify_genres([]) == frozenset()
