"""後台 — 課程管理"""
import re
from datetime import date

from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.blueprints.admin import admin_bp
from app.extensions import db
from app.models.artist import Artist
from app.models.course import Course, CourseStatus
from app.utils.decorators import editor_required


def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug


def _parse_date(val: str):
    try:
        return date.fromisoformat(val) if val else None
    except ValueError:
        return None


@admin_bp.route("/courses")
@login_required
@editor_required
def admin_courses():
    all_courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template("admin/courses/list.html", courses=all_courses, CourseStatus=CourseStatus)


@admin_bp.route("/courses/new", methods=["GET", "POST"])
@login_required
@editor_required
def course_create():
    all_artists = Artist.query.filter_by(is_active=True).order_by(Artist.name).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("課程標題為必填。", "error")
            return render_template("admin/courses/form.html", course=None, all_artists=all_artists, CourseStatus=CourseStatus)

        slug = request.form.get("slug", "").strip() or _slugify(title)
        if Course.query.filter_by(slug=slug).first():
            slug = slug + "-" + str(Course.query.count() + 1)

        status_val = request.form.get("status", "draft")
        status = CourseStatus[status_val] if status_val in CourseStatus.__members__ else CourseStatus.draft

        price_str = request.form.get("price", "").strip()
        price = float(price_str) if price_str else None

        course = Course(
            instructor_id=request.form.get("instructor_id", type=int) or None,
            title=title,
            slug=slug,
            description=request.form.get("description", "").strip() or None,
            content=request.form.get("content", "").strip() or None,
            cover_image_url=request.form.get("cover_image_url", "").strip() or None,
            price=price,
            currency=request.form.get("currency", "TWD").strip() or "TWD",
            max_students=request.form.get("max_students", type=int) or None,
            start_date=_parse_date(request.form.get("start_date", "")),
            end_date=_parse_date(request.form.get("end_date", "")),
            location=request.form.get("location", "").strip() or None,
            status=status,
        )
        db.session.add(course)
        db.session.commit()
        flash(f"課程「{title}」已建立。", "success")
        return redirect(url_for("admin.admin_courses"))

    return render_template("admin/courses/form.html", course=None, all_artists=all_artists, CourseStatus=CourseStatus)


@admin_bp.route("/courses/<int:course_id>/edit", methods=["GET", "POST"])
@login_required
@editor_required
def course_edit(course_id: int):
    course = Course.query.get_or_404(course_id)
    all_artists = Artist.query.filter_by(is_active=True).order_by(Artist.name).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("課程標題為必填。", "error")
            return render_template("admin/courses/form.html", course=course, all_artists=all_artists, CourseStatus=CourseStatus)

        status_val = request.form.get("status", "draft")
        price_str = request.form.get("price", "").strip()

        course.instructor_id = request.form.get("instructor_id", type=int) or None
        course.title = title
        course.slug = request.form.get("slug", "").strip() or course.slug
        course.description = request.form.get("description", "").strip() or None
        course.content = request.form.get("content", "").strip() or None
        course.cover_image_url = request.form.get("cover_image_url", "").strip() or None
        course.price = float(price_str) if price_str else None
        course.currency = request.form.get("currency", "TWD").strip() or "TWD"
        course.max_students = request.form.get("max_students", type=int) or None
        course.start_date = _parse_date(request.form.get("start_date", ""))
        course.end_date = _parse_date(request.form.get("end_date", ""))
        course.location = request.form.get("location", "").strip() or None
        course.status = CourseStatus[status_val] if status_val in CourseStatus.__members__ else CourseStatus.draft
        db.session.commit()
        flash(f"課程「{title}」已更新。", "success")
        return redirect(url_for("admin.admin_courses"))

    return render_template("admin/courses/form.html", course=course, all_artists=all_artists, CourseStatus=CourseStatus)


@admin_bp.route("/courses/<int:course_id>/delete", methods=["POST"])
@login_required
@editor_required
def course_delete(course_id: int):
    course = Course.query.get_or_404(course_id)
    title = course.title
    db.session.delete(course)
    db.session.commit()
    flash(f"課程「{title}」已刪除。", "success")
    return redirect(url_for("admin.admin_courses"))
