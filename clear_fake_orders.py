import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')
django.setup()

from store.models import Order, Payment, OrderItem, OrderTracking, Complaint, AdminDashboardStats

def clear_fake_data():
    print("WARNING: This script will delete ALL orders, payments, order tracking, complaints, and dashboard statistics.")
    print("This is meant to wipe out all dummy/fake data so your live dashboard stats reset to 0.")
    print("Your products and users will NOT be affected.")
    
    confirm = input("\nType 'YES' to confirm deletion: ")
    if confirm != 'YES':
        print("Aborting.")
        sys.exit(0)
    
    print("\nDeleting Admin Dashboard Stats...")
    stats_count, _ = AdminDashboardStats.objects.all().delete()
    print(f"Deleted {stats_count} dashboard stat records.")

    print("Deleting Complaints...")
    complaints_count, _ = Complaint.objects.all().delete()
    print(f"Deleted {complaints_count} complaints.")

    print("Deleting Order Tracking...")
    tracking_count, _ = OrderTracking.objects.all().delete()
    print(f"Deleted {tracking_count} tracking records.")

    print("Deleting Order Items...")
    items_count, _ = OrderItem.objects.all().delete()
    print(f"Deleted {items_count} order items.")

    print("Deleting Payments...")
    payments_count, _ = Payment.objects.all().delete()
    print(f"Deleted {payments_count} payments.")

    print("Deleting Orders...")
    orders_count, _ = Order.objects.all().delete()
    print(f"Deleted {orders_count} orders.")

    print("\nSUCCESS! All fake order data has been deleted. Your dashboard will now display real live data based on new orders.")

if __name__ == '__main__':
    clear_fake_data()
