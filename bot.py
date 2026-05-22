import logging
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
OPERATOR_PHONE = os.getenv("OPERATOR_PHONE", "+998932264566")
DATA_FILE = "data.json"

DEFAULT_DATA = {
    "contacts": {
        "address_ru": "г. Каттакурган, массив Казак овул",
        "address_uz": "Kattaqo'rg'on sh., Qozoq ovul massivi",
        "address_kz": "Каттақурғон қ., Қазақ овул массиві",
        "phone1": "+998932264566",
        "phone2": "+998933466277",
        "instagram": "@ergashotaclinis",
        "website": "https://ergash-ota-tm.uz/",
        "work_hours_ru": "Пн–Сб: 08:00–18:00\nВоскресенье: приём новых пациентов",
        "work_hours_uz": "Du–Shan: 08:00–18:00\nYakshanba: yangi bemorlar qabuli",
        "work_hours_kz": "Дс–Сб: 08:00–18:00\nЖексенбі: жаңа науқастар қабылдау",
    },
    "doctor": {
        "name_ru": "Бердикул Эргашев Журакулович",
        "name_uz": "Berdiqul Ergashev Jo'raqulovich",
        "name_kz": "Бердіқұл Ерғашев Жўрақұлович",
        "title_ru": "Главный врач — Академик\nВрач высшей категории\nПочётный профессор\nДействительный член академии наук Туран",
        "title_uz": "Bosh shifokor — Akademik\nOliy toifali shifokor\nFaxriy professor\nTuron fanlari akademiyasining haqiqiy a'zosi",
        "title_kz": "Бас дәрігер — Академик\nЖоғары санатты дәрігер\nКуратты профессор",
        "photo_id": "",
    },
    "staff": [
        {"name": "Эргашев Бердикул Журакулович", "role": "Главный врач, Академик", "photo_id": ""},
    ],
    "rooms_uz": [
        {"name": "Общий", "people": "10", "adult": "185 000", "child": "172 000"},
        {"name": "Урта миёна", "people": "4-5", "adult": "213 000", "child": "198 000"},
        {"name": "Урта миёна", "people": "2-3", "adult": "224 000", "child": "209 000"},
        {"name": "З/Урта миёна", "people": "4-5", "adult": "249 000", "child": "234 000"},
        {"name": "З/Урта миёна", "people": "2", "adult": "269 000", "child": "254 000"},
        {"name": "Пол/Люкс", "people": "5-7", "adult": "295 000", "child": "280 000"},
        {"name": "Пол/Люкс", "people": "4", "adult": "314 000", "child": "299 000"},
        {"name": "Люкс", "people": "3", "adult": "340 000", "child": "325 000"},
        {"name": "Люкс", "people": "2", "adult": "410 000", "child": "395 000"},
        {"name": "Д/Люкс", "people": "5", "adult": "420 000", "child": "405 000"},
        {"name": "Д/Люкс", "people": "3", "adult": "385 000", "child": "370 000"},
        {"name": "Д/Люкс", "people": "2", "adult": "495 000", "child": "480 000"},
        {"name": "М/Люкс", "people": "4-6", "adult": "420 000", "child": "405 000"},
        {"name": "М/Люкс АБ", "people": "2-3", "adult": "465 000", "child": "450 000"},
        {"name": "М/Люкс", "people": "2", "adult": "495 000", "child": "480 000"},
        {"name": "М/Урта миёна", "people": "3-5", "adult": "313 000", "child": "298 000"},
        {"name": "М/VIP", "people": "2", "adult": "699 000", "child": "684 000"},
        {"name": "М/VIP", "people": "1", "adult": "760 000", "child": "745 000"},
    ],
    "rooms_foreign": [
        {"name": "Стандарт", "people": "4-5", "adult": "308 000", "child": "293 000"},
        {"name": "Стандарт", "people": "2-3", "adult": "317 000", "child": "300 000"},
        {"name": "З/Стандарт", "people": "4-5", "adult": "338 000", "child": "323 000"},
        {"name": "З/Стандарт", "people": "2", "adult": "354 000", "child": "339 000"},
        {"name": "Пол/Люкс", "people": "5-7", "adult": "365 000", "child": "350 000"},
        {"name": "Пол/Люкс", "people": "4", "adult": "385 000", "child": "370 000"},
        {"name": "Люкс", "people": "3", "adult": "395 000", "child": "380 000"},
        {"name": "Люкс", "people": "2", "adult": "410 000", "child": "395 000"},
        {"name": "Д/Люкс", "people": "5", "adult": "420 000", "child": "405 000"},
        {"name": "Д/Люкс", "people": "3", "adult": "385 000", "child": "370 000"},
        {"name": "Д/Люкс", "people": "2", "adult": "495 000", "child": "480 000"},
        {"name": "М/Люкс", "people": "4-6", "adult": "420 000", "child": "405 000"},
        {"name": "М/Люкс АБ", "people": "2-3", "adult": "465 000", "child": "450 000"},
        {"name": "М/Люкс", "people": "2", "adult": "495 000", "child": "480 000"},
        {"name": "М/Стандарт", "people": "3-5", "adult": "313 000", "child": "298 000"},
        {"name": "М/VIP", "people": "2", "adult": "699 000", "child": "684 000"},
        {"name": "М/VIP", "people": "1", "adult": "760 000", "child": "745 000"},
    ],
    "ward_photos": [],
    "clinic_photos": [],
    "samarkand_photos": [],
    "bukhara_photos": [],
    "mrt_15": [
        "МРТ бош мия — 390 000 сўм",
        "МРТ буйин умурткалари — 445 000 сўм",
        "МРТ кўкрак умурткалари — 445 000 сўм",
        "МРТ бел-думғаза умурткалари — 390 000 сўм",
        "МРТ бита бўғин (тизза, товон, елка, тирсак...) — 415 000 сўм",
        "МРТ чаноқ-сон бўғими — 485 000 сўм",
        "МРТ қорин бўшлиғи аъзолари — 485 000 сўм",
        "МРТ кичик чаноқ аъзолари — 485 000 сўм",
    ],
    "mrt_3t_groups": {
        "Бош мия": [
            "МРТ головного мозга — 495 000",
            "МРТ гипофиза — 555 000",
            "МРТ орбит + DWI — 645 000",
            "МРТ придаточных пазух носа — 495 000",
            "МРТ головного мозга и гипофиза — 745 000",
            "МРТ ангиография артерий мозга — 745 000",
        ],
        "Умуртқа поғонаси": [
            "МРТ шейного отдела — 525 000",
            "МРТ грудного отдела — 495 000",
            "МРТ пояснично-крестцового отдела — 495 000",
            "МРТ всего позвоночника (TOTAL SPINE) — 1 300 000",
            "МРТ копчика — 495 000",
        ],
        "Бўғимлар": [
            "МРТ коленного сустава — 475 000",
            "МРТ голеностопного сустава — 475 000",
            "МРТ тазобедренных суставов — 475 000",
            "МРТ лучезапястного сустава — 475 000",
            "МРТ локтевого сустава — 475 000",
            "МРТ стопы — 475 000",
        ],
        "Ички аъзолар": [
            "МРТ печени — 595 000",
            "МРТ брюшной полости — 625 000",
            "МРТ почек и надпочечников — 595 000",
            "МРТ органов малого таза — 595 000",
            "МРТ молочной железы — 615 000",
            "МРТ холангиография 3D — 575 000",
        ],
        "Контраст билан": [
            "Контраст (до 50 кг) — 625 000",
            "Контраст (до 80 кг) — 725 000",
            "Контраст (до 100 кг) — 825 000",
            "Контраст (более 100 кг) — 1 300 000",
        ],
    },
    "mskt_256": [
        "Головной мозг — 345 000",
        "Головной мозг + орбиты — 345 000",
        "Шейный отдел позвоночника — 345 000",
        "Грудной отдел позвоночника — 365 000",
        "Поясничный отдел — 365 000",
        "Органы брюшной полости — 365 000",
        "Малый таз — 365 000",
        "Коленный сустав — 345 000",
        "Кисть / стопа — 345 000",
        "Головной мозг + шейный отдел — 690 000",
        "Грудной отдел + брюшная полость — 730 000",
        "Весь позвоночник — 1 075 000",
        "Исследование полного тела — 3 650 000",
    ],
    "mskt_128": [
        "МСКТ бош мия — 300 000",
        "МСКТ кўзлар — 300 000",
        "МСКТ буйин умурткалари — 300 000",
        "МСКТ кўкрак қафаси — 320 000",
        "МСКТ бел умурткалари — 300 000",
        "МСКТ тоз суяклари — 310 000",
        "МСКТ қорин бўшлиғи — 320 000",
        "МСКТ бутун тана — 820 000",
        "МСКТ кичик чаноқ — 300 000",
        "МСКТ тизза бўғими — 300 000",
        "МСКТ товон суяклари — 300 000",
    ],
    "other_diagnostics": [
        "УЗИ (ўт-жигар ва бошқалар) — 70 000 сўмдан",
        "Маммография — 250 000 сўм",
        "Фиброскан — 220 000 сўм",
        "Криолиполиз — 56 000 сўм",
    ],
    "lab": [
        "Инсулин — 105 000",
        "Тестостерон — 100 000",
        "Эстрадиол — 100 000",
        "Пролактин — 100 000",
        "ТТГ — 70 000",
        "Т3 — 70 000",
        "Т4 свободный — 70 000",
        "HCV — 75 000",
        "HBsAg — 75 000",
        "Ревма проба — 98 000",
        "Ферритин — 80 000",
        "Витамин D3 — 70 000",
    ],
    "diseases": [
        "1. Анемия касаллиги, даволаш ва олдини олиш",
        "2. Верльгоф касаллиги",
        "3. Сурункали простатит",
        "4. Буйрак ва сийдик йўллари касалликлари",
        "5. Ревматоидли полиартрит",
        "6. Семизлик хасталиги, олдини олиш ва вазнни камайтириш",
        "7. Ўсма касалликлари, профилактика ва даволаш",
        "8. Гиршпрунг касаллиги",
        "9. Рейно касаллиги",
        "10. Витилиго (пес) касаллиги",
        "11. Ўпканинг сурункали касалликлари",
        "12. Тери касалликлари (псориаз, экзема, аллергик дерматитлар)",
        "14. Бўйин, кўкрак, бел – думғаза қисмлари остеохондрози ва диск чурралари",
        "15. Гижжа касалликлари",
        "16. Озиқ – овқат аллергияси",
        "17. Сурункали қабзиятлар",
        "18. Сурункали диареялар",
        "19. Долихоколон, долихосигма касалликлари",
        "20. COVID инфекциясига чалинган ва асоратланган беморларни даволаш",
        "21. ТОРЧ инфекциясига чалинган ва асоратланган беморларни даволаш",
        "22. Иммунитетни ошириш ва қайта тиклаш",
        "23. Инсон ички муҳитини тозалаш",
        "24. Демпинг синдром",
        "25. Жигар ва ўт йўллари касалликлари",
        "26. Қандли диабет ва қалқонсимон без касалликлари",
        "27. Эхинококкоз касаллиги",
        "28. Атеросклероз ва юрак ишемик касалликлари",
        "29. Гипертония касаллиги ва унинг асоратлари",
        "30. Ошқозон – ичак йўллари касалликлари",
        "31. Гельминтозлар",
    ],
    "transfer": {
        "ru": "🚗 Стоимость трансфера:\n\n• Каттакурган (вокзал) — 60 000 сум\n• Самарканд (вокзал/аэропорт) — 300 000 сум\n• Ташкент (аэропорт) — 800 000 сум\n\n📞 Для заказа: {phone}",
        "uz": "🚗 Transfer narxlari:\n\n• Kattaqo'rg'on (vokzal) — 60 000 so'm\n• Samarqand (vokzal/aeroport) — 300 000 so'm\n• Toshkent (aeroport) — 800 000 so'm\n\n📞 Buyurtma uchun: {phone}",
        "kz": "🚗 Трансфер бағасы:\n\n• Каттақурғон (вокзал) — 60 000 сум\n• Самарқанд (вокзал/әуежай) — 300 000 сум\n• Ташкент (әуежай) — 800 000 сум\n\n📞 Тапсырыс: {phone}",
    },
    "excursion": {
        "ru": "🕌 Экскурсионные туры (по выходным):\n\n🏛 Самарканд:\n• 1 человек — 150 000 сум\n• Салон (группа) — 500 000 сум\n\n🕌 Бухара:\n• 1 человек — 200 000 сум\n• Салон (группа) — 800 000 сум\n\nВ программе: Регистан, Шахи-Зинда, Биби-Ханум и др.\n\n📞 Запись: {phone}",
        "uz": "🕌 Ekskursiya turlari (dam olish kunlari):\n\n🏛 Samarqand:\n• 1 kishi — 150 000 so'm\n• Salon (guruh) — 500 000 so'm\n\n🕌 Buxoro:\n• 1 kishi — 200 000 so'm\n• Salon (guruh) — 800 000 so'm\n\nDasturda: Registon, Shahi-Zinda, Bibixonim va boshqalar\n\n📞 Buyurtma: {phone}",
        "kz": "🕌 Экскурсиялар (демалыс күндері):\n\n🏛 Самарқанд:\n• 1 адам — 150 000 сум\n• Салон (топ) — 500 000 сум\n\n🕌 Бұхара:\n• 1 адам — 200 000 сум\n• Салон (топ) — 800 000 сум\n\n📞 Тіркелу: {phone}",
    },
    "included": {
        "ru": "✅ В стоимость включено:\n• Проживание\n• Лечение\n• Физиотерапия и мануальная терапия\n• УЗИ, анализ крови, ЭКГ\n• МРТ 1.5Т или МСКТ (1 орган)\n\n➕ Дополнительно:\nМРТ-3Т, МСКТ-256, Маммография, Криолиполиз, Растяжка, Ударно-волновая терапия",
        "uz": "✅ Narxga kiradigan xizmatlar:\n• Turar joy\n• Davolash\n• Fizioterapiya va manual terapiya\n• УЗИ, qon tahlili, EKG\n• МРТ 1.5Т yoki МСКТ (1 organ)\n\n➕ Qo'shimcha:\nМРТ-3Т, МСКТ-256, Mammografiya, Kriolipoliz, Cho'zilish, Zarba-to'lqin terapiyasi",
        "kz": "✅ Бағаға кіретін қызметтер:\n• Тұру\n• Емдеу\n• Физиотерапия және мануалды терапия\n• УДЗ, қан анализі, ЭКГ\n• МРТ 1.5Т немесе МСКТ (1 орган)\n\n➕ Қосымша:\nМРТ-3Т, МСКТ-256, Маммография, Криолиполиз",
    },
    "weekend": {
        "ru": "🌅 В воскресенье мы работаем для новых пациентов!\n\n✅ Приём и регистрация\n✅ Первичный осмотр\n✅ Начало лечения в первый же день\n\n🕌 А в свободное время — экскурсии в Самарканд и Бухару!\n\n📞 Свяжитесь с нами: {phone}",
        "uz": "🌅 Yakshanba kuni yangi bemorlarni qabul qilamiz!\n\n✅ Qabul va ro'yxatga olish\n✅ Dastlabki ko'rik\n✅ Birinchi kuniyoq davolash boshlanadi\n\n🕌 Bo'sh vaqtda — Samarqand va Buxoroga ekskursiya!\n\n📞 Bog'laning: {phone}",
        "kz": "🌅 Жексенбіде жаңа науқастарды қабылдаймыз!\n\n✅ Тіркеу және қабылдау\n✅ Алғашқы тексеру\n✅ Бірінші күні емдеу басталады\n\n📞 Байланысыңыз: {phone}",
    },
}


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    save_data(DEFAULT_DATA)
    return DEFAULT_DATA


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_lang(context):
    return context.user_data.get("lang", "ru")


