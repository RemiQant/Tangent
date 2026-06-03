ALTER TABLE "generated_playlists" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "playlist_songs" ADD FOREIGN KEY ("playlist_id") REFERENCES "generated_playlists" ("id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "playlist_songs" ADD FOREIGN KEY ("song_id") REFERENCES "songs" ("id") DEFERRABLE INITIALLY IMMEDIATE;

CREATE INDEX IF NOT EXISTS "idx_generated_playlists_user_id" ON "generated_playlists" ("user_id");
CREATE INDEX IF NOT EXISTS "idx_playlist_songs_playlist_id" ON "playlist_songs" ("playlist_id");
CREATE INDEX IF NOT EXISTS "idx_playlist_songs_song_id" ON "playlist_songs" ("song_id");