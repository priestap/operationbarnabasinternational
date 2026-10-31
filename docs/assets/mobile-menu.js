(() => {
 const menu = document.querySelector('#mobile-menu');
 const toggle = document.querySelector('.menu-toggle');
 const close = document.querySelector('.menu-close');
 if (!menu || !toggle || !close) return;
 let scrollY = 0;
 toggle.addEventListener('click', () => {
   scrollY = window.scrollY;
   menu.showModal();
   toggle.setAttribute('aria-expanded', 'true');
   document.body.style.position = 'fixed';
   document.body.style.top = `-${scrollY}px`;
   document.body.style.width = '100%';
   close.focus();
 });
 close.addEventListener('click', () => menu.close());
 menu.addEventListener('close', () => {
   toggle.setAttribute('aria-expanded', 'false');
   document.body.style.position = '';
   document.body.style.top = '';
   document.body.style.width = '';
   const behavior = document.documentElement.style.scrollBehavior;
   document.documentElement.style.scrollBehavior = 'auto';
   window.scrollTo(0, scrollY);
   document.documentElement.style.scrollBehavior = behavior;
   toggle.focus({ preventScroll: true });
 });
 menu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => menu.close()));
 window.matchMedia('(max-width: 900px)').addEventListener('change', e => {
   if (!e.matches && menu.open) menu.close();
 });
})();
