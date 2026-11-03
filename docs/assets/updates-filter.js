(() => {
 // News / Devotionals tabs on the Updates page. Without this script every card simply shows.
 const tabs = document.querySelector('.filter-tabs');
 const cards = document.querySelectorAll('#update-cards .card');
 if (!tabs || !cards.length) return;
 const buttons = tabs.querySelectorAll('button');
 const show = filter => {
   if (![...buttons].some(b => b.dataset.filter === filter)) filter = 'all';
   buttons.forEach(b => b.setAttribute('aria-pressed', b.dataset.filter === filter));
   cards.forEach(card => { card.hidden = filter !== 'all' && card.dataset.cat !== filter; });
 };
 tabs.addEventListener('click', event => {
   const button = event.target.closest('button');
   if (!button) return;
   show(button.dataset.filter);
   // Keep the choice in the address so it survives a refresh or a shared link (old category links land here too).
   history.replaceState(null, '', button.dataset.filter === 'all' ? location.pathname : '#' + button.dataset.filter);
 });
 tabs.hidden = false;
 show(location.hash.slice(1));
})();
