// Common utilities loaded on every page.

(function () {
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

  // Asciinema players: each .asciinema-cast element with data-cast-url
  document.querySelectorAll('.asciinema-cast').forEach(async (el) => {
    const url = el.dataset.castUrl;
    if (!url || !window.AsciinemaPlayer) return;
    try {
      window.AsciinemaPlayer.create(url, el, {
        autoPlay: false,
        idleTimeLimit: 2,
        speed: 2,
        theme: 'monokai',
        fit: 'width',
      });
    } catch (err) {
      el.textContent = 'Failed to load recording: ' + err;
    }
  });

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
