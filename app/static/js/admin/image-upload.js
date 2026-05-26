/* 後台圖片上傳：自動為 data-upload 欄位加上「選擇圖片」按鈕 */
(function () {
  'use strict';

  function getCsrfToken() {
    const el = document.getElementById('csrf_token');
    return el ? el.value : '';
  }

  function buildWidget(urlInput, thumbInput, subfolder) {
    const wrapper = document.createElement('div');
    wrapper.style.cssText = 'display:flex;gap:8px;align-items:center;margin-top:6px;flex-wrap:wrap;';

    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.style.display = 'none';

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = '選擇圖片';
    btn.style.cssText = 'padding:6px 12px;font-size:12px;font-weight:600;border:1px solid #444;background:#1a1a1a;color:#f0f0ee;cursor:pointer;letter-spacing:0.05em;white-space:nowrap;';

    const status = document.createElement('span');
    status.style.cssText = 'font-size:11px;color:#999;';

    const preview = document.createElement('img');
    preview.style.cssText = 'max-width:80px;max-height:60px;object-fit:cover;border:1px solid #333;display:none;';

    // 若欄位已有 URL，顯示預覽
    if (urlInput.value) {
      preview.src = urlInput.value;
      preview.style.display = 'block';
    }
    urlInput.addEventListener('input', function () {
      if (this.value) { preview.src = this.value; preview.style.display = 'block'; }
      else { preview.style.display = 'none'; }
    });

    btn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', function () {
      const file = this.files[0];
      if (!file) return;

      btn.disabled = true;
      btn.textContent = '上傳中…';
      status.textContent = '';

      const fd = new FormData();
      fd.append('file', file);
      fd.append('subfolder', subfolder);
      fd.append('csrf_token', getCsrfToken());

      fetch('/admin/upload-image', { method: 'POST', body: fd })
        .then(r => r.json())
        .then(data => {
          if (data.error) { status.textContent = '✗ ' + data.error; return; }
          urlInput.value = data.image_url;
          if (thumbInput) thumbInput.value = data.thumb_url;
          preview.src = data.image_url;
          preview.style.display = 'block';
          status.textContent = '✓ 上傳成功';
          setTimeout(() => { status.textContent = ''; }, 3000);
        })
        .catch(() => { status.textContent = '✗ 上傳失敗'; })
        .finally(() => { btn.disabled = false; btn.textContent = '選擇圖片'; fileInput.value = ''; });
    });

    wrapper.append(fileInput, btn, status, preview);
    urlInput.parentNode.appendChild(wrapper);
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-upload]').forEach(function (urlInput) {
      const subfolder = urlInput.dataset.upload;
      const thumbId   = urlInput.dataset.thumb;
      const thumbInput = thumbId ? document.getElementById(thumbId) : null;
      buildWidget(urlInput, thumbInput, subfolder);
    });
  });
})();
