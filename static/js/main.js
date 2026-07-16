/* HYPEHAVENHUB - Main JavaScript */

const CSRF = () => document.cookie.split(';').map(c => c.trim()).find(c => c.startsWith('csrftoken='))?.split('=')[1] || '';

const api = async (url, data = {}) => {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF() },
    body: JSON.stringify(data)
  });
  let payload;
  try {
    payload = await res.json();
  } catch (err) {
    if (res.redirected && res.url) {
      window.location.href = res.url;
      return { success: false, requires_login: true };
    }
    return { success: false, message: 'Request failed. Please try again.' };
  }
  if (payload?.requires_login && payload.redirect) {
    if (payload.message) {
      alert(payload.message);
    }
    window.location.href = payload.redirect;
  }
  return payload;
};

/* ====== TOAST ====== */
function showToast(msg, type = 'success') {
  const toast = document.getElementById('cartToast');
  if (!toast) return;
  const msgEl = document.getElementById('cartToastMsg');
  if (msgEl) msgEl.textContent = msg;
  toast.className = 'cart-toast show';
  if (type === 'error') toast.style.background = '#ef4444';
  else toast.style.background = '#1d4ed8';
  setTimeout(() => { toast.className = 'cart-toast'; }, 3000);
}

/* ====== CART BADGE ====== */
function updateCartBadge(count) {
  const badges = document.querySelectorAll('.cart-badge, #cartBadge');
  badges.forEach(b => { b.textContent = count; b.style.display = count > 0 ? 'flex' : 'none'; });
}

/* ====== CART DRAWER ====== */
async function openCartDrawer() {
  const drawerEl = document.getElementById('cartDrawer');
  if (!drawerEl) return;
  const bsDrawer = bootstrap.Offcanvas.getOrCreateInstance(drawerEl);
  bsDrawer.show();
  const bodyEl = document.getElementById('cartDrawerBody');
  bodyEl.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
  try {
    const res = await fetch('/cart/drawer/');
    if (res.ok) {
      bodyEl.innerHTML = await res.text();
    } else {
      bodyEl.innerHTML = '<div class="text-danger text-center py-4">Failed to load cart.</div>';
    }
  } catch (err) {
    bodyEl.innerHTML = '<div class="text-danger text-center py-4">Error loading cart.</div>';
  }
}

/* ====== ADD TO CART ====== */
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('[data-add-cart]');
  if (!btn) return;
  e.preventDefault();
  const productId = btn.dataset.productId;
  const variantId = btn.dataset.variantId || null;
  const qty = parseInt(document.getElementById('qtyInput')?.value || 1);

  btn.disabled = true;
  const original = btn.innerHTML;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Adding...';

  const data = await api('/cart/add/', { product_id: productId, variant_id: variantId, quantity: qty });

  btn.disabled = false;
  btn.innerHTML = original;

  if (data.requires_login) return;

  if (data.success) {
    updateCartBadge(data.cart_count);
    showToast(data.message || 'Added to cart!');
    if (typeof openCartDrawer === 'function') openCartDrawer();
  } else {
    showToast(data.message || 'Something went wrong', 'error');
  }
});

/* ====== CART PAGE: UPDATE / REMOVE ====== */
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('[data-cart-action]');
  if (!btn) return;

  const action = btn.dataset.cartAction;
  const itemId = btn.dataset.itemId;
  const data = await api('/cart/update/', { item_id: itemId, action });
  if (data.requires_login) return;

  if (data.success) {
    if (data.removed) {
      /* Reload the page so the server re-renders with correct totals */
      showToast('Item removed');
      updateCartBadge(data.cart_count);
      setTimeout(() => location.reload(), 300);
    } else {
      const qtyEl = document.getElementById(`qty-${itemId}`);
      const totalEl = document.getElementById(`total-${itemId}`);
      if (qtyEl) qtyEl.textContent = data.quantity;
      if (totalEl) totalEl.textContent = '₹' + Math.round(data.item_total);
      updateCartBadge(data.cart_count);
      refreshOrderSummary(data);
    }
  }
});

