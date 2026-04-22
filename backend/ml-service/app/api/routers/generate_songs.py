from fastapi import APIRouter, Request, HTTPException
import logging
from app.ml import generate_similar_songs, PredictRequest, PredictResponse
from app.core.ml_exceptions import SongNotFoundError, InsufficientRecommendationsError
from app.middleware.rate_limit import limiter

logger = logging.getLogger("uvicorn.error")
router = APIRouter()

@router.post("/songs", response_model=PredictResponse)
@limiter.limit("5/minute")
def get_song_recommendations(payload: PredictRequest, request: Request):
    model = getattr(request.app.state, "knn_model", None)
    df = getattr(request.app.state, "music_df", None)

    if model is None or df is None:
        logger.error("MODEL_NOT_READY song_id=%s", payload.song_id)
        raise HTTPException(
            status_code=503, 
            detail={"code": "MODEL_NOT_READY", "message": "Model or dataset is not loaded."}
        )
    
    try:
        return generate_similar_songs(
            song_id=payload.song_id,
            model=model,
            df=df,
            max_distance=payload.max_distance
        )
    except SongNotFoundError as e:
        logger.warning("SONG_NOT_FOUND song_id=%s error=%s", payload.song_id, str(e))
        raise HTTPException(
            status_code=404,
            detail={"code": "SONG_NOT_FOUND", "message": str(e)}
        )
    except InsufficientRecommendationsError as e:
        logger.info("INSUFFICIENT_RECOMMENDATIONS song_id=%s error=%s", payload.song_id, str(e))
        raise HTTPException(
            status_code=422,
            detail={"code": "INSUFFICIENT_RECOMMENDATIONS", "message": str(e)}
        )
    except Exception:
        logger.exception("RECOMMENDATION_INTERNAL_ERROR song_id=%s", payload.song_id)
        raise HTTPException(
            status_code=500,
            detail={"code": "INTERNAL_ERROR", "message": "Unexpected server error while generating recommendations."}
        )