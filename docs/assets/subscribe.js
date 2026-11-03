(() => {
 // The form posts to Mailchimp's hosted page in a new tab (Mailchimp no longer supports in-page sign-ups);
 // leave a note here so people know where to finish.
 document.querySelectorAll('.subscribe-form').forEach(form => {
   const status = form.querySelector('.subscribe-status');
   form.addEventListener('submit', () => {
     setTimeout(() => {
       status.dataset.state = 'success';
       status.textContent = 'Almost done! Finish signing up in the Mailchimp tab that just opened.';
       form.reset();
     }, 300);
   });
 });
 // The first time the sign-up band scrolls into view, its contents rise in and the envelope badge settles like a stamp.
 if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
 const observer = new IntersectionObserver(entries => entries.forEach(entry => {
   if (!entry.isIntersecting) return;
   entry.target.classList.add('revealed');
   observer.unobserve(entry.target);
 }), { threshold: 0.35 });
 document.querySelectorAll('.subscribe').forEach(band => {
   band.classList.add('will-reveal');
   observer.observe(band);
 });
})();
