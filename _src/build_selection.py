#!/usr/bin/env python3
"""Сборка страницы подборки selection.html (search_selections_v1, раздел 7; решения 270 (2), 274).

Страница только показывает подборку и объект; любое действие ведёт в приложение
(easyestate://selection?t=...). Данные — функция selection-view по токену из
фрагмента #t= (фрагмент не уходит в журналы сервера).

Выход:
  selection.html                 — страница (стили и скрипт внутри);
  assets/sel/<lang>.json         — реестр полей и названия (ru, en, uz, id) из репозитория приложения;
  assets/geo/<cc>.json           — названия регионов и городов GeoNames (CC BY 4.0) по странам.

Запуск: python3 _src/build_selection.py <путь к копии репозитория EASY-ESTATE>
Пересобирать при смене версии реестра (config/registry) или справочника assets/geo приложения.
"""
import gzip
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
LANGS = ["ru", "en", "uz", "id"]
FUNCTION_URL = "https://yyaehdfbdhmqnamyhgtl.supabase.co/functions/v1/selection-view"

# Группы полной карточки у клиента: порядок и ключи — form_layout.json приложения;
# заметки и «Только для вас» на веб не идут никогда; «reveal» у клиента — «Адрес и документы».
CLIENT_GROUPS = ["main", "features", "building", "sale_terms", "rent_terms", "reveal"]
# Поля, которые карточка показывает отдельно (шапка, фото, цены, описание) или не показывает.
SKIP_KEYS = {
    "property.offer_sale", "property.offer_rent", "property.property_type", "property.property_subtype",
    "property.hide_from_clients", "property.photos", "property.video", "property.floor_plan",
    "property.description_short", "property.description_full", "property.description_language",
    "property.geo", "offer_sale.sale_price", "offer_rent.rent_rate", "offer_rent.rent_period",
    "property.agent_code", "property.developer_project_id", "property.developer_unit_id",
    "property.actuality_checked_at",
}

