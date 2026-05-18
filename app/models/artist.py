"""刺青師傅 model"""
from datetime import datetime, timezone

from app.extensions import db

# 師傅 ↔ 風格 多對多關聯表
artist_styles = db.Table(
    "artist_styles",
    db.Column("artist_id", db.Integer, db.ForeignKey("artists.id"), primary_key=True),
    db.Column("style_id", db.Integer, db.ForeignKey("styles.id"), primary_key=True),
)


class Style(db.Model):
    """刺青風格標籤（e.g. 傳統、黑灰、幾何、水彩）"""

    __tablename__ = "styles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"<Style {self.name}>"


class Artist(db.Model):
    """刺青師傅"""

    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), nullable=False, unique=True, index=True)
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(500))
    avatar_thumb_url = db.Column(db.String(500))
    instagram_url = db.Column(db.String(300))
    facebook_url = db.Column(db.String(300))
    tiktok_url = db.Column(db.String(300))
    website_url = db.Column(db.String(300))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    styles = db.relationship("Style", secondary=artist_styles, backref="artists", lazy="subquery")
    works = db.relationship("Work", back_populates="artist", lazy="dynamic", cascade="all, delete-orphan")
    bookings = db.relationship("Booking", back_populates="artist", lazy="dynamic")
    courses = db.relationship("Course", back_populates="instructor", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Artist {self.name}>"
