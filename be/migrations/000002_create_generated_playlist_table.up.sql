CREATE TABLE IF NOT EXISTS "generated_playlists" (
    "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "seed_song_id" text NOT NULL,
    "created_at" timestamptz DEFAULT now()
);