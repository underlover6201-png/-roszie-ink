"""認領圖（Flash Design）model — 每個設計只賣給一個人"""
from datetime import datetime, timezone

from app.extensions import db

# Flash Design ↔ Style 多對多
flash_styles = db.Table(
    "flash_styles",
    db.Column("flash_id",  db.Integer, db.ForeignKey("flash_designs.id"), primary_key=True),
    db.Column("style_id",  db.Integer, db.ForeignKey("styles.id"),        primary_key=True),
)


class FlashDesign(db.Model):
    """認領圖 / Flash Design — 限量一份，買斷制"""

    __tablename__ = "flash_designs"

    id           = db.Column(db.Integer, primary_key=True)
    artist_id    = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=False, index=True)
    title        = db.Column(db.String(200), nullable=False)
    slug         = db.Column(db.String(250), nullable=False, unique=True, index=True)
    description  = db.Column(db.Text)
    image_url    = db.Column(db.String(500), nullable=False)
    thumb_url    = db.Column(db.String(500))
    price        = db.Column(db.Numeric(10, 2), nullable=False)
    currency     = db.Column(db.String(10), default="TWD", nullable=False)
    placement    = db.Column(db.String(100))          # 建議刺青部位
    size_note    = db.Column(db.String(100))          # 尺寸說明（例：約 8×8 cm）
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    is_claimed   = db.Column(db.Boolean, default=False, nullable=False, index=True)
    claimed_at   = db.Column(db.DateTime(timezone=True))
    sort_order   = db.Column(db.Integer, default=0)
    created_at   = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at   = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    artist = db.relationship("Artist", backref=db.backref("flash_designs", lazy="dynamic"))
    styles = db.relationship("Style", secondary=flash_styles, lazy="subquery",
                             backref=db.backref("flash_designs", lazy="dynamic"))

    def claim(self) -> None:
        self.is_claimed = True
        self.claimed_at = datetime.now(timezone.utc)

    @property
    def status_label(self) -> str:
        return "已認領" if self.is_claimed else "可認領"

    def __repr__(self) -> str:
        return f"<FlashDesign {self.slug}>"
