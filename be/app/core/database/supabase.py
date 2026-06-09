import os
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Load from .env/.env.development (dev) or system env (prod)
_env_file = Path(__file__).parents[3] / ".env" / ".env.development"
if _env_file.exists():
    load_dotenv(_env_file)
else:
    load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# We will initialize this safely; if missing, it won't crash import but will fail on usage.
def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)
