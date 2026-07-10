export interface ProductVariant {
  id: string;
  shade_name: string;
  color_code: string;
  size: string;
  finish: string;
  sku: string;
  additional_price: number;
  stock: number;
  is_active: boolean;
}

export interface Review {
  id: string;
  userEmail: string;
  rating: number;
  title: string;
  body: string;
  isVerifiedPurchase: boolean;
  helpfulCount: number;
  createdAt: string;
}

export interface Product {
  id: string;
  name: string;
  slug: string;
  brand: string;
  category: string;
  description: string;
  short_description: string;
  ingredients: string;
  how_to_use: string;
  material: string;
  metal_purity: string;
  warranty: string;
  base_price: number;
  discount_percent: number;
  finish: string;
  is_active: boolean;
  is_featured: boolean;
  is_new_arrival: boolean;
  is_bestseller: boolean;
  display_image_url: string;
  secondary_image_url: string;
  gallery_urls: string[];
  variants: ProductVariant[];
  reviews: Review[];
}

export interface Address {
  id: string;
  type: 'home' | 'work' | 'other';
  full_name: string;
  phone: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  pincode: string;
  is_default: boolean;
}

export interface CartItem {
  id: string;
  productId: string;
  productName: string;
  productSlug: string;
  display_image_url: string;
  variantId?: string;
  variantLabel?: string;
  quantity: number;
  basePrice: number;
  sellingPrice: number;
}

export interface OrderItem {
  id: string;
  productId: string;
  productName: string;
  variantLabel: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
}

export interface Order {
  id: string;
  order_id: string;
  status: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'out_for_delivery' | 'delivered' | 'cancelled';
  subtotal: number;
  discount_amount: number;
  delivery_charge: number;
  grand_total: number;
  coupon_code?: string;
  items: OrderItem[];
  address: Address;
  created_at: string;
  tracking: {
    status: string;
    description: string;
    created_at: string;
  }[];
}

export interface Complaint {
  id: string;
  complaint_id: string;
  complaint_type: 'product_quality' | 'delivery' | 'payment' | 'account' | 'website' | 'other';
  subject: string;
  description: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  admin_response: string;
  priority: 'low' | 'medium' | 'high';
  created_at: string;
}

export interface Notification {
  id: string;
  type: 'order' | 'offer' | 'general';
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface User {
  email: string;
  phone?: string;
  is_email_verified: boolean;
  addresses: Address[];
}
