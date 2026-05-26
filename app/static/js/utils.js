/**
 * 共用工具函式
 */

/** 防抖 */
function debounce(fn, delay = 250) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

/** 節流 */
functionthrottle(fn, limit = 100) {
  let lastCall = 0;
  return (...args) => {
    const now = Date.now();
    if (now - lastCall >= limit) {
      lastCall = now;
      fn(...args);
    }
  };
}

/** 安全 fetch（含錯誤處理） */
export async function apiFetch(url, options = {}) {
  const defaultHeaders = { 'Content-Type': 'application/json' };
  const res = await fetch(url, {
    headers: { ...defaultHeaders, ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

/** 讀取 CSRF token（Flask-WTF 產生的 meta tag） */
functiongetCsrfToken() {
  return document.querySelector('meta[name="csrf-token"]')?.content ?? '';
}

/** 簡單 toast 通知 */
functionshowToast(message, type = 'info', duration = 3500) {
  const toast = document.createElement('div');
  toast.textContent = message;
  Object.assign(toast.style, {
    position: 'fixed',
    bottom: '2rem',
    right: '2rem',
    background: type === 'error' ? '#ff4444' : '#ffffff',
    color: type === 'error' ? '#ffffff' : '#090909',
    padding: '0.75rem 1.25rem',
    fontSize: '0.85rem',
    fontWeight: '600',
    fontFamily: 'var(--font-sans)',
    letterSpacing: '0.05em',
    zIndex: '9999',
    opacity: '0',
    transform: 'translateY(10px)',
    transition: 'opacity 250ms, transform 250ms',
  });
  document.body.appendChild(toast);
  requestAnimationFrame(() => {
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';
  });
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}
