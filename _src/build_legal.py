"""Собирает узбекские статьи (латиница и кириллица) в privacy.html и terms.html.

Русская и английская статьи в этих файлах правятся вручную; узбекские
перестраиваются из _src/legal_uz.py при каждом запуске:
    python3 _src/build_legal.py
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import legal_uz  # noqa: E402
import uz  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent

NAV = ('<nav class="langs" aria-label="Language"><a href="?lang=ru" data-l="ru">Русский</a>'
       '<a href="?lang=uz" data-l="uz" lang="uz-Latn">Oʻzbekcha</a>'
       '<a href="?lang=uz-cyrl" data-l="uz-cyrl" lang="uz-Cyrl">Ўзбекча</a>'
       '<a href="?lang=en" data-l="en">English</a></nav>')

SCRIPT = """  <script>
    (function () {
      // Язык: ?lang=ru|uz|uz-cyrl|en; иначе язык браузера. uz-Cyrl* — кириллица, uz* — латиница;
      // kk, ky, tg, be — русский; остальные — английский. Без скрипта видны все версии.
      var q = (new URLSearchParams(window.location.search).get('lang') || navigator.language || '').toLowerCase();
      var lang = q.indexOf('uz') === 0 ? (q.indexOf('cyrl') >= 0 ? 'uz-cyrl' : 'uz')
        : ['ru', 'kk', 'ky', 'tg', 'be'].indexOf(q.slice(0, 2)) >= 0 ? 'ru' : 'en';
      var attr = { 'uz': 'uz-Latn', 'uz-cyrl': 'uz-Cyrl' };
      document.documentElement.lang = attr[lang] || lang;
      var arts = document.querySelectorAll('article[data-lang]');
      for (var i = 0; i < arts.length; i++) { arts[i].hidden = arts[i].getAttribute('data-lang') !== lang; }
      var links = document.querySelectorAll('.langs a');
      for (var j = 0; j < links.length; j++) { if (links[j].getAttribute('data-l') === lang) links[j].setAttribute('aria-current', 'true'); }
      var t = document.querySelector('article[data-lang="' + lang + '"] h1');
      if (t) document.title = 'EASY ESTATE - ' + t.textContent;
    })();
  </script>"""


def article(code, inner):
    attr = "uz-Latn" if code == "uz" else "uz-Cyrl"
    return f'    <article lang="{attr}" data-lang="{code}">\n{inner}\n    </article>'


def build(name, inner_uz):
    path = ROOT / name
    s = path.read_text(encoding="utf-8")
    # Прежние узбекские статьи — убрать (сборка повторяемая).
    s = re.sub(r'\s*<article lang="uz-(Latn|Cyrl)" data-lang="uz(-cyrl)?">.*?</article>', "", s, flags=re.S)
    # Лишний закрывающий тег после английской статьи (была ошибка разметки).
    s = re.sub(r'(<article lang="en" data-lang="en">.*?</article>)\s*</article>', r"\1", s, flags=re.S)
    cyrl = uz.to_cyrl_html(inner_uz).replace("?lang=uz", "?lang=uz-cyrl")
    block = article("uz", inner_uz) + "\n" + article("uz-cyrl", cyrl)
    s = re.sub(r'(<article lang="en" data-lang="en">.*?</article>)', lambda m: m.group(1) + "\n" + block, s, count=1, flags=re.S)
    s = re.sub(r'<nav class="langs" aria-label="Language">.*?</nav>', NAV, s, count=1, flags=re.S)
    s = re.sub(r"  <script>.*?</script>", lambda m: SCRIPT, s, count=1, flags=re.S)
    path.write_text(s, encoding="utf-8")
    print(name, len(s))


build("privacy.html", legal_uz.PRIVACY_UZ)
build("terms.html", legal_uz.TERMS_UZ)
