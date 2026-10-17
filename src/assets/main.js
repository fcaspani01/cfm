// Unico script del sito: chiude il menu mobile al click e invia il modulo di richiesta via email.
(function () {
  var toggle = document.getElementById('nav-toggle');
  document.querySelectorAll('.nav-list a').forEach(function (a) {
    a.addEventListener('click', function () { if (toggle) toggle.checked = false; });
  });

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
