"""Узбекский язык сайта: тексты на латинице (основа) и перевод в кириллицу.

Кириллица строится из латиницы функцией to_cyrl() по официальному соответствию
алфавитов 1995 года; заимствования с иным написанием — в словаре WORDS.
Названия марок, адреса почты и ссылки не переводятся (PROTECT).
"""
import re

# ---------------------------------------------------------------------------
# Тексты главной (те же ключи, что у T["ru"] и T["en"] в build_site.py).
# Апостроф в oʻ, gʻ — U+02BB; тутук белгиси (ʼ) — U+02BC.
# ---------------------------------------------------------------------------

T_UZ = {
    "nav": [("how", "Qanday ishlaydi"), ("client", "Mijozlar uchun"), ("price", "Narxlar"), ("contact", "Aloqa")],
    "status": "Yopiq sinov · Android",
    "h1": "Rieltorning shaxsiy yordamchisi",
    "lead": "Koʻchmas mulk agentining professional ish vositasi: obyektlar, mijozlar va tanlovlar bitta ilovada. Kamroq kundalik ish, yuqoriroq KPI, baza esa doim sizniki.",
    "cta": "Bogʻlanish",
    "cta2": "Qanday ishlashini koʻrish",
    "hero_note": "Ilovaning haqiqiy ekranlari (rus tilidagi interfeys), demo maʼlumotlar: Toshkent",
    "hero_alt": ["Rieltor bosh sahifasi: bugungi ishlar va baza", "Obyekt kartochkasi: narx va tavsif"],
    "p_eyebrow": "Muammo",
    "p_h": "Rieltor kunini bitimlarga emas, telefonga sarflaydi",
    "p_big": "80% gacha",
    "p_big_txt": "ish vaqti obyektlar va mijozlar bilan ishlash oʻrniga qoʻngʻiroqlar va yozishmalarga ketadi",
    "p_src": "Asoschining bozor tajribasiga asoslangan bahosi",
    "p_items": [
        ("Eʼlon", "Mijoz qoʻngʻiroq qiladi va hammasi qaytadan aniqlanadi"),
        ("Messenjerlar", "Variantlar va ovozli xabarlar aralash-quralash"),
        ("Chalkashlik", "Qaysi gap qaysi obyektga tegishli, ikki tomonga ham tushunarsiz"),
        ("Obyekt allaqachon sotilgan", "Yoki kontaktlarni yigʻish uchun qoʻyilgan aldov eʼlon edi"),
    ],
    "s_eyebrow": "Qanday ishlaydi",
    "s_h": "Rieltor gapiradi, mijoz tanlaydi",
    "steps": [
        ("Obyektda ovoz bilan", "Obyekt haqida joyida gapirib bering. SI aytganlaringizni maydonlarga ajratadi, internetsiz ham, va nimani tushunganini koʻrsatadi.", "01_voice", "«Mana nimani tushundim» ekrani: ovoz maydonlarga ajratilgan"),
        ("Maxfiy maʼlumotlar himoyada", "Mulkdor narxi, komissiya va kontaktlar faqat sizga koʻrinadi. Server ularni mijozga bermaydi.", "02_private", "Obyekt kartochkasidagi «Faqat siz uchun» bloki", "Mijoz buni koʻrmaydi"),
        ("Mijoz yulduzcha qoʻyadi", "Mijoz obyektlaringizni oʻz ilovasida koʻradi va baholaydi. Siz unga nima yoqqanini koʻrasiz.", "03_client_list", "Mijoz ilovasi: rieltor obyektlari va baholar"),
    ],
    "c_eyebrow": "Mijozga vitrina, rieltorga tartib",
    "c_h": "Odatda yozishmalarda yoʻqoladigan hamma narsa",
    "c_items": [
        ("1-5 yulduz va «Yashirish»", "Mijoz obyektlarni yozishmasiz baholaydi"),
        ("Narx mijoz valyutasida", "Kurs boʻyicha avtomatik qayta hisoblanadi"),
        ("22 til", "Rieltor va mijoz interfeysni oʻz tilida koʻradi"),
        ("Internetsiz ishlaydi", "Aloqa paydo boʻlganda hammasi yuboriladi"),
    ],
    "c_soon_label": "Tez orada",
    "c_soon": "Havola orqali tanlovlar, koʻrishga yozilish va obyekt boʻyicha chat",
    "c_tags": ["Mijoz", "Rieltor"],
    "c_alts": ["Mijozdagi obyekt kartochkasi va yulduzcha bahosi", "Rieltorning filtrli obyektlar roʻyxati"],
    "b_eyebrow": "Asosiy farq",
    "b_h": "Baza rieltorga tegishli",
    "b_items": [
        ("Sizning bazangiz", "Boshqa agentlikka oʻtdingiz, baza ham siz bilan ketadi. Oʻz bazangizni yuklab olish pullik ishga tushirishdan oldin paydo boʻladi."),
        ("Yopiq maydonlar", "Mulkdor narxi, komissiya va kontaktlar shunchaki ekranda yashirilmagan, serverda yopilgan."),
        ("Toʻliq sikl", "Obyekt, mijoz, tanlov, baholar va koʻrish bir joyda, jadval va messenjerdagi qaydlarsiz."),
    ],
    "pr_eyebrow": "Narxlar",
    "pr_h": "Bitta obuna, darajalarsiz",
    "pr_note": "Hozir ilova yopiq sinovda va sinovchilar uchun bepul. Narxlar ilova Google Play va App Store doʻkonlariga chiqqandan keyin amal qiladi.",
    "pr_cards": [
        ("Sinov muddati", "0", "", "Ilovani ishda sinab koʻrish uchun barcha funksiyalar"),
        ("Oylik", "10", "oyiga", "SI bilan obyektlarni ovozli toʻldirish obunaga kiradi"),
        ("Yillik", "100", "yiliga", "Oylik toʻlovdan $20 arzon, bu ikki oy"),
    ],
    "pr_free": "Rieltor mijozlari uchun ilova doim bepul.",
    "pr_tax": "Narxlar xaridor mamlakati soligʻisiz koʻrsatilgan.",
    "ct_eyebrow": "Aloqa",
    "ct_h": "Sinab koʻrmoqchimisiz yoki savolingiz bormi?",
    "ct_p": "Bizga yozing. Oʻzbekiston, BAA, Tailand va Indoneziyadagi rieltorlarni sinovga birinchi navbatda taklif qilamiz.",
    "copy": "Manzilni nusxalash",
    "copied": "Manzil nusxalandi",
    "f_company": "«EASY ESTATE» MChJ, STIR 307553192, Toshkent, Oʻzbekiston",
    # Политика и условия пока на ru/en — ссылка на русскую редакцию.
    "f_links": [("support.html?lang=uz", "Qoʻllab-quvvatlash"), ("privacy.html?lang=ru", "Maxfiylik siyosati"), ("terms.html?lang=ru", "Foydalanish shartlari"), ("delete-account.html?lang=uz", "Hisobni oʻchirish")],
    "f_demo": "Saytdagi ekranlar haqiqiy, maʼlumotlar demo.",
}

