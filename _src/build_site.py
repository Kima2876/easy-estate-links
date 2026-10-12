#!/usr/bin/env python3
"""Сборка главной easyestate.solutions (RU/EN в одном файле, как privacy.html).

Выход: index.html в корне репозитория (полный документ)
и _src/preview.html (фрагмент для артефакта claude.ai: без doctype/html/head/body).
Запуск: python3 _src/build_site.py
"""
import html
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGO = (ROOT / "assets" / "logo-mark.svg").read_text(encoding="utf-8")
LOGO = LOGO.split("?>", 1)[-1].strip()
LOGO = LOGO.replace('role="img" aria-label="EASY ESTATE logo mark"', 'aria-hidden="true" focusable="false"')
LOGO = LOGO.replace("<title>EASY ESTATE logo mark</title>", "")
LOGO = LOGO.split("<desc>")[0] + LOGO.split("</desc>")[1]

EMAIL = "admin@easyestate.solutions"
LOCK = '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" focusable="false"><path fill="currentColor" d="M5 7V5a3 3 0 0 1 6 0v2h1a1 1 0 0 1 1 1v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1h1zm1.5 0h3V5a1.5 1.5 0 0 0-3 0v2z"/></svg>'

T = {
    "ru": {
        "nav": [("how", "Как работает"), ("client", "Клиенту"), ("price", "Цены"), ("contact", "Контакты")],
        "status": "Закрытое тестирование · Android",
        "h1": "Личный рабочий инструмент риелтора",
        "lead": "Меньше операционки при большем KPI. Объекты, клиенты и подборки в одном приложении, и база всегда принадлежит вам.",
        "cta": "Связаться",
        "cta2": "Как это работает",
        "hero_note": "Настоящие экраны приложения, демо-данные: Ташкент",
        "hero_alt": ["Главная риелтора: дела на сегодня и база", "Карточка объекта с ценой и характеристиками"],
        "p_eyebrow": "Проблема",
        "p_h": "Риелтор тратит день на телефон, а не на сделки",
        "p_big": "до 80%",
        "p_big_txt": "рабочего времени уходит на звонки и переписку вместо работы с объектами и клиентами",
        "p_src": "Оценка основателя по опыту рынка",
        "p_items": [
            ("Объявление", "Клиент звонит, и всё уточняется заново"),
            ("Мессенджеры", "Варианты и голосовые вперемешку"),
            ("Путаница", "Что к какому объекту, непонятно обоим"),
            ("Объект уже продан", "Или был приманкой для сбора контактов"),
        ],
        "s_eyebrow": "Как работает",
        "s_h": "Риелтор говорит, клиент выбирает",
        "steps": [
            ("Голос на объекте", "Наговорите объект прямо на месте. ИИ разложит сказанное по полям, даже без сети, и покажет, что понял.", "01_voice", "Экран «Вот что я понял»: голос разложен по полям"),
            ("Приватное под замком", "Цена собственника, комиссия и контакты видны только вам. Сервер не отдаёт их клиенту.", "02_private", "Блок «Только для вас» в карточке объекта", "Клиент этого не видит"),
            ("Клиент ставит звёзды", "Клиент смотрит ваши объекты в своём приложении и оценивает их. Вы видите, что понравилось.", "03_client_list", "Приложение клиента: объекты риелтора с оценками"),
        ],
        "c_eyebrow": "Клиенту витрина, риелтору порядок",
        "c_h": "Всё, что обычно теряется в переписке",
        "c_items": [
            ("Звёзды 1-5 и «Скрыть»", "Клиент оценивает объекты без переписки"),
            ("Цена в валюте клиента", "Пересчёт по курсу автоматически"),
            ("22 языка", "У риелтора и клиента свой язык интерфейса"),
            ("Работает без сети", "Всё отправится, когда появится связь"),
        ],
        "c_soon_label": "Скоро",
        "c_soon": "Подборки по ссылке, запись на показ и чат по объекту",
        "c_tags": ["Клиент", "Риелтор"],
        "c_alts": ["Карточка объекта у клиента с оценкой звёздами", "Список объектов риелтора с фильтрами"],
        "b_eyebrow": "Главное отличие",
        "b_h": "База принадлежит риелтору",
        "b_items": [
            ("Ваша база", "Перешли в другое агентство, и база ушла вместе с вами. Выгрузка своей базы будет доступна до платного запуска."),
            ("Закрытые поля", "Цена собственника, комиссия и контакты закрыты на сервере, а не просто спрятаны на экране."),
            ("Полный цикл", "Объект, клиент, подборка, оценки и показ в одном месте, без таблиц и заметок в мессенджере."),
        ],
        "pr_eyebrow": "Цены",
        "pr_h": "Одна подписка, без уровней",
        "pr_note": "Сейчас приложение в закрытом тестировании и бесплатно для тестировщиков. Цены начнут действовать после выхода в Google Play и App Store.",
        "pr_cards": [
            ("Пробный период", "0", "", "Все функции, чтобы попробовать приложение в работе"),
            ("Месяц", "10", "в месяц", "Голосовое заполнение объектов с ИИ входит в подписку"),
            ("Год", "100", "в год", "Выгоднее помесячной оплаты на $20, это два месяца"),
        ],
        "pr_free": "Клиентам риелтора приложение бесплатно всегда.",
        "pr_tax": "Цены указаны без налога страны покупателя.",
        "ct_eyebrow": "Контакты",
        "ct_h": "Хотите попробовать или задать вопрос?",
        "ct_p": "Напишите нам. Риелторов из Узбекистана, ОАЭ, Таиланда и Индонезии приглашаем в тестирование в первую очередь.",
        "copy": "Скопировать адрес",
        "copied": "Адрес скопирован",
        "f_company": "ООО «EASY ESTATE», ИНН 307553192, Ташкент, Узбекистан",
        "f_links": [("privacy.html?lang=ru", "Политика конфиденциальности"), ("terms.html?lang=ru", "Условия использования")],
        "f_demo": "Экраны на сайте настоящие, данные демонстрационные.",
    },
    "en": {
        "nav": [("how", "How it works"), ("client", "For clients"), ("price", "Pricing"), ("contact", "Contact")],
        "status": "Closed beta · Android",
        "h1": "A personal work tool for real estate agents",
        "lead": "Less routine, higher KPI. Properties, clients and selections in one app, and the base always belongs to you.",
        "cta": "Get in touch",
        "cta2": "See how it works",
        "hero_note": "Real app screens, demo data: Tashkent",
        "hero_alt": ["Agent home screen: today's tasks and the base", "Property card with price and details"],
        "p_eyebrow": "Problem",
        "p_h": "Agents spend the day on the phone, not on deals",
        "p_big": "up to 80%",
        "p_big_txt": "of working time goes to calls and chats instead of properties and clients",
        "p_src": "Founder's estimate based on market experience",
        "p_items": [
            ("Listing", "A client calls and everything is clarified from scratch"),
            ("Messengers", "Options and voice notes all mixed up"),
            ("Confusion", "Neither side knows what refers to which property"),
            ("Already sold", "Or it was bait to collect contacts"),
        ],
        "s_eyebrow": "How it works",
        "s_h": "The agent speaks, the client chooses",
        "steps": [
            ("Voice at the property", "Dictate the property on site. AI sorts what you said into fields, even offline, and shows what it understood.", "en_01_voice", "Here is what I understood: voice sorted into fields"),
            ("Private stays private", "The owner's price, commission and contacts are visible only to you. The server never sends them to the client.", "en_02_private", "Only for you block in the property card", "Hidden from the client"),
            ("The client rates with stars", "The client browses your properties in their own app and rates them. You see what they liked.", "en_03_client_list", "Client app: the agent's properties with ratings"),
        ],
        "c_eyebrow": "A showcase for the client, order for the agent",
        "c_h": "Everything that usually gets lost in chats",
        "c_items": [
            ("1-5 stars and “Hide”", "The client rates properties without any chat"),
            ("Price in the client's currency", "Converted at the current rate automatically"),
            ("22 languages", "The agent and the client each use their own"),
            ("Works offline", "Everything syncs once the connection returns"),
        ],
        "c_soon_label": "Coming soon",
        "c_soon": "Selections by link, viewing booking and property chat",
        "c_tags": ["Client", "Agent"],
        "c_alts": ["Property card in the client app with star rating", "The agent's property list with filters"],
        "b_eyebrow": "The key difference",
        "b_h": "The base belongs to the agent",
        "b_items": [
            ("Your base", "Move to another agency and the base moves with you. Exporting your base will be available before the paid launch."),
            ("Locked fields", "The owner's price, commission and contacts are locked on the server, not just hidden on screen."),
            ("Full cycle", "Property, client, selection, ratings and viewing in one place, without spreadsheets and notes in messengers."),
        ],
        "pr_eyebrow": "Pricing",
        "pr_h": "One subscription, no tiers",
        "pr_note": "The app is in closed beta and free for testers. Prices apply after the launch on Google Play and the App Store.",
        "pr_cards": [
            ("Free trial", "0", "", "Every feature, so you can try the app at work"),
            ("Monthly", "10", "per month", "AI voice filling of properties is included"),
            ("Yearly", "100", "per year", "$20 less than paying monthly, that is two months"),
        ],
        "pr_free": "The app is always free for the agent's clients.",
        "pr_tax": "Prices exclude the buyer's local tax.",
        "ct_eyebrow": "Contact",
        "ct_h": "Want to try it or ask a question?",
        "ct_p": "Write to us. Agents from Uzbekistan, the UAE, Thailand and Indonesia are first in line for the beta.",
        "copy": "Copy address",
        "copied": "Address copied",
        "f_company": "EASY ESTATE LLC, Taxpayer ID 307553192, Tashkent, Uzbekistan",
        "f_links": [("privacy.html?lang=en", "Privacy Policy"), ("terms.html?lang=en", "Terms of Use")],
        "f_demo": "The screens on this site are real; the data is demo.",
    },
}

