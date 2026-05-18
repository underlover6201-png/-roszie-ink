"""部落格文章 model"""
import enum
from datetime import datetime, timezone

from app.extensions import db


class PostStatus(enum.Enum):
    draft = "draft"
    published = "published"
    scheduled = "scheduled"


class PostCategory(db.Model):
    """文章分類"""

    __tablename__ = "post_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), nullable=False, unique=True)
    sort_order = db.Column(db.Integer, default=0)

    posts = db.relationship("Post", back_populates="category", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<PostCategory {self.name}>"


class Post(db.Model):
    """Magazine 文章"""

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("post_categories.id"))
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(350), nullable=False, unique=True, index=True)
    excerpt = db.Column(db.Text)
    content = db.Column(db.Text)  # Markdown
    cover_image_url = db.Column(db.String(500))
    cover_thumb_url = db.Column(db.String(500))
    status = db.Column(db.Enum(PostStatus), default=PostStatus.draft, nullable=False, index=True)
    published_at = db.Column(db.DateTime(timezone=True))
    scheduled_at = db.Column(db.DateTime(timezone=True))
    view_count = db.Column(db.Integer, default=0, nullable=False)
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(300))
    og_image_url = db.Column(db.String(500))
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    author = db.relationship("User", back_populates="posts")
    category = db.relationship("PostCategory", back_populates="posts")

    def increment_view(self) -> None:
        self.view_count += 1

    def publish(self) -> None:
        self.status = PostStatus.published
        if not self.published_at:
            self.published_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<Post {self.slug}>"
