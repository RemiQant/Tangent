from pydantic import BaseModel, Field
from typing import List

class PredictRequest(BaseModel):
    song_id: str
    max_distance: float = Field(
        default=0.5,
        ge=0.0,
        le=5.0,
        description="Similarity threshold. Lower means stricter matches."
    )

class SongRecommendation(BaseModel):
    song_id: str
    name: str
    artists: str
    distance_score: float
    
    danceability: float
    energy: float
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float

class PredictResponse(BaseModel):
    seed_song_id: str
    total_recommendations: int
    recommendations: List[SongRecommendation]
