from django.urls import path
from django.views.generic import RedirectView
from . import views
from . import admin_views
from . import magic_checkout_api

urlpatterns = [
    # Home & Products
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('brand/<slug:slug>/', views.brand_products, name='brand_products'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    path('contact/', views.contact_us, name='contact_us'),
    path('about/', views.about_us, name='about_us'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),

    # Authentication
    path('auth/signup/', views.signup_view, name='signup'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('auth/forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('auth/reset-otp/', views.reset_otp_view, name='reset_otp'),
    path('auth/reset-password/', views.reset_password_view, name='reset_password'),

    # User Profile & Settings
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),

    # Addresses
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/edit/<int:pk>/', views.edit_address, name='edit_address'),
    path('addresses/delete/<int:pk>/', views.delete_address, name='delete_address'),

    # Cart & Checkout
    path('cart/', views.cart_view, name='cart'),
    path('cart/drawer/', views.cart_drawer_view, name='cart_drawer'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('cart/coupon/remove/', views.remove_coupon, name='remove_coupon'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/place-order/', views.place_order, name='place_order'),
    path('checkout/verify-payment/', views.verify_payment, name='verify_payment'),

    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('order-success/<str:order_id>/', views.order_success_animation, name='order_success_animation'),
    path('orders/<str:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<str:order_id>/assign/', views.assign_guest_order, name='assign_guest_order'),
    path('orders/<str:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('orders/<str:order_id>/return/', views.return_request_view, name='return_request'),

    # API / Utils
    path('api/variant-info/<int:variant_id>/', views.get_variant_info, name='get_variant_info'),
    path('api/quick-view/<int:product_id>/', views.quick_view, name='quick_view'),
    path('api/set-country/', views.set_country_session, name='set_country_session'),
    path('api/set-language/', views.set_language, name='set_language'),
    path('api/pincode-lookup/', views.pincode_lookup, name='pincode_lookup'),
    path('run-migrations/', views.run_migrations_view, name='run_migrations'),
    path('api/razorpay-webhook/', views.razorpay_webhook, name='razorpay_webhook'),
    path('api/magic-checkout/shipping/', magic_checkout_api.shipping_info, name='magic_checkout_shipping'),
    path('api/magic-checkout/promotions/', magic_checkout_api.get_promotions, name='magic_checkout_get_promotions'),
    path('api/magic-checkout/promotions/apply/', magic_checkout_api.apply_promotion, name='magic_checkout_apply_promotion'),

    # Admin Panel
    path('admin/', RedirectView.as_view(pattern_name='admin_dashboard', permanent=False), name='admin_root'),
    path('admin/login/', admin_views.custom_admin_login, name='custom_admin_login'),
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    
    # Custom Admin: Site Settings & Hero Panels
    path('admin/site-settings/', admin_views.admin_site_settings, name='admin_site_settings'),
    path('admin/hero-panels/', admin_views.admin_hero_panels, name='admin_hero_panels'),
    path('admin/hero-panels/create/', admin_views.admin_hero_panel_create, name='admin_hero_panel_create'),
    path('admin/hero-panels/<int:pk>/edit/', admin_views.admin_hero_panel_edit, name='admin_hero_panel_edit'),
    path('admin/hero-panels/<int:pk>/delete/', admin_views.admin_hero_panel_delete, name='admin_hero_panel_delete'),
    

    path('admin/products/', admin_views.admin_products, name='admin_products'),
    path('admin/products/create/', admin_views.admin_product_create, name='admin_product_create'),
    path('admin/products/<int:pk>/edit/', admin_views.admin_product_edit, name='admin_product_edit'),
    path('admin/products/<int:pk>/prices/', admin_views.admin_product_prices, name='admin_product_prices'),
    path('admin/products/images/<int:pk>/delete/', admin_views.admin_product_image_delete, name='admin_product_image_delete'),
    path('admin/products/aplus_images/<int:pk>/delete/', admin_views.admin_product_aplus_image_delete, name='admin_product_aplus_image_delete'),
    path('admin/products/<int:pk>/delete/', admin_views.admin_product_delete, name='admin_product_delete'),
    path('admin/orders/', admin_views.admin_orders, name='admin_orders'),
    path('admin/orders/<str:order_id>/', admin_views.admin_order_detail, name='admin_order_detail'),
    path('admin/complaints/', admin_views.admin_complaints, name='admin_complaints'),
    path('admin/complaints/<str:complaint_id>/', admin_views.admin_complaint_detail, name='admin_complaint_detail'),
    path('admin/reports/', admin_views.admin_reports, name='admin_reports'),
    path('admin/shiprocket-test/', admin_views.admin_shiprocket_test, name='admin_shiprocket_test'),
    path('admin/countries/', admin_views.admin_countries, name='admin_countries'),
    path('admin/countries/create/', admin_views.admin_country_create, name='admin_country_create'),
    path('admin/countries/<int:pk>/edit/', admin_views.admin_country_edit, name='admin_country_edit'),
    path('admin/countries/<int:pk>/delete/', admin_views.admin_country_delete, name='admin_country_delete'),
    path('admin/get-presigned-url/', admin_views.get_presigned_url, name='admin_get_presigned_url'),

    
    # User Complaints
    path('complaints/submit/', admin_views.submit_complaint, name='submit_complaint'),
    path('complaints/<str:complaint_id>/', admin_views.complaint_detail, name='complaint_detail'),
    path('complaints/', admin_views.user_complaints, name='user_complaints'),

    # Shiprocket Catalog Sync
    path('shiprocket/products/', views.shiprocket_fetch_products, name='sr_fetch_products'),
    path('shiprocket/collections/', views.shiprocket_fetch_collections, name='sr_fetch_collections'),
    path('shiprocket/collection-products/', views.shiprocket_fetch_collection_products, name='sr_fetch_collection_products'),

    # Shiprocket Checkout & Webhooks
    path('razorpay/checkout/initiate/', views.razorpay_direct_checkout, name='razorpay_direct_checkout'),
    path('shiprocket/webhook/order/', views.shiprocket_order_webhook, name='sr_order_webhook'),
]
