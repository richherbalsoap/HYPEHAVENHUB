import express from 'express';
import path from 'path';
import { createServer as createViteServer } from 'vite';
import { Product, Order, Complaint, Review, Address } from './src/types';

const app = express();
const PORT = 3000;

app.use(express.json());

// ==========================================
// IN-MEMORY DATABASE & DATA SEEDING
// ==========================================

// Initial Seed Products
const SEED_PRODUCTS: Product[] = [
  {
    id: 'prod-1',
    name: '12 Piece Jhumka Box Set',
    slug: '12-piece-jhumka-box-set',
    brand: 'HYPEHAVENHUB',
    category: '12 Piece Jhumka Box Set',
    short_description: 'A ready box of 12 assorted jhumka pieces for daily, festive, and gifting use.',
    description: 'This 12 piece jhumka box set brings together assorted lightweight designs in one neat box. It is made for resellers, gifting, college wear, festive styling, and quick outfit matching. Each piece is individually wrapped to avoid scratches and arranged beautifully in a premium pink gifting box.',
    ingredients: 'Alloy base, enamel accents, faux pearls, crystal-style stones, and gold-tone polish. Keep away from perfume, sweat, and water.',
    how_to_use: 'Store every jhumka in the box after use. Mix the designs with kurtis, sarees, lehengas, and casual ethnic outfits.',
    material: 'Alloy base, Gold-tone polish',
    metal_purity: 'Handcrafted Traditional Jhumka Base',
    warranty: '6 Months Polish Warranty',
    base_price: 599,
    discount_percent: 10,
    finish: 'shimmer',
    is_active: true,
    is_featured: true,
    is_new_arrival: false,
    is_bestseller: true,
    display_image_url: 'https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=600&q=80', // Beautiful earrings image
    secondary_image_url: 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80',
    gallery_urls: [
      'https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=600&q=80',
      'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80',
      'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=600&q=80'
    ],
    variants: [
      {
        id: 'var-1a',
        shade_name: 'Classic Gold Assortment',
        color_code: '#d8ad4f',
        size: '12 Pieces',
        finish: 'shimmer',
        sku: 'SKU-12J-GLD',
        additional_price: 0,
        stock: 75,
        is_active: true
      }
    ],
    reviews: [
      {
        id: 'rev-1',
        userEmail: 'priya.sharma@gmail.com',
        rating: 5,
        title: 'Amazing Variety!',
        body: 'Absolutely loved the collection. All 12 pairs are distinct and gorgeous. Perfect for gifting or college wear!',
        isVerifiedPurchase: true,
        helpfulCount: 14,
        createdAt: '2026-06-15T10:00:00Z'
      },
      {
        id: 'rev-2',
        userEmail: 'neha12@yahoo.com',
        rating: 4,
        title: 'Great value for money',
        body: 'Very pretty jhumkas at a very affordable rate. Some pieces are extremely lightweight, which is great for long wear.',
        isVerifiedPurchase: true,
        helpfulCount: 5,
        createdAt: '2026-06-20T14:30:00Z'
      }
    ]
  },
  {
    id: 'prod-2',
    name: '16 Piece Jhumka Box Set',
    slug: '16-piece-jhumka-box-set',
    brand: 'HYPEHAVENHUB',
    category: '16 Piece Jhumka Box Set',
    short_description: 'A fuller 16 piece jhumka box set with assorted colors and festive designs.',
    description: 'This 16 piece jhumka box set gives more variety in one premium box, with assorted colors, pearl looks, and festive-ready patterns for daily sales, gifting, and outfit styling. Features heavier ethnic motifs, vibrant enamel artwork (Meenakari), and premium hanging bead drops.',
    ingredients: 'Alloy base, enamel accents, faux pearls, crystal-style stones, and gold-tone polish. Keep dry and store inside the box.',
    how_to_use: 'Choose a pair by outfit color, then place it back in its slot after use. Ideal for boutique display, gifting, and regular festive wear.',
    material: 'Premium Alloy, Faux Pearls, Kundan Crystals',
    metal_purity: 'Handcrafted Traditional Premium Base',
    warranty: '6 Months Polish Warranty',
    base_price: 799,
    discount_percent: 12,
    finish: 'glossy',
    is_active: true,
    is_featured: true,
    is_new_arrival: true,
    is_bestseller: false,
    display_image_url: 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=600&q=80',
    secondary_image_url: 'https://images.unsplash.com/photo-1635767798638-3e25273a8236?auto=format&fit=crop&w=600&q=80',
    gallery_urls: [
      'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=600&q=80',
      'https://images.unsplash.com/photo-1635767798638-3e25273a8236?auto=format&fit=crop&w=600&q=80',
      'https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?auto=format&fit=crop&w=600&q=80'
    ],
    variants: [
      {
        id: 'var-2a',
        shade_name: 'Premium Festive Assortment',
        color_code: '#c96f90',
        size: '16 Pieces',
        finish: 'glossy',
        sku: 'SKU-16J-PRM',
        additional_price: 0,
        stock: 60,
        is_active: true
      }
    ],
    reviews: [
      {
        id: 'rev-3',
        userEmail: 'ananya.m@gmail.com',
        rating: 5,
        title: 'Perfect for weddings!',
        body: 'This premium set is just beautiful. Heavy meenakari work and rich colors. I got so many compliments wearing these at my cousin\'s wedding functions!',
        isVerifiedPurchase: true,
        helpfulCount: 22,
        createdAt: '2026-06-18T11:22:00Z'
      }
    ]
  },
  {
    id: 'prod-3',
    name: 'Oxidized Silver Jhumka Box Set (12 Pieces)',
    slug: 'oxidized-silver-jhumka-box-set-12-pieces',
    brand: 'HYPEHAVENHUB',
    category: '12 Piece Jhumka Box Set',
    short_description: 'A curated set of 12 beautiful oxidized silver jhumkas, perfect for boho-chic outfits.',
    description: 'This Oxidized Silver Jhumka Box Set features 12 pairs of premium German Silver styled earrings. They showcase vintage patterns, floral carvings, and tiny metal-bead drops that create a lovely chiming sound. Perfect for casual wear, college, and ethnic fusion outfits.',
    ingredients: 'German silver alloy, oxidized black polish, protective coat. Keep away from water and humidity.',
    how_to_use: 'Wipe with a soft dry cloth after wearing. Store individually in the slots to prevent tangling.',
    material: 'German Silver, Brass',
    metal_purity: 'Oxidized Antique Finish',
    warranty: 'No Polish Warranty (Oxidized nature is antique)',
    base_price: 499,
    discount_percent: 15,
    finish: 'matte',
    is_active: true,
    is_featured: true,
    is_new_arrival: false,
    is_bestseller: false,
    display_image_url: 'https://images.unsplash.com/photo-1635767798638-3e25273a8236?auto=format&fit=crop&w=600&q=80',
    secondary_image_url: 'https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?auto=format&fit=crop&w=600&q=80',
    gallery_urls: [
      'https://images.unsplash.com/photo-1635767798638-3e25273a8236?auto=format&fit=crop&w=600&q=80',
      'https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?auto=format&fit=crop&w=600&q=80'
    ],
    variants: [
      {
        id: 'var-3a',
        shade_name: 'Vintage Silver Assortment',
        color_code: '#a6a6a6',
        size: '12 Pieces',
        finish: 'matte',
        sku: 'SKU-12J-OXI',
        additional_price: 0,
        stock: 45,
        is_active: true
      }
    ],
    reviews: [
      {
        id: 'rev-4',
        userEmail: 'riya_das@yahoo.com',
        rating: 5,
        title: 'Boho Vibe!',
        body: 'Extremely stunning silver designs. Perfect for college. It goes wonderfully with kurtas and jeans!',
        isVerifiedPurchase: true,
        helpfulCount: 8,
        createdAt: '2026-06-25T17:15:00Z'
      }
    ]
  },
  {
    id: 'prod-4',
    name: 'Antique Gold Jhumka Box Set (12 Pieces)',
    slug: 'antique-gold-jhumka-box-set-12-pieces',
    brand: 'HYPEHAVENHUB',
    category: '12 Piece Jhumka Box Set',
    short_description: 'Premium antique gold plated jhumkas with exquisite matte finish.',
    description: 'Heritage Temple Design jhumkas featuring warm antique-matte gold plating. This 12-piece box includes classic round domes, umbrella styles, and teardrop shapes embellished with synthetic ruby-pink stones and tiny hanging pearls.',
    ingredients: 'Copper alloy base, matte antique gold micro-plating, synthetic stones, faux shell pearls.',
    how_to_use: 'Put on after applying makeup and hairspray. Avoid direct contact with liquids. Store in a cool dry place.',
    material: 'Matte Antique Gold plating, Brass-Copper base',
    metal_purity: 'Traditional Antique Finish',
    warranty: '6 Months Polish Warranty',
    base_price: 649,
    discount_percent: 8,
    finish: 'satin',
    is_active: true,
    is_featured: false,
    is_new_arrival: false,
    is_bestseller: false,
    display_image_url: 'https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?auto=format&fit=crop&w=600&q=80',
    secondary_image_url: 'https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=600&q=80',
    gallery_urls: [
      'https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?auto=format&fit=crop&w=600&q=80',
      'https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=600&q=80'
    ],
    variants: [
      {
        id: 'var-4a',
        shade_name: 'Heritage Temple Gold',
        color_code: '#b08a3d',
        size: '12 Pieces',
        finish: 'satin',
        sku: 'SKU-12J-ANT',
        additional_price: 0,
        stock: 30,
        is_active: true
      }
    ],
    reviews: []
  },
  {
    id: 'prod-5',
    name: 'Pearl Drop Festive Jhumka Box Set (16 Pieces)',
    slug: 'pearl-drop-festive-jhumka-box-set-16-pieces',
    brand: 'HYPEHAVENHUB',
    category: '16 Piece Jhumka Box Set',
    short_description: 'A premium 16-piece collection of royal pearl-drop festive jhumkas.',
    description: 'Our grandest box set yet! Contains 16 pieces of royal-grade earrings featuring premium hanging cluster pearls, intricate kundan stone carvings, and traditional meenakari colors. This box represents India\'s diverse heritage jewel styles in a durable, well-cushioned wooden velvet drawer box.',
    ingredients: 'Brass alloy, premium micro gold-plating, hand-painted meenakari enamel, AAA-grade faux pearls, glass kundan.',
    how_to_use: 'Perfect for bridal wear, grand festivals, or as high-value return gifts. Keep dry and enclosed in dry storage.',
    material: '22K Gold plating, Kundan glass, AAA Pearls',
    metal_purity: 'Premium Traditional Gold Polish',
    warranty: '1 Year Polish Warranty',
    base_price: 899,
    discount_percent: 20,
    finish: 'glossy',
    is_active: true,
    is_featured: true,
    is_new_arrival: true,
    is_bestseller: false,
    display_image_url: 'https://images.unsplash.com/photo-1635767798638-3e25273a8236?auto=format&fit=crop&w=600&q=80',
    secondary_image_url: 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=600&q=80',
    gallery_urls: [
      'https://images.unsplash.com/photo-1635767798638-3e25273a8236?auto=format&fit=crop&w=600&q=80',
      'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=600&q=80'
    ],
    variants: [
      {
        id: 'var-5a',
        shade_name: 'Royal Kundan & Pearl Drops',
        color_code: '#ebd096',
        size: '16 Pieces',
        finish: 'glossy',
        sku: 'SKU-16J-PRL',
        additional_price: 0,
        stock: 25,
        is_active: true
      }
    ],
    reviews: [
      {
        id: 'rev-5',
        userEmail: 'kanchan_singh@gmail.com',
        rating: 5,
        title: 'Magnificent!',
        body: 'The drawer box is beautiful and the jhumkas are pure royalty. This is easily worth double the price. Very happy with Hype Haven Hub!',
        isVerifiedPurchase: true,
        helpfulCount: 31,
        createdAt: '2026-07-02T08:12:00Z'
      }
    ]
  }
];

