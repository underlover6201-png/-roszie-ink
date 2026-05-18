"""付款紀錄 model"""
import enum
import uuid
from datetime import datetime, timezone

from app.extensions import db


class PaymentStatus(enum.Enum):
    pending = "pending"       # 建立訂單，尚未前往付款
    processing = "processing" # 已提交到 ECPay，等待回呼
    paid = "paid"             # 付款成功
    failed = "failed"         # 付款失敗
    refunded = "refunded"     # 已退款


class PaymentType(enum.Enum):
    flash = "flash"    # 認領圖
    course = "course"  # 課程報名


def _generate_trade_no() -> str:
    """產生最多 20 碼的訂單號（ECPay 限制）"""
    ts = datetime.now().strftime("%y%m%d%H%M")  # 10 碼
    uid = uuid.uuid4().hex[:8].upper()           # 8 碼
    return f"RI{ts}{uid}"                        # 共 20 碼


class Payment(db.Model):
    """付款紀錄（對應一筆 ECPay 交易）"""

    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    # 我們的內部訂單號（= ECPay MerchantTradeNo）
    trade_no = db.Column(
        db.String(20), unique=True, nullable=False,
        default=_generate_trade_no, index=True
    )

    # ECPay 回傳的交易序號
    ecpay_trade_no = db.Column(db.String(50))

    # 付款類型 & 關聯 ID
    payment_type = db.Column(db.Enum(PaymentType), nullable=False, index=True)
    ref_id = db.Column(db.Integer, nullable=False)  # flash_design.id 或 course.id

    # 金額
    amount = db.Column(db.Integer, nullable=False)  # ECPay 只接受整數
    currency = db.Column(db.String(10), default="TWD", nullable=False)

    # 付款人資訊
    payer_name = db.Column(db.String(100), nullable=False)
    payer_email = db.Column(db.String(120), nullable=False, index=True)
    payer_phone = db.Column(db.String(30))
    payer_note = db.Column(db.Text)

    # 狀態
    status = db.Column(
        db.Enum(PaymentStatus), default=PaymentStatus.pending,
        nullable=False, index=True
    )

    # ECPay 回呼原始資料
    ecpay_payment_method = db.Column(db.String(50))
    ecpay_raw_response = db.Column(db.Text)

    paid_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def status_label(self) -> str:
        labels = {
            PaymentStatus.pending: "待付款",
            PaymentStatus.processing: "處理中",
            PaymentStatus.paid: "已付款",
            PaymentStatus.failed: "付款失敗",
            PaymentStatus.refunded: "已退款",
        }
        return labels.get(self.status, self.status.value)

    def mark_paid(self, ecpay_trade_no: str, payment_method: str, raw: str) -> None:
        self.status = PaymentStatus.paid
        self.ecpay_trade_no = ecpay_trade_no
        self.ecpay_payment_method = payment_method
        self.ecpay_raw_response = raw
        self.paid_at = datetime.now(timezone.utc)

    def mark_failed(self, raw: str = "") -> None:
        self.status = PaymentStatus.failed
        self.ecpay_raw_response = raw

    def __repr__(self) -> str:
        return f"<Payment {self.trade_no} [{self.status.name}]>"
