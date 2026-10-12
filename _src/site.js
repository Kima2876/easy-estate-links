(function () {
  // Язык: ?lang=код; ru, uz, kk, ky, tg, be — русский; остальные — английский (как privacy.html). Без скрипта видны обе версии.
  var RU = ['ru', 'uz', 'kk', 'ky', 'tg', 'be'];
  var root = document.documentElement;
  root.classList.add('js');
  function pick(code) { return RU.indexOf((code || '').toLowerCase().slice(0, 2)) >= 0 ? 'ru' : 'en'; }
  function apply(lang) {
    root.lang = lang;
    var blocks = document.querySelectorAll('.lang-block');
    for (var i = 0; i < blocks.length; i++) {
      blocks[i].setAttribute('data-hidden', blocks[i].getAttribute('data-lang') === lang ? 'false' : 'true');
    }
    var links = document.querySelectorAll('.langs a');
    for (var j = 0; j < links.length; j++) {
      if (links[j].getAttribute('data-l') === lang) links[j].setAttribute('aria-current', 'true');
      else links[j].removeAttribute('aria-current');
    }
    document.title = lang === 'ru' ? 'EASY ESTATE - инструмент риелтора' : 'EASY ESTATE - a tool for real estate agents';
  }
  var q = null;
  try { q = new URLSearchParams(window.location.search).get('lang'); } catch (e) { q = null; }
  apply(pick(q || navigator.language || 'en'));
  var links = document.querySelectorAll('.langs a');
  for (var k = 0; k < links.length; k++) {
    links[k].addEventListener('click', function (ev) {
      ev.preventDefault();
      var lang = this.getAttribute('data-l');
      apply(lang);
      try { history.replaceState(null, '', '?lang=' + lang); } catch (e) { /* в превью адрес не меняется */ }
    });
  }
  var buttons = document.querySelectorAll('.copy');
  for (var b = 0; b < buttons.length; b++) {
    buttons[b].addEventListener('click', function () {
      var btn = this;
      var box = btn.parentNode;
      var addr = box.querySelector('.mail-addr');
      var status = box.querySelector('.copy-status');
      function done() { status.textContent = btn.getAttribute('data-copied'); }
      function fallback() {
        var r = document.createRange();
        r.selectNodeContents(addr);
        var s = window.getSelection();
        s.removeAllRanges();
        s.addRange(r);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(addr.textContent).then(done, fallback);
      } else { fallback(); }
    });
  }
})();