# ─── KEYBOARDS ────────────────────────────────────────────────────────────────

def lang_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton("🇰🇿 Қазақша", callback_data="lang_kz"),
        ]
    ])


MENU_LABELS = {
    "ru": {
        "clinic":      "🏥 О клинике",
        "rooms":       "🛏 Стоимость номеров",
        "diagnostics": "🧲 Диагностика",
        "doctor":      "👨‍⚕️ Главный врач",
        "staff":       "👥 Наша команда",
        "diseases":    "🩺 Список болезней",
        "wards":       "🏨 Палаты",
        "transfer":    "🚗 Трансфер",
        "excursion":   "🕌 Экскурсии",
        "weekend":     "🌅 Воскресенье",
        "operator":    "📞 Оператор",
    },
    "uz": {
        "clinic":      "🏥 Klinika haqida",
        "rooms":       "🛏 Xonalar narxi",
        "diagnostics": "🧲 Diagnostika",
        "doctor":      "👨‍⚕️ Bosh shifokor",
        "staff":       "👥 Jamoamiz",
        "diseases":    "🩺 Kasalliklar ro'yxati",
        "wards":       "🏨 Palatalar",
        "transfer":    "🚗 Kutib olish",
        "excursion":   "🕌 Ekskursiya",
        "weekend":     "🌅 Yakshanba",
        "operator":    "📞 Operator",
    },
    "kz": {
        "clinic":      "🏥 Клиника туралы",
        "rooms":       "🛏 Бөлмелер бағасы",
        "diagnostics": "🧲 Диагностика",
        "doctor":      "👨‍⚕️ Бас дәрігер",
        "staff":       "👥 Біздің команда",
        "diseases":    "🩺 Аурулар тізімі",
        "wards":       "🏨 Палаталар",
        "transfer":    "🚗 Трансфер",
        "excursion":   "🕌 Экскурсия",
        "weekend":     "🌅 Жексенбі",
        "operator":    "📞 Оператор",
    },
}