function refreshOrderSummary(data) {
  const sub = document.getElementById('summary-subtotal');
  const total = document.getElementById('summary-total');
  if (sub) sub.textContent = '₹' + Math.round(data.cart_subtotal);
  if (total) total.textContent = '₹' + Math.round(data.cart_total);

  // Update item count text in the subtotal line
  const subtotalLabel = sub ? sub.parentElement.querySelector('.text-muted') : null;
  if (subtotalLabel) subtotalLabel.textContent = `Subtotal (${data.cart_count} items)`;

  // Update the header badge
  const headerBadge = document.querySelector('h2 .badge');
  if (headerBadge) headerBadge.textContent = `${data.cart_count} items`;

  // Update delivery line
  const deliveryVal = document.getElementById('delivery-value');
  if (deliveryVal) {
    if (data.delivery_charge === 0) {
      deliveryVal.innerHTML = '<span class="text-success">FREE</span>';
    } else {
      deliveryVal.innerHTML = '₹' + Math.round(data.delivery_charge);
    }
  }
}

/* ====== WISHLIST TOGGLE ====== */
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('[data-wishlist]');
  if (!btn) return;
  const productId = btn.dataset.productId;
  const data = await api('/wishlist/toggle/', { product_id: productId });
  if (data.success) {
    btn.classList.toggle('active', data.in_wishlist);
    const icon = btn.querySelector('i');
    if (icon) {
      icon.className = data.in_wishlist ? 'fas fa-heart' : 'far fa-heart';
    }
    showToast(data.message);
    const wBadges = document.querySelectorAll('.wishlist-count');
    wBadges.forEach(b => {
      const c = parseInt(b.textContent || 0);
      b.textContent = data.in_wishlist ? c + 1 : Math.max(0, c - 1);
    });
  }
});

/* ====== COUPON ====== */
const couponForm = document.getElementById('couponForm');
if (couponForm) {
  couponForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const code = document.getElementById('couponInput')?.value;
    const data = await api('/cart/coupon/apply/', { code });
    if (data.requires_login) return;
    const msg = document.getElementById('couponMsg');
    if (msg) {
      msg.textContent = data.message;
      msg.className = data.success ? 'text-success mt-2 small' : 'text-danger mt-2 small';
    }
    if (data.success) {
      refreshOrderSummary({ cart_subtotal: 0, cart_total: data.grand_total });
      const discRow = document.getElementById('discount-row');
      if (discRow) { discRow.style.display = 'flex'; document.getElementById('discount-amt').textContent = '-₹' + data.discount; }
    }
  });
}

/* ====== GALLERY MOVED TO PRODUCT_DETAIL.HTML ====== */

/* ====== VARIANT SELECTOR ====== */
document.querySelectorAll('.variant-btn').forEach(btn => {
  btn.addEventListener('click', async () => {
    if (btn.classList.contains('out-stock')) return;
    document.querySelectorAll('.variant-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');

    const variantId = btn.dataset.variantId;
    document.querySelectorAll('[data-add-cart]').forEach(b => b.dataset.variantId = variantId);

    const data = await fetch(`/api/variant-info/${variantId}/`).then(r => r.json());
    const priceEl = document.getElementById('detailPrice');
    if (priceEl) priceEl.textContent = '₹' + data.price.toFixed(2);

    const stockEl = document.getElementById('stockStatus');
    if (stockEl) {
      stockEl.textContent = data.in_stock ? `In Stock (${data.stock})` : 'Out of Stock';
      stockEl.className = data.in_stock ? 'badge bg-success' : 'badge bg-danger';
    }

    if (data.image) {
      const mainImg = document.querySelector('.gallery-main img');
      if (mainImg) mainImg.src = data.image;
    }
  });
});

/* ====== QTY SELECTOR ====== */
const qtyInp = document.getElementById('qtyInput');
document.querySelector('.qty-increase')?.addEventListener('click', () => { if (qtyInp) qtyInp.value = parseInt(qtyInp.value) + 1; });
document.querySelector('.qty-decrease')?.addEventListener('click', () => { if (qtyInp && parseInt(qtyInp.value) > 1) qtyInp.value = parseInt(qtyInp.value) - 1; });

