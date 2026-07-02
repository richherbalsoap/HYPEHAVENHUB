# Quick Setup Guide - Admin Panel

## 🚀 Getting Started (5 Minutes)

### Step 1: Make Your User Admin
```bash
python manage.py shell
```

```python
from store.models import User

# Replace 'your@email.com' with your actual email
user = User.objects.get(email='your@email.com')
user.is_staff = True
user.is_superuser = True
user.save()

print("Admin access granted!")
```

### Step 2: Login & Visit Admin Dashboard
1. Go to `http://localhost:8000/auth/login/`
2. Login with your credentials
3. Navigate to `http://localhost:8000/admin/dashboard/`

---

## 📋 What You Can Do Now

### ✅ Product Management
**Add a Product:**
1. Click "Dashboard" → "Products" 
2. Or go to `/admin/products/`
3. Click "Add New Product" button
4. Fill in:
   - Product name
   - Brand
   - Category
   - Price & discount
   - Description
   - **Video URL** (YouTube link) ← NEW
   - **Material** (e.g., 18K Gold) ← NEW
   - **Warranty** (e.g., 1 Year) ← NEW
   - Weight
   - Upload images

### ✅ View & Filter Orders
1. Go to `/admin/orders/`
2. Search by order ID or email
3. Filter by status (pending, shipped, delivered, etc.)
4. Click "View" to see order details

### ✅ Manage Complaints
**View Complaints:**
1. Go to `/admin/complaints/`
2. Filter by status (open, in_progress, resolved)

**Respond to Complaint:**
1. Click on complaint ID
2. Add your response
3. Update status
4. Assign to team member (if needed)
5. Save

### ✅ View Sales Reports
1. Go to `/admin/reports/`
2. Select time period (7/30/90/365 days)
3. See:
   - Total revenue
   - Top products
   - Top categories
   - Daily sales trend
   - Return rate

---

## 👥 User Complaint System

### For End Users (Customers):
1. Login to store
2. Go to `/complaints/submit/` (or click link in account menu)
3. Fill complaint form:
   - Select complaint type
   - (Optional) Select related order
   - Add subject & description
4. Submit

### For Admins (Managing Complaints):
1. Go to `/admin/dashboard/`
2. See recent complaints in widget
3. Click on complaint ID
4. Add response message
5. Update status:
   - Open → In Progress → Resolved → Closed
6. Set priority (Low/Medium/High)
7. Assign to team member
8. Save

---

## 🔧 Key URLs

### Admin Panel:
```
/admin/dashboard/              Dashboard (overview)
/admin/products/               Product list
/admin/products/create/        Add new product
/admin/products/<id>/edit/     Edit product
/admin/products/<id>/delete/   Delete product
/admin/orders/                 View orders
/admin/complaints/             View all complaints
/admin/complaints/<id>/        Complaint detail
/admin/reports/                Analytics & reports
```

### User Complaints:
```
/complaints/submit/            Submit complaint
/complaints/                   My complaints
/complaints/<id>/              Complaint detail
```

---

## 💡 Tips

1. **Product Images:** Add main product image by uploading in product form
2. **Video Links:** Paste full YouTube URL (e.g., https://www.youtube.com/watch?v=xxx)
3. **Categories:** Must create category first before adding product
4. **Complaints:** Customers can track their complaints in real-time
5. **Reports:** Select different time periods to analyze trends

---

## ❓ Troubleshooting

### "Admin access required" error?
→ Make sure you set `is_staff = True`

### Can't see products?
→ Go to `/admin/products/` and add a product

### Form not submitting?
→ Check browser console for validation errors

### Server not running?
```bash
python manage.py runserver
```

---

## 📞 Support

For detailed documentation, see `ADMIN_GUIDE.md`

---

**Happy managing! 🎉**