def main_menu_keyboard(lang):
    labels = MENU_LABELS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(labels["clinic"],      callback_data="menu_clinic"),
         InlineKeyboardButton(labels["doctor"],      callback_data="menu_doctor")],
        [InlineKeyboardButton(labels["staff"],       callback_data="menu_staff"),
         InlineKeyboardButton(labels["diseases"],    callback_data="menu_diseases")],
        [InlineKeyboardButton(labels["rooms"],       callback_data="menu_rooms")],
        [InlineKeyboardButton(labels["wards"],       callback_data="menu_wards")],
        [InlineKeyboardButton(labels["diagnostics"], callback_data="menu_diagnostics")],
        [InlineKeyboardButton(labels["transfer"],    callback_data="menu_transfer"),
         InlineKeyboardButton(labels["excursion"],   callback_data="menu_excursion")],
        [InlineKeyboardButton(labels["weekend"],     callback_data="menu_weekend")],
        [InlineKeyboardButton(labels["operator"],    callback_data="menu_operator")],
    ])


def back_keyboard(lang):
    label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data="back_main")]])


def rooms_keyboard(lang):
    labels = {
        "ru": ("🇺🇿 Граждане Узбекистана", "🌍 Иностранные граждане", "⬅️ Назад"),
        "uz": ("🇺🇿 O'zbekiston fuqarolari", "🌍 Xorijiy fuqarolar", "⬅️ Orqaga"),
        "kz": ("🇺🇿 Өзбекстан азаматтары", "🌍 Шетел азаматтары", "⬅️ Артқа"),
    }[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(labels[0], callback_data="rooms_uz")],
        [InlineKeyboardButton(labels[1], callback_data="rooms_foreign")],
        [InlineKeyboardButton(labels[2], callback_data="back_main")],
    ])


