import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class ShiprocketService:
    """
    Shiprocket API Service wrapper to handle authentication and shipment bookings.
    """
    BASE_URL = "https://apiv2.shiprocket.in/v1/external"

    @classmethod
    def _get_token(cls):
        """
        Authenticate with Shiprocket and retrieve JWT token.
        """
        api_key = getattr(settings, 'SHIPROCKET_API_KEY', '')
        if api_key:
            return api_key
            
        email = getattr(settings, 'SHIPROCKET_EMAIL', '')
        password = getattr(settings, 'SHIPROCKET_PASSWORD', '')

        if not email or not password or "example.com" in email:
            logger.warning("Shiprocket credentials are not configured or still placeholders.")
            return None

        try:
            url = f"{cls.BASE_URL}/auth/login"
            payload = {"email": email, "password": password}
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json().get("token")
            else:
                logger.error(f"Shiprocket auth failed: {response.text}")
        except Exception as e:
            logger.error(f"Error authenticating with Shiprocket: {str(e)}")
        return None

    @classmethod
    def create_shipment(cls, order):
        """
        Creates a new order shipment in Shiprocket.
        """
        token = cls._get_token()
        if not token:
            logger.warning(f"Skipping Shiprocket booking for order {order.order_id} - no valid API token.")
            return None

        # Build address details
        address = order.address
        customer_name = f"{order.user.first_name} {order.user.last_name}".strip() or order.user.email

        # Prepare order items for Shiprocket
        shiprocket_items = []
        for item in order.items.all():
            product_id = item.product.id if item.product else 'UNKNOWN'
            variant_id = item.variant.id if item.variant else 'default'
            shiprocket_items.append({
                "name": item.product_name,
                "sku": f"JHMK-{product_id}-{variant_id}",
                "units": item.quantity,
                "selling_price": float(item.unit_price),
                "discount": 0.0,
                "tax": 0.0,
            })

        # Set default dimensions/weight based on box set category
        # A typical jhumka box weighs around 0.5kg for 12pcs, and 0.7kg for 16pcs
        weight = 0.5
        length = 15
        width = 15
        height = 10

        # Attempt to detect package properties from items
        for item in order.items.all():
            cat_slug = getattr(getattr(item.product, 'category', None), 'slug', '') if item.product else ''
            if "16" in item.product_name or "16-piece" in cat_slug:
                weight = 0.7
                length = 20
                width = 20
                height = 12

        # Sanitize phone to exactly 10 digits for Shiprocket
        phone_digits = ''.join(filter(str.isdigit, str(address.phone)))
        if len(phone_digits) > 10:
            phone_digits = phone_digits[-10:]
        if len(phone_digits) < 10 or not phone_digits[0] in ['6', '7', '8', '9'] or phone_digits == '9999999999':
            phone_digits = '9876543210' # fallback for test garbage data

        # Sanitize pincode to exactly 6 digits
        pincode_digits = ''.join(filter(str.isdigit, str(address.pincode)))[:6]
        if len(pincode_digits) < 6:
            pincode_digits = '110001' # fallback for test garbage data

        payload = {
            "order_id": order.order_id,
            "order_date": order.created_at.strftime("%Y-%m-%d %H:%M"),
            "pickup_location": getattr(settings, 'SHIPROCKET_PICKUP_LOCATION', 'Primary'),
            "billing_customer_name": customer_name,
            "billing_last_name": "",
            "billing_address": address.address_line1,
            "billing_address_2": address.address_line2 or "",
            "billing_city": address.city,
            "billing_pincode": pincode_digits,
            "billing_state": address.state,
            "billing_country": "India",
            "billing_email": order.user.email,
            "billing_phone": phone_digits,
            "shipping_is_billing": True,
            "order_items": shiprocket_items,
            "payment_method": "Prepaid" if order.payment.status == 'completed' else "COD",
            "sub_total": float(order.subtotal),
            "length": length,
            "breadth": width,
            "height": height,
            "weight": weight
        }

        try:
            url = f"{cls.BASE_URL}/orders/create/adhoc"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code in [200, 201]:
                res_data = response.json()
                shipment_id = res_data.get("shipment_id")
                logger.info(f"Shiprocket order created successfully. Shipment ID: {shipment_id}")
                return shipment_id
            else:
                logger.error(f"Shiprocket order creation failed: {response.text}")
        except Exception as e:
            logger.error(f"Error booking Shiprocket delivery: {str(e)}")
        return None
