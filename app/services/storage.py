import os
from urllib.parse import unquote, urlparse
from uuid import uuid4

import requests


class StorageConfigurationError(RuntimeError):
    pass


class StorageUploadError(RuntimeError):
    pass


class StorageDeleteError(RuntimeError):
    pass


def _storage_config() -> tuple[str, str, str]:
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "cvs")
    if not supabase_url or not service_role_key:
        raise StorageConfigurationError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be configured"
        )
    return supabase_url.rstrip("/"), service_role_key, bucket


def upload_cv_pdf(file_name: str, content: bytes) -> str:
    supabase_url, service_role_key, bucket = _storage_config()

    object_name = f"{uuid4().hex}-{file_name}"
    upload_url = (
        f"{supabase_url.rstrip('/')}/storage/v1/object/"
        f"{bucket}/{object_name}"
    )
    headers = {
        "Authorization": f"Bearer {service_role_key}",
        "apikey": service_role_key,
        "Content-Type": "application/pdf",
        "x-upsert": "false",
    }

    try:
        response = requests.post(
            upload_url,
            headers=headers,
            data=content,
            timeout=30,
        )
    except requests.RequestException as error:
        raise StorageUploadError("Could not reach Supabase Storage") from error

    if not response.ok:
        raise StorageUploadError("Supabase Storage rejected the PDF upload")

    public_url = os.getenv("SUPABASE_STORAGE_PUBLIC_URL")
    if public_url:
        return f"{public_url.rstrip('/')}/{object_name}"
    return f"{supabase_url.rstrip('/')}/storage/v1/object/public/{bucket}/{object_name}"


def delete_cv_pdf(file_url: str) -> None:
    supabase_url, service_role_key, bucket = _storage_config()
    object_name = unquote(urlparse(file_url).path.rstrip("/").rsplit("/", 1)[-1])
    if not object_name:
        raise StorageDeleteError("Could not determine the stored PDF object")

    delete_url = f"{supabase_url}/storage/v1/object/{bucket}/{object_name}"
    headers = {
        "Authorization": f"Bearer {service_role_key}",
        "apikey": service_role_key,
    }

    try:
        response = requests.delete(delete_url, headers=headers, timeout=30)
    except requests.RequestException as error:
        raise StorageDeleteError("Could not reach Supabase Storage") from error

    if not response.ok:
        raise StorageDeleteError("Supabase Storage rejected the PDF deletion")