# Bu yerda haqiqiy provider API'lariga HTTP so'rov yuboriladi.
# Quyida faqat struktura ko'rsatilgan, sizning credentials va haqiqiy endpoint'larni o'rnating.

import requests
from django.conf import settings

def create_provider_payment(payment):
    """
    Yaratuvchi funktsiya: providerga so'rov yuboradi va checkout link / transaction_id qaytaradi.
    """
    # Misol: Click / Payme API integration — implement as needed.
    # Return example:
    return {
        "provider_id": f"prov_{payment.id}",
        "checkout_url": f"https://provider/pay/{payment.id}",
        "metadata": {"raw": "provider_create_response"}
    }

def verify_provider_payment(payload):
    """
    Webhook payloadni tekshirish: signature, fields va status ni aniqlash.
    Return dict: {"valid": True/False, "provider_id": "...", "status": "success"/"failure"}
    """
    # Implement signature check per provider
    # Example stub:
    try:
        provider_id = payload.get("order_id") or payload.get("transaction_id")
        provider_status = payload.get("status") or payload.get("state")
        mapped_status = "success" if provider_status in ["completed", "success", "paid"] else "failure"
        return {"valid": True, "provider_id": provider_id, "status": mapped_status}
    except Exception:
        return {"valid": False}

def refund_provider_payment(payment):
    """
    Initiate refund request to provider. Return {"success": True/False, ...}
    """
    # Example stub:
    return {"success": True, "provider_ref": f"refund_{payment.id}"}

import requests
from django.conf import settings

def create_click_payment(payment):
    payload = {
        "merchant_id": settings.CLICK_MERCHANT_ID,
        "service_id": settings.CLICK_SERVICE_ID,
        "amount": float(payment.amount),
        "transaction_param": str(payment.id),
        "return_url": "https://your-domain.com/payments/success",
        "card_type": "uzcard",
    }

    response = requests.post(settings.CLICK_API_URL, json=payload)
    data = response.json()

    # sample response:
    # {
    #   "error": 0,
    #   "error_note": "Success",
    #   "invoice_id": 12345,
    #   "merchant_trans_id": "abc",
    #   "payment_url": "https://my.click.uz/services/pay/?invoice_id=12345"
    # }

    if data.get("error") == 0:
        return {
            "provider_id": data["invoice_id"],
            "checkout_url": data["payment_url"],
            "metadata": data
        }
    else:
        return {"error": data}

import hashlib

def verify_click_signature(payload):
    sign_string = (
        payload["click_trans_id"] +
        settings.CLICK_SERVICE_ID +
        settings.CLICK_MERCHANT_USER_ID +
        payload["merchant_trans_id"] +
        payload["amount"] +
        payload["action"] +
        payload["sign_time"] +
        settings.CLICK_SECRET_KEY
    )

    calculated = hashlib.md5(sign_string.encode()).hexdigest()

    return calculated == payload["sign_string"]