e = html.escape


def phone(src, alt, cls="", eager=False):
    load = "eager" if eager else "lazy"
    return (f'<figure class="phone {cls}"><img src="assets/screens/{src}.webp" alt="{e(alt)}" '
            f'width="600" height="1304" loading="{load}" decoding="async"></figure>')


def block(lang):
    t = T[lang]
    hero_imgs = ("05_home", "07_property_card") if lang == "ru" else ("en_05_home", "en_07_property_card")
    c_imgs = ("04_client_card", "06_properties") if lang == "ru" else ("en_04_client_card", "en_06_properties")
    p_items = "".join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in t["p_items"])
    steps = []
    for i, s in enumerate(t["steps"], 1):
        pill = f'<span class="lockpill">{LOCK}{e(s[4])}</span>' if len(s) > 4 else ""
        steps.append(
            f'<li class="step"><div class="step-text"><span class="num" aria-hidden="true">{i}</span>'
            f'<h3>{e(s[0])}</h3><p>{e(s[1])}</p></div>'
            f'<div class="step-shot">{phone(s[2], s[3])}{pill}</div></li>')
    c_items = "".join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in t["c_items"])
    b_items = "".join(f'<li><h3>{e(a)}</h3><p>{e(b)}</p></li>' for a, b in t["b_items"])
    cards = []
    for i, (name, amount, per, note) in enumerate(t["pr_cards"]):
        feat = " price-card--main" if i == 2 else ""
        per_html = f'<span class="per">{e(per)}</span>' if per else ""
        cards.append(
            f'<li class="price-card{feat}"><h3>{e(name)}</h3>'
            f'<p class="amount"><span class="cur">$</span>{amount}{per_html}</p><p>{e(note)}</p></li>')
    nav = "".join(f'<a href="#{a}-{lang}">{e(b)}</a>' for a, b in t["nav"])
    flinks = "".join(f'<a href="{h}">{e(x)}</a>' for h, x in t["f_links"])
    return f'''
<div class="lang-block" data-lang="{lang}" lang="{lang}">
  <nav class="topnav" aria-label="{'Разделы' if lang == 'ru' else 'Sections'}">{nav}</nav>
  <section class="hero">
    <div class="hero-text">
      <p class="status"><span class="dot" aria-hidden="true"></span>{e(t["status"])}</p>
      <h1>{e(t["h1"])}</h1>
      <p class="lead">{e(t["lead"])}</p>
      <div class="actions"><a class="btn" href="#contact-{lang}">{e(t["cta"])}</a><a class="btn btn--ghost" href="#how-{lang}">{e(t["cta2"])}</a></div>
    </div>
    <div class="hero-shots">
      {phone(hero_imgs[0], t["hero_alt"][0], "back", True)}
      {phone(hero_imgs[1], t["hero_alt"][1], "front", True)}
      <p class="shots-note">{e(t["hero_note"])}</p>
    </div>
  </section>

  <section class="problem">
    <p class="eyebrow">{e(t["p_eyebrow"])}</p>
    <h2>{e(t["p_h"])}</h2>
    <div class="problem-grid">
      <div class="big"><p class="big-num">{e(t["p_big"])}</p><p class="big-txt">{e(t["p_big_txt"])}</p><p class="src">{e(t["p_src"])}</p></div>
      <ul class="rows">{p_items}</ul>
    </div>
  </section>

  <section class="how" id="how-{lang}">
    <p class="eyebrow">{e(t["s_eyebrow"])}</p>
    <h2>{e(t["s_h"])}</h2>
    <ol class="steps">{"".join(steps)}</ol>
  </section>

  <section class="client" id="client-{lang}">
    <div class="client-text">
      <p class="eyebrow">{e(t["c_eyebrow"])}</p>
      <h2>{e(t["c_h"])}</h2>
      <ul class="rows">{c_items}</ul>
      <p class="soon"><span class="chip">{e(t["c_soon_label"])}</span>{e(t["c_soon"])}</p>
    </div>
    <div class="client-shots">
      <div class="tagged"><span class="tag">{e(t["c_tags"][0])}</span>{phone(c_imgs[0], t["c_alts"][0])}</div>
      <div class="tagged"><span class="tag">{e(t["c_tags"][1])}</span>{phone(c_imgs[1], t["c_alts"][1])}</div>
    </div>
  </section>

  <section class="band">
    <p class="eyebrow">{e(t["b_eyebrow"])}</p>
    <h2>{e(t["b_h"])}</h2>
    <ul class="pillars">{b_items}</ul>
  </section>

  <section class="price" id="price-{lang}">
    <p class="eyebrow">{e(t["pr_eyebrow"])}</p>
    <h2>{e(t["pr_h"])}</h2>
    <p class="note">{e(t["pr_note"])}</p>
    <ul class="price-grid">{"".join(cards)}</ul>
    <p class="small">{e(t["pr_free"])} {e(t["pr_tax"])}</p>
  </section>

  <section class="contact" id="contact-{lang}">
    <p class="eyebrow">{e(t["ct_eyebrow"])}</p>
    <h2>{e(t["ct_h"])}</h2>
    <p>{e(t["ct_p"])}</p>
    <div class="mail"><a class="mail-addr" href="mailto:{EMAIL}">{EMAIL}</a>
      <button type="button" class="btn btn--ghost copy" id="copy-{lang}" data-copied="{e(t["copied"])}">{e(t["copy"])}</button>
      <span class="copy-status" role="status" aria-live="polite"></span></div>
  </section>

  <footer class="foot">
    <p>{e(t["f_company"])}</p>
    <p class="foot-links">{flinks}</p>
    <p class="small">{e(t["f_demo"])}</p>
  </footer>
</div>'''