TITLE_UZ = "EASY ESTATE - rieltorning shaxsiy yordamchisi"

PAGE_TITLES_UZ = {
    "support": "Qoʻllab-quvvatlash",
    "delete-account": "Hisobni oʻchirish",
    "404": "Sahifa topilmadi",
}


def page_uz(slug, mail, L, bot, support_mail, privacy_mail):
    """HTML служебной страницы на узбекском (латиница); L — код языка для ссылок и кнопок."""
    if slug == "support":
        return f'''
<p class="lead">Ilova, sinov va hisobingiz haqidagi savollarga javob beramiz.</p>
<section><h2>Telegram</h2>
<p>EASY ESTATE qoʻllab-quvvatlash boti: unga savol yoki fikringizni yozing.</p>
<p><a class="btn" href="https://t.me/{bot}">@{bot}</a></p></section>
<section><h2>Elektron pochta</h2>{mail(support_mail, L)}</section>
<section><h2>Maʼlumotlar va hisob</h2>
<p>Shaxsiy maʼlumotlar boʻyicha savollar: {privacy_mail}. Hisobni qanday oʻchirish: <a href="delete-account.html?lang={L}">Hisobni oʻchirish</a>.</p></section>'''
    if slug == "delete-account":
        return f'''
<p class="lead">EASY ESTATE ilovasi, ishlab chiquvchi «EASY ESTATE» MChJ. Bu yerda hisobni va unga bogʻliq maʼlumotlarni qanday oʻchirish tushuntirilgan.</p>
<section><h2>Oʻchirishni qanday soʻrash mumkin</h2>
<ol class="doc-steps">
<li>Hisob roʻyxatdan oʻtgan pochtadan quyidagi manzilga xat yozing.</li>
<li>Mavzuda «Hisobni oʻchirish» deb yozing. Sababini tushuntirish shart emas.</li>
<li>Hisob va unga bogʻliq maʼlumotlarni 30 kun ichida oʻchiramiz va bu haqda javob xatida xabar beramiz.</li>
</ol>
{mail(privacy_mail, L)}
<p class="small">Ilovaning oʻzida oʻchirish ommaviy ishga tushirishdan oldin paydo boʻladi.</p></section>
<section><h2>Nima oʻchiriladi</h2>
<p>Hisob va anketa, rieltor bazasi (obyektlar, foto va videolar, mijozlar va mulkdorlar, soʻrovlar, vazifalar, hujjatlar), mijozning rieltor bilan bogʻlanishi, baholar va yashirilgan obyektlar, SI yordamchisi bilan yozishmalar.</p></section>
<section><h2>Nima qoladi va qancha muddat</h2>
<p>Rieltorning obyekt hujjatlari bilan amallari jurnali hujjat oʻchirilgandan keyin 3 yil saqlanadi. Texnik hodisalar hisobga bogʻlanmagan holda qoladi. SI yordamchisidan foydalanishning oylik anonim yakunlarida sizning maʼlumotlaringiz yoʻq.</p></section>
<section><h2>Agar siz rieltor mijozi boʻlsangiz</h2>
<p>Hisobingiz xuddi shunday oʻchiriladi. Rieltor oʻz bazasiga oʻzi kiritgan siz haqingizdagi maʼlumotlarni rieltor oʻchiradi; agar u javob bermasa, bizga yozing.</p></section>'''
    return '''
<p class="lead">Bunday sahifa yoʻq. Havola eskirgan boʻlishi mumkin.</p>
<p><a class="btn" href="/">Bosh sahifaga</a></p>'''


