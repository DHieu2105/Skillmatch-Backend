import hashlib
import os
import time
import requests

class CloudinaryConfigError(RuntimeError):
    pass

class CloudinaryUploadError(RuntimeError):
    pass

def upload_avatar_to_cloudinary(file_bytes: bytes, filename: str) -> str:
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if not cloud_name or not api_key or not api_secret:
        raise CloudinaryConfigError(
            "CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY và CLOUDINARY_API_SECRET cần được cấu hình trong Backend/.env"
        )

    timestamp = str(int(time.time()))
    folder = "avatars"

    # Cloudinary signed upload: generate signature sorted alphabetically
    to_sign = f"folder={folder}&timestamp={timestamp}{api_secret}"
    signature = hashlib.sha1(to_sign.encode("utf-8")).hexdigest()

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
    data = {
        "api_key": api_key,
        "timestamp": timestamp,
        "folder": folder,
        "signature": signature,
    }
    files = {
        "file": (filename, file_bytes)
    }

    try:
        response = requests.post(url, data=data, files=files, timeout=30)
    except requests.RequestException as err:
        raise CloudinaryUploadError("Không thể kết nối đến dịch vụ Cloudinary") from err

    if not response.ok:
        raise CloudinaryUploadError(f"Cloudinary upload thất bại ({response.status_code}): {response.text}")

    result = response.json()
    return result.get("secure_url") or result.get("url")

