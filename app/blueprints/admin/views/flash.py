"""後台 — 認領圖管理"""
import re

from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.blueprints.admin import admin_bp
from app.extensions import db
from app.models.artist import Artist, Style
from app.models.flash import FlashDesign
from app.utils.decorators import editor_required


def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug


@admin_bp.route("/flash")
@login_required
@editor_required
def flash_designs():
    claimed_filter = request.args.get("claimed")
    page = request.args.get("page", 1, type=int)

    query = FlashDesign.query.order_by(FlashDesign.is_claimed, FlashDesign.sort_order, FlashDesign.created_at.desc())
    if claimed_filter == "yes":
        query = query.filter_by(is_claimed=True)
    elif claimed_filter == "no":
        query = query.filter_by(is_claimed=False)

    pagination = query.paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/flash/list.html", designs=pagination, claimed_filter=claimed_filter)


@admin_bp.route("/flash/new", methods=["GET", "POST"])
@login_required
@editor_required
def flash_create():
    all_artists = Artist.query.filter_by(is_active=True).order_by(Artist.name).all()
    all_styles = Style.query.order_by(Style.name).all()

    if request.method == "POST":
        artist_id = request.form.get("artist_id", type=int)
        title = request.form.get("title", "").strip()
        image_url = request.form.get("image_url", "").strip()

        if not artist_id or not title or not image_url:
            flash("師傅、標題、圖片 URL 為必填。", "error")
            return render_template("admin/flash/form.html", design=None, all_artists=all_artists, all_styles=all_styles)

        price_str = request.form.get("price", "").strip()
        if not price_str:
            flash("售價為必填。", "error")
            return render_template("admin/flash/form.html", design=None, all_artists=all_artists, all_styles=all_styles)

        slug = request.form.get("slug", "").strip() or _slugify(title)
        if FlashDesign.query.filter_by(slug=slug).first():
            slug = slug + "-" + str(FlashDesign.query.count() + 1)

        selected_style_ids = request.form.getlist("style_ids", type=int)
        styles = Style.query.filter(Style.id.in_(selected_style_ids)).all()

        design = FlashDesign(
            artist_id=artist_id,
            title=title,
            slug=slug,
            description=request.form.get("description", "").strip() or None,
            image_url=image_url,
            thumb_url=request.form.get("thumb_url", "").strip() or None,
            price=float(price_str),
            currency=request.form.get("currency", "TWD").strip() or "TWD",
            placement=request.form.get("placement", "").strip() or None,
            size_note=request.form.get("size_note", "").strip() or None,
            is_published=request.form.get("is_published") == "1",
            is_claimed=False,
            sort_order=int(request.form.get("sort_order", 0)),
            styles=styles,
        )
        db.session.add(design)
        db.session.commit()
        flash(f"認領圖「{title}」已建立。", "success")
        return redirect(url_for("admin.flash_designs"))

    return render_template("admin/flash/form.html", design=None, all_artists=all_artists, all_styles=all_styles)


@admin_bp.route("/flash/<int:design_id>/edit", methods=["GET", "POST"])
@login_required
@editor_required
def flash_edit(design_id: int):
    design = FlashDesign.query.get_or_404(design_id)
    all_artists = Artist.query.filter_by(is_active=True).order_by(Artist.name).all()
    all_styles = Style.query.order_by(Style.name).all()

    if request.method == "POST":
        artist_id = request.form.get("artist_id", type=int)
        title = request.form.get("title", "").strip()
        image_url = request.form.get("image_url", "").strip()
        price_str = request.form.get("price", "").strip()

        if not artist_id or not title or not image_url or not price_str:
            flash("師傅、標題、圖片 URL、售價為必填。", "error")
            return render_template("admin/flash/form.html", design=design, all_artists=all_artists, all_styles=all_styles)

        selected_style_ids = request.form.getlist("style_ids", type=int)
        design.styles = Style.query.filter(Style.id.in_(selected_style_ids)).all()

        design.artist_id = artist_id
        design.title = title
        design.slug = request.form.get("slug", "").strip() or design.slug
        design.description = request.form.get("description", "").strip() or None
        design.image_url = image_url
        design.thumb_url = request.form.get("thumb_url", "").strip() or None
        design.price = float(price_str)
        design.currency = request.form.get("currency", "TWD").strip() or "TWD"
        design.placement = request.form.get("placement", "").strip() or None
        design.size_note = request.form.get("size_note", "").strip() or None
        design.is_published = request.form.get("is_published") == "1"
        design.is_claimed = request.form.get("is_claimed") == "1"
        design.sort_order = int(request.form.get("sort_order", 0))
        db.session.commit()
        flash(f"認領圖「{title}」已更新。", "success")
        return redirect(url_for("admin.flash_designs"))

    return render_template("admin/flash/form.html", design=design, all_artists=all_artists, all_styles=all_styles)


@admin_bp.route("/flash/<int:design_id>/delete", methods=["POST"])
@login_required
@editor_required
def flash_delete(design_id: int):
    design = FlashDesign.query.get_or_404(design_id)
    title = design.title
    db.session.delete(design)
    db.session.commit()
    flash(f"認領圖「{title}」已刪除。", "success")
    return redirect(url_for("admin.flash_designs"))
