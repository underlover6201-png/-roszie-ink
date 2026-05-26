"""後台 — 圖片上傳（本機 or Cloudflare R2）"""
import io
import uuid
from pathlib import Path

from flask import current_app, jsonify, request
from flask_login import login_required

from app.blueprints.admin import admin_bp
from app.utils.decorators import editor_required

ALLOWED = {"jpg", "jpeg", "png", "gif", "webp"}


def _upload_to_r2(data: bytes, key: str) -> str:
    """Upload bytes to Cloudflare R2, return public URL."""
    import boto3
    from botocore.config import Config

    cfg = current_app.config
    s3 = boto3.client(
        "s3",
        endpoint_url=cfg["S3_ENDPOINT_URL"],
        aws_access_key_id=cfg["S3_ACCESS_KEY"],
        aws_secret_access_key=cfg["S3_SECRET_KEY"],
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )
    bucket = cfg["S3_BUCKET_NAME"]
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=data,
        ContentType="image/jpeg",
        CacheControl="public, max-age=31536000",
    )
    # Public URL pattern for R2 custom domain or r2.dev
    pub_domain = cfg.get("R2_PUBLIC_URL", "").rstrip("/")
    if pub_domain:
        return f"{pub_domain}/{key}"
    # fallback: r2.dev public bucket URL
    account_id = cfg.get("R2_ACCOUNT_ID", "")
    return f"https://{account_id}.r2.dev/{bucket}/{key}"


def _use_r2() -> bool:
    cfg = current_app.config
    return bool(
        cfg.get("STORAGE_BACKEND") == "r2"
        and cfg.get("S3_BUCKET_NAME")
        and cfg.get("S3_ACCESS_KEY")
        and cfg.get("S3_SECRET_KEY")
        and cfg.get("S3_ENDPOINT_URL")
    )


@admin_bp.route("/upload-image", methods=["POST"])
@login_required
@editor_required
def upload_image():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "沒有選擇檔案"}), 400

    ext = Path(file.filename).suffix.lower().lstrip(".")
    if ext not in ALLOWED:
        return jsonify({"error": "請上傳 JPG / PNG / WEBP / GIF"}), 400

    subfolder = request.form.get("subfolder", "works")
    if "/" in subfolder or ".." in subfolder:
        return jsonify({"error": "無效的資料夾"}), 400

    try:
        from PIL import Image

        img = Image.open(file)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail((2000, 2000), Image.LANCZOS)

        filename = uuid.uuid4().hex + ".jpg"

        # ── 縮圖 ──
        thumb = img.copy()
        thumb.thumbnail((400, 400), Image.LANCZOS)

        if _use_r2():
            # 原圖
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=85, optimize=True)
            image_url = _upload_to_r2(buf.getvalue(), f"{subfolder}/{filename}")

            # 縮圖
            tbuf = io.BytesIO()
            thumb.save(tbuf, "JPEG", quality=85, optimize=True)
            thumb_url = _upload_to_r2(tbuf.getvalue(), f"{subfolder}/thumbs/{filename}")
        else:
            upload_root = Path(current_app.config["UPLOAD_FOLDER"])

            folder = upload_root / subfolder
            folder.mkdir(parents=True, exist_ok=True)
            img.save(str(folder / filename), "JPEG", quality=85, optimize=True)
            image_url = f"/uploads/{subfolder}/{filename}"

            thumb_folder = upload_root / subfolder / "thumbs"
            thumb_folder.mkdir(parents=True, exist_ok=True)
            thumb.save(str(thumb_folder / filename), "JPEG", quality=85, optimize=True)
            thumb_url = f"/uploads/{subfolder}/thumbs/{filename}"

        return jsonify({"image_url": image_url, "thumb_url": thumb_url})

    except Exception as e:
        current_app.logger.error(f"圖片上傳失敗: {e}")
        return jsonify({"error": f"上傳失敗：{e}"}), 500
