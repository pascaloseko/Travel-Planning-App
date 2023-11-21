import hashlib
from pydantic import BaseModel

from app.internal.supadb import SupabaseClient


class User(BaseModel):
    username: str
    email: str
    password: str


class UserQueries:
    def __init__(self, supabase_client: SupabaseClient):
        self.supabase_client = supabase_client

    def _hash_password(self, password: str) -> str:
        sha256 = hashlib.sha256()
        sha256.update(password.encode("utf-8"))
        return sha256.hexdigest()

    def verify_password(
        self, entered_password: str, stored_hashed_password: str
    ) -> bool:
        entered_password_hash = self._hash_password(entered_password)
        return entered_password_hash == stored_hashed_password

    def register_user(self, user: User) -> dict:
        try:
            data, count = (
                self.supabase_client.client.table("users")
                .insert(
                    [
                        {
                            "username": user.username,
                            "email": user.email,
                            "password": self._hash_password(user.password),
                        }
                    ]
                )
                .execute()
            )

            return {"data": data, "error": None}
        except Exception as e:
            return {"data": None, "error": str(e)}

    def get_users(self):
        try:
            response = (
                self.supabase_client.client.table("users")
                .select("username", "email")
                .execute()
            )
            return {"data": response, "error": None}
        except Exception as e:
            return {"data": None, "error": e}

    def get_user(self, email: str):
        try:
            response = (
                self.supabase_client.client.table("users")
                .select("*")
                .eq("email", email)
                .execute()
            )
            return {"data": response, "error": None}
        except Exception as e:
            return {"data": None, "error": e}
