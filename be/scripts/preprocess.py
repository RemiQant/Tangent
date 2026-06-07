"""
Run this after placing tracks_features.csv in be/data/raw/
Output: be/data/processed/spotify_features_scaled.csv
"""
from pathlib import Path
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

RAW = Path(__file__).parent.parent / "data" / "raw" / "tracks_features.csv"
OUT = Path(__file__).parent.parent / "data" / "processed" / "spotify_features_scaled.csv"

METADATA_COLS = ["id", "name", "artists"]
FEATURE_COLS = ["danceability", "energy", "speechiness", "acousticness",
                "instrumentalness", "liveness", "valence", "tempo"]

print("Loading dataset...")
df = pd.read_csv(RAW)
print(f"  Loaded {len(df):,} rows")

df = df[METADATA_COLS + FEATURE_COLS + ["loudness"]].copy()
df = df.dropna(subset=["name"])
df = df.loc[~df.duplicated(subset=["name", "artists"])].reset_index(drop=True)
df = df.drop(columns=["loudness"])
print(f"  After dedup: {len(df):,} rows")

scaler = MinMaxScaler()
df[FEATURE_COLS] = scaler.fit_transform(df[FEATURE_COLS])

OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)
print(f"Done! Saved to {OUT}")
print(f"  Final shape: {df.shape}")
