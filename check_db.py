import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')
django.setup()

from store.models import OrderTracking

try:
    failed_trackings = OrderTracking.objects.filter(status='shiprocket_failed').order_by('-created_at')[:5]
    if not failed_trackings.exists():
        print("No shiprocket_failed tracking found in DB.")
    for item in failed_trackings:
        print(f"Order: {item.order_id}, Status: {item.status}, Time: {item.created_at}")
except Exception as e:
    print(f"Database check note: {e}")


