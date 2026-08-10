import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')
django.setup()

from store.models import OrderTracking

failed_tracks = OrderTracking.objects.filter(status='shiprocket_failed').order_by('-created_at')[:5]
if not failed_tracks:
    print("No shiprocket_failed tracking found.")
for track in failed_tracks:
    print(f"Order: {track.order.order_id} at {track.created_at}")
    print(f"Error: {track.description}")
    print("-" * 50)
