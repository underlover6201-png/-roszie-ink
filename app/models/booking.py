"""預約諮詢 model"""
import enum
import uuid
from datetime import datetime, timezone

from app.extensions import db


class BookingStatus(enum.Enum):
    pending = "pending"
    contacted = "contacted"
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"


class BookingSize(enum.Enum):
    small = "small"
    medium = "medium"
    large = "large"
    extra_large = "extra_large"


class ColorPreference(enum.Enum):
    black_gray = "black_gray"
    color = "color"
    both = "both"


def _generate_booking_number() -> str:
    """產生格式 RI2026-00001 的預約編號"""
    from datetime import datetime

    year = datetime.now().year
    unique = uuid.uuid4().hex[:5].upper()
    return f"RI{year}-{unique}"


class Booking(db.Model):
    """客人預約諮詢"""

    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(
        db.String(20), unique=True, nullable=False, default=_generate_booking_number, index=True
    )
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), index=True)

    # 客人資料
    client_name = db.Column(db.String(100), nullable=False)
    client_email = db.Column(db.String(120), nullable=False, index=True)
    client_phone = db.Column(db.String(30))
    client_instagram = db.Column(db.String(100))

    # 刺青資訊
    placement = db.Column(db.String(100))
    size = db.Column(db.Enum(BookingSize))
    style = db.Column(db.String(100))
    color_preference = db.Column(db.Enum(ColorPreference))
    budget_range = db.Column(db.String(50))
    preferred_date_start = db.Column(db.Date)
    preferred_date_end = db.Column(db.Date)
    notes = db.Column(db.Text)

    # 管理
    status = db.Column(
        db.Enum(BookingStatus), default=BookingStatus.pending, nullable=False, index=True
    )
    admin_notes = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    artist = db.relationship("Artist", back_populates="bookings")
    images = db.relationship(
        "BookingImage", back_populates="booking", cascade="all, delete-orphan", lazy="subquery"
    )

    @property
    def status_label(self) -> str:
        labels = {
            BookingStatus.pending: "待處理",
            BookingStatus.contacted: "已聯絡",
            BookingStatus.scheduled: "已排程",
            BookingStatus.completed: "已完成",
            BookingStatus.cancelled: "已取消",
        }
        return labels.get(self.status, self.status.value)

    def __repr__(self) -> str:
        return f"<Booking {self.booking_number}>"


class BookingImage(db.Model):
    """預約參考圖片"""

    __tablename__ = "booking_images"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(
        db.Integer, db.ForeignKey("bookings.id"), nullable=False, index=True
    )
    image_url = db.Column(db.String(500), nullable=False)
    thumb_url = db.Column(db.String(500))
    original_filename = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    booking = db.relationship("Booking", back_populates="images")

    def __repr__(self) -> str:
        return f"<BookingImage {self.id} for booking {self.booking_id}>"
