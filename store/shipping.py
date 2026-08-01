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
    def _get_token(cls, return_error=False):
        """
        Authenticate with Shiprocket and retrieve JWT token.

        NOTE: Shiprocket's v1 external API (the one this whole file talks to)
        does NOT support a static "API key" as a Bearer token. The only way
        to get a valid token is by logging in with an email + password
        (either your main account, or a dedicated "API User" created under
        Shiprocket > Settings > API in your dashboard) against /auth/login.
        SHIPROCKET_API_KEY is kept here only for backwards-compatibility in
        case Shiprocket ever ships real API keys for this endpoint - if it's
        not a real JWT, using it directly will make every request fail with
        401 Unauthorized, and that failure will look exactly like "nothing
        happens" from the website's point of view.
        """
        api_key = (getattr(settings, 'SHIPROCKET_API_KEY', '') or '').strip()
        email = (getattr(settings, 'SHIPROCKET_EMAIL', '') or '').strip()
        password = (getattr(settings, 'SHIPROCKET_PASSWORD', '') or '').strip()

        if api_key:
            if return_error:
                return api_key, None
            return api_key

        if not email or not password or "example.com" in email:
            msg = ("Shiprocket credentials are not configured. Set SHIPROCKET_EMAIL and "
                   "SHIPROCKET_PASSWORD (your Shiprocket API User email/password) in your "
                   "environment variables.")
            logger.warning(msg)
            if return_error:
                return None, msg
            return None

        try:
            url = f"{cls.BASE_URL}/auth/login"
            payload = {"email": email, "password": password}
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                token = response.json().get("token")
                if not token:
                    msg = f"Shiprocket login succeeded but no token in response: {response.text[:200]}"
                    logger.error(msg)
                    if return_error:
                        return None, msg
                    return None
                if return_error:
                    return token, None
                return token
            else:
                msg = f"Shiprocket auth failed ({response.status_code}): {response.text[:300]}"
                logger.error(msg)
                if return_error:
                    return None, msg
        except Exception as e:
            msg = f"Error authenticating with Shiprocket: {str(e)}"
            logger.error(msg)
            if return_error:
                return None, msg
        return None

    @classmethod
    def create_shipment(cls, order):
        """
        Creates a new order shipment in Shiprocket.
        """
        token = cls._get_token()
        if not token:
            logger.warning(f"Skipping Shiprocket booking for order {order.order_id} - no valid API token.")
            return None, "No valid API token configured."

        # Build address details
        address = order.address
        if not address:
            logger.warning(f"Skipping Shiprocket booking for order {order.order_id} - missing shipping address.")
            return None, "Order is missing shipping address."
            
        customer_name = f"{order.user.first_name} {order.user.last_name}".strip() or order.user.email

        # Determine billing country dynamically from user profile, default to "India"
        country_name = "India"
        profile = getattr(order.user, 'userprofile', None)
        if profile and profile.country:
            country_name = profile.country.name

        # Prepare order items for Shiprocket
        shiprocket_items = []
        is_international = country_name.lower() != "india"

        for item in order.items.all():
            product_id = item.product.id if item.product else 'UNKNOWN'
            variant_id = item.variant.id if item.variant else 'default'
            
            # Extract material details from product model
            product_material = item.product.material if (item.product and item.product.material) else "Alloy Metal"
            p_name = getattr(item, 'personalization_name', '') or ''
            if not p_name and order.notes and 'Personalisation' in order.notes:
                p_name = order.notes.replace('Personalisation:', '').strip()
            
            # If international order, declare clearly as Imitation Jewelry / Non-Precious Metal / Sample
            if is_international:
                item_name = f"{item.product_name} (Imitation Jewelry - Non-Precious Metal: {product_material}) - SAMPLE"
            else:
                item_name = item.product_name

            if p_name:
                item_name += f" [Name: {p_name}]"

            item_payload = {
                "name": item_name[:250],  # Ensure length limit
                "sku": f"JHMK-{product_id}-{variant_id}",
                "units": item.quantity,
                "selling_price": float(item.unit_price),
                "discount": 0.0,
                "tax": 0.0,
                "hsn": "71179090"  # Standard HSN for base metal imitation jewelry
            }
            shiprocket_items.append(item_payload)

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

        # Sanitize phone
        phone_digits = ''.join(filter(str.isdigit, str(address.phone)))
        if country_name.lower() == "india":
            # Sanitize to exactly 10 digits for India
            if len(phone_digits) > 10:
                phone_digits = phone_digits[-10:]
            if len(phone_digits) < 10 or not phone_digits[0] in ['6', '7', '8', '9'] or phone_digits == '9999999999':
                phone_digits = '9876543210' # fallback for test garbage data
        else:
            # For international, keep digits as-is, ensure it's not empty
            if not phone_digits:
                phone_digits = '9876543210'

        # Sanitize pincode
        if country_name.lower() == "india":
            # Sanitize to exactly 6 digits for India
            pincode_digits = ''.join(filter(str.isdigit, str(address.pincode)))[:6]
            if len(pincode_digits) < 6:
                pincode_digits = '110001' # fallback for test garbage data
        else:
            # For international, keep alphanumeric zip/pincode as-is (e.g., SW1A 1AA, 90210)
            pincode_digits = str(address.pincode).strip()
            if not pincode_digits:
                pincode_digits = '90210' # default fallback zip

        pickup_location = (getattr(settings, 'SHIPROCKET_PICKUP_LOCATION', 'Primary') or 'Primary').strip()
        channel_id = (getattr(settings, 'SHIPROCKET_CHANNEL_ID', '') or '').strip()

        payload = {
            "order_id": order.order_id,
            "order_date": order.created_at.strftime("%Y-%m-%d %H:%M"),
            "pickup_location": pickup_location,
            "billing_customer_name": customer_name,
            "billing_last_name": "",
            "billing_address": address.address_line1,
            "billing_address_2": f"{address.address_line2}, {address.town}".strip(", ") if getattr(address, 'town', None) else (address.address_line2 or ""),
            "billing_city": address.city,
            "billing_pincode": pincode_digits,
            "billing_state": address.state,
            "billing_country": country_name,
            "billing_email": order.user.email,
            "billing_phone": phone_digits,
            "shipping_is_billing": True,
            "order_items": shiprocket_items,
            "payment_method": "Prepaid" if order.payment.status in ['success', 'completed'] else "COD",
            "sub_total": float(order.subtotal),
            "length": length,
            "breadth": width,
            "height": height,
            "weight": weight
        }

        # Only send channel_id if actually configured. Sending an empty string
        # here makes Shiprocket reject the whole order on some accounts.
        if channel_id:
            payload["channel_id"] = channel_id

        # Add comment with personalisation details
        pers_details = [f"{item.product_name}: {item.personalization_name}" for item in order.items.all() if getattr(item, 'personalization_name', '')]
        if not pers_details and order.notes and "Personalisation" in order.notes:
            pers_details = [order.notes]

        comment_parts = []
        if is_international:
            comment_parts.append("SAMPLE ONLY - IMITATION JEWELRY (NON-PRECIOUS METAL). NO COMMERCIAL VALUE. FOR CUSTOMS CLEARANCE.")
        if pers_details:
            comment_parts.append("PERSONALISATION: " + ", ".join(pers_details))
        if comment_parts:
            payload["comment"] = " | ".join(comment_parts)[:500]

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
                return shipment_id, None
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    res_json = response.json()
                    if isinstance(res_json, dict):
                        msg = res_json.get("message") or res_json.get("error")
                        errors = res_json.get("errors")
                        if msg:
                            error_msg = str(msg)
                        if errors:
                            error_msg += f" Details: {errors}"
                except Exception:
                    error_msg = response.text[:300]

                logger.error(f"Shiprocket order creation failed for order {order.order_id}: {error_msg}")
                return None, error_msg
        except Exception as e:
            error_msg = str(e)[:300]
            logger.error(f"Error booking Shiprocket delivery: {str(e)}")
            return None, error_msg

    @classmethod
    def cancel_shipment(cls, order):
        """
        Cancels an order/shipment in Shiprocket via API.
        POST /orders/cancel with payload {"ids": [order_id or shipment_id]}
        """
        token = cls._get_token()
        if not token:
            logger.warning(f"Skipping Shiprocket cancellation for order {order.order_id} - no valid API token.")
            return False, "No valid API token configured."

        ids_to_cancel = []
        if getattr(order, 'shipping_tracking_id', None):
            tracking_id = str(order.shipping_tracking_id).strip()
            if tracking_id.isdigit():
                ids_to_cancel.append(int(tracking_id))
            elif tracking_id:
                ids_to_cancel.append(tracking_id)

        if order.order_id and order.order_id not in ids_to_cancel:
            ids_to_cancel.append(order.order_id)

        if not ids_to_cancel:
            return False, "No tracking or order ID available to cancel."

        try:
            url = f"{cls.BASE_URL}/orders/cancel"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            payload = {"ids": ids_to_cancel}
            logger.info(f"Triggering Shiprocket order cancellation for order {order.order_id}: {payload}")
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code in [200, 201]:
                res_data = response.json()
                logger.info(f"Shiprocket cancellation succeeded for order {order.order_id}: {res_data}")
                msg = res_data.get("message") or res_data.get("data") or "Order cancelled successfully in Shiprocket."
                return True, str(msg)
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:300]}"
                logger.error(f"Shiprocket order cancellation failed for {order.order_id}: {error_msg}")
                return False, error_msg
        except Exception as e:
            error_msg = str(e)[:300]
            logger.error(f"Error cancelling order in Shiprocket ({order.order_id}): {error_msg}")
            return False, error_msg

    @classmethod
    def verify_pincode_city(cls, pincode, city, state=None):
        """
        Validates if pincode matches city/district using Postal Pincode API.
        Returns tuple: (is_valid, official_district, official_state, message)
        """
        pincode = str(pincode).strip()
        city = str(city).strip()
        if not pincode or len(pincode) < 6:
            return False, None, None, "Invalid pincode length (must be 6 digits)."

        try:
            url = f"https://api.postalpincode.in/pincode/{pincode}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data and data[0].get('Status') == 'Success':
                    post_offices = data[0].get('PostOffice', []) or []
                    districts = {po.get('District', '').strip().lower() for po in post_offices if po.get('District')}
                    names = {po.get('Name', '').strip().lower() for po in post_offices if po.get('Name')}
                    off_district = post_offices[0].get('District', '') if post_offices else ''
                    off_state = post_offices[0].get('State', '') if post_offices else ''

                    city_lower = city.lower()
                    if city_lower in districts or city_lower in names or any(d in city_lower or city_lower in d for d in districts if d):
                        return True, off_district, off_state, "Pincode and City match."
                    else:
                        return False, off_district, off_state, f"Pincode {pincode} belongs to district '{off_district}' ({off_state}), which does not match city '{city}'."
                elif data and data[0].get('Status') == 'Error':
                    return False, None, None, f"Pincode {pincode} is not a valid Indian Postal pincode."
        except Exception as e:
            logger.warning(f"Postal pincode API verification skipped due to error: {e}")

        return True, city, state or '', "Validation skipped."

    @classmethod
    def test_connection(cls):
        """
        Read-only diagnostic check. Does NOT create any order in Shiprocket.
        Returns a dict describing exactly what is configured, whether login
        works, and (if login works) which pickup location nicknames exist on
        the account - so a mismatched SHIPROCKET_PICKUP_LOCATION can be
        spotted immediately instead of guessed at.
        """
        result = {
            'api_key_configured': bool((getattr(settings, 'SHIPROCKET_API_KEY', '') or '').strip()),
            'email_configured': bool((getattr(settings, 'SHIPROCKET_EMAIL', '') or '').strip()),
            'password_configured': bool((getattr(settings, 'SHIPROCKET_PASSWORD', '') or '').strip()),
            'channel_id_configured': bool((getattr(settings, 'SHIPROCKET_CHANNEL_ID', '') or '').strip()),
            'configured_pickup_location': (getattr(settings, 'SHIPROCKET_PICKUP_LOCATION', 'Primary') or 'Primary').strip(),
            'auth_success': False,
            'auth_error': None,
            'pickup_locations_on_account': [],
            'pickup_location_match': None,
            'pickup_fetch_error': None,
        }

        token, auth_error = cls._get_token(return_error=True)
        result['auth_error'] = auth_error
        result['auth_success'] = bool(token)

        if not token:
            return result

        try:
            url = f"{cls.BASE_URL}/settings/company/pickup"
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                addresses = (data.get("data", {}) or {}).get("shipping_address", []) or []
                names = [a.get("pickup_location") for a in addresses if a.get("pickup_location")]
                result['pickup_locations_on_account'] = names
                result['pickup_location_match'] = result['configured_pickup_location'] in names
            else:
                result['pickup_fetch_error'] = response.text[:500]
        except Exception as e:
            result['pickup_fetch_error'] = str(e)[:500]

        return result

    @classmethod
    def get_live_tracking(cls, tracking_id_or_order_id):
        """
        Fetches real-time live tracking details directly from Shiprocket API.
        Can track by AWB number or Order ID.
        """
        token = cls._get_token()
        if not token:
            return None, "No active Shiprocket API token."

        tracking_id_or_order_id = str(tracking_id_or_order_id).strip()
        if not tracking_id_or_order_id:
            return None, "No tracking code or order ID provided."

        headers = {"Authorization": f"Bearer {token}"}

        try:
            if tracking_id_or_order_id.isdigit():
                url = f"{cls.BASE_URL}/courier/track/awb/{tracking_id_or_order_id}"
            else:
                url = f"{cls.BASE_URL}/courier/track?order_id={tracking_id_or_order_id}"

            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                tracking_data = data.get("tracking_data", {}) or {}
                shipment_track = tracking_data.get("shipment_track", [])
                
                if isinstance(shipment_track, list) and len(shipment_track) > 0:
                    track_info = shipment_track[0]
                    scans = track_info.get("scans", []) or []
                    
                    live_events = []
                    for scan in scans:
                        activity = scan.get("activity") or scan.get("status") or "Package update"
                        location = scan.get("location") or scan.get("city") or ""
                        date_str = scan.get("date") or scan.get("updated_at") or ""
                        desc = f"{activity}" + (f" - {location}" if location else "")
                        live_events.append({
                            'description': desc,
                            'created_at_display': date_str,
                            'location': location,
                            'activity': activity
                        })
                    
                    return {
                        'courier_name': track_info.get('courier_name') or tracking_data.get('courier_name') or 'Shiprocket Courier',
                        'current_status': track_info.get('current_status') or tracking_data.get('track_status') or 'Booked',
                        'awb_code': track_info.get('awb_code') or tracking_id_or_order_id,
                        'origin': track_info.get('origin', ''),
                        'destination': track_info.get('destination', ''),
                        'etd': track_info.get('etd') or tracking_data.get('etd') or '',
                        'scans': live_events,
                    }, None
        except Exception as e:
            logger.error(f"Error fetching live tracking from Shiprocket API: {e}")
            return None, str(e)

        return None, "No tracking data found on Shiprocket."
