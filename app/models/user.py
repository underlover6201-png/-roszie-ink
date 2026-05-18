"""管理員帳號 model"""
import enum
from datetime import datetime, timedelta, timezone

from flask_login import UserMixin

from app.extensions import bcrypt, db


class UserRole(enum.Enum):
    admin = "admin"
    editor = "editor"


class User(UserMixin, db.Model):
    """後台管理員"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.editor)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime(timezone=True))
    login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    posts = db.relationship("Post", back_populates="author", lazy="dynamic")
    audit_logs = db.relationship("AuditLog", back_populates="user", lazy="dynamic")

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_locked(self) -> bool:
        if self.locked_until and self.locked_until > datetime.now(timezone.utc):
            return True
        return False

    def increment_login_attempts(self) -> None:
        from flask import current_app

        self.login_attempts += 1
        if self.login_attempts >= current_app.config["MAX_LOGIN_ATTEMPTS"]:
            lockout = current_app.config["LOGIN_LOCKOUT_MINUTES"]
            self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=lockout)

    def reset_login_attempts(self) -> None:
        self.login_attempts = 0
        self.locked_until = None

    def is_admin(self) -> bool:
        return self.role == UserRole.admin

    def __repr__(self) -> str:
        return f"<User {self.username}>"
