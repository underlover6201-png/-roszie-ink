"""後台 Dashboard"""
from flask import render_template
from flask_login import login_required

from app.blueprints.admin import admin_bp
from app.utils.decorators import editor_required


@admin_bp.route("/")
@admin_bp.route("/dashboard")
@login_required
@editor_required
def dashboard():
    from app.models.booking import Booking, BookingStatus
    from app.models.artist import Artist
    from app.models.post import Post

    pending_count = Booking.query.filter_by(status=BookingStatus.pending).count()
    total_bookings = Booking.query.count()
    artists_count = Artist.query.filter_by(is_active=True).count()
    posts_count = Post.query.count()

    recent_bookings = (
        Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    )

    return render_template(
        "admin/dashboard.html",
        pending_count=pending_count,
        total_bookings=total_bookings,
        artists_count=artists_count,
        posts_count=posts_count,
        recent_bookings=recent_bookings,
    )
