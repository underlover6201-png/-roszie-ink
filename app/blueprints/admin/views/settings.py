"""後台 — 網站設定"""
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.blueprints.admin import admin_bp
from app.extensions import db
from app.models.setting import Setting
from app.utils.decorators import admin_required

SETTINGS_SCHEMA = [
    {
        "section": "工作室基本資訊",
        "fields": [
            {"key": "site_name",     "label": "工作室名稱",   "type": "text",     "default": "ROSZIE INK"},
            {"key": "site_tagline",  "label": "標語",         "type": "text",     "default": ""},
            {"key": "studio_address","label": "地址",         "type": "text",     "default": ""},
            {"key": "studio_phone",  "label": "電話",         "type": "text",     "default": ""},
            {"key": "studio_email",  "label": "Email",        "type": "email",    "default": ""},
        ],
    },
    {
        "section": "社群媒體",
        "fields": [
            {"key": "instagram_url", "label": "Instagram URL", "type": "url", "default": ""},
            {"key": "facebook_url",  "label": "Facebook URL",  "type": "url", "default": ""},
            {"key": "tiktok_url",    "label": "TikTok URL",    "type": "url", "default": ""},
        ],
    },
    {
        "section": "SEO",
        "fields": [
            {"key": "site_logo_url",    "label": "Logo URL",         "type": "url",  "default": ""},
            {"key": "site_favicon_url", "label": "Favicon URL",      "type": "url",  "default": ""},
            {"key": "ga_tracking_id",   "label": "Google Analytics ID", "type": "text", "default": ""},
        ],
    },
]


@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
@admin_required
def admin_settings():
    if request.method == "POST":
        for section in SETTINGS_SCHEMA:
            for field in section["fields"]:
                key = field["key"]
                val = request.form.get(key, "").strip()
                setting = Setting.query.filter_by(key=key).first()
                if setting is None:
                    setting = Setting(key=key, description=field["label"])
                    db.session.add(setting)
                setting.set_value(val)
                setting.updated_by = current_user.id
        db.session.commit()
        flash("設定已儲存。", "success")
        return redirect(url_for("admin.admin_settings"))

    current_values = {}
    for s in Setting.query.all():
        current_values[s.key] = s.get_value() or ""

    return render_template(
        "admin/settings/index.html",
        schema=SETTINGS_SCHEMA,
        current_values=current_values,
    )
