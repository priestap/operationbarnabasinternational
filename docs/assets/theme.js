(() => {
 const root = document.documentElement;
 const system = window.matchMedia('(prefers-color-scheme: dark)');
 let preference = null;
 try { preference = localStorage.getItem('obi-theme'); } catch (_) {}
 function apply(theme) {
   root.dataset.theme = theme;
   root.style.colorScheme = theme;
   const toggle = document.querySelector('.theme-toggle');
   if (toggle) {
     toggle.setAttribute('aria-pressed', String(theme === 'dark'));
     const label = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
     toggle.setAttribute('aria-label', label);
     toggle.setAttribute('title', label);
     toggle.querySelector('svg').innerHTML = theme === 'dark' ? '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/>' : '<path d="M20 14A8 8 0 0 1 10 4a8 8 0 1 0 10 10Z"/>';
   }
 }
 apply(preference === 'dark' || preference === 'light' ? preference : system.matches ? 'dark' : 'light');
 document.addEventListener('DOMContentLoaded', () => {
   apply(root.dataset.theme);
   const toggle = document.querySelector('.theme-toggle');
   if (toggle) toggle.hidden = false;
   toggle?.addEventListener('click', () => {
     preference = root.dataset.theme === 'dark' ? 'light' : 'dark';
     try { localStorage.setItem('obi-theme', preference); } catch (_) {}
     apply(preference);
   });
 });
 system.addEventListener('change', e => { if (!preference) apply(e.matches ? 'dark' : 'light'); });
})();
