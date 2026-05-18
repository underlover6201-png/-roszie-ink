"""
開發用假資料（執行一次即可）
用法：python scripts/seed_data.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import db
from app.models.artist import Artist, Style
from app.models.setting import Setting
from app.models.work import WorkCategory


def seed():
    app = create_app("development")
    with app.app_context():
        db.create_all()

        # 風格標籤
        styles_data = [
            ("黑灰寫實", "blackgray-realism"),
            ("傳統美式", "traditional"),
            ("幾何線條", "geometric"),
            ("日式和風", "japanese"),
            ("水彩風格", "watercolor"),
            ("極簡線條", "fineline"),
        ]
        for name, slug in styles_data:
            if not Style.query.filter_by(slug=slug).first():
                db.session.add(Style(name=name, slug=slug))

        # 作品分類
        cats_data = [
            ("手臂", "arm"), ("腿部", "leg"), ("背部", "back"),
            ("胸口", "chest"), ("手腕", "wrist"), ("腳踝", "ankle"),
        ]
        for name, slug in cats_data:
            if not WorkCategory.query.filter_by(slug=slug).first():
                db.session.add(WorkCategory(name=name, slug=slug))

        # 師傅
        if not Artist.query.filter_by(slug="roszie").first():
            artist = Artist(
                name="Roszie",
                slug="roszie",
                bio="工作室創辦人，擅長黑灰寫實與幾何線條。",
                is_active=True,
                sort_order=1,
            )
            db.session.add(artist)

        # 基本設定
        Setting.set("site_name", "ROSZIE INK", "網站名稱")
        Setting.set("site_tagline", "Make it permanent.", "標語")
        Setting.set("studio_address", "台北市大安區忠孝東路四段", "地址")
        Setting.set(
            "business_hours",
            {
                "tuesday": {"open": True, "from": "13:00", "to": "21:00"},
                "wednesday": {"open": True, "from": "13:00", "to": "21:00"},
                "thursday": {"open": True, "from": "13:00", "to": "21:00"},
                "friday": {"open": True, "from": "13:00", "to": "21:00"},
                "saturday": {"open": True, "from": "12:00", "to": "20:00"},
                "sunday": {"open": False},
                "monday": {"open": False},
            },
            "營業時間",
        )

        db.session.commit()
        print("✓ 假資料建立完成")


if __name__ == "__main__":
    seed()