UI = {
    "ru": {
        "title": "Подборка от риелтора",
        "loading": "Загружаем подборку",
        "realtor": "Ваш риелтор",
        "exp": {"one": "опыт {n} год", "few": "опыт {n} года", "many": "опыт {n} лет", "other": "опыт {n} года"},
        "picked": "Подобрано для вас",
        "objects": {"one": "{n} объект", "few": "{n} объекта", "many": "{n} объектов", "other": "{n} объекта"},
        "now": "обновлено сейчас",
        "rec": "Рекомендации риелтора",
        "rec_badge": "Рекомендую",
        "all": "Все объекты подборки",
        "criteria": "Что ищем",
        "price": "Цена",
        "area": "Площадь",
        "land": "Участок",
        "from": "от {v}",
        "to": "до {v}",
        "tol": "Расширить поиск",
        "tol_hint": "Допуск по цене и площади, до {n} %",
        "currency": "Валюта цен",
        "no_rate": "Курса для этой валюты нет, цены показаны в валюте риелтора",
        "rate_date": "Пересчёт по курсу на {d}",
        "more": "Показать ещё",
        "gone": "Объект больше недоступен",
        "dev_up": "на {n} % выше запроса",
        "dev_down": "на {n} % ниже запроса",
        "photos": "{n} фото",
        "video": "Видео",
        "open": "Открыть в приложении",
        "act": "Оценить объекты, сохранить подборку, задать вопрос риелтору и записаться на просмотр можно в приложении EASY ESTATE.",
        "install": "Если приложения ещё нет, попросите у риелтора ссылку на установку, затем снова откройте эту ссылку.",
        "expired": "Срок подборки истёк. Попросите риелтора прислать новую.",
        "bad": "Ссылка на подборку неполная. Попросите риелтора прислать её ещё раз.",
        "busy": "Слишком много запросов. Повторим через {n} с.",
        "error": "Не удалось загрузить. Проверьте интернет и попробуйте ещё раз.",
        "retry": "Повторить",
        "back": "Вся подборка",
        "empty": "Сейчас в подборке нет объектов.",
        "empty_tol": "Попробуйте расширить поиск.",
        "note": "Заметка риелтора",
        "place": "Расположение",
        "approx": "Показана примерная область, около 300 м. Точный адрес риелтор сообщит в приложении.",
        "checked": "Актуальность проверена {d}",
        "updated": "Обновлено {d}",
        "studio": "Студия",
        "bedrooms": {"one": "{n} спальня", "few": "{n} спальни", "many": "{n} спален", "other": "{n} спальни"},
        "rooms": {"one": "{n} комната", "few": "{n} комнаты", "many": "{n} комнат", "other": "{n} комнаты"},
        "sum_bed": "{n} сп.",
        "sum_floor": "{n} эт.",
        "yes": "Да", "no": "Нет", "no_parking": "Нет парковки",
        "city_region": "{n} (город)",
        "m2": "кв. м", "sqft": "кв. футы",
        "sotka": {"one": "{n} сотка", "few": "{n} сотки", "many": "{n} соток", "fraction": "{n} сотки"},
        "per": {"day": "/ сутки", "week": "/ нед.", "month": "/ мес."},
        "groups": {"main": "Основное", "features": "Характеристики", "building": "Дом и инфраструктура",
                   "sale_terms": "Условия продажи", "rent_terms": "Условия аренды", "reveal": "Адрес и документы",
                   "description": "Описание"},
        "sale": "Продажа", "rent": "Аренда",
        "foot": "EASY ESTATE. Личный помощник риелтора",
        "map_attr": "Карта",
    },
    "en": {
        "title": "Selection from your agent",
        "loading": "Loading the selection",
        "realtor": "Your agent",
        "exp": {"one": "{n} year of experience", "other": "{n} years of experience"},
        "picked": "Picked for you",
        "objects": {"one": "{n} property", "other": "{n} properties"},
        "now": "updated just now",
        "rec": "Agent's recommendations",
        "rec_badge": "Recommended",
        "all": "All properties in the selection",
        "criteria": "What we are looking for",
        "price": "Price",
        "area": "Area",
        "land": "Land",
        "from": "from {v}",
        "to": "up to {v}",
        "tol": "Widen the search",
        "tol_hint": "Tolerance for price and area, up to {n} %",
        "currency": "Currency",
        "no_rate": "There is no rate for this currency, prices are in the agent's currency",
        "rate_date": "Converted at the rate of {d}",
        "more": "Show more",
        "gone": "This property is no longer available",
        "dev_up": "{n} % above the request",
        "dev_down": "{n} % below the request",
        "photos": "{n} photos",
        "video": "Video",
        "open": "Open in the app",
        "act": "Rate the properties, save the selection, ask your agent and book a viewing in the EASY ESTATE app.",
        "install": "If the app is not installed yet, ask your agent for the installation link, then open this link again.",
        "expired": "This selection has expired. Ask your agent to send a new one.",
        "bad": "The selection link is incomplete. Ask your agent to send it again.",
        "busy": "Too many requests. Retrying in {n} s.",
        "error": "Could not load. Check your connection and try again.",
        "retry": "Try again",
        "back": "Whole selection",
        "empty": "There are no properties in the selection right now.",
        "empty_tol": "Try widening the search.",
        "note": "Note from your agent",
        "place": "Location",
        "approx": "An approximate area of about 300 m is shown. Your agent will share the exact address in the app.",
        "checked": "Availability checked {d}",
        "updated": "Updated {d}",
        "studio": "Studio",
        "bedrooms": {"one": "{n} bedroom", "other": "{n} bedrooms"},
        "rooms": {"one": "{n} room", "other": "{n} rooms"},
        "sum_bed": "{n} bd",
        "sum_floor": "fl. {n}",
        "yes": "Yes", "no": "No", "no_parking": "No parking",
        "city_region": "{n} (city)",
        "m2": "sq m", "sqft": "sq ft",
        "sotka": {"one": "{n} sotka", "few": "{n} sotkas", "many": "{n} sotkas", "fraction": "{n} sotkas"},
        "per": {"day": "/ day", "week": "/ week", "month": "/ month"},
        "groups": {"main": "Main", "features": "Features", "building": "Building and surroundings",
                   "sale_terms": "Sale terms", "rent_terms": "Rent terms", "reveal": "Address and documents",
                   "description": "Description"},
        "sale": "Sale", "rent": "Rent",
        "foot": "EASY ESTATE. Personal assistant for real estate agents",
        "map_attr": "Map",
    },
    "uz": {
        "title": "Rieltordan toʻplam",
        "loading": "Toʻplam yuklanmoqda",
        "realtor": "Rieltoringiz",
        "exp": {"other": "{n} yillik tajriba"},
        "picked": "Siz uchun tanlandi",
        "objects": {"other": "{n} ta obyekt"},
        "now": "hozir yangilandi",
        "rec": "Rieltor tavsiyalari",
        "rec_badge": "Tavsiya qilaman",
        "all": "Toʻplamdagi barcha obyektlar",
        "criteria": "Nima qidiryapmiz",
        "price": "Narx",
        "area": "Maydon",
        "land": "Yer maydoni",
        "from": "{v} dan",
        "to": "{v} gacha",
        "tol": "Qidiruvni kengaytirish",
        "tol_hint": "Narx va maydon boʻyicha ogʻish, {n} % gacha",
        "currency": "Narx valyutasi",
        "no_rate": "Bu valyuta uchun kurs yoʻq, narxlar rieltor valyutasida",
        "rate_date": "{d} kursi boʻyicha hisoblangan",
        "more": "Yana koʻrsatish",
        "gone": "Obyekt endi mavjud emas",
        "dev_up": "soʻrovdan {n} % yuqori",
        "dev_down": "soʻrovdan {n} % past",
        "photos": "{n} ta foto",
        "video": "Video",
        "open": "Ilovada ochish",
        "act": "Obyektlarni baholash, toʻplamni saqlash, rieltorga savol berish va koʻrishga yozilish EASY ESTATE ilovasida.",
        "install": "Agar ilova hali oʻrnatilmagan boʻlsa, rieltordan oʻrnatish havolasini soʻrang va bu havolani qayta oching.",
        "expired": "Toʻplam muddati tugagan. Rieltordan yangisini yuborishni soʻrang.",
        "bad": "Toʻplam havolasi toʻliq emas. Rieltordan uni qayta yuborishni soʻrang.",
        "busy": "Soʻrovlar juda koʻp. {n} soniyadan keyin qayta urinamiz.",
        "error": "Yuklab boʻlmadi. Internetni tekshirib, qayta urinib koʻring.",
        "retry": "Qayta urinish",
        "back": "Butun toʻplam",
        "empty": "Hozir toʻplamda obyekt yoʻq.",
        "empty_tol": "Qidiruvni kengaytirib koʻring.",
        "note": "Rieltor izohi",
        "place": "Joylashuv",
        "approx": "Taxminiy hudud koʻrsatilgan, taxminan 300 m. Aniq manzilni rieltor ilovada aytadi.",
        "checked": "Dolzarbligi tekshirilgan: {d}",
        "updated": "Yangilangan: {d}",
        "studio": "Studiya",
        "bedrooms": {"other": "{n} yotoqxona"},
        "rooms": {"other": "{n} xona"},
        "sum_bed": "{n} yot.",
        "sum_floor": "{n} qavat",
        "yes": "Ha", "no": "Yoʻq", "no_parking": "Avtoturargoh yoʻq",
        "city_region": "{n} (shahar)",
        "m2": "kv. m", "sqft": "kv. fut",
        "sotka": {"other": "{n} sotix", "fraction": "{n} sotix"},
        "per": {"day": "/ kun", "week": "/ hafta", "month": "/ oy"},
        "groups": {"main": "Asosiy", "features": "Xususiyatlar", "building": "Uy va infratuzilma",
                   "sale_terms": "Sotuv shartlari", "rent_terms": "Ijara shartlari", "reveal": "Manzil va hujjatlar",
                   "description": "Tavsif"},
        "sale": "Sotuv", "rent": "Ijara",
        "foot": "EASY ESTATE. Rieltorning shaxsiy yordamchisi",
        "map_attr": "Xarita",
    },
    "id": {
        "title": "Pilihan properti dari agen Anda",
        "loading": "Memuat pilihan",
        "realtor": "Agen Anda",
        "exp": {"other": "pengalaman {n} tahun"},
        "picked": "Dipilih untuk Anda",
        "objects": {"other": "{n} properti"},
        "now": "baru diperbarui",
        "rec": "Rekomendasi agen",
        "rec_badge": "Direkomendasikan",
        "all": "Semua properti pilihan",
        "criteria": "Yang dicari",
        "price": "Harga",
        "area": "Luas",
        "land": "Luas tanah",
        "from": "dari {v}",
        "to": "hingga {v}",
        "tol": "Perluas pencarian",
        "tol_hint": "Toleransi harga dan luas, hingga {n} %",
        "currency": "Mata uang",
        "no_rate": "Kurs untuk mata uang ini tidak tersedia, harga dalam mata uang agen",
        "rate_date": "Dikonversi dengan kurs {d}",
        "more": "Tampilkan lagi",
        "gone": "Properti ini sudah tidak tersedia",
        "dev_up": "{n} % di atas permintaan",
        "dev_down": "{n} % di bawah permintaan",
        "photos": "{n} foto",
        "video": "Video",
        "open": "Buka di aplikasi",
        "act": "Beri nilai properti, simpan pilihan, tanya agen, dan jadwalkan kunjungan di aplikasi EASY ESTATE.",
        "install": "Jika aplikasi belum terpasang, minta tautan instalasi kepada agen Anda, lalu buka tautan ini lagi.",
        "expired": "Masa berlaku pilihan ini sudah habis. Minta agen Anda mengirim yang baru.",
        "bad": "Tautan pilihan tidak lengkap. Minta agen Anda mengirimkannya lagi.",
        "busy": "Terlalu banyak permintaan. Mencoba lagi dalam {n} detik.",
        "error": "Gagal memuat. Periksa koneksi Anda dan coba lagi.",
        "retry": "Coba lagi",
        "back": "Semua pilihan",
        "empty": "Saat ini belum ada properti dalam pilihan.",
        "empty_tol": "Coba perluas pencarian.",
        "note": "Catatan dari agen",
        "place": "Lokasi",
        "approx": "Ditampilkan perkiraan area sekitar 300 m. Agen akan memberikan alamat tepat di aplikasi.",
        "checked": "Ketersediaan diperiksa {d}",
        "updated": "Diperbarui {d}",
        "studio": "Studio",
        "bedrooms": {"other": "{n} kamar tidur"},
        "rooms": {"other": "{n} ruangan"},
        "sum_bed": "{n} KT",
        "sum_floor": "lt. {n}",
        "yes": "Ya", "no": "Tidak", "no_parking": "Tanpa parkir",
        "city_region": "{n} (kota)",
        "m2": "m²", "sqft": "sq ft",
        "sotka": {"other": "{n} sotka", "fraction": "{n} sotka"},
        "per": {"day": "/ hari", "week": "/ minggu", "month": "/ bulan"},
        "groups": {"main": "Utama", "features": "Fitur", "building": "Bangunan dan lingkungan",
                   "sale_terms": "Ketentuan jual", "rent_terms": "Ketentuan sewa", "reveal": "Alamat dan dokumen",
                   "description": "Deskripsi"},
        "sale": "Dijual", "rent": "Disewakan",
        "foot": "EASY ESTATE. Asisten pribadi agen properti",
        "map_attr": "Peta",
    },
}


