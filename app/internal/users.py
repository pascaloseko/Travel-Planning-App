import base64
import hashlib
import imghdr

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
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def verify_password(
        self, entered_password: str, stored_hashed_password: str
    ) -> bool:
        return self._hash_password(entered_password) == stored_hashed_password

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

    async def upload_profile_image(self, user_id: str, file_name: bytes):
        try:
            # Detect file format using imghdr
            file_format = imghdr.what(None, h=file_name)
            if not file_format:
                raise ValueError("Unable to determine file format from bytes.")

            # Call upload_image_to_storage with the detected file format
            (
                image_data,
                error_message,
            ) = await self.supabase_client.upload_image_to_storage(
                user_id, file_name, file_format
            )
            if error_message:
                return {"data": None, "error": str(error_message)}

            return {"data": base64.b64encode(image_data).decode("utf-8"), "error": None}
        except Exception as e:
            return {"data": None, "error": str(e)}

    async def load_profile_image(self, user_id: str):
        try:
            (
                image_data,
                error_message,
            ) = await self.supabase_client.fetch_image_by_user_id(user_id)
            if error_message:
                return {"data": None, "error": error_message}
            return {"data": base64.b64encode(image_data).decode("utf-8"), "error": None}
        except Exception as e:
            return {"data": None, "error": e}
