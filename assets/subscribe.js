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
})();