def diagnostics_keyboard(lang):
    labels = {
        "ru": ("🧲 МРТ 1.5Т", "🧲 МРТ 3Т", "🖥 МСКТ 256", "🖥 МСКТ 128",
               "📡 УЗИ и другие", "🔬 Лаборатория", "⬅️ Назад"),
        "uz": ("🧲 МРТ 1.5Т", "🧲 МРТ 3Т", "🖥 МСКТ 256", "🖥 МСКТ 128",
               "📡 УЗИ ва бошқалар", "🔬 Laboratoriya", "⬅️ Orqaga"),
        "kz": ("🧲 МРТ 1.5Т", "🧲 МРТ 3Т", "🖥 МСКТ 256", "🖥 МСКТ 128",
               "📡 УДЗ және басқа", "🔬 Зертхана", "⬅️ Артқа"),
    }[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(labels[0], callback_data="diag_mrt15"),
         InlineKeyboardButton(labels[1], callback_data="diag_mrt3t")],
        [InlineKeyboardButton(labels[2], callback_data="diag_mskt256"),
         InlineKeyboardButton(labels[3], callback_data="diag_mskt128")],
        [InlineKeyboardButton(labels[4], callback_data="diag_other")],
        [InlineKeyboardButton(labels[5], callback_data="diag_lab")],
        [InlineKeyboardButton(labels[6], callback_data="back_main")],
    ])


