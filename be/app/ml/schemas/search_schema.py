from pydantic import BaseModel


class SongSearchResult(BaseModel):
    song_id: str
    name: str
    artists: str
    album_art_url: str
