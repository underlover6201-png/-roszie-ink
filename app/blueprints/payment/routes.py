"""金流路由 — 綠界 ECPay"""
import logging

from flask import current_app, redirect, render_template, request, url_for

from app.blueprints.payment import payment_bp
from app.extensions import csrf, db
from app.models.payment import Payment, PaymentStatus, PaymentType
from app.services.ecpay_service import build_ecpay_form, verify_check_mac_value

logger = logging.getLogger(__name__)


# ── 認領圖結帳 ─────────────────────────────────────────────
@payment_bp.route("/flash/<slug>", methods=["GET", "POST"])
def flash_checkout(slug: str):
    from app.models.flash import FlashDesign

    design = FlashDesign.query.filter_by(slug=slug, is_published=True).first_or_404()
    if design.is_claimed:
        return render_template("payment/unavailable.html",
                               reason="此認領圖已被其他人認領。",
                               back_url=url_for("public.shop"))

    if request.method == "POST":
        name = request.form.get("payer_name", "").strip()
        email = request.form.get("payer_email", "").strip().lower()
        phone = request.form.get("payer_phone", "").strip()
        note = request.form.get("payer_note", "").strip()

        if not name or not email:
            return render_template("payment/checkout.html", design=design, course=None,
                                   error="姓名和 Email 為必填。")

        amount = int(design.price)
        payment = Payment(
            payment_type=PaymentType.flash,
            ref_id=design.id,
            amount=amount,
            currency=design.currency,
            payer_name=name,
            payer_email=email,
            payer_phone=phone or None,
            payer_note=note or None,
            status=PaymentStatus.processing,
        )
        db.session.add(payment)
        db.session.commit()

        site_url = current_app.config["SITE_URL"].rstrip("/")
        html = build_ecpay_form(
            merchant_id=current_app.config["ECPAY_MERCHANT_ID"],
            hash_key=current_app.config["ECPAY_HASH_KEY"],
            hash_iv=current_app.config["ECPAY_HASH_IV"],
            api_url=current_app.config["ECPAY_API_URL"],
            trade_no=payment.trade_no,
            amount=amount,
            item_name=f"認領圖：{design.title}",
            trade_desc=f"ROSZIE INK Flash Design - {design.title}",
            return_url=f"{site_url}/pay/notify",
            order_result_url=f"{site_url}/pay/result",
            client_back_url=f"{site_url}/shop/{slug}",
            payer_email=email,
            test_mode=current_app.config.get("ECPAY_TEST_MODE", True),
        )
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}

    return render_template("payment/checkout.html", design=design, course=None, error=None)


# ── 課程報名結帳 ────────────────────────────────────────────
@payment_bp.route("/course/<slug>", methods=["GET", "POST"])
def course_checkout(slug: str):
    from app.models.course import Course, CourseStatus

    course = Course.query.filter_by(slug=slug, status=CourseStatus.open).first_or_404()
    if course.is_full:
        return render_template("payment/unavailable.html",
                               reason="此課程名額已額滿。",
                               back_url=url_for("public.courses"))

    if request.method == "POST":
        name = request.form.get("payer_name", "").strip()
        email = request.form.get("payer_email", "").strip().lower()
        phone = request.form.get("payer_phone", "").strip()
        note = request.form.get("payer_note", "").strip()

        if not name or not email:
            return render_template("payment/checkout.html", design=None, course=course,
                                   error="姓名和 Email 為必填。")

        if not course.price:
            return render_template("payment/unavailable.html",
                                   reason="此課程尚未設定價格，請聯絡我們。",
                                   back_url=url_for("public.course_detail", slug=slug))

        # 先建立 pending 的 CourseEnrollment
        from app.models.course import CourseEnrollment, EnrollmentStatus
        enrollment = CourseEnrollment(
            course_id=course.id,
            student_name=name,
            student_email=email,
            student_phone=phone or None,
            notes=note or None,
            status=EnrollmentStatus.pending,
        )
        db.session.add(enrollment)

        amount = int(course.price)
        payment = Payment(
            payment_type=PaymentType.course,
            ref_id=course.id,
            amount=amount,
            currency=course.currency or "TWD",
            payer_name=name,
            payer_email=email,
            payer_phone=phone or None,
            payer_note=note or None,
            status=PaymentStatus.processing,
        )
        db.session.add(payment)
        db.session.commit()

        # 在 payment 備註存 enrollment_id 以便 notify 時找到
        payment.payer_note = f"enrollment_id:{enrollment.id}|{note}"
        db.session.commit()

        site_url = current_app.config["SITE_URL"].rstrip("/")
        html = build_ecpay_form(
            merchant_id=current_app.config["ECPAY_MERCHANT_ID"],
            hash_key=current_app.config["ECPAY_HASH_KEY"],
            hash_iv=current_app.config["ECPAY_HASH_IV"],
            api_url=current_app.config["ECPAY_API_URL"],
            trade_no=payment.trade_no,
            amount=amount,
            item_name=f"課程報名：{course.title}",
            trade_desc=f"ROSZIE INK Course - {course.title}",
            return_url=f"{site_url}/pay/notify",
            order_result_url=f"{site_url}/pay/result",
            client_back_url=f"{site_url}/courses/{slug}",
            payer_email=email,
            test_mode=current_app.config.get("ECPAY_TEST_MODE", True),
        )
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}

    return render_template("payment/checkout.html", design=None, course=course, error=None)


