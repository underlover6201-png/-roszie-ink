"""後台 — 師傅管理"""
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.blueprints.admin import admin_bp
from app.extensions import db
from app.models.artist import Artist, Style
from app.utils.decorators import editor_required


def _slugify(text: str) -> str:
    import re
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug


@admin_bp.route("/artists")
@login_required
@editor_required
def artists():
    all_artists = Artist.query.order_by(Artist.sort_order, Artist.name).all()
    return render_template("admin/artists/list.html", artists=all_artists)


@admin_bp.route("/artists/new", methods=["GET", "POST"])
@login_required
@editor_required
def artist_create():
    all_styles = Style.query.order_by(Style.name).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("師傅姓名為必填。", "error")
            return render_template("admin/artists/form.html", artist=None, all_styles=all_styles)

        slug = request.form.get("slug", "").strip() or _slugify(name)
        if Artist.query.filter_by(slug=slug).first():
            slug = slug + "-" + str(Artist.query.count() + 1)

        selected_style_ids = request.form.getlist("style_ids", type=int)
        styles = Style.query.filter(Style.id.in_(selected_style_ids)).all()

        artist = Artist(
            name=name,
            slug=slug,
            bio=request.form.get("bio", "").strip() or None,
            avatar_url=request.form.get("avatar_url", "").strip() or None,
            avatar_thumb_url=request.form.get("avatar_thumb_url", "").strip() or None,
            instagram_url=request.form.get("instagram_url", "").strip() or None,
            facebook_url=request.form.get("facebook_url", "").strip() or None,
            tiktok_url=request.form.get("tiktok_url", "").strip() or None,
            website_url=request.form.get("website_url", "").strip() or None,
            is_active=request.form.get("is_active") == "1",
            sort_order=int(request.form.get("sort_order", 0)),
            styles=styles,
        )
        db.session.add(artist)
        db.session.commit()
        flash(f"師傅「{name}」已建立。", "success")
        return redirect(url_for("admin.artists"))

    return render_template("admin/artists/form.html", artist=None, all_styles=all_styles)


@admin_bp.route("/artists/<int:artist_id>/edit", methods=["GET", "POST"])
@login_required
@editor_required
def artist_edit(artist_id: int):
    artist = Artist.query.get_or_404(artist_id)
    all_styles = Style.query.order_by(Style.name).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("師傅姓名為必填。", "error")
            return render_template("admin/artists/form.html", artist=artist, all_styles=all_styles)

        artist.name = name
        artist.slug = request.form.get("slug", "").strip() or _slugify(name)
        artist.bio = request.form.get("bio", "").strip() or None
        artist.avatar_url = request.form.get("avatar_url", "").strip() or None
        artist.avatar_thumb_url = request.form.get("avatar_thumb_url", "").strip() or None
        artist.instagram_url = request.form.get("instagram_url", "").strip() or None
        artist.facebook_url = request.form.get("facebook_url", "").strip() or None
        artist.tiktok_url = request.form.get("tiktok_url", "").strip() or None
        artist.website_url = request.form.get("website_url", "").strip() or None
        artist.is_active = request.form.get("is_active") == "1"
        artist.sort_order = int(request.form.get("sort_order", 0))

        selected_style_ids = request.form.getlist("style_ids", type=int)
        artist.styles = Style.query.filter(Style.id.in_(selected_style_ids)).all()

        db.session.commit()
        flash(f"師傅「{name}」已更新。", "success")
        return redirect(url_for("admin.artists"))

    return render_template("admin/artists/form.html", artist=artist, all_styles=all_styles)


@admin_bp.route("/artists/<int:artist_id>/delete", methods=["POST"])
@login_required
@editor_required
def artist_delete(artist_id: int):
    artist = Artist.query.get_or_404(artist_id)
    name = artist.name
    db.session.delete(artist)
    db.session.commit()
    flash(f"師傅「{name}」已刪除。", "success")
    return redirect(url_for("admin.artists"))


@admin_bp.route("/styles", methods=["GET", "POST"])
@login_required
@editor_required
def styles():
    """風格標籤管理"""
    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            name = request.form.get("name", "").strip()
            if name:
                slug = _slugify(name)
                if not Style.query.filter_by(slug=slug).first():
                    db.session.add(Style(name=name, slug=slug))
                    db.session.commit()
                    flash(f"風格「{name}」已新增。", "success")
        elif action == "delete":
            style_id = request.form.get("style_id", type=int)
            style = Style.query.get(style_id)
            if style:
                db.session.delete(style)
                db.session.commit()
                flash("風格已刪除。", "success")
        return redirect(url_for("admin.styles"))

    all_styles = Style.query.order_by(Style.name).all()
    return render_template("admin/artists/styles.html", styles=all_styles)
