"""後台 — 作品管理"""
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.blueprints.admin import admin_bp
from app.extensions import db
from app.models.artist import Artist
from app.models.work import Work, WorkCategory, WorkSize
from app.utils.decorators import editor_required


@admin_bp.route("/works")
@login_required
@editor_required
def works():
    artist_filter = request.args.get("artist_id", type=int)
    page = request.args.get("page", 1, type=int)

    query = Work.query.order_by(Work.created_at.desc())
    if artist_filter:
        query = query.filter_by(artist_id=artist_filter)

    pagination = query.paginate(page=page, per_page=24, error_out=False)
    all_artists = Artist.query.filter_by(is_active=True).order_by(Artist.name).all()

    return render_template(
        "admin/works/list.html",
        works=pagination,
        all_artists=all_artists,
        artist_filter=artist_filter,
    )


@admin_bp.route("/works/new", methods=["GET", "POST"])
@login_required
@editor_required
def work_create():
    all_artists = Artist.query.filter_by(is_active=True).order_by(Artist.name).all()
    all_categories = WorkCategory.query.order_by(WorkCategory.sort_order).all()

    if request.method == "POST":
        artist_id = request.form.get("artist_id", type=int)
        image_url = request.form.get("image_url", "").strip()
        if not artist_id or not image_url:
            flash("師傅與圖片 URL 為必填。", "error")
            return render_template("admin/works/form.html", work=None, all_artists=all_artists, all_categories=all_categories, WorkSize=WorkSize)

        size_val = request.form.get("size")
        size = WorkSize[size_val] if size_val and size_val in WorkSize.__members__ else None

        work = Work(
            artist_id=artist_id,
            category_id=request.form.get("category_id", type=int) or None,
            title=request.form.get("title", "").strip() or None,
            description=request.form.get("description", "").strip() or None,
            image_url=image_url,
            thumb_url=request.form.get("thumb_url", "").strip() or None,
            body_part=request.form.get("body_part", "").strip() or None,
            size=size,
            is_featured=request.form.get("is_featured") == "1",
            is_published=request.form.get("is_published") == "1",
            sort_order=int(request.form.get("sort_order", 0)),
        )
        db.session.add(work)
        db.session.commit()
        flash("作品已新增。", "success")
        return redirect(url_for("admin.works"))

    return render_template("admin/works/form.html", work=None, all_artists=all_artists, all_categories=all_categories, WorkSize=WorkSize)


@admin_bp.route("/works/<int:work_id>/edit", methods=["GET", "POST"])
@login_required
@editor_required
def work_edit(work_id: int):
    work = Work.query.get_or_404(work_id)
    all_artists = Artist.query.filter_by(is_active=True).order_by(Artist.name).all()
    all_categories = WorkCategory.query.order_by(WorkCategory.sort_order).all()

    if request.method == "POST":
        artist_id = request.form.get("artist_id", type=int)
        image_url = request.form.get("image_url", "").strip()
        if not artist_id or not image_url:
            flash("師傅與圖片 URL 為必填。", "error")
            return render_template("admin/works/form.html", work=work, all_artists=all_artists, all_categories=all_categories, WorkSize=WorkSize)

        size_val = request.form.get("size")
        work.artist_id = artist_id
        work.category_id = request.form.get("category_id", type=int) or None
        work.title = request.form.get("title", "").strip() or None
        work.description = request.form.get("description", "").strip() or None
        work.image_url = image_url
        work.thumb_url = request.form.get("thumb_url", "").strip() or None
        work.body_part = request.form.get("body_part", "").strip() or None
        work.size = WorkSize[size_val] if size_val and size_val in WorkSize.__members__ else None
        work.is_featured = request.form.get("is_featured") == "1"
        work.is_published = request.form.get("is_published") == "1"
        work.sort_order = int(request.form.get("sort_order", 0))
        db.session.commit()
        flash("作品已更新。", "success")
        return redirect(url_for("admin.works"))

    return render_template("admin/works/form.html", work=work, all_artists=all_artists, all_categories=all_categories, WorkSize=WorkSize)


@admin_bp.route("/works/<int:work_id>/delete", methods=["POST"])
@login_required
@editor_required
def work_delete(work_id: int):
    work = Work.query.get_or_404(work_id)
    db.session.delete(work)
    db.session.commit()
    flash("作品已刪除。", "success")
    return redirect(url_for("admin.works"))
