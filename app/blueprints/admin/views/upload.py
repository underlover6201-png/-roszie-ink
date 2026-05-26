"""後台 — 圖片上傳（Cloudinary 優先，fallback 本機）"""
import io
import uuid
from pathlib import Path

from flask import current_app, jsonify, request
from flask_login import login_required

from app.blueprints.admin import admin_bp
from app.utils.decorators import editor_required

ALLOWED = {"jpg", "jpeg", "png", "gif", "webp"}


def _use_cloudinary() -> bool:
    cfg = current_app.config
    return bool(
        cfg.get("CLOUDINARY_CLOUD_NAME")
        and cfg.get("CLOUDINARY_API_KEY")
        and cfg.get("CLOUDINARY_API_SECRET")
    )


def _upload_cloudinary(buf: bytes, folder: str) -> tuple[str, str]:
    """Upload to Cloudinary, return (image_url, thumb_url)."""
    import cloudinary
    import cloudinary.uploader

    cfg = current_app.config
    cloudinary.config(
        cloud_name=cfg["CLOUDINARY_CLOUD_NAME"],
        api_key=cfg["CLOUDINARY_API_KEY"],
        api_secret=cfg["CLOUDINARY_API_SECRET"],
        secure=True,
    )

    public_id = f"roszie-ink/{folder}/{uuid.uuid4().hex}"
    result = cloudinary.uploader.upload(
        buf,
        public_id=public_id,
        overwrite=True,
        resource_type="image",
        quality="auto",
        fetch_format="auto",
    )
    image_url = result["secure_url"]
    thumb_url = image_url  # Cloudinary 自動最佳化，不另加 transform

    return image_url, thumb_url


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

        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=85, optimize=True)
        buf.seek(0)

        if _use_cloudinary():
            image_url, thumb_url = _upload_cloudinary(buf.read(), subfolder)
        else:
            # 本機存檔（Railway 重啟會消失，僅開發用）
            filename = uuid.uuid4().hex + ".jpg"
            upload_root = Path(current_app.config["UPLOAD_FOLDER"])

            folder_path = upload_root / subfolder
            folder_path.mkdir(parents=True, exist_ok=True)
            buf.seek(0)
            (folder_path / filename).write_bytes(buf.read())
            image_url = f"/uploads/{subfolder}/{filename}"

            thumb = img.copy()
            thumb.thumbnail((400, 400), Image.LANCZOS)
            thumb_folder = upload_root / subfolder / "thumbs"
            thumb_folder.mkdir(parents=True, exist_ok=True)
            tbuf = io.BytesIO()
            thumb.save(tbuf, "JPEG", quality=85, optimize=True)
            (thumb_folder / filename).write_bytes(tbuf.getvalue())
            thumb_url = f"/uploads/{subfolder}/thumbs/{filename}"

        return jsonify({"image_url": image_url, "thumb_url": thumb_url})

    except Exception as e:
        current_app.logger.error(f"圖片上傳失敗: {e}")
        return jsonify({"error": f"上傳失敗：{e}"}), 500