def registry_pack(app: pathlib.Path, lang: str) -> dict:
    reg = json.loads((app / "config/registry/realtor_registry.json").read_text(encoding="utf-8"))
    layout = json.loads((app / "config/registry/form_layout.json").read_text(encoding="utf-8"))
    labels = json.loads((app / f"config/registry/labels/{lang}.json").read_text(encoding="utf-8"))
    types = {}
    for entity in ("property", "offer_sale", "offer_rent"):
        for f in reg["entities"][entity]["fields"]:
            if f["visibility"] == "private":
                continue
            entry = [f["type"]]
            if f.get("dict"):
                entry.append(f["dict"])
            types[f"{entity}.{f['key']}"] = entry
    groups = []
    by_name = {g["group"]: g for g in layout["groups"]["property"]}
    for name in CLIENT_GROUPS:
        keys = [k for k in by_name[name]["keys"] if k in types and k not in SKIP_KEYS]
        groups.append([name, keys])
    names = {}
    for entity in ("property", "offer_sale", "offer_rent"):
        for key, text in labels["fields"][entity].items():
            if f"{entity}.{key}" in types:
                names[f"{entity}.{key}"] = text
    used = {t[1] for t in types.values() if len(t) > 1}
    dicts = {}
    for name, values in labels["dicts"].items():
        if name in used and name not in ("country", "region", "city", "district", "currency", "language"):
            dicts[name] = {k: v for k, v in values.items() if k != "_name"}
    return {
        "v": reg["version"],
        "types": types,
        "names": names,
        "groups": groups,
        "dicts": dicts,
        "by_country": labels.get("field_by_country", {}).get("property", {}),
        "entities": labels["entities"],
    }


