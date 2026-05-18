"""郵件發送服務"""
from flask import current_app, render_template
from flask_mail import Message

from app.extensions import mail


def send_booking_admin_notification(booking) -> None:
    """通知管理員有新預約"""
    admin_email = current_app.config.get("ADMIN_EMAIL")
    if not admin_email:
        return

    msg = Message(
        subject=f"【ROSZIE INK】新預約諮詢 #{booking.booking_number}",
        recipients=[admin_email],
        html=render_template("emails/booking_admin.html", booking=booking),
        body=render_template("emails/booking_admin.txt", booking=booking),
    )
    _send(msg)


def send_booking_client_confirmation(booking) -> None:
    """寄確認信給客人"""
    msg = Message(
        subject=f"【ROSZIE INK】預約諮詢確認 #{booking.booking_number}",
        recipients=[booking.client_email],
        html=render_template("emails/booking_client.html", booking=booking),
        body=render_template("emails/booking_client.txt", booking=booking),
    )
    _send(msg)


def send_newsletter_confirmation(subscriber) -> None:
    """訂閱電子報確認信"""
    from flask import url_for

    confirm_url = url_for(
        "public.confirm_newsletter",
        token=subscriber.confirmation_token,
        _external=True,
    )
    msg = Message(
        subject="【ROSZIE INK】確認您的電子報訂閱",
        recipients=[subscriber.email],
        html=render_template(
            "emails/newsletter_confirm.html",
            confirm_url=confirm_url,
        ),
    )
    _send(msg)


def _send(msg: Message) -> None:
    """實際發送，失敗只記 log 不讓整個請求爆掉"""
    try:
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"郵件發送失敗: {e}")
