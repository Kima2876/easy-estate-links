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
    "status": "Yopiq test rejimi · Android",
    "h1": "Rieltorning shaxsiy yordamchisi",
    "lead": "Koʻchmas mulk agentlari va agentliklari uchun professional ish vositasi: obyektlar, mijozlar va obyektlar toʻplamlari yagona ilovada. Kundalik ish kamayadi, KPI oshadi, mijozlar bazasi esa doimo sizda qoladi.",
    "cta": "Biz bilan bogʻlanish",
    "cta2": "Imkoniyatlar bilan tanishish",
    "hero_note": "Ilovaning haqiqiy ekranlari (interfeys rus tilida), maʼlumotlar namunaviy: Toshkent",
    "hero_alt": ["Rieltorning bosh sahifasi: bugungi vazifalar va baza", "Obyekt kartasi: narx va tavsif"],
    "p_eyebrow": "Muammo",
    "p_h": "Rieltorning ish kuni bitimlarga emas, telefonga sarflanadi",
    "p_big": "80% gacha",
    "p_big_txt": "ish vaqti obyekt va mijozlar bilan ishlashga emas, qoʻngʻiroqlar va yozishmalarga sarflanadi",
    "p_src": "Asoschining bozordagi amaliy tajribasiga asoslangan baho",
    "p_items": [
        ("Eʼlon", "Mijoz qoʻngʻiroq qiladi va barcha tafsilotlarni qaytadan aniqlashtirishga toʻgʻri keladi"),
        ("Messenjerlar", "Variantlar va ovozli xabarlar bir-biriga aralashib ketadi"),
        ("Chalkashlik", "Qaysi xabar qaysi obyektga tegishli ekani har ikki tomon uchun noaniq"),
        ("Obyekt allaqachon sotilgan", "Yoki eʼlon faqat kontaktlarni yigʻish uchun joylashtirilgan boʻlib chiqadi"),
    ],
    "s_eyebrow": "Qanday ishlaydi",
    "s_h": "Rieltor ovoz bilan kiritadi, mijoz oʻzi tanlaydi",
    "steps": [
        ("Obyektni ovoz bilan kiritish", "Obyekt haqida joyning oʻzida aytib bering. Sunʼiy intellekt maʼlumotlarni tegishli maydonlarga ajratadi, internet boʻlmaganda ham ishlaydi va nimani aniqlaganini koʻrsatadi.", "01_voice", "«Mana nimalarni aniqladim» ekrani: ovozli maʼlumot maydonlarga ajratilgan"),
        ("Maxfiy maʼlumotlar himoyalangan", "Mulkdor narxi, komissiya va kontaktlar faqat sizga koʻrinadi. Server ularni mijozga hech qachon uzatmaydi.", "02_private", "Obyekt kartasidagi «Faqat siz uchun» bloki", "Mijoz bu maʼlumotlarni koʻrmaydi"),
        ("Mijoz baho beradi", "Mijoz obyektlaringizni oʻz ilovasida koʻradi va ularni baholaydi. Siz esa unga qaysi variantlar maʼqul kelganini koʻrasiz.", "03_client_list", "Mijoz ilovasi: rieltor obyektlari va baholar"),
    ],
    "c_eyebrow": "Mijoz uchun vitrina, rieltor uchun tartib",
    "c_h": "Odatda yozishmalarda yoʻqolib ketadigan barcha maʼlumotlar bir joyda",
    "c_items": [
        ("1 dan 5 gacha yulduz va «Yashirish»", "Mijoz obyektlarni yozishmalarsiz baholaydi"),
        ("Narx mijoz valyutasida", "Joriy kurs boʻyicha avtomatik qayta hisoblanadi"),
        ("22 ta til", "Rieltor ham, mijoz ham interfeysni oʻz tilida koʻradi"),
        ("Internetsiz ishlaydi", "Aloqa tiklanishi bilan barcha maʼlumotlar avtomatik yuboriladi"),
    ],
    "c_soon_label": "Tez orada",
    "c_soon": "Obyektlar toʻplamini havola orqali yuborish, koʻrikka yozilish va obyekt boʻyicha chat",
    "c_tags": ["Mijoz", "Rieltor"],
    "c_alts": ["Mijoz ilovasidagi obyekt kartasi va yulduzli baho", "Rieltorning filtrlangan obyektlar roʻyxati"],
    "b_eyebrow": "Asosiy afzallik",
    "b_h": "Baza rieltorning oʻziga tegishli",
    "b_items": [
        ("Sizning bazangiz", "Boshqa agentlikka oʻtsangiz ham, baza siz bilan qoladi. Bazani toʻliq yuklab olish imkoniyati pullik tarif ishga tushishidan oldin qoʻshiladi."),
        ("Yopiq maydonlar", "Mulkdor narxi, komissiya va kontaktlar ekranda shunchaki yashirilmaydi, ular server darajasida himoyalangan."),
        ("Toʻliq jarayon", "Obyekt, mijoz, obyektlar toʻplami, baholar va koʻriklar bir joyda: jadvallar va messenjerdagi qaydlarsiz."),
    ],
    "pr_eyebrow": "Narxlar",
    "pr_h": "Yagona obuna, tariflarga boʻlinmagan",
    "pr_note": "Hozirda ilova yopiq test rejimida va sinovchilar uchun bepul. Narxlar ilova Google Play va App Store doʻkonlarida chiqqanidan soʻng amal qiladi.",
    "pr_cards": [
        ("Sinov muddati", "0", "", "Ilovani amalda sinab koʻrish uchun barcha imkoniyatlar"),
        ("Oylik", "10", "oyiga", "Sunʼiy intellekt yordamida obyektlarni ovoz bilan toʻldirish obunaga kiritilgan"),
        ("Yillik", "100", "yiliga", "Oylik toʻlovga nisbatan $20 tejaysiz, bu ikki oylik obuna narxiga teng"),
    ],
    "pr_free": "Rieltor mijozlari uchun ilova doimo bepul.",
    "pr_tax": "Narxlar xaridor mamlakatida undiriladigan soliqlarsiz koʻrsatilgan.",
    "ct_eyebrow": "Aloqa",
    "ct_h": "Sinab koʻrmoqchimisiz yoki savollaringiz bormi?",
    "ct_p": "Bizga yozing. Oʻzbekiston, BAA, Tailand va Indoneziyadagi rieltorlarni sinovga birinchi navbatda taklif qilamiz.",
    "copy": "Manzilni nusxalash",
    "copied": "Manzil nusxalandi",
    "f_company": "«EASY ESTATE» MChJ, STIR 307553192, Toshkent, Oʻzbekiston",
    # Политика и условия — узбекская редакция (_src/legal_uz.py, сборка _src/build_legal.py).
    "f_links": [("support.html?lang=uz", "Qoʻllab-quvvatlash"), ("privacy.html?lang=uz", "Maxfiylik siyosati"), ("terms.html?lang=uz", "Foydalanish shartlari"), ("delete-account.html?lang=uz", "Hisobni oʻchirish")],
    "f_demo": "Saytdagi ekranlar haqiqiy, maʼlumotlar namunaviy.",
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
<p class="lead">Ilova, sinov jarayoni va hisobingizga oid savollarga javob beramiz.</p>
<section><h2>Telegram</h2>
<p>EASY ESTATE qoʻllab-quvvatlash boti: savol yoki taklifingizni shu yerga yozing.</p>
<p><a class="btn" href="https://t.me/{bot}">@{bot}</a></p></section>
<section><h2>Elektron pochta</h2>{mail(support_mail, L)}</section>
<section><h2>Maʼlumotlar va hisob</h2>
<p>Shaxsiy maʼlumotlarga oid savollar: {privacy_mail}. Hisobni oʻchirish tartibi: <a href="delete-account.html?lang={L}">Hisobni oʻchirish</a>.</p></section>'''
    if slug == "delete-account":
        return f'''