# ── ECPay 伺服器回呼（notify_url）──────────────────────────
@payment_bp.route("/notify", methods=["POST"])
@csrf.exempt
def notify():
    """
    ECPay 付款結果通知（server-to-server）。
    必須回傳 '0|OK' 讓 ECPay 知道我們收到了。
    此路由需要公開可訪問（用 ngrok 或正式網域）。
    """
    data = request.form.to_dict()
    logger.info(f"ECPay notify received: MerchantTradeNo={data.get('MerchantTradeNo')}, "
                f"RtnCode={data.get('RtnCode')}")

    hash_key = current_app.config["ECPAY_HASH_KEY"]
    hash_iv = current_app.config["ECPAY_HASH_IV"]

    if not verify_check_mac_value(data, hash_key, hash_iv):
        logger.warning("ECPay notify: CheckMacValue 驗證失敗")
        return "0|Fail", 200

    trade_no = data.get("MerchantTradeNo", "")
    rtn_code = data.get("RtnCode", "")
    ecpay_trade_no = data.get("TradeNo", "")
    payment_type = data.get("PaymentType", "")

    payment = Payment.query.filter_by(trade_no=trade_no).first()
    if not payment:
        logger.warning(f"ECPay notify: 找不到訂單 {trade_no}")
        return "0|OK", 200

    import json
    raw = json.dumps(data, ensure_ascii=False)

    if rtn_code == "1":
        payment.mark_paid(ecpay_trade_no, payment_type, raw)
        _on_payment_success(payment)
        logger.info(f"付款成功：{trade_no}")
    else:
        payment.mark_failed(raw)
        _on_payment_failed(payment)
        logger.info(f"付款失敗：{trade_no}, RtnCode={rtn_code}")

    db.session.commit()
    return "0|OK", 200


def _on_payment_success(payment: Payment) -> None:
    """付款成功後的業務邏輯"""
    if payment.payment_type == PaymentType.flash:
        from app.models.flash import FlashDesign
        design = FlashDesign.query.get(payment.ref_id)
        if design:
            design.claim()

    elif payment.payment_type == PaymentType.course:
        from app.models.course import CourseEnrollment, EnrollmentStatus
        # 從 payer_note 取出 enrollment_id
        note = payment.payer_note or ""
        enrollment_id = None
        for part in note.split("|"):
            if part.startswith("enrollment_id:"):
                try:
                    enrollment_id = int(part.split(":")[1])
                except (ValueError, IndexError):
                    pass
        if enrollment_id:
            enrollment = CourseEnrollment.query.get(enrollment_id)
            if enrollment:
                enrollment.status = EnrollmentStatus.confirmed


def _on_payment_failed(payment: Payment) -> None:
    """付款失敗後清理"""
    if payment.payment_type == PaymentType.course:
        from app.models.course import CourseEnrollment, EnrollmentStatus
        note = payment.payer_note or ""
        for part in note.split("|"):
            if part.startswith("enrollment_id:"):
                try:
                    enrollment_id = int(part.split(":")[1])
                    enrollment = CourseEnrollment.query.get(enrollment_id)
                    if enrollment:
                        enrollment.status = EnrollmentStatus.cancelled
                except (ValueError, IndexError):
                    pass


# ── 付款結果頁（瀏覽器跳轉）────────────────────────────────
@payment_bp.route("/result", methods=["GET", "POST"])
@csrf.exempt
def result():
    """ECPay 付款後跳轉頁"""
    data = request.form.to_dict() if request.method == "POST" else request.args.to_dict()
    rtn_code = data.get("RtnCode", "")
    trade_no = data.get("MerchantTradeNo", "")

    payment = Payment.query.filter_by(trade_no=trade_no).first()

    if rtn_code == "1" or (payment and payment.status == PaymentStatus.paid):
        return render_template("payment/success.html", payment=payment, data=data)
    else:
        rtn_msg = data.get("RtnMsg", "付款未完成")
        return render_template("payment/failure.html", payment=payment,
                               data=data, rtn_msg=rtn_msg)
