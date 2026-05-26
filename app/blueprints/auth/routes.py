"""認證路由 - 登入、登出"""
from datetime import datetime, timezone

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.blueprints.auth import auth_bp
from app.blueprints.auth.forms import LoginForm
from app.extensions import db, limiter
from app.models.user import User


@auth_bp.route("/admin/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()

        if user is None or not user.is_active:
            flash("帳號或密碼錯誤。", "error")
            return render_template("auth/login.html", form=form)

        if user.is_locked():
            flash("帳號已鎖定，請稍後再試。", "error")
            return render_template("auth/login.html", form=form)

        if not user.check_password(form.password.data):
            user.increment_login_attempts()
            db.session.commit()
            flash("帳號或密碼錯誤。", "error")
            return render_template("auth/login.html", form=form)

        # 登入成功
        user.reset_login_attempts()
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

        login_user(user, remember=form.remember.data)
        next_page = request.args.get("next")
        return redirect(next_page or url_for("admin.dashboard"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/admin/logout")
@login_required
def logout():
    logout_user()
    flash("已登出。", "info")
    return redirect(url_for("auth.login"))
