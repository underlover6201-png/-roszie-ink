"""操作稽核日誌 model"""
import json
from datetime import datetime, timezone

from app.extensions import db


class AuditLog(db.Model):
    """記錄管理員的所有操作（新增/修改/刪除）"""

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    action = db.Column(db.String(100), nullable=False)  # create / update / delete
    resource_type = db.Column(db.String(100), nullable=False)  # booking / artist / post...
    resource_id = db.Column(db.Integer)
    old_values = db.Column(db.Text)  # JSON
    new_values = db.Column(db.Text)  # JSON
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    user = db.relationship("User", back_populates="audit_logs")

    def set_old_values(self, data: dict) -> None:
        self.old_values = json.dumps(data, ensure_ascii=False, default=str)

    def set_new_values(self, data: dict) -> None:
        self.new_values = json.dumps(data, ensure_ascii=False, default=str)

    @classmethod
    def log(
        cls,
        action: str,
        resource_type: str,
        resource_id: int | None = None,
        old_values: dict | None = None,
        new_values: dict | None = None,
        user_id: int | None = None,
    ) -> "AuditLog":
        from flask import request

        entry = cls(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=request.remote_addr if request else None,
            user_agent=request.user_agent.string if request else None,
        )
        if old_values:
            entry.set_old_values(old_values)
        if new_values:
            entry.set_new_values(new_values)

        db.session.add(entry)
        return entry

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} {self.resource_type}:{self.resource_id}>"
