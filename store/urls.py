from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('brand/<slug:slug>/', views.brand_products, name='brand_products'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),

    path('auth/signup/', views.signup_view, name='signup'),
    path('auth/verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('auth/reset-otp/', views.reset_otp_view, name='reset_otp'),
    path('auth/reset-password/', views.reset_password_view, name='reset_password'),

    path('profile/', views.profile_view, name='profile'),
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/<int:pk>/edit/', views.edit_address, name='edit_address'),
    path('addresses/<int:pk>/delete/', views.delete_address, name='delete_address'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('cart/coupon/remove/', views.remove_coupon, name='remove_coupon'),

    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),

    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/place-order/', views.place_order, name='place_order'),

    path('orders/', views.order_list, name='order_list'),
    path('orders/<str:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<str:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('orders/<str:order_id>/return/', views.return_request_view, name='return_request'),

    path('notifications/', views.notifications_view, name='notifications'),
    path('api/variant/<int:variant_id>/', views.get_variant_info, name='variant_info'),
]
