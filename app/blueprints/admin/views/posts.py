"""後台 — 文章管理"""
import re
from datetime import datetime, timezone

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.blueprints.admin import admin_bp
from app.extensions import db
from app.models.post import Post, PostCategory, PostStatus
from app.utils.decorators import editor_required


def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug


@admin_bp.route("/posts")
@login_required
@editor_required
def posts():
    status_filter = request.args.get("status")
    page = request.args.get("page", 1, type=int)

    query = Post.query.order_by(Post.created_at.desc())
    if status_filter and status_filter in PostStatus.__members__:
        query = query.filter_by(status=PostStatus[status_filter])

    pagination = query.paginate(page=page, per_page=20, error_out=False)
    return render_template(
        "admin/posts/list.html",
        posts=pagination,
        status_filter=status_filter,
        PostStatus=PostStatus,
    )


@admin_bp.route("/posts/new", methods=["GET", "POST"])
@login_required
@editor_required
def post_create():
    all_categories = PostCategory.query.order_by(PostCategory.sort_order).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("文章標題為必填。", "error")
            return render_template("admin/posts/form.html", post=None, all_categories=all_categories, PostStatus=PostStatus)

        slug = request.form.get("slug", "").strip() or _slugify(title)
        if Post.query.filter_by(slug=slug).first():
            slug = slug + "-" + str(Post.query.count() + 1)

        status_val = request.form.get("status", "draft")
        status = PostStatus[status_val] if status_val in PostStatus.__members__ else PostStatus.draft

        published_at = None
        if status == PostStatus.published:
            pub_str = request.form.get("published_at", "").strip()
            if pub_str:
                try:
                    published_at = datetime.fromisoformat(pub_str).replace(tzinfo=timezone.utc)
                except ValueError:
                    published_at = datetime.now(timezone.utc)
            else:
                published_at = datetime.now(timezone.utc)

        post = Post(
            author_id=current_user.id,
            category_id=request.form.get("category_id", type=int) or None,
            title=title,
            slug=slug,
            excerpt=request.form.get("excerpt", "").strip() or None,
            content=request.form.get("content", "").strip() or None,
            cover_image_url=request.form.get("cover_image_url", "").strip() or None,
            cover_thumb_url=request.form.get("cover_thumb_url", "").strip() or None,
            status=status,
            published_at=published_at,
            meta_title=request.form.get("meta_title", "").strip() or None,
            meta_description=request.form.get("meta_description", "").strip() or None,
        )
        db.session.add(post)
        db.session.commit()
        flash(f"文章「{title}」已建立。", "success")
        return redirect(url_for("admin.posts"))

    return render_template("admin/posts/form.html", post=None, all_categories=all_categories, PostStatus=PostStatus)


@admin_bp.route("/posts/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
@editor_required
def post_edit(post_id: int):
    post = Post.query.get_or_404(post_id)
    all_categories = PostCategory.query.order_by(PostCategory.sort_order).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("文章標題為必填。", "error")
            return render_template("admin/posts/form.html", post=post, all_categories=all_categories, PostStatus=PostStatus)

        status_val = request.form.get("status", "draft")
        status = PostStatus[status_val] if status_val in PostStatus.__members__ else PostStatus.draft

        if status == PostStatus.published and not post.published_at:
            pub_str = request.form.get("published_at", "").strip()
            if pub_str:
                try:
                    post.published_at = datetime.fromisoformat(pub_str).replace(tzinfo=timezone.utc)
                except ValueError:
                    post.published_at = datetime.now(timezone.utc)
            else:
                post.published_at = datetime.now(timezone.utc)

        post.title = title
        post.slug = request.form.get("slug", "").strip() or post.slug
        post.category_id = request.form.get("category_id", type=int) or None
        post.excerpt = request.form.get("excerpt", "").strip() or None
        post.content = request.form.get("content", "").strip() or None
        post.cover_image_url = request.form.get("cover_image_url", "").strip() or None
        post.cover_thumb_url = request.form.get("cover_thumb_url", "").strip() or None
        post.status = status
        post.meta_title = request.form.get("meta_title", "").strip() or None
        post.meta_description = request.form.get("meta_description", "").strip() or None
        db.session.commit()
        flash(f"文章「{title}」已更新。", "success")
        return redirect(url_for("admin.posts"))

    return render_template("admin/posts/form.html", post=post, all_categories=all_categories, PostStatus=PostStatus)


@admin_bp.route("/posts/<int:post_id>/delete", methods=["POST"])
@login_required
@editor_required
def post_delete(post_id: int):
    post = Post.query.get_or_404(post_id)
    title = post.title
    db.session.delete(post)
    db.session.commit()
    flash(f"文章「{title}」已刪除。", "success")
    return redirect(url_for("admin.posts"))