// In-Memory Database Collections
const users = new Map<string, { email: string; phone?: string; otp?: string; is_verified: boolean; addresses: Address[] }>();
const orders: Order[] = [];
const complaints: Complaint[] = [];
const activeSessions = new Map<string, string>(); // sessionId -> email

// Helper to generate IDs
function generateId(prefix: string): string {
  return `${prefix}-${Math.random().toString(36).substring(2, 9).toUpperCase()}`;
}

// Pre-create a demo user for easy testing
users.set('demo@hypehaven.com', {
  email: 'demo@hypehaven.com',
  phone: '9876543210',
  is_verified: true,
  addresses: [
    {
      id: 'addr-1',
      type: 'home',
      full_name: 'Demo Customer',
      phone: '9876543210',
      address_line1: 'Flat 405, Rosewood Apartments',
      address_line2: 'Near Central Park, Sector 62',
      city: 'Noida',
      state: 'Uttar Pradesh',
      pincode: '201301',
      is_default: true
    }
  ]
});

// Seed some historic orders for the demo user
orders.push({
  id: 'ord-hist-1',
  order_id: 'HH8F2C7A1D',
  status: 'delivered',
  subtotal: 599,
  discount_amount: 59.9,
  delivery_charge: 0,
  grand_total: 539.1,
  coupon_code: 'JHUMKA10',
  items: [
    {
      id: 'item-hist-1',
      productId: 'prod-1',
      productName: '12 Piece Jhumka Box Set',
      variantLabel: 'Classic Gold Assortment (12 Pieces)',
      quantity: 1,
      unitPrice: 539.1,
      totalPrice: 539.1
    }
  ],
  address: {
    id: 'addr-1',
    type: 'home',
    full_name: 'Demo Customer',
    phone: '9876543210',
    address_line1: 'Flat 405, Rosewood Apartments',
    address_line2: 'Near Central Park, Sector 62',
    city: 'Noida',
    state: 'Uttar Pradesh',
    pincode: '201301',
    is_default: true
  },
  created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 days ago
  tracking: [
    { status: 'pending', description: 'Order submitted by customer', created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString() },
    { status: 'confirmed', description: 'Seller approved the order and compiled billing details', created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000 + 2 * 3600 * 1000).toISOString() },
    { status: 'processing', description: 'Earrings quality inspected and sealed in gift box', created_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString() },
    { status: 'shipped', description: 'Package dispatched via BlueDart Express (Tracking ID: BD9283719)', created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString() },
    { status: 'out_for_delivery', description: 'Out for delivery in Sector 62, Courier partner contact: +91999912345', created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString() },
    { status: 'delivered', description: 'Delivered at reception, OTP verified successfully.', created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000 + 4 * 3600 * 1000).toISOString() }
  ]
});

