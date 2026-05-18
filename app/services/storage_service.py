"""圖片儲存後端 - 本地 / S3 / Cloudflare R2 統一介面"""
import hashlib
import os
import uuid
from pathlib import Path

from flask import current_app


def _hash_filename(original: str) -> str:
    """將原始檔名雜湊化，避免路徑遍歷攻擊和衝突"""
    ext = Path(original).suffix.lower()
    unique = uuid.uuid4().hex
    return f"{unique}{ext}"


class LocalStorage:
    def save(self, file_obj, subfolder: str, original_filename: str) -> str:
        upload_root = current_app.config["UPLOAD_FOLDER"]
        folder = Path(upload_root) / subfolder
        folder.mkdir(parents=True, exist_ok=True)

        filename = _hash_filename(original_filename)
        save_path = folder / filename
        file_obj.save(str(save_path))

        return f"/uploads/{subfolder}/{filename}"

    def delete(self, url: str) -> None:
        upload_root = current_app.config["UPLOAD_FOLDER"]
        relative = url.replace("/uploads/", "")
        path = Path(upload_root) / relative
        if path.exists():
            path.unlink()


class S3Storage:
    """AWS S3 / Cloudflare R2（API 相容）"""

    def __init__(self):
        import boto3

        self.client = boto3.client(
            "s3",
            region_name=current_app.config["S3_REGION"],
            endpoint_url=current_app.config.get("S3_ENDPOINT_URL"),
            aws_access_key_id=current_app.config["S3_ACCESS_KEY"],
            aws_secret_access_key=current_app.config["S3_SECRET_KEY"],
        )
        self.bucket = current_app.config["S3_BUCKET_NAME"]

    def save(self, file_obj, subfolder: str, original_filename: str) -> str:
        filename = _hash_filename(original_filename)
        key = f"{subfolder}/{filename}"
        ext = Path(original_filename).suffix.lower()
        content_type = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }.get(ext, "application/octet-stream")

        self.client.upload_fileobj(
            file_obj,
            self.bucket,
            key,
            ExtraArgs={"ContentType": content_type, "ACL": "public-read"},
        )
        endpoint = current_app.config.get("S3_ENDPOINT_URL", "")
        return f"{endpoint}/{self.bucket}/{key}"

    def delete(self, url: str) -> None:
        # URL 中最後的部分就是 S3 key
        key = "/".join(url.split("/")[-2:])
        self.client.delete_object(Bucket=self.bucket, Key=key)


def get_storage():
    """根據設定回傳對應的儲存後端實例"""
    backend = current_app.config.get("STORAGE_BACKEND", "local")
    if backend in ("s3", "r2"):
        return S3Storage()
    return LocalStorage()
