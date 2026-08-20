document.querySelectorAll('a[href*="dodaj"]').forEach(btn => {
  btn.addEventListener('click', () => {
    const cartBtn = document.querySelector('.pd-cart-btn');
    if (cartBtn) {
      cartBtn.classList.remove('bumped');
      void cartBtn.offsetWidth; // reset animation
      cartBtn.classList.add('bumped');
    }
  });
});

document.querySelectorAll('.pd-toast').forEach(toast => {
  setTimeout(() => {
    toast.style.transition = 'opacity 0.4s';
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 400);
  }, 3000);
});

const input = document.getElementById('live-search');
const dropdown = document.getElementById('search-dropdown');

if (input) {
  let timer;
  input.addEventListener('input', () => {
    clearTimeout(timer);
    const q = input.value.trim();
    if (q.length < 2) { dropdown.style.display = 'none'; return; }
    timer = setTimeout(() => {
      fetch(`/search/?q=${encodeURIComponent(q)}`)
        .then(r => r.json())
        .then(data => {
          if (!data.results.length) {
            dropdown.innerHTML = '<div style="padding:14px 16px;font-size:13px;color:#7a7a7a;">Nema rezultata.</div>';
          } else {
            dropdown.innerHTML = data.results.map(p => `
              <a href="${p.url}" style="display:flex;align-items:center;gap:12px;padding:10px 14px;text-decoration:none;color:#161616;border-bottom:1px solid #e4e4e4;">
                ${p.image ? `<img src="${p.image}" style="width:40px;height:40px;object-fit:cover;border-radius:8px;flex:none;">` : '<div style="width:40px;height:40px;border-radius:8px;background:#ececec;flex:none;"></div>'}
                <div>
                  <div style="font-size:13px;font-weight:600;">${p.name}</div>
                  <div style="font-size:12px;color:#7a7a7a;">${p.category}</div>
                </div>
                <div style="margin-left:auto;font-size:13px;font-weight:700;color:#333;">${p.price} KM</div>
              </a>
            `).join('');
          }
          dropdown.style.display = 'block';
        });
    }, 250);
  });

  document.addEventListener('click', e => {
    if (!input.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.style.display = 'none';
    }
  });

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      window.location = `/katalog/?q=${encodeURIComponent(input.value)}`;
    }
  });
}

// Mobile search toggle
const mobileToggle = document.getElementById('mobile-search-toggle');
const mobileBar = document.getElementById('mobile-search-bar');
const mobileInput = document.getElementById('live-search-mobile');
const mobileDropdown = document.getElementById('search-dropdown-mobile');

if (mobileToggle) {
  mobileToggle.addEventListener('click', () => {
    const visible = mobileBar.style.display === 'block';
    mobileBar.style.display = visible ? 'none' : 'block';
    if (!visible) mobileInput.focus();
  });
}

if (mobileInput) {
  let timer2;
  mobileInput.addEventListener('input', () => {
    clearTimeout(timer2);
    const q = mobileInput.value.trim();
    if (q.length < 2) { mobileDropdown.style.display = 'none'; return; }
    timer2 = setTimeout(() => {
      fetch(`/search/?q=${encodeURIComponent(q)}`)
        .then(r => r.json())
        .then(data => {
          if (!data.results.length) {
            mobileDropdown.innerHTML = '<div style="padding:14px 16px;font-size:13px;color:#7a7a7a;">Nema rezultata.</div>';
          } else {
            mobileDropdown.innerHTML = data.results.map(p => `
              <a href="${p.url}" style="display:flex;align-items:center;gap:12px;padding:10px 14px;text-decoration:none;color:#161616;border-bottom:1px solid #e4e4e4;">
                ${p.image ? `<img src="${p.image}" style="width:40px;height:40px;object-fit:cover;border-radius:8px;flex:none;">` : '<div style="width:40px;height:40px;border-radius:8px;background:#ececec;flex:none;"></div>'}
                <div>
                  <div style="font-size:13px;font-weight:600;">${p.name}</div>
                  <div style="font-size:12px;color:#7a7a7a;">${p.category}</div>
                </div>
                <div style="margin-left:auto;font-size:13px;font-weight:700;color:#333;">${p.price} KM</div>
              </a>
            `).join('');
          }
          mobileDropdown.style.display = 'block';
        });
    }, 250);
  });

  mobileInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      window.location = `/katalog/?q=${encodeURIComponent(mobileInput.value)}`;
    }
  });
}