// Seed some complaints
complaints.push({
  id: 'comp-1',
  complaint_id: 'CP7D29E1A',
  complaint_type: 'delivery',
  subject: 'Delay in BlueDart dispatch',
  description: 'My order took 3 days to ship instead of the expected 24 hours. Please expedite.',
  status: 'resolved',
  admin_response: 'We sincerely apologize for the delay. Your package was expedited and has now been delivered. As a goodwill gesture, we have sent a 15% discount code JHUMKA15 to your email.',
  priority: 'high',
  created_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString()
});

// ==========================================
// API ROUTE HANDLERS
// ==========================================

// Get All Products
app.get('/api/products', (req, res) => {
  res.json(SEED_PRODUCTS);
});

// Get Single Product by Slug
app.get('/api/products/:slug', (req, res) => {
  const product = SEED_PRODUCTS.find(p => p.slug === req.params.slug);
  if (!product) {
    return res.status(404).json({ error: 'Product not found' });
  }
  res.json(product);
});

// Submit/Request OTP (Registration / Login)
app.post('/api/auth/otp', (req, res) => {
  const { email, phone } = req.body;
  if (!email) {
    return res.status(400).json({ error: 'Email address is required' });
  }

  const generatedOtp = Math.floor(100000 + Math.random() * 900000).toString(); // 6-digit OTP
  console.log(`[HYPEHAVENHUB OTP] Email: ${email} | Generated OTP: ${generatedOtp}`);

  const existingUser = users.get(email);
  if (existingUser) {
    users.set(email, { ...existingUser, otp: generatedOtp });
  } else {
    users.set(email, {
      email,
      phone: phone || '',
      otp: generatedOtp,
      is_verified: false,
      addresses: []
    });
  }

  res.json({ message: 'OTP sent successfully (Simulated in Console)', otp: generatedOtp });
});

