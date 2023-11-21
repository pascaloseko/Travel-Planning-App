import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class SupabaseClient:
    def __init__(self):
        self.client = self.get_supabase_client()

    @staticmethod
    def get_supabase_client() -> Client:
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")

        supabase: Client = create_client(url, key)
        return supabase
