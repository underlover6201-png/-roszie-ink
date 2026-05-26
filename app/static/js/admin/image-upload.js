/* 後台圖片上傳：隱藏 URL 欄位，只顯示上傳區塊 */
(function () {
  'use strict';

  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.content;
    const el = document.getElementById('csrf_token');
    return el ? el.value : '';
  }

  function buildWidget(urlInput, thumbInput, subfolder) {
    // 隱藏原本的 URL 輸入框和相關 label
    urlInput.style.display = 'none';
    const urlLabel = urlInput.closest('.field');

    // 也隱藏縮圖欄位
    if (thumbInput) {
      const thumbField = thumbInput.closest('.field');
      if (thumbField) thumbField.style.display = 'none';
    }

    // 建立上傳區塊
    const widget = document.createElement('div');
    widget.style.cssText = 'margin-top:var(--sp-2,8px);';

    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.style.display = 'none';

    // 預覽區
    const preview = document.createElement('div');
    preview.style.cssText = [
      'position:relative',
      'width:100%',
      'aspect-ratio:16/9',
      'background:#1a1a18',
      'border:2px dashed #333',
      'display:flex',
      'flex-direction:column',
      'align-items:center',
      'justify-content:center',
      'cursor:pointer',
      'overflow:hidden',
      'transition:border-color .15s',
    ].join(';');

    const previewImg = document.createElement('img');
    previewImg.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:none;';

    const uploadIcon = document.createElement('div');
    uploadIcon.innerHTML = '＋';
    uploadIcon.style.cssText = 'font-size:32px;color:#666;line-height:1;';

    const uploadText = document.createElement('div');
    uploadText.textContent = '點擊上傳圖片';
    uploadText.style.cssText = 'font-size:11px;color:#666;letter-spacing:0.1em;margin-top:8px;';

    const statusText = document.createElement('div');
    statusText.style.cssText = 'font-size:11px;color:#999;margin-top:6px;';

    // 有既有圖片就顯示
    if (urlInput.value) {
      previewImg.src = urlInput.value;
      previewImg.style.display = 'block';
      uploadIcon.style.display = 'none';
      uploadText.style.display = 'none';
    }

    // 右上角覆蓋按鈕（已有圖片時顯示「更換」）
    const changeBtn = document.createElement('button');
    changeBtn.type = 'button';
    changeBtn.textContent = '更換';
    changeBtn.style.cssText = [
      'position:absolute',
      'top:8px',
      'right:8px',
      'padding:4px 10px',
      'font-size:11px',
      'font-weight:600',
      'background:rgba(0,0,0,0.7)',
      'color:#fff',
      'border:1px solid #555',
      'cursor:pointer',
      'display:' + (urlInput.value ? 'block' : 'none'),
    ].join(';');

    preview.append(previewImg, uploadIcon, uploadText, statusText, changeBtn);
    widget.append(fileInput, preview);

    // 點擊觸發選檔
    preview.addEventListener('click', () => fileInput.click());

    // Hover 效果
    preview.addEventListener('mouseenter', () => { preview.style.borderColor = '#888'; });
    preview.addEventListener('mouseleave', () => { preview.style.borderColor = '#333'; });

    // 上傳邏輯
    fileInput.addEventListener('change', function () {
      const file = this.files[0];
      if (!file) return;

      // 顯示 loading
      uploadIcon.style.display = 'none';
      uploadText.style.display = 'none';
      statusText.textContent = '上傳中…';
      preview.style.opacity = '0.6';
      preview.style.pointerEvents = 'none';

      const fd = new FormData();
      fd.append('file', file);
      fd.append('subfolder', subfolder);
      fd.append('csrf_token', getCsrfToken());

      fetch('/admin/upload-image', { method: 'POST', body: fd })
        .then(r => r.json())
        .then(data => {
          if (data.error) {
            statusText.textContent = '✗ ' + data.error;
            uploadIcon.style.display = 'block';
            uploadText.style.display = 'block';
            return;
          }
          // 成功
          urlInput.value = data.image_url;
          if (thumbInput) thumbInput.value = data.thumb_url;
          previewImg.src = data.image_url;
          previewImg.style.display = 'block';
          changeBtn.style.display = 'block';
          uploadIcon.style.display = 'none';
          uploadText.style.display = 'none';
          statusText.textContent = '';
        })
        .catch(() => {
          statusText.textContent = '✗ 上傳失敗，請重試';
          uploadIcon.style.display = 'block';
          uploadText.style.display = 'block';
        })
        .finally(() => {
          preview.style.opacity = '1';
          preview.style.pointerEvents = 'auto';
          fileInput.value = '';
        });
    });

    // 插入到欄位後面
    if (urlLabel) {
      urlLabel.after(widget);
    } else {
      urlInput.parentNode.insertBefore(widget, urlInput.nextSibling);
    }
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
