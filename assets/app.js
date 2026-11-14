// Table search and status filter. Works with any table whose inputs carry data-filter="<table id>".
(function () {
  document.querySelectorAll('input[data-filter]').forEach(function (inp) {
    var id = inp.getAttribute('data-filter');
    var table = document.getElementById(id);
    var sel = document.querySelector('select[data-filter="' + id + '"]');
    if (!table) return;
    function apply() {
      var q = inp.value.trim().toLowerCase();
      var st = sel ? sel.value : '';
      Array.prototype.forEach.call(table.tBodies[0].rows, function (tr) {
        var okQ = !q || tr.textContent.toLowerCase().indexOf(q) !== -1;
        var okS = !st || tr.getAttribute('data-status') === st;
        tr.style.display = (okQ && okS) ? '' : 'none';
      });
    }
    inp.addEventListener('input', apply);
    if (sel) sel.addEventListener('change', apply);
  });
})();
