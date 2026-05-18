"""API 路由（階段 3-4 逐步完整實作）"""
from flask import jsonify, request

from app.blueprints.api import api_bp
from app.extensions import db, limiter


@api_bp.route("/works")
@limiter.limit("60 per minute")
def get_works():
    """取得作品列表（支援 artist_id、category_id 篩選）"""
    from app.models.work import Work

    query = Work.query.filter_by(is_published=True)

    artist_id = request.args.get("artist_id", type=int)
    if artist_id:
        query = query.filter_by(artist_id=artist_id)

    works = query.order_by(Work.sort_order, Work.created_at.desc()).all()
    return jsonify(
        [
            {
                "id": w.id,
                "image_url": w.image_url,
                "thumb_url": w.thumb_url,
                "webp_url": w.webp_url,
                "artist_id": w.artist_id,
                "body_part": w.body_part,
            }
            for w in works
        ]
    )


@api_bp.route("/subscribe", methods=["POST"])
@limiter.limit("5 per hour")
def subscribe():
    """電子報訂閱"""
    from app.models.subscriber import Subscriber
    from app.services.email_service import send_newsletter_confirmation

    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email or "@" not in email:
        return jsonify({"error": "請輸入有效的 Email"}), 400

    existing = Subscriber.query.filter_by(email=email).first()
    if existing:
        if existing.is_confirmed:
            return jsonify({"message": "您已訂閱，感謝支持！"}), 200
        # 重新發送確認信
        send_newsletter_confirmation(existing)
        return jsonify({"message": "確認信已重新寄出，請查收信箱。"}), 200

    sub = Subscriber(email=email)
    sub.generate_token()
    db.session.add(sub)
    db.session.commit()

    send_newsletter_confirmation(sub)
    return jsonify({"message": "感謝訂閱！請查收確認信。"}), 201


@api_bp.route("/business-status")
@limiter.limit("120 per minute")
def business_status():
    """回傳目前是否營業中"""
    from app.utils.helpers import is_business_open

    return jsonify({"is_open": is_business_open()})
