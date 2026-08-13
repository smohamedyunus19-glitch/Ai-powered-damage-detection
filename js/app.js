/* ===========================
   FIX NEARBY — APP LOGIC
   =========================== */

const API = 'http://localhost:5000/api';

const App = {
  state: {
    device: 'mobile',
    file: null,
    lat: 13.0827,
    lng: 80.2707,
    currentPage: 'home',
  },

  init() {
    // Loader hide
    const loader = document.getElementById('loader');
    if (loader) {
      setTimeout(() => {
        loader.style.transition = 'opacity 0.5s ease';
        loader.style.opacity = '0';
        loader.style.pointerEvents = 'none';
        setTimeout(() => { loader.style.display = 'none'; }, 500);
      }, 2200);
    }

    // Geolocation
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(pos => {
        this.state.lat = pos.coords.latitude;
        this.state.lng = pos.coords.longitude;
      });
    }

    // Theme
    const saved = localStorage.getItem('fn_theme') || 'light';
    this.setTheme(saved);

    const themeBtn = document.getElementById('themeBtn');
    if (themeBtn) {
      themeBtn.addEventListener('click', () => {
        const cur = document.documentElement.dataset.theme;
        this.setTheme(cur === 'dark' ? 'light' : 'dark');
      });
    }

    // Drag & Drop
    this.initDragDrop();
  },

  setTheme(theme) {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('fn_theme', theme);
    const icon = document.querySelector('.theme-icon');
    if (icon) icon.textContent = theme === 'dark' ? '☀️' : '🌙';
  },

  switchPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.bnav-item').forEach(b => b.classList.remove('active'));

    const target = document.getElementById('page-' + page);
    if (target) target.classList.add('active');

    const bnav = document.getElementById('bnav-' + page);
    if (bnav) bnav.classList.add('active');

    this.state.currentPage = page;

    if (page === 'history') this.renderHistory();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  },

  selectDevice(type) {
    this.state.device = type;
    document.querySelectorAll('.device-tile').forEach(t => t.classList.remove('selected'));
    const tile = document.getElementById('tile-' + type);
    if (tile) tile.classList.add('selected');
  },

  handleFile(event) {
    const file = event.target.files[0];
    if (!file) return;
    this._loadFile(file);
  },

  _loadFile(file) {
    if (!file.type.startsWith('image/')) {
      UI.toast('❌ Image file மட்டும் upload பண்ணுங்கள்');
      return;
    }
    this.state.file = file;
    const reader = new FileReader();
    reader.onload = e => {
      const img = document.getElementById('previewImg');
      const preview = document.getElementById('dropPreview');
      const content = document.getElementById('dropContent');
      const btn = document.getElementById('analyzeBtn');
      if (img) img.src = e.target.result;
      if (preview) preview.style.display = 'block';
      if (content) content.style.display = 'none';
      if (btn) btn.disabled = false;
    };
    reader.readAsDataURL(file);
  },

  removeFile(event) {
    event.stopPropagation();
    this.state.file = null;
    const preview = document.getElementById('dropPreview');
    const content = document.getElementById('dropContent');
    const input = document.getElementById('fileInput');
    const btn = document.getElementById('analyzeBtn');
    const panel = document.getElementById('resultPanel');
    const empty = document.getElementById('resultEmpty');
    if (preview) preview.style.display = 'none';
    if (content) content.style.display = 'block';
    if (input) input.value = '';
    if (btn) btn.disabled = true;
    if (panel) panel.style.display = 'none';
    if (empty) {
      empty.style.display = 'block';
      empty.innerHTML = `
        <div class="empty-circle"><span>🔍</span></div>
        <h3>Ready to Analyze</h3>
        <p>Select your device type and upload a photo to get started</p>`;
    }
  },

  async analyze() {
    if (!this.state.file) return;

    const btn = document.getElementById('analyzeBtn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoader = btn.querySelector('.btn-loader');
    const resultEmpty = document.getElementById('resultEmpty');
    const resultPanel = document.getElementById('resultPanel');

    if (btnText) btnText.style.display = 'none';
    if (btnLoader) btnLoader.style.display = 'flex';
    btn.disabled = true;

    if (resultEmpty) resultEmpty.style.display = 'none';
    if (resultPanel) resultPanel.style.display = 'none';

    try {
      // 1. Upload
      const form = new FormData();
      form.append('file', this.state.file);
      form.append('device_type', this.state.device);

      const upRes = await fetch(`${API}/upload`, { method: 'POST', body: form });
      const upData = await upRes.json();
      if (!upData.success) throw new Error('Upload failed');

      // 2. Predict
      const prRes = await fetch(`${API}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename: upData.filename,
          device_type: this.state.device,
          latitude: this.state.lat,
          longitude: this.state.lng
        })
      });
      const prData = await prRes.json();

      // Wrong device check
      if (!prData.success && prData.error_type === 'wrong_device') {
        UI.toast(prData.error, 6000);
        if (resultEmpty) {
          resultEmpty.style.display = 'block';
          resultEmpty.innerHTML = `
            <div class="empty-circle" style="background:#FEE2E2">⚠️</div>
            <h3 style="color:#EF4444">Wrong Device Image!</h3>
            <p>${prData.error}</p>
            <p style="margin-top:0.5rem;font-size:0.8rem;color:var(--text-3)">சரியான device-ஓட photo upload பண்ணுங்கள்</p>`;
        }
        return;
      }

      if (!prData.success) throw new Error(prData.error || 'Prediction failed');

      // 3. Render
      this._renderResult(prData);
      this.fetchShops();
      this._saveHistory(prData);
      UI.toast('✅ Analysis complete!');

    } catch (err) {
      UI.toast('❌ ' + err.message);
      if (resultEmpty) resultEmpty.style.display = 'block';
    } finally {
      if (btnText) btnText.style.display = 'flex';
      if (btnLoader) btnLoader.style.display = 'none';
      btn.disabled = false;
    }
  },

  _renderResult(data) {
    const damage = data.damage_type || 'unknown';
    const conf = Math.round((data.confidence || 0) * 100);
    const sev = data.severity || 'low';
    const device = this.state.device === 'mobile' ? 'Mobile Phone' : 'Laptop';

    const panel = document.getElementById('resultPanel');
    if (panel) panel.style.display = 'block';

    const headline = document.getElementById('resultHeadline');
    const meta = document.getElementById('resultMeta');
    const mDamage = document.getElementById('mDamage');
    const mConf = document.getElementById('mConf');
    const mSeverity = document.getElementById('mSeverity');

    if (headline) headline.textContent = UI.fmt(damage) + ' Detected';
    if (meta) meta.textContent = `${device} · ${new Date().toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' })}`;
    if (mDamage) mDamage.textContent = UI.fmt(damage);
    if (mConf) mConf.textContent = conf + '%';

    const sevColors = { low: 'badge-low', medium: 'badge-medium', high: 'badge-high' };
    if (mSeverity) mSeverity.innerHTML = `<span class="badge ${sevColors[sev] || 'badge-low'}">${sev.toUpperCase()}</span>`;

    // Detections
    const detections = data.all_detections || [];
    const detectionsBox = document.getElementById('detectionsBox');
    const detectionsList = document.getElementById('detectionsList');

    if (detections.length > 1 && detectionsBox && detectionsList) {
      detectionsBox.style.display = 'block';
      detectionsList.innerHTML = detections.map(d => `
        <div class="detection-item">
          <span class="det-name">${UI.fmt(d.class)}</span>
          <div class="det-bar-wrap"><div class="det-bar" style="width:${Math.round(d.confidence*100)}%"></div></div>
          <span class="det-conf">${Math.round(d.confidence*100)}%</span>
        </div>`).join('');
    } else if (detectionsBox) {
      detectionsBox.style.display = 'none';
    }
  },

  async fetchShops() {
    const shopsList = document.getElementById('shopsList');
    if (!shopsList) return;

    shopsList.innerHTML = `
      <div class="shops-loading">
        <div class="mini-spin"></div>
        <span>Finding nearby repair shops...</span>
      </div>`;
    try {
      const res = await fetch(`${API}/shops?lat=${this.state.lat}&lng=${this.state.lng}&device_type=${this.state.device}`);
      const data = await res.json();
      this._renderShops(data.shops || []);
    } catch {
      this._renderShops([]);
    }
  },

  _renderShops(shops) {
    const shopsList = document.getElementById('shopsList');
    if (!shopsList) return;

    if (!shops.length) {
      shopsList.innerHTML = '<p style="color:var(--text-3);font-size:0.85rem;padding:1rem;text-align:center">No shops found nearby.</p>';
      return;
    }
    const icons = ['🔧', '🛠️', '⚙️', '🔩', '🖥️'];
    shopsList.innerHTML = shops.map((s, i) => `
      <div class="shop-item">
        <div class="shop-avatar">${icons[i % icons.length]}</div>
        <div class="shop-info">
          <div class="shop-name">${s.name}</div>
          <div class="shop-addr">📍 ${s.address || 'Address not available'}</div>
        </div>
        <div class="shop-actions">
          ${s.open_now !== null && s.open_now !== undefined ? `<div class="open-dot ${s.open_now ? 'open' : 'closed'}"></div>` : ''}
          ${s.phone && s.phone !== 'Not available' ? `<button class="shop-call" onclick="window.open('tel:${s.phone}')">📞</button>` : ''}
        </div>
      </div>`).join('');
  },

  _saveHistory(data) {
    const h = JSON.parse(localStorage.getItem('fn_history') || '[]');
    h.unshift({
      damage: data.damage_type || 'unknown',
      confidence: Math.round((data.confidence || 0) * 100),
      severity: data.severity || 'low',
      device: this.state.device,
      date: new Date().toISOString()
    });
    if (h.length > 30) h.pop();
    localStorage.setItem('fn_history', JSON.stringify(h));
  },

  renderHistory() {
    const h = JSON.parse(localStorage.getItem('fn_history') || '[]');
    const c = document.getElementById('historyList');
    if (!c) return;

    if (!h.length) {
      c.innerHTML = `
        <div class="history-empty">
          <div class="he-icon">📋</div>
          <h3>No History Yet</h3>
          <p>Diagnose a device to see your history here</p>
        </div>`;
      return;
    }

    const sevClass = { low: 'badge-low', medium: 'badge-medium', high: 'badge-high' };
    c.innerHTML = h.map(x => `
      <div class="history-item">
        <div class="history-thumb">${x.device === 'mobile' ? '📱' : '💻'}</div>
        <div class="history-info">
          <h4>${UI.fmt(x.damage)}</h4>
          <p>${x.device === 'mobile' ? 'Mobile Phone' : 'Laptop'} · ${x.confidence}% confidence · ${new Date(x.date).toLocaleDateString('en-IN', {day:'numeric',month:'short',year:'numeric'})}</p>
        </div>
        <span class="badge ${sevClass[x.severity] || 'badge-low'}" style="margin-left:auto;flex-shrink:0">${x.severity.toUpperCase()}</span>
      </div>`).join('');
  },

  clearHistory() {
    if (!confirm('Clear all history?')) return;
    localStorage.removeItem('fn_history');
    this.renderHistory();
    UI.toast('🗑️ History cleared');
  },

  initDragDrop() {
    const zone = document.getElementById('dropZone');
    if (!zone) return;

    zone.addEventListener('dragover', e => {
      e.preventDefault();
      zone.classList.add('over');
    });
    zone.addEventListener('dragleave', () => zone.classList.remove('over'));
    zone.addEventListener('drop', e => {
      e.preventDefault();
      zone.classList.remove('over');
      const file = e.dataTransfer.files[0];
      if (file) this._loadFile(file);
    });
  }
};

// Boot — DOM ready ஆனதும் மட்டும் init பண்ணு
document.addEventListener('DOMContentLoaded', () => App.init());
