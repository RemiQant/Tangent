from contextlib import asynccontextmanager
import joblib
import logging
import pandas as pd
from pathlib import Path
from fastapi import FastAPI
from app.ml.constants import METADATA_COLS, FEATURE_COLS

logger = logging.getLogger("uvicorn.error")

def load_knn_model():
    model_path = Path(__file__).parent / "knn_model.pkl"
    
    try:
        model = joblib.load(model_path)
        logger.info("KNN model loaded successfully.")
        return model
    except FileNotFoundError:
        logger.error(f"Cannot find model file at {model_path}")
        raise RuntimeError("Server failed to start: Missing KNN model file.")
    except Exception as e:
        logger.error(f"Failed to load KNN model: {e}")
        raise RuntimeError('Server failed to start: Corrupted model file.')

def load_music_dataset():
    csv_path = Path(__file__).parent.parent.parent / "data" / "processed" / "spotify_features_scaled.csv"

    try:
        df = pd.read_csv(csv_path)

        required_cols = set(METADATA_COLS) | set(FEATURE_COLS)
        missing_cols = required_cols - set(df.columns)
        if missing_cols:
            raise RuntimeError(f"Missing columns {missing_cols}")

        logger.info(f"Music dataset loaded successfully: {len(df)} tracks.")
        return df
    except FileNotFoundError:
        logger.error(f"Cannot find dataset at {csv_path}")
        raise RuntimeError("Server failed to start: Missing dataset CSV.")
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        raise RuntimeError("Server failed to start: Could not read CSV.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.knn_model = load_knn_model()
    app.state.music_df = load_music_dataset()

    yield

    app.state.knn_model = None
    app.state.music_df = None
