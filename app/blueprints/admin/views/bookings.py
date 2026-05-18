"""後台 — 預約管理"""
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.blueprints.admin import admin_bp
from app.extensions import db
from app.models.booking import Booking, BookingStatus
from app.utils.decorators import editor_required


@admin_bp.route("/bookings")
@login_required
@editor_required
def bookings():
    status_filter = request.args.get("status")
    page = request.args.get("page", 1, type=int)

    query = Booking.query.order_by(Booking.created_at.desc())
    if status_filter and status_filter in BookingStatus.__members__:
        query = query.filter_by(status=BookingStatus[status_filter])

    pagination = query.paginate(page=page, per_page=20, error_out=False)
    pending_count = Booking.query.filter_by(status=BookingStatus.pending).count()

    return render_template(
        "admin/bookings/list.html",
        bookings=pagination,
        status_filter=status_filter,
        pending_count=pending_count,
        BookingStatus=BookingStatus,
    )


@admin_bp.route("/bookings/<int:booking_id>", methods=["GET", "POST"])
@login_required
@editor_required
def booking_detail(booking_id: int):
    booking = Booking.query.get_or_404(booking_id)

    if request.method == "POST":
        new_status = request.form.get("status")
        admin_notes = request.form.get("admin_notes", "").strip()

        if new_status and new_status in BookingStatus.__members__:
            booking.status = BookingStatus[new_status]
        booking.admin_notes = admin_notes or None
        db.session.commit()
        flash("預約狀態已更新。", "success")
        return redirect(url_for("admin.booking_detail", booking_id=booking_id))

    return render_template("admin/bookings/detail.html", booking=booking, BookingStatus=BookingStatus)


@admin_bp.route("/bookings/<int:booking_id>/delete", methods=["POST"])
@login_required
@editor_required
def booking_delete(booking_id: int):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash("預約紀錄已刪除。", "success")
    return redirect(url_for("admin.bookings"))