/* ====== STAR RATING ====== */
const starInputs = document.querySelectorAll('.star-rating-input i');
starInputs.forEach((star, idx) => {
  star.addEventListener('mouseover', () => {
    starInputs.forEach((s, i) => s.classList.toggle('active', i <= idx));
  });
  star.addEventListener('mouseout', () => {
    const rating = parseInt(document.getElementById('ratingInput')?.value || 0);
    starInputs.forEach((s, i) => s.classList.toggle('active', i < rating));
  });
  star.addEventListener('click', () => {
    const rating = idx + 1;
    const inp = document.getElementById('ratingInput');
    if (inp) inp.value = rating;
    starInputs.forEach((s, i) => s.classList.toggle('active', i < rating));
  });
});

/* ====== SEARCH SUGGESTIONS ====== */
const searchInput = document.getElementById('searchInput');
const suggBox = document.getElementById('searchSuggestions');
let searchTimeout;

if (searchInput && suggBox) {
  searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    const q = searchInput.value.trim();
    if (q.length < 2) { suggBox.style.display = 'none'; return; }
    searchTimeout = setTimeout(async () => {
      const res = await fetch(`/search/suggestions/?q=${encodeURIComponent(q)}`).then(r => r.json());
      if (res.results.length) {
        suggBox.innerHTML = res.results.map(r =>
          `<div class="search-suggestion-item" onclick="location.href='/product/${r.slug}/'">
            <strong>${r.name}</strong><br><small class="text-muted">${r.brand}</small>
          </div>`
        ).join('');
        suggBox.style.display = 'block';
      } else {
        suggBox.style.display = 'none';
      }
    }, 300);
  });

  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target)) suggBox.style.display = 'none';
  });
}