CSS = (pathlib.Path(__file__).parent / "site.css").read_text(encoding="utf-8")
JS = (pathlib.Path(__file__).parent / "site.js").read_text(encoding="utf-8")

HEADER = f'''<header class="site-head">
  <a class="brand" href="./" aria-label="EASY ESTATE">{LOGO}<span>EASY ESTATE</span></a>
  <div class="langs" role="group" aria-label="Language / Язык">
    <a href="?lang=ru" data-l="ru">RU</a><a href="?lang=en" data-l="en">EN</a>
  </div>
</header>'''

BODY = f'''<div class="page">
{HEADER}
<main>{block("ru")}{block("en")}</main>
</div>
<script>{JS}</script>'''

TITLE = "EASY ESTATE"
DESC = "Личный рабочий инструмент риелтора: объекты, клиенты и подборки в одном приложении. A personal work tool for real estate agents."

HEAD_META = f'''<title>{TITLE}</title>
<meta name="description" content="{e(DESC)}">
<meta property="og:title" content="EASY ESTATE">
<meta property="og:description" content="{e(DESC)}">
<meta property="og:type" content="website">
<link rel="icon" href="assets/logo-mark.svg" type="image/svg+xml">'''

full = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{HEAD_META}
<style>{CSS}</style>
</head>
<body>
{BODY}
</body>
</html>
'''
(ROOT / "index.html").write_text(full, encoding="utf-8")
preview = f'''<title>{TITLE}</title>
<style>{CSS}</style>
{BODY}
'''
(ROOT / "_src" / "preview.html").write_text(preview, encoding="utf-8")
print("ok", len(full), len(preview))
