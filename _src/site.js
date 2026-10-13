(function () {
  // Язык: ?lang=код; ru, uz, kk, ky, tg, be — русский; остальные — английский (как privacy.html). Без скрипта видны обе версии.
  // Язык: ?lang=ru|uz|uz-cyrl|en; иначе выбор, сохранённый в браузере; иначе язык браузера.
  // uz-Cyrl* — кириллица, uz* — латиница; kk, ky, tg, be — русский; остальные — английский. Без скрипта видны все версии.
  var RU = ['ru', 'kk', 'ky', 'tg', 'be'];
  var root = document.documentElement;
  root.classList.add('js');
  // Подсветка раздела, который сейчас на экране (только на главной).
  var observer = null;
  var markSection = null;  // подсветить пункт меню раздела (ставит watchSections)
  var lastSection = '';    // последний раздел (контакты) — до середины экрана он не доходит
  var lockUntil = 0;
  // Последний раздел короче экрана: внизу страницы подсвечиваем его (отзыв 13.10: «Контакты» — а горит «Цены»).
  window.addEventListener('scroll', function () {
    if (!markSection || Date.now() < lockUntil) return;
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) markSection(lastSection);
  }, { passive: true });
  // Клик по пункту меню раздела: сразу подсветить пункт и мягко выделить сам раздел.
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('[data-sec]');
    if (!a || !markSection) return;
    var id = a.getAttribute('data-sec');
    lockUntil = Date.now() + 1200;
    markSection(id);
    var sec = document.getElementById(id);
    if (!sec) return;
    sec.classList.remove('flash');
    void sec.offsetWidth; // перезапуск анимации при повторном клике
    sec.classList.add('flash');
    setTimeout(function () { sec.classList.remove('flash'); }, 1800);
  });
  function watchSections(lang) {
    if (!('IntersectionObserver' in window)) return;
    if (observer) observer.disconnect();
    var ids = ['how', 'client', 'price', 'contact'];
    var links = document.querySelectorAll('[data-sec]');
    function mark(id) {
      for (var i = 0; i < links.length; i++) {
        if (links[i].getAttribute('data-sec') === id) links[i].setAttribute('aria-current', 'location');
        else links[i].removeAttribute('aria-current');
      }
    }
    observer = new IntersectionObserver(function (entries) {
      if (Date.now() < lockUntil) return; // переход по ссылке меню: подсветку уже поставил клик
      for (var i = 0; i < entries.length; i++) {
        if (entries[i].isIntersecting) mark(entries[i].target.id);
      }
    }, { rootMargin: '-45% 0px -50% 0px' });
    markSection = mark;
    lastSection = ids[ids.length - 1] + '-' + lang;
    var found = false;
    for (var k = 0; k < ids.length; k++) {
      var el = document.getElementById(ids[k] + '-' + lang);
      if (el) { observer.observe(el); found = true; }
    }
    var hero = document.querySelector('.lang-block[data-lang="' + lang + '"] .hero');
    if (found && hero) {
      new IntersectionObserver(function (en) { if (en[0].isIntersecting) mark(''); }, { rootMargin: '-45% 0px -50% 0px' }).observe(hero);
    }
  }
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
    var mb = document.getElementById('menu-btn');
    if (mb && mb.getAttribute('data-label-' + lang)) mb.setAttribute('aria-label', mb.getAttribute('data-label-' + lang));
    if (typeof watchSections === 'function') watchSections(lang);
  }
  var q = null;
  try { q = new URLSearchParams(window.location.search).get('lang'); } catch (e) { q = null; }
  // Страница языка (/ru/, /uz/, /uz-cyrl/, /en/) задаёт язык сама; ?lang важнее везде, сохранённый выбор и язык браузера — только на корне.
  var fixed = root.getAttribute('data-lang-fixed');
  var current = pick(q || fixed || saved() || navigator.language || 'en');
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
  // Меню на телефоне: открыть/закрыть кнопкой, закрыть по ссылке, Escape или нажатию вне меню.
  var menuBtn = document.getElementById('menu-btn');
  var menuPanel = document.getElementById('menu-panel');
  function setMenu(open) {
    if (!menuBtn || !menuPanel) return;
    menuPanel.hidden = !open;
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  if (menuBtn) {
    menuBtn.addEventListener('click', function (ev) { ev.stopPropagation(); setMenu(menuPanel.hidden); });
    menuPanel.addEventListener('click', function (ev) { if (ev.target.closest('a')) setMenu(false); });
    document.addEventListener('click', function (ev) { if (!menuPanel.hidden && !ev.target.closest('.site-head')) setMenu(false); });
    document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape' && !menuPanel.hidden) { setMenu(false); menuBtn.focus(); } });
  }
  // Логотип на главной — плавно наверх, без перезагрузки.
  var home = document.querySelector('[data-home]');
  if (home && document.querySelector('.hero')) {
    home.addEventListener('click', function (ev) {
      ev.preventDefault();
      setMenu(false);
      var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
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
