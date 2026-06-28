# HYPEHAVENHUB - Premium Makeup E-commerce Platform

## Overview
A Myntra-level, production-ready makeup e-commerce website built with Django targeting women aged 18–35. Luxury fashion-brand feel with Pink + Black + White color palette.

## Tech Stack
- **Backend**: Python 3.11 + Django 5.2
- **API**: Django REST Framework + SimpleJWT
- **Frontend**: HTML5, CSS3, Bootstrap 5, Vanilla JS
- **Database**: PostgreSQL (via Replit DB)
- **Media**: Django media storage (local)
- **Static**: WhiteNoise

## Architecture
```
glamour_store/   # Django project config
  settings.py   # All settings (DB, Auth, JWT, etc.)
  urls.py       # Root URL config
store/           # Main app
  models.py     # All database models
  views.py      # All view logic
  admin.py      # Customized Django admin
  forms.py      # Form classes
  urls.py       # App URL routes
  context_processors.py  # Cart/wishlist counts
templates/
  base.html     # Master layout with nav/footer
  store/        # All storefront templates
  auth/         # Auth flow templates
static/
  css/style.css # Complete luxury CSS
  js/main.js    # All JS (cart, wishlist, variants)
media/          # Uploaded files
```

## Database Models
- **User** (CustomUser with email auth, OTP, profile photo)
- **Category** & **SubCategory**
- **Brand**
- **Product** (with variants, images, flash sale, featured, etc.)
- **ProductImage** & **ProductVariant** (shade, color, size, finish, stock)
- **Cart** & **CartItem** (session-based for guests, user-linked for auth)
- **Coupon** (percent/flat discounts with validity)
- **Order** & **OrderItem** (with unique GS-prefixed IDs)
- **Payment** (UPI, Card, COD, Wallet — pending/success/failed)
- **OrderTracking** (timeline events)
- **Review** & **ReviewImage** (verified purchase, star ratings)
- **Wishlist**
- **Address** (multiple per user)
- **ReturnRequest** (with reason selection and status)
- **Notification**

## Key Features
- Full auth: signup, OTP verification, login, forgot/reset password
- Product catalog with variants (shade, size, finish) & color swatches
- Cart: guest + user-merged, coupon apply, price breakdown
- Checkout with address selection + payment method
- Order tracking with visual timeline
- Wishlist, Reviews, Return requests
- Smart search with live suggestions
- Filters: category, brand, price, discount, finish
- Custom Django Admin with inline images, variants, analytics
- Flash sale countdown timer, new arrivals, bestsellers
- Mobile-first responsive design

## Admin Access
- URL: /admin/
- Email: admin@hypehavenhub.com
- Password: Admin@1234

## Coupon Codes
- `GLAM10` — 10% off (min ₹500, max ₹200 discount)
- `FLAT100` — ₹100 flat off (min ₹700)

## Run Command
```bash
python manage.py runserver 0.0.0.0:5000
```

## Environment Variables
- `DATABASE_URL`, `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` — PostgreSQL
- `SESSION_SECRET` — Django secret key (uses env or fallback)
- `DEBUG` — defaults to True

## Dependencies
django, djangorestframework, psycopg2-binary, Pillow, django-cors-headers, 
python-decouple, djangorestframework-simplejwt, crispy-bootstrap5, whitenoise, gunicorn
