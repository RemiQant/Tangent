ALTER TABLE "generated_playlists" DROP CONSTRAINT IF EXISTS generated_playlists_user_id_fkey;
ALTER TABLE "playlist_songs" DROP CONSTRAINT IF EXISTS playlist_songs_playlist_id_fkey;
ALTER TABLE "playlist_songs" DROP CONSTRAINT IF EXISTS playlist_songs_song_id_fkey;

DROP INDEX IF EXISTS "idx_generated_playlists_user_id";
DROP INDEX IF EXISTS "idx_playlist_songs_playlist_id";
DROP INDEX IF EXISTS "idx_playlist_songs_song_id";