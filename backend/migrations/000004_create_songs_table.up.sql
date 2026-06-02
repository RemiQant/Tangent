CREATE TABLE IF NOT EXISTS "songs" (
    "id" text PRIMARY KEY,
    "name" text NOT NULL,
    "artists" text NOT NULL,
    "danceability" float NOT NULL,
    "energy" float NOT NULL,
    "acousticness" float NOT NULL,
    "instrumentalness" float NOT NULL,
    "liveness" float NOT NULL,
    "valence" float NOT NULL,
    "tempo" float NOT NULL
);