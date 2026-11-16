
(function () {
  // ---- table filtering -------------------------------------------------
  function filterTables() {
    var tables = {};
    document.querySelectorAll('input[type=search][data-filter]').forEach(function (input) {
      var id = input.getAttribute('data-filter');
      var table = document.getElementById(id);
      if (!table) return;
      tables[id] = {
        input: input,
        table: table,
        selects: Array.prototype.slice.call(document.querySelectorAll('select[data-filter="' + id + '"]'))
      };
    });

    function colFor(select, heads) {
      var want = select.getAttribute('aria-label').replace(/^filter /i, '').trim().toLowerCase();
      for (var i = 0; i < heads.length; i++) {
        if (heads[i].textContent.trim().toLowerCase() === want) return i;
      }
      return -1;
    }

    function apply(cfg) {
      var q = cfg.input.value.toLowerCase().trim();
      var heads = Array.prototype.slice.call(cfg.table.querySelectorAll('thead th'));
      var rows = Array.prototype.slice.call(cfg.table.tBodies[0].rows);
      rows.forEach(function (row) {
        var ok = !q || row.textContent.toLowerCase().indexOf(q) !== -1;
        if (ok) {
          cfg.selects.forEach(function (sel) {
            if (!ok) return;
            var v = sel.value.trim();
            if (!v) return;
            var ci = colFor(sel, heads);
            if (ci < 0) return;
            var cell = row.cells[ci];
            if (!cell || cell.textContent.trim() !== v) ok = false;
          });
        }
        row.style.display = ok ? '' : 'none';
      });
    }

    Object.keys(tables).forEach(function (id) {
      var cfg = tables[id];
      cfg.input.addEventListener('input', function () { apply(cfg); });
      cfg.selects.forEach(function (sel) {
        sel.addEventListener('change', function () { apply(cfg); });
      });
    });
  }

  // ---- suggestion review board (stored in this browser only) -----------
  var KEY = 'fl4-lab-suggestions-v1';

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { return {}; }
  }

  function persist(data) {
    try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) {}
  }

  function applySaved(data) {
    Object.keys(data).forEach(function (id) {
      var v = data[id] || {};
      if (v.option) {
        var r = document.querySelector('input[name="sg-' + id + '"][value="' + v.option + '"]');
        if (r) r.checked = true;
      }
      var own = document.querySelector('input.own[data-sg="' + id + '"]');
      if (own && v.own) own.value = v.own;
    });
  }

  function collect() {
    var data = load();
    document.querySelectorAll('input[type=radio][name^="sg-"]').forEach(function (r) {
      if (!r.checked) return;
      var id = r.getAttribute('name').slice(3);
      data[id] = data[id] || {};
      data[id].option = r.value;
    });
    document.querySelectorAll('input.own[data-sg]').forEach(function (i) {
      var id = i.getAttribute('data-sg');
      data[id] = data[id] || {};
      data[id].own = i.value;
    });
    return data;
  }

  var note = document.getElementById('save-note');
  var saveBtn = document.getElementById('save-all');
  var clearBtn = document.getElementById('clear-all');
  var exportBtn = document.getElementById('export-all');

  if (saveBtn) saveBtn.addEventListener('click', function () {
    var d = collect();
    persist(d);
    var n = Object.keys(d).length;
    if (note) note.textContent = 'Saved ' + n + ' choice(s) in this browser only. To make one binding, set status in data/lab/suggestions.json.';
  });

  if (clearBtn) clearBtn.addEventListener('click', function () {
    try { localStorage.removeItem(KEY); } catch (e) {}
    document.querySelectorAll('input[type=radio][name^="sg-"]').forEach(function (r) { r.checked = false; });
    document.querySelectorAll('input.own[data-sg]').forEach(function (i) { i.value = ''; });
    if (note) note.textContent = 'Cleared saved choices from this browser.';
  });

  if (exportBtn) exportBtn.addEventListener('click', function () {
    var d = collect();
    var lines = Object.keys(d).sort().map(function (id) {
      return id + ': ' + (d[id].option || '(none)') + (d[id].own ? ' | ' + d[id].own : '');
    }).join('\n');
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(lines).then(function () {
        if (note) note.textContent = 'Copied ' + Object.keys(d).length + ' choice(s) to the clipboard.';
      }, function () { if (note) note.textContent = 'Copy failed. Choices: ' + lines; });
    } else if (note) {
      note.textContent = 'Clipboard unavailable. Choices: ' + lines;
    }
  });

  filterTables();
  applySaved(load());
})();
