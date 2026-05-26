"""後台 — 圖片上傳"""
import uuid
from pathlib import Path

from flask import current_app, jsonify, request
from flask_login import login_required

from app.blueprints.admin import admin_bp
from app.utils.decorators import editor_required

ALLOWED = {"jpg", "jpeg", "png", "gif", "webp"}


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
        import io

        img = Image.open(file)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail((2000, 2000), Image.LANCZOS)

        upload_root = Path(current_app.config["UPLOAD_FOLDER"])
        filename = uuid.uuid4().hex + ".jpg"

        # 原圖
        folder = upload_root / subfolder
        folder.mkdir(parents=True, exist_ok=True)
        img.save(str(folder / filename), "JPEG", quality=85, optimize=True)
        image_url = f"/uploads/{subfolder}/{filename}"

        # 縮圖
        thumb = img.copy()
        thumb.thumbnail((400, 400), Image.LANCZOS)
        thumb_folder = upload_root / subfolder / "thumbs"
        thumb_folder.mkdir(parents=True, exist_ok=True)
        thumb.save(str(thumb_folder / filename), "JPEG", quality=85, optimize=True)
        thumb_url = f"/uploads/{subfolder}/thumbs/{filename}"

        return jsonify({"image_url": image_url, "thumb_url": thumb_url})

    except Exception as e:
        current_app.logger.error(f"圖片上傳失敗: {e}")
        return jsonify({"error": "上傳失敗，請重試"}), 500
