CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS "users" (
    "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    "spotify_id" text UNIQUE NOT NULL,
    "username" text NOT NULL,
    "created_at" timestamptz DEFAULT now()
);