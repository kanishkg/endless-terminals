// Common utilities loaded on every page.

(function () {
  // Theme switcher
  const THEME_KEY = 'endless-terminals-theme';
  const themes = ['dark', 'light', 'dim', 'midnight'];

  function getTheme() {
    return localStorage.getItem(THEME_KEY) || 'dark';
  }

  function setTheme(theme) {
    if (!themes.includes(theme)) theme = 'dark';
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
    updateThemeButton();

    // Toggle syntax highlighting theme
    const hljsDark = document.getElementById('hljs-dark');
    const hljsLight = document.getElementById('hljs-light');
    if (theme === 'light') {
      if (hljsDark) hljsDark.disabled = true;
      if (hljsLight) hljsLight.disabled = false;
    } else {
      if (hljsDark) hljsDark.disabled = false;
      if (hljsLight) hljsLight.disabled = true;
    }
  }

  function updateThemeButton() {
    const current = getTheme();
    const btn = document.getElementById('theme-btn-text');
    if (btn) {
      const names = { dark: 'Dark', light: 'Light', dim: 'Dim', midnight: 'Midnight' };
      btn.textContent = names[current] || 'Dark';
    }

    // Update active state in menu
    document.querySelectorAll('.theme-option').forEach(opt => {
      opt.classList.toggle('active', opt.dataset.theme === current);
    });
  }

  // Initialize theme on page load
  setTheme(getTheme());

  // Theme button toggle
  const themeBtn = document.getElementById('theme-btn');
  const themeMenu = document.getElementById('theme-menu');

  if (themeBtn && themeMenu) {
    themeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      themeMenu.classList.toggle('hidden');
    });

    // Close menu when clicking outside
    document.addEventListener('click', () => {
      themeMenu.classList.add('hidden');
    });

    // Theme option clicks
    document.querySelectorAll('.theme-option').forEach(opt => {
      opt.addEventListener('click', (e) => {
        e.stopPropagation();
        setTheme(opt.dataset.theme);
        themeMenu.classList.add('hidden');
      });
    });
  }
  if (window.hljs) {
    window.hljs.highlightAll();
  }

  // Render markdown blocks marked with .render-md from <script type="text/markdown">
  document.querySelectorAll('script[type="text/markdown"]').forEach((node) => {
    const target = document.querySelector(node.dataset.target);
    if (!target) return;
    const md = node.textContent || '';
    target.innerHTML = window.marked ? window.marked.parse(md) : md;
    target.querySelectorAll('pre code').forEach((b) => window.hljs && window.hljs.highlightElement(b));
  });

  // Asciinema cast player — uses an inline <script id="cast-data"> blob so we
  // don't depend on a fetch round-trip and can render even when the server is
  // not reachable. Falls back to a downloadable link if the player library
  // didn't load.
  const castContainer = document.getElementById('cast-container');
  const castScript = document.getElementById('cast-data');
  if (castContainer && castScript) {
    let castText = '';
    try {
      castText = (JSON.parse(castScript.textContent || '""') || '').trim();
    } catch (_) {
      castText = (castScript.textContent || '').trim();
    }
    if (!castText) {
      castContainer.innerHTML = '<div class="p-6 text-sm text-ink-500">No recording for this trial.</div>';
    } else if (!window.AsciinemaPlayer) {
      castContainer.innerHTML = '<div class="p-6 text-sm text-amber-300">asciinema-player failed to load — check your network.</div>';
    } else {
      try {
        window.AsciinemaPlayer.create(
          { data: castText },
          castContainer,
          {
            autoPlay: false,
            idleTimeLimit: 2,
            speed: 2,
            theme: 'monokai',
            fit: 'width',
            terminalFontSize: '12px',
          }
        );
      } catch (err) {
        console.error('asciinema-player error:', err);
        castContainer.innerHTML =
          '<div class="p-6 text-sm text-amber-300">Failed to render recording: ' +
          (err && err.message ? err.message : String(err)) +
          '</div>';
      }
    }
  }

  // Toggle expand/collapse code blocks with .collapsible
  document.querySelectorAll('.collapsible').forEach((el) => {
    const btn = el.querySelector('.collapsible-toggle');
    const body = el.querySelector('.collapsible-body');
    if (!btn || !body) return;
    btn.addEventListener('click', () => {
      const open = el.classList.toggle('open');
      btn.textContent = open ? 'Hide' : 'Show';
      body.style.display = open ? '' : 'none';
    });
    body.style.display = el.classList.contains('open') ? '' : 'none';
    btn.textContent = el.classList.contains('open') ? 'Hide' : 'Show';
  });

  // Step expand all / collapse all
  const expandAll = document.getElementById('expand-all-steps');
  const collapseAll = document.getElementById('collapse-all-steps');
  function setAllSteps(open) {
    document.querySelectorAll('.step-block').forEach((s) => {
      s.classList.toggle('open', open);
      const body = s.querySelector('.collapsible-body');
      const btn = s.querySelector('.collapsible-toggle');
      if (body) body.style.display = open ? '' : 'none';
      if (btn) btn.textContent = open ? 'Hide' : 'Show';
    });
  }
  if (expandAll) expandAll.addEventListener('click', () => setAllSteps(true));
  if (collapseAll) collapseAll.addEventListener('click', () => setAllSteps(false));
})();
