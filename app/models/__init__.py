"""匯出所有 model，讓 Flask-Migrate 能偵測到所有資料表"""
from app.models.artist import Artist, Style, artist_styles  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.booking import Booking, BookingImage  # noqa: F401
from app.models.course import Course, CourseEnrollment  # noqa: F401
from app.models.post import Post, PostCategory  # noqa: F401
from app.models.setting import Setting  # noqa: F401
from app.models.subscriber import Subscriber  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.work import Work, WorkCategory  # noqa: F401
from app.models.flash import FlashDesign, flash_styles  # noqa: F401
from app.models.payment import Payment  # noqa: F401
