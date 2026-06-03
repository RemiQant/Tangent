import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def filter_songs_by_genre(
    generated_track_ids: List[str], 
    seed_genres: List[str], 
    track_to_artist: Dict[str, str], 
    artist_genres: Dict[str, List[str]], 
    max_songs: int = 30
) -> List[str]:
    """
    Filters a list of track IDs down to only those whose artists' genres 
    intersect with the seed song's genres.
    
    Args:
        generated_track_ids: The list of 100 tracks from the KNN engine.
        seed_genres: The genres of the original seed song.
        track_to_artist: A map of track_id -> artist_id.
        artist_genres: A map of artist_id -> [genre1, genre2, ...].
        max_songs: Maximum number of songs to return (default 30).
        
    Returns:
        A filtered list of track IDs.
    """
    filtered_tracks = []
    seed_genre_set = set(seed_genres)
    
    # If seed_genres is empty, return top N without filtering
    if not seed_genre_set:
        return generated_track_ids[:max_songs]
        
    for track_id in generated_track_ids:
        artist_id = track_to_artist.get(track_id)
        if not artist_id:
            continue
            
        genres_for_this_artist = set(artist_genres.get(artist_id, []))
        
        # Check for intersection. If ANY genre matches, keep the song.
        if seed_genre_set.intersection(genres_for_this_artist):
            filtered_tracks.append(track_id)
            
        if len(filtered_tracks) >= max_songs:
            break
            
    return filtered_tracks
