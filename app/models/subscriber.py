"""電子報訂閱者 model"""
import secrets
from datetime import datetime, timezone

from app.extensions import db


class Subscriber(db.Model):
    """電子報訂閱者"""

    __tablename__ = "subscribers"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    confirmation_token = db.Column(db.String(100), unique=True)
    confirmed_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def generate_token(self) -> str:
        self.confirmation_token = secrets.token_urlsafe(32)
        return self.confirmation_token

    def confirm(self) -> None:
        self.is_confirmed = True
        self.confirmed_at = datetime.now(timezone.utc)
        self.confirmation_token = None

    def __repr__(self) -> str:
        return f"<Subscriber {self.email}>"
