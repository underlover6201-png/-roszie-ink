/**
 * 首頁 info bar：即時時間 + 營業狀態
 */

(function () {
  // 即時時間
  function updateTime() {
    const el = document.getElementById('local-time');
    if (!el) return;
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    el.textContent = `Taipei  ${h}:${m}`;
  }

  // 營業狀態
  async function updateBusinessStatus() {
    const dot  = document.getElementById('status-dot');
    const text = document.getElementById('business-status');
    if (!dot || !text) return;

    try {
      const res = await fetch('/api/v1/business-status');
      const { is_open } = await res.json();
      dot.classList.toggle('info-bar__dot--open', is_open);
      text.textContent = is_open ? 'Open Now' : 'Closed';
    } catch {
      text.textContent = '—';
    }
  }

  updateTime();
  setInterval(updateTime, 30_000);
  updateBusinessStatus();
})();