<p class="lead">EASY ESTATE ilovasi, ishlab chiquvchi: «EASY ESTATE» MChJ. Ushbu sahifada hisob va unga bogʻliq maʼlumotlarni oʻchirish tartibi bayon etilgan.</p>
<section><h2>Oʻchirish uchun soʻrov yuborish tartibi</h2>
<ol class="doc-steps">
<li>Hisob roʻyxatdan oʻtkazilgan elektron pochta manzilidan quyidagi manzilga xat yuboring.</li>
<li>Xat mavzusida «Hisobni oʻchirish» deb koʻrsating. Sababini izohlash shart emas.</li>
<li>Hisob va unga bogʻliq maʼlumotlar 30 kun ichida oʻchiriladi, bu haqda sizga javob xati yuboriladi.</li>
</ol>
{mail(privacy_mail, L)}
<p class="small">Ilovaning oʻzida hisobni oʻchirish imkoniyati ommaviy ishga tushirishdan oldin qoʻshiladi.</p></section>
<section><h2>Nimalar oʻchiriladi</h2>
<p>Hisob va anketa, rieltor bazasi (obyektlar, foto va videolar, mijozlar va mulkdorlar, soʻrovlar, vazifalar, hujjatlar), mijozning rieltor bilan bogʻlanishi, baholar va yashirilgan obyektlar, sunʼiy intellekt yordamchisi bilan yozishmalar.</p></section>
<section><h2>Nimalar saqlanib qoladi va qancha muddatga</h2>
<p>Rieltorning obyekt hujjatlari bilan bajargan amallari jurnali hujjat oʻchirilganidan keyin 3 yil davomida saqlanadi. Texnik hodisalar hisobga bogʻlanmagan holda saqlanib qoladi. Sunʼiy intellekt yordamchisidan foydalanish boʻyicha oylik anonim hisobotlarda shaxsiy maʼlumotlaringiz mavjud emas.</p></section>
<section><h2>Agar siz rieltorning mijozi boʻlsangiz</h2>
<p>Hisobingiz xuddi shu tartibda oʻchiriladi. Rieltor oʻz bazasiga kiritgan siz haqingizdagi maʼlumotlarni rieltorning oʻzi oʻchiradi; agar u javob bermasa, bizga murojaat qiling.</p></section>'''
    return '''
<p class="lead">Bunday sahifa mavjud emas. Havola eskirgan boʻlishi mumkin.</p>
<p><a class="btn" href="/">Bosh sahifaga qaytish</a></p>'''


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
    r"&[#\w]+;|https?://\S+|[\w.+-]+@[\w.-]+\.\w+|@\w+|EASY ESTATE|KPI|Android|Google Play|Google Maps|Google|Gemini|Gmail|GitHub|Supabase|HTTPS|PDF|API|App Store|Telegram"
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
