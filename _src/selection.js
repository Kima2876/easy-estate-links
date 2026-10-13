(function () {
  'use strict';
  // Страница подборки (search_selections_v1, раздел 7). Токен — только во фрагменте #t=
  // (фрагмент не уходит на сервер сайта); функция selection-view получает его в теле запроса.
  // Страница только показывает; любое действие — в приложении (easyestate://selection?t=...).
  var CFG = window.EE_SEL;
  var LANGS = ['ru', 'uz', 'en', 'id'];
  var LOCALE = { ru: 'ru-RU', en: 'en-US', uz: 'uz-Latn-UZ', id: 'id-ID' };
  var GEO_COL = { en: 0, ru: 1, uz: 2, id: 3 };
  var CURRENCIES = ['USD', 'EUR', 'UZS', 'RUB', 'KZT', 'AED', 'IDR', 'THB', 'MYR', 'TRY', 'GBP', 'CNY'];
  var SOTKA = ['UZ', 'KZ', 'KG', 'TJ', 'RU', 'BY'];
  var CITY_REGIONS = [1484839, 292224, 1609348, 1642907, 1733046, 1996552]; // geo_directory.dart cityRegionIds
  var BEDROOM_TYPES = ['apartment', 'house', 'villa', 'townhouse', 'hotel_room', 'shophouse'];
  var STALE_MS = 50 * 60 * 1000; // ссылки на фото живут час
  var TOKEN_RE = /^[A-Za-z0-9_-]{20,128}$/;
  var UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

  var app = document.getElementById('app');
  var cta = document.getElementById('cta');
  var openBtn = document.getElementById('open');
  var reg = null;           // реестр и названия на языке страницы
  var regLang = null;
  var geoCache = {};
  var listCache = null;     // { key, data, items, cursor, loadedAt, scroll }
  var lastRender = 0;
  var retryTimer = null;
  var tolTimer = null;

  // ---------- состояние из фрагмента ----------
  function params() {
    var p = new URLSearchParams((location.hash || '').replace(/^#/, ''));
    var t = p.get('t') || '';
    var lang = (p.get('lang') || '').toLowerCase().split('-')[0];
    if (LANGS.indexOf(lang) < 0) lang = pickLang();
    var pid = p.get('p') || '';
    var cur = (p.get('cur') || '').toUpperCase();
    var tol = parseInt(p.get('tol') || '', 10);
    return {
      t: t, lang: lang,
      pid: UUID_RE.test(pid) ? pid : '',
      cur: /^[A-Z]{3}$/.test(cur) ? cur : '',
      tol: isFinite(tol) && tol >= 0 && tol <= 100 ? tol : 0
    };
  }
  function pickLang() {
    var list = navigator.languages || [navigator.language || ''];
    for (var i = 0; i < list.length; i++) {
      var c = String(list[i] || '').toLowerCase().split('-')[0];
      if (c === 'in') c = 'id';
      if (LANGS.indexOf(c) >= 0) return c;
      if (['kk', 'ky', 'tg', 'be', 'uk'].indexOf(c) >= 0) return 'ru';
    }
    return 'en';
  }
  function hashOf(s) {
    var p = new URLSearchParams();
    p.set('t', s.t);
    p.set('lang', s.lang);
    if (s.pid) p.set('p', s.pid);
    if (s.cur) p.set('cur', s.cur);
    if (s.tol) p.set('tol', String(s.tol));
    return '#' + p.toString();
  }
  function go(change) {
    var s = params();
    for (var k in change) s[k] = change[k];
    location.hash = hashOf(s);
  }

  // ---------- текст ----------
  function ui(lang) { return CFG.ui[lang] || CFG.ui.en; }
  function fill(str, n) { return String(str).replace('{n}', n).replace('{v}', n).replace('{d}', n); }
  function plural(lang, forms, n) {
    var cat = 'other';
    try { cat = new Intl.PluralRules(LOCALE[lang]).select(n); } catch (e) { /* старый браузер */ }
    return fill(forms[cat] || forms.other || forms.many || forms.few, n);
  }
  function nf(lang, digits) {
    try { return new Intl.NumberFormat(LOCALE[lang], { maximumFractionDigits: digits || 0 }); }
    catch (e) { return new Intl.NumberFormat('en-US', { maximumFractionDigits: digits || 0 }); }
  }
  function num(lang, v, digits) { return nf(lang, digits).format(v).replace(/\s/g, ' '); }
  function money(lang, v, cur) { return num(lang, Math.round(v)) + (cur ? ' ' + cur : ''); }
  function dateText(lang, value) {
    var d = new Date(value);
    if (isNaN(d.getTime())) return String(value);
    try { return new Intl.DateTimeFormat(LOCALE[lang], { day: 'numeric', month: 'long', year: 'numeric' }).format(d); }
    catch (e) { return d.toISOString().slice(0, 10); }
  }
  function countryName(lang, code) {
    try { return new Intl.DisplayNames([LOCALE[lang]], { type: 'region' }).of(code) || code; }
    catch (e) { return code; }
  }

  // ---------- данные ----------
  function getJSON(url) {
    return fetch(url, { credentials: 'omit' }).then(function (r) {
      if (!r.ok) throw new Error('http ' + r.status);
      return r.json();
    });
  }
  function loadReg(lang) {
    if (reg && regLang === lang) return Promise.resolve(reg);
    return getJSON('assets/sel/' + lang + '.json?v=' + CFG.reg).then(function (r) { reg = r; regLang = lang; return r; });
  }
  function loadGeo(cc) {
    cc = String(cc || '').toLowerCase();
    if (!/^[a-z]{2}$/.test(cc)) return Promise.resolve(null);
    if (geoCache[cc] !== undefined) return Promise.resolve(geoCache[cc]);
    return getJSON('assets/geo/' + cc + '.json?v=' + CFG.reg)
      .then(function (g) { geoCache[cc] = g; return g; }, function () { geoCache[cc] = null; return null; });
  }
  function call(body) {
    return fetch(CFG.fn, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body),
      credentials: 'omit',
      cache: 'no-store',
      referrerPolicy: 'no-referrer'
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (data) {
        if (r.ok) return data;
        var err = new Error(data && data.error || ('http_' + r.status));
        err.code = data && data.error || 'http_' + r.status;
        err.status = r.status;
        err.retry = parseInt(r.headers.get('retry-after') || '', 10) || 10;
        throw err;
      });
    });
  }

  // ---------- DOM ----------
  function h(tag, attrs, kids) {
    var el = document.createElement(tag);
    if (attrs) {
      for (var k in attrs) {
        var v = attrs[k];
        if (v === null || v === undefined || v === false) continue;
        if (k === 'text') el.textContent = v;
        else if (k === 'cls') el.className = v;
        else if (k.slice(0, 2) === 'on') el.addEventListener(k.slice(2), v);
        else el.setAttribute(k, v === true ? '' : v);
      }
    }
    (kids || []).forEach(function (c) {
      if (c === null || c === undefined || c === false) return;
      el.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    });
    return el;
  }
  var HOUSE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3 2 11h3v9h5v-6h4v6h5v-9h3z"/></svg>';
  function setContent(nodes) {
    app.textContent = '';
    nodes.forEach(function (n) { if (n) app.appendChild(n); });
  }
  function stateBox(title, text, button) {
    return h('div', { cls: 'state' }, [title ? h('b', { text: title }) : null, text ? h('p', { text: text }) : null, button || null]);
  }

  // ---------- значения полей (как value_text.dart приложения) ----------
  function ctxOf(lang, card, geo, country) {
    return {
      lang: lang, t: ui(lang), geo: geo, country: country,
      currency: card.currency || null,
      units: card.area_units || ['m2'],
      custom: card.custom_labels || {},
      type: card.fields && card.fields.property_type || null
    };
  }
  function dictLabel(c, dict, code) {
    code = String(code);
    if (code.indexOf('x:') === 0) {
      var own = c.custom[code];
      return own ? (own.label || own.original || null) : null;
    }
    var d = reg.dicts[dict];
    if (!d) return null;
    if (c.type && d._by_type && d._by_type[c.type] && d._by_type[c.type][code]) return d._by_type[c.type][code];
    return typeof d[code] === 'string' ? d[code] : null;
  }
  function geoName(c, kind, code) {
    var g = c.geo && c.geo[kind] && c.geo[kind][String(code)];
    if (!g) return null;
    var name = g[GEO_COL[c.lang]] || g[0];
    // Регион, который сам город (Ташкент, Дубай и др.), — «<название> (город)», как в приложении.
    return kind === 'r' && CITY_REGIONS.indexOf(Number(code)) >= 0 ? fill(c.t.city_region, name) : name;
  }
  function areaText(c, m2, key) {
    if (typeof m2 !== 'number') return null;
    var unit = (c.units || []).indexOf('sqft') >= 0 && (c.units || []).indexOf('m2') < 0 ? 'sqft' : 'm2';
    var meters = unit === 'sqft'
      ? num(c.lang, m2 * 10.7639104, 0) + ' ' + c.t.sqft
      : num(c.lang, m2, 1) + ' ' + c.t.m2;
    if (key === 'land_area' && SOTKA.indexOf(c.country) >= 0) {
      var s = Math.round(m2) / 100;
      var form = s % 1 !== 0 ? 'fraction' : (function (n) {
        if (n % 10 === 1 && n % 100 !== 11) return 'one';
        if (n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14)) return 'few';
        return 'many';
      })(Math.abs(s));
      var tpl = c.t.sotka[form] || c.t.sotka.other || c.t.sotka.many;
      return fill(tpl, num(c.lang, s, 2)) + ' (' + num(c.lang, m2, 1) + ' ' + c.t.m2 + ')';
    }
    return meters;
  }
  function bedroomsText(c, v) {
    if (typeof v !== 'number' || v < 0) return null;
    if (v === 0) return !c.type || BEDROOM_TYPES.indexOf(c.type) >= 0 ? c.t.studio : null;
    return plural(c.lang, c.t.bedrooms, v);
  }
  function valueText(c, fullKey, value) {
    if (value === null || value === undefined || value === '') return null;
    var def = reg.types[fullKey];
    if (!def) return null;
    var type = def[0], dict = def[1], key = fullKey.split('.')[1];
    switch (type) {
      case 'text': case 'long_text': case 'system': case 'email': case 'time':
        return String(value).trim() || null;
      case 'int':
        if (key === 'parking_spaces' && value === 0) return c.t.no_parking;
        if (key === 'bedrooms') return bedroomsText(c, value);
        if (key === 'rooms_total' && value > 0) return plural(c.lang, c.t.rooms, value);
        return String(value); // как в приложении: без разрядов (год постройки, этаж)
      case 'decimal':
        return typeof value === 'number' ? num(c.lang, value, 2) : String(value);
      case 'money':
        return typeof value === 'number' ? money(c.lang, value, c.currency) : null;
      case 'area':
        return areaText(c, value, key);
      case 'bool':
        return value === true ? c.t.yes : c.t.no;
      case 'date':
        return dateText(c.lang, value);
      case 'dict':
        if (dict === 'country') return countryName(c.lang, String(value));
        if (dict === 'city') return geoName(c, 'c', value);
        if (dict === 'region') {
          var r = geoName(c, 'r', value);
          return r;
        }
        return dictLabel(c, dict, value);
      case 'dict_multi':
        var codes = Array.isArray(value) ? value : [value];
        var names = codes.map(function (x) { return dictLabel(c, dict, x); }).filter(Boolean);
        return names.length ? names.join(', ') : null;
      case 'dict_or_text':
        if (value && typeof value === 'object') return value.text ? String(value.text) : null;
        return /^[0-9]+$/.test(String(value)) ? null : String(value);
      case 'season_prices':
        if (!Array.isArray(value) || !value.length) return null;
        return value.filter(function (s) { return s && typeof s === 'object'; }).map(function (s) {
          return s.from + '–' + s.to + ': ' + money(c.lang, Number(s.rate) || 0, c.currency);
        }).join('; ');
      default:
        return null; // commission, geo, media, ref — на веб не показываются
    }
  }
  function placeText(c, fields) {
    var d = fields.district;
    var district = d && typeof d === 'object' ? (d.text || '') : '';
    var city = fields.city ? geoName(c, 'c', fields.city) : null;
    return [district, city].filter(Boolean).join(', ');
  }
  function nameText(c, fields, revealed) {
    var type = fields.property_type ? dictLabel(c, 'property_type', fields.property_type) : null;
    var sub = fields.property_subtype ? dictLabel(c, 'property_subtype', fields.property_subtype) : null;
    var complex = revealed && revealed.complex_name ? String(revealed.complex_name) : '';
    var main = sub ? (type ? type + ', ' + sub.charAt(0).toLowerCase() + sub.slice(1) : sub) : (type || reg.entities.property);
    return complex ? main + ' · ' + complex : main;
  }
  function summaryText(c, fields) {
    var parts = [];
    if (typeof fields.bedrooms === 'number') {
      if (fields.bedrooms > 0) parts.push(fill(c.t.sum_bed, fields.bedrooms));
      else { var s = bedroomsText(c, 0); if (s) parts.push(s); }
    }
    var area = typeof fields.total_area === 'number' ? areaText(c, fields.total_area, 'total_area')
      : (typeof fields.land_area === 'number' ? areaText(c, fields.land_area, 'land_area') : null);
    if (area) parts.push(area);
    var f = fields.floor, tf = fields.total_floors, fl = null;
    if (f > 0 && tf > 0) fl = f + '/' + tf; else if (f > 0) fl = String(f); else if (tf > 0) fl = String(tf);
    if (fl) parts.push(fill(c.t.sum_floor, fl));
    return parts.join(' · ');
  }
  function offerPrice(c, offer, display) {
    var conv = typeof offer.price_display === 'number' && display && display.currency &&
      display.currency !== c.currency;
    var amount = conv ? offer.price_display : offer.price;
    if (typeof amount !== 'number') return null;
    var text = money(c.lang, amount, conv ? display.currency : c.currency);
    var per = offer.kind === 'rent' && offer.rent_period ? c.t.per[offer.rent_period] : '';
    return { text: text, per: per || '' };
  }

  // ---------- карточка в списке ----------
  function cardNode(s, c, item, display, kind) {
    if (!item.available) return h('div', { cls: 'card gone', text: c.t.gone });
    var fields = item.fields || {};
    var cc = ctxOf(s.lang, item, c.geo, c.country);
    var media = item.main_media && item.main_media.url
      ? h('img', { src: item.main_media.url, alt: '', loading: 'lazy', decoding: 'async', referrerpolicy: 'no-referrer' })
      : null;
    var empty = h('div', { cls: 'ph-empty', hidden: !!media });
    empty.innerHTML = HOUSE;
    if (media) media.addEventListener('error', function () { media.remove(); empty.hidden = false; });
    var badges = h('div', { cls: 'badges' }, [
      item.recommended && !item.recommendation_removed ? h('span', { cls: 'badge rec', text: cc.t.rec_badge }) : null,
      item.photo_count > 1 ? h('span', { cls: 'badge', text: fill(cc.t.photos, item.photo_count) }) : null,
      item.has_video ? h('span', { cls: 'badge', text: cc.t.video }) : null
    ]);
    var prices = (item.offers || []).map(function (o) { return offerPrice(cc, o, display); }).filter(Boolean);
    var priceNode = prices.length ? h('p', { cls: 'price' }, [
      prices[0].text, prices[0].per ? h('small', { text: ' ' + prices[0].per }) : null,
      prices[1] ? h('small', { text: ' · ' + prices[1].text + (prices[1].per ? ' ' + prices[1].per : '') }) : null
    ]) : null;
    var place = placeText(cc, fields);
    var meta = [summaryText(cc, fields), place].filter(Boolean).join(' · ');
    var dev = null;
    if (kind === 'matching' && typeof item.price_dev_pct === 'number' && Math.abs(item.price_dev_pct) >= 1) {
      var p = Math.round(Math.abs(item.price_dev_pct));
      dev = h('p', { cls: 'dev', text: fill(item.price_dev_pct > 0 ? cc.t.dev_up : cc.t.dev_down, p) });
    }
    var link = hashOf({ t: s.t, lang: s.lang, pid: item.id, cur: s.cur, tol: s.tol });
    return h('a', { cls: 'card', href: link }, [
      h('div', { cls: 'ph' }, [media, empty, badges]),
      h('div', { cls: 'body' }, [
        priceNode,
        h('p', { cls: 'name', text: nameText(cc, fields, item.revealed) }),
        meta ? h('p', { cls: 'meta', text: meta }) : null,
        dev
      ])
    ]);
  }

  // ---------- шапка риелтора и критерии ----------
  function realtorNode(lang, realtor) {
    var t = ui(lang);
    realtor = realtor || {};
    var name = String(realtor.name || '').trim();
    var bits = [];
    var place = [realtor.city, realtor.country_code ? countryName(lang, realtor.country_code) : null]
      .filter(function (x) { return x && String(x).trim(); }).join(', ');
    if (place) bits.push(place);
    if (typeof realtor.experience_years === 'number' && realtor.experience_years > 0) {
      bits.push(plural(lang, t.exp, realtor.experience_years));
    }
    return h('section', { cls: 'realtor', 'aria-label': t.realtor }, [
      h('div', { cls: 'avatar', 'aria-hidden': 'true', text: (name.charAt(0) || 'E').toUpperCase() }),
      h('div', null, [h('small', { text: t.realtor }), h('b', { text: name || 'EASY ESTATE' }), bits.length ? h('span', { text: bits.join(' · ') }) : null])
    ]);
  }
  function rangeText(c, r, fmt) {
    if (!r) return null;
    var has = function (x) { return typeof x === 'number'; };
    if (has(r.from) && has(r.to)) return fmt(r.from) + '–' + fmt(r.to);
    if (has(r.from)) return fill(c.t.from, fmt(r.from));
    if (has(r.to)) return fill(c.t.to, fmt(r.to));
    return null;
  }
  function areaRange(c, r, key) {
    // «60–90 кв. м»: единица один раз; участок в сотках — каждое значение полностью.
    if (key === 'land_area' && SOTKA.indexOf(c.country) >= 0) {
      return rangeText(c, r, function (v) { return areaText(c, v, key); });
    }
    var sqft = (c.units || []).indexOf('sqft') >= 0 && (c.units || []).indexOf('m2') < 0;
    var text = rangeText(c, r, function (v) { return sqft ? num(c.lang, v * 10.7639104, 0) : num(c.lang, v, 1); });
    return text ? text + '\u00a0' + (sqft ? c.t.sqft : c.t.m2) : null;
  }
  function criteriaNode(s, c, data) {
    var sum = data.summary;
    var sel = data.selection;
    var display = data.display || {};
    var t = c.t;
    var lines = [];
    if (sum) {
      var head = [];
      if (sum.deal) head.push(sum.deal === 'sale' ? t.sale : t.rent);
      var types = (sum.types || []).map(function (x) { return dictLabel(c, 'property_type', x); }).filter(Boolean);
      if (types.length) head.push(types.join(', '));
      var where = [];
      (sum.districts || []).forEach(function (d) { if (d && !/^[0-9]+$/.test(String(d.text || d))) where.push(String(d.text || d)); });
      if (sum.city) { var cn = geoName(c, 'c', Array.isArray(sum.city) ? sum.city[0] : sum.city); if (cn) where.push(cn); }
      (sum.regions || []).forEach(function (r) { var rn = geoName(c, 'r', r); if (rn) where.push(rn); });
      if (!where.length && sum.country) where.push(countryName(s.lang, String(sum.country)));
      if (where.length) head.push(where.join(', '));
      if (head.length) lines.push(h('p', { text: head.join(' · ') }));
      if (sum.price) {
        var conv = sum.price.display && display.currency && display.currency !== sum.price.currency;
        var src = conv ? sum.price.display : sum.price;
        var cur = conv ? display.currency : sum.price.currency;
        var pt = rangeText(c, src, function (v) { return money(s.lang, v, null); });
        if (pt) {
          var tol = typeof sel.price_tolerance_pct === 'number' ? sel.price_tolerance_pct : sum.price.tolerance_pct;
          lines.push(h('p', { text: t.price + ': ' + pt + ' ' + cur + (tol ? ' ± ' + tol + ' %' : '') }));
        }
      }
      if (sum.area) {
        var at = areaRange(c, sum.area, 'total_area');
        var atol = typeof sel.area_tolerance_pct === 'number' ? sel.area_tolerance_pct : sum.area.tolerance_pct;
        if (at) lines.push(h('p', { text: t.area + ': ' + at + (atol ? ' ± ' + atol + ' %' : '') }));
      }
      if (sum.land_area) {
        var lt = areaRange(c, sum.land_area, 'land_area');
        if (lt) lines.push(h('p', { text: t.land + ': ' + lt }));
      }
      var rooms = [];
      if (sum.bedrooms) { var b = rangeText(c, sum.bedrooms, function (v) { return String(v); }); if (b) rooms.push(reg.names['property.bedrooms'] + ': ' + b); }
      if (sum.rooms) { var r2 = rangeText(c, sum.rooms, function (v) { return String(v); }); if (r2) rooms.push(reg.names['property.rooms_total'] + ': ' + r2); }
      if (rooms.length) lines.push(h('p', { text: rooms.join(' · ') }));
    }
    var controls = [];
    if (sel.kind === 'matching' && typeof sel.tolerance_limit_pct === 'number' && sel.tolerance_limit_pct > 0) {
      var out = h('output', { text: s.tol + ' %' });
      var range = h('input', {
        type: 'range', min: '0', max: String(sel.tolerance_limit_pct), step: '1', value: String(Math.min(s.tol, sel.tolerance_limit_pct)),
        id: 'tol', 'aria-describedby': 'tol-hint',
        oninput: function (e) { out.textContent = e.target.value + ' %'; },
        onchange: function (e) {
          var v = parseInt(e.target.value, 10) || 0;
          clearTimeout(tolTimer);
          tolTimer = setTimeout(function () { go({ tol: v, pid: '' }); }, 250);
        }
      });
      controls.push(h('div', { cls: 'control' }, [
        h('label', { for: 'tol' }, [t.tol, out]), range,
        h('small', { id: 'tol-hint', text: fill(t.tol_hint, sel.tolerance_limit_pct) })
      ]));
    }
    var base = sel.currency;
    if (base) {
      var shown = display.currency || base;
      var list = [base].concat(CURRENCIES.filter(function (x) { return x !== base; }));
      if (list.indexOf(shown) < 0) list.splice(1, 0, shown);
      var select = h('select', {
        id: 'cur',
        onchange: function (e) { go({ cur: e.target.value === base ? '' : e.target.value, pid: '' }); }
      }, list.map(function (code) { return h('option', { value: code, selected: code === shown, text: code }); }));
      var note = null;
      if (display.no_rate && s.cur && s.cur !== base) note = h('p', { cls: 'note-line warn', text: t.no_rate });
      else if (display.rate_date && shown !== base) note = h('p', { cls: 'note-line', text: fill(t.rate_date, dateText(s.lang, display.rate_date)) });
      controls.push(h('div', { cls: 'control' }, [h('label', { for: 'cur' }, [t.currency]), select, note]));
    }
    if (!lines.length && !controls.length) return null;
    return h('section', { cls: 'criteria' }, [
      lines.length ? h('h2', { text: t.criteria }) : null
    ].concat(lines).concat(controls.length ? [h('div', { cls: 'controls' }, controls)] : []));
  }
  function actNode(t) {
    return h('section', { cls: 'act' }, [h('p', { text: t.act }), h('small', { text: t.install })]);
  }

  // ---------- страница подборки ----------
  function listKey(s) { return [s.t, s.lang, s.cur, s.tol].join('|'); }
  function renderList(s) {
    var key = listKey(s);
    if (listCache && listCache.key === key && Date.now() - listCache.loadedAt < STALE_MS) {
      drawList(s, listCache);
      window.scrollTo(0, listCache.scroll || 0);
      return Promise.resolve();
    }
    setContent([h('div', { cls: 'skeleton' }), h('p', { cls: 'state', text: ui(s.lang).loading })]);
    return Promise.all([loadReg(s.lang), call(body(s, 'view'))]).then(function (res) {
      var data = res[1];
      return loadGeo(data.realtor && data.realtor.country_code).then(function (geo) {
        listCache = {
          key: key, data: data, geo: geo,
          items: (data.selection && data.selection.items) || [],
          cursor: data.selection && data.selection.next_cursor || null,
          loadedAt: Date.now(), scroll: 0
        };
        drawList(s, listCache);
        window.scrollTo(0, 0);
      });
    });
  }
  function body(s, action, extra) {
    var b = { t: s.t, action: action, lang: s.lang };
    if (s.cur) b.currency = s.cur;
    if (action === 'view' && s.tol) b.tolerance = s.tol;
    for (var k in (extra || {})) b[k] = extra[k];
    return b;
  }
  function drawList(s, cache) {
    var data = cache.data, sel = data.selection || {};
    var country = data.realtor && data.realtor.country_code || null;
    var c = ctxOf(s.lang, { currency: sel.currency }, cache.geo, country);
    var t = c.t;
    var display = data.display || {};
    var total = typeof sel.total === 'number' ? sel.total : cache.items.length;
    var nodes = [
      realtorNode(s.lang, data.realtor),
      h('h1', { cls: 'title', text: t.picked }),
      h('p', { cls: 'sub', text: plural(s.lang, t.objects, total) + ' · ' + t.now }),
      criteriaNode(s, c, data)
    ];
    var rec = (sel.recommended || []).filter(function (x) { return x.available; });
    if (rec.length) {
      nodes.push(h('h2', { cls: 'section-title', text: t.rec }));
      nodes.push(h('div', { cls: 'grid' }, rec.map(function (it) { return cardNode(s, c, it, display, sel.kind); })));
      nodes.push(h('h2', { cls: 'section-title', text: t.all }));
    }
    if (!cache.items.length) {
      nodes.push(stateBox(null, t.empty + (sel.kind === 'matching' && sel.tolerance_limit_pct > s.tol ? ' ' + t.empty_tol : '')));
    } else {
      nodes.push(h('div', { cls: 'grid', id: 'grid' }, cache.items.map(function (it) { return cardNode(s, c, it, display, sel.kind); })));
    }
    if (cache.cursor) {
      var btn = h('button', { cls: 'btn btn--ghost', type: 'button', text: t.more });
      btn.addEventListener('click', function () { more(s, cache, btn); });
      nodes.push(h('div', { cls: 'more' }, [btn]));
      if ('IntersectionObserver' in window) {
        var io = new IntersectionObserver(function (en) {
          if (en[0].isIntersecting) { io.disconnect(); more(s, cache, btn); }
        }, { rootMargin: '400px 0px' });
        setTimeout(function () { io.observe(btn); }, 0);
      }
    }
    nodes.push(actNode(t));
    setContent(nodes);
    showCta(s, true);
    lastRender = Date.now();
  }
  function more(s, cache, btn) {
    if (btn.disabled || !cache.cursor) return;
    btn.disabled = true;
    call(body(s, 'view', { cursor: cache.cursor })).then(function (data) {
      var sel = data.selection || {};
      cache.items = cache.items.concat(sel.items || []);
      cache.cursor = sel.next_cursor || null;
      var y = window.scrollY;
      drawList(s, cache);
      window.scrollTo(0, y);
    }, function (err) {
      btn.disabled = false;
      if (err.code === 'unavailable') showError(s, err);
    });
  }

  // ---------- страница объекта ----------
  function renderProperty(s) {
    if (listCache && listCache.key === listKey(s)) listCache.scroll = window.scrollY;
    setContent([h('div', { cls: 'skeleton' })]);
    return Promise.all([loadReg(s.lang), call(body(s, 'property', { property_id: s.pid }))]).then(function (res) {
      var data = res[1], p = data.property || {};
      var country = p.fields && p.fields.country || data.realtor && data.realtor.country_code;
      return loadGeo(country).then(function (geo) { drawProperty(s, data, geo, country); window.scrollTo(0, 0); });
    });
  }
  function rowsFor(c, keys, values) {
    var rows = [];
    keys.forEach(function (key) {
      var parts = key.split('.');
      var v = values[parts[0]] && values[parts[0]][parts[1]];
      var text = valueText(c, key, v);
      if (!text) return;
      if (parts[1] === 'region' && values.property.city) {
        // Регион совпадает с городом (Ташкент) — строку не повторять, как в приложении.
        var city = valueText(c, 'property.city', values.property.city);
        if (city && (text === city || text === fill(c.t.city_region, city))) return;
      }
      var label = reg.names[key] || parts[1];
      if (parts[1] === 'region' && reg.by_country.region && reg.by_country.region[c.country]) label = reg.by_country.region[c.country];
      rows.push(h('li', null, [h('span', { text: label }), h('b', { text: text })]));
    });
    return rows;
  }
  function drawProperty(s, data, geo, country) {
    var p = data.property || {};
    var fields = p.fields || {};
    var c = ctxOf(s.lang, p, geo, country);
    var t = c.t;
    var display = data.display || {};
    var nodes = [h('a', { cls: 'back', href: hashOf({ t: s.t, lang: s.lang, cur: s.cur, tol: s.tol }), text: '← ' + t.back })];

    var media = (p.media || []).filter(function (m) { return m.url; });
    if (media.length) {
      nodes.push(h('div', { cls: 'gallery' }, media.map(function (m, i) {
        if (m.kind === 'video') {
          return h('div', null, [h('video', { src: m.url, controls: true, preload: 'metadata', playsinline: true })]);
        }
        return h('div', null, [h('img', { src: m.url, alt: '', loading: i ? 'lazy' : 'eager', referrerpolicy: 'no-referrer' })]);
      })));
      if (media.length > 1) nodes.push(h('p', { cls: 'gallery-count', text: fill(t.photos, p.photo_count || media.length) + (p.has_video ? ' · ' + t.video : '') }));
    }

    var offers = p.offers || [];
    nodes.push(h('div', { cls: 'prices' }, offers.map(function (o) {
      var pr = offerPrice(c, o, display);
      if (!pr) return null;
      return h('div', null, [h('p', { cls: 'deal', text: o.kind === 'sale' ? t.sale : t.rent }),
        h('p', { cls: 'price' }, [pr.text, pr.per ? h('small', { text: ' ' + pr.per }) : null])]);
    })));
    if (display.no_rate && s.cur) nodes.push(h('p', { cls: 'note-line warn', text: t.no_rate }));

    nodes.push(h('h1', { cls: 'obj-title', text: nameText(c, fields, p.revealed) }));
    var meta = [summaryText(c, fields), placeText(c, fields)].filter(Boolean).join(' · ');
    if (meta) nodes.push(h('p', { cls: 'obj-meta', text: meta }));
    if (p.recommended) nodes.push(h('span', { cls: 'pill', text: t.rec_badge }));

    var note = p.audience_notes && p.audience_notes.client_note;
    if (note && String(note).trim()) nodes.push(h('div', { cls: 'note' }, [h('b', { text: t.note }), h('p', { cls: 'text-block', text: String(note) })]));

    var desc = [fields.description_short, fields.description_full].filter(function (x) { return x && String(x).trim(); });
    if (desc.length) {
      nodes.push(h('section', { cls: 'group' }, [h('h2', { text: t.groups.description })].concat(desc.map(function (d) {
        return h('p', { cls: 'text-block', text: String(d) });
      }))));
    }

    // Значения по сущностям: объект, продажа, аренда (публичные и открытые риелтором).
    var sale = offers.filter(function (o) { return o.kind === 'sale'; })[0];
    var rent = offers.filter(function (o) { return o.kind === 'rent'; })[0];
    function offerValues(o) {
      if (!o) return {};
      var v = {};
      [o.attrs, o.revealed].forEach(function (src) { for (var k in (src || {})) v[k] = src[k]; });
      if (o.rent_type) v.rent_type = o.rent_type;
      return v;
    }
    var values = { property: {}, offer_sale: offerValues(sale), offer_rent: offerValues(rent) };
    [fields, p.revealed || {}].forEach(function (src) { for (var k in src) values.property[k] = src[k]; });
    var rentCtx = rent ? c : null;
    reg.groups.forEach(function (g) {
      var name = g[0], keys = g[1];
      if (name === 'sale_terms' && !sale) return;
      if (name === 'rent_terms' && !rent) return;
      var rows = rowsFor(name === 'rent_terms' && rentCtx ? rentCtx : c, keys, values);
      if (!rows.length) return;
      nodes.push(h('section', { cls: 'group' }, [h('h2', { text: t.groups[name] || name }), h('ul', { cls: 'rows' }, rows)]));
    });

    var area = p.area;
    if (area && (typeof area.approx_lat === 'number' || typeof area.lat === 'number')) {
      var mapBox = h('div', { cls: 'map', id: 'map', role: 'img', 'aria-label': t.place });
      nodes.push(h('section', { cls: 'group' }, [h('h2', { text: t.place }), mapBox,
        area.exact ? null : h('p', { cls: 'small', text: t.approx })]));
      setTimeout(function () { drawMap(mapBox, area); }, 0);
    }
    var checked = p.actuality_checked_at ? fill(t.checked, dateText(s.lang, p.actuality_checked_at))
      : (p.updated_at ? fill(t.updated, dateText(s.lang, p.updated_at)) : null);
    if (checked) nodes.push(h('p', { cls: 'small', text: checked }));
    nodes.push(actNode(t));
    setContent(nodes);
    showCta(s, true);
    lastRender = Date.now();
  }
  var leaflet = null;
  function drawMap(box, area) {
    var lat = typeof area.lat === 'number' ? area.lat : area.approx_lat;
    var lng = typeof area.lng === 'number' ? area.lng : area.approx_lng;
    if (!leaflet) {
      leaflet = new Promise(function (resolve, reject) {
        var css = document.createElement('link');
        css.rel = 'stylesheet';
        css.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css';
        document.head.appendChild(css);
        var js = document.createElement('script');
        js.src = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js';
        js.onload = function () { resolve(window.L); };
        js.onerror = reject;
        document.head.appendChild(js);
      });
    }
    leaflet.then(function (L) {
      if (!document.body.contains(box)) return;
      var map = L.map(box, { scrollWheelZoom: false, dragging: !L.Browser.mobile, tap: false });
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      }).addTo(map);
      if (area.exact) {
        L.marker([lat, lng]).addTo(map);
        map.setView([lat, lng], 16);
      } else {
        var circle = L.circle([lat, lng], { radius: area.radius_m || 300, color: '#4A7640', fillColor: '#77B75F', fillOpacity: 0.25 }).addTo(map);
        map.fitBounds(circle.getBounds(), { padding: [16, 16] });
      }
    }, function () { box.hidden = true; });
  }

  // ---------- кнопка приложения, языки, ошибки ----------
  function showCta(s, on) {
    cta.hidden = !on;
    openBtn.textContent = ui(s.lang).open;
    openBtn.href = 'easyestate://selection?t=' + encodeURIComponent(s.t);
  }
  function drawChrome(s) {
    var t = ui(s.lang);
    document.documentElement.lang = s.lang === 'uz' ? 'uz-Latn' : s.lang;
    document.title = t.title + ' · EASY ESTATE';
    var nav = document.getElementById('langs');
    nav.textContent = '';
    LANGS.forEach(function (code) {
      nav.appendChild(h('a', {
        href: s.t ? hashOf({ t: s.t, lang: code, pid: s.pid, cur: s.cur, tol: s.tol }) : '#lang=' + code,
        'aria-current': code === s.lang ? 'true' : 'false', lang: code,
        text: code.toUpperCase()
      }));
    });
    var foot = document.getElementById('foot');
    foot.textContent = '';
    foot.appendChild(h('a', { href: '/?lang=' + (s.lang === 'id' ? 'en' : s.lang), text: t.foot }));
    foot.appendChild(document.createTextNode(' · '));
    foot.appendChild(h('a', { href: '/privacy.html', text: 'Privacy' }));
  }
  function showError(s, err) {
    var t = ui(s.lang);
    clearTimeout(retryTimer);
    if (err.code === 'unavailable' && s.pid) {
      setContent([h('a', { cls: 'back', href: hashOf({ t: s.t, lang: s.lang, cur: s.cur, tol: s.tol }), text: '← ' + t.back }), stateBox(null, t.gone)]);
      showCta(s, true);
      return;
    }
    if (err.code === 'unavailable') {
      listCache = null;
      setContent([stateBox(t.expired, t.install)]);
      showCta(s, false);
      return;
    }
    if (err.code === 'tolerance_not_allowed' && s.tol) { go({ tol: 0 }); return; }
    if (err.code === 'invalid') { setContent([stateBox(t.bad)]); showCta(s, false); return; }
    if (err.code === 'rate_limited') {
      var left = Math.min(Math.max(err.retry || 10, 1), 120);
      var p = h('p', { text: fill(t.busy, left) });
      setContent([h('div', { cls: 'state' }, [p])]);
      var tick = function () {
        left -= 1;
        if (left <= 0) { route(); return; }
        p.textContent = fill(t.busy, left);
        retryTimer = setTimeout(tick, 1000);
      };
      retryTimer = setTimeout(tick, 1000);
      return;
    }
    var btn = h('button', { cls: 'btn', type: 'button', text: t.retry, onclick: function () { route(); } });
    setContent([stateBox(null, t.error, btn)]);
  }
  function route() {
    clearTimeout(retryTimer);
    var s = params();
    drawChrome(s);
    if (!TOKEN_RE.test(s.t)) {
      setContent([stateBox(ui(s.lang).bad)]);
      showCta(s, false);
      return;
    }
    var job = s.pid ? renderProperty(s) : renderList(s);
    job.catch(function (err) { showError(s, err || {}); });
  }

  window.addEventListener('hashchange', route);
  document.addEventListener('visibilitychange', function () {
    // Ссылки на фото живут час: открытая дольше страница перезапрашивает данные.
    if (document.visibilityState === 'visible' && lastRender && Date.now() - lastRender > STALE_MS) {
      listCache = null;
      route();
    }
  });
  route();
})();
