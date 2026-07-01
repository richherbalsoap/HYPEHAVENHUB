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
            shiprocket_items.append({
                "name": item.product_name,
                "sku": f"JHMK-{item.product.id}-{item.variant.id if item.variant else 'default'}",
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
            if "16" in item.product_name or "16-piece" in getattr(item.product.category, 'slug', ''):
                weight = 0.7
                length = 20
                width = 20
                height = 12

        payload = {
            "order_id": order.order_id,
            "order_date": order.created_at.strftime("%Y-%m-%d %H:%M"),
            "pickup_location": getattr(settings, 'SHIPROCKET_PICKUP_LOCATION', 'Primary'),
            "billing_customer_name": customer_name,
            "billing_last_name": "",
            "billing_address": address.address_line1,
            "billing_address_2": address.address_line2 or "",
            "billing_city": address.city,
            "billing_pincode": address.pincode,
            "billing_state": address.state,
            "billing_country": "India",
            "billing_email": order.user.email,
            "billing_phone": address.phone,
            "shipping_is_billing": True,
            "order_items": shiprocket_items,
            "payment_method": "Prepaid" if order.payment.status == 'completed' else "COD",
            "sub_total": float(order.subtotal),
            "length": length,
            "width": width,
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
