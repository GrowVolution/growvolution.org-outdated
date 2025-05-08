from LIBRARY import *

cloudinary_.config(
    cloud_name=os.getenv('CLOUDINARY_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

NOT_FOUND_ASSET = "not_found"
DEFAULT_FOLDER = "growv_data"
PROFILE_PIC_FOLDER = "profile_pictures"

def upload_asset(file,
                 preset='profile_pics', public_id=None,
                 folder=DEFAULT_FOLDER, file_type='image'):
    return cloudinary_uploader.upload(
        file,
        upload_preset=preset,
        public_id=public_id,
        folder=folder,
        overwrite=True,
        resource_type=file_type
    )

def retrieve_asset_url(asset_id, asset_folder=DEFAULT_FOLDER):
    public_path = f"{asset_folder}/{asset_id}"

    try:
        result = cloudinary_api.resource(public_path)
        return result.get("secure_url")

    except cloudinary_.exceptions.NotFound:
        if asset_id != NOT_FOUND_ASSET:
            return retrieve_asset_url(NOT_FOUND_ASSET)

        return None
