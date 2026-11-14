/* Progressive enhancement only: tables are readable with JS disabled.
   1) wrap wide tables for horizontal scroll  2) live row filter  3) click-to-sort */
(function () {
  var wrapAll = function () {
    document.querySelectorAll('.tablewrap > table').forEach(function (t) {
      if (t.parentNode.classList.contains('tablescroll')) return;
      var d = document.createElement('div');
      d.className = 'tablescroll';
      t.parentNode.insertBefore(d, t);
      d.appendChild(t);
    });
  };

  var filterRows = function (input) {
    var wrap = document.getElementById(input.getAttribute('data-target'));
    if (!wrap) return;
    var q = input.value.trim().toLowerCase();
    var shown = 0, total = 0;
    wrap.querySelectorAll('tbody tr').forEach(function (tr) {
      total++;
      var hit = !q || tr.textContent.toLowerCase().indexOf(q) !== -1;
      tr.style.display = hit ? '' : 'none';
      if (hit) shown++;
    });
    var old = wrap.querySelector('.fcount');
    if (old) old.remove();
    if (q) {
      var s = document.createElement('div');
      s.className = 'fcount tnote';
      s.textContent = shown + ' of ' + total + ' rows match "' + input.value + '"';
      wrap.appendChild(s);
    }
  };

  var sortTable = function (th) {
    var table = th.closest('table'), tbody = table.querySelector('tbody');
    if (!tbody) return;
    var idx = Array.prototype.indexOf.call(th.parentNode.children, th);
    var dir = th.getAttribute('data-dir') === 'asc' ? -1 : 1;
    var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
    var num = function (s) { var n = parseFloat(String(s).replace(/[^0-9.\-]/g, '')); return isNaN(n) ? null : n; };
    rows.sort(function (a, b) {
      var x = a.children[idx] ? a.children[idx].textContent.trim() : '';
      var y = b.children[idx] ? b.children[idx].textContent.trim() : '';
      if (x.indexOf('\u2014') === 0) return 1;   // blanks always last
      if (y.indexOf('\u2014') === 0) return -1;
      var nx = num(x), ny = num(y);
      if (nx !== null && ny !== null) return (nx - ny) * dir;
      return x.localeCompare(y) * dir;
    });
    rows.forEach(function (r) { tbody.appendChild(r); });
    th.parentNode.querySelectorAll('th').forEach(function (h) { h.removeAttribute('data-dir'); });
    th.setAttribute('data-dir', dir === 1 ? 'asc' : 'desc');
  };

  document.addEventListener('DOMContentLoaded', function () {
    wrapAll();
    document.querySelectorAll('.filter').forEach(function (i) {
      i.addEventListener('input', function () { filterRows(i); });
    });
    document.querySelectorAll('th.sortable').forEach(function (th) {
      th.addEventListener('click', function () { sortTable(th); });
    });
  });
})();