/* ====== FLASH SALE COUNTDOWN ====== */
function startTimer(targetEl, endTime) {
  if (!targetEl) return;
  const update = () => {
    const diff = endTime - Date.now();
    if (diff <= 0) { targetEl.innerHTML = '<span>Sale Ended</span>'; return; }
    const h = Math.floor(diff / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    const s = Math.floor((diff % 60000) / 1000);
    document.getElementById('timerHH') && (document.getElementById('timerHH').textContent = String(h).padStart(2,'0'));
    document.getElementById('timerMM') && (document.getElementById('timerMM').textContent = String(m).padStart(2,'0'));
    document.getElementById('timerSS') && (document.getElementById('timerSS').textContent = String(s).padStart(2,'0'));
  };
  update();
  setInterval(update, 1000);
}

const timerEl = document.getElementById('flashTimer');
if (timerEl) {
  let end;
  if (timerEl.dataset.endTime) {
    end = new Date(timerEl.dataset.endTime).getTime();
  } else {
    end = new Date().setHours(23, 59, 59, 0);
  }
  startTimer(timerEl, end);
}

/* ====== CHECKOUT ====== */
const checkoutForm = document.getElementById('checkoutForm');
if (checkoutForm) {
  checkoutForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    console.log("Checkout form submitted");
    
    const addrId = document.querySelector('input[name="address_id"]:checked')?.value;
    const payMethod = document.querySelector('input[name="payment_method"]:checked')?.value;

    console.log("Selected Address ID:", addrId);
    console.log("Selected Payment Method:", payMethod);

    if (!addrId) { showToast('Please select a delivery address', 'error'); return; }
    if (!payMethod) { showToast('Please select a payment method', 'error'); return; }

    const btn = checkoutForm.querySelector('[type=submit]');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Placing Order...';

    try {
      const data = await api('/checkout/place-order/', { address_id: addrId, payment_method: payMethod });
      console.log("Place order response:", data);

      if (data && data.success) {
        if (data.payment_method === 'razorpay') {
          console.log("Initializing Razorpay checkout gateway");
          if (typeof Razorpay === 'undefined') {
            console.error("Razorpay script not loaded");
            showToast('Razorpay payment gateway is not loaded. Please disable ad-blockers and try again.', 'error');
            btn.disabled = false;
            btn.innerHTML = 'Place Order Securely';
            return;
          }

          try {
            const options = {
              "key": data.razorpay_key_id,
              "amount": data.amount,
              "currency": "INR",
              "name": "HYPEHAVENHUB",
              "description": "Premium Assorted Jhumka Box Sets",
              "order_id": data.razorpay_order_id,
              "line_items_total": data.line_items_total,
              "line_items": data.line_items,
              "one_click_checkout": true, // Enabled Razorpay Magic Checkout
              "handler": async function (paymentRes) {
                console.log("Razorpay payment successful response:", paymentRes);
                btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Verifying Payment...';
                try {
                  const verifyRes = await fetch('/checkout/verify-payment/', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'X-CSRFToken': checkoutForm.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({
                      razorpay_payment_id: paymentRes.razorpay_payment_id,
                      razorpay_order_id: paymentRes.razorpay_order_id,
                      razorpay_signature: paymentRes.razorpay_signature,
                      order_id: data.order_id
                    })
                  });
                  const verifyData = await verifyRes.json();
                  console.log("Payment verification response:", verifyData);
                  
                  if (verifyData && verifyData.success) {
                    showToast('Payment successful & order placed!');
                    if (verifyData.redirect) {
                      setTimeout(() => {
                        window.location.href = verifyData.redirect;
                      }, 1000);
                    } else {
                      showToast('Order placed successfully. Redirection failed.', 'error');
                    }
                  } else {
                    showToast(verifyData.message || 'Payment verification failed', 'error');
                    btn.disabled = false;
                    btn.innerHTML = 'Place Order Securely';
                  }
                } catch (err) {
                  console.error("Verification AJAX error:", err);
                  showToast('Error verifying payment. Contact support.', 'error');
                  btn.disabled = false;
                  btn.innerHTML = 'Place Order Securely';
                }
              },
              "prefill": {
                "name": data.customer_name,
                "email": data.customer_email,
                "contact": data.customer_phone
              },
              "theme": {
                "color": "#092c20"
              },
              "modal": {
                "ondismiss": function() {
                  console.log("Razorpay modal dismissed by user");
                  showToast('Payment cancelled.', 'error');
                  btn.disabled = false;
                  btn.innerHTML = 'Place Order Securely';
                }
              }
            };
            const rzp = new Razorpay(options);
            rzp.open();
          } catch (rzpErr) {
            console.error("Razorpay instance or open error:", rzpErr);
            showToast('Failed to open payment gateway: ' + rzpErr.message, 'error');
            btn.disabled = false;
            btn.innerHTML = 'Place Order Securely';
          }
        } else {
          showToast('Order placed successfully!');
          if (data.redirect) {
            setTimeout(() => location.href = data.redirect, 1000);
          } else {
            console.warn("COD order placed but no redirect URL provided");
          }
        }
      } else {
        showToast(data.message || 'Failed to place order', 'error');
        btn.disabled = false;
        btn.innerHTML = 'Place Order Securely';
      }
    } catch (apiErr) {
      console.error("API error during checkout place-order:", apiErr);
      showToast('Connection error. Please try again.', 'error');
      btn.disabled = false;
      btn.innerHTML = 'Place Order Securely';
    }
  });

  document.querySelectorAll('.address-card').forEach(card => {
    card.addEventListener('click', () => {
      card.querySelector('input[type=radio]').checked = true;
      document.querySelectorAll('.address-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
    });
  });

  document.querySelectorAll('.payment-method').forEach(pm => {
    pm.addEventListener('click', () => {
      pm.querySelector('input[type=radio]').checked = true;
      document.querySelectorAll('.payment-method').forEach(p => p.classList.remove('selected'));
      pm.classList.add('selected');
    });
  });
}

/* ====== CANCEL ORDER ====== */
document.querySelectorAll('[data-cancel-order]').forEach(btn => {
  btn.addEventListener('click', async function () {
    const confirmMsg = "Are you sure you want to cancel this order?\n\nIf you have already paid (e.g., via Razorpay), your refund will be automatically initiated and credited back to your original payment method within 5-7 working days.";
    if (!confirm(confirmMsg)) return;
    const orderId = this.dataset.cancelOrder;
    const data = await api(`/orders/${orderId}/cancel/`);
    if (data.success) { 
        showToast(data.message); 
        setTimeout(() => location.reload(), 2000); 
    }
    else {
        showToast(data.message, 'error');
    }
  });
});

