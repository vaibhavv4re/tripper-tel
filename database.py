from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Save user preferences
def save_preferences(user_id: str, preferences: str):
    supabase.table("user_preferences").upsert({
        "user_id": user_id,
        "preferences": preferences
    }).execute()

# Get user preferences
def get_preferences(user_id: str) -> str:
    response = supabase.table("user_preferences")\
                      .select("preferences")\
                      .eq("user_id", user_id)\
                      .execute()
    return response.data[0]["preferences"] if response.data else None

# Log interactions
def log_interaction(user_id: str, query: str, response: str):
    supabase.table("interactions").insert({
        "user_id": user_id,
        "query": query,
        "response": response
    }).execute()