def mrt3t_groups_keyboard(lang):
    back = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
    d = load_data()
    buttons = []
    for group in d["mrt_3t_groups"].keys():
        buttons.append([InlineKeyboardButton(f"📋 {group}", callback_data=f"mrt3t_{group}")])
    buttons.append([InlineKeyboardButton(back, callback_data="menu_diagnostics")])
    return InlineKeyboardMarkup(buttons)


def excursion_keyboard(lang):
    labels = {
        "ru": ("🏛 Самарканд", "🕌 Бухара", "⬅️ Назад"),
        "uz": ("🏛 Samarqand", "🕌 Buxoro", "⬅️ Orqaga"),
        "kz": ("🏛 Самарқанд", "🕌 Бұхара", "⬅️ Артқа"),
    }[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(labels[0], callback_data="excursion_samarkand")],
        [InlineKeyboardButton(labels[1], callback_data="excursion_bukhara")],
        [InlineKeyboardButton(labels[2], callback_data="back_main")],
    ])


# ─── SEND PHOTOS HELPER ───────────────────────────────────────────────────────

async def send_photos(context, chat_id, photo_ids, caption=""):
    if not photo_ids:
        return False
    sent = False
    for i, photo_id in enumerate(photo_ids[:10]):
        try:
            cap = caption if i == 0 else ""
            await context.bot.send_photo(chat_id=chat_id, photo=photo_id, caption=cap)
            sent = True
        except Exception as e:
            logger.error(f"Photo send error: {e}")
    return sent


