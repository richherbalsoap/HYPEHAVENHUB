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
    Calculates shipping and COD fees based on the provided address.
    """
    try:
        data = json.loads(request.body)
        shipping_address = data.get('customer_details', {}).get('shipping_address', {})
        country_code = shipping_address.get('country', 'IN')
        
        # Default fallback fees (in paise)
        shipping_fee = 0
        cod_fee = 0
        shipping_serviceable = True
        cod_serviceable = True

        # Custom logic based on country
        if country_code:
            country = CountrySetting.objects.filter(code__iexact=country_code).first()
            if country:
                shipping_fee = int(country.shipping_charge * 100) # Convert to paise
                # Assuming COD is only available in India or specific countries
                if country_code.upper() != 'IN':
                    cod_serviceable = False

        response_data = {
            "shipping_fee": shipping_fee,
            "cod_fee": cod_fee,
            "shipping_serviceable": shipping_serviceable,
            "cod_serviceable": cod_serviceable
        }
        return JsonResponse(response_data)
    except Exception as e:
        logger.error(f"Error in magic checkout shipping info: {str(e)}")
        # Fallback response
        return JsonResponse({
            "shipping_fee": 0,
            "cod_fee": 0,
            "shipping_serviceable": True,
            "cod_serviceable": True
        })


@csrf_exempt
@require_http_methods(["GET"])
def get_promotions(request):
    """
    Razorpay Magic Checkout Get Promotions API
    Returns a list of active coupons.
    """
    try:
        coupons = Coupon.objects.filter(active=True)
        promotions = []
        for coupon in coupons:
            promotions.append({
                "code": coupon.code,
                "description": f"{coupon.discount_percent}% off" if coupon.discount_type == 'percentage' else f"Flat ₹{coupon.discount_amount} off",
                "type": coupon.discount_type,
                "value": float(coupon.discount_percent) if coupon.discount_type == 'percentage' else float(coupon.discount_amount),
                "min_order_value": float(coupon.min_order_amount)
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
    Validates the coupon code and returns the discount amount.
    """
    try:
        data = json.loads(request.body)
        coupon_code = data.get('promotion_code')
        order_amount = data.get('order_amount', 0) / 100  # Razorpay sends amount in paise
        
        if not coupon_code:
            return JsonResponse({"is_valid": False, "error_message": "Coupon code is required"})
            
        coupon = Coupon.objects.filter(code__iexact=coupon_code, active=True).first()
        if not coupon:
            return JsonResponse({"is_valid": False, "error_message": "Invalid or expired coupon"})
            
        if order_amount < coupon.min_order_amount:
            return JsonResponse({"is_valid": False, "error_message": f"Minimum order amount is ₹{coupon.min_order_amount}"})
            
        discount_amount = 0
        if coupon.discount_type == 'percentage':
            discount_amount = (order_amount * float(coupon.discount_percent)) / 100
        else:
            discount_amount = float(coupon.discount_amount)
            
        return JsonResponse({
            "is_valid": True,
            "discount_amount": int(discount_amount * 100) # Convert to paise
        })
    except Exception as e:
        logger.error(f"Error in magic checkout apply promotion: {str(e)}")
        return JsonResponse({"is_valid": False, "error_message": "Internal server error"})