/* ====== SMOOTH REVEAL ANIMATIONS ====== */
const revealEls = document.querySelectorAll([
  '.section-header',
  '.jewel-ad-inner',
  '.jewel-ad-tile',
  '.product-card',
  '.category-card',
  '.brand-pill',
  '.review-card',
  '.wishlist-card',
  '.cart-item',
  '.checkout-step',
  '.order-summary',
  '.filter-card',
  '.profile-sidebar',
  '.glamour-form-card'
].join(','));

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if ('IntersectionObserver' in window && !reduceMotion) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('fade-in-up');
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  revealEls.forEach((el, index) => {
    el.classList.add('reveal-ready');
    el.style.setProperty('--reveal-delay', `${Math.min(index % 8, 7) * 45}ms`);
    observer.observe(el);
  });
} else {
  revealEls.forEach(el => el.classList.add('fade-in-up'));
}

/* ====== AUTO DISMISS ALERTS ====== */
setTimeout(() => {
  document.querySelectorAll('.glamour-alert').forEach(a => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(a);
    bsAlert.close();
  });
}, 5000);

/* ====== HERO CAROUSEL ====== */
const setupHeroCarousel = () => {
  const carousel = document.querySelector('.hero-carousel');
  if (!carousel) return;
  
  const inner = carousel.querySelector('.carousel-inner');
  const slides = carousel.querySelectorAll('.carousel-slide');
  const prevBtn = carousel.querySelector('.carousel-control-prev');
  const nextBtn = carousel.querySelector('.carousel-control-next');
  const dots = carousel.querySelectorAll('.carousel-dot');
  const playPauseBtn = carousel.querySelector('.carousel-play-pause');
  
  let currentIndex = 0;
  let intervalId = null;
  let isPlaying = true;
  const slideDuration = 5000;
  
  const showSlide = (index) => {
    if (index < 0) index = slides.length - 1;
    if (index >= slides.length) index = 0;
    
    currentIndex = index;
    inner.style.transform = `translateX(-${currentIndex * 100}%)`;
    
    dots.forEach((dot, idx) => {
      dot.classList.toggle('active', idx === currentIndex);
    });
  };
  
  const nextSlide = () => showSlide(currentIndex + 1);
  const prevSlide = () => showSlide(currentIndex - 1);
  
  const startAutoplay = () => {
    if (intervalId) clearInterval(intervalId);
    intervalId = setInterval(nextSlide, slideDuration);
  };
  
  const stopAutoplay = () => {
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
  };
  
  if (prevBtn) prevBtn.addEventListener('click', () => { prevSlide(); if (isPlaying) startAutoplay(); });
  if (nextBtn) nextBtn.addEventListener('click', () => { nextSlide(); if (isPlaying) startAutoplay(); });
  
  dots.forEach((dot, idx) => {
    dot.addEventListener('click', () => {
      showSlide(idx);
      if (isPlaying) startAutoplay();
    });
  });
  
  if (playPauseBtn) {
    playPauseBtn.addEventListener('click', () => {
      isPlaying = !isPlaying;
      if (isPlaying) {
        playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
        startAutoplay();
      } else {
        playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
        stopAutoplay();
      }
    });
  }
  
  // Swipe gestures for mobile
  let touchStartX = 0;
  let touchEndX = 0;
  carousel.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });
  carousel.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    if (touchStartX - touchEndX > 50) {
      nextSlide();
      if (isPlaying) startAutoplay();
    } else if (touchEndX - touchStartX > 50) {
      prevSlide();
      if (isPlaying) startAutoplay();
    }
  }, { passive: true });
  
  if (isPlaying) startAutoplay();
};

