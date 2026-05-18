/**
 * Scroll reveal 動畫（Intersection Observer）
 */

(function () {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -60px 0px' }
  );

  // Lazy image observer
  const imageObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.classList.add('lazyloaded');
            img.classList.remove('lazyload');
          }
          imageObserver.unobserve(img);
        }
      });
    },
    { rootMargin: '200px' }
  );

  // 掃描 DOM 後初始化
  const init = () => {
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
    document.querySelectorAll('img.lazyload').forEach(img => imageObserver.observe(img));
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
