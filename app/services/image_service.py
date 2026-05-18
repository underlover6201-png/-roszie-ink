"""圖片處理 - 壓縮、縮圖、轉 WebP"""
import io
from pathlib import Path

from PIL import Image


THUMB_SIZE = (400, 400)
MAX_DIMENSION = 2000
QUALITY = 85


def process_and_save(file_obj, subfolder: str, original_filename: str) -> dict:
    """
    處理上傳圖片：壓縮原圖、產生縮圖、轉 WebP
    回傳 {'image_url': ..., 'thumb_url': ..., 'webp_url': ...}
    """
    from app.services.storage_service import get_storage

    storage = get_storage()
    img = Image.open(file_obj)

    # 轉 RGB（避免 PNG RGBA 轉 JPEG 出錯）
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # 限制最大尺寸
    img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    # 儲存壓縮原圖（JPEG）
    orig_buf = io.BytesIO()
    img.save(orig_buf, format="JPEG", quality=QUALITY, optimize=True)
    orig_buf.seek(0)
    image_url = storage.save(orig_buf, subfolder, original_filename)

    # 縮圖
    thumb = img.copy()
    thumb.thumbnail(THUMB_SIZE, Image.LANCZOS)
    thumb_buf = io.BytesIO()
    thumb.save(thumb_buf, format="JPEG", quality=QUALITY, optimize=True)
    thumb_buf.seek(0)
    thumb_url = storage.save(thumb_buf, f"{subfolder}/thumbs", original_filename)

    # WebP 版本
    webp_buf = io.BytesIO()
    img.save(webp_buf, format="WEBP", quality=QUALITY)
    webp_buf.seek(0)
    stem = Path(original_filename).stem
    webp_url = storage.save(webp_buf, subfolder, f"{stem}.webp")

    return {
        "image_url": image_url,
        "thumb_url": thumb_url,
        "webp_url": webp_url,
    }
