(function () {
  // Язык: ?lang=код; ru, uz, kk, ky, tg, be — русский; остальные — английский (как privacy.html). Без скрипта видны обе версии.
  // Язык: ?lang=ru|uz|uz-cyrl|en; иначе выбор, сохранённый в браузере; иначе язык браузера.
  // uz-Cyrl* — кириллица, uz* — латиница; kk, ky, tg, be — русский; остальные — английский. Без скрипта видны все версии.
  var RU = ['ru', 'kk', 'ky', 'tg', 'be'];
  var root = document.documentElement;
  root.classList.add('js');
  function pick(code) {
    var c = (code || '').toLowerCase();
    if (c.indexOf('uz') === 0) return c.indexOf('cyrl') >= 0 ? 'uz-cyrl' : 'uz';
    return RU.indexOf(c.slice(0, 2)) >= 0 ? 'ru' : 'en';
  }
  function save(lang) { try { localStorage.setItem('ee-lang', lang); } catch (e) { /* хранилище недоступно */ } }
  function saved() { try { return localStorage.getItem('ee-lang'); } catch (e) { return null; } }
  function apply(lang) {
    var attr = lang === 'uz' ? 'uz-Latn' : lang === 'uz-cyrl' ? 'uz-Cyrl' : lang;
    root.lang = attr;
    var blocks = document.querySelectorAll('.lang-block');
    for (var i = 0; i < blocks.length; i++) {
      blocks[i].setAttribute('data-hidden', blocks[i].getAttribute('data-lang') === lang ? 'false' : 'true');
    }
    var isUz = lang.indexOf('uz') === 0;
    var links = document.querySelectorAll('[data-l]');
    for (var j = 0; j < links.length; j++) {
      var l = links[j];
      var on = l.getAttribute('data-group') === 'uz' ? isUz : l.getAttribute('data-l') === lang;
      if (on) l.setAttribute('aria-current', 'true'); else l.removeAttribute('aria-current');
    }
    var bar = document.querySelector('.scriptbar');
    if (bar) bar.hidden = !isUz;
    var page = document.querySelector('.page');
    var t = page && page.getAttribute('data-title-' + lang);
    if (t) document.title = t;
  }
  var q = null;
  try { q = new URLSearchParams(window.location.search).get('lang'); } catch (e) { q = null; }
  var current = pick(q || saved() || navigator.language || 'en');
  apply(current);
  var lastUz = current.indexOf('uz') === 0 ? current : (pick(saved() || '') === 'uz-cyrl' ? 'uz-cyrl' : 'uz');
  var links = document.querySelectorAll('[data-l]');
  for (var k = 0; k < links.length; k++) {
    links[k].addEventListener('click', function (ev) {
      ev.preventDefault();
      var lang = this.getAttribute('data-l');
      if (this.getAttribute('data-group') === 'uz') lang = current.indexOf('uz') === 0 ? current : lastUz;
      if (lang.indexOf('uz') === 0) lastUz = lang;
      current = lang;
      apply(lang);
      save(lang);
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
