/* Glamour Store - Main JavaScript */

const CSRF = () => document.cookie.split(';').map(c => c.trim()).find(c => c.startsWith('csrftoken='))?.split('=')[1] || '';

const api = async (url, data = {}) => {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF() },
    body: JSON.stringify(data)
  });
  return res.json();
};

/* ====== TOAST ====== */
function showToast(msg, type = 'success') {
  const toast = document.getElementById('cartToast');
  if (!toast) return;
  const msgEl = document.getElementById('cartToastMsg');
  if (msgEl) msgEl.textContent = msg;
  toast.className = 'cart-toast show';
  if (type === 'error') toast.style.background = '#ef4444';
  else toast.style.background = '#1a1a1a';
  setTimeout(() => { toast.className = 'cart-toast'; }, 3000);
}

/* ====== CART BADGE ====== */
function updateCartBadge(count) {
  const badges = document.querySelectorAll('.cart-badge, #cartBadge');
  badges.forEach(b => { b.textContent = count; b.style.display = count > 0 ? 'flex' : 'none'; });
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

  if (data.success) {
    updateCartBadge(data.cart_count);
    showToast(data.message || 'Added to cart!');
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

  if (data.success) {
    if (data.removed) {
      const row = document.getElementById(`cart-item-${itemId}`);
      if (row) row.remove();
      updateCartBadge(data.cart_count);
      showToast('Item removed');
      if (document.querySelectorAll('[data-cart-item]').length === 0) location.reload();
    } else {
      const qtyEl = document.getElementById(`qty-${itemId}`);
      const totalEl = document.getElementById(`total-${itemId}`);
      if (qtyEl) qtyEl.textContent = data.quantity;
      if (totalEl) totalEl.textContent = '₹' + data.item_total.toFixed(2);
      updateCartBadge(data.cart_count);
      refreshOrderSummary(data);
    }
  }
});

function refreshOrderSummary(data) {
  const sub = document.getElementById('summary-subtotal');
  const total = document.getElementById('summary-total');
  if (sub) sub.textContent = '₹' + data.cart_subtotal.toFixed(2);
  if (total) total.textContent = '₹' + data.cart_total.toFixed(2);
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

/* ====== PRODUCT GALLERY ====== */
document.querySelectorAll('.gallery-thumb').forEach(thumb => {
  thumb.addEventListener('click', () => {
    const mainImg = document.querySelector('.gallery-main img');
    if (mainImg) mainImg.src = thumb.dataset.src;
    document.querySelectorAll('.gallery-thumb').forEach(t => t.classList.remove('active'));
    thumb.classList.add('active');
  });
});

/* ====== VARIANT SELECTOR ====== */
document.querySelectorAll('.variant-btn').forEach(btn => {
  btn.addEventListener('click', async () => {
    if (btn.classList.contains('out-stock')) return;
    document.querySelectorAll('.variant-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');

    const variantId = btn.dataset.variantId;
    document.querySelectorAll('[data-add-cart]').forEach(b => b.dataset.variantId = variantId);

    const data = await fetch(`/api/variant/${variantId}/`).then(r => r.json());
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
          `<div class="search-suggestion-item" onclick="location.href='/products/${r.slug}/'">
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
  const end = new Date().setHours(23, 59, 59, 0);
  startTimer(timerEl, end);
}

/* ====== CHECKOUT ====== */
const checkoutForm = document.getElementById('checkoutForm');
if (checkoutForm) {
  checkoutForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const addrId = document.querySelector('input[name="address_id"]:checked')?.value;
    const payMethod = document.querySelector('input[name="payment_method"]:checked')?.value;

    if (!addrId) { showToast('Please select a delivery address', 'error'); return; }
    if (!payMethod) { showToast('Please select a payment method', 'error'); return; }

    const btn = checkoutForm.querySelector('[type=submit]');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Placing Order...';

    const data = await api('/checkout/place-order/', { address_id: addrId, payment_method: payMethod });

    if (data.success) {
      showToast('Order placed successfully!');
      setTimeout(() => location.href = data.redirect, 1000);
    } else {
      showToast(data.message, 'error');
      btn.disabled = false;
      btn.innerHTML = 'Place Order';
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
document.querySelector('[data-cancel-order]')?.addEventListener('click', async function () {
  if (!confirm('Are you sure you want to cancel this order?')) return;
  const orderId = this.dataset.cancelOrder;
  const data = await api(`/orders/${orderId}/cancel/`);
  if (data.success) { showToast(data.message); setTimeout(() => location.reload(), 1200); }
  else showToast(data.message, 'error');
});

/* ====== FADE IN CARDS ====== */
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('fade-in-up'); observer.unobserve(e.target); } });
}, { threshold: 0.1 });

document.querySelectorAll('.product-card, .category-card, .review-card').forEach(el => observer.observe(el));

/* ====== AUTO DISMISS ALERTS ====== */
setTimeout(() => {
  document.querySelectorAll('.glamour-alert').forEach(a => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(a);
    bsAlert.close();
  });
}, 5000);
