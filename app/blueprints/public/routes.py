"""前台公開路由（階段 3 會逐頁完整實作，此處先建立骨架確保 app 可啟動）"""
from flask import render_template

from app.blueprints.public import public_bp


@public_bp.route("/")
def home():
    from app.models.work import Work
    from app.models.artist import Artist
    from app.models.post import Post, PostStatus

    featured_works = Work.query.filter_by(is_featured=True, is_published=True).limit(9).all()
    artists = Artist.query.filter_by(is_active=True).order_by(Artist.sort_order).all()
    latest_posts = (
        Post.query.filter_by(status=PostStatus.published).order_by(Post.published_at.desc()).limit(3).all()
    )
    return render_template(
        "public/home.html",
        featured_works=featured_works,
        artists=artists,
        latest_posts=latest_posts,
    )


@public_bp.route("/artists")
def artists():
    from app.models.artist import Artist

    all_artists = Artist.query.filter_by(is_active=True).order_by(Artist.sort_order).all()
    return render_template("public/artists/list.html", artists=all_artists)


@public_bp.route("/artists/<slug>")
def artist_detail(slug: str):
    from app.models.artist import Artist

    artist = Artist.query.filter_by(slug=slug, is_active=True).first_or_404()
    works = artist.works.filter_by(is_published=True).all()
    return render_template("public/artists/detail.html", artist=artist, works=works)


@public_bp.route("/portfolio")
def portfolio():
    from flask import request
    from app.models.work import Work
    from app.utils.helpers import paginate_query

    page = request.args.get("page", 1, type=int)
    works = paginate_query(Work.query.filter_by(is_published=True), page=page, per_page=18)
    return render_template("public/portfolio/index.html", works=works)


@public_bp.route("/appointment", methods=["GET", "POST"])
def appointment():
    from flask import redirect, request, url_for
    from app.extensions import db
    from app.models.artist import Artist
    from app.models.booking import Booking, BookingSize, ColorPreference

    artists = Artist.query.filter_by(is_active=True).order_by(Artist.sort_order).all()

    if request.method == "POST":
        client_name = request.form.get("client_name", "").strip()
        client_email = request.form.get("client_email", "").strip().lower()
        placement = request.form.get("placement", "").strip()

        if not client_name or not client_email or not placement:
            return render_template("public/appointment/form.html", artists=artists,
                                   error="請填寫必填欄位（姓名、Email、刺青位置）。")

        artist_id = request.form.get("artist_id") or None
        if artist_id:
            artist_id = int(artist_id)

        size_val = request.form.get("size")
        size = BookingSize[size_val] if size_val and size_val in BookingSize.__members__ else None

        color_val = request.form.get("color_preference")
        color = ColorPreference[color_val] if color_val and color_val in ColorPreference.__members__ else None

        from datetime import date
        def parse_date(val):
            try:
                return date.fromisoformat(val) if val else None
            except (ValueError, TypeError):
                return None

        booking = Booking(
            client_name=client_name,
            client_email=client_email,
            client_phone=request.form.get("client_phone", "").strip() or None,
            client_instagram=request.form.get("client_instagram", "").strip() or None,
            artist_id=artist_id,
            placement=placement,
            size=size,
            color_preference=color,
            style=request.form.get("style", "").strip() or None,
            budget_range=request.form.get("budget_range", "").strip() or None,
            preferred_date_start=parse_date(request.form.get("preferred_date_start")),
            preferred_date_end=parse_date(request.form.get("preferred_date_end")),
            notes=request.form.get("notes", "").strip() or None,
        )
        db.session.add(booking)
        db.session.commit()
        return redirect(url_for("public.appointment_success", number=booking.booking_number))

    return render_template("public/appointment/form.html", artists=artists)


@public_bp.route("/appointment/success")
def appointment_success():
    from flask import request
    booking_number = request.args.get("number", "")
    return render_template("public/appointment/success.html", booking_number=booking_number)


