from app.ml.model import lifespan
from app.ml.song_generator import generate_similar_songs
from app.ml.schemas import PredictRequest, PredictResponse, SongRecommendation

__all__ = [
    "lifespan",
    "generate_similar_songs",
    "PredictRequest",
    "PredictResponse",
    "SongRecommendation"
]
