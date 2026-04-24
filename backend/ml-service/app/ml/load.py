from contextlib import asynccontextmanager
import joblib
import logging
import pandas as pd
from pathlib import Path
from fastapi import FastAPI
from app.ml.constants import METADATA_COLS, FEATURE_COLS
from app.core.exceptions import LoadError

logger = logging.getLogger("uvicorn.error")


def load_knn_model():
    model_path = Path(__file__).parent.parent.parent / "models" / "knn_model.pkl"
    
    try:
        model = joblib.load(model_path)
        logger.info("KNN model loaded successfully.")
        return model
    except FileNotFoundError:
        raise LoadError(f"Cannot find model file at {model_path}")
    except Exception as e:
        raise LoadError(f"Failed to load KNN model: {str(e)}") from e


def load_music_dataset():
    csv_path = Path(__file__).parent.parent.parent / "data" / "processed" / "spotify_features_scaled.csv"

    try:
        df = pd.read_csv(csv_path)

        required_cols = set(METADATA_COLS) | set(FEATURE_COLS)
        missing_cols = required_cols - set(df.columns)
        if missing_cols:
            raise LoadError(f"Dataset is missing required columns: {sorted(missing_cols)}")

        logger.info("Music dataset loaded successfully: %s tracks.", len(df))
        return df
    except FileNotFoundError:
        raise LoadError(f"Cannot find dataset at {csv_path}")
    except Exception as e:
        raise LoadError(f"Failed to load dataset: {str(e)}") from e


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.knn_model = load_knn_model()
    app.state.music_df = load_music_dataset()

    yield

    app.state.knn_model = None
    app.state.music_df = None