// Verify OTP
app.post('/api/auth/verify-otp', (req, res) => {
  const { email, otp } = req.body;
  if (!email || !otp) {
    return res.status(400).json({ error: 'Email and OTP are required' });
  }

  const user = users.get(email);
  if (!user || user.otp !== otp) {
    return res.status(400).json({ error: 'Invalid or expired OTP. Please try again.' });
  }

  // Verification success
  user.is_verified = true;
  user.otp = undefined; // Clear OTP
  users.set(email, user);

  // Generate Session ID
  const sessionId = generateId('sess');
  activeSessions.set(sessionId, email);

  res.json({
    message: 'Authentication successful',
    sessionId,
    user: {
      email: user.email,
      phone: user.phone,
      addresses: user.addresses
    }
  });
});

// Get Profile details of verified User
app.post('/api/auth/profile', (req, res) => {
  const { sessionId } = req.body;
  const email = activeSessions.get(sessionId);
  if (!email) {
    return res.status(401).json({ error: 'Unauthorized session' });
  }

  const user = users.get(email);
  if (!user) {
    return res.status(404).json({ error: 'User profile not found' });
  }

  res.json({
    email: user.email,
    phone: user.phone,
    addresses: user.addresses
  });
});

// Log out user
app.post('/api/auth/logout', (req, res) => {
  const { sessionId } = req.body;
  if (sessionId) {
    activeSessions.delete(sessionId);
  }
  res.json({ message: 'Logged out successfully' });
});

