"""Cloudinary image service for the Contacts API.

This module provides functionality for uploading and deleting images using Cloudinary.
"""

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
    """Service for managing images in Cloudinary.

    This class provides methods for uploading and deleting images
    using the Cloudinary service.
    """

    @staticmethod
    async def upload(file, public_id: Optional[str] = None) -> dict:
        """Upload an image to Cloudinary.

        Args:
            file: The image file to upload
            public_id (Optional[str]): Custom public ID for the uploaded image

        Returns:
            dict: Cloudinary upload response containing image details
        """
        r = cloudinary.uploader.upload(file, public_id=public_id)
        return r

    @staticmethod
    async def delete(public_id: str) -> dict:
        """Delete an image from Cloudinary.

        Args:
            public_id (str): Public ID of the image to delete

        Returns:
            dict: Cloudinary delete response
        """
        r = cloudinary.uploader.destroy(public_id)
        return r
