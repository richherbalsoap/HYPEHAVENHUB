import os
import django

env_path = '.env.production'
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        if '=' in line:
            key, val = line.split('=', 1)
            val = val.strip().strip('"').strip("'")
            os.environ[key] = val

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')
django.setup()

from store.models import Order, Payment, OrderItem, OrderTracking, Complaint, AdminDashboardStats

print('Orders before:', Order.objects.count())

stats_count, _ = AdminDashboardStats.objects.all().delete()
complaints_count, _ = Complaint.objects.all().delete()
tracking_count, _ = OrderTracking.objects.all().delete()
items_count, _ = OrderItem.objects.all().delete()
payments_count, _ = Payment.objects.all().delete()
orders_count, _ = Order.objects.all().delete()

print('Orders after:', Order.objects.count())
print('SUCCESS DELETING FROM PROD!')
