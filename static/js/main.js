/**
 * CodeAlpha Commerce - Interactive JavaScript Frontend
 */

document.addEventListener('DOMContentLoaded', function () {
  initCartAjax();
  initQuantityButtons();
  initToastSystem();
  initCheckoutPaymentSelect();
});

/**
 * Get Django CSRF Cookie helper
 */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/**
 * Toast Notification Helper
 */
function showToast(message, type = 'success') {
  let container = document.getElementById('custom-toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'custom-toast-container';
    container.className = 'toast-container-custom';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `custom-toast ${type}`;
  const icon = type === 'success' ? 'bi-check-circle-fill text-success' : 'bi-info-circle-fill text-info';
  
  toast.innerHTML = `
    <i class="bi ${icon} fs-5"></i>
    <div class="flex-grow-1">${message}</div>
    <button type="button" class="btn-close btn-close-white ms-2" aria-label="Close"></button>
  `;

  const closeBtn = toast.querySelector('.btn-close');
  closeBtn.addEventListener('click', () => {
    toast.remove();
  });

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

function initToastSystem() {
  window.showToast = showToast;
}

/**
 * AJAX Add to Cart & Counter Badge Updates
 */
function initCartAjax() {
  document.querySelectorAll('.ajax-add-cart-form').forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const submitBtn = this.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;
      
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Adding...`;

      const formData = new FormData(this);
      const url = this.getAttribute('action');

      fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken') || ''
        }
      })
      .then(res => res.json())
      .then(data => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;

        if (data.status === 'success') {
          updateCartBadge(data.cart_count);
          showToast(data.message, 'success');
        } else {
          showToast(data.message || 'Error adding to cart', 'info');
        }
      })
      .catch(err => {
        console.error('Add to cart error:', err);
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        // Fallback to normal submit if JS fetch fails
        form.submit();
      });
    });
  });
}

function updateCartBadge(count) {
  const badges = document.querySelectorAll('.cart-count-badge');
  badges.forEach(badge => {
    badge.textContent = count;
    if (count > 0) {
      badge.style.display = 'flex';
      badge.classList.add('animate__animated', 'animate__pulse');
    } else {
      badge.style.display = 'none';
    }
  });
}

/**
 * Quantity Buttons (+ / - Steppers)
 */
function initQuantityButtons() {
  // Product detail stepper
  document.querySelectorAll('.qty-stepper-container').forEach(container => {
    const input = container.querySelector('.qty-input');
    const btnMinus = container.querySelector('.qty-btn-minus');
    const btnPlus = container.querySelector('.qty-btn-plus');
    const maxStock = parseInt(input.getAttribute('max') || '999');

    if (btnMinus && input) {
      btnMinus.addEventListener('click', () => {
        let val = parseInt(input.value) || 1;
        if (val > 1) {
          input.value = val - 1;
        }
      });
    }

    if (btnPlus && input) {
      btnPlus.addEventListener('click', () => {
        let val = parseInt(input.value) || 1;
        if (val < maxStock) {
          input.value = val + 1;
        } else {
          showToast(`Maximum available stock reached (${maxStock})`, 'info');
        }
      });
    }
  });

  // Cart page AJAX quantity update
  document.querySelectorAll('.cart-qty-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const itemId = this.dataset.itemId;
      const action = this.dataset.action;
      const input = document.getElementById(`cart-qty-${itemId}`);
      let currentVal = parseInt(input.value) || 1;

      if (action === 'increase') {
        currentVal++;
      } else if (action === 'decrease') {
        currentVal = Math.max(0, currentVal - 1);
      }

      sendCartUpdate(itemId, currentVal, action);
    });
  });

  // Cart direct input change
  document.querySelectorAll('.cart-qty-input').forEach(input => {
    input.addEventListener('change', function () {
      const itemId = this.dataset.itemId;
      let val = parseInt(this.value);
      if (isNaN(val) || val < 1) val = 1;
      this.value = val;
      sendCartUpdate(itemId, val, 'set');
    });
  });

  // Cart item remove buttons
  document.querySelectorAll('.cart-remove-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const itemId = this.dataset.itemId;
      const removeUrl = this.getAttribute('href');

      if (!confirm('Remove this item from your cart?')) return;

      fetch(removeUrl, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken') || ''
        }
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          const row = document.getElementById(`cart-item-row-${itemId}`);
          if (row) {
            row.style.transition = 'all 0.3s ease';
            row.style.opacity = '0';
            row.style.transform = 'translateX(-20px)';
            setTimeout(() => {
              row.remove();
              checkEmptyCartState(data.cart_count);
            }, 300);
          }
          updateCartSummaryUI(data);
          showToast(data.message, 'info');
        }
      })
      .catch(() => {
        window.location.href = removeUrl;
      });
    });
  });
}

function sendCartUpdate(itemId, quantity, action) {
  const url = `/cart/update/${itemId}/`;
  const formData = new FormData();
  formData.append('quantity', quantity);
  formData.append('action', action);

  fetch(url, {
    method: 'POST',
    body: formData,
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'X-CSRFToken': getCookie('csrftoken') || ''
    }
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      const input = document.getElementById(`cart-qty-${itemId}`);
      const itemSubtotalEl = document.getElementById(`cart-item-subtotal-${itemId}`);

      if (data.item_quantity === 0) {
        const row = document.getElementById(`cart-item-row-${itemId}`);
        if (row) row.remove();
        checkEmptyCartState(data.cart_count);
      } else {
        if (input) input.value = data.item_quantity;
        if (itemSubtotalEl) itemSubtotalEl.textContent = `$${data.item_subtotal.toFixed(2)}`;
      }

      updateCartSummaryUI(data);
    }
  })
  .catch(err => {
    console.error('Cart update error:', err);
  });
}

function updateCartSummaryUI(data) {
  updateCartBadge(data.cart_count);

  const subtotalEl = document.getElementById('cart-subtotal-val');
  const shippingEl = document.getElementById('cart-shipping-val');
  const discountEl = document.getElementById('cart-discount-val');
  const totalEl = document.getElementById('cart-total-val');
  const progressBar = document.getElementById('free-shipping-progress-bar');
  const shippingMsg = document.getElementById('free-shipping-msg');

  if (subtotalEl) subtotalEl.textContent = `$${data.subtotal.toFixed(2)}`;
  if (shippingEl) shippingEl.textContent = data.shipping === 0 ? 'FREE' : `$${data.shipping.toFixed(2)}`;
  if (discountEl && data.discount > 0) discountEl.textContent = `-$${data.discount.toFixed(2)}`;
  if (totalEl) totalEl.textContent = `$${data.total.toFixed(2)}`;

  // Free shipping progress calculation (Free over $50)
  if (progressBar && shippingMsg) {
    const goal = 50.00;
    const progress = Math.min(100, (data.subtotal / goal) * 100);
    progressBar.style.width = `${progress}%`;
    if (data.subtotal >= goal) {
      shippingMsg.innerHTML = '<span class="text-success fw-bold"><i class="bi bi-check-circle-fill me-1"></i> You have unlocked FREE Shipping!</span>';
    } else {
      const remaining = (goal - data.subtotal).toFixed(2);
      shippingMsg.innerHTML = `Add <strong>$${remaining}</strong> more to qualify for <strong>FREE Shipping</strong>!`;
    }
  }
}

function checkEmptyCartState(count) {
  if (count === 0) {
    const cartWrapper = document.getElementById('cart-content-wrapper');
    const emptyState = document.getElementById('cart-empty-state');
    if (cartWrapper && emptyState) {
      cartWrapper.classList.add('d-none');
      emptyState.classList.remove('d-none');
    }
  }
}

/**
 * Checkout Payment Selection Visual Toggle
 */
function initCheckoutPaymentSelect() {
  const paymentOptions = document.querySelectorAll('.payment-radio-item');
  const cardFields = document.getElementById('card-payment-details');

  paymentOptions.forEach(opt => {
    const radio = opt.querySelector('input[type="radio"]');
    if (!radio) return;

    opt.addEventListener('click', () => {
      paymentOptions.forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
      radio.checked = true;

      if (cardFields) {
        if (radio.value === 'card') {
          cardFields.classList.remove('d-none');
        } else {
          cardFields.classList.add('d-none');
        }
      }
    });

    if (radio.checked) {
      opt.classList.add('selected');
      if (cardFields && radio.value === 'card') {
        cardFields.classList.remove('d-none');
      }
    }
  });
}
