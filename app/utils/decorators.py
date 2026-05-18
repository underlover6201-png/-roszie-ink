"""自訂裝飾器"""
from functools import wraps

from flask import abort
from flask_login import current_user


def admin_required(f):
    """只有 role=admin 才能訪問"""

    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)

    return decorated


def editor_required(f):
    """admin 和 editor 都能訪問"""

    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)
        return f(*args, **kwargs)

    return decorated


def audit_action(action: str, resource_type: str):
    """自動記錄操作到 audit_log"""

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            result = f(*args, **kwargs)
            try:
                from app.extensions import db
                from app.models.audit_log import AuditLog

                AuditLog.log(
                    action=action,
                    resource_type=resource_type,
                    user_id=current_user.id if current_user.is_authenticated else None,
                )
                db.session.commit()
            except Exception:
                pass
            return result

        return decorated

    return decorator
