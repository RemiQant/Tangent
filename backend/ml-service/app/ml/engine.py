from app.ml.schemas import PredictResponse, SongRecommendation
from app.core.ml_exceptions import SongNotFoundError, InsufficientRecommendationsError
from app.ml.constants import FEATURE_COLS

__all__ = ["generate_similar_songs"]

def generate_similar_songs(song_id: str, model, df, max_distance: float = 0.5) -> PredictResponse:
    song_matches = df[df['id'] == song_id]

    if len(song_matches) == 0:
        raise SongNotFoundError(f"Song with ID '{song_id}' not found in dataset")
    
    song_index = song_matches.index[0]
    seed_song_math = df.iloc[[song_index]][FEATURE_COLS]

    distances, indices = model.kneighbors(seed_song_math)

    recommended_indices = indices[0][1:]    # skip seed song itself
    recommendation_distances = distances[0][1:]

    valid_mask = recommendation_distances <= max_distance
    filtered_indices = recommended_indices[valid_mask]
    filtered_distances = recommendation_distances[valid_mask]

    if len(filtered_indices) < 10:
        raise InsufficientRecommendationsError(
            f"Failsafe triggered: only found {len(filtered_indices)} similar songs within max_distance={max_distance}"
        )
    
    recommendations_list = []

    for idx, dist in zip(filtered_indices, filtered_distances):
        row = df.iloc[idx]

        rec = SongRecommendation(
            song_id=row['id'],
            name=row['name'],
            artists=row['artists'],
            distance_score=float(dist),
            danceability=float(row['danceability']),
            energy=float(row['energy']),
            speechiness=float(row['speechiness']),
            acousticness=float(row['acousticness']),
            instrumentalness=float(row['instrumentalness']),
            liveness=float(row['liveness']),
            valence=float(row['valence']),
            tempo=float(row['tempo'])
        )
        recommendations_list.append(rec)

    return PredictResponse(
        seed_song_id=song_id,
        total_recommendations=len(recommendations_list),
        recommendations=recommendations_list
    )