/* ====== PRODUCT ROW SCROLL ====== */
const setupProductScrollRow = () => {
  const row = document.querySelector('.product-scroll-row');
  if (!row) return;
  
  const wrapper = row.querySelector('.product-scroll-wrapper');
  const prevBtn = row.querySelector('.scroll-prev');
  const nextBtn = row.querySelector('.scroll-next');
  
  if (!wrapper) return;
  
  const scrollAmount = 300;
  
  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      wrapper.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    });
  }
  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      wrapper.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    });
  }
  
  // Toggle scroll buttons visibility based on scroll position
  const toggleButtons = () => {
    if (prevBtn) prevBtn.style.opacity = wrapper.scrollLeft <= 5 ? '0.3' : '1';
    if (nextBtn) nextBtn.style.opacity = (wrapper.scrollLeft + wrapper.clientWidth >= wrapper.scrollWidth - 5) ? '0.3' : '1';
  };
  
  wrapper.addEventListener('scroll', toggleButtons);
  window.addEventListener('resize', toggleButtons);
  // Initial toggle
  setTimeout(toggleButtons, 200);
};

/* ====== QUICK VIEW MODAL ====== */
const setupQuickView = () => {
  const modalEl = document.getElementById('quickViewModal');
  if (!modalEl) return;
  
  const modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
  const contentContainer = document.getElementById('quickViewContent');
  
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-quick-view]');
    if (!btn) return;
    
    e.preventDefault();
    const productId = btn.dataset.productId;
    
    // Open modal and show spinner
    contentContainer.innerHTML = `
      <div class="text-center py-5 col-12">
        <i class="fas fa-spinner fa-spin fa-2x" style="color: var(--pink);"></i>
      </div>
    `;
    modalInstance.show();
    
    try {
      const res = await fetch(`/api/quick-view/${productId}/`);
      const data = await res.json();
      
      if (!data || data.detail) {
        contentContainer.innerHTML = '<div class="col-12 text-center text-danger py-4">Failed to load product details.</div>';
        return;
      }
      
      let variantsHtml = '';
      if (data.variants && data.variants.length > 0) {
        variantsHtml += '<div class="mb-4"><label class="fw-600 mb-2">Select Variant</label><select id="qvVariantSelect" class="form-select">';
        data.variants.forEach((v) => {
          const disabledStr = v.stock <= 0 ? ' (Out of stock)' : '';
          const disabledAttr = v.stock <= 0 ? 'disabled' : '';
          variantsHtml += `<option value="${v.id}" data-price="${v.price}" data-stock="${v.stock}" ${disabledAttr}>${v.label} - ₹${v.price}${disabledStr}</option>`;
        });
        variantsHtml += '</select></div>';
      }
       const isDiscounted = data.discount_percent > 0;
      const priceHtml = isDiscounted 
        ? `<span class="fs-3 fw-bold me-3" id="qvPrice" style="color: var(--primary);">${data.localized_selling_price}</span>
           <span class="text-decoration-line-through text-muted me-3" id="qvPriceOriginal" style="font-size: 14px;">${data.localized_base_price}</span>
           <span class="badge" style="background: var(--primary-fixed); color: var(--on-primary-fixed); border: 1px solid var(--outline-variant); font-size: 11px;">${data.discount_percent}% OFF</span>`
        : `<span class="fs-3 fw-bold" id="qvPrice" style="color: var(--primary);">${data.localized_selling_price}</span>`;
        
      contentContainer.innerHTML = `
        <div class="row g-4 align-items-center">
          <div class="col-md-6 text-center position-relative">
            <div class="position-relative overflow-hidden rounded shadow-sm">
              <img src="${data.image}" alt="${data.name}" class="img-fluid w-100 object-fit-cover" style="max-height: 400px; min-height: 300px;">
              <span class="position-absolute px-3 py-1 text-[9px] uppercase tracking-widest font-semibold" style="background: var(--primary-fixed); color: var(--on-primary-fixed); font-size: 10px; border-radius: 2px; top: 12px; left: 12px;">Atelier Original</span>
            </div>
          </div>
          <div class="col-md-6">
            <span class="text-uppercase fw-600 text-muted d-block mb-1" style="font-size: 10px; letter-spacing: 2px;">Heritage Series</span>
            <h3 style="font-family: var(--font-display); font-weight: 700; color: var(--primary);" class="mb-2 fs-2">${data.name}</h3>
            <div class="mb-3 d-flex align-items-center">
              ${priceHtml}
            </div>
            <p class="text-muted mb-4" style="font-size: 14px; line-height: 1.6;">${data.description}</p>
            
            <hr class="my-3" style="border-top: 1px solid var(--outline-variant); opacity: 0.25;">
            
            <div class="row g-2 mb-3" style="font-size: 13px;">
              <div class="col-6">
                <span class="text-uppercase fw-600 text-muted d-block mb-1" style="font-size: 9px; letter-spacing: 1px;">Material</span>
                <span class="fw-500" style="color: var(--on-surface);">${data.material || 'Oxidized Silver'}</span>
              </div>
              <div class="col-6">
                <span class="text-uppercase fw-600 text-muted d-block mb-1" style="font-size: 9px; letter-spacing: 1px;">Metal Purity</span>
                <span class="fw-500" style="color: var(--on-surface);">${data.metal_purity || '925 Sterling Silver'}</span>
              </div>
            </div>
            
            <hr class="my-3" style="border-top: 1px solid var(--outline-variant); opacity: 0.25;">
            
            ${variantsHtml}
            
            <div class="d-flex flex-column gap-2 mt-3">
              <button class="btn w-100 py-3" id="qvAddToCartBtn" style="background-color: var(--primary-fixed) !important; color: var(--on-primary-fixed) !important; border: none; font-size: 11px; font-weight: bold; letter-spacing: 0.15em; text-transform: uppercase; border-radius: 4px;">
                Add to Bag
              </button>
              <button class="btn w-100 py-3" id="qvBuyDirectlyBtn" style="background-color: var(--primary) !important; color: var(--on-primary) !important; border: 1px solid var(--outline-variant); font-size: 11px; font-weight: bold; letter-spacing: 0.15em; text-transform: uppercase; border-radius: 4px;">
                Buy Directly
              </button>
            </div>
          </div>
        </div>
      `;
      
      // Event listener for dynamic variant changes
      const variantSelect = document.getElementById('qvVariantSelect');
      const addToCartBtn = document.getElementById('qvAddToCartBtn');
      const qvPriceEl = document.getElementById('qvPrice');
      
      if (variantSelect) {
        variantSelect.addEventListener('change', () => {
          const selectedOption = variantSelect.options[variantSelect.selectedIndex];
          const newPrice = selectedOption.dataset.price;
          const newStock = selectedOption.dataset.stock;
          
          if (qvPriceEl) {
            const currencySymbol = data.localized_selling_price.replace(/[0-9.,]/g, '').trim();
            qvPriceEl.textContent = `${currencySymbol}${parseFloat(newPrice).toFixed(0)}`;
          }
          if (addToCartBtn) {
            if (parseInt(newStock) <= 0) {
              addToCartBtn.disabled = true;
              addToCartBtn.textContent = 'Out of Stock';
            } else {
              addToCartBtn.disabled = false;
              addToCartBtn.textContent = 'Add to Bag';
            }
          }
        });
      }
      
      // Event listener for dynamic add to cart
      if (addToCartBtn) {
        addToCartBtn.addEventListener('click', async (e) => {
          e.preventDefault();
          const selectedVariantId = variantSelect ? variantSelect.value : null;
          
          addToCartBtn.disabled = true;
          const originalText = addToCartBtn.textContent;
          addToCartBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Adding...';
          
          const cartRes = await api('/cart/add/', { 
            product_id: data.id, 
            variant_id: selectedVariantId, 
            quantity: 1 
          });
          
          addToCartBtn.disabled = false;
          addToCartBtn.textContent = originalText;
          
          if (cartRes.requires_login) {
            modalInstance.hide();
            return;
          }
          
          if (cartRes.success) {
            updateCartBadge(cartRes.cart_count);
            showToast(cartRes.message || 'Added to cart!');
            modalInstance.hide();
            if (typeof openCartDrawer === 'function') openCartDrawer();
          } else {
            showToast(cartRes.message || 'Something went wrong', 'error');
          }
        });
      }

      // Event listener for Buy Directly
      const buyDirectlyBtn = document.getElementById('qvBuyDirectlyBtn');
      if (buyDirectlyBtn) {
        buyDirectlyBtn.addEventListener('click', async (e) => {
          e.preventDefault();
          const selectedVariantId = variantSelect ? variantSelect.value : null;
          
          buyDirectlyBtn.disabled = true;
          const originalText = buyDirectlyBtn.textContent;
          buyDirectlyBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
          
          const cartRes = await api('/cart/add/', { 
            product_id: data.id, 
            variant_id: selectedVariantId, 
            quantity: 1 
          });
          
          buyDirectlyBtn.disabled = false;
          buyDirectlyBtn.textContent = originalText;
          
          if (cartRes.requires_login) {
            modalInstance.hide();
            window.initiateMagicCheckout(buyDirectlyBtn);
            return;
          }
          
          if (cartRes.success) {
            updateCartBadge(cartRes.cart_count);
            modalInstance.hide();
            window.initiateMagicCheckout(buyDirectlyBtn);
          } else {
            showToast(cartRes.message || 'Something went wrong', 'error');
          }
        });
      }
      
    } catch (err) {
      console.error("Quick View AJAX error:", err);
      contentContainer.innerHTML = '<div class="col-12 text-center text-danger py-4">Error loading product details.</div>';
    }
  });
};

