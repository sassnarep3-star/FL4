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

// Review choices are deliberately local to this browser; they never change site data.
(function () {
  var controls = Array.prototype.slice.call(document.querySelectorAll('[data-suggestion-choice]'));
  if (!controls.length) return;
  var prefix = 'fl4:suggestion-choice:';
  var feedback = document.querySelector('[data-suggestion-feedback]');

  function setMessage(message) {
    if (feedback) feedback.textContent = message;
  }

  controls.forEach(function (select) {
    var id = select.getAttribute('data-suggestion-choice');
    var key = prefix + id;
    try {
      var saved = window.localStorage.getItem(key);
      if (saved && Array.prototype.some.call(select.options, function (option) { return option.value === saved; })) {
        select.value = saved;
        if (select.closest('tr')) select.closest('tr').classList.add('decision-made');
      }
    } catch (error) {
      setMessage('Browser storage is unavailable; choices will not persist after you leave this page.');
    }
    select.addEventListener('change', function () {
      try {
        if (select.value) {
          window.localStorage.setItem(key, select.value);
        } else {
          window.localStorage.removeItem(key);
        }
        if (select.closest('tr')) select.closest('tr').classList.toggle('decision-made', Boolean(select.value));
        setMessage(select.value ? id + ' choice saved in this browser only.' : 'Choice cleared.');
      } catch (error) {
        setMessage('Browser storage is unavailable; this choice could not be saved.');
      }
    });
  });

  var clearButton = document.querySelector('[data-clear-suggestion-choices]');
  if (clearButton) {
    clearButton.addEventListener('click', function () {
      try {
        controls.forEach(function (select) {
          window.localStorage.removeItem(prefix + select.getAttribute('data-suggestion-choice'));
          select.value = '';
          if (select.closest('tr')) select.closest('tr').classList.remove('decision-made');
        });
        setMessage('All saved choices for this site were cleared from this browser.');
      } catch (error) {
        setMessage('Browser storage is unavailable; saved choices could not be cleared.');
      }
    });
  }
})();
