"""作品集 model"""
import enum
from datetime import datetime, timezone

from app.extensions import db


class WorkSize(enum.Enum):
    small = "small"
    medium = "medium"
    large = "large"
    extra_large = "extra_large"


class WorkCategory(db.Model):
    """作品分類（e.g. 臂部、背部、胸口）"""

    __tablename__ = "work_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), nullable=False, unique=True)
    sort_order = db.Column(db.Integer, default=0)

    works = db.relationship("Work", back_populates="category", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<WorkCategory {self.name}>"


class Work(db.Model):
    """單一刺青作品"""

    __tablename__ = "works"

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("work_categories.id"), index=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500), nullable=False)
    thumb_url = db.Column(db.String(500))
    webp_url = db.Column(db.String(500))
    body_part = db.Column(db.String(100))
    size = db.Column(db.Enum(WorkSize))
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    artist = db.relationship("Artist", back_populates="works")
    category = db.relationship("WorkCategory", back_populates="works")

    def __repr__(self) -> str:
        return f"<Work {self.id} by {self.artist_id}>"
