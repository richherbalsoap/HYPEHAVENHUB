import logging
from datetime import datetime, timezone as datetime_timezone
from django.conf import settings
import razorpay
from .models import OrderTracking

logger = logging.getLogger(__name__)

def process_razorpay_refund(order, reason="Order cancelled"):
    """
    Safely initiates a Razorpay refund for a given order if eligible.
    Returns a tuple (status, message).
    """
    payment = getattr(order, 'payment', None)
    
    if not payment:
        return "none", "No payment found for this order."
        
    if payment.method != 'razorpay':
        return "none", f"Payment method is {payment.method}, not razorpay."
        
    if payment.status not in ['success', 'completed']:
        return "none", f"Payment status is {payment.status}, cannot refund."
        
    if not payment.payment_id:
        return "none", "No Razorpay payment ID found."

    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        amount_in_paise = int(payment.amount * 100)
        
        refund = client.payment.refund(payment.payment_id, {
            "amount": amount_in_paise,
            "notes": {
                "order_id": order.order_id,
                "reason": reason
            }
        })
        
        payment.status = 'refunded'
        resp_dict = payment.gateway_response or {}
        resp_dict['refund_id'] = refund.get('id')
        resp_dict['refunded_at'] = datetime.now(datetime_timezone.utc).isoformat()
        payment.gateway_response = resp_dict
        payment.save()
        
        # Add tracking note for refund
        OrderTracking.objects.create(
            order=order,
            status="refunded",
            description=f"Razorpay refund of INR {payment.amount:.2f} initiated. Refund ID: {refund.get('id')}"
        )
        
        logger.info(f"Razorpay automatic refund successful for order {order.order_id}.")
        return "processed", f"Refund of INR {payment.amount:.2f} initiated successfully."
        
    except Exception as refund_err:
        error_msg = str(refund_err)
        logger.error(f"Razorpay automatic refund failed for order {order.order_id}: {error_msg}")
        return "failed", f"Automatic refund failed: {error_msg}"
