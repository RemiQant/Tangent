CREATE TABLE IF NOT EXISTS "user_tokens" (
    "user_id" uuid PRIMARY KEY,
    "access_token" text NOT NULL,
    "refresh_token" text NOT NULL,
    "expires_at" timestamptz NOT NULL,
    "scope" text,
    "updated_at" timestamptz DEFAULT now(),
    FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE
);