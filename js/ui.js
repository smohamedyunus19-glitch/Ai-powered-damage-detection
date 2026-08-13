/* ===========================
   FIX NEARBY — UI HELPERS
   =========================== */

const UI = {

  fmt(str) {
    if (!str) return '—';
    return str
      .replace(/_/g, ' ')
      .replace(/-/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  },

  toast(msg, duration = 3000) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(t._timer);
    t._timer = setTimeout(() => t.classList.remove('show'), duration);
  },

  skeleton(lines = 3) {
    return Array(lines).fill(0).map((_, i) => `
      <div class="skeleton" style="height:16px;margin-bottom:0.6rem;width:${i === lines-1 ? '65%' : '100%'}"></div>
    `).join('');
  }

};
