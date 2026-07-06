import hmac
import hashlib
import base64
import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# Base API endpoint for Shiprocket Checkout (Fastrr)
BASE_URL = "https://checkout-api.shiprocket.com"

# API Key & Secret Key defaults from public integration examples
DEFAULT_API_KEY = "H3E8hebrr7oZFnVV"
DEFAULT_SECRET_KEY = "C3TMxIORicQUmJ70OYFCSqlXxTO1tADvFItwGp0kE60="

def get_checkout_credentials():
    """
    Retrieve Shiprocket Checkout API Key and Secret Key from Django settings
    with fallback to defaults ONLY in local DEBUG mode.
    """
    api_key = getattr(settings, 'SHIPROCKET_CHECKOUT_API_KEY', '')
    secret_key = getattr(settings, 'SHIPROCKET_CHECKOUT_SECRET_KEY', '')
    
    if not api_key:
        if settings.DEBUG:
            api_key = DEFAULT_API_KEY
        else:
            logger.error("Shiprocket Checkout API Key is missing in production!")
            api_key = ""
    if not secret_key:
        if settings.DEBUG:
            secret_key = DEFAULT_SECRET_KEY
        else:
            logger.error("Shiprocket Checkout Secret Key is missing in production!")
            secret_key = ""
        
    return api_key, secret_key


def calculate_hmac(secret_key, body_bytes):
    """
    Calculate HMAC SHA256 signature in Base64 encoding.
    """
    signature = hmac.new(
        secret_key.encode('utf-8'),
        body_bytes,
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

def generate_checkout_token(cart_items, redirect_url, timestamp_str):
    """
    Calls Shiprocket Checkout API to generate a session checkout token.
    
    cart_items structure: [{"variant_id": "...", "quantity": 1}]
    """
    api_key, secret_key = get_checkout_credentials()
    
    payload = {
        "cart_data": {
            "items": cart_items
        },
        "redirect_url": redirect_url,
        "timestamp": timestamp_str
    }
    
    body_json = json.dumps(payload, separators=(',', ':'))
    body_bytes = body_json.encode('utf-8')
    
    hmac_sig = calculate_hmac(secret_key, body_bytes)
    
    url = f"{BASE_URL}/api/v1/access-token/checkout"
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key,
        "X-Api-HMAC-SHA256": hmac_sig
    }
    
    try:
        logger.info(f"Initiating Shiprocket Checkout token generation. URL: {url}")
        response = requests.post(url, data=body_bytes, headers=headers, timeout=15)
        
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get("ok"):
                result = res_data.get("result", {})
                return {
                    "success": True,
                    "token": result.get("token"),
                    "expires_at": result.get("expires_at"),
                    "order_id": result.get("data", {}).get("order_id")
                }
            else:
                error_msg = res_data.get("error", "Unknown error")
                logger.error(f"Shiprocket Checkout response error: {error_msg}")
                return {"success": False, "message": error_msg}
        else:
            logger.error(f"Shiprocket Checkout token status code {response.status_code}: {response.text}")
            return {"success": False, "message": f"API error: {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Exception during Shiprocket token generation: {str(e)}")
        return {"success": False, "message": str(e)}

def verify_webhook_signature(body_bytes, signature_header):
    """
    Verifies that the incoming webhook request is signed correctly.
    """
    if not signature_header:
        return False
        
    _, secret_key = get_checkout_credentials()
    calculated = calculate_hmac(secret_key, body_bytes)
    
    return hmac.compare_digest(calculated, signature_header)
