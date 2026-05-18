"""通用工具函式"""
from functools import lru_cache


def get_site_settings() -> dict:
    """讀取常用設定，注入每個模板（用 lru_cache 減少 DB 查詢）"""
    try:
        from app.models.setting import Setting

        return {
            "name": Setting.get("site_name", "ROSZIE INK"),
            "tagline": Setting.get("site_tagline", ""),
            "logo_url": Setting.get("site_logo_url", ""),
            "favicon_url": Setting.get("site_favicon_url", ""),
            "instagram_url": Setting.get("instagram_url", ""),
            "facebook_url": Setting.get("facebook_url", ""),
            "tiktok_url": Setting.get("tiktok_url", ""),
            "address": Setting.get("studio_address", ""),
            "phone": Setting.get("studio_phone", ""),
            "email": Setting.get("studio_email", ""),
            "business_hours": Setting.get("business_hours", {}),
            "ga_id": Setting.get("ga_tracking_id", ""),
        }
    except Exception:
        # 資料庫尚未初始化時（第一次啟動）回傳預設值
        return {
            "name": "ROSZIE INK",
            "tagline": "",
            "logo_url": "",
            "favicon_url": "",
            "instagram_url": "",
            "facebook_url": "",
            "tiktok_url": "",
            "address": "",
            "phone": "",
            "email": "",
            "business_hours": {},
            "ga_id": "",
        }


def paginate_query(query, page: int, per_page: int = 12):
    """統一分頁邏輯，回傳 Flask-SQLAlchemy Pagination 物件"""
    return query.paginate(page=page, per_page=per_page, error_out=False)


def allowed_image(filename: str) -> bool:
    """檢查副檔名是否在白名單內"""
    from flask import current_app

    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


def is_business_open() -> bool:
    """根據設定的營業時間判斷目前是否營業中"""
    from datetime import datetime

    hours = get_site_settings().get("business_hours", {})
    if not hours:
        return False

    now = datetime.now()
    weekday = now.strftime("%A").lower()  # monday, tuesday...
    day_hours = hours.get(weekday)

    if not day_hours or not day_hours.get("open"):
        return False

    try:
        open_h, open_m = map(int, day_hours["from"].split(":"))
        close_h, close_m = map(int, day_hours["to"].split(":"))
        open_time = now.replace(hour=open_h, minute=open_m, second=0)
        close_time = now.replace(hour=close_h, minute=close_m, second=0)
        return open_time <= now <= close_time
    except Exception:
        return False
