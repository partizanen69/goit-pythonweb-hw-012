import cloudinary
import cloudinary.uploader
from typing import Optional


from src.conf.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


class CloudImage:
    @staticmethod
    async def upload(file, public_id: Optional[str] = None) -> dict:
        r = cloudinary.uploader.upload(file, public_id=public_id)
        return r

    @staticmethod
    async def delete(public_id: str) -> dict:
        r = cloudinary.uploader.destroy(public_id)
        return r
