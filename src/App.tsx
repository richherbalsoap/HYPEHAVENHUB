import React from 'react';
import { Product, CartItem, Address, User, Order } from './types';
import AnnouncementBar from './components/AnnouncementBar';
import Header from './components/Header';
import Footer from './components/Footer';
import ReviewSection from './components/ReviewSection';
import Dashboard from './components/Dashboard';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Heart, ShoppingBag, ArrowLeft, Star, ShieldCheck, Truck, RefreshCw, 
  HelpCircle, CheckCircle, Ticket, Trash2, ArrowRight, Sparkles 
} from 'lucide-react';

export default function App() {
  // Navigation & Category States
  const [view, setView] = React.useState<string>('home');
  const [selectedProductSlug, setSelectedProductSlug] = React.useState<string>('');
  const [currentCategory, setCategory] = React.useState<string>('All');
  const [searchQuery, setSearchQuery] = React.useState<string>('');

  // Catalog States
  const [products, setProducts] = React.useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = React.useState<Product | null>(null);
  const [activeGalleryIdx, setActiveGalleryIdx] = React.useState<number>(0);
  
  // Filter States
  const [priceFilter, setPriceFilter] = React.useState<string>('all');
  const [finishFilter, setFinishFilter] = React.useState<string>('all');
  const [sortBy, setSortBy] = React.useState<string>('bestselling');

  // Cart & Wishlist States
  const [cart, setCart] = React.useState<CartItem[]>([]);
  const [wishlist, setWishlist] = React.useState<string[]>([]);
  const [couponCode, setCouponCode] = React.useState<string>('');
  const [appliedCoupon, setAppliedCoupon] = React.useState<string>('');
  const [couponError, setCouponError] = React.useState<string>('');
  
  // Selected shipping address for checkout
  const [selectedAddressId, setSelectedAddressId] = React.useState<string>('');

  // Auth States
  const [isLoggedIn, setIsLoggedIn] = React.useState<boolean>(false);
  const [user, setUser] = React.useState<User | null>(null);
  const [authEmail, setAuthEmail] = React.useState<string>('');
  const [authPhone, setAuthPhone] = React.useState<string>('');
  const [otpSent, setOtpSent] = React.useState<boolean>(false);
  const [authOtp, setAuthOtp] = React.useState<string>('');
  const [visibleOtpCode, setVisibleOtpCode] = React.useState<string>(''); // For easy UI testing
  const [authError, setAuthError] = React.useState<string>('');

  // Checkout Success Overlay
  const [placedOrder, setPlacedOrder] = React.useState<Order | null>(null);

  // Active Hero Slide
  const [currentSlide, setCurrentSlide] = React.useState(0);
  const heroSlides = [
    {
      title: "Handcrafted Jhumka Box Sets",
      subtitle: "Traditional oxidised silver and luxury gold-plated temple designs.",
      badge: "BESTSELLER",
      image: "https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=800&q=80",
      slug: "12-piece-jhumka-box-set"
    },
    {
      title: "Royal Meenakari Collections",
      subtitle: "Vibrant colors, kundan, and pearl hanging beads perfect for weddings.",
      badge: "NEW ARRIVALS",
      image: "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80",
      slug: "16-piece-jhumka-box-set"
    }
  ];

  // Load Products & Cart/Wishlist Cache
  React.useEffect(() => {
    // Load local storage cache
    const cachedCart = localStorage.getItem('hypehaven_cart');
    const cachedWishlist = localStorage.getItem('hypehaven_wishlist');
    const cachedSession = localStorage.getItem('hypehaven_session');
    
    if (cachedCart) setCart(JSON.parse(cachedCart));
    if (cachedWishlist) setWishlist(JSON.parse(cachedWishlist));

    const loadProducts = async () => {
      try {
        const res = await fetch('/api/products');
        if (res.ok) {
          const data = await res.json();
          setProducts(data);
        }
      } catch (err) {
        console.error("Failed to load products from Express API:", err);
      }
    };
    
    loadProducts();

    // If session exists, validate profile
    if (cachedSession) {
      fetch('/api/auth/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId: cachedSession })
      })
      .then(res => {
        if (res.ok) return res.json();
        throw new Error();
      })
      .then(profile => {
        setIsLoggedIn(true);
        setUser(profile);
        if (profile.addresses?.length > 0) {
          const def = profile.addresses.find((a: Address) => a.is_default);
          setSelectedAddressId(def ? def.id : profile.addresses[0].id);
        }
      })
      .catch(() => {
        localStorage.removeItem('hypehaven_session');
      });
    }
  }, []);

  // Save Cart & Wishlist to LocalStorage
  React.useEffect(() => {
    localStorage.setItem('hypehaven_cart', JSON.stringify(cart));
  }, [cart]);

  React.useEffect(() => {
    localStorage.setItem('hypehaven_wishlist', JSON.stringify(wishlist));
  }, [wishlist]);

  // Load single product details
  React.useEffect(() => {
    if (selectedProductSlug) {
      const loadProduct = async () => {
        try {
          const res = await fetch(`/api/products/${selectedProductSlug}`);
          if (res.ok) {
            const data = await res.json();
            setSelectedProduct(data);
            setActiveGalleryIdx(0);
          }
        } catch (e) {
          console.error(e);
        }
      };
      loadProduct();
    }
  }, [selectedProductSlug]);

  // Slide interval
  React.useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % heroSlides.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  // Handler: Add to Cart
  const handleAddToCart = (product: Product, quantity = 1, variantId?: string) => {
    const variant = variantId 
      ? product.variants.find(v => v.id === variantId)
      : product.variants[0];

    const finalPrice = product.base_price * (1 - product.discount_percent / 100);

    const existingIndex = cart.findIndex(
      item => item.productId === product.id && item.variantId === variant?.id
    );

    if (existingIndex !== -1) {
      const newCart = [...cart];
      newCart[existingIndex].quantity += quantity;
      setCart(newCart);
    } else {
      const newItem: CartItem = {
        id: `citem-${Math.random().toString(36).substring(2, 9)}`,
        productId: product.id,
        productName: product.name,
        productSlug: product.slug,
        display_image_url: product.display_image_url,
        variantId: variant?.id,
        variantLabel: variant ? `${variant.shade_name} (${variant.size})` : undefined,
        quantity,
        basePrice: product.base_price,
        sellingPrice: finalPrice
      };
      setCart([...cart, newItem]);
    }
  };

  // Handler: Toggle Wishlist
  const handleToggleWishlist = (productId: string) => {
    if (wishlist.includes(productId)) {
      setWishlist(wishlist.filter(id => id !== productId));
    } else {
      setWishlist([...wishlist, productId]);
    }
  };

  // Handler: Cart Operations
  const updateCartQuantity = (id: string, qty: number) => {
    if (qty <= 0) {
      setCart(cart.filter(item => item.id !== id));
    } else {
      setCart(cart.map(item => item.id === id ? { ...item, quantity: qty } : item));
    }
  };

  // Auth: Request OTP
  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!authEmail) {
      setAuthError("Email address is required.");
      return;
    }
    setAuthError('');
    try {
      const res = await fetch('/api/auth/otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: authEmail, phone: authPhone })
      });
      if (res.ok) {
        const data = await res.json();
        setOtpSent(true);
        if (data.otp) {
          setVisibleOtpCode(data.otp); // Show in simulated alert bubble for easy testing!
        }
      } else {
        const data = await res.json();
        setAuthError(data.error || "Failed to trigger OTP.");
      }
    } catch (err) {
      setAuthError("Server communication error.");
    }
  };

  // Auth: Verify OTP
  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!authOtp) {
      setAuthError("Please input the 6-digit OTP code.");
      return;
    }
    setAuthError('');
    try {
      const res = await fetch('/api/auth/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: authEmail, otp: authOtp })
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('hypehaven_session', data.sessionId);
        setIsLoggedIn(true);
        setUser(data.user);
        setView('home');
        setOtpSent(false);
        setAuthOtp('');
        setAuthEmail('');
        setAuthPhone('');
        if (data.user.addresses?.length > 0) {
          const def = data.user.addresses.find((a: Address) => a.is_default);
          setSelectedAddressId(def ? def.id : data.user.addresses[0].id);
        }
      } else {
        const data = await res.json();
        setAuthError(data.error || "Incorrect OTP. Check display bubble and retry.");
      }
    } catch (err) {
      setAuthError("Verification failed.");
    }
  };

  // Auth: Logout
  const handleLogout = async () => {
    const sessionId = localStorage.getItem('hypehaven_session');
    if (sessionId) {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId })
      });
    }
    localStorage.removeItem('hypehaven_session');
    setIsLoggedIn(false);
    setUser(null);
    setView('home');
  };

  // Profile: Save Address
  const handleSaveAddress = async (addrData: Partial<Address>) => {
    const sessionId = localStorage.getItem('hypehaven_session');
    if (!sessionId) return;

    try {
      const res = await fetch('/api/profile/address', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId, address: addrData })
      });
      if (res.ok) {
        const data = await res.json();
        if (user) {
          const updatedUser = { ...user, addresses: data.addresses };
          setUser(updatedUser);
          
          // Select default or new address
          const def = data.addresses.find((a: Address) => a.is_default);
          setSelectedAddressId(def ? def.id : data.addresses[0]?.id || '');
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Profile: Delete Address
  const handleDeleteAddress = async (addressId: string) => {
    const sessionId = localStorage.getItem('hypehaven_session');
    if (!sessionId) return;

    try {
      const res = await fetch('/api/profile/address/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId, addressId })
      });
      if (res.ok) {
        const data = await res.json();
        if (user) {
          setUser({ ...user, addresses: data.addresses });
          if (selectedAddressId === addressId) {
            setSelectedAddressId(data.addresses[0]?.id || '');
          }
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Coupon Application
  const handleApplyCoupon = () => {
    setCouponError('');
    if (couponCode.toUpperCase() === 'JHUMKA10') {
      setAppliedCoupon('JHUMKA10');
    } else {
      setCouponError('Invalid Coupon Code. Try using JHUMKA10.');
    }
  };

  // Order Calculations
  const cartSubtotal = cart.reduce((sum, item) => sum + item.sellingPrice * item.quantity, 0);
  const couponDiscount = appliedCoupon === 'JHUMKA10' ? cartSubtotal * 0.10 : 0;
  const cartShipping = (cartSubtotal - couponDiscount) >= 499 || cartSubtotal === 0 ? 0 : 50;
  const cartGrandTotal = Math.max(0, cartSubtotal - couponDiscount + cartShipping);

  // Submit Order Checkout
  const handlePlaceOrder = async () => {
    const activeAddress = user?.addresses.find(a => a.id === selectedAddressId) || user?.addresses[0];
    
    if (!activeAddress) {
      alert("Please add and select a delivery address in your profile/checkout before placing order.");
      setView('dashboard');
      return;
    }

    const sessionId = localStorage.getItem('hypehaven_session');
    try {
      const res = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId,
          cartItems: cart,
          subtotal: cartSubtotal,
          discount: couponDiscount,
          shipping: cartShipping,
          grandTotal: cartGrandTotal,
          couponCode: appliedCoupon,
          shippingAddress: activeAddress
        })
      });
      if (res.ok) {
        const data = await res.json();
        setPlacedOrder(data.order);
        setCart([]); // Clear cart
        setAppliedCoupon('');
        setCouponCode('');
      }
    } catch (err) {
      console.error("Failed checkout placement:", err);
    }
  };

  // Submit Review Form
  const handlePostReview = async (reviewData: { rating: number; title: string; body: string; userEmail: string }) => {
    if (!selectedProduct) return;
    try {
      const res = await fetch('/api/reviews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          productId: selectedProduct.id,
          ...reviewData
        })
      });
      if (res.ok) {
        const data = await res.json();
        setSelectedProduct({ ...selectedProduct, reviews: data.reviews });
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Filter & Sort Calculations
  const filteredProducts = products.filter(prod => {
    // Search Query
    if (searchQuery) {
      const term = searchQuery.toLowerCase();
      const matchName = prod.name.toLowerCase().includes(term);
      const matchDesc = prod.description.toLowerCase().includes(term);
      const matchMaterial = prod.material.toLowerCase().includes(term);
      if (!matchName && !matchDesc && !matchMaterial) return false;
    }

    // Category
    if (currentCategory !== 'All' && currentCategory !== 'Offers') {
      if (prod.category !== currentCategory) return false;
    }

    // Offers
    if (currentCategory === 'Offers') {
      if (prod.discount_percent < 12) return false; // Items with 12%+ discount
    }

    // Price Filter
    const finalPrice = prod.base_price * (1 - prod.discount_percent / 100);
    if (priceFilter === 'under500' && finalPrice >= 500) return false;
    if (priceFilter === '500to700' && (finalPrice < 500 || finalPrice > 700)) return false;
    if (priceFilter === 'above700' && finalPrice <= 700) return false;

    // Finish Filter
    if (finishFilter !== 'all' && prod.finish !== finishFilter) return false;

    return true;
  }).sort((a, b) => {
    const finalPriceA = a.base_price * (1 - a.discount_percent / 100);
    const finalPriceB = b.base_price * (1 - b.discount_percent / 100);

    if (sortBy === 'priceLow') return finalPriceA - finalPriceB;
    if (sortBy === 'priceHigh') return finalPriceB - finalPriceA;
    if (sortBy === 'newest') return a.is_new_arrival ? -1 : 1;
    
    // Default Bestselling
    return a.is_bestseller ? -1 : 1;
  });

  return (
    <div className="min-h-screen bg-brand-pink-bg text-brand-dark flex flex-col font-sans">
      
      {/* Top Banner Announcements */}
      <AnnouncementBar />

      {/* Primary Header */}
      <Header
        cartCount={cart.reduce((sum, item) => sum + item.quantity, 0)}
        wishlistCount={wishlist.length}
        currentCategory={currentCategory}
        setCategory={(cat) => {
          setCategory(cat);
          setSearchQuery('');
        }}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onNavigate={(newView) => {
          setView(newView);
          setSelectedProduct(null);
          setSelectedProductSlug('');
        }}
        isLoggedIn={isLoggedIn}
        userEmail={user?.email}
        onLogout={handleLogout}
      />

      {/* MAIN VIEWPORT */}
      <main className="flex-grow">
        
        {/* VIEW: HOME / CATALOG */}
        {view === 'home' && (
          <div className="space-y-12 pb-16">
            
            {/* Elegant Hero Slider (Only if no active filters/searches) */}
            {!searchQuery && currentCategory === 'All' && priceFilter === 'all' && finishFilter === 'all' && (
              <div className="relative h-[480px] bg-neutral-900 overflow-hidden select-none">
                <div className="absolute inset-0 bg-radial-at-c from-neutral-800/20 to-neutral-900/90 z-10" />
                
                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentSlide}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.8 }}
                    className="absolute inset-0"
                  >
                    <img 
                      src={heroSlides[currentSlide].image} 
                      alt={heroSlides[currentSlide].title}
                      className="w-full h-full object-cover opacity-45 scale-105"
                      referrerPolicy="no-referrer"
                    />
                    <div className="absolute inset-0 z-20 flex items-center justify-start px-6 md:px-16 lg:px-24">
                      <div className="max-w-xl text-white space-y-4 font-sans">
                        <span className="inline-block px-3 py-1 text-[10px] tracking-widest font-bold text-brand-gold bg-brand-gold/10 border border-brand-gold/20 rounded-full font-mono uppercase">
                          {heroSlides[currentSlide].badge}
                        </span>
                        <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight font-display text-white">
                          {heroSlides[currentSlide].title}
                        </h1>
                        <p className="text-sm md:text-base text-neutral-300 font-sans font-light leading-relaxed">
                          {heroSlides[currentSlide].subtitle}
                        </p>
                        
                        <div className="pt-4 flex items-center gap-4">
                          <button
                            onClick={() => {
                              setSelectedProductSlug(heroSlides[currentSlide].slug);
                              setView('product-detail');
                            }}
                            className="px-6 py-3 bg-brand-pink text-white font-bold text-xs uppercase tracking-wider rounded-full hover:bg-brand-pink-light shadow-md transition-all flex items-center gap-2"
                          >
                            Explore Box <ArrowRight size={14} />
                          </button>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </AnimatePresence>

                {/* Dots indicators */}
                <div className="absolute bottom-6 right-6 z-30 flex gap-2">
                  {heroSlides.map((_, sIdx) => (
                    <button
                      key={sIdx}
                      onClick={() => setCurrentSlide(sIdx)}
                      className={`h-2 rounded-full transition-all ${
                        currentSlide === sIdx ? 'w-6 bg-brand-pink' : 'w-2 bg-white/40'
                      }`}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Catalog Grid Section with Filters */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              
              {/* Filter Tool Rail */}
              <div className="bg-white rounded-3xl border border-rose-100 p-6 shadow-xs flex flex-col lg:flex-row justify-between items-stretch lg:items-center gap-6 mb-8 mt-4">
                
                {/* Left Active Tags */}
                <div className="flex flex-wrap items-center gap-3">
                  <span className="text-[11px] font-bold font-mono uppercase text-gray-400 tracking-wider">Filters:</span>
                  <select
                    value={priceFilter}
                    onChange={(e) => setPriceFilter(e.target.value)}
                    className="bg-rose-50/50 border border-rose-100 text-xs px-3 py-1.5 rounded-full font-semibold focus:outline-hidden text-gray-700"
                  >
                    <option value="all">All Prices</option>
                    <option value="under500">Under ₹500</option>
                    <option value="500to700">₹500 - ₹700</option>
                    <option value="above700">Above ₹700</option>
                  </select>

                  <select
                    value={finishFilter}
                    onChange={(e) => setFinishFilter(e.target.value)}
                    className="bg-rose-50/50 border border-rose-100 text-xs px-3 py-1.5 rounded-full font-semibold focus:outline-hidden text-gray-700"
                  >
                    <option value="all">All Finishes</option>
                    <option value="shimmer">Shimmer Gold</option>
                    <option value="glossy">Glossy Gold / Enamel</option>
                    <option value="matte">Matte Oxidized Silver</option>
                    <option value="satin">Satin Matte Gold</option>
                  </select>
                </div>

                {/* Right Sort controls */}
                <div className="flex items-center gap-3">
                  <span className="text-[11px] font-bold font-mono uppercase text-gray-400 tracking-wider shrink-0">Sort By:</span>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="bg-rose-50/50 border border-rose-100 text-xs px-3 py-1.5 rounded-full font-semibold focus:outline-hidden text-gray-700"
                  >
                    <option value="bestselling">Bestselling</option>
                    <option value="newest">New Arrivals</option>
                    <option value="priceLow">Price: Low to High</option>
                    <option value="priceHigh">Price: High to Low</option>
                  </select>
                </div>

              </div>

              {/* Title Header */}
              <div className="mb-8 flex justify-between items-end">
                <div>
                  <h2 className="text-2xl font-bold tracking-tight font-display text-neutral-800 flex items-center gap-2">
                    <Sparkles className="text-brand-pink" size={20} />
                    {currentCategory === 'All' ? 'Curated Jhumka Box Sets' : currentCategory}
                  </h2>
                  <p className="text-xs text-gray-400 font-sans mt-0.5">
                    Showing {filteredProducts.length} unique handcrafted box collections
                  </p>
                </div>
              </div>

              {/* Product Cards Grid */}
              {filteredProducts.length === 0 ? (
                <div className="text-center py-20 bg-white rounded-3xl border border-rose-100/50 shadow-xs">
                  <p className="text-sm font-semibold text-gray-600">No Jhumka sets match your filters.</p>
                  <p className="text-xs text-gray-400 mt-1">Try resetting the filters or broadening your search keywords.</p>
                  <button 
                    onClick={() => { setPriceFilter('all'); setFinishFilter('all'); setSearchQuery(''); setCategory('All'); }}
                    className="mt-4 px-4 py-1.5 text-xs font-bold rounded-full bg-brand-pink text-white hover:bg-brand-pink-light transition-colors"
                  >
                    Reset All Filters
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
                  {filteredProducts.map((prod) => {
                    const finalPrice = prod.base_price * (1 - prod.discount_percent / 100);
                    const avgRating = prod.reviews.length > 0
                      ? (prod.reviews.reduce((sum, r) => sum + r.rating, 0) / prod.reviews.length).toFixed(1)
                      : '5.0';

                    return (
                      <div 
                        key={prod.id}
                        className="group bg-white rounded-3xl border border-rose-100/60 shadow-xs overflow-hidden transform hover:-translate-y-1 hover:shadow-md transition-all duration-300"
                        id={`product-${prod.id}`}
                      >
                        {/* Hover Image block */}
                        <div 
                          className="relative h-64 bg-rose-50/25 overflow-hidden cursor-pointer"
                          onClick={() => {
                            setSelectedProductSlug(prod.slug);
                            setView('product-detail');
                          }}
                        >
                          <img 
                            src={prod.display_image_url} 
                            alt={prod.name}
                            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                            referrerPolicy="no-referrer"
                          />
                          <img 
                            src={prod.secondary_image_url} 
                            alt={`${prod.name} layout`}
                            className="absolute inset-0 w-full h-full object-cover opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                            referrerPolicy="no-referrer"
                          />
                          
                          {/* Slashed Discount badge */}
                          {prod.discount_percent > 0 && (
                            <span className="absolute top-4 left-4 z-10 px-2.5 py-1 text-[9px] font-bold font-mono tracking-wider text-white bg-brand-pink rounded-md">
                              {prod.discount_percent}% OFF
                            </span>
                          )}

                          {prod.is_bestseller && (
                            <span className="absolute top-4 right-4 z-10 px-2.5 py-1 text-[9px] font-bold font-mono tracking-wider text-white bg-brand-gold rounded-md">
                              BESTSELLER
                            </span>
                          )}
                        </div>

                        {/* Card Info Details */}
                        <div className="p-6 space-y-4">
                          <div className="flex justify-between items-start gap-4">
                            <h3 
                              onClick={() => {
                                setSelectedProductSlug(prod.slug);
                                setView('product-detail');
                              }}
                              className="text-sm font-bold text-neutral-800 hover:text-brand-pink transition-colors font-display line-clamp-1 cursor-pointer"
                            >
                              {prod.name}
                            </h3>
                            <button
                              onClick={() => handleToggleWishlist(prod.id)}
                              className="text-gray-400 hover:text-brand-pink shrink-0 transition-colors"
                            >
                              <Heart 
                                size={18} 
                                className={wishlist.includes(prod.id) ? 'fill-brand-pink text-brand-pink' : ''} 
                              />
                            </button>
                          </div>

                          <p className="text-[11px] text-gray-500 line-clamp-2 leading-relaxed h-8">
                            {prod.short_description}
                          </p>

                          {/* Star Rating Panel */}
                          <div className="flex items-center gap-1.5 text-brand-gold">
                            <Star size={12} className="fill-brand-gold" />
                            <span className="text-xs font-bold text-neutral-800 leading-none">{avgRating}</span>
                            <span className="text-[10px] text-gray-400 font-mono">({prod.reviews.length})</span>
                          </div>

                          {/* Price Tag Footer & Action button */}
                          <div className="flex items-center justify-between pt-2 border-t border-rose-50">
                            <div className="flex items-baseline gap-2">
                              <span className="text-sm font-bold text-brand-pink">₹{finalPrice.toFixed(0)}</span>
                              {prod.discount_percent > 0 && (
                                <span className="text-[11px] text-gray-400 line-through">₹{prod.base_price}</span>
                              )}
                            </div>
                            
                            <button
                              onClick={() => {
                                handleAddToCart(prod);
                                alert(`Added ${prod.name} to shopping bag!`);
                              }}
                              className="px-4 py-1.5 text-xs font-semibold rounded-full bg-rose-50 border border-rose-100 text-brand-pink hover:bg-brand-pink hover:text-white hover:border-brand-pink transition-all"
                            >
                              Add to Bag
                            </button>
                          </div>
                        </div>

                      </div>
                    );
                  })}
                </div>
              )}

              {/* USP/Trust Elements Row */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-16 border-t border-rose-100/40 mt-16 font-sans">
                <div className="p-6 rounded-2xl bg-white border border-rose-100/50 flex gap-4 items-start">
                  <div className="w-10 h-10 rounded-full bg-rose-50 flex items-center justify-center text-brand-pink shrink-0">
                    <Truck size={18} />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-neutral-800">FREE Shipping above ₹499</h4>
                    <p className="text-[11px] text-gray-400 mt-1 leading-relaxed">Fast premium delivery via BlueDart logistics. Orders processed within 24 hours.</p>
                  </div>
                </div>
                <div className="p-6 rounded-2xl bg-white border border-rose-100/50 flex gap-4 items-start">
                  <div className="w-10 h-10 rounded-full bg-rose-50 flex items-center justify-center text-brand-pink shrink-0">
                    <RefreshCw size={18} />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-neutral-800">Easy Replacement & Returns</h4>
                    <p className="text-[11px] text-gray-400 mt-1 leading-relaxed">Damage during shipment? Report it via Support Desk to get quick replacement dispatches.</p>
                  </div>
                </div>
                <div className="p-6 rounded-2xl bg-white border border-rose-100/50 flex gap-4 items-start">
                  <div className="w-10 h-10 rounded-full bg-rose-50 flex items-center justify-center text-brand-pink shrink-0">
                    <ShieldCheck size={18} />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-neutral-800">100% Authentic Quality</h4>
                    <p className="text-[11px] text-gray-400 mt-1 leading-relaxed">Each Jhumka piece is quality tested, hand-carved, and sealed in traditional velvet boxes.</p>
                  </div>
                </div>
              </div>

            </div>
          </div>
        )}

        {/* VIEW: PRODUCT DETAIL */}
        {view === 'product-detail' && selectedProduct && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 font-sans">
            
            {/* Back rail link */}
            <button
              onClick={() => { setView('home'); setSelectedProduct(null); setSelectedProductSlug(''); }}
              className="flex items-center gap-1.5 text-xs text-gray-600 hover:text-brand-pink font-semibold mb-6 transition-colors"
            >
              <ArrowLeft size={14} /> Back to Catalog
            </button>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-12">
              
              {/* Product Gallery Images Column */}
              <div className="space-y-4">
                <div className="relative h-[420px] rounded-3xl bg-white border border-rose-100 overflow-hidden shadow-xs">
                  <img 
                    src={selectedProduct.gallery_urls[activeGalleryIdx] || selectedProduct.display_image_url} 
                    alt={selectedProduct.name}
                    className="w-full h-full object-cover"
                    referrerPolicy="no-referrer"
                  />
                </div>
                <div className="flex gap-3">
                  {selectedProduct.gallery_urls.map((url, gIdx) => (
                    <button
                      key={gIdx}
                      onClick={() => setActiveGalleryIdx(gIdx)}
                      className={`w-20 h-20 rounded-xl overflow-hidden border bg-white transition-all ${
                        activeGalleryIdx === gIdx ? 'border-brand-pink ring-2 ring-brand-pink-light/30' : 'border-rose-100 hover:border-brand-pink-light'
                      }`}
                    >
                      <img src={url} alt="thumbnail" className="w-full h-full object-cover" referrerPolicy="no-referrer" />
                    </button>
                  ))}
                </div>
              </div>

              {/* Product Specifications & Details Column */}
              <div className="space-y-6">
                <div>
                  <span className="text-[10px] font-bold font-mono tracking-widest text-brand-pink uppercase bg-rose-50 px-2.5 py-1 rounded-md">
                    {selectedProduct.category}
                  </span>
                  <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-neutral-800 mt-3 font-display">
                    {selectedProduct.name}
                  </h1>
                </div>

                <div className="flex items-baseline gap-3">
                  <span className="text-2xl font-bold text-brand-pink">
                    ₹{(selectedProduct.base_price * (1 - selectedProduct.discount_percent / 100)).toFixed(0)}
                  </span>
                  {selectedProduct.discount_percent > 0 && (
                    <>
                      <span className="text-sm text-gray-400 line-through">₹{selectedProduct.base_price}</span>
                      <span className="text-xs font-bold text-brand-gold bg-brand-gold/10 px-2 py-0.5 rounded-sm">
                        {selectedProduct.discount_percent}% OFF
                      </span>
                    </>
                  )}
                </div>

                <p className="text-xs text-gray-600 leading-relaxed">
                  {selectedProduct.description}
                </p>

                {/* Technical Specifications Grid */}
                <div className="p-5 rounded-2xl bg-white border border-rose-50/80 space-y-3">
                  <h4 className="text-[11px] font-bold font-mono uppercase tracking-wider text-neutral-800">Jewellery Specifications</h4>
                  <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-xs">
                    <div className="flex justify-between py-1 border-b border-rose-50/30">
                      <span className="text-gray-400">Box Contents</span>
                      <span className="font-semibold text-neutral-800">{selectedProduct.variants[0]?.size || '12 Pairs'}</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-rose-50/30">
                      <span className="text-gray-400">Core Material</span>
                      <span className="font-semibold text-neutral-800">{selectedProduct.material}</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-rose-50/30">
                      <span className="text-gray-400">Metal Finish</span>
                      <span className="font-semibold text-neutral-800 capitalize">{selectedProduct.finish}</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-rose-50/30">
                      <span className="text-gray-400">Polish Warranty</span>
                      <span className="font-semibold text-neutral-800">{selectedProduct.warranty}</span>
                    </div>
                  </div>
                </div>

                {/* Care guidelines */}
                <div className="text-xs space-y-1.5 text-gray-600 leading-relaxed">
                  <p className="font-bold text-neutral-800">Care Instructions & Ingredients:</p>
                  <p className="italic">"{selectedProduct.ingredients}"</p>
                </div>

                {/* Add To Cart actions */}
                <div className="flex gap-4 pt-4 border-t border-rose-100">
                  <button
                    onClick={() => {
                      handleAddToCart(selectedProduct);
                      alert(`Added ${selectedProduct.name} to your shopping bag.`);
                    }}
                    className="flex-1 py-3 px-6 rounded-full bg-brand-pink text-white font-bold text-xs uppercase tracking-wider hover:bg-brand-pink-light shadow-md transition-all text-center"
                  >
                    Add to Shopping Bag
                  </button>
                  <button
                    onClick={() => {
                      handleAddToCart(selectedProduct);
                      setView('cart');
                    }}
                    className="px-6 py-3 rounded-full bg-neutral-900 text-white font-bold text-xs uppercase tracking-wider hover:bg-neutral-800 transition-colors"
                  >
                    Buy Now
                  </button>
                </div>

              </div>
            </div>

            {/* Custom Review Section for detail */}
            <div className="pt-10 border-t border-rose-100/40">
              <ReviewSection
                productId={selectedProduct.id}
                reviews={selectedProduct.reviews}
                onAddReview={handlePostReview}
                userEmail={user?.email}
              />
            </div>

          </div>
        )}

        {/* VIEW: SHOPPING CART */}
        {view === 'cart' && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 font-sans">
            <h1 className="text-2xl font-bold tracking-tight text-brand-pink font-display">Shopping Bag</h1>
            <p className="text-xs text-gray-400 font-sans mt-1 mb-8">Review your selected Jhumka boxes and proceed to secure checkout.</p>

            {cart.length === 0 ? (
              <div className="text-center py-20 bg-white rounded-3xl border border-rose-100 shadow-xs">
                <ShoppingBag size={48} className="mx-auto text-gray-200 mb-3" />
                <p className="text-sm font-semibold text-gray-600">Your shopping bag is empty.</p>
                <p className="text-xs text-gray-400 mt-1">Check out our handcrafted box sets and add them to your cart!</p>
                <button
                  onClick={() => setView('home')}
                  className="mt-6 px-6 py-2 rounded-full bg-brand-pink text-white text-xs font-bold hover:bg-brand-pink-light transition-all shadow-sm"
                >
                  Browse Box Sets
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
                
                {/* Cart list panel */}
                <div className="lg:col-span-2 space-y-4">
                  {cart.map((item) => (
                    <div 
                      key={item.id}
                      className="p-4 rounded-2xl border border-rose-100/50 bg-white flex gap-4 items-center justify-between"
                    >
                      <div className="flex gap-4 items-center min-w-0">
                        <div className="w-16 h-16 rounded-xl overflow-hidden shrink-0 border border-rose-50">
                          <img src={item.display_image_url} alt={item.productName} className="w-full h-full object-cover" referrerPolicy="no-referrer" />
                        </div>
                        <div className="min-w-0">
                          <h4 className="text-xs font-bold text-neutral-800 truncate">{item.productName}</h4>
                          <span className="text-[10px] text-gray-400 font-mono block mt-0.5">{item.variantLabel}</span>
                          <span className="text-xs font-bold text-brand-pink block mt-1">₹{item.sellingPrice.toFixed(0)}</span>
                        </div>
                      </div>

                      {/* Quantity controls */}
                      <div className="flex items-center gap-3">
                        <div className="flex items-center border border-rose-100 rounded-lg overflow-hidden bg-rose-50/20">
                          <button
                            onClick={() => updateCartQuantity(item.id, item.quantity - 1)}
                            className="px-2 py-1 text-xs hover:bg-rose-100/30 font-bold"
                          >
                            -
                          </button>
                          <span className="px-3 text-xs font-bold text-neutral-800">{item.quantity}</span>
                          <button
                            onClick={() => updateCartQuantity(item.id, item.quantity + 1)}
                            className="px-2 py-1 text-xs hover:bg-rose-100/30 font-bold"
                          >
                            +
                          </button>
                        </div>
                        <button
                          onClick={() => updateCartQuantity(item.id, 0)}
                          className="text-gray-400 hover:text-red-500 transition-colors p-1"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>

                    </div>
                  ))}
                </div>

                {/* Billing Summary Panel */}
                <div className="space-y-6">
                  
                  {/* Coupon card */}
                  <div className="p-5 rounded-2xl bg-white border border-rose-100/80 shadow-xs space-y-3">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-800 flex items-center gap-1.5">
                      <Ticket size={14} className="text-brand-pink" />
                      Promo Code
                    </h4>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="Try: JHUMKA10"
                        value={couponCode}
                        onChange={e => setCouponCode(e.target.value)}
                        className="flex-grow p-2 text-xs border border-rose-100 rounded-lg uppercase bg-rose-50/10 focus:outline-hidden"
                      />
                      <button
                        onClick={handleApplyCoupon}
                        className="px-4 py-2 bg-brand-pink text-white text-xs font-bold rounded-lg hover:bg-brand-pink-light"
                      >
                        Apply
                      </button>
                    </div>
                    {couponError && <p className="text-[10px] text-red-500 font-semibold">{couponError}</p>}
                    {appliedCoupon && (
                      <div className="p-2 rounded-lg bg-emerald-50 border border-emerald-100 text-emerald-800 text-[10px] font-bold flex justify-between">
                        <span>Code JHUMKA10 Active (10% off)</span>
                        <button onClick={() => setAppliedCoupon('')} className="text-emerald-950 font-bold hover:underline">Remove</button>
                      </div>
                    )}
                  </div>

                  {/* Pricing receipt */}
                  <div className="p-6 rounded-2xl bg-white border border-rose-100/80 shadow-xs space-y-4">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-800">Order Invoice</h4>
                    
                    <div className="space-y-2 text-xs">
                      <div className="flex justify-between py-1">
                        <span className="text-gray-500">Cart Subtotal</span>
                        <span className="font-semibold text-neutral-800">₹{cartSubtotal.toFixed(2)}</span>
                      </div>
                      {couponDiscount > 0 && (
                        <div className="flex justify-between py-1 text-emerald-600 font-medium">
                          <span>Coupon Discount (10%)</span>
                          <span>- ₹{couponDiscount.toFixed(2)}</span>
                        </div>
                      )}
                      <div className="flex justify-between py-1 border-b border-rose-50 pb-2">
                        <span className="text-gray-500">Delivery Charge</span>
                        <span className="font-semibold text-neutral-800">
                          {cartShipping === 0 ? <span className="text-emerald-600 font-bold">FREE Delivery</span> : `₹${cartShipping.toFixed(2)}`}
                        </span>
                      </div>
                      <div className="flex justify-between py-2 text-sm font-bold text-brand-dark">
                        <span>Grand Total</span>
                        <span className="text-brand-pink font-display">₹{cartGrandTotal.toFixed(2)}</span>
                      </div>
                    </div>

                    {/* Shipping Address Selection inside Checkout */}
                    {isLoggedIn ? (
                      <div className="space-y-3 pt-4 border-t border-rose-50">
                        <h5 className="text-[11px] font-bold uppercase text-gray-500">Shipping Destination</h5>
                        {user?.addresses && user.addresses.length > 0 ? (
                          <div className="space-y-2">
                            <select
                              value={selectedAddressId}
                              onChange={e => setSelectedAddressId(e.target.value)}
                              className="w-full text-xs p-2 rounded-lg border border-rose-100 bg-rose-50/20"
                            >
                              {user.addresses.map(a => (
                                <option key={a.id} value={a.id}>
                                  {a.type.toUpperCase()}: {a.full_name} ({a.pincode})
                                </option>
                              ))}
                            </select>
                            
                            <p className="text-[10px] text-gray-400">
                              Need to change addresses? Do so under address books in account settings.
                            </p>
                          </div>
                        ) : (
                          <div className="text-center py-3 bg-rose-50/25 rounded-xl border border-rose-100">
                            <p className="text-[10px] text-gray-500 font-sans">No shipping address added to profile.</p>
                            <button
                              onClick={() => setView('dashboard')}
                              className="text-[10px] text-brand-pink font-bold underline mt-1"
                            >
                              Add Address in Dashboard
                            </button>
                          </div>
                        )}

                        <button
                          onClick={handlePlaceOrder}
                          disabled={user?.addresses.length === 0}
                          className="w-full py-3 bg-brand-pink text-white text-xs uppercase tracking-widest font-bold rounded-full hover:bg-brand-pink-light shadow-md transition-all flex items-center justify-center gap-1.5 disabled:opacity-50"
                        >
                          Place Order (Cash On Delivery) <ArrowRight size={14} />
                        </button>
                      </div>
                    ) : (
                      <div className="pt-4 border-t border-rose-50 space-y-3">
                        <p className="text-xs text-gray-500 text-center leading-relaxed">
                          Please log in to register shipping addresses and complete your order.
                        </p>
                        <button
                          onClick={() => setView('login')}
                          className="w-full py-3 bg-neutral-900 text-white text-xs uppercase tracking-widest font-bold rounded-full hover:bg-neutral-800 transition-colors text-center"
                        >
                          Sign In with OTP
                        </button>
                      </div>
                    )}

                  </div>
                </div>

              </div>
            )}

          </div>
        )}

        {/* VIEW: BOOKMARK WISHLIST */}
        {view === 'wishlist' && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 font-sans">
            <h1 className="text-2xl font-bold tracking-tight text-brand-pink font-display">My Wishlist</h1>
            <p className="text-xs text-gray-400 font-sans mt-1 mb-8">Your saved favorites for future purchase.</p>

            {wishlist.length === 0 ? (
              <div className="text-center py-20 bg-white rounded-3xl border border-rose-100 shadow-xs">
                <Heart size={48} className="mx-auto text-gray-200 mb-3" />
                <p className="text-sm font-semibold text-gray-600">Your wishlist is empty.</p>
                <p className="text-xs text-gray-400 mt-1">Tap the heart on any product card to bookmark it.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
                {products.filter(p => wishlist.includes(p.id)).map((prod) => {
                  const finalPrice = prod.base_price * (1 - prod.discount_percent / 100);
                  return (
                    <div 
                      key={prod.id}
                      className="bg-white rounded-3xl border border-rose-100/50 overflow-hidden shadow-xs relative p-5 space-y-4"
                    >
                      <div className="h-44 rounded-2xl overflow-hidden bg-rose-50/20">
                        <img src={prod.display_image_url} alt={prod.name} className="w-full h-full object-cover" referrerPolicy="no-referrer" />
                      </div>
                      
                      <div className="flex justify-between items-start gap-4">
                        <h4 className="text-xs font-bold text-neutral-800 line-clamp-1">{prod.name}</h4>
                        <button 
                          onClick={() => handleToggleWishlist(prod.id)}
                          className="text-brand-pink"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>

                      <div className="flex justify-between items-center pt-2 border-t border-rose-50">
                        <span className="text-xs font-bold text-brand-pink">₹{finalPrice.toFixed(0)}</span>
                        <button
                          onClick={() => {
                            handleAddToCart(prod);
                            alert(`Added ${prod.name} to shopping bag.`);
                          }}
                          className="px-3 py-1 text-[10px] font-bold rounded-full bg-rose-50 border border-rose-100 text-brand-pink hover:bg-brand-pink hover:text-white"
                        >
                          Add to Bag
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* VIEW: SIMULATED OTP LOGIN */}
        {view === 'login' && (
          <div className="max-w-md mx-auto px-4 py-16 font-sans">
            <div className="bg-white rounded-3xl border border-rose-100 p-8 shadow-sm space-y-6">
              
              <div className="text-center space-y-1.5">
                <div className="w-12 h-12 rounded-full bg-rose-50 text-brand-pink flex items-center justify-center mx-auto mb-3">
                  <ShieldCheck size={24} />
                </div>
                <h2 className="text-xl font-bold tracking-tight text-neutral-800 font-display">Simulated OTP Login</h2>
                <p className="text-xs text-gray-400">Authenticate instantly to record order histories, checkouts, and filing support complaints.</p>
              </div>

              {authError && (
                <div className="p-3 bg-red-50 text-red-800 text-xs font-medium rounded-xl">
                  {authError}
                </div>
              )}

              {/* simulated notification box containing active OTP code for quick copy testing */}
              {visibleOtpCode && (
                <div className="p-3 bg-amber-50 border border-amber-100 rounded-xl space-y-1 text-center">
                  <span className="text-[10px] font-bold text-amber-800 uppercase tracking-wider block font-mono">Simulated OTP Code Sent</span>
                  <p className="text-sm font-extrabold text-neutral-800 font-mono tracking-widest">{visibleOtpCode}</p>
                  <p className="text-[9px] text-gray-400">Copy this code and input below to log in successfully.</p>
                </div>
              )}

              {!otpSent ? (
                <form onSubmit={handleRequestOtp} className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-600 mb-1">Email Address *</label>
                    <input
                      type="email"
                      required
                      value={authEmail}
                      onChange={e => setAuthEmail(e.target.value)}
                      placeholder="E.g., demo@hypehaven.com"
                      className="w-full text-xs p-3 rounded-lg border border-rose-100 bg-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-600 mb-1">Phone Number (Optional)</label>
                    <input
                      type="tel"
                      value={authPhone}
                      onChange={e => setAuthPhone(e.target.value)}
                      placeholder="10-digit number"
                      className="w-full text-xs p-3 rounded-lg border border-rose-100 bg-white"
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full py-3 rounded-full bg-brand-pink text-white font-bold text-xs uppercase tracking-wider hover:bg-brand-pink-light shadow-sm"
                  >
                    Send Simulated OTP Code
                  </button>
                </form>
              ) : (
                <form onSubmit={handleVerifyOtp} className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-600 mb-1">Enter 6-Digit OTP *</label>
                    <input
                      type="text"
                      required
                      maxLength={6}
                      value={authOtp}
                      onChange={e => setAuthOtp(e.target.value)}
                      placeholder="123456"
                      className="w-full text-center text-sm font-mono tracking-widest p-3 rounded-lg border border-rose-100 bg-white"
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full py-3 rounded-full bg-brand-pink text-white font-bold text-xs uppercase tracking-wider hover:bg-brand-pink-light shadow-sm"
                  >
                    Verify & Access Profile
                  </button>
                  <button
                    type="button"
                    onClick={() => { setOtpSent(false); setAuthOtp(''); }}
                    className="w-full text-center text-xs text-gray-400 hover:underline"
                  >
                    Go Back / Change Email
                  </button>
                </form>
              )}

            </div>
          </div>
        )}

        {/* VIEW: ACCOUNT DASHBOARD */}
        {view === 'dashboard' && isLoggedIn && user && (
          <Dashboard
            sessionId={localStorage.getItem('hypehaven_session') || ''}
            userEmail={user.email}
            userPhone={user.phone}
            addresses={user.addresses || []}
            onSaveAddress={handleSaveAddress}
            onDeleteAddress={handleDeleteAddress}
          />
        )}

      </main>

      {/* FOOTER */}
      <Footer />

      {/* ORDER PLACEMENT CONGRATS OVERLAY */}
      {placedOrder && (
        <div className="fixed inset-0 bg-neutral-950/60 z-50 flex items-center justify-center p-4 backdrop-blur-xs font-sans">
          <div className="bg-white rounded-3xl border border-rose-100 p-8 max-w-md w-full text-center space-y-5 animate-fade-in shadow-lg">
            <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto">
              <CheckCircle size={36} />
            </div>
            
            <div className="space-y-1.5">
              <h3 className="text-xl font-bold text-neutral-800 font-display">Order Confirmed! 😍</h3>
              <p className="text-xs text-gray-400 leading-relaxed">
                Thank you for buying my product! Your handcrafted Jhumka box set has been booked under order code:
              </p>
              <span className="inline-block px-3 py-1 bg-rose-50 text-brand-pink font-mono font-extrabold text-xs rounded-md">
                {placedOrder.order_id}
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-neutral-50 border border-neutral-100 text-left space-y-2 text-xs text-neutral-600">
              <p className="font-bold text-neutral-800">Summary Details:</p>
              <div className="flex justify-between">
                <span>Shipping Method</span>
                <span className="font-semibold text-neutral-800">Cash On Delivery</span>
              </div>
              <div className="flex justify-between">
                <span>Total Amount Paid</span>
                <span className="font-bold text-brand-pink">INR {placedOrder.grand_total.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>Courier Logistics</span>
                <span className="font-semibold text-neutral-800">BlueDart Express</span>
              </div>
            </div>

            <div className="space-y-2">
              <button
                onClick={() => {
                  setPlacedOrder(null);
                  setView('dashboard');
                }}
                className="w-full py-2.5 rounded-full bg-brand-pink text-white text-xs font-bold uppercase tracking-wider hover:bg-brand-pink-light transition-colors"
              >
                Track Shipping Steps
              </button>
              <button
                onClick={() => {
                  setPlacedOrder(null);
                  setView('home');
                }}
                className="w-full py-2.5 rounded-full border border-gray-200 text-gray-600 text-xs font-bold uppercase tracking-wider hover:bg-gray-50 transition-colors"
              >
                Continue Shopping
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
