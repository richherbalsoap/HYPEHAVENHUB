import json
import logging
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Coupon, CountrySetting, Cart

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def shipping_info(request):
    """
    Razorpay Magic Checkout Shipping API
    Request shape sent by Razorpay:
    {
      "order_id": "...", "razorpay_order_id": "...", "email": "...", "contact": "...",
      "addresses": [{"id": "0", "zipcode": "560060", "state_code": "KA", "country": "IN"}]
    }
    Required response shape:
    {
      "addresses": [
        {
          "id": "0", "zipcode": "560060", "country": "IN",
          "shipping_methods": [
            {"id": "standard", "description": "...", "name": "...",
             "serviceable": true, "shipping_fee": 0, "cod": true, "cod_fee": 0}
          ]
        }
      ]
    }
    """
    try:
        data = json.loads(request.body)
        addresses = data.get('addresses', [])

        response_addresses = []
        for addr in addresses:
            country_code = (addr.get('country') or 'IN').upper()

            shipping_fee = 0
            cod_available = True
            cod_fee = 0
            serviceable = True

            country = CountrySetting.objects.filter(code__iexact=country_code).first()
            if country:
                shipping_fee = int(country.shipping_charge * 100)  # paise
                
            if country_code != 'IN':
                cod_available = False
                serviceable = False

            response_addresses.append({
                "id": addr.get('id', '0'),
                "zipcode": addr.get('zipcode', ''),
                "country": country_code,
                "shipping_methods": [
                    {
                        "id": "standard",
                        "description": "Standard Delivery",
                        "name": "Standard Delivery",
                        "serviceable": serviceable,
                        "shipping_fee": shipping_fee,
                        "cod": cod_available,
                        "cod_fee": cod_fee
                    }
                ]
            })

        return JsonResponse({"addresses": response_addresses})
    except Exception as e:
        logger.error(f"Error in magic checkout shipping info: {str(e)}")
        # Safe fallback: mark serviceable with no extra charge so checkout doesn't hard-block
        return JsonResponse({
            "addresses": [
                {
                    "id": "0",
                    "zipcode": "",
                    "country": "IN",
                    "shipping_methods": [
                        {
                            "id": "standard",
                            "description": "Standard Delivery",
                            "name": "Standard Delivery",
                            "serviceable": True,
                            "shipping_fee": 0,
                            "cod": True,
                            "cod_fee": 0
                        }
                    ]
                }
            ]
        })


@csrf_exempt
@require_http_methods(["POST"])
def get_promotions(request):
    """
    Razorpay Magic Checkout Get Promotions API
    Razorpay calls this via POST with {order_id, contact, email}.
    Required response: {"promotions": [{"code": "...", "summary": "...", "description": "..."}]}
    """
    try:
        coupons = Coupon.objects.filter(active=True)
        promotions = []
        for coupon in coupons:
            summary = (
                f"{coupon.discount_percent}% off"
                if coupon.discount_type == 'percentage'
                else f"Flat ₹{coupon.discount_amount} off"
            )
            promotions.append({
                "code": coupon.code,
                "summary": summary,
                "description": f"{summary} on orders above ₹{coupon.min_order_amount}"
            })

        return JsonResponse({"promotions": promotions})
    except Exception as e:
        logger.error(f"Error in magic checkout get promotions: {str(e)}")
        return JsonResponse({"promotions": []})


@csrf_exempt
@require_http_methods(["POST"])
def apply_promotion(request):
    """
    Razorpay Magic Checkout Apply Promotion API
    Razorpay sends: {"order_id": "...", "contact": "...", "email": "...", "code": "500OFF"}
    Required success response:
    {
      "promotion": {
        "reference_id": "...", "code": "...", "type": "coupon",
        "value": <int, paise>, "value_type": "fixed_amount"|"percentage",
        "description": "..."
      }
    }
    """
    try:
        data = json.loads(request.body)
        coupon_code = data.get('code') or data.get('promotion_code')
        order_amount_paise = data.get('order_amount', 0)
        order_amount = order_amount_paise / 100 if order_amount_paise else 0

        if not coupon_code:
            return JsonResponse({"error": {"description": "Coupon code is required"}}, status=400)

        coupon = Coupon.objects.filter(code__iexact=coupon_code, active=True).first()
        if not coupon:
            return JsonResponse({"error": {"description": "Invalid or expired coupon"}}, status=400)

        if order_amount and order_amount < coupon.min_order_amount:
            return JsonResponse({
                "error": {"description": f"Minimum order amount is ₹{coupon.min_order_amount}"}
            }, status=400)

        if coupon.discount_type == 'percentage':
            value = int(coupon.discount_percent)  # percentage points, e.g. 10 for 10%
            value_type = "percentage"
        else:
            value = int(coupon.discount_amount * 100)  # paise
            value_type = "fixed_amount"

        return JsonResponse({
            "promotion": {
                "reference_id": f"coupon_{coupon.id}",
                "code": coupon.code,
                "type": "coupon",
                "value": value,
                "value_type": value_type,
                "description": f"Discount applied: {coupon.code}"
            }
        })
    except Exception as e:
        logger.error(f"Error in magic checkout apply promotion: {str(e)}")
        return JsonResponse({"error": {"description": "Internal server error"}}, status=500)