@public_bp.route("/magazine")
def magazine():
    from flask import request
    from app.models.post import Post, PostStatus
    from app.utils.helpers import paginate_query

    page = request.args.get("page", 1, type=int)
    posts = paginate_query(
        Post.query.filter_by(status=PostStatus.published).order_by(Post.published_at.desc()),
        page=page,
        per_page=9,
    )
    return render_template("public/magazine/list.html", posts=posts)


@public_bp.route("/magazine/<slug>")
def post_detail(slug: str):
    from app.extensions import db
    from app.models.post import Post, PostStatus

    post = Post.query.filter_by(slug=slug, status=PostStatus.published).first_or_404()
    post.increment_view()
    db.session.commit()
    return render_template("public/magazine/detail.html", post=post)


@public_bp.route("/courses")
def courses():
    from app.models.course import Course, CourseStatus

    all_courses = Course.query.filter_by(status=CourseStatus.open).all()
    return render_template("public/courses/list.html", courses=all_courses)


@public_bp.route("/courses/<slug>")
def course_detail(slug: str):
    from app.models.course import Course, CourseStatus

    course = Course.query.filter_by(slug=slug, status=CourseStatus.open).first_or_404()
    return render_template("public/courses/detail.html", course=course)


@public_bp.route("/shop")
def shop():
    from app.models.flash import FlashDesign
    from app.models.artist import Artist

    artist_id = None
    from flask import request as req
    artist_id_str = req.args.get("artist")
    if artist_id_str:
        try:
            artist_id = int(artist_id_str)
        except ValueError:
            pass

    query = FlashDesign.query.filter_by(is_published=True)
    if artist_id:
        query = query.filter_by(artist_id=artist_id)
    designs = query.order_by(FlashDesign.is_claimed, FlashDesign.sort_order, FlashDesign.created_at.desc()).all()
    artists = Artist.query.filter_by(is_active=True).order_by(Artist.sort_order).all()
    return render_template("public/shop/index.html", designs=designs, artists=artists, active_artist=artist_id)


@public_bp.route("/shop/<slug>")
def shop_detail(slug: str):
    from app.models.flash import FlashDesign

    design = FlashDesign.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template("public/shop/detail.html", design=design)


@public_bp.route("/about")
def about():
    return render_template("public/about.html")


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    return render_template("public/contact.html")


@public_bp.route("/privacy")
def privacy():
    return render_template("public/privacy.html")


@public_bp.route("/terms")
def terms():
    return render_template("public/terms.html")


@public_bp.route("/newsletter/confirm/<token>")
def confirm_newsletter(token: str):
    from app.extensions import db
    from app.models.subscriber import Subscriber

    sub = Subscriber.query.filter_by(confirmation_token=token).first_or_404()
    sub.confirm()
    db.session.commit()
    return render_template("public/newsletter_confirmed.html")


@public_bp.route("/health")
def health():
    """健康檢查端點（Docker / load balancer 用）"""
    from flask import jsonify

    return jsonify({"status": "ok", "studio": "ROSZIE INK"})


@public_bp.route("/sitemap.xml")
def sitemap():
    from flask import Response, url_for
    from app.models.artist import Artist
    from app.models.post import Post, PostStatus
    from app.models.course import Course, CourseStatus

    pages = []
    pages.append(url_for("public.home", _external=True))
    pages.append(url_for("public.artists", _external=True))
    pages.append(url_for("public.portfolio", _external=True))
    pages.append(url_for("public.appointment", _external=True))
    pages.append(url_for("public.magazine", _external=True))
    pages.append(url_for("public.courses", _external=True))
    pages.append(url_for("public.about", _external=True))
    pages.append(url_for("public.contact", _external=True))

    for artist in Artist.query.filter_by(is_active=True).all():
        pages.append(url_for("public.artist_detail", slug=artist.slug, _external=True))

    for post in Post.query.filter_by(status=PostStatus.published).all():
        pages.append(url_for("public.post_detail", slug=post.slug, _external=True))

    for course in Course.query.filter_by(status=CourseStatus.open).all():
        pages.append(url_for("public.course_detail", slug=course.slug, _external=True))

    xml = render_template("sitemap.xml", pages=pages)
    return Response(xml, mimetype="application/xml")
