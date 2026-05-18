"""課程 model"""
import enum
from datetime import datetime, timezone

from app.extensions import db


class CourseStatus(enum.Enum):
    draft = "draft"
    open = "open"
    closed = "closed"
    completed = "completed"


class EnrollmentStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class Course(db.Model):
    """刺青課程"""

    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey("artists.id"))
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(350), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    content = db.Column(db.Text)  # Markdown（課程大綱）
    cover_image_url = db.Column(db.String(500))
    price = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(10), default="TWD")
    max_students = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    location = db.Column(db.String(300))
    status = db.Column(db.Enum(CourseStatus), default=CourseStatus.draft, nullable=False)
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(300))
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    instructor = db.relationship("Artist", back_populates="courses")
    enrollments = db.relationship(
        "CourseEnrollment", back_populates="course", cascade="all, delete-orphan", lazy="dynamic"
    )

    @property
    def current_students(self) -> int:
        return self.enrollments.filter_by(status=EnrollmentStatus.confirmed).count()

    @property
    def seats_remaining(self) -> int | None:
        if self.max_students is None:
            return None
        return max(0, self.max_students - self.current_students)

    @property
    def is_full(self) -> bool:
        if self.max_students is None:
            return False
        return self.current_students >= self.max_students

    def __repr__(self) -> str:
        return f"<Course {self.title}>"


class CourseEnrollment(db.Model):
    """課程報名"""

    __tablename__ = "course_enrollments"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_email = db.Column(db.String(120), nullable=False, index=True)
    student_phone = db.Column(db.String(30))
    notes = db.Column(db.Text)
    status = db.Column(
        db.Enum(EnrollmentStatus), default=EnrollmentStatus.pending, nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    course = db.relationship("Course", back_populates="enrollments")

    def __repr__(self) -> str:
        return f"<Enrollment {self.student_name} -> {self.course_id}>"
