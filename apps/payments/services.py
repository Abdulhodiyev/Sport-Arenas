# apps/payments/services.py
import uuid
from typing import Dict, Any

# NOTE: In real integration, you do HTTP requests to Click/Payme and verify signatures.
# Here we simulate provider behaviour.

def create_click_payment(payment) -> Dict[str, Any]:
    """
    Simulate creating a payment at provider.
    Return dict with 'provider_id', 'pay_url', 'metadata'.
    """
    provider_id = str(uuid.uuid4())
    # In real life pay_url is a provider page. For testing we'll provide a fake callback URL
    # that frontend can hit or you can call directly.
    pay_url = f"/api/payments/fake-pay-page/{payment.id}/?provider_id={provider_id}"
    metadata = {
        "fake": True,
        "intent": "click_simulation"
    }
    return {"provider_id": provider_id, "pay_url": pay_url, "metadata": metadata}


def verify_provider_payment(payload: dict) -> dict:
    """
    Simulate verifying provider payload.
    Expect payload contain provider_id or merchant_trans_id, status.
    Return dict: {'valid': True/False, 'provider_id': ..., 'status': 'success'/'failed'}
    """
    provider_id = payload.get("provider_id") or payload.get("transaction_id") or payload.get("merchant_trans_id")
    status = payload.get("status") or payload.get("error_status") or payload.get("error")
    # For fake provider, accept everything that has provider_id
    if not provider_id:
        return {"valid": False}

    # Interpret status: provider might send error="0" for success (Click)
    if status in (0, "0", "success", "ok", "paid"):
        mapped = "success"
    elif status in (1, "1", "failed", "error"):
        mapped = "failed"
    else:
        # default: success if explicit success token present
        mapped = "success" if payload.get("simulate_success") else "failed"
    return {"valid": True, "provider_id": str(provider_id), "status": mapped}


def refund_provider_payment(payment) -> dict:
    """
    Simulate refund call to provider.
    """
    # Fake immediate success
    return {"success": True, "provider_refund_id": str(uuid.uuid4())}


def verify_click_signature(payload: dict) -> bool:
    """
    Fake signature check for Click webhook.
    If payload contains key 'fake_signature' == 'ok' accept it.
    """
    sig = payload.get("fake_signature")
    return sig == "ok"