# ─── HANDLERS ─────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Добро пожаловать / Xush kelibsiz / Қош келдіңіз!\n\n🌐 Выберите язык / Tilni tanlang / Тілді таңдаңыз:",
        reply_markup=lang_keyboard()
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    d = load_data()
    lang = get_lang(context)
    phone = d["contacts"]["phone1"]
    chat_id = query.message.chat_id

    # ── Til tanlash ──
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        context.user_data["lang"] = lang
        welcome = {
            "ru": "🏥 Клиника *Эргаш-Ота* — Каттакурган\n\nВыберите раздел:",
            "uz": "🏥 *Эргаш-Ота* klinikasi — Kattaqo'rg'on\n\nBo'limni tanlang:",
            "kz": "🏥 *Эргаш-Ота* клиникасы — Каттақурғон\n\nБөлімді таңдаңыз:",
        }[lang]
        await query.edit_message_text(welcome, parse_mode="Markdown",
                                      reply_markup=main_menu_keyboard(lang))

    # ── Orqaga ──
    elif data == "back_main":
        title = {
            "ru": "🏥 Клиника *Эргаш-Ота*\n\nВыберите раздел:",
            "uz": "🏥 *Эргаш-Ота* klinikasi\n\nBo'limni tanlang:",
            "kz": "🏥 *Эргаш-Ота* клиникасы\n\nБөлімді таңдаңыз:",
        }[lang]
        await query.edit_message_text(title, parse_mode="Markdown",
                                      reply_markup=main_menu_keyboard(lang))

    # ── Klinika haqida ──
    elif data == "menu_clinic":
        c = d["contacts"]
        addr = c[f"address_{lang}"]
        hours = c[f"work_hours_{lang}"]
        inc = d["included"][lang]
        text = {
            "ru": f"🏥 *Клиника Эргаш-Ота*\n\n📍 {addr}\n📞 {c['phone1']}\n📞 {c['phone2']}\n🕐 {hours}\n📸 {c['instagram']}\n🌐 {c['website']}\n\n{inc}",
            "uz": f"🏥 *Эргаш-Ота klinikasi*\n\n📍 {addr}\n📞 {c['phone1']}\n📞 {c['phone2']}\n🕐 {hours}\n📸 {c['instagram']}\n🌐 {c['website']}\n\n{inc}",
            "kz": f"🏥 *Эргаш-Ота клиникасы*\n\n📍 {addr}\n📞 {c['phone1']}\n📞 {c['phone2']}\n🕐 {hours}\n📸 {c['instagram']}\n🌐 {c['website']}\n\n{inc}",
        }[lang]
        await query.edit_message_text(text, parse_mode="Markdown",
                                      reply_markup=back_keyboard(lang))
        # Klinika rasmlari
        if d.get("clinic_photos"):
            await send_photos(context, chat_id, d["clinic_photos"])

    # ── Shifokor ──
    elif data == "menu_doctor":
        doc = d["doctor"]
        name = doc[f"name_{lang}"]
        title_text = doc[f"title_{lang}"]
        text = {
            "ru": f"👨‍⚕️ *Главный врач*\n\n🩺 {name}\n\n{title_text}",
            "uz": f"👨‍⚕️ *Bosh shifokor*\n\n🩺 {name}\n\n{title_text}",
            "kz": f"👨‍⚕️ *Бас дәрігер*\n\n🩺 {name}\n\n{title_text}",
        }[lang]
        if doc.get("photo_id"):
            await context.bot.send_photo(chat_id=chat_id, photo=doc["photo_id"], caption=text, parse_mode="Markdown")
            await query.edit_message_reply_markup(reply_markup=back_keyboard(lang))
        else:
            await query.edit_message_text(text, parse_mode="Markdown",
                                          reply_markup=back_keyboard(lang))

    # ── Jamoa ──
    elif data == "menu_staff":
        staff = d.get("staff", [])
        title = {"ru": "👥 *Наша команда:*", "uz": "👥 *Jamoamiz:*", "kz": "👥 *Біздің команда:*"}[lang]
        await query.edit_message_text(title, parse_mode="Markdown", reply_markup=back_keyboard(lang))
        for member in staff:
            text = f"👨‍⚕️ *{member['name']}*\n{member['role']}"
            if member.get("photo_id"):
                await context.bot.send_photo(chat_id=chat_id, photo=member["photo_id"], caption=text, parse_mode="Markdown")
            else:
                await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")

    # ── Kasalliklar ──
    elif data == "menu_diseases":
        diseases = d.get("diseases", [])
        title = {
            "ru": "🩺 *Список лечимых заболеваний:*\n\n",
            "uz": "🩺 *Davolanadigan kasalliklar ro'yxati:*\n\n",
            "kz": "🩺 *Емделетін аурулар тізімі:*\n\n",
        }[lang]
        # Bo'lib yuborish (uzun bo'lgani uchun)
        chunk = title
        for disease in diseases:
            if len(chunk) + len(disease) > 3800:
                await query.edit_message_text(chunk, parse_mode="Markdown")
                chunk = disease + "\n"
            else:
                chunk += disease + "\n"
        await query.edit_message_text(chunk, parse_mode="Markdown", reply_markup=back_keyboard(lang))

    # ── Palatalar ──
    elif data == "menu_wards":
        title = {
            "ru": "🏨 *Палаты клиники:*",
            "uz": "🏨 *Klinika palatalari:*",
            "kz": "🏨 *Клиника палаталары:*",
        }[lang]
        await query.edit_message_text(title, parse_mode="Markdown", reply_markup=back_keyboard(lang))
        photos = d.get("ward_photos", [])
        if photos:
            await send_photos(context, chat_id, photos)
        else:
            no_photo = {
                "ru": "📸 Фото палат скоро будут добавлены!",
                "uz": "📸 Palata rasmlari tez orada qo'shiladi!",
                "kz": "📸 Палата суреттері жақында қосылады!",
            }[lang]
            await context.bot.send_message(chat_id=chat_id, text=no_photo)

    # ── Xonalar ──
    elif data == "menu_rooms":
        title = {
            "ru": "🛏 Выберите категорию:",
            "uz": "🛏 Kategoriyani tanlang:",
            "kz": "🛏 Санатты таңдаңыз:",
        }[lang]
        await query.edit_message_text(title, reply_markup=rooms_keyboard(lang))

    elif data in ("rooms_uz", "rooms_foreign"):
        rooms = d["rooms_uz"] if data == "rooms_uz" else d["rooms_foreign"]
        flag = "🇺🇿" if data == "rooms_uz" else "🌍"
        header = {
            "ru": f"{flag} Стоимость за 1 день / 1 человек:\n_(взрослые / дети до 10 лет)_\n\n",
            "uz": f"{flag} 1 kun / 1 kishi narxi:\n_(kattalar / 10 yoshgacha bolalar)_\n\n",
            "kz": f"{flag} 1 күн / 1 адам бағасы:\n_(ересектер / 10 жасқа дейін)_\n\n",
        }[lang]
        lines = []
        for r in rooms:
            lines.append(f"🛏 *{r['name']}* ({r['people']} кіші) — {r['adult']} / {r['child']} сум")
        text = header + "\n".join(lines)
        if len(text) > 4000:
            text = text[:4000] + "..."
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard(lang))

    # ── Diagnostika ──
    elif data == "menu_diagnostics":
        title = {
            "ru": "🧲 Выберите вид диагностики:",
            "uz": "🧲 Diagnostika turini tanlang:",
            "kz": "🧲 Диагностика түрін таңдаңыз:",
        }[lang]
        await query.edit_message_text(title, reply_markup=diagnostics_keyboard(lang))

    elif data == "diag_mrt15":
        lines = "\n".join([f"• {x}" for x in d["mrt_15"]])
        title = {"ru": "🧲 *МРТ 1.5Т — цены:*", "uz": "🧲 *МРТ 1.5Т — narxlar:*", "kz": "🧲 *МРТ 1.5Т — бағалар:*"}[lang]
        await query.edit_message_text(f"{title}\n\n{lines}", parse_mode="Markdown", reply_markup=back_keyboard(lang))

    elif data == "diag_mrt3t":
        title = {"ru": "🧲 МРТ 3Т — выберите группу:", "uz": "🧲 МРТ 3Т — guruhni tanlang:", "kz": "🧲 МРТ 3Т — топты таңдаңыз:"}[lang]
        await query.edit_message_text(title, reply_markup=mrt3t_groups_keyboard(lang))

    elif data.startswith("mrt3t_"):
        group = data[6:]
        items = d["mrt_3t_groups"].get(group, [])
        lines = "\n".join([f"• {x}" for x in items])
        await query.edit_message_text(f"🧲 *МРТ 3Т — {group}:*\n\n{lines}",
                                      parse_mode="Markdown", reply_markup=back_keyboard(lang))

    elif data == "diag_mskt256":
        lines = "\n".join([f"• {x}" for x in d["mskt_256"]])
        title = {"ru": "🖥 *МСКТ 256 — цены:*", "uz": "🖥 *МСКТ 256 — narxlar:*", "kz": "🖥 *МСКТ 256 — бағалар:*"}[lang]
        await query.edit_message_text(f"{title}\n\n{lines}", parse_mode="Markdown", reply_markup=back_keyboard(lang))

    elif data == "diag_mskt128":
        lines = "\n".join([f"• {x}" for x in d["mskt_128"]])
        title = {"ru": "🖥 *МСКТ 128 — цены:*", "uz": "🖥 *МСКТ 128 — narxlar:*", "kz": "🖥 *МСКТ 128 — бағалар:*"}[lang]
        await query.edit_message_text(f"{title}\n\n{lines}", parse_mode="Markdown", reply_markup=back_keyboard(lang))

    elif data == "diag_other":
        lines = "\n".join([f"• {x}" for x in d["other_diagnostics"]])
        title = {"ru": "📡 *УЗИ и другие:*", "uz": "📡 *УЗИ va boshqalar:*", "kz": "📡 *УДЗ және басқалар:*"}[lang]
        await query.edit_message_text(f"{title}\n\n{lines}", parse_mode="Markdown", reply_markup=back_keyboard(lang))

    elif data == "diag_lab":
        lines = "\n".join([f"• {x}" for x in d["lab"]])
        title = {"ru": "🔬 *Лаборатория — цены:*", "uz": "🔬 *Laboratoriya — narxlar:*", "kz": "🔬 *Зертхана — бағалар:*"}[lang]
        await query.edit_message_text(f"{title}\n\n{lines}", parse_mode="Markdown", reply_markup=back_keyboard(lang))

    # ── Transfer ──
    elif data == "menu_transfer":
        text = d["transfer"][lang].format(phone=phone)
        await query.edit_message_text(text, reply_markup=back_keyboard(lang))

    # ── Ekskursiya ──
    elif data == "menu_excursion":
        title = {
            "ru": "🕌 Выберите направление:",
            "uz": "🕌 Yo'nalishni tanlang:",
            "kz": "🕌 Бағытты таңдаңыз:",
        }[lang]
        await query.edit_message_text(title, reply_markup=excursion_keyboard(lang))

    elif data == "excursion_samarkand":
        text = {
            "ru": f"🏛 *Самарканд*\n\n• 1 человек — 150 000 сум\n• Салон (группа) — 500 000 сум\n\n🗺 Маршрут:\n• Площадь Регистан\n• Шахи-Зинда\n• Мавзолей Тамерлана (Гур-Эмир)\n• Мечеть Биби-Ханум\n• Обсерватория Улугбека\n\n📞 Запись: {phone}",
            "uz": f"🏛 *Samarqand*\n\n• 1 kishi — 150 000 so'm\n• Salon (guruh) — 500 000 so'm\n\n🗺 Marshrut:\n• Registon maydoni\n• Shahi-Zinda\n• Temur maqbarasi (Gur-Amir)\n• Bibixonim masjidi\n• Ulug'bek rasadxonasi\n\n📞 Buyurtma: {phone}",
            "kz": f"🏛 *Самарқанд*\n\n• 1 адам — 150 000 сум\n• Салон (топ) — 500 000 сум\n\n📞 Тіркелу: {phone}",
        }[lang].format(phone=phone)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard(lang))
        if d.get("samarkand_photos"):
            await send_photos(context, chat_id, d["samarkand_photos"])

    elif data == "excursion_bukhara":
        text = {
            "ru": f"🕌 *Бухара*\n\n• 1 человек — 200 000 сум\n• Салон (группа) — 800 000 сум\n\n🗺 Маршрут:\n• Арк (крепость)\n• Боло-Хауз\n• Пои-Калон\n• Мавзолей Саманидов\n• Чор-Минор\n\n📞 Запись: {phone}",
            "uz": f"🕌 *Buxoro*\n\n• 1 kishi — 200 000 so'm\n• Salon (guruh) — 800 000 so'm\n\n🗺 Marshrut:\n• Ark (qal'a)\n• Bolo-Xovuz\n• Poi-Kalon\n• Somoniylar maqbarasi\n• Chor-Minor\n\n📞 Buyurtma: {phone}",
            "kz": f"🕌 *Бұхара*\n\n• 1 адам — 200 000 сум\n• Салон (топ) — 800 000 сум\n\n📞 Тіркелу: {phone}",
        }[lang].format(phone=phone)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard(lang))
        if d.get("bukhara_photos"):
            await send_photos(context, chat_id, d["bukhara_photos"])

    # ── Yakshanba ──
    elif data == "menu_weekend":
        text = d["weekend"][lang].format(phone=phone)
        await query.edit_message_text(text, reply_markup=back_keyboard(lang))

    # ── Operator ──
    elif data == "menu_operator":
        c = d["contacts"]
        text = {
            "ru": f"📞 *Свяжитесь с нами:*\n\n☎️ {c['phone1']}\n☎️ {c['phone2']}\n\n📸 Instagram: {c['instagram']}\n🌐 {c['website']}\n\nМы ответим в рабочее время!",
            "uz": f"📞 *Biz bilan bog'laning:*\n\n☎️ {c['phone1']}\n☎️ {c['phone2']}\n\n📸 Instagram: {c['instagram']}\n🌐 {c['website']}\n\nIsh vaqtida javob beramiz!",
            "kz": f"📞 *Бізбен байланысыңыз:*\n\n☎️ {c['phone1']}\n☎️ {c['phone2']}\n\n📸 Instagram: {c['instagram']}\n🌐 {c['website']}\n\nЖұмыс уақытында жауап береміз!",
        }[lang]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard(lang))