// Save user Address
app.post('/api/profile/address', (req, res) => {
  const { sessionId, address } = req.body;
  const email = activeSessions.get(sessionId);
  if (!email) {
    return res.status(401).json({ error: 'Unauthorized session' });
  }

  const user = users.get(email);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }

  const newAddress: Address = {
    id: address.id || generateId('addr'),
    type: address.type || 'home',
    full_name: address.full_name,
    phone: address.phone,
    address_line1: address.address_line1,
    address_line2: address.address_line2,
    city: address.city,
    state: address.state,
    pincode: address.pincode,
    is_default: address.is_default || false
  };

  // If set to default, change other addresses of this user to not-default
  if (newAddress.is_default) {
    user.addresses.forEach(a => a.is_default = false);
  }

  const existingIndex = user.addresses.findIndex(a => a.id === newAddress.id);
  if (existingIndex !== -1) {
    user.addresses[existingIndex] = newAddress;
  } else {
    // If it is the first address, default it
    if (user.addresses.length === 0) {
      newAddress.is_default = true;
    }
    user.addresses.push(newAddress);
  }

  users.set(email, user);
  res.json({ message: 'Address saved successfully', addresses: user.addresses });
});

// Delete user Address
app.post('/api/profile/address/delete', (req, res) => {
  const { sessionId, addressId } = req.body;
  const email = activeSessions.get(sessionId);
  if (!email) {
    return res.status(401).json({ error: 'Unauthorized session' });
  }

  const user = users.get(email);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }

  user.addresses = user.addresses.filter(a => a.id !== addressId);
  // Set another address to default if default was deleted
  if (user.addresses.length > 0 && !user.addresses.some(a => a.is_default)) {
    user.addresses[0].is_default = true;
  }

  users.set(email, user);
  res.json({ message: 'Address deleted successfully', addresses: user.addresses });
});

// Submit order
app.post('/api/orders', (req, res) => {
  const { sessionId, cartItems, subtotal, discount, shipping, grandTotal, couponCode, shippingAddress } = req.body;
  const email = activeSessions.get(sessionId) || 'demo@hypehaven.com'; // Default to demo user for simple quick checkouts!

  const orderId = `HH${Math.floor(100000 + Math.random() * 900000).toString()}${String.fromCharCode(65 + Math.floor(Math.random() * 26))}${String.fromCharCode(65 + Math.floor(Math.random() * 26))}`;

  const newOrder: Order = {
    id: generateId('ord'),
    order_id: orderId,
    status: 'pending',
    subtotal,
    discount_amount: discount,
    delivery_charge: shipping,
    grand_total: grandTotal,
    coupon_code: couponCode,
    items: cartItems.map((item: any) => ({
      id: generateId('item'),
      productId: item.productId,
      productName: item.productName,
      variantLabel: item.variantLabel || 'Default',
      quantity: item.quantity,
      unitPrice: item.sellingPrice,
      totalPrice: item.sellingPrice * item.quantity
    })),
    address: shippingAddress,
    created_at: new Date().toISOString(),
    tracking: [
      { status: 'pending', description: 'Order successfully created. Awaiting merchant processing.', created_at: new Date().toISOString() }
    ]
  };

  orders.unshift(newOrder);

  // Update product stock levels
  cartItems.forEach((item: any) => {
    const prod = SEED_PRODUCTS.find(p => p.id === item.productId);
    if (prod) {
      const variant = prod.variants.find(v => v.id === item.variantId);
      if (variant) {
        variant.stock = Math.max(0, variant.stock - item.quantity);
      }
    }
  });

  res.json({ message: 'Order placed successfully!', order: newOrder });
});

