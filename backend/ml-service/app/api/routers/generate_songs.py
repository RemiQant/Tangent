from fastapi import APIRouter, Request
from app.ml import generate_similar_songs, PredictRequest, PredictResponse
from app.core.exceptions import LoadError
from app.middleware.rate_limit import limiter

router = APIRouter()

@router.post("/songs", response_model=PredictResponse)
@limiter.limit("5/minute")
def get_song_recommendations(payload: PredictRequest, request: Request):
    model = getattr(request.app.state, "knn_model", None)
    df = getattr(request.app.state, "music_df", None)

    if model is None or df is None:
        raise LoadError(f"Model or dataset is not loaded. song_id={payload.song_id}")

    return generate_similar_songs(
        song_id=payload.song_id,
        model=model,
        df=df,
        max_distance=payload.max_distance
    )