import base64
import io
import os
from typing import Union

from uplink_python.errors import StorjException
from uplink_python.module_classes import ListObjectsOptions
from uplink_python.project import Project
from uplink_python.uplink import Uplink


class StorjClient:
    def __init__(self):
        self.storj = self._get_storj_client()
        self.bucket_name = "profile"

    @staticmethod
    def _get_storj_client() -> Project:
        try:
            api_key = os.environ.get("STORJ_API_KEY")

            uplink = Uplink()
            access = uplink.parse_access(api_key)
            project = access.open_project()
            return project
        except Exception as e:
            print(e)

    async def upload_user_profile(
        self, user_id: str, file_path: str, file_content: bytes
    ) -> str:
        uploaded = None
        try:
            if self.storj:
                object_name = f"{user_id}/{os.path.basename(file_path)}"
                uploaded = self.storj.upload_object(self.bucket_name, object_name)

                uploaded.write(file_content, len(file_content))
                uploaded.commit()

                return ""
            return "Failed to initialize Storj"
        except StorjException as e:
            if uploaded:
                uploaded.abort()
            return str(e)

    async def get_user_profile_image(self) -> Union[str, None]:
        try:
            if not self.storj:
                raise StorjException(
                    "Failed to initialize Storj", 500, "storj not initialized"
                )

            objects_list = self.storj.list_objects(
                self.bucket_name, ListObjectsOptions(recursive=True, system=True)
            )

            # Find the image with the most recent creation time
            most_recent_image = None
            max_creation_time = 0

            for obj in objects_list:
                creation_time = obj.get_dict().get("system", {}).get("created", 0)
                if creation_time > max_creation_time:
                    max_creation_time = creation_time
                    most_recent_image = obj.get_dict()

            if most_recent_image:
                image_key = most_recent_image["key"]
                object_name = f"{image_key}"
                print(f"object {object_name}")

                download = self.storj.download_object(self.bucket_name, object_name)
                image_data_in_bytes = download.read(download.file_size())
                image_data = base64.b64encode(image_data_in_bytes[0]).decode()

                return image_data

            return None  # Return None if no image found
        except StorjException as storj_error:
            raise storj_error
        except Exception as e:
            raise StorjException(
                f"An unexpected error occurred: {e}", 500, "unexpected error"
            )