// Get specific User Orders
app.post('/api/orders/list', (req, res) => {
  const { sessionId } = req.body;
  const email = activeSessions.get(sessionId);

  if (!email) {
    // If not logged in but testing, let them see orders. If demo, show demo orders.
    return res.json(orders.filter(o => o.address.full_name === 'Demo Customer' || o.id.startsWith('ord-')));
  }

  const user = users.get(email);
  if (!user) {
    return res.json([]);
  }

  // Filter orders by user full name or phone, or return all for the demo.
  const userOrderList = orders.filter(o => {
    if (email === 'demo@hypehaven.com') return true;
    return o.address.full_name === (user.addresses[0]?.full_name || email);
  });

  res.json(userOrderList);
});

// Submit support complaint
app.post('/api/complaints', (req, res) => {
  const { sessionId, complaint_type, subject, description, priority } = req.body;
  const email = activeSessions.get(sessionId) || 'demo@hypehaven.com';

  const complaintId = `CP${Math.floor(100000 + Math.random() * 900000).toString()}${String.fromCharCode(65 + Math.floor(Math.random() * 26))}`;

  const newComplaint: Complaint = {
    id: generateId('comp'),
    complaint_id: complaintId,
    complaint_type,
    subject,
    description,
    status: 'open',
    admin_response: '',
    priority: priority || 'medium',
    created_at: new Date().toISOString()
  };

  complaints.unshift(newComplaint);

  // Simulate an automatic smart response from admin support after a brief moment
  setTimeout(() => {
    const responses: Record<string, string> = {
      product_quality: 'Thank you for reaching out. We have received your query regarding the quality of the jewellery in your box set. Our quality team has been alerted, and we are initiating a free replacement dispatch for any damaged earring loops. A support executive will contact you shortly.',
      delivery: 'We apologize for any shipment delay. Our delivery team is checking with BlueDart / ShipRocket regarding your shipment status. Your order is prioritised and will be delivered on an express timeline.',
      payment: 'We have received your payment check request. If your payment was deducted but shown as failed, please be assured that refunds are auto-credited within 3-5 business days. We are manually validating your transaction ref code.',
      account: 'Your account related query is logged. We are resolving verification and profile display settings for your active email address.',
      website: 'Thank you for notifying us about the web layout issue. Our tech division is rectifying the visual layout parameters.'
    };
    newComplaint.status = 'in_progress';
    newComplaint.admin_response = responses[complaint_type] || 'Your support ticket has been noted and assigned to our customer care team. We will resolve it within 24 hours.';
  }, 1500);

  res.json({ message: 'Complaint filed successfully', complaint: newComplaint });
});

// Get complaints list
app.post('/api/complaints/list', (req, res) => {
  res.json(complaints);
});

// Submit Product Review
app.post('/api/reviews', (req, res) => {
  const { productId, rating, title, body, userEmail } = req.body;
  if (!productId || !rating || !title || !body) {
    return res.status(400).json({ error: 'All review fields are required' });
  }

  const product = SEED_PRODUCTS.find(p => p.id === productId);
  if (!product) {
    return res.status(404).json({ error: 'Product not found' });
  }

  const newReview: Review = {
    id: generateId('rev'),
    userEmail: userEmail || 'anonymous@hypehaven.com',
    rating,
    title,
    body,
    isVerifiedPurchase: true,
    helpfulCount: 0,
    createdAt: new Date().toISOString()
  };

  product.reviews.unshift(newReview);
  res.json({ message: 'Review posted successfully!', review: newReview, reviews: product.reviews });
});

// ==========================================
// VITE DEV SERVER / STATIC ASSETS
// ==========================================

async function startServer() {
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa'
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`[HYPEHAVENHUB] Fullstack Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
