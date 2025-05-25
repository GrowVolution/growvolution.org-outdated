from cloudinary import uploader, api
from typing import Any
import cloudinary, os

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

NOT_FOUND_ASSET = "not_found"
DEFAULT_FOLDER = "growv_data"
PROFILE_PIC_FOLDER = "profile_pictures"


def upload_asset(file: Any,
                 preset: str = 'default', public_id: str | None = None,
                 folder: str = DEFAULT_FOLDER, overwrite: bool | None = None,
                 file_type: str = 'image') -> dict:
    return uploader.upload(
        file,
        upload_preset=preset,
        public_id=public_id,
        folder=folder,
        overwrite=overwrite,
        resource_type=file_type
    )


def retrieve_asset_url(asset_id: str) -> str | None:
    try:
        result = api.resource(asset_id)
        return result.get("secure_url")

    except cloudinary.exceptions.NotFound:
        if asset_id != NOT_FOUND_ASSET:
            return retrieve_asset_url(NOT_FOUND_ASSET)

        return None
