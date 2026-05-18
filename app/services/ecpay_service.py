"""綠界 ECPay 金流服務"""
import hashlib
import urllib.parse
from datetime import datetime


def _generate_check_mac_value(params: dict, hash_key: str, hash_iv: str) -> str:
    """
    ECPay CheckMacValue 計算：
    1. 依 key 字母排序
    2. 組成 HashKey={key}&k1=v1&k2=v2...&HashIV={iv}
    3. URL encode（quote_plus）並全部轉小寫
    4. SHA-256 → 轉大寫
    """
    sorted_params = sorted(params.items(), key=lambda x: x[0].lower())
    param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
    raw = f"HashKey={hash_key}&{param_str}&HashIV={hash_iv}"
    encoded = urllib.parse.quote_plus(raw).lower()
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()


def verify_check_mac_value(data: dict, hash_key: str, hash_iv: str) -> bool:
    """驗證 ECPay 回呼的 CheckMacValue"""
    received = data.get("CheckMacValue", "")
    params = {k: v for k, v in data.items() if k != "CheckMacValue"}
    expected = _generate_check_mac_value(params, hash_key, hash_iv)
    return received.upper() == expected.upper()


def build_ecpay_form(
    *,
    merchant_id: str,
    hash_key: str,
    hash_iv: str,
    api_url: str,
    trade_no: str,
    amount: int,
    item_name: str,
    trade_desc: str,
    return_url: str,
    order_result_url: str,
    client_back_url: str,
    payer_email: str = "",
    choose_payment: str = "ALL",
    test_mode: bool = True,
) -> str:
    """
    產生自動提交的 ECPay 付款 HTML form。

    trade_desc：交易描述，不能超過 200 字元，不能含特殊字元。
    item_name：商品名稱，多個用 # 分隔。
    """
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    params: dict[str, str] = {
        "MerchantID": merchant_id,
        "MerchantTradeNo": trade_no,
        "MerchantTradeDate": now,
        "PaymentType": "aio",
        "TotalAmount": str(amount),
        "TradeDesc": urllib.parse.quote(trade_desc[:200]),
        "ItemName": item_name[:200],
        "ReturnURL": return_url,
        "ChoosePayment": choose_payment,
        "EncryptType": "1",           # SHA-256
        "OrderResultURL": order_result_url,
        "ClientBackURL": client_back_url,
    }

    if payer_email:
        params["Email"] = payer_email

    # 測試模式：ECPay 提供固定測試信用卡
    if test_mode:
        params["IgnorePayment"] = ""  # 不篩選付款方式

    params["CheckMacValue"] = _generate_check_mac_value(params, hash_key, hash_iv)

    # 產生 hidden input 清單
    inputs = "\n".join(
        f'    <input type="hidden" name="{k}" value="{v}">'
        for k, v in params.items()
    )

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>正在前往付款頁面...</title>
</head>
<body>
<p style="font-family:sans-serif;text-align:center;margin-top:20vh;color:#666;">
  正在安全地引導您前往付款頁面，請稍候...
</p>
<form id="ecpay-form" method="POST" action="{api_url}">
{inputs}
</form>
<script>document.getElementById('ecpay-form').submit();</script>
</body></html>"""
