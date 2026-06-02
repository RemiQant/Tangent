from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.db_service import DBService

router = APIRouter(
    prefix="/users",
    tags=["Users & Supabase Testing"],
)

# Pydantic Schemas for validation
class MockUserCreate(BaseModel):
    spotify_id: str
    username: str

def get_db_service():
    return DBService()

@router.post("/mock-login")
def mock_supabase_login(user: MockUserCreate, db: DBService = Depends(get_db_service)):
    """
    Since Spotify OAuth isn't ready yet, use this endpoint to test your Supabase connection.
    It manually inserts a mock user into your Supabase 'users' table.
    """
    try:
        data = db.upsert_user(
            spotify_id=user.spotify_id,
            username=user.username
        )
        return {"message": "User saved to Supabase successfully!", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{spotify_id}")
def get_user(spotify_id: str, db: DBService = Depends(get_db_service)):
    """
    Fetch a user from Supabase using their Spotify ID.
    """
    try:
        user_data = db.get_user_by_id(spotify_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found in Supabase")
        return {"user": user_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