# ─── ADMIN PANEL ──────────────────────────────────────────────────────────────

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    text = update.message.text.strip()

    if text == "/admin_help":
        help_text = """🔧 *Admin buyruqlari:*

📝 *Matn o'zgartirish:*
`/admin contacts|phone1|+998901234567`
`/admin contacts|address_ru|Новый адрес`
`/admin transfer|ru|Yangi matn`
`/admin excursion|uz|Yangi matn`
`/admin doctor|name_ru|Yangi ism`

📸 *Rasm qo'shish:*
Rasmni menga yuboring, men file_id ni beraman
Keyin: `/admin_photo clinic` yoki `/admin_photo ward` yoki `/admin_photo samarkand` yoki `/admin_photo bukhara` yoki `/admin_photo doctor`

👥 *Jamoa a'zosi qo'shish:*
`/admin_staff_add Ism Familiya|Lavozim`

📋 *Bo'limlar:*
contacts, doctor, transfer, excursion, weekend, included"""
        await update.message.reply_text(help_text, parse_mode="Markdown")
        return

    if text.startswith("/admin_photo"):
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text("Format: /admin_photo clinic|ward|samarkand|bukhara|doctor")
            return
        context.user_data["waiting_photo"] = parts[1]
        await update.message.reply_text(f"✅ Endi rasmni yuboring — {parts[1]} uchun saqlanadi!")
        return

    if text.startswith("/admin_staff_add"):
        parts = text.replace("/admin_staff_add ", "").split("|")
        if len(parts) < 2:
            await update.message.reply_text("Format: /admin_staff_add Ism Familiya|Lavozim")
            return
        d = load_data()
        d["staff"].append({"name": parts[0], "role": parts[1], "photo_id": ""})
        save_data(d)
        await update.message.reply_text(f"✅ Qo'shildi: {parts[0]}")
        return

    if text.startswith("/admin"):
        parts = text.replace("/admin ", "").split("|")
        if len(parts) < 3:
            await update.message.reply_text("Format: /admin bo'lim|kalit|qiymat")
            return
        d = load_data()
        section, key, value = parts[0], parts[1], "|".join(parts[2:])
        if section in d and isinstance(d[section], dict) and key in d[section]:
            d[section][key] = value
            save_data(d)
            await update.message.reply_text(f"✅ Yangilandi: {section} → {key}")
        else:
            await update.message.reply_text(f"❌ Topilmadi: {section} → {key}")


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    waiting = context.user_data.get("waiting_photo")
    if not waiting:
        return

    photo = update.message.photo[-1]
    file_id = photo.file_id
    d = load_data()

    if waiting == "clinic":
        d["clinic_photos"].append(file_id)
        await update.message.reply_text(f"✅ Klinika rasmi qo'shildi! Jami: {len(d['clinic_photos'])} ta")
    elif waiting == "ward":
        d["ward_photos"].append(file_id)
        await update.message.reply_text(f"✅ Palata rasmi qo'shildi! Jami: {len(d['ward_photos'])} ta")
    elif waiting == "samarkand":
        d["samarkand_photos"].append(file_id)
        await update.message.reply_text(f"✅ Samarqand rasmi qo'shildi! Jami: {len(d['samarkand_photos'])} ta")
    elif waiting == "bukhara":
        d["bukhara_photos"].append(file_id)
        await update.message.reply_text(f"✅ Buxoro rasmi qo'shildi! Jami: {len(d['bukhara_photos'])} ta")
    elif waiting == "doctor":
        d["doctor"]["photo_id"] = file_id
        await update.message.reply_text("✅ Shifokor rasmi saqlandi!")
    elif waiting.startswith("staff_"):
        idx = int(waiting.split("_")[1])
        if idx < len(d["staff"]):
            d["staff"][idx]["photo_id"] = file_id
            await update.message.reply_text(f"✅ {d['staff'][idx]['name']} rasmi saqlandi!")

    save_data(d)
    context.user_data["waiting_photo"] = None


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    text = {
        "ru": "Используйте /start для начала",
        "uz": "Boshlash uchun /start ni bosing",
        "kz": "Бастау үшін /start пайдаланыңыз",
    }.get(lang, "Use /start")
    await update.message.reply_text(text)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_handler))
    app.add_handler(CommandHandler("admin_help", admin_handler))
    app.add_handler(CommandHandler("admin_photo", admin_handler))
    app.add_handler(CommandHandler("admin_staff_add", admin_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.PHOTO & filters.User(ADMIN_ID), photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
