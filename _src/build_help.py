#!/usr/bin/env python3
"""Справка на сайте: статьи публичной базы знаний приложения (docs/kb/public) как страницы /help/.

Источник истины — база знаний в репозитории приложения; страницы пересобираются после её изменения.
Запуск: python3 _src/build_help.py <путь к копии EASY-ESTATE>, затем python3 _src/build_site.py (карта сайта).
Пока статьи только на русском (как база знаний); переводы — отдельной задачей.
"""
import html
import json
import pathlib
import re
import sys

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://easyestate.solutions/"
KB = pathlib.Path(sys.argv[1]) / "docs" / "kb" / "public"

# Порядок статей в оглавлении; assistant-scope.md — служебная статья для помощника, на сайт не идёт.
ORDER = [
    "about", "for-realtors", "for-clients", "getting-started",
    "how-properties", "how-voice-fill", "how-ai-description", "how-clients", "how-requests",
    "how-invite-client", "how-client-selections", "how-client-view", "how-show-to-client",
    "how-privacy", "how-currency", "how-home-tasks", "how-offline-sync", "reminders-phones",
    "faq", "responsibility",
]
SKIP = {"assistant-scope"}

e = html.escape
CSS = (ROOT / "_src" / "site.css").read_text(encoding="utf-8")
LOGO = (ROOT / "assets" / "logo-mark.svg").read_text(encoding="utf-8").split("?>", 1)[-1].strip()
LOGO = LOGO.replace('role="img" aria-label="EASY ESTATE logo mark"', 'aria-hidden="true" focusable="false"')
LOGO = LOGO.replace("<title>EASY ESTATE logo mark</title>", "")
LOGO = LOGO.split("<desc>")[0] + LOGO.split("</desc>")[1]
OG_IMAGE = SITE + "assets/og-easyestate-2.jpg"

HELP_CSS = """
.site-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding-block: 14px; border-bottom: 1px solid var(--line); }
.help-nav { display: flex; gap: 20px; font-size: 15px; }
.help-nav a { color: var(--fg); text-decoration: none; }
.help { padding-inline: max(16px, calc((100% - 760px) / 2)); padding-block: 40px 64px; display: flex; flex-direction: column; gap: 16px; }
.help h1 { font-size: clamp(28px, 4.6vw, 40px); line-height: 1.15; max-width: none; }
.help h2 { font-size: 22px; margin-top: 16px; max-width: none; }
.help h3 { font-size: 18px; margin-top: 8px; }
.help p, .help li { max-width: 42em; line-height: 1.6; }
.help ol, .help ul { padding-left: 22px; display: flex; flex-direction: column; gap: 6px; }
.help ol { list-style: decimal; }
.help ul { list-style: disc; }
.help .crumbs { font-size: 14px; color: var(--muted); }
.help .crumbs a { color: var(--muted); }
.help-list { list-style: none !important; padding-left: 0 !important; gap: 14px !important; }
.help-list a { font-weight: 600; font-size: 17px; }
.help-list p { color: var(--muted); margin-top: 2px; font-size: 15px; }
"""


def read(slug):
    """Заголовок из frontmatter и тело статьи без frontmatter и без первого заголовка H1."""
    text = (KB / f"{slug}.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    meta = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    body = text[m.end():].lstrip()
    body = re.sub(r"^# .*\n", "", body, count=1)
    return meta["title"].strip(), body


def lead_of(body):
    """Первый абзац статьи — описание страницы и строка в оглавлении (до 200 знаков)."""
    for block in body.split("\n\n"):
        b = block.strip()
        if b and not b.startswith(("#", "1.", "-", "|", "**")):
            b = re.sub(r"[*_`]", "", b).replace("\n", " ")
            return b if len(b) <= 200 else b[:197].rsplit(" ", 1)[0] + "…"
    return ""


def page(title, desc, url, content, ld):
    return f'''<!DOCTYPE html>
<html lang="ru" data-lang-fixed="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:site_name" content="EASY ESTATE">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="ru_RU">
<meta property="og:image" content="{OG_IMAGE}">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{url}">
<link rel="icon" href="/assets/logo-mark.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{CSS}{HELP_CSS}</style>
</head>
<body>
<header class="site-head">
  <a class="brand" href="/ru/" aria-label="EASY ESTATE">{LOGO}<span>EASY ESTATE</span></a>
  <nav class="help-nav" aria-label="Справка"><a href="/help/">Справка</a><a href="/support.html?lang=ru">Поддержка</a></nav>
</header>
<main class="help">{content}</main>
<footer class="foot"><p>ООО «EASY ESTATE», ИНН 307553192, Ташкент, Узбекистан</p>
<p class="foot-links"><a href="/ru/">Главная</a><a href="/privacy.html?lang=ru">Политика конфиденциальности</a><a href="/terms.html?lang=ru">Условия использования</a></p></footer>
</body>
</html>
'''


def crumbs(title=None):
    tail = f' / <span>{e(title)}</span>' if title else ""
    return f'<p class="crumbs"><a href="/ru/">EASY ESTATE</a> / <a href="/help/">Справка</a>{tail}</p>'


def main():
    slugs = [s for s in ORDER if (KB / f"{s}.md").exists()]
    extra = sorted(p.stem for p in KB.glob("*.md") if p.stem not in ORDER and p.stem not in SKIP)
    slugs += extra  # новая статья базы знаний попадает в справку сама, в конец оглавления
    out = ROOT / "help"
    out.mkdir(exist_ok=True)
    for old in out.glob("*.html"):
        old.unlink()
    items = []
    for slug in slugs:
        title, body = read(slug)
        url = f"{SITE}help/{slug}"  # без .html: Cloudflare Pages переадресует .html на адрес без расширения
        desc = lead_of(body) or title
        html_body = markdown.markdown(body, extensions=["sane_lists"])
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": title, "inLanguage": "ru",
              "url": url, "publisher": {"@type": "Organization", "name": "EASY ESTATE", "url": SITE}}
        content = f"{crumbs(title)}<h1>{e(title)}</h1>{html_body}"
        (out / f"{slug}.html").write_text(page(f"{title} - EASY ESTATE", desc, url, content, ld), encoding="utf-8")
        items.append((slug, title, desc))
        print("help", slug)
    lst = "".join(f'<li><a href="/help/{s}">{e(t)}</a><p>{e(d)}</p></li>' for s, t, d in items)
    content = (f'{crumbs()}<h1>Справка EASY ESTATE</h1>'
               f'<p>Как работает приложение для риелторов и их клиентов: объекты, клиенты, голосовое заполнение, '
               f'подборки, приватность. Приложение в закрытом тестировании.</p><ul class="help-list">{lst}</ul>')
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Справка EASY ESTATE",
          "inLanguage": "ru", "url": SITE + "help/"}
    (out / "index.html").write_text(
        page("Справка - EASY ESTATE", "Как работает приложение EASY ESTATE для риелторов и их клиентов.",
             SITE + "help/", content, ld), encoding="utf-8")
    print("help index", len(items))


main()
