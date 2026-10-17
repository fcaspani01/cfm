// Unico script del sito: chiude il menu mobile al click e invia il modulo di richiesta via email.
(function () {
  var toggle = document.getElementById('nav-toggle');
  document.querySelectorAll('.nav-list a').forEach(function (a) {
    a.addEventListener('click', function () { if (toggle) toggle.checked = false; });
  });

  // Display della caldaia: la temperatura sale fino al valore finale
  var temp = document.querySelector('.hi-temp');
  if (temp && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var to = parseInt(temp.dataset.to, 10), from = 20, t0 = null;
    var step = function (ts) {
      if (!t0) t0 = ts;
      var p = Math.min((ts - t0) / 1800, 1), eased = 1 - Math.pow(1 - p, 3);
      temp.textContent = Math.round(from + (to - from) * eased) + '°';
      if (p < 1) requestAnimationFrame(step);
    };
    temp.textContent = from + '°';
    setTimeout(function () { requestAnimationFrame(step); }, 600);
  }

  var form = document.getElementById('richiesta-form');
  if (!form) return;
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var d = new FormData(form);
    var body = [
      'Nome: ' + (d.get('nome') || ''),
      'Telefono: ' + (d.get('telefono') || ''),
      'Comune: ' + (d.get('comune') || ''),
      'Tipo di richiesta: ' + (d.get('tipo') || ''),
      'Modello caldaia: ' + (d.get('modello') || ''),
      '',
      (d.get('messaggio') || '')
    ].join('\n');
    var subject = 'Richiesta intervento – ' + (d.get('tipo') || 'caldaia') + ' – ' + (d.get('comune') || '');
    window.location.href = 'mailto:' + form.dataset.email +
      '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    var ok = document.getElementById('form-ok');
    if (ok) ok.hidden = false;
  });
})();
