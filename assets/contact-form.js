(() => {
 const form = document.querySelector('.contact-form');
 if (!form) return;
 const status = document.querySelector('#form-status');
 const button = form.querySelector('button[type="submit"]');
 form.addEventListener('submit', async event => {
   event.preventDefault();
   if (button.disabled || !form.reportValidity()) return;
   button.disabled = true;
   button.textContent = 'Sending…';
   status.textContent = '';
   form.setAttribute('aria-busy', 'true');
   const controller = new AbortController();
   const timer = setTimeout(() => controller.abort(), 30000);
   try {
     const response = await fetch(form.action, {
       method: 'POST', body: new FormData(form),
       headers: { Accept: 'application/json' }, signal: controller.signal
     });
     if (!response.ok) {
       const data = await response.json().catch(() => null);
       throw new Error(data?.errors?.map(error => error.message).join(' ') || 'Your message could not be sent. Please try again.');
     }
     status.textContent = 'Thank you! Your message has been submitted.';
     status.dataset.state = 'success';
     form.reset();
   } catch (error) {
     status.dataset.state = 'error';
     status.textContent = error.name === 'AbortError'
       ? 'The request timed out. Your message is still here. Please check your connection and try again.'
       : error instanceof TypeError
         ? 'We could not connect. Your message is still here. Please check your connection and try again.'
         : error.message;
   } finally {
     clearTimeout(timer);
     button.disabled = false;
     button.textContent = 'Send message';
     form.removeAttribute('aria-busy');
     status.focus();
   }
 });
})();
