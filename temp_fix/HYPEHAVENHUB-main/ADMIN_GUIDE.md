# HYPEHAVENHUB - Admin Panel Guide

## 📊 Features Added

### 1. **Admin Dashboard**
- Overview of key metrics (revenue, orders, users, complaints)
- Quick stats cards showing performance
- Recent orders and complaints display
- Access: `/admin/dashboard/`

### 2. **Product Management**
- ✅ View all products with search & filtering
- ✅ Add new products with detailed information
- ✅ Edit existing products
- ✅ Delete products
- ✅ Enhanced fields:
  - Video URL (YouTube links)
  - Weight
  - Material
  - Warranty information
  - Discount percentage
  - Brand, Category, Sub-category

**Routes:**
- `/admin/products/` - List products
- `/admin/products/create/` - Add new product
- `/admin/products/<id>/edit/` - Edit product
- `/admin/products/<id>/delete/` - Delete product

### 3. **Order Management**
- View all orders with detailed information
- Filter orders by status
- Search by order ID or customer email
- Track order status changes
- Access: `/admin/orders/`

### 4. **Complaint Management**
**Admin Side:**
- View all complaints with filtering
- Respond to complaints
- Assign complaints to team members
- Set priority levels (Low, Medium, High)
- Update complaint status
- Access: `/admin/complaints/` → `/admin/complaints/<id>/`

**User Side:**
- Submit complaints with details
- View complaint status
- Receive admin responses
- Routes:
  - `/complaints/submit/` - Submit complaint
  - `/complaints/` - View my complaints
  - `/complaints/<id>/` - View complaint detail

### 5. **Sales Reports & Analytics**
- Daily, weekly, monthly, yearly revenue analysis
- Top selling products
- Top categories by sales
- Return rate statistics
- Average order value
- Customer purchase trends
- Access: `/admin/reports/`

## 🔐 Admin Access Control

### Authentication
- Admin panel requires `is_staff=True` on user account
- `@admin_required` decorator on all admin views
- Automatic redirect to login if not authenticated

### User Complaints
- Regular users can submit complaints
- Admins can view, respond, and update complaint status
- Complaints linked to orders for context

## 📋 Database Models

### New Models Created:
```python
1. Complaint
   - complaint_id (auto-generated)
   - user (ForeignKey)
   - order (ForeignKey, optional)
   - complaint_type (choices: product_quality, delivery, payment, etc.)
   - subject, description
   - status (open, in_progress, resolved, closed)
   - admin_response
   - priority (low, medium, high)
   - assigned_to (admin)
   - created_at, updated_at, resolved_at

2. AdminDashboardStats
   - date (auto)
   - total_orders, total_revenue
   - total_users, new_orders_today
   - total_products, returned_orders
   - total_complaints, open_complaints
```

### Enhanced Models:
```python
Product - Added fields:
- video_url
- weight
- material
- warranty
```

## 🎯 User Flows

### Admin Creating Product:
1. Go to `/admin/products/create/`
2. Fill in product details
3. Set price, discount, images
4. Add video, material, warranty info
5. Set as featured/bestseller if needed
6. Submit

### Handling Complaints:
**User:**
1. Click "Submit Complaint" (from account menu)
2. Select complaint type and related order
3. Describe issue in detail
4. Submit

**Admin:**
1. View complaints on dashboard
2. Click on complaint to open details
3. Add admin response
4. Update status and priority
5. Assign to team member if needed

### Viewing Analytics:
1. Go to `/admin/reports/`
2. Select time period (7, 30, 90, 365 days)
3. View:
   - Total sales & revenue
   - Top products & categories
   - Daily sales trend
   - Return rates

## 🛠️ Setup Instructions

### 1. **Make User Admin**
```python
python manage.py shell
>>> from store.models import User
>>> user = User.objects.get(email='admin@example.com')
>>> user.is_staff = True
>>> user.is_superuser = True
>>> user.save()
```

### 2. **Access Admin Panel**
- Login with admin account
- Navigate to `/admin/dashboard/`

### 3. **Manage Products**
- Add product with all details
- Upload images
- Add video links (YouTube)
- Set pricing & discounts

### 4. **Monitor Complaints**
- Check dashboard for open complaints
- Respond to user issues
- Update status as resolved

## 📱 Templates Created

**Admin Templates:**
- `admin/base.html` - Admin layout with sidebar
- `admin/dashboard.html` - Main dashboard
- `admin/products_list.html` - Product listing
- `admin/product_form.html` - Add/Edit product form
- `admin/product_confirm_delete.html` - Delete confirmation
- `admin/orders_list.html` - View orders
- `admin/complaints_list.html` - View all complaints
- `admin/complaint_detail.html` - Complaint detail & response
- `admin/reports.html` - Analytics & reports

**User Templates:**
- `store/complaint_form.html` - Submit complaint
- `store/complaints_list.html` - My complaints
- `store/complaint_detail.html` - Complaint detail

## 🔗 URL Patterns

```
Admin Routes:
/admin/dashboard/                    - Dashboard
/admin/products/                     - Products list
/admin/products/create/              - Create product
/admin/products/<id>/edit/           - Edit product
/admin/products/<id>/delete/         - Delete product
/admin/orders/                       - Orders list
/admin/complaints/                   - All complaints
/admin/complaints/<id>/              - Complaint detail
/admin/reports/                      - Analytics

User Routes:
/complaints/submit/                  - Submit complaint
/complaints/                         - My complaints
/complaints/<id>/                    - Complaint detail
```

## 🎨 Styling

- **Color Scheme:**
  - Primary: #8B5CF6 (Purple)
  - Secondary: #EC4899 (Pink)
  - Success: #10B981 (Green)
  - Warning: #F59E0B (Orange)
  - Danger: #EF4444 (Red)

- **Design Elements:**
  - Sidebar navigation
  - Stat cards with metrics
  - Responsive tables
  - Clean, modern UI
  - Bootstrap 5 framework

## 📝 Notes

1. **Database Migration:**
   - Run `python manage.py makemigrations`
   - Run `python manage.py migrate`

2. **Admin Creation:**
   - Create a superuser: `python manage.py createsuperuser`
   - Or set `is_staff=True` on existing user

3. **Complaint Auto-ID:**
   - Generates like: `CP1A2B3C4D`
   - Used for easy tracking

4. **Stats Cache:**
   - Dashboard stats are cached per day
   - Updates automatically each day

## ✨ Future Enhancements

- Email notifications for admin responses
- Export reports to PDF
- Multi-language support
- Advanced filtering options
- Bulk operations on products
- Customer segmentation
- Refund management
- Inventory alerts

---

**Last Updated:** June 2026
**Version:** 1.0
