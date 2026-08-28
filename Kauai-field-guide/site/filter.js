// Client-side filter for the field guide index.
// Operates entirely on DOM data-attributes emitted by build_site.py.
// No fetch(), no external requests — works under file:// in all major browsers.
(function () {
  var input = document.getElementById('filter-input');
  var countEl = document.getElementById('filter-count');
  if (!input) return;
  var cards = Array.prototype.slice.call(document.querySelectorAll('.card[data-search]'));
  function updateCount() {
    var visible = cards.filter(function (c) { return !c.classList.contains('hidden'); }).length;
    if (countEl) countEl.textContent = visible + ' / ' + cards.length + ' species shown';
  }
  function apply() {
    var q = (input.value || '').toLowerCase().trim();
    var terms = q.split(/\s+/).filter(Boolean);
    cards.forEach(function (c) {
      var hay = c.getAttribute('data-search') || '';
      var ok = terms.every(function (t) { return hay.indexOf(t) !== -1; });
      c.classList.toggle('hidden', !ok);
    });
    // Also hide any tier/zone section whose cards are all hidden.
    document.querySelectorAll('.group').forEach(function (g) {
      var kids = g.querySelectorAll('.card[data-search]');
      var anyVisible = false;
      kids.forEach(function (c) { if (!c.classList.contains('hidden')) anyVisible = true; });
      g.classList.toggle('hidden', !anyVisible);
    });
    updateCount();
  }
  input.addEventListener('input', apply);
  updateCount();
})();