# ---------------------------------------------------------------------------
# Латиница → кириллица
# ---------------------------------------------------------------------------

# Заимствования, которые в кириллице пишутся не по правилам (основа слова, нижний регистр).
WORDS = {
    "obyekt": "объект",
    "sikl": "цикл",
    "funksiya": "функция",
    "tailand": "таиланд",
}

# Не переводить: марки, адреса почты, @имена, ссылки, HTML-сущности.
PROTECT = re.compile(
    r"&[#\w]+;|https?://\S+|[\w.+-]+@[\w.-]+\.\w+|@\w+|EASY ESTATE|KPI|Android|Google Play|App Store|Telegram"
)

_PAIRS = {"oʻ": "ў", "gʻ": "ғ", "sh": "ш", "ch": "ч", "yo": "ё", "yu": "ю", "ya": "я", "ye": "е"}
_SINGLE = {
    "a": "а", "b": "б", "d": "д", "e": "е", "f": "ф", "g": "г", "h": "ҳ", "i": "и", "j": "ж", "k": "к",
    "l": "л", "m": "м", "n": "н", "o": "о", "p": "п", "q": "қ", "r": "р", "s": "с", "t": "т", "u": "у",
    "v": "в", "x": "х", "y": "й", "z": "з", "c": "ц", "w": "в", "ʼ": "ъ",
}
_VOWELS = set("aeiouAEIOUоаеиуОАЕИУўЎ")


def _word(w):
    low = w.lower()
    for base, cyr in WORDS.items():
        if low.startswith(base):
            rest = _word(w[len(base):]) if len(w) > len(base) else ""
            head = cyr.capitalize() if w[:1].isupper() else cyr
            if w[:len(base)].isupper() and len(base) > 1:
                head = cyr.upper()
            return head + rest
    out = []
    i = 0
    while i < len(w):
        two = w[i:i + 2]
        lt = two.lower()
        prev = w[i - 1] if i else ""
        if lt in _PAIRS and not (lt == "yo" and w[i + 2:i + 3] == "ʻ"):
            c = _PAIRS[lt]
            i += 2
            src = two
        else:
            ch = w[i]
            lc = ch.lower()
            if lc == "e" and (i == 0 or prev in _VOWELS):
                c = "э"
            else:
                c = _SINGLE.get(lc, ch)
            i += 1
            src = ch
        if src[:1].isupper():
            c = c.upper() if (len(src) > 1 and src.isupper()) else c[:1].upper() + c[1:]
        out.append(c)
    return "".join(out)


def to_cyrl(text):
    """Перевести узбекский текст с латиницы на кириллицу (без HTML)."""
    parts = []
    pos = 0
    for m in PROTECT.finditer(text):
        parts.append(_text(text[pos:m.start()]))
        parts.append(m.group(0))
        pos = m.end()
    parts.append(_text(text[pos:]))
    return "".join(parts)


def _text(s):
    return re.sub(r"[A-Za-zʻʼ]+", lambda m: _word(m.group(0)), s)


def to_cyrl_html(html_text):
    """То же для HTML: теги и атрибуты не трогаются."""
    return "".join(p if p.startswith("<") else to_cyrl(p) for p in re.split(r"(<[^>]+>)", html_text))


def t_cyrl(t_uz):
    """Словарь T для кириллицы из латинского; ссылки ?lang=uz → ?lang=uz-cyrl."""
    def conv(v, key=""):
        if isinstance(v, str):
            return to_cyrl(v)
        if isinstance(v, list):
            return [conv(x, key) for x in v]
        if isinstance(v, tuple):
            return tuple(conv(x, key) for x in v)
        return v
    out = {}
    for k, v in t_uz.items():
        if k == "nav":
            out[k] = [(a, to_cyrl(b)) for a, b in v]
        elif k == "steps":
            out[k] = [tuple(to_cyrl(x) if j != 2 else x for j, x in enumerate(s)) for s in v]
        elif k == "pr_cards":
            out[k] = [(to_cyrl(n), a, to_cyrl(p), to_cyrl(d)) for n, a, p, d in v]
        elif k == "f_links":
            out[k] = [(h.replace("lang=uz", "lang=uz-cyrl"), to_cyrl(x)) for h, x in v]
        else:
            out[k] = conv(v, k)
    return out
