"""網站設定 model（key-value 儲存）"""
import json
from datetime import datetime, timezone

from app.extensions import db


class Setting(db.Model):
    """網站設定（key-value，value 以 JSON 格式儲存複雜值）"""

    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    description = db.Column(db.String(300))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    def get_value(self):
        """自動從 JSON 解析回 Python 物件"""
        if self.value is None:
            return None
        try:
            return json.loads(self.value)
        except (json.JSONDecodeError, TypeError):
            return self.value

    def set_value(self, val) -> None:
        """自動將 Python 物件序列化為 JSON"""
        if isinstance(val, str):
            self.value = val
        else:
            self.value = json.dumps(val, ensure_ascii=False)

    @classmethod
    def get(cls, key: str, default=None):
        """快速讀取設定值"""
        setting = cls.query.filter_by(key=key).first()
        if setting is None:
            return default
        return setting.get_value()

    @classmethod
    def set(cls, key: str, value, description: str = "") -> "Setting":
        """快速寫入設定值"""
        setting = cls.query.filter_by(key=key).first()
        if setting is None:
            setting = cls(key=key, description=description)
            db.session.add(setting)
        setting.set_value(value)
        db.session.commit()
        return setting

    def __repr__(self) -> str:
        return f"<Setting {self.key}>"
