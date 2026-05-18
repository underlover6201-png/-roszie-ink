"""Model 單元測試"""
import pytest

from app.models.user import User, UserRole
from app.models.booking import Booking, BookingStatus
from app.models.setting import Setting


class TestUserModel:
    def test_password_hashing(self, db):
        user = User(email="u@test.com", username="tester", role=UserRole.editor)
        user.set_password("securepass")
        db.session.add(user)
        db.session.commit()

        assert user.password_hash != "securepass"
        assert user.check_password("securepass")
        assert not user.check_password("wrongpass")

    def test_login_lockout(self, db):
        from flask import current_app

        user = User(email="lock@test.com", username="locktest", role=UserRole.editor)
        user.set_password("pass")
        db.session.add(user)
        db.session.commit()

        max_attempts = current_app.config["MAX_LOGIN_ATTEMPTS"]
        for _ in range(max_attempts):
            user.increment_login_attempts()

        assert user.is_locked()

    def test_reset_login_attempts(self, db):
        user = User(email="reset@test.com", username="resettest", role=UserRole.editor)
        user.set_password("pass")
        user.login_attempts = 3
        db.session.add(user)
        db.session.commit()

        user.reset_login_attempts()
        assert user.login_attempts == 0
        assert not user.is_locked()

    def test_is_admin(self, db):
        admin = User(email="a@test.com", username="admintest", role=UserRole.admin)
        editor = User(email="e@test.com", username="editortest", role=UserRole.editor)
        assert admin.is_admin()
        assert not editor.is_admin()


class TestBookingModel:
    def test_booking_number_generated(self, db):
        booking = Booking(
            client_name="Test User",
            client_email="client@test.com",
        )
        db.session.add(booking)
        db.session.commit()

        assert booking.booking_number is not None
        assert booking.booking_number.startswith("RI")

    def test_status_label(self, db):
        booking = Booking(
            client_name="Label Test",
            client_email="label@test.com",
            status=BookingStatus.pending,
        )
        assert booking.status_label == "待處理"


class TestSettingModel:
    def test_set_and_get_string(self, db):
        Setting.set("test_key", "hello", "測試")
        val = Setting.get("test_key")
        assert val == "hello"

    def test_set_and_get_dict(self, db):
        data = {"hours": "13:00-21:00", "open": True}
        Setting.set("test_dict", data)
        result = Setting.get("test_dict")
        assert result["open"] is True

    def test_get_default(self, db):
        val = Setting.get("nonexistent_key", "default_val")
        assert val == "default_val"
