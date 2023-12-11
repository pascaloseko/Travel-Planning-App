import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


class SupabaseClient:
    def __init__(self):
        self.client = self.get_supabase_client()
        self.bucket_name = "profile"

    @staticmethod
    def get_supabase_client() -> Client:
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")

        supabase: Client = create_client(url, key)
        return supabase

    async def upload_image_to_storage(
        self, user_id: str, file_data: bytes, file_format: str
    ):
        file_name = f"{user_id}.{file_format}"
        file_path = f"{user_id}/{file_name}"

        try:
            content_type = (
                f"image/{file_format}"
                if file_format in ["png", "jpg", "jpeg"]
                else "image/png"
            )

            response = self.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_data,
                file_options={"content-type": content_type},
            )

            if response.status_code == 200:
                return file_data, None  # Return image data and no error

        except Exception as e:
            if "already exists" in str(e):
                # If the file already exists, update it
                try:
                    response = self.client.storage.from_(self.bucket_name).update(
                        file=file_data,
                        path=file_path,
                        file_options={"cache-control": "3600", "upsert": "true"},
                    )
                    if response.status_code == 200:
                        return response, None  # Return image data and no error
                except Exception as e:
                    error_message = f"Failed to update image. {str(e)}"
                    return None, error_message

        return None, None

    async def fetch_image_by_user_id(
        self, user_id: str
    ) -> (bytes, None) or (None, str):
        try:
            file_path = f"{user_id}/{user_id}.png"

            response = self.client.storage.from_(self.bucket_name).download(file_path)

            return response, None
        except Exception as e:
            if "not_found" in str(e):
                return None, None
            error_message = f"Error fetching image: {str(e)}"
            return None, error_message