def geo_pack(path: pathlib.Path) -> dict:
    data = json.loads(gzip.decompress(path.read_bytes()).decode("utf-8"))

    def names(n: dict) -> list:
        en = n.get("en", "")
        # Пустая строка — как по-английски (меньше файл).
        return [en] + ["" if n.get(code, en) == en else n[code] for code in ("ru", "uz", "id")]

    return {
        "r": {str(r[0]): names(r[1]) for r in data["regions"]},
        "c": {str(c[0]): names(c[5]) for c in data["cities"]},
    }


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Нужен путь к копии репозитория EASY-ESTATE")
    app = pathlib.Path(sys.argv[1]).resolve()
    sel_dir = ROOT / "assets" / "sel"
    sel_dir.mkdir(parents=True, exist_ok=True)
    version = None
    for lang in LANGS:
        pack = registry_pack(app, lang)
        version = pack["v"]
        (sel_dir / f"{lang}.json").write_text(
            json.dumps(pack, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    geo_dir = ROOT / "assets" / "geo"
    geo_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for path in sorted((app / "assets" / "geo").glob("*.json.gz")):
        cc = path.name.split(".")[0]
        (geo_dir / f"{cc}.json").write_text(
            json.dumps(geo_pack(path), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        count += 1
    css = (SRC / "selection.css").read_text(encoding="utf-8")
    js = (SRC / "selection.js").read_text(encoding="utf-8")
    logo = (ROOT / "assets" / "logo-mark.svg").read_text(encoding="utf-8").split("?>", 1)[-1].strip()
    logo = logo.split("<title>")[0] + logo.split("</title>")[1]
    logo = logo.split("<desc>")[0] + logo.split("</desc>")[1]
    logo = logo.replace('role="img" aria-label="EASY ESTATE logo mark"', 'aria-hidden="true" focusable="false"')
    config = {"fn": FUNCTION_URL, "reg": version, "ui": UI}
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<meta name="referrer" content="no-referrer">
<meta name="theme-color" content="#4A7640">
<title>EASY ESTATE</title>
<link rel="icon" href="assets/logo-mark.svg" type="image/svg+xml">
<style>
{css}</style>
</head>
<body>
<header class="head">
  <a class="brand" href="/" aria-label="EASY ESTATE">{logo}<span>EASY ESTATE</span></a>
  <nav class="langs" id="langs" aria-label="Language"></nav>
</header>
<main id="app" aria-live="polite"><p class="state" id="state">Loading…</p></main>
<div class="cta" id="cta" hidden>
  <a class="btn" id="open" href="#"></a>
</div>
<footer class="foot" id="foot"></footer>
<script>
window.EE_SEL = {json.dumps(config, ensure_ascii=False, separators=(",", ":"))};
</script>
<script>
{js}</script>
</body>
</html>
"""
    (ROOT / "selection.html").write_text(page, encoding="utf-8")
    print(f"selection.html, assets/sel ({len(LANGS)}), assets/geo ({count}); реестр версии {version}")


if __name__ == "__main__":
    main()
