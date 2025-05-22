import cloudinary
from cloudinary.exceptions import Error
from fastapi import UploadFile
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

import cloudinary.uploader


def upload_file_to_cloudinary(file: UploadFile):
    file.file.seek(0)
    uploaded_file = cloudinary.uploader.upload(
        file.file.read(), unique_filename=False, overwrite=True
    )
    return uploaded_file.get("secure_url")