// Run when DOM content is loaded
document.addEventListener('DOMContentLoaded', () => {
  setupHeroCarousel();
  setupProductScrollRow();
  setupQuickView();
});

/* ====== GLOBAL MAGIC CHECKOUT ====== */
window.initiateMagicCheckout = async function(btn, productId = null, variantId = null, quantity = null) {
  btn.style.pointerEvents = 'none';
  const originalHtml = btn.innerHTML;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';

  try {
    const data = await api('/razorpay/checkout/initiate/', {
      product_id: productId,
      variant_id: variantId,
      quantity: quantity
    });

    if (data.requires_login && data.redirect) {
      window.location.href = data.redirect;
      return;
    }

    if (data.success && data.razorpay_order_id) {
      if (typeof Razorpay === 'undefined') {
        await new Promise((resolve, reject) => {
          const script = document.createElement('script');
          script.src = 'https://checkout.razorpay.com/v1/magic-checkout.js';
          script.onload = resolve;
          script.onerror = reject;
          document.head.appendChild(script);
        });
      }

      var options = {
        "key": data.razorpay_key_id,
        "amount": data.amount,
        "currency": "INR",
        "name": "HYPEHAVENHUB",
        "description": "Order Payment",
        "order_id": data.razorpay_order_id,
        "line_items_total": data.line_items_total,
        "line_items": data.line_items,
        "one_click_checkout": true, // Enabled Razorpay Magic Checkout
        "handler": async function (response) {
          const verifyData = await api('/checkout/verify-payment/', {
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_order_id: response.razorpay_order_id,
            razorpay_signature: response.razorpay_signature,
            order_id: data.order_id
          });
          
          if (verifyData.success !== false) {
            window.location.href = "/orders/?status=SUCCESS";
          } else {
            alert("Payment verification failed. " + (verifyData.message || ""));
            window.location.href = "/orders/?status=FAILED";
          }
        },
        "theme": { "color": "#3b8c7b" },
        "modal": {
          "ondismiss": function() {
             console.log("Razorpay modal dismissed by user");
          }
        }
      };

      // Crucial for Magic Checkout: Do NOT send prefill if it's empty or guest
      if (data.customer_email || data.customer_phone || data.customer_name) {
        options.prefill = {};
        if (data.customer_name && data.customer_name !== 'Guest User') options.prefill.name = data.customer_name;
        if (data.customer_email && data.customer_email !== 'guest@hypehavenhub.com') options.prefill.email = data.customer_email;
        if (data.customer_phone) options.prefill.contact = data.customer_phone;
        if (Object.keys(options.prefill).length === 0) delete options.prefill;
      }

      var rzp1 = new Razorpay(options);
      rzp1.on('payment.failed', function (response){
        alert("Payment failed: " + response.error.description);
      });
      rzp1.open();
    } else {
      alert("Failed to initiate checkout: " + (data.message || "Unknown error"));
    }
  } catch (err) {
    console.error("Error initiating checkout:", err);
    alert("Something went wrong. Please try again later.");
  } finally {
    btn.style.pointerEvents = 'auto';
    btn.innerHTML = originalHtml;
  }
};
