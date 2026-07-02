import logging
import os
import json
import re
import asyncio
import datetime
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
OPERATOR_PHONE = os.getenv("OPERATOR_PHONE", "+998932264567")
# Railway Variables'ga: ALLOWED_STAFF=123456789,987654321 formatida kiriting
ALLOWED_STAFF = [int(x) for x in os.getenv("ALLOWED_STAFF", "").split(",") if x.strip().isdigit()]

# ── AI Administrator sozlamalari ──
AI_PROVIDER = os.getenv("AI_PROVIDER", "anthropic")  # "anthropic" yoki "openai"
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "claude-sonnet-4-6" if AI_PROVIDER == "anthropic" else "gpt-4o")
STATSIONAR_CHANNEL = int(os.getenv("STATSIONAR_CHANNEL", "-1003991204638"))
DIAGNOSTIKA_CHANNEL = int(os.getenv("DIAGNOSTIKA_CHANNEL", "-1003933653831"))
TRANSFER_CHANNEL = int(os.getenv("TRANSFER_CHANNEL", "-1003939453314"))
DATA_FILE = os.getenv("DATA_FILE", "/app/data/data.json")
AI_LOG_FILE = os.getenv("AI_LOG_FILE", "/app/data/ai_logs.json")
TASHKENT_TZ = datetime.timezone(datetime.timedelta(hours=5))
CLINIC_LATITUDE = 39.892639
CLINIC_LONGITUDE = 66.307028

DEFAULT_DATA = {
    "contacts": {
        "address_ru": "г. Каттакурган, массив Казак овул",
        "address_uz": "Kattaqo'rg'on sh., Qozoq ovul massivi",
        "address_kz": "Каттақурғон қ., Қазақ овул массиві",
        "phone1": "+998932264567",
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
        {"name": "Д/Урта миёна", "people": "3", "adult": "243 000", "child": "228 000"},
        {"name": "Д/Люкс", "people": "5", "adult": "420 000", "child": "405 000"},
        {"name": "Д/Люкс", "people": "3", "adult": "385 000", "child": "370 000"},
        {"name": "Д/Люкс", "people": "2", "adult": "495 000", "child": "480 000"},
        {"name": "С/Люкс", "people": "5", "adult": "420 000", "child": "405 000"},
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
        {"name": "Д/Стандарт", "people": "3", "adult": "317 000", "child": "300 000"},
        {"name": "С/Люкс", "people": "4", "adult": "420 000", "child": "405 000"},
        {"name": "М/Люкс", "people": "4-6", "adult": "420 000", "child": "405 000"},
        {"name": "М/Люкс АБ", "people": "2-3", "adult": "465 000", "child": "450 000"},
        {"name": "М/Люкс", "people": "2", "adult": "495 000", "child": "480 000"},
        {"name": "М/Стандарт", "people": "3-5", "adult": "313 000", "child": "298 000"},
        {"name": "М/VIP", "people": "2", "adult": "699 000", "child": "684 000"},
        {"name": "М/VIP", "people": "1", "adult": "760 000", "child": "745 000"},
    ],
    "clinic_history": {
        "ru": "📖 *История клиники Эргаш-Ота*\n\nКлиника основана врачом высшей категории, академиком Бердикулом Эргашевым Журакуловичем.\n\nЗа годы работы клиника помогла тысячам пациентов из Узбекистана, Казахстана, Кыргызстана и других стран.\n\nСегодня клиника оснащена современным оборудованием: МРТ 1.5Т и 3Т, МСКТ 256 срезов, и многим другим.",
        "uz": "📖 *Эргаш-Ота klinikasi tarixi*\n\nKlinika oliy toifali shifokor, akademik Berdiqul Ergashev Jo'raqulovich tomonidan tashkil etilgan.\n\nFaoliyat yillari davomida klinika O'zbekiston, Qozog'iston, Qirg'iziston va boshqa mamlakatlardan minglab bemorlarga yordam berdi.\n\nBugun klinika zamonaviy uskunalar bilan jihozlangan: МРТ 1.5Т va 3Т, МСКТ 256 qism va boshqalar.",
        "kz": "📖 *Эргаш-Ота клиникасының тарихы*\n\nКлиника жоғары санатты дәрігер, академик Бердіқұл Ерғашев Жўрақұлович тарапынан құрылған.\n\nЖылдар бойы клиника мыңдаған науқастарға көмек берді.",
    },
    "clinic_certs": {
        "ru": "📜 *Сертификаты и лицензии*\n\n✅ Лицензия на медицинскую деятельность\n✅ Сертификаты специалистов\n✅ Международные стандарты качества",
        "uz": "📜 *Sertifikatlar va litsenziyalar*\n\n✅ Tibbiy faoliyat litsenziyasi\n✅ Mutaxassislar sertifikatlari\n✅ Xalqaro sifat standartlari",
        "kz": "📜 *Сертификаттар мен лицензиялар*\n\n✅ Медициналық қызмет лицензиясы\n✅ Маман сертификаттары\n✅ Халықаралық сапа стандарттары",
    },
    "clinic_videos": [],
    "cert_photos": [],
    "ward_photos": [],
    "clinic_photos": [],
    "team_photos": [],
    "korpuslar": [
        {
            "id": "umumiy_z",
            "name_uz": "Umumiy + Z Korpus",
            "name_ru": "Общий + Z корпус",
            "emoji": "🏠",
            "photos": [],
            "xonalar": [
                {"nom": "Umumiy", "kishi": "10", "uz_adult": "185 000", "uz_child": "172 000", "foreign_adult": "308 000", "foreign_child": "293 000", "photos": [],
                 "description_uz": "🛏 *Umumiy (Obshiy) xona sharoitlari*\n\n• 🏢 *Korpus:* Asosiy korpus\n• 👥 *Sig'imi:* 10 kishi uchun mo'ljallangan\n\n⚙️ *Xonada mavjud qulayliklar:*\n✅ 10 ta alohida qulay krovat\n✅ Har bir bemor uchun alohida tumba\n✅ Kiyimlar uchun kiyim osgich (veshalka)\n✅ Oyoq kiyimlar uchun maxsus stelaj\n✅ Yuqori tezlikdagi Wi-Fi hududi\n✅ Dam olish va hordiq chiqarish uchun televizor\n\n☀️ *Isitish va sovitish tizimi:* Xonada qishki isitish tizimi to'liq mavjud (Yozgi konditsioner tizimi mavjud emas).\n\n🛁 *Yuvinish va gigiyena xonasi:* Dush va hojatxonalar (tualet) Umumiy tashqarida.",
                 "description_ru": "🛏 *Условия общей палаты*\n\n• 🏢 *Корпус:* Главный корпус\n• 👥 *Вместимость:* рассчитана на 10 человек\n\n⚙️ *Удобства в палате:*\n✅ 10 отдельных удобных кроватей\n✅ Тумбочка для каждого пациента\n✅ Вешалка для одежды\n✅ Стеллаж для обуви\n✅ Высокоскоростной Wi-Fi\n✅ Телевизор для отдыха\n\n☀️ *Отопление и охлаждение:* Зимнее отопление полностью есть (летнего кондиционера нет).\n\n🛁 *Санузел:* Душ и туалет — общие, находятся снаружи.",
                 "description_kz": "🛏 *Жалпы палата жағдайлары*\n\n• 🏢 *Корпус:* Бас корпус\n• 👥 *Сыйымдылығы:* 10 адамға арналған\n\n⚙️ *Палатадағы қолайлықтар:*\n✅ 10 жеке ыңғайлы кереует\n✅ Әр науқасқа жеке тумба\n✅ Киім ілгіш\n✅ Аяқ киімге арналған стеллаж\n✅ Жоғары жылдамдықты Wi-Fi\n✅ Теледидар\n\n☀️ *Жылыту:* Қысқы жылыту толық бар (жазғы кондиционер жоқ).\n\n🛁 *Санторап:* Душ және дәретхана — жалпы, сыртта."},
                {"nom": "Urta miyona", "kishi": "2-3", "uz_adult": "224 000", "uz_child": "209 000", "foreign_adult": "317 000", "foreign_child": "300 000", "photos": [],
                 "description_uz": "🛏 *Urta miyona xona sharoitlari*\n\n• 🏢 *Korpus:* Asosiy korpus\n• 👥 *Sig'imi:* 2-3 kishi uchun mo'ljallangan\n\n⚙️ *Xonada mavjud qulayliklar:*\n✅ 3 ta alohida qulay krovat\n✅ Har bir bemor uchun alohida tumba\n✅ Kiyimlar uchun kiyim osgich yoki Shkaf\n✅ Oyoq kiyimlar uchun maxsus stelaj\n✅ Yuqori tezlikdagi Wi-Fi hududi\n✅ Dam olish va hordiq chiqarish uchun televizor\n\n☀️ *Isitish va sovitish tizimi:* Xonada qishki isitish tizimi to'liq mavjud (Yozgi konditsioner tizimi mavjud emas).\n\n🛁 *Yuvinish va gigiyena xonasi:* Dush va hojatxonalar (tualet) Umumiy tashqarida.",
                 "description_ru": "🛏 *Условия палаты «Среднего» класса*\n\n• 🏢 *Корпус:* Главный корпус\n• 👥 *Вместимость:* 2-3 человека\n\n⚙️ *Удобства в палате:*\n✅ 3 отдельные удобные кровати\n✅ Тумбочка для каждого пациента\n✅ Вешалка или шкаф для одежды\n✅ Стеллаж для обуви\n✅ Высокоскоростной Wi-Fi\n✅ Телевизор для отдыха\n\n☀️ *Отопление и охлаждение:* Зимнее отопление полностью есть (летнего кондиционера нет).\n\n🛁 *Санузел:* Душ и туалет — общие, находятся снаружи.",
                 "description_kz": "🛏 *Орта деңгейлі палата жағдайлары*\n\n• 🏢 *Корпус:* Бас корпус\n• 👥 *Сыйымдылығы:* 2-3 адам\n\n⚙️ *Палатадағы қолайлықтар:*\n✅ 3 жеке ыңғайлы кереует\n✅ Әр науқасқа жеке тумба\n✅ Киім ілгіш немесе шкаф\n✅ Аяқ киімге арналған стеллаж\n✅ Жоғары жылдамдықты Wi-Fi\n✅ Теледидар\n\n☀️ *Жылыту:* Қысқы жылыту толық бар (жазғы кондиционер жоқ).\n\n🛁 *Санторап:* Душ және дәретхана — жалпы, сыртта."},
                {"nom": "Urta miyona", "kishi": "4-5", "uz_adult": "213 000", "uz_child": "198 000", "foreign_adult": "308 000", "foreign_child": "293 000", "photos": [],
                 "description_uz": "🛏 *Urta miyona xona sharoitlari*\n\n• 🏢 *Korpus:* Asosiy korpus\n• 👥 *Sig'imi:* 4-5 kishi uchun mo'ljallangan\n\n⚙️ *Xonada mavjud qulayliklar:*\n✅ 4-5 ta alohida qulay krovat\n✅ Har bir bemor uchun alohida tumba\n✅ Kiyimlar uchun kiyim osgich yoki Shkaf\n✅ Oyoq kiyimlar uchun maxsus stelaj\n✅ Yuqori tezlikdagi Wi-Fi hududi\n✅ Dam olish va hordiq chiqarish uchun televizor\n\n☀️ *Isitish va sovitish tizimi:* Xonada qishki isitish tizimi to'liq mavjud (Yozgi konditsioner tizimi mavjud emas).\n\n🛁 *Yuvinish va gigiyena xonasi:* Dush va hojatxonalar (tualet) Umumiy tashqarida.",
                 "description_ru": "🛏 *Условия палаты «Среднего» класса*\n\n• 🏢 *Корпус:* Главный корпус\n• 👥 *Вместимость:* 4-5 человек\n\n⚙️ *Удобства в палате:*\n✅ 4-5 отдельных удобных кроватей\n✅ Тумбочка для каждого пациента\n✅ Вешалка или шкаф для одежды\n✅ Стеллаж для обуви\n✅ Высокоскоростной Wi-Fi\n✅ Телевизор для отдыха\n\n☀️ *Отопление и охлаждение:* Зимнее отопление полностью есть (летнего кондиционера нет).\n\n🛁 *Санузел:* Душ и туалет — общие, находятся снаружи.",
                 "description_kz": "🛏 *Орта деңгейлі палата жағдайлары*\n\n• 🏢 *Корпус:* Бас корпус\n• 👥 *Сыйымдылығы:* 4-5 адам\n\n⚙️ *Палатадағы қолайлықтар:*\n✅ 4-5 жеке ыңғайлы кереует\n✅ Әр науқасқа жеке тумба\n✅ Киім ілгіш немесе шкаф\n✅ Аяқ киімге арналған стеллаж\n✅ Жоғары жылдамдықты Wi-Fi\n✅ Теледидар\n\n☀️ *Жылыту:* Қысқы жылыту толық бар (жазғы кондиционер жоқ).\n\n🛁 *Санторап:* Душ және дәретхана — жалпы, сыртта."},
                {"nom": "Z/Urta miyona", "kishi": "2", "uz_adult": "269 000", "uz_child": "254 000", "foreign_adult": "354 000", "foreign_child": "339 000", "photos": [],
                 "description_uz": "🛏 *Z/Urta miyona xona sharoitlari*\n\n• 🏢 *Korpus:* Z korpus\n• 👥 *Sig'imi:* 2 kishi uchun mo'ljallangan\n\n⚙️ *Xonada mavjud qulayliklar:*\n✅ 2 ta alohida qulay krovat\n✅ Har bir bemor uchun alohida tumba\n✅ Kiyimlar uchun Shkaf\n✅ Oyoq kiyimlar uchun maxsus stelaj\n✅ Ish stol va stuli bilan\n✅ Yuqori tezlikdagi Wi-Fi hududi\n✅ Dam olish va hordiq chiqarish uchun televizor\n\n☀️ *Isitish va sovitish tizimi:* Xonada qishki isitish tizimi to'liq mavjud (Yozgi konditsioner tizimi mavjud emas).\n\n🛁 *Yuvinish va gigiyena xonasi:* Dush va hojatxonalar (tualet) Umumiy xonadan tashqarida.",
                 "description_ru": "🛏 *Условия палаты Z/Средний*\n\n• 🏢 *Корпус:* Z корпус\n• 👥 *Вместимость:* 2 человека\n\n⚙️ *Удобства в палате:*\n✅ 2 отдельные удобные кровати\n✅ Тумбочка для каждого пациента\n✅ Шкаф для одежды\n✅ Стеллаж для обуви\n✅ Рабочий стол со стулом\n✅ Высокоскоростной Wi-Fi\n✅ Телевизор для отдыха\n\n☀️ *Отопление и охлаждение:* Зимнее отопление полностью есть (летнего кондиционера нет).\n\n🛁 *Санузел:* Душ и туалет находятся снаружи общей палаты.",
                 "description_kz": "🛏 *Z/Орта деңгейлі палата жағдайлары*\n\n• 🏢 *Корпус:* Z корпусы\n• 👥 *Сыйымдылығы:* 2 адам\n\n⚙️ *Палатадағы қолайлықтар:*\n✅ 2 жеке ыңғайлы кереует\n✅ Әр науқасқа жеке тумба\n✅ Киім шкафы\n✅ Аяқ киімге арналған стеллаж\n✅ Жұмыс үстелі мен орындығы\n✅ Жоғары жылдамдықты Wi-Fi\n✅ Теледидар\n\n☀️ *Жылыту:* Қысқы жылыту толық бар (жазғы кондиционер жоқ).\n\n🛁 *Санторап:* Душ және дәретхана жалпы палатадан тыс орналасқан."},
                {"nom": "Z/Urta miyona", "kishi": "4-5", "uz_adult": "249 000", "uz_child": "234 000", "foreign_adult": "338 000", "foreign_child": "323 000", "photos": [],
                 "description_uz": "🛏 *Z/Urta miyona xona sharoitlari*\n\n• 🏢 *Korpus:* Z korpus\n• 👥 *Sig'imi:* 5 kishi uchun mo'ljallangan\n\n⚙️ *Xonada mavjud qulayliklar:*\n✅ 5 ta alohida qulay krovat\n✅ Har bir bemor uchun alohida tumba\n✅ Kiyimlar uchun Shkaf\n✅ Oyoq kiyimlar uchun maxsus stelaj\n✅ Ish stol va stuli bilan\n✅ Yuqori tezlikdagi Wi-Fi hududi\n✅ Dam olish va hordiq chiqarish uchun televizor\n\n☀️ *Isitish va sovitish tizimi:* Xonada qishki isitish tizimi to'liq mavjud (Yozgi konditsioner tizimi mavjud emas).\n\n🛁 *Yuvinish va gigiyena xonasi:* Dush va hojatxonalar (tualet) Umumiy xonadan tashqarida.",
                 "description_ru": "🛏 *Условия палаты Z/Средний*\n\n• 🏢 *Корпус:* Z корпус\n• 👥 *Вместимость:* 5 человек\n\n⚙️ *Удобства в палате:*\n✅ 5 отдельных удобных кроватей\n✅ Тумбочка для каждого пациента\n✅ Шкаф для одежды\n✅ Стеллаж для обуви\n✅ Рабочий стол со стулом\n✅ Высокоскоростной Wi-Fi\n✅ Телевизор для отдыха\n\n☀️ *Отопление и охлаждение:* Зимнее отопление полностью есть (летнего кондиционера нет).\n\n🛁 *Санузел:* Душ и туалет находятся снаружи общей палаты.",
                 "description_kz": "🛏 *Z/Орта деңгейлі палата жағдайлары*\n\n• 🏢 *Корпус:* Z корпусы\n• 👥 *Сыйымдылығы:* 5 адам\n\n⚙️ *Палатадағы қолайлықтар:*\n✅ 5 жеке ыңғайлы кереует\n✅ Әр науқасқа жеке тумба\n✅ Киім шкафы\n✅ Аяқ киімге арналған стеллаж\n✅ Жұмыс үстелі мен орындығы\n✅ Жоғары жылдамдықты Wi-Fi\n✅ Теледидар\n\n☀️ *Жылыту:* Қысқы жылыту толық бар (жазғы кондиционер жоқ).\n\n🛁 *Санторап:* Душ және дәретхана жалпы палатадан тыс орналасқан."},
            ]
        },
        {
            "id": "pol_lyuks",
            "name_uz": "Pol/Lyuks + Lyuks Korpus",
            "name_ru": "Пол/Люкс + Люкс корпус",
            "emoji": "⭐",
            "photos": [],
            "xonalar": [
                {"nom": "Pol/Lyuks", "kishi": "5-7", "uz_adult": "295 000", "uz_child": "280 000", "foreign_adult": "365 000", "foreign_child": "350 000", "photos": [],
                 "description_uz": "🛏 *Pol/Lyuks (5-7 kishi) xona sharoitlari*\n\n• 🏢 *Korpus:* Asosiy\n• 👥 *Sig'imi:* 5-7 kishi uchun mo'ljallangan\n\n⚙️ *Xonaning ichida mavjud qulayliklar:*\n✅ 5 yoki 7 kishi uchun alohida krovatlar\n✅ Har bir bemor uchun shaxsiy tumba\n✅ Kiyimlarni tartibli saqlash uchun keng kiyim shkafi\n✅ Yuqori tezlikdagi Wi-Fi hududi\n✅ Hordiq chiqarish uchun televizor\n\n☀️ *Isitish va sovitish tizimi:* Xonada qishki isitish tizimi to'liq mavjud (Yozgi konditsioner tizimi mavjud emas).\n\n🛁 *Shaxsiy gigiyena va qulaylik (Xona ichida):*\n✅ Zamonaviy dush xonasi\n✅ Shaxsiy hojatxona (tualet)\n✅ Yuvinish uchun qulay rakovina",
                 "description_ru": "🛏 *Условия палаты Пол/Люкс (5-7 человек)*\n\n• 🏢 *Корпус:* Главный\n• 👥 *Вместимость:* 5-7 человек\n\n⚙️ *Удобства внутри палаты:*\n✅ Отдельные кровати для 5 или 7 человек\n✅ Личная тумбочка для каждого пациента\n✅ Просторный шкаф для одежды\n✅ Высокоскоростной Wi-Fi\n✅ Телевизор для отдыха\n\n☀️ *Отопление и охлаждение:* Зимнее отопление полностью есть (летнего кондиционера нет).\n\n🛁 *Личная гигиена и удобства (внутри палаты):*\n✅ Современный душ\n✅ Личный туалет\n✅ Удобная раковина для умывания",
                 "description_kz": "🛏 *Пол/Люкс (5-7 адам) палата жағдайлары*\n\n• 🏢 *Корпус:* Бас корпус\n• 👥 *Сыйымдылығы:* 5-7 адам\n\n⚙️ *Палата ішіндегі қолайлықтар:*\n✅ 5 немесе 7 адамға жеке кереуеттер\n✅ Әр науқасқа жеке тумба\n✅ Кең киім шкафы\n✅ Жоғары жылдамдықты Wi-Fi\n✅ Теледидар\n\n☀️ *Жылыту:* Қысқы жылыту толық бар (жазғы кондиционер жоқ).\n\n🛁 *Жеке гигиена және қолайлық (палата ішінде):*\n✅ Заманауи душ бөлмесі\n✅ Жеке дәретхана\n✅ Ыңғайлы раковина"},
                {"nom": "Pol/Lyuks", "kishi": "4", "uz_adult": "314 000", "uz_child": "299 000", "foreign_adult": "385 000", "foreign_child": "370 000", "photos": [],
                 "description_uz": "🛏 *Pol/Lyuks (4 kishi) xona sharoitlari*\n\n• 🏢 *Korpus:* Asosiy\n• 👥 *Sig'imi:* 4 kishi uchun mo'ljallangan\n\n⚙️ *Xonaning ichida mavjud qulayliklar:*\n✅ 4 ta alohida qulay krovat\n✅ Har bir bemor uchun shaxsiy tumba\n✅ Kiyimlarni tartibli saqlash uchun keng shkaf\n✅ Yuqori tezlikdagi Wi-Fi hududi\n✅ Hordiq chiqarish uchun televizor\n\n☀️ *Isitish va sovitish tizimi:* Xonada qishki isitish tizimi to'liq mavjud (Yozgi konditsioner tizimi mavjud emas).\n\n🛁 *Shaxsiy gigiyena va qulaylik (Xona ichida):*\n✅ Zamonaviy dush xonasi\n✅ Shaxsiy hojatxona (tualet)\n✅ Yuvinish uchun qulay rakovina",
                 "description_ru": "🛏 *Условия палаты Пол/Люкс (4 человека)*\n\n• 🏢 *Корпус:* Главный\n• 👥 *Вместимость:* 4 человека\n\n⚙️ *Удобства внутри палаты:*\n✅ 4 отдельные удобные кровати\n✅ Личная тумбочка для каждого пациента\n✅ Просторный шкаф для одежды\n✅ Высокоскоростной Wi-Fi\n✅ Телевизор для отдыха\n\n☀️ *Отопление и охлаждение:* Зимнее отопление полностью есть (летнего кондиционера нет).\n\n🛁 *Личная гигиена и удобства (внутри палаты):*\n✅ Современный душ\n✅ Личный туалет\n✅ Удобная раковина для умывания",
                 "description_kz": "🛏 *Пол/Люкс (4 адам) палата жағдайлары*\n\n• 🏢 *Корпус:* Бас корпус\n• 👥 *Сыйымдылығы:* 4 адам\n\n⚙️ *Палата ішіндегі қолайлықтар:*\n✅ 4 жеке ыңғайлы кереует\n✅ Әр науқасқа жеке тумба\n✅ Кең шкаф\n✅ Жоғары жылдамдықты Wi-Fi\n✅ Теледидар\n\n☀️ *Жылыту:* Қысқы жылыту толық бар (жазғы кондиционер жоқ).\n\n🛁 *Жеке гигиена және қолайлық (палата ішінде):*\n✅ Заманауи душ бөлмесі\n✅ Жеке дәретхана\n✅ Ыңғайлы раковина"},
                {"nom": "Lyuks", "kishi": "3", "uz_adult": "340 000", "uz_child": "325 000", "foreign_adult": "395 000", "foreign_child": "380 000", "photos": [],
                 "description_uz": "🛏 *Lyuks (3 kishi) xona sharoitlari*\n\n• 🏢 *Korpus:* Asosiy\n• 👥 *Sig'imi:* 3 kishi uchun mo'ljallangan\n\n⚙️ *Xonaning ichida mavjud qulayliklar:*\n✅ 3 ta alohida qulay krovat\n✅ Har bir bemor uchun shaxsiy tumba\n✅ Kiyimlarni tartibli saqlash uchun keng shkaf\n✅ Yuqori tezlikdagi Wi-Fi hududi\n✅ Hordiq chiqarish uchun televizor\n\n☀️ *Isitish va sovitish tizimi:* Xonada qishki isitish tizimi to'liq mavjud (Yozgi konditsioner tizimi mavjud emas).\n\n🛁 *Shaxsiy gigiyena va qulaylik (Xona ichida):*\n✅ Zamonaviy dush xonasi\n✅ Shaxsiy hojatxona (tualet)\n✅ Yuvinish uchun qulay rakovina",
                 "description_ru": "🛏 *Условия палаты Люкс (3 человека)*\n\n• 🏢 *Корпус:* Главный\n• 👥 *Вместимость:* 3 человека\n\n⚙️ *Удобства внутри палаты:*\n✅ 3 отдельные удобные кровати\n✅ Личная тумбочка для каждого пациента\n✅ Просторный шкаф для одежды\n✅ Высокоскоростной Wi-Fi\n✅ Телевизор для отдыха\n\n☀️ *Отопление и охлаждение:* Зимнее отопление полностью есть (летнего кондиционера нет).\n\n🛁 *Личная гигиена и удобства (внутри палаты):*\n✅ Современный душ\n✅ Личный туалет\n✅ Удобная раковина для умывания",
                 "description_kz": "🛏 *Люкс (3 адам) палата жағдайлары*\n\n• 🏢 *Корпус:* Бас корпус\n• 👥 *Сыйымдылығы:* 3 адам\n\n⚙️ *Палата ішіндегі қолайлықтар:*\n✅ 3 жеке ыңғайлы кереует\n✅ Әр науқасқа жеке тумба\n✅ Кең шкаф\n✅ Жоғары жылдамдықты Wi-Fi\n✅ Теледидар\n\n☀️ *Жылыту:* Қысқы жылыту толық бар (жазғы кондиционер жоқ).\n\n🛁 *Жеке гигиена және қолайлық (палата ішінде):*\n✅ Заманауи душ бөлмесі\n✅ Жеке дәретхана\n✅ Ыңғайлы раковина"},
                {"nom": "Lyuks", "kishi": "2", "uz_adult": "410 000", "uz_child": "395 000", "foreign_adult": "410 000", "foreign_child": "395 000", "photos": [],
                 "description_uz": "🛏 *Lyuks (2 kishi) xona sharoitlari*\n\n• 🏢 *Korpus:* Asosiy\n• 👥 *Sig'imi:* 2 kishi uchun mo'ljallangan\n\n⚙️ *Xonaning ichida mavjud qulayliklar:*\n✅ 2 ta alohida qulay krovat\n✅ Har bir bemor uchun shaxsiy tumba\n✅ Kiyimlarni tartibli saqlash uchun keng shkaf\n✅ Yuqori tezlikdagi Wi-Fi hududi\n✅ Hordiq chiqarish uchun televizor\n\n☀️ *Isitish va sovitish tizimi:* Xonada qishki isitish tizimi to'liq mavjud.\n\n🛁 *Shaxsiy gigiyena va qulaylik (Xona ichida):*\n✅ Zamonaviy dush xonasi\n✅ Shaxsiy hojatxona (tualet)\n✅ Yuvinish uchun qulay rakovina",
                 "description_ru": "🛏 *Условия палаты Люкс (2 человека)*\n\n• 🏢 *Корпус:* Главный\n• 👥 *Вместимость:* 2 человека\n\n⚙️ *Удобства внутри палаты:*\n✅ 2 отдельные удобные кровати\n✅ Личная тумбочка для каждого пациента\n✅ Просторный шкаф для одежды\n✅ Высокоскоростной Wi-Fi\n✅ Телевизор для отдыха\n\n☀️ *Отопление:* Зимнее отопление полностью есть.\n\n🛁 *Личная гигиена и удобства (внутри палаты):*\n✅ Современный душ\n✅ Личный туалет\n✅ Удобная раковина для умывания",
                 "description_kz": "🛏 *Люкс (2 адам) палата жағдайлары*\n\n• 🏢 *Корпус:* Бас корпус\n• 👥 *Сыйымдылығы:* 2 адам\n\n⚙️ *Палата ішіндегі қолайлықтар:*\n✅ 2 жеке ыңғайлы кереует\n✅ Әр науқасқа жеке тумба\n✅ Кең шкаф\n✅ Жоғары жылдамдықты Wi-Fi\n✅ Теледидар\n\n☀️ *Жылыту:* Қысқы жылыту толық бар.\n\n🛁 *Жеке гигиена және қолайлық (палата ішінде):*\n✅ Заманауи душ бөлмесі\n✅ Жеке дәретхана\n✅ Ыңғайлы раковина"},
            ]
        },
        {
            "id": "d_diagnostika",
            "name_uz": "D Korpus",
            "name_ru": "Д корпус",
            "emoji": "🔬",
            "photos": [],
            "xonalar": [
                {"nom": "D/Urta miyona", "kishi": "3", "uz_adult": "243 000", "uz_child": "228 000", "foreign_adult": "317 000", "foreign_child": "300 000", "photos": [],
                 "description_uz": "🛏 *D/Urta miyona (3 kishi) xona sharoitlari*\n\n• 🏢 *Korpus:* Diagnostika\n• 👥 *Sig'imi:* 3 kishi uchun mo'ljallangan\n\n⚙️ *Xonaning ichida mavjud qulayliklar:*\n✅ 3 ta alohida qulay krovat\n✅ Har bir bemor uchun shaxsiy tumba\n✅ Kiyimlarni tartibli saqlash uchun keng shkaf\n✅ Yuqori tezlikdagi Wi-Fi hududi\n✅ Hordiq chiqarish uchun televizor\n\n☀️ *Isitish va sovitish tizimi:* Xonada qishki isitish tizimi to'liq mavjud (Yozgi konditsioner tizimi mavjud emas).\n\n🛁 *Shaxsiy gigiyena va qulaylik (Xona ichida):*\n✅ Yuvinish uchun qulay rakovina",
                 "description_ru": "🛏 *Условия палаты Д/Средний (3 человека)*\n\n• 🏢 *Корпус:* Диагностика\n• 👥 *Вместимость:* 3 человека\n\n⚙️ *Удобства внутри палаты:*\n✅ 3 отдельные удобные кровати\n✅ Личная тумбочка для каждого пациента\n✅ Просторный шкаф для одежды\n✅ Высокоскоростной Wi-Fi\n✅ Телевизор для отдыха\n\n☀️ *Отопление и охлаждение:* Зимнее отопление полностью есть (летнего кондиционера нет).\n\n🛁 *Личная гигиена и удобства (внутри палаты):*\n✅ Удобная раковина для умывания",
                 "description_kz": "🛏 *Д/Орта деңгейлі (3 адам) палата жағдайлары*\n\n• 🏢 *Корпус:* Диагностика\n• 👥 *Сыйымдылығы:* 3 адам\n\n⚙️ *Палата ішіндегі қолайлықтар:*\n✅ 3 жеке ыңғайлы кереует\n✅ Әр науқасқа жеке тумба\n✅ Кең шкаф\n✅ Жоғары жылдамдықты Wi-Fi\n✅ Теледидар\n\n☀️ *Жылыту:* Қысқы жылыту толық бар (жазғы кондиционер жоқ).\n\n🛁 *Жеке гигиена және қолайлық (палата ішінде):*\n✅ Ыңғайлы раковина"},
                {"nom": "D/Lyuks", "kishi": "5", "uz_adult": "420 000", "uz_child": "405 000", "foreign_adult": "420 000", "foreign_child": "405 000", "photos": [],
                 "description_uz": "🛏 *D/Lyuks (5 kishi)*\n\n• 🏢 *Korpus:* Diagnostika\n• 👥 *Sig'imi:* 5 kishi\n\n⚙️ *Qulayliklar:*\n✅ 5 ta krovat\n✅ Shaxsiy tumba\n✅ Shkaf\n✅ Ish stoli va stuli\n✅ Wi-Fi\n✅ Televizor\n\n☀️ *Isitish va sovitish:* Qishki isitish + Yozgi konditsioner mavjud.\n\n🛁 *Xona ichida:*\n✅ Dush\n✅ Hojatxona (tualet)\n✅ Rakovina",
                 "description_ru": "🛏 *Д/Люкс (5 человек)*\n\n• 🏢 *Корпус:* Диагностика\n• 👥 *Вместимость:* 5 человек\n\n⚙️ *Удобства:*\n✅ 5 кроватей\n✅ Тумбочка\n✅ Шкаф\n✅ Рабочий стол и стул\n✅ Wi-Fi\n✅ Телевизор\n\n☀️ *Климат:* Отопление + кондиционер.\n\n🛁 *Внутри палаты:*\n✅ Душ\n✅ Туалет\n✅ Раковина",
                 "description_kz": "🛏 *Д/Люкс (5 адам)*\n\n• 🏢 *Корпус:* Диагностика\n• 👥 *Сыйымдылығы:* 5 адам\n\n⚙️ *Қолайлықтар:*\n✅ 5 кереует\n✅ Тумба\n✅ Шкаф\n✅ Үстел мен орындық\n✅ Wi-Fi\n✅ Теледидар\n\n☀️ *Климат:* Жылыту + кондиционер.\n\n🛁 *Палата ішінде:*\n✅ Душ\n✅ Дәретхана\n✅ Раковина"},
                {"nom": "D/Lyuks", "kishi": "2", "uz_adult": "495 000", "uz_child": "480 000", "foreign_adult": "495 000", "foreign_child": "480 000", "photos": [],
                 "description_uz": "🛏 *D/Lyuks (2 kishi)*\n\n• 🏢 *Korpus:* Diagnostika\n• 👥 *Sig'imi:* 2 kishi\n\n⚙️ *Qulayliklar:*\n✅ 2 ta krovat\n✅ Shaxsiy tumba\n✅ Shkaf\n✅ Ish stoli va stuli\n✅ Wi-Fi\n✅ Televizor\n\n☀️ *Isitish va sovitish:* Qishki isitish + Yozgi konditsioner mavjud.\n\n🛁 *Xona ichida:*\n✅ Dush\n✅ Hojatxona (tualet)\n✅ Rakovina",
                 "description_ru": "🛏 *Д/Люкс (2 человека)*\n\n• 🏢 *Корпус:* Диагностика\n• 👥 *Вместимость:* 2 человека\n\n⚙️ *Удобства:*\n✅ 2 кровати\n✅ Тумбочка\n✅ Шкаф\n✅ Рабочий стол и стул\n✅ Wi-Fi\n✅ Телевизор\n\n☀️ *Климат:* Отопление + кондиционер.\n\n🛁 *Внутри палаты:*\n✅ Душ\n✅ Туалет\n✅ Раковина",
                 "description_kz": "🛏 *Д/Люкс (2 адам)*\n\n• 🏢 *Корпус:* Диагностика\n• 👥 *Сыйымдылығы:* 2 адам\n\n⚙️ *Қолайлықтар:*\n✅ 2 кереует\n✅ Тумба\n✅ Шкаф\n✅ Үстел мен орындық\n✅ Wi-Fi\n✅ Теледидар\n\n☀️ *Климат:* Жылыту + кондиционер.\n\n🛁 *Палата ішінде:*\n✅ Душ\n✅ Дәретхана\n✅ Раковина"},
            ]
        },
        {
            "id": "s_korpus",
            "name_uz": "S Korpus",
            "name_ru": "С корпус",
            "emoji": "🏨",
            "photos": [],
            "xonalar": [
                {"nom": "S/Lyuks", "kishi": "4", "uz_adult": "420 000", "uz_child": "405 000", "foreign_adult": "420 000", "foreign_child": "405 000", "photos": [],
                 "description_uz": "🛏 *S/Lyuks (4 kishi)*\n\n• 🏢 *Korpus:* S Korpus\n• 👥 *Sig'imi:* 4 kishi\n\n⚙️ *Qulayliklar:*\n✅ 4 ta krovat\n✅ Shaxsiy tumba\n✅ Shkaf\n✅ Ish stoli va stuli\n✅ Wi-Fi\n✅ Televizor\n\n☀️ *Isitish va sovitish:* Qishki isitish + Yozgi konditsioner mavjud.\n\n🛁 *Xona ichida:*\n✅ Dush\n✅ Hojatxona (tualet)\n✅ Rakovina",
                 "description_ru": "🛏 *С/Люкс (4 человека)*\n\n• 🏢 *Корпус:* С корпус\n• 👥 *Вместимость:* 4 человека\n\n⚙️ *Удобства:*\n✅ 4 кровати\n✅ Тумбочка\n✅ Шкаф\n✅ Рабочий стол и стул\n✅ Wi-Fi\n✅ Телевизор\n\n☀️ *Климат:* Отопление + кондиционер.\n\n🛁 *Внутри палаты:*\n✅ Душ\n✅ Туалет\n✅ Раковина",
                 "description_kz": "🛏 *С/Люкс (4 адам)*\n\n• 🏢 *Корпус:* С корпусы\n• 👥 *Сыйымдылығы:* 4 адам\n\n⚙️ *Қолайлықтар:*\n✅ 4 кереует\n✅ Тумба\n✅ Шкаф\n✅ Үстел мен орындық\n✅ Wi-Fi\n✅ Теледидар\n\n☀️ *Климат:* Жылыту + кондиционер.\n\n🛁 *Палата ішінде:*\n✅ Душ\n✅ Дәретхана\n✅ Раковина"},
            ]
        },
        {
            "id": "m_yangi",
            "name_uz": "M Yangi Korpus",
            "name_ru": "Новый корпус М",
            "emoji": "🏢",
            "photos": [],
            "xonalar": [
                {"nom": "M/Urta miyona", "kishi": "3-5", "uz_adult": "313 000", "uz_child": "298 000", "foreign_adult": "313 000", "foreign_child": "298 000", "photos": [],
                 "description_uz": "🛏 *M/Urta miyona (3-5 kishi)*\n\n• 🏢 *Korpus:* M Yangi Korpus\n• 👥 *Sig'imi:* 3-5 kishi\n\n⚙️ *Qulayliklar:*\n✅ 3-5 ta krovat\n✅ Shaxsiy tumba\n✅ Shkaf\n✅ Wi-Fi\n✅ Televizor\n\n☀️ *Isitish va sovitish:* Qishki isitish + Yozgi konditsioner mavjud.\n\n🛁 *Yuvinish va gigiyena:* Dush va hojatxona umumiy, tashqarida.",
                 "description_ru": "🛏 *М/Средний (3-5 человек)*\n\n• 🏢 *Корпус:* Новый корпус М\n• 👥 *Вместимость:* 3-5 человек\n\n⚙️ *Удобства:*\n✅ 3-5 кроватей\n✅ Тумбочка\n✅ Шкаф\n✅ Wi-Fi\n✅ Телевизор\n\n☀️ *Климат:* Отопление + кондиционер.\n\n🛁 *Санузел:* Душ и туалет общие, снаружи.",
                 "description_kz": "🛏 *М/Орта (3-5 адам)*\n\n• 🏢 *Корпус:* М жаңа корпусы\n• 👥 *Сыйымдылығы:* 3-5 адам\n\n⚙️ *Қолайлықтар:*\n✅ 3-5 кереует\n✅ Тумба\n✅ Шкаф\n✅ Wi-Fi\n✅ Теледидар\n\n☀️ *Климат:* Жылыту + кондиционер.\n\n🛁 *Санторап:* Душ және дәретхана жалпы, сыртта."},
                {"nom": "M/Lyuks", "kishi": "4-6", "uz_adult": "420 000", "uz_child": "405 000", "foreign_adult": "420 000", "foreign_child": "405 000", "photos": [],
                 "description_uz": "🛏 *M/Lyuks (4-6 kishi)*\n\n• 🏢 *Korpus:* M Yangi Korpus\n• 👥 *Sig'imi:* 4-6 kishi\n\n⚙️ *Qulayliklar:*\n✅ 4-6 ta krovat\n✅ Shaxsiy tumba\n✅ Shkaf\n✅ Ish stoli va stuli\n✅ Wi-Fi\n✅ Televizor\n\n☀️ *Isitish va sovitish:* Qishki isitish + Yozgi konditsioner mavjud.\n\n🛁 *Xona ichida:*\n✅ Dush\n✅ Hojatxona (tualet)\n✅ Rakovina",
                 "description_ru": "🛏 *М/Люкс (4-6 человек)*\n\n• 🏢 *Корпус:* Новый корпус М\n• 👥 *Вместимость:* 4-6 человек\n\n⚙️ *Удобства:*\n✅ 4-6 кроватей\n✅ Тумбочка\n✅ Шкаф\n✅ Рабочий стол и стул\n✅ Wi-Fi\n✅ Телевизор\n\n☀️ *Климат:* Отопление + кондиционер.\n\n🛁 *Внутри палаты:*\n✅ Душ\n✅ Туалет\n✅ Раковина",
                 "description_kz": "🛏 *М/Люкс (4-6 адам)*\n\n• 🏢 *Корпус:* М жаңа корпусы\n• 👥 *Сыйымдылығы:* 4-6 адам\n\n⚙️ *Қолайлықтар:*\n✅ 4-6 кереует\n✅ Тумба\n✅ Шкаф\n✅ Үстел мен орындық\n✅ Wi-Fi\n✅ Теледидар\n\n☀️ *Климат:* Жылыту + кондиционер.\n\n🛁 *Палата ішінде:*\n✅ Душ\n✅ Дәретхана\n✅ Раковина"},
                {"nom": "M/Lyuks AB", "kishi": "2-3", "uz_adult": "465 000", "uz_child": "450 000", "foreign_adult": "465 000", "foreign_child": "450 000", "photos": [],
                 "description_uz": "🛏 *M/Lyuks AB (2-3 kishi)*\n\n• 🏢 *Korpus:* M Yangi Korpus\n• 👥 *Sig'imi:* 2-3 kishi\n\n⚙️ *Qulayliklar:*\n✅ 2-3 ta krovat\n✅ Shaxsiy tumba\n✅ Shkaf\n✅ Ish stoli va stuli\n✅ Wi-Fi\n✅ Televizor\n\n☀️ *Isitish va sovitish:* Qishki isitish + Yozgi konditsioner mavjud.\n\n🛁 *Xona ichida:*\n✅ Dush\n✅ Hojatxona (tualet)\n✅ Rakovina",
                 "description_ru": "🛏 *М/Люкс АБ (2-3 человека)*\n\n• 🏢 *Корпус:* Новый корпус М\n• 👥 *Вместимость:* 2-3 человека\n\n⚙️ *Удобства:*\n✅ 2-3 кровати\n✅ Тумбочка\n✅ Шкаф\n✅ Рабочий стол и стул\n✅ Wi-Fi\n✅ Телевизор\n\n☀️ *Климат:* Отопление + кондиционер.\n\n🛁 *Внутри палаты:*\n✅ Душ\n✅ Туалет\n✅ Раковина",
                 "description_kz": "🛏 *М/Люкс АБ (2-3 адам)*\n\n• 🏢 *Корпус:* М жаңа корпусы\n• 👥 *Сыйымдылығы:* 2-3 адам\n\n⚙️ *Қолайлықтар:*\n✅ 2-3 кереует\n✅ Тумба\n✅ Шкаф\n✅ Үстел мен орындық\n✅ Wi-Fi\n✅ Теледидар\n\n☀️ *Климат:* Жылыту + кондиционер.\n\n🛁 *Палата ішінде:*\n✅ Душ\n✅ Дәретхана\n✅ Раковина"},
                {"nom": "M/Lyuks", "kishi": "3", "uz_adult": "385 000", "uz_child": "370 000", "foreign_adult": "385 000", "foreign_child": "370 000", "photos": [],
                 "description_uz": "🛏 *M/Lyuks (3 kishi)*\n\n• 🏢 *Korpus:* M Yangi Korpus\n• 👥 *Sig'imi:* 3 kishi\n\n⚙️ *Qulayliklar:*\n✅ 3 ta krovat\n✅ Shaxsiy tumba\n✅ Shkaf\n✅ Ish stoli va stuli\n✅ Wi-Fi\n✅ Televizor\n\n☀️ *Isitish va sovitish:* Qishki isitish + Yozgi konditsioner mavjud.\n\n🛁 *Xona ichida:*\n✅ Dush\n✅ Hojatxona (tualet)\n✅ Rakovina",
                 "description_ru": "🛏 *М/Люкс (3 человека)*\n\n• 🏢 *Корпус:* Новый корпус М\n• 👥 *Вместимость:* 3 человека\n\n⚙️ *Удобства:*\n✅ 3 кровати\n✅ Тумбочка\n✅ Шкаф\n✅ Рабочий стол и стул\n✅ Wi-Fi\n✅ Телевизор\n\n☀️ *Климат:* Отопление + кондиционер.\n\n🛁 *Внутри палаты:*\n✅ Душ\n✅ Туалет\n✅ Раковина",
                 "description_kz": "🛏 *М/Люкс (3 адам)*\n\n• 🏢 *Корпус:* М жаңа корпусы\n• 👥 *Сыйымдылығы:* 3 адам\n\n⚙️ *Қолайлықтар:*\n✅ 3 кереует\n✅ Тумба\n✅ Шкаф\n✅ Үстел мен орындық\n✅ Wi-Fi\n✅ Теледидар\n\n☀️ *Климат:* Жылыту + кондиционер.\n\n🛁 *Палата ішінде:*\n✅ Душ\n✅ Дәретхана\n✅ Раковина"},
                {"nom": "M/Lyuks", "kishi": "2", "uz_adult": "495 000", "uz_child": "480 000", "foreign_adult": "495 000", "foreign_child": "480 000", "photos": [],
                 "description_uz": "🛏 *M/Lyuks (2 kishi)*\n\n• 🏢 *Korpus:* M Yangi Korpus\n• 👥 *Sig'imi:* 2 kishi\n\n⚙️ *Qulayliklar:*\n✅ 2 ta krovat\n✅ Shaxsiy tumba\n✅ Shkaf\n✅ Ish stoli va stuli\n✅ Wi-Fi\n✅ Televizor\n\n☀️ *Isitish va sovitish:* Qishki isitish + Yozgi konditsioner mavjud.\n\n🛁 *Xona ichida:*\n✅ Dush\n✅ Hojatxona (tualet)\n✅ Rakovina",
                 "description_ru": "🛏 *М/Люкс (2 человека)*\n\n• 🏢 *Корпус:* Новый корпус М\n• 👥 *Вместимость:* 2 человека\n\n⚙️ *Удобства:*\n✅ 2 кровати\n✅ Тумбочка\n✅ Шкаф\n✅ Рабочий стол и стул\n✅ Wi-Fi\n✅ Телевизор\n\n☀️ *Климат:* Отопление + кондиционер.\n\n🛁 *Внутри палаты:*\n✅ Душ\n✅ Туалет\n✅ Раковина",
                 "description_kz": "🛏 *М/Люкс (2 адам)*\n\n• 🏢 *Корпус:* М жаңа корпусы\n• 👥 *Сыйымдылығы:* 2 адам\n\n⚙️ *Қолайлықтар:*\n✅ 2 кереует\n✅ Тумба\n✅ Шкаф\n✅ Үстел мен орындық\n✅ Wi-Fi\n✅ Теледидар\n\n☀️ *Климат:* Жылыту + кондиционер.\n\n🛁 *Палата ішінде:*\n✅ Душ\n✅ Дәретхана\n✅ Раковина"},
                {"nom": "M/VIP", "kishi": "2", "uz_adult": "699 000", "uz_child": "684 000", "foreign_adult": "699 000", "foreign_child": "684 000", "photos": [],
                 "description_uz": "🛏 *M/VIP (2 kishi)*\n\n• 🏢 *Korpus:* M Yangi Korpus\n• 👥 *Sig'imi:* 2 kishi\n\n⚙️ *Qulayliklar:*\n✅ 2 ta krovat\n✅ Shaxsiy tumba\n✅ Shkaf\n✅ Ish stoli va stuli\n✅ Wi-Fi\n✅ Televizor\n✅ Massaj kreslosi\n✅ Velo trenajor\n✅ Relaksatsion oyoq nuqtalari massaji\n\n☀️ *Isitish va sovitish:* Qishki isitish + Yozgi konditsioner mavjud.\n\n🛁 *Xona ichida:*\n✅ Dush\n✅ Hojatxona (tualet)\n✅ Rakovina",
                 "description_ru": "🛏 *М/VIP (2 человека)*\n\n• 🏢 *Корпус:* Новый корпус М\n• 👥 *Вместимость:* 2 человека\n\n⚙️ *Удобства:*\n✅ 2 кровати\n✅ Тумбочка\n✅ Шкаф\n✅ Рабочий стол и стул\n✅ Wi-Fi\n✅ Телевизор\n✅ Массажное кресло\n✅ Велотренажёр\n✅ Релаксационный массаж точек стоп\n\n☀️ *Климат:* Отопление + кондиционер.\n\n🛁 *Внутри палаты:*\n✅ Душ\n✅ Туалет\n✅ Раковина",
                 "description_kz": "🛏 *М/VIP (2 адам)*\n\n• 🏢 *Корпус:* М жаңа корпусы\n• 👥 *Сыйымдылығы:* 2 адам\n\n⚙️ *Қолайлықтар:*\n✅ 2 кереует\n✅ Тумба\n✅ Шкаф\n✅ Үстел мен орындық\n✅ Wi-Fi\n✅ Теледидар\n✅ Массаж креслосы\n✅ Велотренажер\n✅ Релаксациялық аяқ нүктелері массажы\n\n☀️ *Климат:* Жылыту + кондиционер.\n\n🛁 *Палата ішінде:*\n✅ Душ\n✅ Дәретхана\n✅ Раковина"},
                {"nom": "M/VIP", "kishi": "1", "uz_adult": "760 000", "uz_child": "745 000", "foreign_adult": "760 000", "foreign_child": "745 000", "photos": [],
                 "description_uz": "🛏 *M/VIP (1 kishi)*\n\n• 🏢 *Korpus:* M Yangi Korpus\n• 👥 *Sig'imi:* 1 kishi\n\n⚙️ *Qulayliklar:*\n✅ 1 ta krovat\n✅ Shaxsiy tumba\n✅ Shkaf\n✅ Ish stoli va stuli\n✅ Wi-Fi\n✅ Televizor\n✅ Massaj kreslosi\n✅ Velo trenajor\n✅ Relaksatsion oyoq nuqtalari massaji\n\n☀️ *Isitish va sovitish:* Qishki isitish + Yozgi konditsioner mavjud.\n\n🛁 *Xona ichida:*\n✅ Dush\n✅ Hojatxona (tualet)\n✅ Rakovina",
                 "description_ru": "🛏 *М/VIP (1 человек)*\n\n• 🏢 *Корпус:* Новый корпус М\n• 👥 *Вместимость:* 1 человек\n\n⚙️ *Удобства:*\n✅ 1 кровать\n✅ Тумбочка\n✅ Шкаф\n✅ Рабочий стол и стул\n✅ Wi-Fi\n✅ Телевизор\n✅ Массажное кресло\n✅ Велотренажёр\n✅ Релаксационный массаж точек стоп\n\n☀️ *Климат:* Отопление + кондиционер.\n\n🛁 *Внутри палаты:*\n✅ Душ\n✅ Туалет\n✅ Раковина",
                 "description_kz": "🛏 *М/VIP (1 адам)*\n\n• 🏢 *Корпус:* М жаңа корпусы\n• 👥 *Сыйымдылығы:* 1 адам\n\n⚙️ *Қолайлықтар:*\n✅ 1 кереует\n✅ Тумба\n✅ Шкаф\n✅ Үстел мен орындық\n✅ Wi-Fi\n✅ Теледидар\n✅ Массаж креслосы\n✅ Велотренажер\n✅ Релаксациялық аяқ нүктелері массажы\n\n☀️ *Климат:* Жылыту + кондиционер.\n\n🛁 *Палата ішінде:*\n✅ Душ\n✅ Дәретхана\n✅ Раковина"},
                {"nom": "M/Apartament", "kishi": "2", "uz_adult": "760 000", "uz_child": "745 000", "foreign_adult": "760 000", "foreign_child": "745 000", "photos": [],
                 "description_uz": "🛏 *M/Apartament (2 kishi)*\n\n• 🏢 *Korpus:* M Yangi Korpus\n• 👥 *Sig'imi:* 2 kishi\n\n⚙️ *Qulayliklar:*\n✅ 2 ta krovat\n✅ Shaxsiy tumba\n✅ Shkaf\n✅ Ish stoli va stuli\n✅ Wi-Fi\n✅ Televizor\n\n☀️ *Isitish va sovitish:* Qishki isitish + Yozgi konditsioner mavjud.\n\n🛁 *Xona ichida:*\n✅ Dush\n✅ Hojatxona (tualet)\n✅ Rakovina",
                 "description_ru": "🛏 *М/Апартамент (2 человека)*\n\n• 🏢 *Корпус:* Новый корпус М\n• 👥 *Вместимость:* 2 человека\n\n⚙️ *Удобства:*\n✅ 2 кровати\n✅ Тумбочка\n✅ Шкаф\n✅ Рабочий стол и стул\n✅ Wi-Fi\n✅ Телевизор\n\n☀️ *Климат:* Отопление + кондиционер.\n\n🛁 *Внутри палаты:*\n✅ Душ\n✅ Туалет\n✅ Раковина",
                 "description_kz": "🛏 *М/Апартамент (2 адам)*\n\n• 🏢 *Корпус:* М жаңа корпусы\n• 👥 *Сыйымдылығы:* 2 адам\n\n⚙️ *Қолайлықтар:*\n✅ 2 кереует\n✅ Тумба\n✅ Шкаф\n✅ Үстел мен орындық\n✅ Wi-Fi\n✅ Теледидар\n\n☀️ *Климат:* Жылыту + кондиционер.\n\n🛁 *Палата ішінде:*\n✅ Душ\n✅ Дәретхана\n✅ Раковина"},
            ]
        },
    ],
    "xona_included": {
        "uz": "✅ *Narxga kiradigan xizmatlar:*\n• Turar joy\n• Davolash\n• Fizioterapiya va manual terapiya\n• УЗИ, qon tahlili, EKG\n• МРТ 1.5Т yoki МСКТ (1 organ)\n\n⚠️ Bolalar 5 yoshdan qabul qilinadi\n\n➕ *Qo'shimcha (alohida to'lov):*\nМРТ-3Т, МСКТ-256, Mammografiya, Kriolipoliz, Cho'zilish, Zarba-to'lqin terapiyasi",
        "ru": "✅ *В стоимость включено:*\n• Проживание\n• Лечение\n• Физиотерапия и мануальная терапия\n• УЗИ, анализ крови, ЭКГ\n• МРТ 1.5Т или МСКТ (1 орган)\n\n⚠️ Дети принимаются с 5 лет\n\n➕ *Дополнительно (отдельная оплата):*\nМРТ-3Т, МСКТ-256, Маммография, Криолиполиз, Растяжка, Ударно-волновая терапия",
        "kz": "✅ *Бағаға кіреді:*\n• Тұру\n• Емдеу\n• Физиотерапия және мануалды терапия\n• УДЗ, қан анализі, ЭКГ\n• МРТ 1.5Т немесе МСКТ (1 орган)\n\n⚠️ Балалар 5 жастан қабылданады\n\n➕ *Қосымша (бөлек төлем):*\nМРТ-3Т, МСКТ-256, Маммография, Криолиполиз",
    },
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
    "clinic_info_text": {
        "uz": (
            "🏥 *\"Ergash ota\" xususiy tibbiyot markazi*\n\n"
            "Zamonaviy diagnostika va kompleks davolash markazi.\n\n"
            "📍 *Manzil:* Kattaqo'rg'on shahri, Qozoq ovul massivi\n\n"
            "🕐 *Ish vaqti:*\n"
            "• Du–Shan: 08:00 – 18:00\n"
            "• Yakshanba: Dam olish kuni. Registratsiya bo'limi ishlaydi — yangi kelgan bemorlar qabul qilinadi va birinchi kun davolash boshlanadi.\n\n"
            "📞 *Qo'shimcha ma'lumotlar uchun:* Du–Shan: 08:00 – 18:00\n"
            "+998 93 346 62 77\n"
            "+998 93 226 45 67\n\n"
            "🔬 *Zamonaviy diagnostika:*\n"
            "• MRT 3 Tesla\n"
            "• Canon Aquilion MSKT 256 kesimli\n"
            "• NUESOFT MSKT 128 kesimli\n"
            "• Mammografiya\n"
            "• Fibroscan\n"
            "• UZI diagnostikasi\n"
            "• Laboratoriya tekshiruvlari\n\n"
            "💆‍♂️ *Davolash va muolajalar:*\n"
            "• Fizioterapiya | Manual terapiya\n"
            "• Zarba-to'lqin terapiyasi\n"
            "• Umurtqa cho'zish muolajalari | Kriolipoliz\n\n"
            "🏨 *Davo paketiga nimalar kiradi?*\n"
            "_(Xona turiga qarab asosiy paket tarkibi):_\n"
            "✔️ Turar joy va shinam statsionar sharoit\n"
            "✔️ Davolash muolajalari\n"
            "✔️ Fizioterapiya va manual terapiya\n"
            "✔️ UZI, qon tahlili, EKG\n"
            "✔️ Lyuks xonalarda: MRT 1.5T yoki MSKT (1 organ)\n\n"
            "✅ *Bir joyning o'zida:* Diagnostika • Reabilitatsiya • Statsionar • Davolash\n\n"
            "📸 *Instagram:* https://www.instagram.com/ergashotaclinics\n"
            "🌐 *Veb-sayt:* https://ergash-ota-tm.uz/"
        ),
        "ru": (
            "🏥 *Частный медицинский центр «Эргаш ота»*\n\n"
            "Современный центр диагностики и комплексного лечения.\n\n"
            "📍 *Адрес:* г. Каттакурган, массив Казак овул\n\n"
            "🕐 *Режим работы:*\n"
            "• Пн–Сб: 08:00 – 18:00\n"
            "• Воскресенье: Выходной. Регистратура работает — принимаются новые пациенты, в первый день начинается лечение.\n\n"
            "📞 *Для справок:* Пн–Сб: 08:00 – 18:00\n"
            "+998 93 346 62 77\n"
            "+998 93 226 45 67\n\n"
            "🔬 *Современная диагностика:*\n"
            "• МРТ 3 Тесла\n"
            "• Canon Aquilion МСКТ 256 срезов\n"
            "• NUESOFT МСКТ 128 срезов\n"
            "• Маммография\n"
            "• Фибросканирование\n"
            "• УЗИ диагностика\n"
            "• Лабораторные исследования\n\n"
            "💆‍♂️ *Лечение и процедуры:*\n"
            "• Физиотерапия | Мануальная терапия\n"
            "• Ударно-волновая терапия\n"
            "• Вытяжение позвоночника | Криолиполиз\n\n"
            "🏨 *Что входит в лечебный пакет?*\n"
            "_(В зависимости от типа палаты):_\n"
            "✔️ Проживание и комфортные условия\n"
            "✔️ Лечебные процедуры\n"
            "✔️ Физиотерапия и мануальная терапия\n"
            "✔️ УЗИ, анализ крови, ЭКГ\n"
            "✔️ В люкс-палатах: МРТ 1.5Т или МСКТ (1 орган)\n\n"
            "✅ *В одном месте:* Диагностика • Реабилитация • Стационар • Лечение\n\n"
            "📸 *Instagram:* https://www.instagram.com/ergashotaclinics\n"
            "🌐 *Сайт:* https://ergash-ota-tm.uz/"
        ),
        "kz": (
            "🏥 *«Эргаш ота» жеке медициналық орталығы*\n\n"
            "Заманауи диагностика және кешенді емдеу орталығы.\n\n"
            "📍 *Мекенжай:* Каттақўрғон қаласы, Қазақ овул массиві\n\n"
            "🕐 *Жұмыс уақыты:*\n"
            "• Дс–Сб: 08:00 – 18:00\n"
            "• Жексенбі: Демалыс. Тіркеу бөлімі жұмыс істейді — жаңа науқастар қабылданады, бірінші күні ем басталады.\n\n"
            "📞 *Анықтама үшін:* Дс–Сб: 08:00 – 18:00\n"
            "+998 93 346 62 77\n"
            "+998 93 226 45 67\n\n"
            "🔬 *Заманауи диагностика:*\n"
            "• МРТ 3 Тесла\n"
            "• Canon Aquilion МСКТ 256 кесінді\n"
            "• NUESOFT МСКТ 128 кесінді\n"
            "• Маммография\n"
            "• Фибросканерлеу\n"
            "• УДЗ диагностикасы\n"
            "• Зертханалық зерттеулер\n\n"
            "💆‍♂️ *Емдеу және процедуралар:*\n"
            "• Физиотерапия | Мануалды терапия\n"
            "• Соққы-толқын терапиясы\n"
            "• Омыртқаны созу | Криолиполиз\n\n"
            "🏨 *Ем бумасына не кіреді?*\n"
            "_(Палата түріне байланысты):_\n"
            "✔️ Тұрғын үй және ыңғайлы жағдай\n"
            "✔️ Ем процедуралары\n"
            "✔️ Физиотерапия және мануалды терапия\n"
            "✔️ УДЗ, қан анализі, ЭКГ\n"
            "✔️ Люкс палаталарда: МРТ 1.5Т немесе МСКТ (1 орган)\n\n"
            "✅ *Бір жерде:* Диагностика • Реабилитация • Стационар • Емдеу\n\n"
            "📸 *Instagram:* https://www.instagram.com/ergashotaclinics\n"
            "🌐 *Сайт:* https://ergash-ota-tm.uz/"
        ),
    },
    "weekend": {
        "ru": "🌅 В воскресенье мы работаем для новых пациентов!\n\n✅ Приём и регистрация\n✅ Первичный осмотр\n✅ Начало лечения в первый же день\n\n🕌 А в свободное время — экскурсии в Самарканд и Бухару!\n\n📞 Свяжитесь с нами: {phone}",
        "uz": "🌅 Yakshanba kuni yangi bemorlarni qabul qilamiz!\n\n✅ Qabul va ro'yxatga olish\n✅ Dastlabki ko'rik\n✅ Birinchi kuniyoq davolash boshlanadi\n\n🕌 Bo'sh vaqtda — Samarqand va Buxoroga ekskursiya!\n\n📞 Bog'laning: {phone}",
        "kz": "🌅 Жексенбіде жаңа науқастарды қабылдаймыз!\n\n✅ Тіркеу және қабылдау\n✅ Алғашқы тексеру\n✅ Бірінші күні емдеу басталады\n\n📞 Байланысыңыз: {phone}",
    },
    "guide": {
        "arrival_step1": {
            "ru": "🏥 *Порядок размещения в клинике*\n\n1️⃣ *Шаг 1: Регистрация*\n\nОбратитесь в регистратуру с паспортом или удостоверением личности и пройдите регистрацию.\n\n",
            "uz": "🏥 *Klinikaga joylashish tartibi*\n\n1️⃣ *1-bosqich: Ro'yxatdan o'tish*\n\nPasport yoki ID karta bilan registraturaga murojaat qiling va ro'yxatdan o'ting.\n\n",
            "kz": "🏥 *Клиникаға орналасу тәртібі*\n\n1️⃣ *1-кезең: Тіркелу*\n\nПаспорт немесе жеке куәлікпен тіркеуге барыңыз.\n\n",
            "video": "",
        },
        "arrival_step2": {
            "ru": "❤️ *Шаг 2: Осмотр врача*\n\nвы: На 2-м этаже приёмного корпуса.\n✅ Проходите ЭКГ\n✅ Проходите осмотр врача\n✅ Заполняете расписку\n\nПри необходимости назначаются:\n• МРТ\n• МСКТ\n• Лабораторные анализы\n\n📍 Вы находитесь в приёмном отделении на *2-м этаже*.",
            "uz": "❤️ *2-bosqich: Shifokor ko'rigi*\n\nSiz: Qabulxonaning 2-qavatida joylashgan.\n✅ EKG tekshiruvidan o'tasiz\n✅ Shifokor ko'rigidan o'tasiz\n✅ Tilxat to'ldirasiz\n\nZarurat bo'lsa:\n• MRT\n• MSKT\n• Laboratoriya tekshiruvlari tavsiya qilinadi\n\n📍 Siz qabulxonaning *2-qavatida*siz.",
            "kz": "❤️ *2-кезең: Дәрігер қарауы*\n\nСіз: Қабылдау корпусының 2-қабатында орналасқан.\n✅ ЭКГ тексерісінен өтесіз\n✅ Дәрігер қарауынан өтесіз\n✅ Тілхат толтырасыз\n\nҚажет болса:\n• МРТ\n• МСКТ\n• Зертхана анализдері\n\n📍 Сіз қабылдау бөлімінің *2-қабатынdasız*.",
            "video": "",
        },
        "arrival_step3": {
            "ru": "🏨 *Шаг 3: Выбор номера и размещение*\n\nВы: находитесь на 1-м этаже приёмной\n\n✅ Выбираете удобный номер\n✅ Оплачиваете на кассе\n✅ Принимаете слабительный препарат (кабинет 12)\n✅ Медсёстры размещают вас\n\n🕐 *Приём и размещение:* 08:00 – 18:00\n📍 *После 18:00:* пациенты принимаются дежурными врачами",
            "uz": "🏨 *3-bosqich: Xona tanlash va joylashish*\n\nSiz: Qabulxonaning 1- qavatidasiz\n\n✅ O'zingizga qulay xonani tanlaysiz\n✔ Kassada to'lov qilasiz\n✅ 12-xonaga surgi giyohini ichasiz\n✔ Hamshiralar sizni joylashtiradi\n\n🕐 *Qabul va joylashish:* 08:00 – 18:00\n📍 *18:00 dan keyin kelgan bemorlar:* navbatchi vrachlar tomonidan qabul qilinadi",
            "kz": "🏨 *3-кезең: Бөлме таңдау және орналасу*\n\nСіз қабылдау бөлмесінің 1-қабатындасыз\n\n✅ Ыңғайлы бөлмені таңдайсыз\n✅ Кассада төлем жасайсыз\n✅ Іш жүргізетін дәрі қабылдайсыз (12-кабинет)\n✅ Медбикелер орналастырады\n\n🕐 *Қабылдау:* 08:00 – 18:00\n📍 *18:00 кейін:* кезекші дәрігерлер қабылдайды",
            "video": "",
        },
        "arrival": {
            "ru": "🏥 *Порядок размещения в клинике*\n\nВыберите шаг:",
            "uz": "🏥 *Klinikaga joylashish tartibi*\n\nBosqichni tanlang:",
            "kz": "🏥 *Клиникаға орналасу тәртібі*\n\nКезеңді таңдаңыз:",
            "video": "",
        },
        "malham": {
            "ru": "2️⃣ *Малхам — главная процедура*\n\nМалхам — чудодейственное снадобье, разработанное лично Бердикулом Эргашевым. Рецепт знает только он.\n\n📍 Место: главное здание, приёмный кабинет доктора\n🕐 Время для иностранцев: 10:00–12:00\n\nЧто взять с собой:\n• Процедурную книжку\n• Платок или салфетки\n• Пустую грелку\n\n📋 *Порядок:*\n1. Отдайте книжку медбрату у двери\n2. Заходят по 4 человека\n3. Доктор читает молитву, осматривает, выдаёт малхам\n4. Пьётся залпом! Можно заесть леденцом или куртом\n\n⏱ *Важно:*\n• Не пить за 1.5 часа ДО и 1.5 часа ПОСЛЕ\n• После приёма сразу идите в номер с грелкой\n• Грелку наполнить кипятком из бойлера\n• Лечь на правый бок (грелка на печень) на 1.5–2 часа",
            "uz": "2️⃣ *Malham — asosiy protsedura*\n\nMalham — Berdiqul Ergashev tomonidan ishlab chiqilgan mo'jizali dori. Retseptni faqat u biladi.\n\n📍 Joy: asosiy bino, doktor qabul xonasi\n🕐 Xorijiylar uchun vaqt: 10:00–12:00\n\nO'zingiz bilan oling:\n• Protsedura daftarchasi\n• Ro'molcha yoki salfetkalar\n• Bo'sh grелка\n\n📋 *Tartib:*\n1. Daftarchani eshik oldidagi tibbiy xodimga bering\n2. 4 kishidan kiriladi\n3. Doktor duo o'qiydi, ko'rik o'tkazadi, malham beradi\n4. Bir yutkida ichiladi! Konfet yoki kurt bilan yeyish mumkin\n\n⏱ *Muhim:*\n• Oldin 1.5 soat va keyin 1.5 soat hech narsa ichmaslik\n• Ichgandan keyin darhol xonaga boring\n• Grелkani qaynagan suv bilan to'ldiring\n• O'ng yoningizda yoting (grелka jigar ustida) 1.5–2 soat",
            "kz": "2️⃣ *Малхам — негізгі процедура*\n\nМалхам — Бердіқұл Ерғашев жасаған ғажайып дәрі.\n\n📍 Орын: бас ғимарат, дәрігер қабылдау бөлмесі\n🕐 Шетелдіктер үшін: 10:00–12:00\n\nАлып баруға:\n• Процедуралық кітапша\n• Орамал немесе сүлгі\n• Бос жылытқыш\n\n⏱ *Маңызды:*\n• Малхамнан 1.5 сағат бұрын және кейін ештеңе ішпеу\n• Қабылдаудан кейін бірден бөлмеге барыңыз\n• Оң жаққа жатыңыз (бауыр үстіне жылытқыш) 1.5–2 сағат",
            "video": "",
        },
        "procedures": {
            "ru": "3️⃣ *Процедуры и распорядок дня*\n\n🌅 *Утро:*\n• Клизма (кишечное промывание) — обязательно!\n  Возьмите: насадки, процедурную простынь\n• После клизмы — отдых в номере\n• Затем — Малхам (10:00–12:00)\n• После Малхама — грелка 1.5–2 часа\n\n☀️ *День:*\n• Массаж (кабинеты в 2 корпусах)\n  Возьмите: книжку, простынь, массажное масло\n• Аппаратная физиотерапия (ноги, живот, спина)\n• Растяжка\n• Тренажёрный зал\n• Аппаратная косметология\n• Укол в ухо\n• Анализы\n\n🍵 *Питание:*\n• Еда только в субботу вечером и воскресенье\n• Ежедневно: сок (1 банка/день) — покупается справа от столовой\n• Лечебные чаи — у санитарок в каждом корпусе\n\n⚠️ *Четверг* — короткий день (субботник)\n🎵 *Четверг и воскресенье* — музыкальный отдых после ужина (21:00)",
            "uz": "3️⃣ *Protseduralar va kun tartibi*\n\n🌅 *Ertalab:*\n• Klizma (ichak yuvish) — majburiy!\n  Oling: nasadkalar, protsedura choyshab\n• Klizmadan keyin — xonada dam olish\n• Keyin — Malham (10:00–12:00)\n• Malhamdan keyin — grелka 1.5–2 soat\n\n☀️ *Kunduz:*\n• Massaj (2 korpusda xonalar)\n  Oling: daftarcha, choyshab, massaj yog'i\n• Apparat fizioterapiya (oyoqlar, qorin, orqa)\n• Cho'zilish\n• Sport zal\n• Apparat kosmetologiya\n• Quloqqa ukol\n• Tahlillar\n\n🍵 *Ovqatlanish:*\n• Ovqat faqat shanba kechqurun va yakshanba\n• Har kuni: sharbat (1 banka/kun) — oshxona o'ng tomonida\n• Shifobaxsh choylar — har korpusdagi sanitarkalarda\n\n⚠️ *Payshanba* — qisqa kun\n🎵 *Payshanba va yakshanba* — musiqali dam olish kechki ovqatdan keyin (21:00)",
            "kz": "3️⃣ *Процедуралар және күн тәртібі*\n\n🌅 *Таңертең:*\n• Клизма — міндетті!\n• Малхам (10:00–12:00)\n• Малхамнан кейін — жылытқыш 1.5–2 сағат\n\n☀️ *Күндіз:*\n• Массаж\n• Аппараттық физиотерапия\n• Созылу\n• Спорт залы\n• Анализдер\n\n🍵 *Тамақтану:*\n• Тамақ тек сенбі кешінде және жексенбіде\n• Күнде: шырын (1 банка/күн)\n• Емдік шайлар — әр корпуста",
        },
        "infrastructure": {
            "ru": "4️⃣ *Инфраструктура комплекса*\n\n🏢 *Корпуса:*\n• Главный корпус — касса, приём врача, Малхам\n• Корпус «Диагностика» — ресепшн, МРТ, МСКТ\n• Процедурные корпуса — клизма, массаж, физиотерапия\n\n🍽 *Питание:*\n• Столовая — еда в субботу вечером и воскресенье\n• Кафе — дополнительное питание\n• Сок — справа от столовой (первый раз: оплата банки + сок)\n\n🛒 *Магазин:*\n• Рядом с комплексом — продукты, чашки для чая\n\n📶 *WiFi* — доступен в корпусах\n\n👕 *Прачечная* — услуги стирки доступны\n\n⚖️ *Весы* — расположены в корпусах (уточнить у персонала)",
            "uz": "4️⃣ *Kompleks infratuzilmasi*\n\n🏢 *Korpuslar:*\n• Asosiy korpus — kassa, doktor qabuli, Malham\n• «Diagnostika» korpusi — resepshn, МРТ, МСКТ\n• Protsedura korpuslari — klizma, massaj, fizioterapiya\n\n🍽 *Ovqatlanish:*\n• Oshxona — shanba kechqurun va yakshanba\n• Kafe — qo'shimcha ovqat\n• Sharbat — oshxona o'ng tomonida\n\n🛒 *Do'kon:*\n• Kompleks yonida — oziq-ovqat, choy piyolalari\n\n📶 *WiFi* — korpuslarda mavjud\n\n👕 *Kir yuvish* — xizmat mavjud\n\n⚖️ *Tarozilar* — korpuslarda joylashgan",
            "kz": "4️⃣ *Кешен инфрақұрылымы*\n\n🏢 *Корпустар:*\n• Бас корпус — касса, дәрігер қабылдауы, Малхам\n• «Диагностика» корпусы — ресепшн, МРТ, МСКТ\n• Процедуралық корпустар — клизма, массаж\n\n🍽 *Тамақтану:*\n• Асхана — сенбі кешінде және жексенбіде\n• Кафе — қосымша тамақ\n• Шырын — асхананың оң жағында\n\n📶 *WiFi* — корпустарда қолжетімді\n\n👕 *Кір жуу* — қызмет бар",
        },
        "rules": {
            "ru": "5️⃣ *Общие правила*\n\n👗 *Одежда:*\n• Удобная, свободная одежда\n• Для массажа — отдельный комплект (масло не отстирывается!)\n\n🚌 *Поездки в город:*\n• Разрешены, но соблюдайте режим процедур\n\n🕐 *Распорядок:*\n• Обеденный перерыв — примерно (время уточните на ресепшн)\n• Четверг — короткий день (субботник)\n• Музыкальный вечер: Четверг и Воскресенье в 21:00\n\n🛏 *Уборка номеров:*\n• Проводится персоналом\n\n⚠️ *Важно знать:*\nВ Узбекистане другой темп жизни — здесь всё примерно. Будьте терпеливы и наслаждайтесь процессом выздоровления! 🌿",
            "uz": "5️⃣ *Umumiy qoidalar*\n\n👗 *Kiyim:*\n• Qulay, erkin kiyim\n• Massaj uchun — alohida to'plam (yog' ketmaydi!)\n\n🚌 *Shaharga chiqish:*\n• Ruxsat beriladi, lekin protsedura rejimini saqlang\n\n🕐 *Kun tartibi:*\n• Tushlik tanaffus — taxminan (resepshnga aniqlang)\n• Payshanba — qisqa kun\n• Musiqali kech: Payshanba va Yakshanba 21:00 da\n\n🛏 *Xona tozalash:*\n• Xodimlar tomonidan amalga oshiriladi\n\n⚠️ *Muhim:*\nO'zbekistonda hayot sur'ati boshqacha — sabr-toqatli bo'ling! 🌿",
            "kz": "5️⃣ *Жалпы ережелер*\n\n👗 *Киім:*\n• Ыңғайлы, еркін киім\n• Массажға — бөлек киім жиынтығы\n\n🕐 *Күн тәртібі:*\n• Бейсенбі — қысқа күн\n• Музыкалық кеш: Бейсенбі және Жексенбі 21:00\n\n⚠️ *Маңызды:*\nӨзбекстанда өмір қарқыны басқаша — шыдамды болыңыз! 🌿",
        },
        "shopping": {
            "ru": "6️⃣ *Что купить домой*\n\n🛍 Рекомендуем приобрести на территории комплекса:\n\n🌿 *Исырык (могильник)* — очищающее растение\n💊 *Чудо-мазь* — разработка клиники\n🍯 *Натуральный мёд* — местный, чистый\n🍵 *Лечебные чаи* — по назначению врача\n🫙 *Миндальное масло* — для массажа и ухода\n\n📍 Всё это можно найти на территории комплекса или у персонала.\n\n💡 Спросите у медперсонала — они подскажут где купить!",
            "uz": "6️⃣ *Uyga nima sotib olish kerak*\n\n🛍 Kompleks hududida sotib olishni tavsiya qilamiz:\n\n🌿 *Isiriq* — tozalovchi o'simlik\n💊 *Mo'jizaviy malham* — klinika ishlanmasi\n🍯 *Tabiiy asal* — mahalliy, sof\n🍵 *Shifobaxsh choylar* — doktor tavsiyasiga ko'ra\n🫙 *Bodom yog'i* — massaj va parvarishlash uchun\n\n📍 Hammasini kompleks hududida yoki xodimlardan topish mumkin.\n\n💡 Tibbiy xodimlardan so'rang — ular qayerdan sotib olishni aytib berishadi!",
            "kz": "6️⃣ *Үйге не сатып алу керек*\n\n🛍 Кешен аумағында сатып алуды ұсынамыз:\n\n🌿 *Ысырық* — тазартатын өсімдік\n💊 *Керемет жақпа май* — клиника өнімі\n🍯 *Табиғи бал* — жергілікті, таза\n🍵 *Емдік шайлар* — дәрігер тағайындауы бойынша\n🫙 *Бадам майы* — массажға\n\n💡 Медперсоналдан сұраңыз!",
        },
    },
}


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        # Yangi kalitlarni qo'shish (DEFAULT_DATA da bor, saved da yo'q)
        updated = False
        for key, val in DEFAULT_DATA.items():
            if key not in saved:
                saved[key] = val
                updated = True
        # korpuslar tartibini va nomlarini DEFAULT_DATA dan yangilash
        default_korpuslar = DEFAULT_DATA.get("korpuslar", [])
        saved_korpuslar = {k["id"]: k for k in saved.get("korpuslar", [])}
        merged_korpuslar = []
        for dk in default_korpuslar:
            sk = saved_korpuslar.get(dk["id"], {})
            merged = dict(dk)
            # Rasmlarni saqlab qolish
            merged["photos"] = sk.get("photos", [])
            # Xonalarni birlashtirish
            merged_xonalar = []
            for di, dxona in enumerate(dk.get("xonalar", [])):
                sx = sk.get("xonalar", [{}] * (di + 1))
                sxona = sx[di] if di < len(sx) else {}
                mxona = dict(dxona)
                mxona["photos"] = sxona.get("photos", [])
                mxona["videos"] = sxona.get("videos", [])
                merged_xonalar.append(mxona)
            merged["xonalar"] = merged_xonalar
            merged_korpuslar.append(merged)
        saved["korpuslar"] = merged_korpuslar
        # clinic_info_text ni DEFAULT_DATA dan har doim yangilash
        saved["clinic_info_text"] = DEFAULT_DATA["clinic_info_text"]
        # rooms_uz va rooms_foreign ni DEFAULT_DATA dan yangilash
        saved["rooms_uz"] = DEFAULT_DATA["rooms_uz"]
        saved["rooms_foreign"] = DEFAULT_DATA["rooms_foreign"]
        updated = True
        if updated:
            save_data(saved)
        return saved
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
        "clinic":          "🏥 О клинике",
        "rooms":           "🛏 Стоимость номеров",
        "diagnostics":     "🧲 Диагностика",
        "wards":           "🏨 Палаты",
        "guide":           "📖 Инструкция для пациентов",
        "faq":             "❓ Частые вопросы",
        "booking":         "📅 Записаться на приём",
        "transfer":        "🚗 Добраться до клиники",
        "weekend":         "🌅 Воскресенье",
        "operator":        "📞 Оператор",
        "doctor_question": "👨‍⚕️ Задать вопрос врачу",
    },
    "uz": {
        "clinic":          "🏥 Klinika haqida",
        "rooms":           "🛏 Xonalar narxi",
        "diagnostics":     "🧲 Diagnostika",
        "wards":           "🏨 Palatalar",
        "guide":           "📖 Bemor uchun qo'llanma",
        "faq":             "❓ Ko'p so'raladigan savollar",
        "booking":         "📅 Qabulga yozilish",
        "transfer":        "🚗 Klinikaga yetib olish",
        "weekend":         "🌅 Yakshanba",
        "operator":        "📞 Operator",
        "doctor_question": "👨‍⚕️ Shifokorga savol yuborish",
    },
    "kz": {
        "clinic":          "🏥 Клиника туралы",
        "rooms":           "🛏 Бөлмелер бағасы",
        "diagnostics":     "🧲 Диагностика",
        "wards":           "🏨 Палаталар",
        "guide":           "📖 Науқас нұсқаулығы",
        "faq":             "❓ Жиі сұрақтар",
        "booking":         "📅 Қабылдауға жазылу",
        "transfer":        "🚗 Клиникаға жету",
        "weekend":         "🌅 Жексенбі",
        "operator":        "📞 Оператор",
        "doctor_question": "👨‍⚕️ Дәрігерге сұрақ жіберу",
    },
}


def main_menu_keyboard(lang, user_id: int = 0):
    labels = MENU_LABELS[lang]
    buttons = [
        [InlineKeyboardButton(labels["clinic"],          callback_data="menu_clinic")],
        [InlineKeyboardButton(labels["rooms"],           callback_data="menu_rooms")],
        [InlineKeyboardButton(labels["wards"],           callback_data="menu_wards")],
        [InlineKeyboardButton(labels["diagnostics"],     callback_data="menu_diagnostics")],
        [InlineKeyboardButton(labels["guide"],           callback_data="menu_guide")],
        [InlineKeyboardButton(labels["faq"],             callback_data="menu_faq")],
        [InlineKeyboardButton(labels["booking"],         callback_data="menu_booking")],
        [InlineKeyboardButton(labels["weekend"],         callback_data="menu_weekend")],
        [InlineKeyboardButton(labels["doctor_question"], callback_data="doctor_question")],
    ]
    if user_id and (user_id == ADMIN_ID or user_id in ALLOWED_STAFF):
        upload_label = {"ru": "📤 Загрузить PDF результат", "uz": "📤 PDF Natija Yuklash", "kz": "📤 PDF Нәтиже Жүктеу"}.get(lang, "📤 PDF Natija Yuklash")
        buttons.append([InlineKeyboardButton(upload_label, callback_data="staff_pdf_upload")])
    return InlineKeyboardMarkup(buttons)


def back_keyboard(lang):
    label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data="back_main")]])


def rooms_keyboard(lang):
    labels = {
        "ru": ("🇺🇿 Граждане Узбекистана", "🌍 Иностранные граждане", "🧮 Рассчитать стоимость", "⬅️ Назад"),
        "uz": ("🇺🇿 O'zbekiston fuqarolari", "🌍 Xorijiy fuqarolar", "🧮 Narxni hisoblash", "⬅️ Orqaga"),
        "kz": ("🇺🇿 Өзбекстан азаматтары", "🌍 Шетел азаматтары", "🧮 Құнын есептеу", "⬅️ Артқа"),
    }[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(labels[0], callback_data="rooms_uz")],
        [InlineKeyboardButton(labels[1], callback_data="rooms_foreign")],
        [InlineKeyboardButton(labels[2], callback_data="calc_start")],
        [InlineKeyboardButton(labels[3], callback_data="back_main")],
    ])


def rooms_type_keyboard(lang, category):
    back_cb = f"rooms_{category}"
    labels = {
        "ru": (
            "👨‍👩‍👧 Для взрослых",
            "👶 Для детей (до 10 лет)",
            "⬅️ Назад"
        ),
        "uz": (
            "👨‍👩‍👧 Kattalar uchun",
            "👶 Bolalar uchun (10 yoshgacha)",
            "⬅️ Orqaga"
        ),
        "kz": (
            "👨‍👩‍👧 Ересектер үшін",
            "👶 Балалар үшін (10 жасқа дейін)",
            "⬅️ Артқа"
        ),
    }[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(labels[0], callback_data=f"rooms_{category}_adult")],
        [InlineKeyboardButton(labels[1], callback_data=f"rooms_{category}_child")],
        [InlineKeyboardButton(labels[2], callback_data="menu_rooms")],
    ])


def diagnostics_keyboard(lang):
    labels = {
        "ru": ("🧲 МРТ 1.5Т", "🧲 МРТ 3Т", "🖥 МСКТ 256", "🖥 МСКТ 128",
               "📡 УЗИ", "🔬 Лаборатория", "🩺 Маммография", "🫀 Фиброскан", "⬅️ Назад"),
        "uz": ("🧲 МРТ 1.5Т", "🧲 МРТ 3Т", "🖥 МСКТ 256", "🖥 МСКТ 128",
               "📡 УЗИ", "🔬 Laboratoriya", "🩺 Mammografiya", "🫀 Fibroskan", "⬅️ Orqaga"),
        "kz": ("🧲 МРТ 1.5Т", "🧲 МРТ 3Т", "🖥 МСКТ 256", "🖥 МСКТ 128",
               "📡 УДЗ", "🔬 Зертхана", "🩺 Маммография", "🫀 Фибросканерлеу", "⬅️ Артқа"),
    }[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(labels[0], callback_data="diag_mrt15"),
         InlineKeyboardButton(labels[1], callback_data="diag_mrt3t")],
        [InlineKeyboardButton(labels[2], callback_data="diag_mskt256"),
         InlineKeyboardButton(labels[3], callback_data="diag_mskt128")],
        [InlineKeyboardButton(labels[4], callback_data="diag_other")],
        [InlineKeyboardButton(labels[5], callback_data="diag_lab")],
        [InlineKeyboardButton(labels[6], callback_data="diag_mammografiya"),
         InlineKeyboardButton(labels[7], callback_data="diag_fibroskan")],
        [InlineKeyboardButton(labels[8], callback_data="back_main")],
    ])


def mrt3t_groups_keyboard(lang):
    back = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
    d = load_data()
    buttons = []
    for i, group in enumerate(d["mrt_3t_groups"].keys()):
        buttons.append([InlineKeyboardButton(f"📋 {group}", callback_data=f"mrt3t_{i}")])
    buttons.append([InlineKeyboardButton(back, callback_data="menu_diagnostics")])
    return InlineKeyboardMarkup(buttons)


def guide_keyboard(lang):
    labels = {
        "ru": (
            "1️⃣ Порядок размещения",
            "2️⃣ Первый день лечения",
            "3️⃣ Лечение и порядок приёма Malxam",
            "4️⃣ Инфраструктура",
            "⚠️ Важные правила",
            "6️⃣ Что купить домой",
            "🏢 Медицинские услуги — ваше мнение",
            "⬅️ Назад",
        ),
        "uz": (
            "1️⃣ Joylashish tartibi",
            "2️⃣ Birinchi kun muolaja tartibi",
            "3️⃣ Davolanish va Malxam ichish tartibi",
            "4️⃣ Infrastruktura",
            "⚠️ Muhim qoidalar",
            "6️⃣ Uyga tafsiyaoma",
            "🏢 Tibbiy xizmatlar haqida fikringiz",
            "⬅️ Orqaga",
        ),
        "kz": (
            "1️⃣ Орналасу тәртібі",
            "2️⃣ Бірінші күн ем тәртібі",
            "3️⃣ Емдеу және Malxam ішу тәртібі",
            "4️⃣ Инфрақұрылым",
            "⚠️ Маңызды ережелер",
            "6️⃣ Үйге ұсыным",
            "🏢 Медициналық қызметтер туралы пікіріңіз",
            "⬅️ Артқа",
        ),
    }[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(labels[0], callback_data="guide_arrival")],
        [InlineKeyboardButton(labels[1], callback_data="guide_malham")],
        [InlineKeyboardButton(labels[2], callback_data="g_step_1")],
        [InlineKeyboardButton(labels[3], callback_data="guide_infrastructure")],
        [InlineKeyboardButton(labels[4], callback_data="guide_muhim_qoidalar")],
        [InlineKeyboardButton(labels[5], callback_data="guide_shopping")],
        [InlineKeyboardButton(labels[6], callback_data="guide_feedback")],
        [InlineKeyboardButton(labels[7], callback_data="back_main")],
    ])


def clinic_submenu_keyboard(lang):
    labels = {
        "ru": (
            "📋 Общая информация",
            "👨‍⚕️ Главный врач",
            "👥 Наша команда",
            "🩺 Список болезней",
            "🎥 Видео",
            "📜 Сертификаты",
            "📖 История клиники",
            "🌿 Малхам и процедуры",
            "⬅️ Назад"
        ),
        "uz": (
            "📋 Umumiy ma'lumot",
            "👨‍⚕️ Bosh shifokor",
            "👥 Jamoamiz",
            "🩺 Kasalliklar ro'yxati",
            "🎥 Videolar",
            "📜 Sertifikatlar",
            "📖 Klinika tarixi",
            "🌿 Малхам va muolajalar",
            "⬅️ Orqaga"
        ),
        "kz": (
            "📋 Жалпы ақпарат",
            "👨‍⚕️ Бас дәрігер",
            "👥 Біздің команда",
            "🩺 Аурулар тізімі",
            "🎥 Бейнелер",
            "📜 Сертификаттар",
            "📖 Клиника тарихы",
            "🌿 Малхам и процедуры",
            "⬅️ Артқа"
        ),
    }[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(labels[0], callback_data="clinic_info")],
        [InlineKeyboardButton(labels[1], callback_data="menu_doctor"),
         InlineKeyboardButton(labels[2], callback_data="menu_staff")],
        [InlineKeyboardButton(labels[3], callback_data="menu_diseases")],
        [InlineKeyboardButton(labels[7], callback_data="malham_va_muolajalar")],
        [InlineKeyboardButton(labels[4], callback_data="clinic_video")],
        [InlineKeyboardButton(labels[5], callback_data="clinic_certs")],
        [InlineKeyboardButton(labels[6], callback_data="clinic_history")],
        [InlineKeyboardButton(labels[8], callback_data="back_main")],
    ])


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
    # Foydalanuvchini saqlash
    user = update.effective_user
    d = load_data()
    users = d.get("users", {})
    user_id = str(user.id)
    if user_id not in users:
        users[user_id] = {
            "id": user.id,
            "name": user.full_name,
            "username": f"@{user.username}" if user.username else "—",
            "lang": "—",
        }
        d["users"] = users
        save_data(d)

    # ── Deep Linking: ?start=PARAM bo'lsa, tilni tanlagandan keyin shu bo'limga yo'naltirish uchun saqlaymiz ──
    if context.args:
        context.user_data["deep_link_target"] = context.args[0]

    await update.message.reply_text(
        "👋 Добро пожаловать / Xush kelibsiz / Қош келдіңіз!\n\n🌐 Выберите язык / Tilni tanlang / Тілді таңдаңыз:",
        reply_markup=lang_keyboard()
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, override_data: str = None):
    query = update.callback_query
    if not override_data:
        await query.answer()
    data = override_data if override_data else query.data
    logger.info(f"CALLBACK: data='{data}'")
    d = load_data()
    lang = get_lang(context)
    phone = d["contacts"]["phone1"]
    chat_id = query.message.chat_id

    # ── Til tanlash ──
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        context.user_data["lang"] = lang
        # User tilini saqlash
        user = query.from_user
        d2 = load_data()
        users = d2.get("users", {})
        uid = str(user.id)
        if uid not in users:
            users[uid] = {"id": user.id, "name": user.full_name,
                         "username": f"@{user.username}" if user.username else "—", "lang": lang}
        else:
            users[uid]["lang"] = lang
        d2["users"] = users
        save_data(d2)

        # ── Deep Linking: agar /start parametri bilan kelgan bo'lsa, shu bo'limga yo'naltiramiz ──
        target = context.user_data.pop("deep_link_target", None)
        DEEP_LINK_MAP = {
            "guide": "menu_guide",
            "feedback": "guide_feedback",
            "rooms": "menu_rooms",
            "wards": "menu_wards",
            "doctor": "doctor_question",
            "diagnostics": "menu_diagnostics",
            "faq": "menu_faq",
            "results": "get_results",
        }
        if target in DEEP_LINK_MAP:
            return await callback_handler(update, context, override_data=DEEP_LINK_MAP[target])

        welcome = {
            "ru": "🏥 Клиника *Эргаш-Ота* — Каттакурган\n\nВыберите раздел:",
            "uz": "🏥 *Эргаш-Ота* klinikasi — Kattaqo'rg'on\n\nBo'limni tanlang:",
            "kz": "🏥 *Эргаш-Ота* клиникасы — Каттақурғон\n\nБөлімді таңдаңыз:",
        }[lang]
        await query.edit_message_text(welcome, parse_mode="Markdown",
                                      reply_markup=main_menu_keyboard(lang, update.effective_user.id if update.effective_user else 0))

    # ── Orqaga ──
    elif data == "back_main":
        context.user_data["state"] = None
        title = {
            "ru": "🏥 Клиника *Эргаш-Ота*\n\nВыберите раздел:",
            "uz": "🏥 *Эргаш-Ота* klinikasi\n\nBo'limni tanlang:",
            "kz": "🏥 *Эргаш-Ота* клиникасы\n\nБөлімді таңдаңыз:",
        }[lang]
        await query.edit_message_text(title, parse_mode="Markdown",
                                      reply_markup=main_menu_keyboard(lang, update.effective_user.id if update.effective_user else 0))

    # ── FAQ ──
    elif data in ("menu_faq",) or data.startswith("faq_") or data in ("m_kelish_tartibi", "back_delete_registration", "q_no_surgery", "back_delete_surgery_question", "q_diet_food", "back_delete_diet_question", "q_work_hours", "back_delete_work_hours"):
        await handle_faq_callbacks(query, context, data, lang)

    # ── Booking ──
    elif data == "book_confirm":
        btype_now = context.user_data.get("booking_type", "statsionar")
        if btype_now in ("transfer", "excursion"):
            # Transfer va excursion confirm ni to'g'ridan-to'g'ri hal qilamiz
            booking = context.user_data.get("booking", {})
            user = query.from_user
            username = f"@{user.username}" if user.username else "—"
            phone = d["contacts"]["phone1"]

            if btype_now == "transfer":
                fr = booking.get("from", "—")
                sana = booking.get("sana", "—")
                kishi = booking.get("kishi", "—")
                phone_num = booking.get("phone", "—")
                success = {
                    "ru": f"🎉 *Заявка принята!*\n\n📍 Откуда: {fr}\n📅 Дата: {sana}\n👥 Человек: {kishi}\n📞 {phone_num}\n\nОператор свяжется с вами.\n📞 {phone}",
                    "uz": f"🎉 *Ariza qabul qilindi!*\n\n📍 Qayerdan: {fr}\n📅 Sana: {sana}\n👥 Kishi: {kishi}\n📞 {phone_num}\n\nOperator siz bilan bog'lanadi.\n📞 {phone}",
                    "kz": f"🎉 *Өтінім қабылданды!*\n\n📍 Қайдан: {fr}\n📅 Күні: {sana}\n👥 Адам: {kishi}\n📞 {phone_num}\n\nОператор байланысады.\n📞 {phone}",
                }[lang]
                await query.edit_message_text(success, parse_mode="Markdown", reply_markup=back_keyboard(lang))
                lid = (f"🚗 *TRANSFER LID*\n\n"
                       f"📍 Qayerdan: {fr}\n📅 Sana: {sana}\n"
                       f"👥 Kishi: {kishi}\n📞 Telefon: {phone_num}\n"
                       f"💬 Telegram: {username}\n🌐 Til: {lang.upper()}\n\n"
                       f"🟢 QO'NG'IROQ QILING!")
                await send_lid(context, TRANSFER_CHANNEL, lid)

            elif btype_now == "excursion":
                city = booking.get("city", "—")
                sana = booking.get("sana", "—")
                kishi = booking.get("kishi", "—")
                phone_num = booking.get("phone", "—")
                success = {
                    "ru": f"🎉 *Заявка принята!*\n\n🕌 {city}\n📅 Дата: {sana}\n👥 Человек: {kishi}\n📞 {phone_num}\n\nОператор свяжется с вами.\n📞 {phone}",
                    "uz": f"🎉 *Ariza qabul qilindi!*\n\n🕌 {city}\n📅 Sana: {sana}\n👥 Kishi: {kishi}\n📞 {phone_num}\n\nOperator siz bilan bog'lanadi.\n📞 {phone}",
                    "kz": f"🎉 *Өтінім қабылданды!*\n\n🕌 {city}\n📅 Күні: {sana}\n👥 Адам: {kishi}\n📞 {phone_num}\n\nОператор байланысады.\n📞 {phone}",
                }[lang]
                await query.edit_message_text(success, parse_mode="Markdown", reply_markup=back_keyboard(lang))
                lid = (f"🕌 *EKSKURSIYA LID*\n\n"
                       f"🏛 Yo'nalish: {city}\n📅 Sana: {sana}\n"
                       f"👥 Kishi: {kishi}\n📞 Telefon: {phone_num}\n"
                       f"💬 Telegram: {username}\n🌐 Til: {lang.upper()}\n\n"
                       f"🟢 QO'NG'IROQ QILING!")
                await send_lid(context, TRANSFER_CHANNEL, lid)

            context.user_data["booking"] = {}
            context.user_data["booking_step"] = None
            context.user_data["booking_type"] = None
        else:
            await handle_booking_callbacks(query, context, data, lang, chat_id)

    elif data == "menu_diagnostics":
        title = {
            "ru": "🧲 Выберите вид диагностики:",
            "uz": "🧲 Diagnostika turini tanlang:",
            "kz": "🧲 Диагностика түрін таңдаңыз:",
        }[lang]
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(chat_id=chat_id, text=title, reply_markup=diagnostics_keyboard(lang))

    elif data == "feedback_confirmed_start":
        text = {
            "ru": "🏢 <b>Обращение к руководству клиники</b>\n\nДля нас искренне важно мнение каждого пациента и ваше впечатление о нашей клинике!\n\nВаши отзывы, предложения или замечания помогают нам улучшать качество работы и сервиса. Каждое ваше обращение внимательно изучается лично Главным врачом.\n\n✨ Внесите свой вклад в развитие клиники! Пожалуйста, поделитесь своими мыслями, предложениями или замечаниями ниже.",
            "uz": "🏢 <b>Klinika rahbariyatiga murojaat</b>\n\nBiz uchun har bir bemorimizning fikri va taassurotlari juda qadrli!\n\nSizning takliflaringiz yoki duch kelgan kamchiliklaringiz haqidagi mulohazalaringiz klinikamiz faoliyatini yanada yaxshilashga yordam beradi. Har bir murojaat shaxsan Bosh shifokor nazoratida to'liq o'rganib chiqiladi.\n\n✨ Klinikamiz rivojiga o'z hissangizni qo'shing! O'z taklif, mulohaza yoki e'tirozlaringizni pastda yozib qoldiring.",
            "kz": "🏢 <b>Клиника басшылығына өтініш</b>\n\nБіз үшін әрбір емделушіміздің пікірі мен алған әсері өте құнды!\n\nСіздің ұсыныстарыңыз бен байқалған кемшіліктер туралы пікірлеріңіз клиникамыздың жұмысын жақсартуға көмектеседі. Әрбір өтініш Бас дәрігердің жеке бақылауымен мұқият зерттеледі.\n\n✨ Клиникамыздың дамуына өз үлесіңізді қосыңыз! Төменде өз ұсыныстарыңызды, пікірлеріңізді немесе ескертулеріңізді қалдырыңыз.",
        }[lang]
        placeholder = {
            "ru": "Пишите только предложения и жалобы...",
            "uz": "Faqat taklif va shikoyat yozing...",
            "kz": "Тек ұсыныстар мен шағымдарды жазыңыз...",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_guide")]])
        context.user_data["state"] = "FEEDBACK_WAITING"
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)
        from telegram import ForceReply
        await context.bot.send_message(
            chat_id=chat_id, text="👇",
            reply_markup=ForceReply(selective=True, input_field_placeholder=placeholder)
        )

    elif data in ("menu_booking", "book_statsionar", "book_diagnostika", "calc_book_statsionar") or \
         data.startswith("diag_book_") or data.startswith("excursion_book_"):
        await handle_booking_callbacks(query, context, data, lang, chat_id)

    # ── Bemor qo'llanmasi ──
    elif data == "menu_guide":
        context.user_data["state"] = None
        title = {
            "ru": "📖 *Руководство пациента*\n\nВыберите раздел:",
            "uz": "📖 *Bemor uchun qo'llanma*\n\nBo'limni tanlang:",
            "kz": "📖 *Науқас нұсқаулығы*\n\nБөлімді таңдаңыз:",
        }[lang]
        await query.edit_message_text(title, parse_mode="Markdown",
                                      reply_markup=guide_keyboard(lang))

    elif data.startswith("guide_") and data not in (
        "guide_step3", "guide_step3_s2", "guide_step3_s3",
        "guide_step3_s4", "guide_step3_foreign", "guide_step3_local",
    ):
        section = data.replace("guide_", "")
        guide_data_all = d.get("guide", {})

        # Arrival bosqichlari alohida
        if section == "arrival":
            step1 = guide_data_all.get("arrival_step1", {})
            text = step1.get(lang, step1.get("ru", ""))
            next_label = {"ru": "➡️ Далее (2/3)", "uz": "➡️ Keyingi (2/3)", "kz": "➡️ Келесі (2/3)"}[lang]
            back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(next_label, callback_data="guide_arrival_step2")],
                [InlineKeyboardButton(back_label, callback_data="menu_guide")],
            ])
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
            # Video
            vid = step1.get("video", "")
            if vid:
                try:
                    await context.bot.send_video(chat_id=chat_id, video=vid)
                except Exception:
                    pass

        elif section == "arrival_step2":
            step2 = guide_data_all.get("arrival_step2", {})
            text = step2.get(lang, step2.get("ru", ""))
            next_label = {"ru": "➡️ Далее (3/3)", "uz": "➡️ Keyingi (3/3)", "kz": "➡️ Келесі (3/3)"}[lang]
            back_label = {"ru": "⬅️ Назад (1/3)", "uz": "⬅️ Orqaga (1/3)", "kz": "⬅️ Артқа (1/3)"}[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(next_label, callback_data="guide_arrival_step3")],
                [InlineKeyboardButton(back_label, callback_data="guide_arrival")],
            ])
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
            vid = step2.get("video", "")
            if vid:
                try:
                    await context.bot.send_video(chat_id=chat_id, video=vid)
                except Exception:
                    pass

        elif section == "arrival_step3":
            step3 = guide_data_all.get("arrival_step3", {})
            text = step3.get(lang, step3.get("ru", ""))
            guide_label = {"ru": "📖 К руководству", "uz": "📖 Qo'llanmaga", "kz": "📖 Нұсқаулыққа"}[lang]
            back_label = {"ru": "⬅️ Назад (2/3)", "uz": "⬅️ Orqaga (2/3)", "kz": "⬅️ Артқа (2/3)"}[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(guide_label, callback_data="menu_guide")],
                [InlineKeyboardButton(back_label, callback_data="guide_arrival_step2")],
            ])
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
            vid = step3.get("video", "")
            if vid:
                try:
                    await context.bot.send_video(chat_id=chat_id, video=vid)
                except Exception:
                    pass

        elif section == "malham":
            # 1-sahifa: Xonaga joylashish
            next_label = {"ru": "➡️ Далее", "uz": "➡️ Keyingi", "kz": "➡️ Келесі"}[lang]
            back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
            text = {
                "ru": (
                    "🌙 *2️⃣ Первый день лечения*\n\n"
                    "1️⃣ *Вы заселились в палату*\n"
                    "✔️ Медсёстры размещают вас в палате\n"
                    "✔️ Объясняют распорядок лечения\n"
                    "✔️ Сообщают время процедур"
                ),
                "uz": (
                    "🌙 *2️⃣ Birinchi kun muolaja tartibi*\n\n"
                    "1️⃣ *Siz Xonaga joylashdingiz*\n"
                    "✔️ Hamshiralar sizni xonaga joylashtiradi\n"
                    "✔️ Davolanish tartibi tushuntiriladi\n"
                    "✔️ Muolajalar vaqti haqida ma'lumot beriladi"
                ),
                "kz": (
                    "🌙 *2️⃣ Бірінші күн ем тәртібі*\n\n"
                    "1️⃣ *Сіз палатаға орналастыңыз*\n"
                    "✔️ Медбикелер сізді палатаға орналастырады\n"
                    "✔️ Емдеу тәртібі түсіндіріледі\n"
                    "✔️ Процедуралар уақыты туралы хабарланады"
                ),
            }[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(next_label, callback_data="guide_malham_step2")],
                [InlineKeyboardButton(back_label, callback_data="menu_guide")],
            ])
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

        elif section == "malham_step2":
            # 2-sahifa: Organizimni tozalash
            next_label = {"ru": "➡️ Далее", "uz": "➡️ Keyingi", "kz": "➡️ Келесі"}[lang]
            back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
            text = {
                "ru": (
                    "🌙 *2️⃣ Первый день лечения*\n\n"
                    "2️⃣ *Очищение организма*\n"
                    "✔️ Примерно через 1,5–2 часа проводится клизма\n"
                    "✔️ Рекомендуется пить яблочный сок\n"
                    "✔️ Принимаются травяные чаи"
                ),
                "uz": (
                    "🌙 *2️⃣ Birinchi kun muolaja tartibi*\n\n"
                    "2️⃣ *Organizimni tozalash jarayoni*\n"
                    "✔️ Taxminan 1,5 – 2 soatdan keyin klizma muolajasi qilinadi\n"
                    "✔️ Olma sharbatini ichish tavsiya etiladi\n"
                    "✔️ Giyohli choylar qabul qilinadi"
                ),
                "kz": (
                    "🌙 *2️⃣ Бірінші күн ем тәртібі*\n\n"
                    "2️⃣ *Ағзаны тазарту процесі*\n"
                    "✔️ Шамамен 1,5–2 сағаттан кейін клизма жасалады\n"
                    "✔️ Алма шырынын ішу ұсынылады\n"
                    "✔️ Шөптен жасалған шайлар қабылданады"
                ),
            }[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(next_label, callback_data="guide_malham_step3")],
                [InlineKeyboardButton(back_label, callback_data="guide_malham")],
            ])
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

        elif section == "malham_step3":
            # 3-sahifa: Ertangi davolanishga tayyorlash
            back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
            guide_label = {"ru": "📖 К руководству", "uz": "📖 Qo'llanmaga", "kz": "📖 Нұсқаулыққа"}[lang]
            text = {
                "ru": (
                    "🌙 *2️⃣ Первый день лечения*\n\n"
                    "3️⃣ *Подготовка к завтрашнему лечению*\n"
                    "🌿 Ваша процедура первого дня:\n"
                    "• очищение организма\n"
                    "• подготовка к приёму мальхама\n\n"
                    "для этого и проводится.\n\n"
                    "📍 Со следующего дня начинается процесс лечения и приём Мальхама."
                ),
                "uz": (
                    "🌙 *2️⃣ Birinchi kun muolaja tartibi*\n\n"
                    "3️⃣ *Ertangi davolanishga tayyorlash*\n"
                    "🌿 Sizning birinchi kun muolajangiz:\n"
                    "• organizmni tozalash\n"
                    "• malham ichishga tayyorlash\n\n"
                    "uchun amalga oshiriladi.\n\n"
                    "📍 Ertangi kundan boshlab davolanishning Malham qabul qilish jarayoni boshlanadi."
                ),
                "kz": (
                    "🌙 *2️⃣ Бірінші күн ем тәртібі*\n\n"
                    "3️⃣ *Ертеңгі емге дайындық*\n"
                    "🌿 Бірінші күнгі процедураңыз:\n"
                    "• ағзаны тазарту\n"
                    "• мальхам қабылдауға дайындық\n\n"
                    "үшін жасалады.\n\n"
                    "📍 Келесі күннен бастап емдеудің Мальхам қабылдау процесі басталады."
                ),
            }[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(guide_label, callback_data="menu_guide")],
                [InlineKeyboardButton(back_label, callback_data="guide_malham_step2")],
            ])
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

        elif section == "step3":
            # 1-QADAM: Ertalabki navbat
            d2 = load_data()
            photo = d2.get("guide_step3_p1_photo", "")
            next_label = {"ru": "➡️ Далее (2/4)", "uz": "➡️ Keyingi (2/4)", "kz": "➡️ Келесі (2/4)"}[lang]
            back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
            text = {
                "ru": (
                    "🕒 <b>Шаг 1: Утренняя очередь и обследования (08:00)</b>\n\n"
                    "Ваш второй день в клинике, процесс приёма Malxam и дополнительные процедуры:\n"
                    "• <b>Лаборатория и УЗИ:</b> Пациенты занимают очередь в отделе регистрации утром в 08:00 для сдачи лабораторных анализов и прохождения УЗИ.\n"
                    "• <b>Процедурная книжка:</b> Вы сможете получать все дополнительные процедуры, разрешённые и назначенные врачом в процедурной книжке."
                ),
                "uz": (
                    "🕒 <b>1-Qadam: Ertalabki navbat va Tekshiruvlar (Soat 08:00)</b>\n\n"
                    "Klinikadagi ikkinchi kuningiz — Malxam ichish jarayoni va qo'shimcha muolajalar:\n"
                    "• <b>Laboratoriya va UZI:</b> Bemorlar laboratoriya tahlillari hamda UZI (EHO) ko'rigidan o'tish uchun ertalab soat 08:00 da Registratsiya bo'limidan navbat olib ko'rikdan o'tadi.\n"
                    "• <b>Muolaja daftarchasi:</b> Muolaja daftarchada shifokor tomonidan ruxsat etilgan va buyurilgan barcha qo'shimcha muolajalarni olishingiz mumkin bo'ladi."
                ),
                "kz": (
                    "🕒 <b>1-Қадам: Таңғы кезек және тексерулер (Сағат 08:00)</b>\n\n"
                    "Клиникадағы екінші күніңіз — Malxam ішу процесі және қосымша ем-шаралар:\n"
                    "• <b>Лаборатория және УЗИ:</b> Емделушілер зертханалық талдаулар мен УЗИ тексеруінен өту үшін таңғы сағат 08:00-де Тіркеу бөлімінен кезек алып тексеруден өтеді.\n"
                    "• <b>Емдеу кітапшасы:</b> Дәрігер рұқсат еткен және тағайындаған барлық қосымша ем-шараларды емдеу кітапшасы арқылы алуыңызға болады."
                ),
            }[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(next_label, callback_data="guide_step3_s2")],
                [InlineKeyboardButton(back_label, callback_data="menu_guide")],
            ])
            await query.message.delete()
            if photo:
                await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
            else:
                await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

        elif section == "step3_s2":
            # 2-QADAM: Malxam ichish va rangli kartochkalar
            d2 = load_data()
            photo = d2.get("guide_step3_p2_photo", "")
            next_label = {"ru": "➡️ Далее (3/4)", "uz": "➡️ Keyingi (3/4)", "kz": "➡️ Келесі (3/4)"}[lang]
            back_label = {"ru": "⬅️ Назад (1/4)", "uz": "⬅️ Orqaga (1/4)", "kz": "⬅️ Артқа (1/4)"}[lang]
            foreign_label = {"ru": "🌍 Иностранные граждане", "uz": "🌍 Chet el fuqarolari", "kz": "🌍 Шет ел азаматтары"}[lang]
            local_label   = {"ru": "🇺🇿 Граждане Узбекистана", "uz": "🇺🇿 O'zbekiston fuqarolari", "kz": "🇺🇿 Өзбекстан азаматтары"}[lang]
            text = {
                "ru": (
                    "🌈 <b>Шаг 2: Порядок приёма Malxam и цветные карточки</b>\n\n"
                    "Второй день — это основной день, когда начинается приём Malxam.\n\n"
                    "⚠️ <b>САМОЕ ВАЖНОЕ ПРАВИЛО:</b> Перед приёмом Malxam <b>как минимум 1.5 часа абсолютно ничего нельзя есть (быть натощак)!</b> Это максимально увеличивает эффект Malxam.\n\n"
                    "• 💳 После оплаты вам выдаются специальные <b>цветные карточки</b>.\n"
                    "• 🗓 Время приёма Malxam и последовательность цветов меняются по дням недели. Вы заходите строго по цвету и номеру вашей карточки.\n\n"
                    "👇 Ознакомьтесь с графиком по кнопкам ниже:"
                ),
                "uz": (
                    "🌈 <b>2-Qadam: Malxam ichish tartibi va Rangli kartochkalar</b>\n\n"
                    "Ikkinchi kun — Malxam ichish boshlanadigan asosiy kun hisoblanadi.\n\n"
                    "⚠️ <b>ENG MUHIM QOIDA:</b> Malxam ichishdan oldin <b>kamida 1.5 soat davomida mutlaqo hech narsa yemaslik (och qoringa bo'lish) kerak!</b> Bu Malxamning ta'sirini maksimal darajada oshiradi.\n\n"
                    "• 💳 To'lovni amalga oshirganingizdan so'ng, qo'lingizga maxsus <b>rangli kartochkalar</b> beriladi.\n"
                    "• 🗓 Malxam ichish vaqtlari va ranglar ketma-ketligi haftaning kunlariga qarab o'zgarib turadi. Siz kartochkangizning rangi va raqamiga qarab o'z vaqtingizda kirasiz.\n\n"
                    "👇 Quyidagi tugmalar orqali grafik va aniq vaqtlar bilan tanishing:"
                ),
                "kz": (
                    "🌈 <b>2-Қадам: Malxam ішу тәртібі және түрлі-түсті карточкалар</b>\n\n"
                    "Екінші күн — Malxam ішу басталатын негізгі күн болып саналады.\n\n"
                    "⚠️ <b>ЕҢ МАҢЫЗДЫ ЕРЕЖЕ:</b> Malxam ішер алдында <b>кем дегенде 1.5 сағат бұрын мүлдем ештеңе жемеу керек (аш қарында болу шарт)!</b> Бұл Malxam-ның әсерін барынша арттырады.\n\n"
                    "• 💳 Төлем жасағаннан кейін қолыңызға арнайы <b>түрлі-түсті карточкалар</b> беріледі.\n"
                    "• 🗓 Malxam ішу уақыты мен түстердің реттілігі апта күндеріне байланысты өзгеріп тұрады. Карточкаңыздың түсі мен нөміріне сәйкес өз уақытыңызда кіресіз.\n\n"
                    "👇 Төмендегі түймелер арқылы кестемен танысыңыз:"
                ),
            }[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(foreign_label, callback_data="guide_step3_foreign")],
                [InlineKeyboardButton(local_label,   callback_data="guide_step3_local")],
                [InlineKeyboardButton(next_label,    callback_data="guide_step3_s3")],
                [InlineKeyboardButton(back_label,    callback_data="g_step_1")],
            ])
            await query.message.delete()
            if photo:
                await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
            else:
                await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

        elif section == "step3_foreign":
            # 2a: Chet el fuqarolari grafigi
            d2 = load_data()
            photo = d2.get("guide_step3_foreign_photo", "")
            back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
            next_label = {"ru": "➡️ Далее (3/4)", "uz": "➡️ Keyingi (3/4)", "kz": "➡️ Келесі (3/4)"}[lang]
            text = {
                "ru": "🌍 <b>График для иностранных граждан</b>\n\nИностранные граждане принимают Malxam начиная с <b>10:00</b> утра согласно цвету своей карточки.",
                "uz": "🌍 <b>Chet el fuqarolari uchun grafik</b>\n\nChet el fuqarolari Malxamni ertalab soat <b>10:00</b> dan boshlab kartochkalarining rangi bo'yicha ichadi.",
                "kz": "🌍 <b>Шет ел азаматтары үшін кесте</b>\n\nШет ел азаматтары Malxam-ды таңғы сағат <b>10:00</b>-ден бастап карточкаларының түсіне сәйкес ішеді.",
            }[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(next_label,  callback_data="guide_step3_s3")],
                [InlineKeyboardButton(back_label,  callback_data="guide_step3_s2")],
            ])
            await query.message.delete()
            if photo:
                await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
            else:
                await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

        elif section == "step3_local":
            # 2b: O'zbekiston fuqarolari grafigi
            d2 = load_data()
            photo = d2.get("guide_step3_local_photo", "")
            back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
            next_label = {"ru": "➡️ Далее (3/4)", "uz": "➡️ Keyingi (3/4)", "kz": "➡️ Келесі (3/4)"}[lang]
            text = {
                "ru": "🇺🇿 <b>График для граждан Узбекистана</b>\n\nГраждане Узбекистана принимают Malxam начиная с <b>13:00 или 14:00</b> согласно цвету своей карточки.",
                "uz": "🇺🇿 <b>O'zbekiston fuqarolari uchun grafik</b>\n\nO'zbekiston fuqarolari Malxamni soat <b>13:00 yoki 14:00</b> dan boshlab kartochkalarining rangi bo'yicha ichadi.",
                "kz": "🇺🇿 <b>Өзбекстан азаматтары үшін кесте</b>\n\nӨзбекстан азаматтары Malxam-ды сағат <b>13:00 немесе 14:00</b>-ден бастап карточкаларының түсіне сәйкес ішеді.",
            }[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(next_label,  callback_data="guide_step3_s3")],
                [InlineKeyboardButton(back_label,  callback_data="guide_step3_s2")],
            ])
            await query.message.delete()
            if photo:
                await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
            else:
                await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

        elif section == "step3_s3":
            # 3-QADAM: Grelka va klizma
            d2 = load_data()
            photo = d2.get("guide_step3_p3_photo", "")
            next_label = {"ru": "➡️ Далее (4/4)", "uz": "➡️ Keyingi (4/4)", "kz": "➡️ Келесі (4/4)"}[lang]
            back_label = {"ru": "⬅️ Назад (2/4)", "uz": "⬅️ Orqaga (2/4)", "kz": "⬅️ Артқа (2/4)"}[lang]
            text = {
                "ru": (
                    "🔥 <b>Шаг 3: Самые важные золотые правила после Malxam!</b>\n\n"
                    "Режим после приёма Malxam — часть лечения, дающая наивысший результат. Строго соблюдайте:\n\n"
                    "1️⃣ 🛏 <b>Применение грелки (Самый важный этап):</b> Сразу после приёма Malxam необходимо пройти в палату и <b>как минимум 1,5–2 часа лежать неподвижно, приложив грелку к правому подреберью (область печени)</b>.\n"
                    "2️⃣ 🩺 <b>Процедура клизмы:</b> После грелки — не спеша отправляйтесь в клизменную комнату для очистительной процедуры.\n"
                    "3️⃣ 🚶‍♂️ <b>После процедур:</b> Рекомендуется вести активный образ жизни, принимать назначенные процедуры и пить травяные чаи в фито-баре."
                ),
                "uz": (
                    "🔥 <b>3-Qadam: Malxamdan keyingi eng muhim oltin qoidalar!</b>\n\n"
                    "Malxamni ichib bo'lgandan keyingi tartib — davolanishning eng yuqori natija beradigan qismi. Qat'iy amal qiling:\n\n"
                    "1️⃣ 🛏 <b>Grelka qo'yish (Eng muhim joyi):</b> Malxamni ichgach, darhol xonangizga borib, <b>kamida 1.5–2 soat davomida o'ng qovurg'a ostiga (jigar sohasiga) grelka qo'yib</b> qimirlamay yotishingiz shart.\n"
                    "2️⃣ 🩺 <b>Klizma muolajasi:</b> Grelkada yotib bo'lgandan keyin, klizma xonasiga borib navbatdagi tozalash muolajasini olasiz.\n"
                    "3️⃣ 🚶‍♂️ <b>Muolajadan so'ng:</b> Kun davomida faol harakatda bo'lish, qo'shimcha muolajalarni olish va fito-bardagi giyohli choylarni ichib yurish tavsiya etiladi."
                ),
                "kz": (
                    "🔥 <b>3-Қадам: Malxamдан кейінгі ең маңызды алтын ережелер!</b>\n\n"
                    "Malxam ішкеннен кейінгі күтім — емнің ең жоғары нәтиже беретін бөлігі. Қатаң сақтаңыз:\n\n"
                    "1️⃣ 🛏 <b>Грелка басу (Ең маңызды кезең):</b> Malxam ішкен бойда бірден бөлмеңізге барып, <b>кем дегенде 1,5–2 сағат бойы оң жақ қабырға астына (бауыр тұсына) грелка басып</b> қозғалмай жатуыңыз шарт.\n"
                    "2️⃣ 🩺 <b>Клизма ем-шарасы:</b> Грелкамен жатып болғаннан кейін — клизма бөлмесіне барып кезекті тазарту ем-шарасын аласыз.\n"
                    "3️⃣ 🚶‍♂️ <b>Ем-шарадан кейін:</b> Күн бойы белсенді қозғалыста болу, тағайындалған ем-шараларды алу және фито-бардағы шөп шайларын ішу ұсынылады."
                ),
            }[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(next_label, callback_data="guide_step3_s4")],
                [InlineKeyboardButton(back_label, callback_data="guide_step3_s2")],
            ])
            await query.message.delete()
            if photo:
                await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
            else:
                await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

        elif section == "step3_s4":
            # 4-QADAM: Navbat orasidagi bo'sh vaqt
            d2 = load_data()
            photo = d2.get("guide_step3_p4_photo", "")
            guide_label = {"ru": "📖 К руководству", "uz": "📖 Qo'llanmaga", "kz": "📖 Нұсқаулыққа"}[lang]
            back_label  = {"ru": "⬅️ Назад (3/4)", "uz": "⬅️ Orqaga (3/4)", "kz": "⬅️ Артқа (3/4)"}[lang]
            text = {
                "ru": (
                    "⏳ <b>Шаг 4: Эффективное использование времени между очередями</b>\n\n"
                    "• 🕒 Процедура выдачи Malxam начинается утром в 10:00. Сначала пьют те, кто уезжает, затем начинается последовательность цветов.\n"
                    "• 🔔 Если по вашей карточке очередь выпадает на середину дня, используйте свободное время с пользой!\n"
                    "• 💆‍♂️ В этот промежуток вы можете принимать другие назначенные процедуры (Массаж, Нуга Бест, Серагем и т.д.) или отдыхать в Фито-баре с травяным чаем."
                ),
                "uz": (
                    "⏳ <b>4-Qadam: Navbat orasidagi bo'sh vaqtdan unumli foydalanish</b>\n\n"
                    "• 🕒 Malxam berish jarayoni ertalab soat 10:00 dan boshlanadi. Birinchi bo'lib ketuvchilar ichadi, keyin ranglar ketma-ketligi boshlanadi.\n"
                    "• 🔔 Agar kartochkangiz bo'yicha navbatingiz tushdan keyin bo'lsa, ungacha bo'sh vaqtingizdan unumli foydalaning!\n"
                    "• 💆‍♂️ Shifokor buyurgan qo'shimcha muolajalarni (Massaj, Nuga Best, Seragem va h.k.) olishingiz yoki Fito-barda shifobaxsh choylardan ichib dam olishingiz mumkin."
                ),
                "kz": (
                    "⏳ <b>4-Қадам: Кезек арасындағы бос уақытты тиімді пайдалану</b>\n\n"
                    "• 🕒 Malxam беру процесі таңғы сағат 10:00-де басталады. Алдымен кететіндер ішеді, содан кейін түстердің реттілігі басталады.\n"
                    "• 🔔 Егер карточкаңыз бойынша кезегіңіз түстен кейін болса, оған дейінгі уақытты тиімді пайдаланыңыз!\n"
                    "• 💆‍♂️ Дәрігер тағайындаған қосымша ем-шараларды (Массаж, Нуга Бест, Серагем т.б.) алуыңызға немесе Фито-бардағы шөп шайларын ішіп демалуыңызға болады."
                ),
            }[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(guide_label, callback_data="menu_guide")],
                [InlineKeyboardButton(back_label,  callback_data="guide_step3_s3")],
            ])
            await query.message.delete()
            if photo:
                await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
            else:
                await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

        elif section == "shopping":
            text = {
                "ru": "🏠 *Рекомендации на дом*\n\nВыберите раздел:",
                "uz": "🏠 *Uyga tafsiyaoma*\n\nBo'limni tanlang:",
                "kz": "🏠 *Үйге ұсыным*\n\nБөлімді таңдаңыз:",
            }[lang]
            back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    {"ru": "ℹ️ Важные правила", "uz": "ℹ️ Muhim qoidalar", "kz": "ℹ️ Маңызды ережелер"}[lang],
                    callback_data="info_qoidalar")],
                [InlineKeyboardButton(
                    {"ru": "🚫 Что запрещено?", "uz": "🚫 Nimalar mumkin emas?", "kz": "🚫 Не тыйым салынған?"}[lang],
                    callback_data="info_taqiq")],
                [InlineKeyboardButton(
                    {"ru": "🍲 Меню питания", "uz": "🍲 Taomnoma", "kz": "🍲 Тамақтану мәзірі"}[lang],
                    callback_data="menu_taomnoma")],
                [InlineKeyboardButton(
                    {"ru": "🌿 Слабительная трава", "uz": "🌿 Surgi giyohi", "kz": "🌿 Іш жүргізетін шөп"}[lang],
                    callback_data="info_giyoh")],
                [InlineKeyboardButton(back_label, callback_data="menu_guide")],
            ])
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

        elif section == "infrastructure":
            d2 = load_data()
            INFRA_MENU_PHOTO = d2.get("infra_menu_photo", "")
            text = {
                "ru": "🏢 <b>Территория клиники и Корпуса</b>\n\nЧтобы не заблудиться и легко найти нужные процедурные кабинеты, выберите интересующий корпус:",
                "uz": "🏢 <b>Klinikamiz hududi va Korpuslar</b>\n\nAdashib ketmasligingiz va kerakli muolaja xonalarini osongina topishingiz uchun kerakli korpusni tanlang:",
                "kz": "🏢 <b>Клиника аумағы мен Корпустар</b>\n\nАдасып кетпей, керекті ем-шара бөлмелерін оңай табу үшін қажетті корпусты таңдаңыз:",
            }[lang]
            back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
            main_label = {"ru": "🏢 Главный корпус", "uz": "🏢 Asosiy korpus", "kz": "🏢 Бас корпус"}[lang]
            m_label    = {"ru": "🏥 Корпус М", "uz": "🏥 M korpus", "kz": "🏥 М корпусы"}[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(main_label, callback_data="infra_main_building")],
                [InlineKeyboardButton(m_label,    callback_data="infra_m_building")],
                [InlineKeyboardButton(back_label, callback_data="back_to_guide_main")],
            ])
            await query.message.delete()
            if INFRA_MENU_PHOTO:
                await context.bot.send_photo(chat_id=chat_id, photo=INFRA_MENU_PHOTO,
                                             caption=text, parse_mode="HTML", reply_markup=kb)
            else:
                await context.bot.send_message(chat_id=chat_id, text=text,
                                               parse_mode="HTML", reply_markup=kb)

        elif section == "feedback":
            warn_text = {
                "ru": "🏢 <b>Обращение к руководству клиники</b>\n\n⚠️ Внимание: этот раздел НЕ для анализов и не для вопросов о лечении!\n\nЗдесь принимаются только отзывы и предложения по качеству обслуживания администрации клиники.",
                "uz": "🏢 <b>Klinika rahbariyatiga murojaat</b>\n\n⚠️ Diqqat: bu bo'lim analizlar uchun EMAS va davolanish bo'yicha savollar uchun emas!\n\nBu yerda faqat ma'muriyatga xizmat sifati bo'yicha fikr-mulohaza va takliflar qabul qilinadi.",
                "kz": "🏢 <b>Клиника басшылығына өтініш</b>\n\n⚠️ Назар аударыңыз: бұл бөлім анализдер үшін ЕМЕС және емдеу туралы сұрақтар үшін емес!\n\nМұнда тек әкімшілікке қызмет сапасы бойынша пікір мен ұсыныстар қабылданады.",
            }[lang]
            confirm_label = {"ru": "✅ Понятно, продолжить", "uz": "✅ Tushunarli, davom etish", "kz": "✅ Түсінікті, жалғастыру"}[lang]
            back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(confirm_label, callback_data="feedback_confirmed_start")],
                [InlineKeyboardButton(back_label, callback_data="menu_guide")],
            ])
            try:
                await query.message.delete()
            except Exception:
                pass
            await context.bot.send_message(chat_id=chat_id, text=warn_text, parse_mode="HTML", reply_markup=kb)

        elif section == "muhim_qoidalar":
            text = {
                "uz": (
                    "⚠️ <b>Muhim qoidalar</b>\n\n"
                    "Hurmatli bemorlar! Siz klinikaga qabul qilinayotganda quyidagi tartib-qoidalarga rozilik bildirgan holda tilxat yozgansiz:\n\n"
                    "• Siz klinika hududidan <b>100 metr uzoqlashmaslik</b> majburiyatini olgansiz.\n"
                    "• Klinikadan uzoqlashish klinika tartib-qoidalariga <b>zid</b> hisoblanadi.\n\n"
                    "⚠️ <b>Eslatib o'tamiz:</b>\n"
                    "Agar siz klinika hududidan tashqariga chiqishingiz zarur bo'lganda:\n\n"
                    "1️⃣ Birinchi navbatda <b>klinika rahbariyati roziligi</b> bilan chiqishingizga ruxsat beriladi.\n"
                    "2️⃣ Xonangiz kalitini o'zingiz bilan olib chiqishingiz <b>qat'iyan man etiladi</b>.\n\n"
                    "Bunday holatda siz:\n"
                    "— Xona kalitini <b>binoning mas'ul xodimi xonasiga topshirishingiz</b> shart.\n\n"
                    "<i>Ushbu tartib barcha bemorlar uchun majburiy hisoblanadi.</i>"
                ),
                "ru": (
                    "⚠️ <b>Важные правила</b>\n\n"
                    "Уважаемые пациенты! При поступлении в клинику вы подписали согласие со следующими правилами:\n\n"
                    "• Вы взяли на себя обязательство <b>не удаляться от территории клиники более чем на 100 метров</b>.\n"
                    "• Удаление от клиники считается <b>нарушением</b> внутреннего распорядка.\n\n"
                    "⚠️ <b>Напоминаем:</b>\n"
                    "Если вам необходимо выйти за пределы территории клиники:\n\n"
                    "1️⃣ Выход разрешён только с <b>согласия руководства клиники</b>.\n"
                    "2️⃣ Брать ключ от палаты с собой <b>строго запрещено</b>.\n\n"
                    "В таком случае вы обязаны:\n"
                    "— <b>Сдать ключ от палаты ответственному сотруднику здания</b>.\n\n"
                    "<i>Данный порядок является обязательным для всех пациентов.</i>"
                ),
                "kz": (
                    "⚠️ <b>Маңызды ережелер</b>\n\n"
                    "Құрметті науқастар! Клиникаға қабылданған кезде сіз мына ережелерге келісіп, тілхат жаздыңыз:\n\n"
                    "• Сіз клиника аумағынан <b>100 метрден артық ұзамау</b> міндеттемесін алдыңыз.\n"
                    "• Клиникадан ұзау клиника тәртіп ережелеріне <b>қайшы</b> келеді.\n\n"
                    "⚠️ <b>Ескертеміз:</b>\n"
                    "Егер клиника аумағынан шығуыңыз қажет болса:\n\n"
                    "1️⃣ Ең алдымен <b>клиника басшылығының рұқсатымен</b> ғана шығуға болады.\n"
                    "2️⃣ Палата кілтін өзіңізбен алып шығу <b>қатаң тыйым салынады</b>.\n\n"
                    "Мұндай жағдайда сіз:\n"
                    "— Палата кілтін <b>ғимараттың жауапты қызметкері бөлмесіне тапсыруыңыз</b> шарт.\n\n"
                    "<i>Бұл тәртіп барлық науқастар үшін міндетті болып табылады.</i>"
                ),
            }[lang]
            back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_guide")]])
            try:
                await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
            except Exception:
                await query.message.delete()
                await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

        elif section == "rules":
            text = {
                "uz": (
                    "5️⃣ <b>Umumiy qoidalar</b>\n\n"
                    "👗 <b>Kiyim:</b>\n"
                    "• Qulay, erkin kiyim\n"
                    "• Massaj uchun — alohida to'plam (yog' ketmaydi!)\n\n"
                    "🚌 <b>Shaharga chiqish:</b>\n"
                    "• Ruxsat beriladi, lekin protsedura rejimini saqlang\n\n"
                    "🕐 <b>Kun tartibi:</b>\n"
                    "• Tushlik tanaffus — taxminan (resepshnga aniqlang)\n"
                    "• Payshanba — qisqa kun\n"
                    "• Musiqali kech: Payshanba va Yakshanba 21:00 da\n\n"
                    "🛏 <b>Xona tozalash:</b>\n"
                    "• Xodimlar tomonidan amalga oshiriladi\n\n"
                    "⚠️ <b>Muhim:</b>\n"
                    "O'zbekistonda hayot sur'ati boshqacha — sabr-toqatli bo'ling! 🌿"
                ),
                "ru": (
                    "5️⃣ <b>Общие правила</b>\n\n"
                    "👗 <b>Одежда:</b>\n"
                    "• Удобная, свободная одежда\n"
                    "• Для массажа — отдельный комплект (масло не отстирывается!)\n\n"
                    "🚌 <b>Выход в город:</b>\n"
                    "• Разрешается, но соблюдайте режим процедур\n\n"
                    "🕐 <b>Распорядок дня:</b>\n"
                    "• Обеденный перерыв — уточните на ресепшене\n"
                    "• Четверг — короткий день\n"
                    "• Музыкальный вечер: Четверг и Воскресенье в 21:00\n\n"
                    "🛏 <b>Уборка номера:</b>\n"
                    "• Производится персоналом\n\n"
                    "⚠️ <b>Важно:</b>\n"
                    "В Узбекистане темп жизни другой — будьте терпеливы! 🌿"
                ),
                "kz": (
                    "5️⃣ <b>Жалпы ережелер</b>\n\n"
                    "👗 <b>Киім:</b>\n"
                    "• Ыңғайлы, еркін киім\n"
                    "• Массаж үшін — бөлек жиынтық (май кетпейді!)\n\n"
                    "🚌 <b>Қалаға шығу:</b>\n"
                    "• Рұқсат етіледі, бірақ процедура режимін сақтаңыз\n\n"
                    "🕐 <b>Күн тәртібі:</b>\n"
                    "• Түскі үзіліс — ресепшеннен нақтылаңыз\n"
                    "• Бейсенбі — қысқа күн\n"
                    "• Музыкалы кеш: Бейсенбі және Жексенбі 21:00-де\n\n"
                    "🛏 <b>Бөлмені тазалау:</b>\n"
                    "• Қызметкерлер жүзеге асырады\n\n"
                    "⚠️ <b>Маңызды:</b>\n"
                    "Өзбекстанда өмір қарқыны басқаша — шыдамды болыңыз! 🌿"
                ),
            }[lang]
            back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_guide")]])
            try:
                await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
            except Exception:
                await query.message.delete()
                await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

        else:
            # Boshqa bo'limlar
            section_data = guide_data_all.get(section, {})
            text = section_data.get(lang, section_data.get("ru", ""))
            back = InlineKeyboardMarkup([[InlineKeyboardButton(
                {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang],
                callback_data="menu_guide")]])
            if text:
                await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back)
            else:
                await query.edit_message_text("⏳ Скоро...", reply_markup=back)
            # Video
            vid = section_data.get("video", "")
            if vid:
                try:
                    await context.bot.send_video(chat_id=chat_id, video=vid)
                except Exception:
                    pass

    # ── guide_step3 uchun yangi qisqa alias callbacklar ──
    elif data in ("g_step_1", "g_step_2", "g_step_3", "g_step_4",
                  "g_graph_foreigner", "g_graph_citizen", "back_to_guide_main"):
        if data == "back_to_guide_main":
            title = {
                "ru": "📖 *Руководство пациента*\n\nВыберите раздел:",
                "uz": "📖 *Bemor uchun qo'llanma*\n\nBo'limni tanlang:",
                "kz": "📖 *Науқас нұсқаулығы*\n\nБөлімді таңдаңыз:",
            }[lang]
            try:
                await query.message.delete()
            except Exception:
                pass
            await context.bot.send_message(chat_id=chat_id, text=title,
                                           parse_mode="Markdown", reply_markup=guide_keyboard(lang))
            return
        # Alias map → mavjud handlerlarga yo'naltirish
        alias_map = {
            "g_step_1":        "guide_step3",
            "g_step_2":        "guide_step3_s2",
            "g_step_3":        "guide_step3_s3",
            "g_step_4":        "guide_step3_s4",
            "g_graph_foreigner": "guide_step3_foreign",
            "g_graph_citizen":   "guide_step3_local",
        }
        # callback_data ni almashtirb, mavjud guide_ handler ni qayta chaqiramiz
        import types as _types
        fake_query = query
        # data ni o'zgartirib, guide_ handler logikasini to'g'ridan bajaramiz
        mapped = alias_map[data]
        section = mapped.replace("guide_", "")
        d2 = load_data()
        photo_key_map = {
            "step3":          "guide_step3_p1_photo",
            "step3_s2":       "guide_step3_p2_photo",
            "step3_foreign":  "guide_step3_foreign_photo",
            "step3_local":    "guide_step3_local_photo",
            "step3_s3":       "guide_step3_p3_photo",
            "step3_s4":       "guide_step3_p4_photo",
        }
        photo = d2.get(photo_key_map.get(section, ""), "")

        back_l  = {"ru": "⬅️ Назад",    "uz": "⬅️ Orqaga",  "kz": "⬅️ Артқа"}[lang]
        next_l  = {"ru": "➡️ Далее",    "uz": "➡️ Keyingi", "kz": "➡️ Келесі"}[lang]
        guide_l = {"ru": "🔝 К руководству", "uz": "🔝 Qo'llanmaga", "kz": "🔝 Нұсқаулыққа"}[lang]

        texts = {
            "step3": {
                "ru": "🕒 <b>Шаг 1: Утренняя очередь и обследования (08:00)</b>\n\nВаш второй день в клинике, процесс приема Malxam и дополнительные процедуры:\n• <b>Лаборатория и УЗИ:</b> Пациенты занимают очередь в отделе регистрации утром в 08:00 для сдачи лабораторных анализов и прохождения УЗИ.\n• <b>Процедурная книжка:</b> Вы сможете получать все дополнительные процедуры, разрешенные и назначенные врачом в процедурной книжке.",
                "uz": "🕒 <b>1-Qadam: Ertalabki navbat va Tekshiruvlar (Soat 08:00)</b>\n\nKlinikadagi ikkinchi kuningiz Malxam ichish jarayoni va qo'shimcha muolajalar:\n• <b>Laboratoriya va UZI:</b> Bemorlar laboratoriya tahlillari hamda UZI (EHO) ko'rigidan o'tish uchun ertalab soat 08:00 da Registratsiya bo'limidan navbat olib ko'rikdan o'tadi.\n• <b>Muolaja daftarchasi:</b> Muolaja daftarchada shifokor tomonidan ruxsat etilgan va buyurilgan barcha qo'shimcha muolajalarni olishingiz mumkin bo'ladi.",
                "kz": "🕒 <b>1-Қадам: Таңғы кезек және тексерулер (Сағат 08:00)</b>\n\nКлиникадағы екінші күніңіз, Malxam ішу процесі және қосымша ем-шаралар:\n• <b>Лаборатория және UZI:</b> Емделушілер зертханалық талдаулар мен UZI тексеруінен өту үшін таңғы сағат 08:00-де Тіркеу бөлімінен кезек алып, тексеруден өтеді.\n• <b>Емдеу кітапшасы:</b> Дәрігер рұқсат еткен және тағайындаған барлық қосымша ем-шараларды емдеу кітапшасы арқылы алуыңызға болады.",
            },
            "step3_s2": {
                "ru": "🌈 <b>Шаг 2: Порядок приема Malxam и цветные карточки</b>\n\nВторой день — это основной день, когда начинается прием Malxam.\n\n⚠️ <b>САМОЕ ВАЖНОЕ ПРАВИЛО:</b> Перед приемом Malxam <b>как минимум 1.5 часа (полтора часа) абсолютно ничего нельзя есть (быть натощак)!</b> Это максимально увеличивает эффект Malxam.\n\n• 💳 После оплаты вам выдаются специальные <b>цветные карточки</b>.\n• 🗓 Время приема Malxam и последовательность цветов меняются в зависимости от дней недели. Вы заходите на прием Malxam строго в свое время, в соответствии с цветом и номером вашей карточки.\n\n👇 Ознакомьтесь с графиком и точным временем с помощью кнопок ниже:",
                "uz": "🌈 <b>2-Qadam: Malxam ichish tartibi va Rangli kartochkalar</b>\n\nIkkinchi kun — Malxam ichish boshlanadigan asosiy kun hisoblanadi.\n\n⚠️ <b>ENG MUHIM QOIDA:</b> Malxam ichishdan oldin <b>kamida 1.5 soat (bir yarim soat) davomida mutlaqo hech narsa yemaslik (och qoringa bo'lish) kerak!</b> Bu Malxamning ta'sirini maksimal darajada oshiradi.\n\n• 💳 To'lovni amalga oshirganingizdan so'ng, qo'lingizga maxsus <b>rangli kartochkalar</b> beriladi.\n• 🗓 Malxam ichish vaqtlari va ranglar ketma-ketligi haftaning kunlariga qarab o'zgarib turadi. Siz qo'lingizdagi kartochkaning rangiga va undagi raqamiga qarab o'z vaqtingizda Malxam ichishga kirasiz.\n\n👇 Quyidagi tugmalar orqali o'zingizga tegishli grafik va aniq vaqtlar bilan tanishing:",
                "kz": "🌈 <b>2-Қадам: Malxam ішу тәртібі және түрлі-түсті карточкалар</b>\n\nЕкінші күн — Malxam ішу басталатын негізгі күн болып саналады.\n\n⚠️ <b>ЕҢ МАҢЫЗДЫ ЕРЕЖЕ:</b> Malxam ішер алдында <b>кем дегенде 1.5 сағат (бір жарым сағат) бұрын мүлдем ештеңе жемеу керек (аш қарында болу шарт)!</b> Бұл Malxam-ның әсерін барынша арттырады.\n\n• 💳 Төлем жасағаннан кейін қолыңызға арнайы <b>түрлі-түсті карточкалар</b> беріледі.\n• 🗓 Malxam ішу уақыты мен түстердің реттілігі апта күндеріне байланысты өзгеріп тұрады. Сіз қолыңыздағы карточканың түсі мен ондағы нөмірге сәйкес өз уақытыңызда Malxam ішуге кіресіз.\n\n👇 Төмендегі түймелер арқылы өзіңізге қатысты кестемен және нақты уақытпен танысыңыз:",
            },
            "step3_foreign": {
                "ru": "✈️ <b>Временный график приема Malxam для иностранных граждан</b>\n\n• 🕒 Иностранные граждане начинают прием Malxam <b>с 10:00 часов</b>.",
                "uz": "✈️ <b>Chet el fuqarolari uchun Malxam ichish vaqtinchalik grafigi</b>\n\n• 🕒 Chet el fuqarolari Malxam ichishni <b>soat 10:00 dan</b> boshlab ichishadi.",
                "kz": "✈️ <b>Шет ел азаматтарына арналған Malxam ішудің уақытша кестесі</b>\n\n• 🕒 Шет ел азаматтары Malxam ішуді <b>сағат 10:00-ден</b> бастайды.",
            },
            "step3_local": {
                "ru": "🇺🇿 <b>Временный график приема Malxam для граждан Узбекистана</b>\n\n• 🕒 Для граждан Узбекистана время приема Malxam начинается <b>с 13:00 или 14:00 часов</b>.",
                "uz": "🇺🇿 <b>O'zbekiston fuqarolari uchun Malxam ichish vaqtinchalik grafigi</b>\n\n• 🕒 O'zbekiston fuqarolari uchun Malxam ichish vaqtlarining boshlanishi: <b>soat 13:00 yoki 14:00 dan</b> boshlanadi.",
                "kz": "🇺🇿 <b>Өзбекстан азаматтарына арналған Malxam ішудің уақытша кестесі</b>\n\n• 🕒 Өзбекстан азаматтары үшін Malxam ішу уақыты <b>сағат 13:00 немесе 14:00-ден</b> басталады.",
            },
            "step3_s3": {
                "ru": "🔥 <b>Шаг 3: Самые важные золотые правила после Malxam!</b>\n\nРежим после приема Malxam — это часть лечения, дающая наивысший результат, поэтому строго соблюдайте следующие правила:\n\n1️⃣ 🛏 <b>Применение грелки (Самый важный этап):</b> Сразу после приема Malxam необходимо пройти в свою палату и <b>как минимум от 1,5 до 2 часов лежать неподвижно, приложив грелку к правому подреберью (в область печени)</b>.\n2️⃣ 🩺 <b>Процедура клизмы:</b> После того как вы полежали с грелкой, не спеша отправляйтесь в клизменную комнату для прохождения следующей очистительной процедуры.\n3️⃣ 🚶‍♂️ <b>После процедур:</b> После клизмы рекомендуется вести активный образ жизни в течение дня, принимать дополнительные назначенные процедуры и пить травяные чаи в фито-баре.",
                "uz": "🔥 <b>3-Qadam: Malxamdan keyingi eng muhim oltin qoidalar!</b>\n\nMalxamni ichib bo'lgandan keyingi tartib davolanishning eng yuqori natija beradigan qismidir, shuning uchun quyidagilarga qat'iy amal qiling:\n\n1️⃣ 🛏 <b>Grelka qo'yish (Eng muhim joyi):</b> Malxamni ichgach, darhol xonangizga borib, <b>kamida 1 yarim yoki 2 soat davomida o'ng qovurg'a ostiga (jigar sohasiga) grelka qo'yib</b>, qimirlamay yotishingiz shart.\n2️⃣ 🩺 <b>Klizma muolajasi:</b> Grelkada yotib bo'lgandan keyin, shoshmasdan klizma xonasiga borib, navbatdagi tozalash muolajasini olasiz.\n3️⃣ 🚶‍♂️ <b>Muolajadan so'ng:</b> Klizmadan keyin kun davomida faol harakatda bo'lish, qo'shimcha belgilangan muolajalarni olish hamda fito-bardagi giyohli choylarni ichib yurish tavsiya etiladi.",
                "kz": "🔥 <b>3-Қадам: Malxamдан кейінгі ең маңызды алтын ережелер!</b>\n\nMalxamды ішкеннен кейінгі күтім — емнің ең жоғары нәтиже беретін бөлігі, сондықтан мына ережелерді қатаң сақтаңыз:\n\n1️⃣ 🛏 <b>Грелка басу (Ең маңызды кезең):</b> Malxamды ішкен бойда бірден бөлмеңізге барып, <b>кем дегенде 1,5 - 2 сағат бойы оң жақ қабырға астына (бауыр тұсына) grelka басып</b>, қозғалмай жатуыңыз шарт.\n2️⃣ 🩺 <b>Клизма ем-шарасы:</b> Грелкамен жатып болғаннан кейін, асықпай клизма бөлмесіне барып, кезекті тазарту ем-шарасын аласыз.\n3️⃣ 🚶‍♂️ <b>Ем-шарадан кейін:</b> Клизмадан кейін күн бойы белсенді қозғалыста болу, қосымша тағайындалған емдерді алу және фито-бардағы шөп шайларын ішіп жүру ұсынылады.",
            },
            "step3_s4": {
                "ru": "⏳ <b>Шаг 4: Эффективное использование времени между очередями</b>\n\n• 🕒 Процедура выдачи Malxam начинается утром в 10:00. Сначала пьют те, кто уезжает, затем начинается последовательность цветов.\n• 🔔 Если по вашей карточке очередь на прием Malxam выпадает на середину дня (после обеда), используйте свободное время с пользой!\n• <b>Процедуры:</b> В этот промежуток времени вы можете спокойно проходить другие дополнительные процедуры, назначенные врачом (Массаж, Нуга Бест, Серагем и т.д.), или отдыхать в Фито-баре, попивая свежезаваренный травяной чай.",
                "uz": "⏳ <b>4-Qadam: Navbat orasidagi bo'sh vaqtdan unumli foydalanish</b>\n\n• 🕒 Malxam berish jarayoni ertalab soat 10:00 dan boshlanadi. Birinchi bo'lib ketuvchilar ichadi, keyin ranglar ketma-ketligi boshlanadi.\n• 🔔 Agar sizning kartochkangiz bo'yicha Malxam ichish navbatingiz kunning yarmida (tushdan keyin) bo'lsa, ungacha bo'sh vaqtingizdan unumli foydalaning!\n• 💆‍♂️ Ungacha bo'lgan vaqt oralig'ida shifokor buyurgan boshqa qo'shimcha muolajalarni (Massaj, Nuga Best, Seragem va h.k.) olishingiz yoki Fito-barda shifobaxsh choylardan ichib dam olishingiz mumkin.",
                "kz": "⏳ <b>4-Қадам: Кезек арасындағы бос уақытты тиімді пайдалану</b>\n\n• 🕒 Malxam беру процесі таңғы сағат 10:00-де басталады. Алдымен кететін адамдар ішеді, содан кейін түстердің реттілігі басталады.\n• 🔔 Егер сіздің карточкаңыз бойынша Malxam ішу кезегіңіз күннің екінші жартысына (түстен кейін) сәйкес келсе, оған дейінгі бос уақытты тиімді пайдаланыңыз!\n• <b>Ем-шаралар:</b> Бұл уақыт аралығында дәрігер тағайындаған басқа да қосымша ем-шараларды (Массаж, Нуга Бест, Seragem т.б.) емін-еркін алуыңызға немесе Фито-бардағы шөп шайларын ішіп демалуыңызға болады.",
            },
        }
        text = texts.get(section, {}).get(lang, "")

        # Keyboard
        if section == "step3":
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{next_l} (2/4)", callback_data="g_step_2")],
                [InlineKeyboardButton(back_l, callback_data="menu_guide")],
            ])
        elif section == "step3_s2":
            foreign_l = {"ru": "✈️ Иностр. граждане", "uz": "✈️ Chet el fuqarolari", "kz": "✈️ Шет ел азаматтары"}[lang]
            local_l   = {"ru": "🇺🇿 Граждане Узбекистана", "uz": "🇺🇿 O'zbekiston fuqarolari", "kz": "🇺🇿 Өзбекстан азаматтары"}[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(foreign_l, callback_data="g_graph_foreigner")],
                [InlineKeyboardButton(local_l,   callback_data="g_graph_citizen")],
                [InlineKeyboardButton(f"{next_l} (3/4)", callback_data="g_step_3"),
                 InlineKeyboardButton(f"⬅️ (1/4)", callback_data="g_step_1")],
            ])
        elif section in ("step3_foreign", "step3_local"):
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{next_l} (3/4)", callback_data="g_step_3")],
                [InlineKeyboardButton(back_l, callback_data="g_step_2")],
            ])
        elif section == "step3_s3":
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{next_l} (4/4)", callback_data="g_step_4")],
                [InlineKeyboardButton(f"⬅️ (2/4)", callback_data="g_step_2")],
            ])
        elif section == "step3_s4":
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(guide_l, callback_data="back_to_guide_main")],
                [InlineKeyboardButton(f"⬅️ (3/4)", callback_data="g_step_3")],
            ])
        else:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_l, callback_data="menu_guide")]])

        await query.message.delete()
        if photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo,
                                         caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=chat_id, text=text,
                                           parse_mode="HTML", reply_markup=kb)

    # ── Infratuzilma ──
    elif data == "guide_infrastructure":
        d2 = load_data()
        INFRA_MENU_PHOTO = d2.get("infra_menu_photo", "")
        text = {
            "ru": "🏢 <b>Территория клиники и Корпуса</b>\n\nЧтобы не заблудиться и легко найти нужные процедурные кабинеты, выберите интересующий корпус:",
            "uz": "🏢 <b>Klinikamiz hududi va Korpuslar</b>\n\nAdashib ketmasligingiz va kerakli muolaja xonalarini osongina topishingiz uchun kerakli korpusni tanlang:",
            "kz": "🏢 <b>Клиника аумағы мен Корпустар</b>\n\nАдасып кетпей, керекті ем-шара бөлмелерін оңай табу үшін қажетті корпусты таңдаңыз:",
        }[lang]
        back_label  = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        main_label  = {"ru": "🏢 Главный корпус", "uz": "🏢 Asosiy korpus", "kz": "🏢 Бас корпус"}[lang]
        m_label     = {"ru": "🏥 Корпус М", "uz": "🏥 M korpus", "kz": "🏥 М корпусы"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(main_label, callback_data="infra_main_building")],
            [InlineKeyboardButton(m_label,    callback_data="infra_m_building")],
            [InlineKeyboardButton(back_label, callback_data="back_to_guide_main")],
        ])
        await query.message.delete()
        if INFRA_MENU_PHOTO:
            await context.bot.send_photo(chat_id=chat_id, photo=INFRA_MENU_PHOTO,
                                         caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=chat_id, text=text,
                                           parse_mode="HTML", reply_markup=kb)

    elif data == "infra_main_building":
        d2 = load_data()
        back_label   = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        klizma_label = {"ru": "🚿 Клизменный кабинет", "uz": "🚿 Klizma xonasi", "kz": "🚿 Клизма бөлмесі"}[lang]
        fizio_label  = {"ru": "⚡ Физиокабинет", "uz": "⚡ Fiziokabinetlar", "kz": "⚡ Физиокабинеттер"}[lang]
        massaj_label = {"ru": "💆 Массажный кабинет", "uz": "💆 Massaj xonasi", "kz": "💆 Массаж бөлмесі"}[lang]
        nurse_label  = {"ru": "🏥 Процедурный кабинет (медсёстры)", "uz": "🏥 Muolaja xonasi (hamshiralar)", "kz": "🏥 Процедуралық бөлме (медбикелер)"}[lang]
        text = {
            "ru": "🏢 <b>Главный корпус — расположение кабинетов</b>\n\nВыберите кабинет, чтобы узнать его местонахождение:",
            "uz": "🏢 <b>Asosiy korpus — xonalar joylashuvi</b>\n\nXona joylashuvini bilish uchun tanlang:",
            "kz": "🏢 <b>Бас корпус — бөлмелердің орналасуы</b>\n\nОрналасуын білу үшін бөлмені таңдаңыз:",
        }[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(klizma_label, callback_data="infra_room_klizma")],
            [InlineKeyboardButton(fizio_label,  callback_data="infra_room_fizio")],
            [InlineKeyboardButton(massaj_label, callback_data="infra_room_massaj")],
            [InlineKeyboardButton(nurse_label,  callback_data="infra_room_nurse")],
            [InlineKeyboardButton(back_label,   callback_data="guide_infrastructure")],
        ])
        await query.message.delete()
        main_photo = d2.get("infra_main_photo", "")
        if main_photo:
            await context.bot.send_photo(chat_id=chat_id, photo=main_photo,
                                         caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=chat_id, text=text,
                                           parse_mode="HTML", reply_markup=kb)

    elif data == "infra_m_building":
        d2 = load_data()
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        text = {
            "ru": "🏥 <b>Корпус М — расположение и информация</b>\n\nЗдесь расположены палаты М/Люкс и М/VIP, а также специализированные процедурные кабинеты корпуса М.",
            "uz": "🏥 <b>M korpus — joylashuv va ma'lumot</b>\n\nBu yerda M/Lyuks va M/VIP xonalari hamda M korpusining maxsus muolaja xonalari joylashgan.",
            "kz": "🏥 <b>М корпусы — орналасуы және ақпарат</b>\n\nМұнда М/Люкс және М/VIP палаталары, сондай-ақ М корпусының арнайы процедуралық бөлмелері орналасқан.",
        }[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(back_label, callback_data="guide_infrastructure")],
        ])
        await query.message.delete()
        m_photo = d2.get("infra_m_building_photo", "")
        if m_photo:
            await context.bot.send_photo(chat_id=chat_id, photo=m_photo,
                                         caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=chat_id, text=text,
                                           parse_mode="HTML", reply_markup=kb)

    elif data in ("infra_room_klizma", "infra_room_fizio", "infra_room_massaj", "infra_room_nurse"):
        d2 = load_data()
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        room_map = {
            "infra_room_klizma": {
                "photo_key": "infra_klizma_photo",
                "text": {
                    "ru": "🚿 <b>Клизменный кабинет</b>\n\nКлизменный кабинет находится в главном корпусе. После приема Malxam и грелки обязательно посетите этот кабинет для очистительной процедуры.",
                    "uz": "🚿 <b>Klizma xonasi</b>\n\nKlizma xonasi asosiy korpusda joylashgan. Malxam ichib, grelka qo'yib bo'lgandan keyin tozalash muolajasi uchun shu xonaga boring.",
                    "kz": "🚿 <b>Клизма бөлмесі</b>\n\nКлизма бөлмесі бас корпуста орналасқан. Malxam ішіп, грелка басқаннан кейін тазарту ем-шарасы үшін осы бөлмеге барыңыз.",
                },
            },
            "infra_room_fizio": {
                "photo_key": "infra_fizio_photo",
                "text": {
                    "ru": "⚡ <b>Физиотерапевтические кабинеты</b>\n\nФизиокабинеты расположены в главном корпусе. Здесь проводятся назначенные врачом физиотерапевтические процедуры.",
                    "uz": "⚡ <b>Fizioterapiya xonalari</b>\n\nFizioxonalar asosiy korpusda joylashgan. Bu yerda shifokor tomonidan buyurilgan fizioterapiya muolajalari olib boriladi.",
                    "kz": "⚡ <b>Физиотерапия бөлмелері</b>\n\nФизиобөлмелер бас корпуста орналасқан. Мұнда дәрігер тағайындаған физиотерапиялық ем-шаралар жүргізіледі.",
                },
            },
            "infra_room_massaj": {
                "photo_key": "infra_massaj_photo",
                "text": {
                    "ru": "💆 <b>Массажный кабинет</b>\n\nМассажный кабинет находится в главном корпусе. Принимаются все виды массажа, назначенные врачом.",
                    "uz": "💆 <b>Massaj xonasi</b>\n\nMassaj xonasi asosiy korpusda joylashgan. Shifokor buyurgan barcha massaj turlari qabul qilinadi.",
                    "kz": "💆 <b>Массаж бөлмесі</b>\n\nМассаж бөлмесі бас корпуста орналасқан. Дәрігер тағайындаған барлық массаж түрлері қабылданады.",
                },
            },
            "infra_room_nurse": {
                "photo_key": "infra_nurse_photo",
                "text": {
                    "ru": "🏥 <b>Процедурный кабинет (медсёстры)</b>\n\nПроцедурный кабинет находится в главном корпусе. Здесь медсёстры выполняют все назначенные инъекции и процедуры по книжке.",
                    "uz": "🏥 <b>Muolaja xonasi (hamshiralar)</b>\n\nMuolaja xonasi asosiy korpusda joylashgan. Bu yerda hamshiralar daftarchada belgilangan barcha ukol va muolajalarni bajaradi.",
                    "kz": "🏥 <b>Процедуралық бөлме (медбикелер)</b>\n\nПроцедуралық бөлме бас корпуста орналасқан. Мұнда медбикелер кітапшада белгіленген барлық инъекция мен ем-шараларды жүзеге асырады.",
                },
            },
        }
        room = room_map[data]
        text = room["text"][lang]
        photo = d2.get(room["photo_key"], "")
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="infra_main_building")]])
        await query.message.delete()
        if photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo,
                                         caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=chat_id, text=text,
                                           parse_mode="HTML", reply_markup=kb)

    # ── Uyga tafsiyaoma — quyi bo'limlar ──
    elif data == "info_qoidalar":
        text = {
            "uz": (
                "⚠️ <b>Muhim qoidalar</b>\n\n"
                "• Dastlabki 3 kun davomida umuman non iste'mol qilmang!\n"
                "• Jismoniy og'ir ishlar qilish va og'ir yuk ko'tarish mutlaqo mumkin emas.\n"
                "• 10 kun davomida hazarsipand (isiriq) qaynatib, uning bug'iga vanna qilishingiz tavsiya etiladi.\n"
                "• 30 kundan so'ng shifokor ko'rigidan o'ting va imkoniyatga qarab 6–9 oydan so'ng takroriy maslahatga keling."
            ),
            "ru": (
                "⚠️ <b>Важные правила</b>\n\n"
                "• В течение первых 3 дней полностью откажитесь от хлеба!\n"
                "• Тяжёлый физический труд и поднятие тяжестей категорически запрещены.\n"
                "• В течение 10 дней рекомендуется делать паровые ванны с отваром гармалы (исирик).\n"
                "• Через 30 дней пройдите осмотр врача, а через 6–9 месяцев (по возможности) приходите на повторную консультацию."
            ),
            "kz": (
                "⚠️ <b>Маңызды ережелер</b>\n\n"
                "• Алғашқы 3 күн бойы наннан мүлдем бас тартыңыз!\n"
                "• Ауыр физикалық жұмыс істеу және ауыр жүк көтеру мүлдем тыйым салынады.\n"
                "• 10 күн бойы исирик (адыраспан) қайнатып, оның буына ванна қабылдау ұсынылады.\n"
                "• 30 күннен кейін дәрігер тексерісінен өтіңіз және мүмкіндігіне қарай 6–9 айдан кейін қайталама кеңеске келіңіз."
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="guide_shopping")]])
        try:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            await query.message.delete()
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

    elif data == "info_taqiq":
        text = {
            "uz": (
                "🚫 *Parhez davomida eyish va qilish mutlaqo taqiqlangan narsalar:*\n\n"
                "• Yog'li va xamirli taomlar\n"
                "• Sho'r, achchiq va o'tkir ziravorli ovqatlar\n"
                "• Dudlangan (kopchyoniy) mahsulotlar\n"
                "• Dukkaklilar: No'xat va moshli taomlar\n"
                "• Spirtli ichimliklar\n"
                "• Tamaki mahsulotlari (sigaret, nos va h.k.)"
            ),
            "ru": (
                "🚫 *Строго запрещено во время диеты:*\n\n"
                "• Жирные и мучные блюда\n"
                "• Солёная, острая и пряная пища\n"
                "• Копчёные продукты\n"
                "• Бобовые: горох и блюда из маша\n"
                "• Алкогольные напитки\n"
                "• Табачные изделия (сигареты, нас и т.д.)"
            ),
            "kz": (
                "🚫 *Диета кезінде мүлдем тыйым салынады:*\n\n"
                "• Майлы және ұнды тағамдар\n"
                "• Тұзды, ащы және өткір дәмдеуіштері бар тағамдар\n"
                "• Ысталған өнімдер\n"
                "• Бұршақтылар: бұршақ және маш тағамдары\n"
                "• Алкогольді сусындар\n"
                "• Темекі өнімдері (сигарет, нас және т.б.)"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="guide_shopping")]])
        try:
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        except Exception:
            await query.message.delete()
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=kb)

    elif data == "info_giyoh":
        text = {
            "uz": (
                "🌿 *Surgi giyohini ichish va tayyorlash yo'riqnomasi*\n\n"
                "Uyingizga berilgan surgi giyohi (ich suruvchi o't) ichaklarni tozalash va hazm tizimini "
                "yaxshilash uchun juda muhimdir.\n\n"
                "☕️ *Tayyorlash usuli (Damlash):*\n"
                "Surgi giyohi xuddi oddiy choy kabi damlanadi:\n"
                "1. Idishga yoki choynakka belgilangan miqdordagi giyohni 10–15 daqiqa davomida damlab qo'yasiz.\n\n"
                "🕒 *Ichish vaqti:* Giyohni faqat ovqatlangandan keyin (to'q qoringa) iliq holatda choy o'rnida ichish kerak.\n\n"
                "❓ *Nima sodir bo'ladi?:*\n"
                "• Ich kelishi suriladi (toksin va shlaklar tozalanadi).\n"
                "• Qorin dam bo'lishi yoki engil sanchiq bo'lishi tabiiy hol, xavotir olmang.\n"
                "• Suv balansi uchun ruxsat etilgan sharbatlardan ichib turing."
            ),
            "ru": (
                "🌿 *Инструкция по приёму слабительной травы*\n\n"
                "Слабительная трава, выданная вам домой, очень важна для очищения кишечника и улучшения пищеварения.\n\n"
                "☕️ *Способ приготовления (заваривание):*\n"
                "Трава заваривается как обычный чай:\n"
                "1. Положите нужное количество травы в посуду или чайник и дайте настояться 10–15 минут.\n\n"
                "🕒 *Время приёма:* Пить только после еды (на сытый желудок) в тёплом виде вместо чая.\n\n"
                "❓ *Что произойдёт?:*\n"
                "• Стул нормализуется (очищаются токсины и шлаки).\n"
                "• Вздутие или лёгкие колики — естественная реакция, не волнуйтесь.\n"
                "• Для водного баланса пейте разрешённые соки."
            ),
            "kz": (
                "🌿 *Іш жүргізетін шөпті қабылдау нұсқаулығы*\n\n"
                "Үйге берілген іш жүргізетін шөп ішекті тазарту және қорыту жүйесін жақсарту үшін өте маңызды.\n\n"
                "☕️ *Дайындау тәсілі (демдеу):*\n"
                "Шөп кәдімгі шай сияқты демделеді:\n"
                "1. Ыдысқа немесе шәйнекке белгіленген мөлшердегі шөпті 10–15 минут демдеп қойыңыз.\n\n"
                "🕒 *Ішу уақыты:* Шөпті тек тамақтанғаннан кейін (тоқ қарынға) жылы күйінде шай орнына ішу керек.\n\n"
                "❓ *Не болады?:*\n"
                "• Іш жүреді (токсиндер мен шлактар тазаланады).\n"
                "• Іштің кебуі немесе жеңіл сырқырау — табиғи жағдай, алаңдамаңыз.\n"
                "• Су балансы үшін рұқсат етілген шырындарды ішіп тұрыңыз."
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="guide_shopping")]])
        try:
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        except Exception:
            await query.message.delete()
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=kb)

    elif data == "menu_taomnoma":
        text = {
            "uz": "🍲 *Taomnoma*\n\nQuyidagilardan birini tanlang:",
            "ru": "🍲 *Меню питания*\n\nВыберите раздел:",
            "kz": "🍲 *Тамақтану мәзірі*\n\nБөлімді таңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton({"uz": "☀️ Nonushta", "ru": "☀️ Завтрак", "kz": "☀️ Таңғы ас"}[lang], callback_data="sub_nonushta")],
            [InlineKeyboardButton({"uz": "🌤 Tushlik", "ru": "🌤 Обед", "kz": "🌤 Түскі ас"}[lang], callback_data="sub_tushlik")],
            [InlineKeyboardButton({"uz": "🌙 Kechki ovqat", "ru": "🌙 Ужин", "kz": "🌙 Кешкі ас"}[lang], callback_data="sub_kechki")],
            [InlineKeyboardButton({"uz": "🧃 Sharbatlar", "ru": "🧃 Соки", "kz": "🧃 Шырындар"}[lang], callback_data="sub_sharbat")],
            [InlineKeyboardButton(back_label, callback_data="guide_shopping")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "sub_nonushta":
        text = {
            "uz": (
                "☀️ *Nonushta*\n\n"
                "• Engil qatiqli taomlar yoki suyuq qatiq\n"
                "• Toza tabiiy asal (1-2 choy qoshiq)\n"
                "• Dastlabki 3 kunda nonsiz, keyin ozroq qora non bilan"
            ),
            "ru": (
                "☀️ *Завтрак*\n\n"
                "• Лёгкие блюда с кефиром или жидкий кефир\n"
                "• Натуральный мёд (1-2 чайные ложки)\n"
                "• Первые 3 дня без хлеба, затем — немного чёрного хлеба"
            ),
            "kz": (
                "☀️ *Таңғы ас*\n\n"
                "• Жеңіл айранды тағамдар немесе сұйық айран\n"
                "• Таза табиғи бал (1-2 шай қасық)\n"
                "• Алғашқы 3 күн нансыз, содан кейін — аздап қара нанмен"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_taomnoma")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "sub_tushlik":
        text = {
            "uz": (
                "🌤 *Tushlik*\n\n"
                "Issiq va engil hazm bo'luvchi suyuq sho'rvalar (go'shtlari yog'siz bo'lsin):\n"
                "• Chopma sho'rva\n"
                "• Qaynatma sho'rva\n"
                "• Tovuq sho'rva\n"
                "• Baliqli sho'rva\n"
                "• Karam sho'rva"
            ),
            "ru": (
                "🌤 *Обед*\n\n"
                "Горячие и лёгкие для переваривания жидкие супы (мясо должно быть нежирным):\n"
                "• Чопма шурпа\n"
                "• Отварной бульон\n"
                "• Куриный суп\n"
                "• Рыбный суп\n"
                "• Капустный суп"
            ),
            "kz": (
                "🌤 *Түскі ас*\n\n"
                "Ыстық және жеңіл қорытылатын сорпалар (еті майсыз болсын):\n"
                "• Чопма сорпа\n"
                "• Қайнатма сорпа\n"
                "• Тауық сорпасы\n"
                "• Балықты сорпа\n"
                "• Қырыққабат сорпасы"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_taomnoma")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "sub_kechki":
        text = {
            "uz": (
                "🌙 *Kechki ovqat*\n\n"
                "Tushlikdan qolgan engil sho'rvalar yoki qatiqli taomlar "
                "(uxlashdan 3-4 soat oldin)."
            ),
            "ru": (
                "🌙 *Ужин*\n\n"
                "Оставшиеся лёгкие супы с обеда или блюда с кефиром "
                "(за 3-4 часа до сна)."
            ),
            "kz": (
                "🌙 *Кешкі ас*\n\n"
                "Түскі асқа қалған жеңіл сорпалар немесе айранды тағамдар "
                "(ұйқыдан 3-4 сағат бұрын)."
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_taomnoma")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "sub_sharbat":
        text = {
            "uz": (
                "🧃 *Sharbatlar*\n\n"
                "Kuniga 250-400 grammgacha yangi chiqarilgan:\n"
                "• Olma suvi\n"
                "• Sabzi suvi\n"
                "• Bodring suvi\n"
                "• Tarvuz suvi\n"
                "• O'rik suvi"
            ),
            "ru": (
                "🧃 *Соки*\n\n"
                "До 250-400 граммов в день свежевыжатых:\n"
                "• Яблочный сок\n"
                "• Морковный сок\n"
                "• Огуречный сок\n"
                "• Арбузный сок\n"
                "• Абрикосовый сок"
            ),
            "kz": (
                "🧃 *Шырындар*\n\n"
                "Күніне 250-400 грамм дейін жаңа сығылған:\n"
                "• Алма шырыны\n"
                "• Сәбіз шырыны\n"
                "• Қияр шырыны\n"
                "• Қарбыз шырыны\n"
                "• Өрік шырыны"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_taomnoma")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    # ── Klinika haqida — submenu ──
    elif data == "menu_clinic":
        title = {
            "ru": "🏥 *Клиника Эргаш-Ота*\n\nВыберите раздел:",
            "uz": "🏥 *Эргаш-Ота klinikasi*\n\nBo'limni tanlang:",
            "kz": "🏥 *Эргаш-Ота клиникасы*\n\nБөлімді таңдаңыз:",
        }[lang]
        await query.edit_message_text(title, parse_mode="Markdown",
                                      reply_markup=clinic_submenu_keyboard(lang))

    elif data == "clinic_info":
        text = d.get("clinic_info_text", {}).get(lang, "")
        back = InlineKeyboardMarkup([[InlineKeyboardButton(
            {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang],
            callback_data="menu_clinic")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back)
        if d.get("clinic_photos"):
            await send_photos(context, chat_id, d["clinic_photos"])

    elif data == "clinic_video":
        videos = d.get("clinic_videos", [])
        back = InlineKeyboardMarkup([[InlineKeyboardButton(
            {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang],
            callback_data="menu_clinic")]])
        title = {
            "ru": "🎥 *Видео о клинике:*",
            "uz": "🎥 *Klinika videolari:*",
            "kz": "🎥 *Клиника бейнелері:*",
        }[lang]
        await query.edit_message_text(title, parse_mode="Markdown", reply_markup=back)
        if videos:
            for vid in videos[:5]:
                try:
                    await context.bot.send_video(chat_id=chat_id, video=vid)
                except Exception as e:
                    logger.error(f"Video error: {e}")
        else:
            no_video = {
                "ru": "🎥 Видео скоро будут добавлены!",
                "uz": "🎥 Videolar tez orada qo'shiladi!",
                "kz": "🎥 Бейнелер жақында қосылады!",
            }[lang]
            await context.bot.send_message(chat_id=chat_id, text=no_video)

    elif data == "clinic_certs":
        text = d.get("clinic_certs", {}).get(lang, "")
        back = InlineKeyboardMarkup([[InlineKeyboardButton(
            {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang],
            callback_data="menu_clinic")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back)
        if d.get("cert_photos"):
            await send_photos(context, chat_id, d["cert_photos"])

    elif data == "clinic_history":
        text = d.get("clinic_history", {}).get(lang, "")
        back = InlineKeyboardMarkup([[InlineKeyboardButton(
            {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang],
            callback_data="menu_clinic")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back)

    # ── Shifobaxsh malhamlar va muolajalar ──
    elif data == "malham_va_muolajalar":
        title = {
            "ru": "🌿 *Малхам и процедуры*\n\nВыберите раздел:",
            "uz": "🌿 *Малхам va muolajalar*\n\nBo'limni tanlang:",
            "kz": "🌿 *Малхам и процедуры*\n\nБөлімді таңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        mal_label  = {"ru": "🟢 Малхам и травы", "uz": "🟢 Малхам va giyohlar", "kz": "🟢 Малхам және шөптер"}[lang]
        muo_label  = {"ru": "🔵 Доп. процедуры",          "uz": "🔵 Qo'shimcha muolajalar",     "kz": "🔵 Қосымша процедуралар"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(mal_label, callback_data="sub_malhamlar")],
            [InlineKeyboardButton(muo_label, callback_data="sub_muolajalar")],
            [InlineKeyboardButton(back_label, callback_data="menu_clinic")],
        ])
        await query.edit_message_text(title, parse_mode="Markdown", reply_markup=kb)

    elif data == "sub_malhamlar":
        title = {
            "ru": "🟢 *Малхам и травы*\n\nВыберите:",
            "uz": "🟢 *Малхам va o'tlar*\n\nTanlang:",
            "kz": "🟢 *Малхам және шөптер*\n\nТаңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        items = [
            ("Malham",                                                                          "mal_malham"),
            ({"ru": "Фито бар",         "uz": "Fito bar",      "kz": "Фито бар"}[lang],       "m_fitobar"),
            ({"ru": "Миндальное масло", "uz": "Bodom yog'i",   "kz": "Бадам майы"}[lang],     "m_bodom"),
            ({"ru": "Оливковое масло",  "uz": "Zaytun yog'i",  "kz": "Зәйтүн майы"}[lang],   "m_zaytun"),
            ({"ru": "Чудо мазь",        "uz": "Chuda maz",     "kz": "Ғажайып жақпа май"}[lang], "mal_chuda"),
        ]
        buttons = [[InlineKeyboardButton(label, callback_data=cb)] for label, cb in items]
        buttons.append([InlineKeyboardButton(back_label, callback_data="malham_va_muolajalar")])
        await query.edit_message_text(title, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "sub_muolajalar":
        title = {
            "ru": "🔵 *Доп. процедуры*\n\nВыберите:",
            "uz": "🔵 *Qo'shimcha muolajalar*\n\nTanlang:",
            "kz": "🔵 *Қосымша процедуралар*\n\nТаңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        items = [
            ("Nuga-best",                                                                                           "muo_nugabest"),
            ("Seragem",                                                                                             "muo_seragem"),
            ({"ru": "Второе сердце", "uz": "Ikkinchi yurak", "kz": "Екінші жүрек"}[lang], "t_foot_massage"),
            ({"ru": "Общий массаж",            "uz": "Umumiy massaj",                       "kz": "Жалпы массаж"}[lang],                           "t_general_massage"),
            ({"ru": "Биоэнергетический массаж", "uz": "Bioenergiya massaji", "kz": "Биоэнергетикалық массаж"}[lang],                           "t_silver_glove"),
            ({"ru": "Лимфодренаж",             "uz": "Limfadrenaj",                         "kz": "Лимфодренаж"}[lang],                            "t_lymph"),
            ({"ru": "Растяжка",                "uz": "Rastyajka",                           "kz": "Растяжка"}[lang],                               "t_stretch"),
            ({"ru": "Ударно-волновая терапия", "uz": "Zarb to'lqinli terapiya",             "kz": "Соққы-толқынды терапия"}[lang],                 "t_shockwave"),
            ("Robospine",                                                                                           "muo_robospine"),
            ({"ru": "Криолиполиз",             "uz": "Kriolipoliz",                         "kz": "Криолиполиз"}[lang],                            "t_cryo"),
        ]
        buttons = [[InlineKeyboardButton(label, callback_data=cb)] for label, cb in items]
        buttons.append([InlineKeyboardButton(back_label, callback_data="malham_va_muolajalar")])
        try:
            await query.edit_message_text(title, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))
        except Exception:
            await query.message.delete()
            await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "muo_nugabest":
        NUGA_BEST_PHOTO_ID = d.get("nuga_best_photo_id", "")
        text = {
            "ru": (
                "🦴 *Nuga-Best — термомагнитный массаж позвоночника*\n\n"
                "Современная технология для коррекции осанки, восстановления позвонков и устранения защемлений нервов.\n\n"
                "🎁 *Отличная возможность:* Данная процедура включена в стоимость проживания — 6 сеансов за 10 дней!\n\n"
                "💰 Дополнительный сеанс вне пакета: *56 000 сум*"
            ),
            "uz": (
                "🦴 *Nuga-Best muolajasi*\n\n"
                "Umurtqa pog'onasini termal magnit bilan massaj qilish, qiyshiqliklarni tiklash va nerv siqilishlarini ochish uchun eng samarali zamonaviy texnologiyadir.\n\n"
                "🎁 *Ajoyib imkoniyat:* Ushbu muolaja klinikamizdagi barcha turdagi xonalar to'lovi ichiga kiritilgan — 10 kunlik to'lovga 6 ta muolaja!\n\n"
                "💰 Paketdan tashqari qo'shimcha olish narxi: 1 seans — *56 000 so'm*"
            ),
            "kz": (
                "🦴 *Nuga-Best процедурасы — термомагниттік омыртқа массажы*\n\n"
                "Омыртқаны қалпына келтіру, қисықтықты түзету және жүйке қысылуын жою үшін заманауи тиімді технология.\n\n"
                "🎁 *Тамаша мүмкіндік:* Бұл процедура барлық нөмір төлемдеріне кіреді — 10 күндік төлемге 6 рет!\n\n"
                "💰 Пакеттен тыс қосымша баға: 1 сеанс — *56 000 сум*"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="sub_muolajalar")]])
        if NUGA_BEST_PHOTO_ID:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=NUGA_BEST_PHOTO_ID,
                caption=text,
                parse_mode="Markdown",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "muo_seragem":
        SERAGEM_PHOTO_ID = d.get("seragem_photo_id", "")
        text = {
            "ru": (
                "🦴 <b>Процедура Серагем</b>\n\n"
                "Одна из самых современных процедур, помогающая оздоровить позвоночник, улучшить кровообращение и успокоить нервную систему.\n\n"
                "🎁 <b>Отличная возможность:</b> Эта процедура включена в стоимость проживания в палатах <b>Полулюкс</b> и <b>Люкс</b> нашей клиники! При оплате 10 дней проживания вы получаете 6 процедур бесплатно.\n\n"
                "💰 Стоимость дополнительного сеанса (вне пакета): 1 сеанс — <b>56 000 сум</b>"
            ),
            "uz": (
                "🦴 <b>Seragem muolajasi</b>\n\n"
                "Umurtqa pog'onasini sog'lomlashtirish, qon aylanishini yaxshilash va asab tizimini tinchlantirishga yordam beruvchi eng zamonaviy muolajalardan biri.\n\n"
                "🎁 <b>Ajoyib imkoniyat:</b> Ushbu muolaja klinikamizdagi <b>Yarim lyuks (Pol lyuks)</b> va <b>Lyuks</b> xonalar umumiy to'lovi ichiga kiritilgan! 10 kunlik to'lovga 6 ta muolaja bepul qo'shib beriladi.\n\n"
                "💰 Paketdan tashqari qo'shimcha olish narxi: 1 seans — <b>56 000 so'm</b>"
            ),
            "kz": (
                "🦴 <b>Серагем ем-шарасы</b>\n\n"
                "Омыртқаны сауықтыруға, қан айналымын жақсартуға және жүйке жүйесін тыныштандыруға көмектесетін ең заманауи ем-шаралардың бірі.\n\n"
                "🎁 <b>Керемет мүмкіндік:</b> Бұл ем-шара клиникамыздағы <b>Жартылай люкс (Пол люкс)</b> және <b>Люкс</b> палаталарының жалпы құнына қосылған! 10 күндік төлем жасағанда 6 ем-шара тегін беріледі.\n\n"
                "💰 Пакеттен тыс қосымша алу бағасы: 1 сеанс — <b>56 000 сум</b>"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_delete_seragem")]])
        if SERAGEM_PHOTO_ID:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=SERAGEM_PHOTO_ID,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

    elif data == "back_delete_seragem":
        title = {
            "ru": "🔵 <b>Доп. процедуры</b>\n\nВыберите:",
            "uz": "🔵 <b>Qo'shimcha muolajalar</b>\n\nTanlang:",
            "kz": "🔵 <b>Қосымша процедуралар</b>\n\nТаңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        items = [
            ("Nuga-best",                                                                                                        "muo_nugabest"),
            ("Seragem",                                                                                                          "muo_seragem"),
            ({"ru": "Второе сердце", "uz": "Ikkinchi yurak", "kz": "Екінші жүрек"}[lang], "t_foot_massage"),
            ({"ru": "Общий массаж",            "uz": "Umumiy massaj",                       "kz": "Жалпы массаж"}[lang],                           "t_general_massage"),
            ({"ru": "Биоэнергетический массаж", "uz": "Bioenergiya massaji", "kz": "Биоэнергетикалық массаж"}[lang],                           "t_silver_glove"),
            ({"ru": "Лимфодренаж",             "uz": "Limfadrenaj",                         "kz": "Лимфодренаж"}[lang],                            "t_lymph"),
            ({"ru": "Растяжка",                "uz": "Rastyajka",                           "kz": "Растяжка"}[lang],                               "t_stretch"),
            ({"ru": "Ударно-волновая терапия", "uz": "Zarb to'lqinli terapiya",             "kz": "Соққы-толқынды терапия"}[lang],                 "t_shockwave"),
            ("Robospine",                                                                                                        "muo_robospine"),
            ({"ru": "Криолиполиз",             "uz": "Kriolipoliz",                         "kz": "Криолиполиз"}[lang],                            "t_cryo"),
        ]
        buttons = [[InlineKeyboardButton(label, callback_data=cb)] for label, cb in items]
        buttons.append([InlineKeyboardButton(back_label, callback_data="malham_va_muolajalar")])
        await query.message.delete()
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "t_foot_massage":
        FOOT_MASSAGE_PHOTO_ID = d.get("foot_massage_photo_id", "")
        text = {
            "ru": (
                "🦶 <b>Релаксационный массаж точек стоп (Второе сердце)</b>\n\n"
                "Специальная процедура для улучшения работы всех органов тела, снятия усталости, нормализации кровообращения и улучшения сна.\n\n"
                "🎁 <b>Отличная возможность:</b> Эта процедура включена в стоимость проживания в палатах <b>Полулюкс, Люкс и VIP</b> нашей клиники! При оплате 10 дней проживания вы получаете 6 процедур бесплатно.\n\n"
                "💰 <b>Стоимость дополнительного сеанса (вне пакета):</b> 1 сеанс — <b>56 000 сум</b>"
            ),
            "uz": (
                "🦶 <b>Relaksatsion oyoq nuqtalari massaji (Ikkinchi yurak)</b>\n\n"
                "Butun tana a'zolarining faoliyatini yaxshilash, charchoqni olish, qon aylanishini normallashtirish va uyquni yaxshilash uchun mo'ljallangan maxsus muolajadir.\n\n"
                "🎁 <b>Ajoyib imkoniyat:</b> Ushbu muolaja klinikamizdagi <b>Yarim lyuks, Lyuks va VIP</b> xonalar umumiy to'lovi ichiga kiritilgan! 10 kunlik to'lovga 6 ta muolaja bepul qo'shib beriladi.\n\n"
                "💰 <b>Paketdan tashqari qo'shimcha olish narxi:</b> 1 seans — <b>56 000 so'm</b>"
            ),
            "kz": (
                "🦶 <b>Аяқ нүктелерінің релаксациялық массажы (Екінші жүрек)</b>\n\n"
                "Барлық дене мүшелерінің жұмысын жақсарту, шаршауды жою, қан айналымын қалыпқа келтіру және ұйқыны жақсарту үшін арналған арнайы ем-шара.\n\n"
                "🎁 <b>Керемет мүмкіндік:</b> Бұл ем-шара клиникамыздағы <b>Жартылай люкс, Люкс және VIP</b> палаталарының жалпы құнына қосылған! 10 күндік төлем жасағанда 6 ем-шара тегін беріледі.\n\n"
                "💰 <b>Пакеттен тыс қосымша алу бағасы:</b> 1 сеанс — <b>56 000 сум</b>"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_delete_foot")]])
        if FOOT_MASSAGE_PHOTO_ID:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=FOOT_MASSAGE_PHOTO_ID,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

    elif data == "back_delete_foot":
        await query.message.delete()
        # sub_muolajalar ro'yxatini qayta yuklash uchun data ni simulate qilamiz
        title = {
            "ru": "🔵 <b>Доп. процедуры</b>\n\nВыберите:",
            "uz": "🔵 <b>Qo'shimcha muolajalar</b>\n\nTanlang:",
            "kz": "🔵 <b>Қосымша процедуралар</b>\n\nТаңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        items = [
            ("Nuga-best",                                                                                                        "muo_nugabest"),
            ("Seragem",                                                                                                          "muo_seragem"),
            ({"ru": "Второе сердце", "uz": "Ikkinchi yurak", "kz": "Екінші жүрек"}[lang], "t_foot_massage"),
            ({"ru": "Общий массаж",            "uz": "Umumiy massaj",                       "kz": "Жалпы массаж"}[lang],                           "t_general_massage"),
            ({"ru": "Биоэнергетический массаж", "uz": "Bioenergiya massaji", "kz": "Биоэнергетикалық массаж"}[lang],                           "t_silver_glove"),
            ({"ru": "Лимфодренаж",             "uz": "Limfadrenaj",                         "kz": "Лимфодренаж"}[lang],                            "t_lymph"),
            ({"ru": "Растяжка",                "uz": "Rastyajka",                           "kz": "Растяжка"}[lang],                               "t_stretch"),
            ({"ru": "Ударно-волновая терапия", "uz": "Zarb to'lqinli terapiya",             "kz": "Соққы-толқынды терапия"}[lang],                 "t_shockwave"),
            ("Robospine",                                                                                                        "muo_robospine"),
            ({"ru": "Криолиполиз",             "uz": "Kriolipoliz",                         "kz": "Криолиполиз"}[lang],                            "t_cryo"),
        ]
        buttons = [[InlineKeyboardButton(label, callback_data=cb)] for label, cb in items]
        buttons.append([InlineKeyboardButton(back_label, callback_data="malham_va_muolajalar")])
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "t_general_massage":
        GENERAL_MASSAGE_PHOTO_ID = d.get("general_massage_photo_id", "")
        text = {
            "ru": (
                "💆‍♂️ <b>Общий массаж</b>\n\n"
                "Прекрасная оздоровительная процедура, направленная на расслабление мышц всего тела, улучшение кровообращения и лимфотока, снижение стресса и повышение гибкости суставов.\n\n"
                "🎁 <b>Отличная возможность:</b> Эта процедура включена в стоимость проживания во всех типах палат (<b>Стандарт, Полулюкс, Люкс и VIP</b>) нашей клиники! При оплате 10 дней проживания вы получаете 6 процедур бесплатно.\n\n"
                "💰 <b>Стоимость дополнительного сеанса (вне пакета):</b> 1 сеанс — <b>56 000 сум</b>"
            ),
            "uz": (
                "💆‍♂️ <b>Umumiy massaj</b>\n\n"
                "Butun tana mushaklarini bo'shashtirish, qon va limfa aylanishini yaxshilash, stressni kamaytirish hamda bo'g'imlar egasuvchanligini oshirish uchun ajoyib sog'lomlashtirish muolajasidir.\n\n"
                "🎁 <b>Ajoyib imkoniyat:</b> Ushbu muolaja klinikamizdagi <b>Standart, Yarim lyuks, Lyuks va VIP</b> xonalar umumiy to'lovi ichiga kiritilgan! 10 kunlik to'lovga 6 ta muolaja bepul qo'shib beriladi.\n\n"
                "💰 <b>Paketdan tashqari qo'shimcha olish narxi:</b> 1 seans — <b>56 000 so'm</b>"
            ),
            "kz": (
                "💆‍♂️ <b>Жалпы массаж</b>\n\n"
                "Бүкіл дене бұлшықеттерін босаңсытуға, қан мен лимфа айналымын жақсартуға, күйзелісті азайтуға және буындардың икемділігін арттыруға арналған тамаша сауықтыру ем-шарасы.\n\n"
                "🎁 <b>Керемет мүмкіндік:</b> Бұл ем-шара клиникамыздағы <b>Стандарт, Жартылай люкс, Люкс және VIP</b> палаталарының жалпы құнына қосылған! 10 күндік төлем жасағанда 6 ем-шара тегін беріледі.\n\n"
                "💰 <b>Пакеттен тыс қосымша алу бағасы:</b> 1 сеанс — <b>56 000 сум</b>"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_delete_general_massage")]])
        if GENERAL_MASSAGE_PHOTO_ID:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=GENERAL_MASSAGE_PHOTO_ID,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

    elif data == "back_delete_general_massage":
        await query.message.delete()
        title = {
            "ru": "🔵 <b>Доп. процедуры</b>\n\nВыберите:",
            "uz": "🔵 <b>Qo'shimcha muolajalar</b>\n\nTanlang:",
            "kz": "🔵 <b>Қосымша процедуралар</b>\n\nТаңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        items = [
            ("Nuga-best",                                                                                                        "muo_nugabest"),
            ("Seragem",                                                                                                          "muo_seragem"),
            ({"ru": "Второе сердце",          "uz": "Ikkinchi yurak",                       "kz": "Екінші жүрек"}[lang],                           "t_foot_massage"),
            ({"ru": "Общий массаж",           "uz": "Umumiy massaj",                        "kz": "Жалпы массаж"}[lang],                           "t_general_massage"),
            ({"ru": "Биоэнергетический массаж", "uz": "Bioenergiya massaji", "kz": "Биоэнергетикалық массаж"}[lang],                           "t_silver_glove"),
            ({"ru": "Лимфодренаж",            "uz": "Limfadrenaj",                          "kz": "Лимфодренаж"}[lang],                            "t_lymph"),
            ({"ru": "Растяжка",               "uz": "Rastyajka",                            "kz": "Растяжка"}[lang],                               "t_stretch"),
            ({"ru": "Ударно-волновая терапия","uz": "Zarb to'lqinli terapiya",              "kz": "Соққы-толқынды терапия"}[lang],                 "t_shockwave"),
            ("Robospine",                                                                                                        "muo_robospine"),
            ({"ru": "Криолиполиз",            "uz": "Kriolipoliz",                          "kz": "Криолиполиз"}[lang],                            "t_cryo"),
        ]
        buttons = [[InlineKeyboardButton(label, callback_data=cb)] for label, cb in items]
        buttons.append([InlineKeyboardButton(back_label, callback_data="malham_va_muolajalar")])
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "t_silver_glove":
        BIOENERGY_MASSAGE_PHOTO_ID = d.get("bioenergy_massage_photo_id", "")
        text = {
            "ru": (
                "⚡️ <b>Биоэнергетический массаж</b>\n\n"
                "Передовая восточная процедура с использованием специальных биоперчаток, которая помогает очистить энергетические каналы тела, улучшить кровообращение, снять боль и обновить клетки.\n\n"
                "🎁 <b>Отличная возможность:</b> Эта процедура включена в общую стоимость проживания только в палатах <b>Д/Средний</b> нашей клиники! При оплате 10 дней проживания вы получаете 6 процедур бесплатно.\n\n"
                "💰 <b>Стоимость дополнительного сеанса (вне пакета):</b> 1 сеанс — <b>56 000 сум</b>"
            ),
            "uz": (
                "⚡️ <b>Bioenergiya massaji</b>\n\n"
                "Maxsus bioqo'lqoplar yordamida tana energiya kanallarini tozalash, qon aylanishini yaxshilash, og'riqlarni qoldirish va hujayralarni yangilashga yordam beruvchi ilg'or sharqona muolajadir.\n\n"
                "🎁 <b>Ajoyib imkoniyat:</b> Ushbu muolaja klinikamizdagi faqat <b>D/O'rta miyona</b> xonalar to'lovi ichiga kiritilgan! 10 kunlik to'lovga 6 ta muolaja bepul qo'shib beriladi.\n\n"
                "💰 <b>Paketdan tashqari qo'shimcha olish narxi:</b> 1 seans — <b>56 000 so'm</b>"
            ),
            "kz": (
                "⚡️ <b>Биоэнергетикалық массаж</b>\n\n"
                "Дене қуат (энергия) арналарын тазартуға, қан айналымын жақсартуға, ауырсынуды басуға және жасушаларды жаңартуға көмектесетін арнайы биоқолғаптармен жасалатын озық шығыс ем-шарасы.\n\n"
                "🎁 <b>Керемет мүмкіндік:</b> Бұл ем-шара клиникамыздағы тек <b>Д/Орташа</b> палаталардың құнына қосылған! 10 күндік төлем жасағанда 6 ем-шара тегін беріледі.\n\n"
                "💰 <b>Пакеттен тыс қосымша алу бағасы:</b> 1 сеанс — <b>56 000 сум</b>"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_delete_bioenergy")]])
        if BIOENERGY_MASSAGE_PHOTO_ID:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=BIOENERGY_MASSAGE_PHOTO_ID,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

    elif data == "back_delete_bioenergy":
        await query.message.delete()
        title = {
            "ru": "🔵 <b>Доп. процедуры</b>\n\nВыберите:",
            "uz": "🔵 <b>Qo'shimcha muolajalar</b>\n\nTanlang:",
            "kz": "🔵 <b>Қосымша процедуралар</b>\n\nТаңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        items = [
            ("Nuga-best",                                                                                                         "muo_nugabest"),
            ("Seragem",                                                                                                           "muo_seragem"),
            ({"ru": "Второе сердце",           "uz": "Ikkinchi yurak",              "kz": "Екінші жүрек"}[lang],                 "t_foot_massage"),
            ({"ru": "Общий массаж",            "uz": "Umumiy massaj",               "kz": "Жалпы массаж"}[lang],                 "t_general_massage"),
            ({"ru": "Биоэнергетический массаж","uz": "Bioenergiya massaji",         "kz": "Биоэнергетикалық массаж"}[lang],      "t_silver_glove"),
            ({"ru": "Лимфодренаж",             "uz": "Limfadrenaj",                 "kz": "Лимфодренаж"}[lang],                  "t_lymph"),
            ({"ru": "Растяжка",                "uz": "Rastyajka",                   "kz": "Растяжка"}[lang],                     "t_stretch"),
            ({"ru": "Ударно-волновая терапия", "uz": "Zarb to'lqinli terapiya",     "kz": "Соққы-толқынды терапия"}[lang],       "t_shockwave"),
            ("Robospine",                                                                                                         "muo_robospine"),
            ({"ru": "Криолиполиз",             "uz": "Kriolipoliz",                 "kz": "Криолиполиз"}[lang],                  "t_cryo"),
        ]
        buttons = [[InlineKeyboardButton(label, callback_data=cb)] for label, cb in items]
        buttons.append([InlineKeyboardButton(back_label, callback_data="malham_va_muolajalar")])
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "t_lymph":
        LYMPH_PHOTO_ID = d.get("lymph_photo_id", "")
        text = {
            "ru": (
                "🫀 <b>Лимфодренаж (Прессотерапия)</b>\n\n"
                "Эффективная процедура, которая с помощью сжатого воздуха воздействует на лимфатическую систему, устраняет отеки тела, улучшает кровообращение и помогает избавиться от лишнего веса.\n\n"
                "🎁 <b>Отличная возможность:</b> Эта процедура включена в общую стоимость проживания только в палатах <b>Д/O'rta miyona</b> нашей клиники! При оплате 10 дней проживания вы получаете 6 процедур бесплатно.\n\n"
                "💰 <b>Стоимость процедуры:</b> 1 сеанс — <b>40 000 сум</b>"
            ),
            "uz": (
                "🫀 <b>Limfadrenaj (Pressoterapiya)</b>\n\n"
                "Maxsus apparat yordamida siqilgan havo orqali limfa tizimiga ta'sir o'tkazish, tana shishlarini yo'qotish, qon aylanishini yaxshilash va ortiqcha vazndan xalos bo'lishga yordam beruvchi samarali muolajadir.\n\n"
                "🎁 <b>Ajoyib imkoniyat:</b> Ushbu muolaja klinikamizdagi faqat <b>D/O'rta miyona</b> xonalar to'lovi ichiga kiritilgan! 10 kunlik to'lovga 6 ta muolaja bepul qo'shib beriladi.\n\n"
                "💰 <b>Muolaja narxi:</b> 1 seans — <b>40 000 so'm</b>"
            ),
            "kz": (
                "🫀 <b>Лимфодренаж (Прессотерапия)</b>\n\n"
                "Қысылған ауа арқылы лимфа жүйесіне әсер етуге, денедегі ісінулерді басуға, қан айналымын жақсартуға және артық салмақтан арылуға көмектесетін тиімді аппараттық ем-шара.\n\n"
                "🎁 <b>Керемет мүмкіндік:</b> Бұл ем-шара клиникамыздағы тек <b>Д/O'rta miyona</b> палаталарының жалпы құнына қосылған! 10 күндік төлем жасағанда 6 ем-шара тегін беріледі.\n\n"
                "💰 <b>Ем-шара бағасы:</b> 1 сеанс — <b>40 000 сум</b>"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_delete_lymph")]])
        if LYMPH_PHOTO_ID:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=LYMPH_PHOTO_ID,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

    elif data == "back_delete_lymph":
        await query.message.delete()
        title = {
            "ru": "🔵 <b>Доп. процедуры</b>\n\nВыберите:",
            "uz": "🔵 <b>Qo'shimcha muolajalar</b>\n\nTanlang:",
            "kz": "🔵 <b>Қосымша процедуралар</b>\n\nТаңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        items = [
            ("Nuga-best",                                                                                                     "muo_nugabest"),
            ("Seragem",                                                                                                       "muo_seragem"),
            ({"ru": "Второе сердце",           "uz": "Ikkinchi yurak",          "kz": "Екінші жүрек"}[lang],                 "t_foot_massage"),
            ({"ru": "Общий массаж",            "uz": "Umumiy massaj",           "kz": "Жалпы массаж"}[lang],                 "t_general_massage"),
            ({"ru": "Биоэнергетический массаж","uz": "Bioenergiya massaji",      "kz": "Биоэнергетикалық массаж"}[lang],     "t_silver_glove"),
            ({"ru": "Лимфодренаж",             "uz": "Limfadrenaj",             "kz": "Лимфодренаж"}[lang],                  "t_lymph"),
            ({"ru": "Растяжка",                "uz": "Rastyajka",               "kz": "Растяжка"}[lang],                     "t_stretch"),
            ({"ru": "Ударно-волновая терапия", "uz": "Zarb to'lqinli terapiya", "kz": "Соққы-толқынды терапия"}[lang],       "t_shockwave"),
            ("Robospine",                                                                                                     "muo_robospine"),
            ({"ru": "Криолиполиз",             "uz": "Kriolipoliz",             "kz": "Криолиполиз"}[lang],                  "t_cryo"),
        ]
        buttons = [[InlineKeyboardButton(label, callback_data=cb)] for label, cb in items]
        buttons.append([InlineKeyboardButton(back_label, callback_data="malham_va_muolajalar")])
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "t_stretch":
        STRETCH_PHOTO_ID = d.get("stretch_photo_id", "")
        text = {
            "ru": (
                "📐 <b>Растяжка (Аппарат для вытяжения позвоночника и шеи)</b>\n\n"
                "Специальная аппаратная процедура, предназначенная для лечения межпозвоночной грыжи, остеохондроза, искривления позвоночника и защемления нервов. Безопасное вытяжение снижает давление на диски и эффективно снимает боль.\n\n"
                "⚠️ <b>Примечание:</b> Эта процедура не входит в общую стоимость проживания (в стоимость палат).\n\n"
                "💰 <b>Стоимость процедуры:</b> 1 сеанс — <b>56 000 сум</b>"
            ),
            "uz": (
                "📐 <b>Rastyajka (Umurtqa va bo'yinni cho'zish apparati)</b>\n\n"
                "Umurtqalararo disk churrasi (gryaja), osteoxondroz, umurtqa pog'onasi qiyshiqligi va nerv siqilishlarini davolash uchun mo'ljallangan maxsus apparat muolajasidir. U umurtqa pog'onasini xavfsiz cho'zish orqali disklardagi bosimni kamaytiradi va og'riqni qoldiradi.\n\n"
                "⚠️ <b>Eslatma:</b> Ushbu muolaja xonalar to'lovi (umumiy to'lov) ichiga kiritilmagan.\n\n"
                "💰 <b>Muolaja narxi:</b> 1 seans — <b>56 000 so'm</b>"
            ),
            "kz": (
                "📐 <b>Растяжка (Омыртқа мен мойынды созу аппараты)</b>\n\n"
                "Омыртқааралық диск жарығын (грыжа), остеохондрозды, омыртқаның қисаюын және жүйкенің қысылуын емдеуге арналған арнайы аппараттық ем-шара. Омыртқаны қауіпсіз созу арқылы дискілердегі қысымды азайтып, ауырсынуды басады.\n\n"
                "⚠️ <b>Ескерту:</b> Бұл ем-шара палаталардың жалпы құнына (жалпы төлемге) кірмейді.\n\n"
                "💰 <b>Ем-шара бағасы:</b> 1 сеанс — <b>56 000 сум</b>"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_delete_stretch")]])
        if STRETCH_PHOTO_ID:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=STRETCH_PHOTO_ID,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

    elif data == "back_delete_stretch":
        await query.message.delete()
        title = {
            "ru": "🔵 <b>Доп. процедуры</b>\n\nВыберите:",
            "uz": "🔵 <b>Qo'shimcha muolajalar</b>\n\nTanlang:",
            "kz": "🔵 <b>Қосымша процедуралар</b>\n\nТаңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        items = [
            ("Nuga-best",                                                                                                     "muo_nugabest"),
            ("Seragem",                                                                                                       "muo_seragem"),
            ({"ru": "Второе сердце",           "uz": "Ikkinchi yurak",          "kz": "Екінші жүрек"}[lang],                 "t_foot_massage"),
            ({"ru": "Общий массаж",            "uz": "Umumiy massaj",           "kz": "Жалпы массаж"}[lang],                 "t_general_massage"),
            ({"ru": "Биоэнергетический массаж","uz": "Bioenergiya massaji",      "kz": "Биоэнергетикалық массаж"}[lang],     "t_silver_glove"),
            ({"ru": "Лимфодренаж",             "uz": "Limfadrenaj",             "kz": "Лимфодренаж"}[lang],                  "t_lymph"),
            ({"ru": "Растяжка",                "uz": "Rastyajka",               "kz": "Растяжка"}[lang],                     "t_stretch"),
            ({"ru": "Ударно-волновая терапия", "uz": "Zarb to'lqinli terapiya", "kz": "Соққы-толқынды терапия"}[lang],       "t_shockwave"),
            ("Robospine",                                                                                                     "muo_robospine"),
            ({"ru": "Криолиполиз",             "uz": "Kriolipoliz",             "kz": "Криолиполиз"}[lang],                  "t_cryo"),
        ]
        buttons = [[InlineKeyboardButton(label, callback_data=cb)] for label, cb in items]
        buttons.append([InlineKeyboardButton(back_label, callback_data="malham_va_muolajalar")])
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "t_shockwave":
        SHOCKWAVE_PHOTO_ID = d.get("shockwave_photo_id", "")
        text = {
            "ru": (
                "⚡️ <b>Ударно-волновая терапия (УВТ)</b>\n\n"
                "Один из самых эффективных современных методов лечения заболеваний опорно-двигательного аппарата с помощью высокоэнергетических акустических (звуковых) волн.\n\n"
                "<b>Основные преимущества и лечебный эффект процедуры:</b>\n"
                "• Расщепляет и растворяет вредные солевые отложения и кальцинаты в суставах и сухожилиях;\n"
                "• Быстро снимает боль при пяточной шпоре, остеохондрозе и радикулите;\n"
                "• Усиливает кровообращение и микроциркуляцию в тканях, ускоряя регенерацию;\n"
                "• Устраняет хронические воспаления и восстанавливает подвижность суставов.\n\n"
                "⚠️ <b>Примечание:</b> Эта процедура не входит в общую стоимость проживания (в стоимость палат).\n\n"
                "💰 <b>Стоимость процедуры:</b> 1 сеанс — <b>80 000 сум</b>"
            ),
            "uz": (
                "⚡️ <b>Zarb to'lqinli terapiya (UVT)</b>\n\n"
                "Yuqori energiyali akustik (tovush) to'lqinlar yordamida tayanch-harakat tizimi kasalliklarini davolovchi eng samarali zamonaviy usullardan biri.\n\n"
                "<b>Muolajaning asosiy afzalliklari va shifobaxsh ta'siri:</b>\n"
                "• Bo'g'imlar va paylarda to'planib qolgan zararli tuzlar va kalsionatlarni parchalab, eritib yuboradi;\n"
                "• Tovon shporasi, osteoxondroz va radikulit og'riqlarini tez fursatda qoldiradi;\n"
                "• To'qimalarda qon aylanishini va mikrosirkulyatsiyani kuchaytirib, tiklanish jarayonini tezlashtiradi;\n"
                "• Surunkali yallig'lanishlarni bartaraf etib, bo'g'imlar harakatchanligini tiklaydi.\n\n"
                "⚠️ <b>Eslatma:</b> Ushbu muolaja xonalar to'lovi (umumiy to'lov) ichiga kiritilmagan.\n\n"
                "💰 <b>Muolaja narxi:</b> 1 seans — <b>80 000 so'm</b>"
            ),
            "kz": (
                "⚡️ <b>Соққы-толқынды терапия (СВТ)</b>\n\n"
                "Жоғары энергиялы акустикалық (дыбыс) толқындар көмегімен тірек-қимыл аппараты ауруларын емдейтін ең тиімді заманауи әдістердің бірі.\n\n"
                "<b>Ем-шараның негізгі артықшылықтары мен емдік әсері:</b>\n"
                "• Буындар мен сіңірлерде жиналып қалған зиянды тұздар мен кальцинаттарды ыдыратып, ерітіп жібереді;\n"
                "• Өкше шпорасы, остеохондроз және радикулит ауырсынуларын тез арада басады;\n"
                "• Тіндердегі қан айналымы мен микроциркуляцияны күшейтіп, жазылу процесін тездетеді;\n"
                "• Созылмалы қабынуды жойып, буындардың қозғалғыштығын қалпына келтіреді.\n\n"
                "⚠️ <b>Ескерту:</b> Бұл ем-шара палаталардың жалпы құнына (жалпы төлемге) кірмейді.\n\n"
                "💰 <b>Ем-шара бағасы:</b> 1 сеанс — <b>80 000 сум</b>"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_delete_shockwave")]])
        if SHOCKWAVE_PHOTO_ID:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=SHOCKWAVE_PHOTO_ID,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

    elif data == "back_delete_shockwave":
        await query.message.delete()
        title = {
            "ru": "🔵 <b>Доп. процедуры</b>\n\nВыберите:",
            "uz": "🔵 <b>Qo'shimcha muolajalar</b>\n\nTanlang:",
            "kz": "🔵 <b>Қосымша процедуралар</b>\n\nТаңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        items = [
            ("Nuga-best",                                                                                                     "muo_nugabest"),
            ("Seragem",                                                                                                       "muo_seragem"),
            ({"ru": "Второе сердце",           "uz": "Ikkinchi yurak",          "kz": "Екінші жүрек"}[lang],                 "t_foot_massage"),
            ({"ru": "Общий массаж",            "uz": "Umumiy massaj",           "kz": "Жалпы массаж"}[lang],                 "t_general_massage"),
            ({"ru": "Биоэнергетический массаж","uz": "Bioenergiya massaji",      "kz": "Биоэнергетикалық массаж"}[lang],     "t_silver_glove"),
            ({"ru": "Лимфодренаж",             "uz": "Limfadrenaj",             "kz": "Лимфодренаж"}[lang],                  "t_lymph"),
            ({"ru": "Растяжка",                "uz": "Rastyajka",               "kz": "Растяжка"}[lang],                     "t_stretch"),
            ({"ru": "Ударно-волновая терапия", "uz": "Zarb to'lqinli terapiya", "kz": "Соққы-толқынды терапия"}[lang],       "t_shockwave"),
            ("Robospine",                                                                                                     "muo_robospine"),
            ({"ru": "Криолиполиз",             "uz": "Kriolipoliz",             "kz": "Криолиполиз"}[lang],                  "t_cryo"),
        ]
        buttons = [[InlineKeyboardButton(label, callback_data=cb)] for label, cb in items]
        buttons.append([InlineKeyboardButton(back_label, callback_data="malham_va_muolajalar")])
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "t_cryo":
        CRYO_PHOTO_ID = d.get("cryo_photo_id", "")
        text = {
            "ru": (
                "❄️ <b>Криолиполиз</b>\n\n"
                "Самая современная технология для безопасной и безоперационной коррекции фигуры, а также избавления от лишних жировых отложений.\n\n"
                "<b>Принцип работы и основные преимущества процедуры:</b>\n"
                "• Жировые клетки в проблемных зонах (живот, бока, бедра) замораживаются контролируемым холодом (от -5°C до -10°C);\n"
                "• Замороженные клетки разрушаются (липолиз) и естественным путем выводятся из организма;\n"
                "• Абсолютно безопасна для кожи, сосудов и окружающих тканей;\n"
                "• Улучшает обмен веществ и способствует общему оздоровлению.\n\n"
                "⚠️ <b>Примечание:</b> Эта процедура не входит в общую стоимость проживания (в стоимость палат).\n\n"
                "💰 <b>Стоимость процедуры:</b> 1 сеанс — <b>100 000 сум</b>"
            ),
            "uz": (
                "❄️ <b>Kriolipoliz</b>\n\n"
                "Tana shaklini xavfsiz va jarrohliksiz korreksiya qilish hamda ortiqcha yog' qatlamlaridan xalos bo'lish uchun qo'llaniladigan eng zamonaviy texnologiya.\n\n"
                "<b>Muolajaning ishlash prinsipi va asosiy foydalari:</b>\n"
                "• Muammoli sohalardagi (qorin, bel, son) yog' hujayralari nazorat ostidagi sovuq harorat (-5°C dan -10°C gacha) bilan muzlatiladi;\n"
                "• Muzlatilgan yog' hujayralari parchalanadi (lipoliz) va organizmdan tabiiy yo'l bilan chiqib ketadi;\n"
                "• Teriga va uning atrofidagi to'qimalarga hech qanday zarar yetkazmaydi;\n"
                "• Moddalar almashinuvini yaxshilab, umumiy sog'lomlashishga yordam beradi.\n\n"
                "⚠️ <b>Eslatma:</b> Ushbu muolaja xonalar to'lovi (umumiy to'lov) ichiga kiritilmagan.\n\n"
                "💰 <b>Muolaja narxi:</b> 1 seans — <b>100 000 so'm</b>"
            ),
            "kz": (
                "❄️ <b>Криолиполиз</b>\n\n"
                "Дене бітімін қауіпсіз және отасыз түзетуге, сондай-ақ артық май қабаттарынан арылуға арналған ең заманауи технология.\n\n"
                "<b>Ем-шараның жұмыс істеу принципі мен негізгі пайдасы:</b>\n"
                "• Проблемалық аймақтардағы (іш, бел, сан) май жасушалары бақыланатын суық температурамен (-5°C-тан -10°C-қа дейін) мұздатылады;\n"
                "• Мұздатылған май жасушалары ыдырап (липолиз), ағзадан табиғи жолмен толықтай шығарылады;\n"
                "• Теріге, тамырларға және айналадағы тіндерге ешқандай зақым келтірмейді;\n"
                "• Зат алмасуды жақсартып, жалпы сауығуға ықпал етеді.\n\n"
                "⚠️ <b>Ескерту:</b> Бұл ем-шара палаталардың жалпы құнына (жалпы төлемге) кірмейді.\n\n"
                "💰 <b>Ем-шара бағасы:</b> 1 сеанс — <b>100 000 сум</b>"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_delete_cryo")]])
        if CRYO_PHOTO_ID:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=CRYO_PHOTO_ID,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

    elif data == "back_delete_cryo":
        await query.message.delete()
        title = {
            "ru": "🔵 <b>Доп. процедуры</b>\n\nВыберите:",
            "uz": "🔵 <b>Qo'shimcha muolajalar</b>\n\nTanlang:",
            "kz": "🔵 <b>Қосымша процедуралар</b>\n\nТаңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        items = [
            ("Nuga-best",                                                                                                     "muo_nugabest"),
            ("Seragem",                                                                                                       "muo_seragem"),
            ({"ru": "Второе сердце",           "uz": "Ikkinchi yurak",          "kz": "Екінші жүрек"}[lang],                 "t_foot_massage"),
            ({"ru": "Общий массаж",            "uz": "Umumiy massaj",           "kz": "Жалпы массаж"}[lang],                 "t_general_massage"),
            ({"ru": "Биоэнергетический массаж","uz": "Bioenergiya massaji",      "kz": "Биоэнергетикалық массаж"}[lang],     "t_silver_glove"),
            ({"ru": "Лимфодренаж",             "uz": "Limfadrenaj",             "kz": "Лимфодренаж"}[lang],                  "t_lymph"),
            ({"ru": "Растяжка",                "uz": "Rastyajka",               "kz": "Растяжка"}[lang],                     "t_stretch"),
            ({"ru": "Ударно-волновая терапия", "uz": "Zarb to'lqinli terapiya", "kz": "Соққы-толқынды терапия"}[lang],       "t_shockwave"),
            ("Robospine",                                                                                                     "muo_robospine"),
            ({"ru": "Криолиполиз",             "uz": "Kriolipoliz",             "kz": "Криолиполиз"}[lang],                  "t_cryo"),
        ]
        buttons = [[InlineKeyboardButton(label, callback_data=cb)] for label, cb in items]
        buttons.append([InlineKeyboardButton(back_label, callback_data="malham_va_muolajalar")])
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "m_fitobar":
        FITOBAR_PHOTO_ID = d.get("fitobar_photo_id", "")
        text = {
            "ru": (
                "🌱 <b>Целебный Фито-Бар нашей клиники</b>\n\n"
                "В каждом отделении клиники организованы уголки Фито-Бара, где ежедневно 3–4 раза завариваются свежие травяные чаи. Все чаи предоставляются <b>бесплатно и в неограниченном количестве!</b>\n\n"
                "⚠️ <b>Рекомендация врача:</b> Поскольку чаи обладают сильным лечебным эффектом, рекомендуется пить их 2–3 раза в день по 200 мл.\n\n"
                "<b>6 видов целебных чаев в нашем Фито-Баре:</b>\n"
                "1️⃣ 🟢 <b>Желчегонный и печеночный чай</b> — очищает печень от токсинов, стимулирует отток желчи и улучшает пищеварение.\n"
                "2️⃣ 🟡 <b>Чай для похудения</b> — ускоряет обмен веществ, способствует расщеплению жиров и помогает снизить вес.\n"
                "3️⃣ 🔵 <b>Почечный чай</b> — мочегонный эффект, выводит соли, снимает отёки и воспаления в почках.\n"
                "4️⃣ 🟤 <b>Грудной чай (от бронхита)</b> — очищает дыхательные пути, способствует отхождению мокроты и укрепляет лёгкие.\n"
                "5️⃣ 🔴 <b>Антипаразитарный чай</b> — безопасно очищает организм от паразитов и продуктов их жизнедеятельности.\n"
                "6️⃣ 🟣 <b>Успокоительный чай</b> — снимает стресс, нормализует сон и устраняет усталость.\n\n"
                "🌿 <i>Используйте силу природы для вашего здоровья!</i>"
            ),
            "uz": (
                "🌱 <b>Klinikamizning Shifobaxsh Fito-Bari</b>\n\n"
                "Klinikamizning har bir bo'limida Fito-Bar burchaklari tashkil etilgan. U yerda har kuni 3–4 mahal yangi giyohli choylar damlab qo'yiladi. Barcha choylar <b>bepul va cheklanmagan miqdorda!</b>\n\n"
                "⚠️ <b>Shifokor tavsiyasi:</b> Choylar kuchli shifobaxsh ta'sirga ega bo'lgani uchun kuniga 2–3 mahal, 200 ml dan ichish tavsiya etiladi.\n\n"
                "<b>Fito-barimizdagi 6 xil shifobaxsh choylar:</b>\n"
                "1️⃣ 🟢 <b>O't va jigar choyi</b> — o't haydovchi, jigarni toksinlardan tozalovchi va hazm tizimini yaxshilovchi.\n"
                "2️⃣ 🟡 <b>Ozdiruvchi choy</b> — moddalar almashinuvini tezlashtiruvchi, tana yog'larini erituvchi.\n"
                "3️⃣ 🔵 <b>Buyrak choyi</b> — siydik haydovchi, buyrakdagi tuz va shishlarni haydovchi.\n"
                "4️⃣ 🟤 <b>Bronxit choyi</b> — nafas yo'llarini tozalovchi, balg'am ko'chiruvchi va o'pkani mustahkamlovchi.\n"
                "5️⃣ 🔴 <b>Gijja choyi</b> — organizmni parazitlar va ularning toksinlaridan xavfsiz tozalovchi.\n"
                "6️⃣ 🟣 <b>Asab choyi</b> — tinchlantiruvchi, uyquni yaxshilovchi va charchoqni oluvchi.\n\n"
                "🌿 <i>Sog'ligingiz uchun fito-barimizdan unumli foydalaning!</i>"
            ),
            "kz": (
                "🌱 <b>Клиникамыздың шипалы Фито-Бары</b>\n\n"
                "Клиникамыздың әрбір бөлімшесінде Фито-Бар бұрыштары ұйымдастырылған. Онда күн сайын 3–4 рет жаңадан демделген емдік шөп шайлары қойылады. Барлық шайлар <b>тегін және шектеусіз!</b>\n\n"
                "⚠️ <b>Дәрігер кеңесі:</b> Шайлардың шипалық әсері күшті болғандықтан, күніне 2–3 рет, 200 мл-ден ішу ұсынылады.\n\n"
                "<b>Фито-бардағы 6 түрлі шипалы шай:</b>\n"
                "1️⃣ 🟢 <b>Өт және бауыр шайы</b> — өт айдайды, бауырды токсиндерден тазартады, ас қорытуды жақсартады.\n"
                "2️⃣ 🟡 <b>Арықтату шайы</b> — зат алмасуды тездетеді, денедегі майларды ерітеді.\n"
                "3️⃣ 🔵 <b>Бүйрек шайы</b> — несеп айдаушы, тұздар мен ісінуді кетіреді, қабынуға қарсы.\n"
                "4️⃣ 🟤 <b>Бронхит шайы</b> — тыныс жолдарын тазартады, қақырық түсіреді, өкпені нығайтады.\n"
                "5️⃣ 🔴 <b>Антипаразиттік шай</b> — ағзаны паразиттерден қауіпсіз тазартады.\n"
                "6️⃣ 🟣 <b>Жүйке жүйесін тыныштандыру шайы</b> — күйзелісті басады, ұйқыны жақсартады.\n\n"
                "🌿 <i>Денсаулығыңыз үшін фито-барымыздан пайдаланыңыз!</i>"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_delete_fitobar")]])
        if FITOBAR_PHOTO_ID:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=FITOBAR_PHOTO_ID,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

    elif data == "back_delete_fitobar":
        await query.message.delete()
        title = {
            "ru": "🟢 <b>Малхам и травы</b>\n\nВыберите:",
            "uz": "🟢 <b>Малхам va o'tlar</b>\n\nTanlang:",
            "kz": "🟢 <b>Малхам және шөптер</b>\n\nТаңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        items = [
            ("Malham",                                                                              "mal_malham"),
            ({"ru": "Фито бар",         "uz": "Fito bar",      "kz": "Фито бар"}[lang],           "m_fitobar"),
            ({"ru": "Миндальное масло", "uz": "Bodom yog'i",   "kz": "Бадам майы"}[lang],         "m_bodom"),
            ({"ru": "Оливковое масло",  "uz": "Zaytun yog'i",  "kz": "Зәйтүн майы"}[lang],       "m_zaytun"),
            ({"ru": "Чудо мазь",        "uz": "Chuda maz",     "kz": "Ғажайып жақпа май"}[lang],  "mal_chuda"),
        ]
        buttons = [[InlineKeyboardButton(label, callback_data=cb)] for label, cb in items]
        buttons.append([InlineKeyboardButton(back_label, callback_data="malham_va_muolajalar")])
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "m_bodom":
        ALMOND_OIL_PHOTO_ID = d.get("almond_oil_photo_id", "")
        text = {
            "ru": (
                "🌱 <b>Целебные свойства миндального масла (Рекомендации Ибн Сины)</b>\n\n"
                "<i>«Миндальное масло — один из эликсиров вечной молодости» — Абу Али ибн Сина.</i>\n\n"
                "<b>Польза при наружном применении (Массаж и растирание):</b>\n"
                "• <b>Уход за кожей:</b> Разглаживает морщины, подтягивает кожу, делает её гладкой и чистой. Устраняет пятна, веснушки и следы от ран.\n"
                "• <b>Нервная система:</b> При массаже лица и головы улучшает кровообращение, питает нервные волокна и успокаивает. Незаменимо при реабилитации после инсульта.\n"
                "• <b>Глаза и уши:</b> Повышает остроту зрения. При боли и шуме в ушах закапывают по 1 капле.\n\n"
                "<b>Польза при приёме внутрь (По 1 ч. ложке перед едой):</b>\n"
                "• Измельчает и выводит камни из почек, мочевого и желчного пузыря;\n"
                "• Выводит соли, накопившиеся в суставах и позвоночнике;\n"
                "• Устраняет воспалительные процессы во внутренних органах.\n\n"
                "💰 <b>Цена продукта:</b> <b>48 000 сум</b>"
            ),
            "uz": (
                "🌱 <b>Bodom yog'ining shifobaxsh xislatlari (Ibn Sino tavsiyalari)</b>\n\n"
                "<i>«Bodom moyi — mangu yoshlik eliksirlaridan biridir» — Abu Ali ibn Sino.</i>\n\n"
                "<b>Tashqi qo'llashdagi foydalari (Massaj va surkash orqali):</b>\n"
                "• <b>Yuz va tana parvarishi:</b> Ajinlarni yozadi, terini tarang, silliq va tiniq qiladi. Dog', sepkil va yara izlarini yo'qotadi.\n"
                "• <b>Asab va miya faoliyati:</b> Yuz va bosh qismiga surtilsa, qon aylanishini yaxshilaydi, asab tolalarini oziqlantiradi. Insultdan keyingi falajliklarni davolashda beqiyosdir.\n"
                "• <b>Ko'z va quloq:</b> Ko'rish quvvatini oshiradi. Quloq og'riganda 1 tomchi tomiziladi.\n\n"
                "<b>Ichishga tavsiyasidagi foydalari (Ovqatdan oldin 1 choy qoshiq):</b>\n"
                "• Buyrak, qovuq va o't pufagidagi toshlarni maydalab eritadi;\n"
                "• Bo'g'imlar va umurtqa pog'onasidagi tuzlarni yo'qotadi;\n"
                "• Ichki a'zolardagi yallig'lanish jarayonlarini bartaraf etadi.\n\n"
                "💰 <b>Mahsulot narxi:</b> <b>48 000 so'm</b>"
            ),
            "kz": (
                "🌱 <b>Бадам майының шипалық қасиеттері (Ибн Синаның кеңестері)</b>\n\n"
                "<i>«Бадам майы — мәңгілік жастық эликсирлерінің бірі» — Әбу Әли ибн Сина.</i>\n\n"
                "<b>Сырттай қолданудың пайдасы (Массаж және жағу арқылы):</b>\n"
                "• <b>Тері күтімі:</b> Әжімдерді жазады, теріні тартып тегіс етеді. Дақтарды, секпілдерді және жара іздерін кетіреді.\n"
                "• <b>Жүйке жүйесі:</b> Бет пен басты массаждағанда қан айналымын жақсартады, жүйке талшықтарын қоректендіреді. Инсульттан кейінгі сал ауруын емдеуде таптырмас.\n"
                "• <b>Көз және құлақ:</b> Көру қабілетін арттырады. Құлақ ауырғанда 1 тамшыдан тамызылады.\n\n"
                "<b>Ішке қабылдаудың пайдасы (Тамақтану алдында 1 шай қасық):</b>\n"
                "• Бүйрек, қуық және өт қабындағы тастарды уатып ерітеді;\n"
                "• Буындар мен омыртқадағы тұздарды жояды;\n"
                "• Ішкі мүшелердегі қабыну процестерін басады.\n\n"
                "💰 <b>Өнім бағасы:</b> <b>48 000 сум</b>"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_delete_almond")]])
        if ALMOND_OIL_PHOTO_ID:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=ALMOND_OIL_PHOTO_ID,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

    elif data == "back_delete_almond":
        await query.message.delete()
        title = {
            "ru": "🟢 <b>Малхам и травы</b>\n\nВыберите:",
            "uz": "🟢 <b>Малхам va o'tlar</b>\n\nTanlang:",
            "kz": "🟢 <b>Малхам және шөптер</b>\n\nТаңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        items = [
            ("Malham",                                                                              "mal_malham"),
            ({"ru": "Фито бар",         "uz": "Fito bar",      "kz": "Фито бар"}[lang],           "m_fitobar"),
            ({"ru": "Миндальное масло", "uz": "Bodom yog'i",   "kz": "Бадам майы"}[lang],         "m_bodom"),
            ({"ru": "Оливковое масло",  "uz": "Zaytun yog'i",  "kz": "Зәйтүн майы"}[lang],       "m_zaytun"),
            ({"ru": "Чудо мазь",        "uz": "Chuda maz",     "kz": "Ғажайып жақпа май"}[lang],  "mal_chuda"),
        ]
        buttons = [[InlineKeyboardButton(label, callback_data=cb)] for label, cb in items]
        buttons.append([InlineKeyboardButton(back_label, callback_data="malham_va_muolajalar")])
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "m_zaytun":
        OLIVE_OIL_PHOTO_ID = d.get("olive_oil_photo_id", "")
        text = {
            "ru": (
                "🫒 <b>Целебные свойства оливкового масла</b>\n\n"
                "Чем дольше хранится оливковое масло, тем выше его целебная сила. Оно сохраняет свои свойства до 400 лет.\n\n"
                "<b>Основные лечебные свойства:</b>\n"
                "• <b>Пищеварение и кишечник:</b> Лечит заболевания кишечника, уничтожает паразитов. Мягко устраняет запоры.\n"
                "• <b>Печень и почки:</b> Очищает печень от токсинов и омолаживает её. Расщепляет и выводит камни из почек и мочевого пузыря.\n"
                "• <b>Суставы и сосуды:</b> Помогает при болях в суставах и ревматизме, предотвращает судороги.\n"
                "• <b>Женское здоровье:</b> Широко используется в гинекологии в виде лечебных тампонов.\n\n"
                "💡 <b>Лечебные рецепты:</b>\n"
                "1. <b>При гриппе и простуде:</b> Смешать 1 ст. ложку масла с 1 ч. ложкой мёда. Принимать 3 раза в день за 30 минут до еды. При насморке — 2–3 капли в нос.\n"
                "2. <b>При аденоме:</b> Мелко нарезанную капусту и зелень сельдерея заправить 1 ст. ложкой оливкового масла и употреблять перед едой.\n\n"
                "💰 <b>Цена продукта:</b> <b>42 000 сум</b>"
            ),
            "uz": (
                "🫒 <b>Zaytun yog'ining shifobaxsh xislatlari</b>\n\n"
                "Zaytun yog'i qanchalik uzoq saqlansa, uning shifobaxshlik quvvati shunchalik ortib boradi va 400 yilgacha o'z kuchini yo'qotmaydi.\n\n"
                "<b>Asosiy shifobaxsh xususiyatlari:</b>\n"
                "• <b>Hazm va ichaklar:</b> Ichak kasalliklariga shifobaxsh, me'dadagi parazitlarni o'ldiradi. Qabziyatni bartaraf etadi.\n"
                "• <b>Jigar va buyrak:</b> Jigarni tozalaydi va yoshartiradi. Buyrak hamda qovuqdagi toshlarni maydalab tushiradi.\n"
                "• <b>A'zolar va bo'g'imlar:</b> Bo'g'im og'riqlari va revmatizmni davolaydi, tomir tortishishining oldini oladi.\n"
                "• <b>Ayollar salomatligida:</b> Ginekologiyada shifobaxsh tampon sifatida keng qo'llaniladi.\n\n"
                "💡 <b>Shifobaxsh retseptlar:</b>\n"
                "1. <b>Gripp va shamollashda:</b> 1 osh qoshiq zaytun yog'ini 1 choy qoshiq asal bilan aralashtirib, kuniga 3 mahal ovqatdan 30 daqiqa oldin ichiladi. Tumovda burunga 2–3 tomchi.\n"
                "2. <b>Adenomada:</b> Mayda to'g'ralgan karam va kashnichga 1 osh qoshiq zaytun yog'i aralashtirib, ovqatdan oldin iste'mol qilinadi.\n\n"
                "💰 <b>Mahsulot narxi:</b> <b>42 000 so'm</b>"
            ),
            "kz": (
                "🫒 <b>Зәйтүн майының шипалық қасиеттері</b>\n\n"
                "Зәйтүн майы неғұрлым ұзақ сақталса, оның шипалық күші соғұрлым арта түседі. Ол өзінің қасиетін 400 жылға дейін жоғалтпайды.\n\n"
                "<b>Негізгі емдік қасиеттері:</b>\n"
                "• <b>Ас қорыту және ішек:</b> Ішек ауруларын емдейді, паразиттерді жояды. Іш қатуды тиімді басады.\n"
                "• <b>Бауыр және бүйрек:</b> Бауырды тазартып жасартады. Бүйрек пен қуықтағы тастарды уатып түсіреді.\n"
                "• <b>Буындар мен тамырлар:</b> Буын аурулары мен ревматизмді емдейді, бұлшықет тартылуының алдын алады.\n"
                "• <b>Әйелдер денсаулығы:</b> Гинекологияда шипалы тампондар ретінде кеңінен қолданылады.\n\n"
                "💡 <b>Шипалық рецептер:</b>\n"
                "1. <b>Тұмау мен суық тиюде:</b> 1 ас қасық майды 1 шай қасық балмен араластырып, күніне 3 рет тамақтанудан 30 минут бұрын ішіңіз. Тұмауда мұрынға 2–3 тамшы.\n"
                "2. <b>Аденомада:</b> Ұсақталған қырыққабат пен балдыркөкке 1 ас қасық зәйтүн майын қосып, тамақтанар алдында жеңіз.\n\n"
                "💰 <b>Өнім бағасы:</b> <b>42 000 сум</b>"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_delete_olive")]])
        if OLIVE_OIL_PHOTO_ID:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=OLIVE_OIL_PHOTO_ID,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

    elif data == "back_delete_olive":
        await query.message.delete()
        title = {
            "ru": "🟢 <b>Малхам и травы</b>\n\nВыберите:",
            "uz": "🟢 <b>Малхам va o'tlar</b>\n\nTanlang:",
            "kz": "🟢 <b>Малхам және шөптер</b>\n\nТаңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        items = [
            ("Malham",                                                                              "mal_malham"),
            ({"ru": "Фито бар",         "uz": "Fito bar",      "kz": "Фито бар"}[lang],           "m_fitobar"),
            ({"ru": "Миндальное масло", "uz": "Bodom yog'i",   "kz": "Бадам майы"}[lang],         "m_bodom"),
            ({"ru": "Оливковое масло",  "uz": "Zaytun yog'i",  "kz": "Зәйтүн майы"}[lang],       "m_zaytun"),
            ({"ru": "Чудо мазь",        "uz": "Chuda maz",     "kz": "Ғажайып жақпа май"}[lang],  "mal_chuda"),
        ]
        buttons = [[InlineKeyboardButton(label, callback_data=cb)] for label, cb in items]
        buttons.append([InlineKeyboardButton(back_label, callback_data="malham_va_muolajalar")])
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

    elif data in (
        "mal_malham", "mal_chuda",
        "muo_robospine",
    ):
        soon_text = {
            "ru": "🔄 Информация будет добавлена в ближайшее время...",
            "uz": "🔄 Ma'lumot tez orada qo'shiladi...",
            "kz": "🔄 Aqparat jaqın arada qosıladı...",
        }[lang]
        # Orqaga tugmasi — malham yoki muolaja bo'limiga qaytaradi
        back_cb = "sub_malhamlar" if data.startswith("mal_") else "sub_muolajalar"
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data=back_cb)]])
        await query.edit_message_text(soon_text, reply_markup=kb)

    # ── Shifokor ──
    elif data == "menu_doctor":
        text = {
            "ru": (
                "🌟 <b>Основатель и Главный Врач Клиники — Эргашев Бердикул Джуракулович</b>\n\n"
                "👴🏼 Врач высшей категории, Почетный профессор, Действительный член Академии наук Турон и Академик.\n"
                "Автор знаменитых книг\n"
                "📘 <i>'Ergash ota Mo'jizalari'</i>\n"
                "📘 <i>'Eng shirin lazzat — salomatlikdir'</i>\n\n"
                "🔬 <b>Уникальный рецепт подлинного \"Malxam\" из 32 видов целебных трав!</b>\n"
                "Разработан Бердикулом Эргашевым в результате глубоких научных исследований, состоит ровно из 32 видов специальных трав. Его единственный подлинный рецепт готовится исключительно в нашей клинике!\n\n"
                "⚠️ <b>ВНИМАНИЕ, ОСТЕРЕГАЙТЕСЬ МОШЕННИКОВ!</b>\n"
                "В последнее время в социальных сетях мошенники утверждают, что якобы 'нашли или получили рецепт Malxam от Эргаш ота'. Будьте бдительны! Настоящий, целебный и лицензированный оригинальный <b>Malxam</b> выдается пациентам только в самой клинике 'Эргаш Ота'. Не доверяйте свое здоровье подделкам!"
            ),
            "uz": (
                "🌟 <b>Klinika Asoschisi va Bosh Shifokori — Ergashev Berdiqul Jo'raqulovich</b>\n\n"
                "👨‍⚕️ Oliy toifali shifokor, Faxriy professor, Turon Fanlar Akademiyasining haqiqiy a'zosi va Akademik.\n"
                "Mashhur\n"
                "📘 <i>'Ergash ota Mo'jizalari'</i>\n"
                "📘 <i>'Eng shirin lazzat — salomatlikdir'</i>\n"
                "kitoblari muallifi.\n\n"
                "🔬 <b>32 Xil Giyohdan Tayyorlanadigan Noyob va Haqiqiy \"Malxam\" Retsepti!</b>\n"
                "Berdiqul Ergashev tomonidan chuqur ilmiy izlanishlar natijasida, aynan 32 xil maxsus giyohdan tarkib topgan bo'lib, uning yagona haqiqiy retsepti faqatgina bizning klinikada tayyorlanadi!\n\n"
                "⚠️ <b>DIQQAT, FIRIBGARLARDAN OGOH BO'LING!</b>\n"
                "Hozirgi kunda ijtimoiy tarmoqlarda 'Ergash otaning Malxam retseptini topdik, biz ham tayyorlayapmiz' deb odamlarni aldab, soxta mahsulot sotayotgan firibgarlar ko'paygan. Ogoh bo'ling! Haqiqiy, shifobaxsh va litsenziyalangan original <b>Malxam</b> faqat va faqat 'Ergash Ota' klinikasining o'zida bemorlarga beriladi. O'z sog'lig'ingizni soxtakorlarga ishonib topshirmang!"
            ),
            "kz": (
                "🌟 <b>Клиниканың Негізін Қалаушы және Бас Дәрігері — Эргашев Бердіқұл Жорақұлұлы</b>\n\n"
                "👴🏼 Жоғары санатты дәрігер, Құрметті профессор, Тұран Ғылым Академиясының толық мүшесі және Академик.\n"
                "Белгілі кітаптарының авторы\n"
                "📘 <i>'Ergash ota Mo'jizalari'</i>\n"
                "📘 <i>'Eng shirin lazzat — salomatlikdir'</i>\n\n"
                "🔬 <b>32 Түрлі Шөптен Дайындалатын Бірегей және Нағыз \"Malxam\" Рецепті!</b>\n"
                "Бердіқұл Эргашевтің терең ғылыми ізденістерінің нәтижесінде, дәл 32 түрлі арнайы шөптен құралған және оның жалғыз шынайы рецепті тек біздің клиникада дайындалады!\n\n"
                "⚠️ <b>НАЗАР АУДАРЫҢЫЗ, АЛАЯҚТАРДАН САҚ БОЛЫҢЫЗ!</b>\n"
                "Қазіргі уақытта әлеуметтік желілерде 'Эргаш отаның Malxam рецептін таптық, біз де дайындаймыз' деп адамдарды алдап, жалған өнім сатып жүрген алаяқтар көбейіп кетті. Сақ болыңыз! Нағыз, шипалы және лицензияланған түпнұсқа <b>Malxam</b> тек қана 'Эргаш Ота' клиникасының өзінде бейтаптарға беріледі. Денсаулығыңызды жалған емшілерге сеніп тапсырмаңыз!"
            ),
        }[lang]
        back_label    = {"ru": "⬅️ Назад",                       "uz": "⬅️ Orqaga",                    "kz": "⬅️ Артқа"}[lang]
        juraqulov_label = {"ru": "👨‍⚕️ Врач Джуракулов Жахонгир", "uz": "👨‍⚕️ Vrach Jo'raqulov Jaxongir", "kz": "👨‍⚕️ Дәрігер Жорақұлов Жахонгир"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(juraqulov_label, callback_data="doctor_juraqulov")],
            [InlineKeyboardButton(back_label,      callback_data="back_to_about_menu")],
        ])
        CHIEF_DOCTOR_PHOTO_ID = d.get("doctor", {}).get("photo_id", "")
        await query.message.delete()
        if CHIEF_DOCTOR_PHOTO_ID:
            await context.bot.send_photo(chat_id=chat_id, photo=CHIEF_DOCTOR_PHOTO_ID,
                                         caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=chat_id, text=text,
                                           parse_mode="HTML", reply_markup=kb)

    elif data == "doctor_juraqulov":
        text = {
            "ru": "👨‍⚕️ <b>Врач высшей категории — Джуракулов Жахонгир Бердикулович</b>\n\nВедущий ассистент главного врача. Врач с 15-летним богатым опытом работы. Является главным помощником главного врача в приёме пациентов, диагностике и эффективной организации курсов лечения с использованием целебного Malxam и натуральных трав.",
            "uz": "👨‍⚕️ <b>Oliy toifali shifokor — Jo'raqulov Jaxongir Berdiqul o'g'li</b>\n\nBosh shifokorning yetakchi yordamchisi. 15 yillik boy tajribaga ega shifokor. Klinikamizda bemorlarni qabul qilish, tashxis qo'yish hamda shifobaxsh Malxam va tabiiy giyohlar bilan davolash kurslarini samarali tashkil etishda bosh shifokorning bosh ko'makchisi hisoblanadi.",
            "kz": "👨‍⚕️ <b>Жоғары санатты дәрігер — Жорақұлов Жахонгир Бердіқұл ұлы</b>\n\nБас дәрігердің жетекші көмекшісі. 15 жылдық бай тәжірибесі бар дәрігер. Клиникамызда бейтаптарды қабылдау, диагноз қою және шипалы Malxam мен табиғи шөптер арқылы емдеу курстарын тиімді ұйымдастыруда бас дәрігердің басты көмекшісі болып табылады.",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_doctor")]])
        JURAQULOV_PHOTO_ID = d.get("juraqulov_photo_id", "")
        await query.message.delete()
        if JURAQULOV_PHOTO_ID:
            await context.bot.send_photo(chat_id=chat_id, photo=JURAQULOV_PHOTO_ID,
                                         caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=chat_id, text=text,
                                           parse_mode="HTML", reply_markup=kb)

    elif data == "back_to_about_menu":
        # Barcha jamoa xabarlarini o'chirish
        ids_to_delete = (
            context.user_data.pop("team_media_ids", []) +
            [context.user_data.pop("team_text_id", None)] +
            [context.user_data.pop("team_main_msg_id", None)]
        )
        for mid in ids_to_delete:
            if mid:
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=mid)
                except Exception:
                    pass
        # Klinika menyusini qaytarish
        title = {
            "ru": "🏥 *Клиника Эргаш-Ота*\n\nВыберите раздел:",
            "uz": "🏥 *Эргаш-Ота klinikasi*\n\nBo'limni tanlang:",
            "kz": "🏥 *Эргаш-Ота клиникасы*\n\nБөлімді таңдаңыз:",
        }[lang]
        await context.bot.send_message(chat_id=chat_id, text=title,
                                       parse_mode="Markdown",
                                       reply_markup=clinic_submenu_keyboard(lang))

    # ── Jamoa ──
    elif data == "menu_staff":
        text = {
            "ru": "👥 Наша дружная команда\n\nВ нашей клинике работают высококвалифицированные врачи, специалисты народной медицины, физиотерапевты и заботливые медсестры с многолетним опытом. Каждый наш сотрудник готов служить круглосуточно, чтобы восстановить ваше здоровье, обеспечить своевременное и качественное прохождение процедур, а также сделать так, чтобы вы чувствовали себя как дома!",
            "uz": "👥 Bizning Ahil Jamoamiz\n\nKlinikamizda o'z kasbining mohir ustasi bo'lgan, ko'p yillik tajribaga ega shifokorlar, xalq tabobati mutaxassislari, fizioterapevtlar va g'amxo'r hamshiralar faoliyat olib borishadi. Har bir xodimimiz sizning salomatligingizni tiklash, muolajalarni o'z vaqtida va oliy darajada olishingiz hamda o'zingizni xuddi uyingizdagidek his qilishingiz uchun tunu-kun xizmatga tayyor!",
            "kz": "👥 Біздің ұйымшыл ұжымымыз\n\nКлиникамызда өз ісінің шебері болып табылатын, көпжылдық тәжірибесі бар дәрігерлер, халық медицинасының мамандары, физиотерапевтер және қамқор медбикелер қызмет атқарады. Біздің әрбір қызметкеріміз сіздің денсаулығыңызды қалпына келтіру, ем-шараларды өз уақытында әрі жоғары деңгейде алуыңыз және өзіңізді үйдегідей сезінуіңіз үшін тәулік бойы қызмет етуге дайын!",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_to_about_menu")]])

        context.user_data["team_main_msg_id"] = query.message.message_id
        await query.answer()

        team_photos = [p for p in d.get("team_photos", []) if p]
        photo_msg_ids = []

        # Rasmlarni bitta-bitta yuboramiz (send_media_group o'rniga)
        for ph in team_photos:
            try:
                msg = await context.bot.send_photo(chat_id=chat_id, photo=ph)
                photo_msg_ids.append(msg.message_id)
            except Exception as e:
                logger.error(f"team photo send error: {e}")

        # Matn + Orqaga tugmasi
        text_msg = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=kb)

        context.user_data["team_media_ids"] = photo_msg_ids
        context.user_data["team_text_id"] = text_msg.message_id

    # ── Kasalliklar ──
    elif data == "menu_diseases":
        title = {
            "ru": "🩺 *Список лечимых заболеваний*\n\nВыберите направление:",
            "uz": "🩺 *Davolanadigan kasalliklar ro'yxati*\n\nYo'nalishni tanlang:",
            "kz": "🩺 *Емделетін аурулар тізімі*\n\nБағытты таңдаңыз:",
        }[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                {"ru": "🍏 ЖКТ и обмен веществ", "uz": "🍏 Oshqozon-ichak va modda almashinuvi", "kz": "🍏 Асқазан-ішек және зат алмасу"}[lang],
                callback_data="dis_oshqozon")],
            [InlineKeyboardButton(
                {"ru": "🫀 Сердечно-сосудистые и дыхательные", "uz": "🫀 Yurak-qon tomir va nafas yo'llari", "kz": "🫀 Жүрек-қан тамыр және тыныс жолдары"}[lang],
                callback_data="dis_yurak")],
            [InlineKeyboardButton(
                {"ru": "🧠 Нервы, позвоночник и суставы", "uz": "🧠 Asab, umurtqa va bo'g'imlar", "kz": "🧠 Жүйке, омыртқа және буындар"}[lang],
                callback_data="dis_asab")],
            [InlineKeyboardButton(
                {"ru": "🩺 Инфекции и паразиты (Глисты)", "uz": "🩺 Infeksiya va parazitlar (Gijja)", "kz": "🩺 Инфекция және паразиттер (Құрт)"}[lang],
                callback_data="dis_infeksiya")],
            [InlineKeyboardButton(
                {"ru": "🧬 Иммун., гормональные и кожные", "uz": "🧬 Immun, gormonal va teri kasalliklari", "kz": "🧬 Иммун., гормоналды және тері"}[lang],
                callback_data="dis_immun")],
            [InlineKeyboardButton(
                {"ru": "✨ Оздоровление и профилактика", "uz": "✨ Umumiy tozalash va profilaktika", "kz": "✨ Сауықтыру және профилактика"}[lang],
                callback_data="dis_umumiy")],
            [InlineKeyboardButton(
                {"ru": "🔍 Моей болезни нет в списке", "uz": "🔍 Mening kasalligim ro'yxatda yo'q", "kz": "🔍 Менің ауруым тізімде жоқ"}[lang],
                callback_data="disease_not_found")],
            [InlineKeyboardButton(
                {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang],
                callback_data="menu_clinic")],
        ])
        await query.edit_message_text(title, parse_mode="Markdown", reply_markup=kb)

    elif data == "dis_oshqozon":
        text = {
            "ru": (
                "🍏 *Заболевания ЖКТ и обмена веществ:*\n\n"
                "Срок лечения обычно составляет *18, 21 или 24 дня* в зависимости от состояния пациента и размера камней:\n\n"
                "• Желчнокаменная болезнь (естественное выведение камней из желчного пузыря и комплексное лечение)\n"
                "• Заболевания желудочно-кишечного тракта\n"
                "• Заболевания печени и желчевыводящих путей\n"
                "• Хронические запоры и хронические диареи\n"
                "• Долихоколон, долихосигма\n"
                "• Болезнь Гиршпрунга и демпинг-синдром\n"
                "• Ожирение (снижение веса)"
            ),
            "uz": (
                "🍏 *Oshqozon-ichak va modda almashinuvi kasalliklari:*\n\n"
                "Bemor holatiga va toshlarning o'lchamiga qarab davolanish muddati odatda *18, 21 yoki 24 kun* etib belgilanadi:\n\n"
                "• O't tosh kasalligi (O't qopidagi toshlarni tabiiy tushirish va kompleks davolash)\n"
                "• Oshqozon-ichak yo'llari kasalliklari\n"
                "• Jigar va o't yo'llari kasalliklari\n"
                "• Surunkali qabziyatlar va surunkali diareyalar\n"
                "• Dolixokolon, dolixosigma kasalliklari\n"
                "• Girshprung kasalligi va Demping sindrom\n"
                "• Semizlik xastaligi (vazn kamaytirish)"
            ),
            "kz": (
                "🍏 *Асқазан-ішек және зат алмасу аурулары:*\n\n"
                "Науқас жағдайына және тастардың өлшеміне байланысты емдеу мерзімі *18, 21 немесе 24 күн* белгіленеді:\n\n"
                "• Өт тас ауруы (өт қабындағы тастарды табиғи жолмен шығару және кешенді емдеу)\n"
                "• Асқазан-ішек жолдары аурулары\n"
                "• Бауыр және өт жолдары аурулары\n"
                "• Созылмалы іш қату және созылмалы диареялар\n"
                "• Долихоколон, долихосигма аурулары\n"
                "• Гиршпрунг ауруы және демпинг-синдром\n"
                "• Семіздік (салмақ азайту)"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_diseases")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "dis_yurak":
        text = {
            "ru": (
                "🫀 *Сердечно-сосудистые и респираторные заболевания:*\n\n"
                "В зависимости от степени заболевания курс лечения длится *от 18 до 24 дней:*\n\n"
                "• Гипертоническая болезнь и её осложнения\n"
                "• Атеросклероз и ишемическая болезнь сердца\n"
                "• Болезнь Рейно\n"
                "• Хронические заболевания лёгких"
            ),
            "uz": (
                "🫀 *Yurak-qon tomir va nafas yo'llari kasalliklari:*\n\n"
                "Kasallik darajasiga qarab davolanish muddati *18 tadan 24 kungacha* davom etadi:\n\n"
                "• Gipertoniya kasalligi va uning asoratlari\n"
                "• Arterioskleroz va yurak ishemik kasalliklari\n"
                "• Reyno kasalligi\n"
                "• O'pkaning surunkali kasalliklari"
            ),
            "kz": (
                "🫀 *Жүрек-қан тамыр және тыныс жолдары аурулары:*\n\n"
                "Ауру деңгейіне байланысты емдеу курсы *18-ден 24 күнге дейін* созылады:\n\n"
                "• Гипертония ауруы және оның асқынулары\n"
                "• Атеросклероз және жүрек ишемиялық ауруы\n"
                "• Рейно ауруы\n"
                "• Өкпенің созылмалы аурулары"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_diseases")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "dis_asab":
        text = {
            "ru": (
                "🧠 *Заболевания нервов, позвоночника и суставов:*\n\n"
                "Комплексный курс лечения назначается на *18, 21 или 24 дня* в зависимости от состояния организма:\n\n"
                "• Остеохондроз и грыжи дисков шейного, грудного, пояснично-крестцового отделов\n"
                "• Ревматоидный полиартрит"
            ),
            "uz": (
                "🧠 *Asab, umurtqa va bo'g'im kasalliklari:*\n\n"
                "Kompleks davolash kursi organizm holatiga ko'ra *18, 21 yoki 24 kun* etib belgilanadi:\n\n"
                "• Bo'yin, ko'krak, bel-dumg'aza qismlari osteoxondrozi va disk churralari (grija)\n"
                "• Revmatoidli poliartrit"
            ),
            "kz": (
                "🧠 *Жүйке, омыртқа және буын аурулары:*\n\n"
                "Кешенді емдеу курсы ағза жағдайына қарай *18, 21 немесе 24 күн* белгіленеді:\n\n"
                "• Мойын, кеуде, бел-сегізкөз бөлімдерінің остеохондрозы және диск жарықтары\n"
                "• Ревматоидты полиартрит"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_diseases")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "dis_infeksiya":
        text = {
            "ru": (
                "🩺 *Инфекционные и паразитарные заболевания:*\n\n"
                "Курс выведения паразитов и лечения осложнений: минимум *12–14 дней (профилактика)* или полный курс *18–21 день*:\n\n"
                "• Гельминтозы и глистные инвазии\n"
                "• Осложнения пищевой аллергии\n"
                "• Лечение пациентов с осложнениями после COVID и TORCH-инфекций\n"
                "• Эхинококкоз"
            ),
            "uz": (
                "🩺 *Infeksion va parazitar kasalliklar:*\n\n"
                "Parazitlarni haydash va asoratlarni davolash kursi minimal *12–14 kun (profilaktika)* yoki to'liq *18–21 kun* davom etadi:\n\n"
                "• Gelmintozlar va gijja kasalliklari\n"
                "• Oziq-ovqat allergiyasi asoratlari\n"
                "• COVID va TORCH infeksiyasiga chalingan hamda asoratlangan bemorlarni davolash\n"
                "• Exinokokkoz kasalligi"
            ),
            "kz": (
                "🩺 *Инфекциялық және паразиттік аурулар:*\n\n"
                "Паразиттерді шығару және асқынуларды емдеу курсы: кемінде *12–14 күн (профилактика)* немесе толық *18–21 күн*:\n\n"
                "• Гельминтоздар және құрт аурулары\n"
                "• Тамақ аллергиясының асқынулары\n"
                "• COVID және TORCH инфекцияларынан кейін асқынған науқастарды емдеу\n"
                "• Эхинококкоз"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_diseases")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "dis_immun":
        text = {
            "ru": (
                "🧬 *Иммунные, гормональные и кожные заболевания:*\n\n"
                "Заболевания, требующие системного подхода — курс лечения *21 или 24 дня:*\n\n"
                "• Сахарный диабет и заболевания щитовидной железы\n"
                "• Кожные заболевания (псориаз, экзема, аллергические дерматиты)\n"
                "• Витилиго\n"
                "• Болезнь Верльгофа\n"
                "• Хронический простатит\n"
                "• Заболевания почек и мочевыводящих путей"
            ),
            "uz": (
                "🧬 *Immun, gormonal va teri kasalliklari:*\n\n"
                "Tizimli yondashuv talab etiluvchi kasalliklar bo'lib, davolash kursi *21 yoki 24 kun* etib belgilanadi:\n\n"
                "• Qandli diabet va qalqonsimon bez kasalliklari\n"
                "• Teri kasalliklari (psoriaz, ekzema, allergik dermatitlar)\n"
                "• Vitiligo (pes) kasalligi\n"
                "• Verlgof kasalligi\n"
                "• Surunkali prostatit\n"
                "• Buyrak va siydik yo'llari kasalliklari"
            ),
            "kz": (
                "🧬 *Иммундық, гормоналды және тері аурулары:*\n\n"
                "Жүйелі тәсілді талап ететін аурулар — емдеу курсы *21 немесе 24 күн:*\n\n"
                "• Қант диабеті және қалқанша без аурулары\n"
                "• Тері аурулары (псориаз, экзема, аллергиялық дерматиттер)\n"
                "• Витилиго ауруы\n"
                "• Верльгоф ауруы\n"
                "• Созылмалы простатит\n"
                "• Бүйрек және несеп жолдары аурулары"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_diseases")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "dis_umumiy":
        text = {
            "ru": (
                "✨ *Оздоровление, восстановление иммунитета и профилактика:*\n\n"
                "Рекомендуемые сроки для предотвращения болезней и повышения жизненных сил:\n\n"
                "• 🛡 *Профилактические курсы:* Минимум *12–14 дней*\n"
                "• 🔋 *Повышение и восстановление иммунитета:* Обычно *14–18 дней*\n"
                "• 🧼 *Глубокое очищение внутренней среды организма:* *21–24 дня*\n"
                "• 🎗 *Профилактика онкологических заболеваний:* Под наблюдением врача *21–30 дней*"
            ),
            "uz": (
                "✨ *Sog'lomlashtirish, immun tiklash va profilaktika:*\n\n"
                "Kasallikning oldini olish va organizm quvvatini oshirish uchun tavsiya etiladigan muddatlar:\n\n"
                "• 🛡 *Profilaktika kurslari:* Kamida *12–14 kun*\n"
                "• 🔋 *Imunitetni oshirish va qayta tiklash:* Odatda *14–18 kun*\n"
                "• 🧼 *Inson ichki muhitini chuqur tozalash:* *21–24 kun*\n"
                "• 🎗 *O'sma kasalliklarini oldini olish profilaktikasi:* Shifokor nazoratida *21–30 kun*"
            ),
            "kz": (
                "✨ *Сауықтыру, иммунды қалпына келтіру және профилактика:*\n\n"
                "Аурудың алдын алу және ағзаны нығайту үшін ұсынылатын мерзімдер:\n\n"
                "• 🛡 *Профилактикалық курстар:* Кемінде *12–14 күн*\n"
                "• 🔋 *Иммунитетті арттыру және қалпына келтіру:* Әдетте *14–18 күн*\n"
                "• 🧼 *Ағзаның ішкі ортасын тереңдетіп тазалау:* *21–24 күн*\n"
                "• 🎗 *Онкологиялық аурулардың профилактикасы:* Дәрігер бақылауымен *21–30 күн*"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_diseases")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "disease_not_found":
        text = {
            "ru": (
                "🔍 *Вашего заболевания нет в списке?*\n\n"
                "Чтобы врачи нашего центра дали точный диагноз и рекомендации по срокам лечения, "
                "им необходимо ознакомиться с вашими медицинскими документами.\n\n"
                "📋 *Пожалуйста, нажмите кнопку ниже и пришлите нам:*\n"
                "• Последнее заключение врача (диагноз)\n"
                "• Снимки МРТ, МСКТ или УЗИ\n"
                "• Или результаты последних анализов крови\n"
                "_(В формате фото или PDF)_\n\n"
                "_После отправки документов наши врачи изучат их и свяжутся с вами._"
            ),
            "uz": (
                "🔍 *Sizning kasalligingiz ro'yxatda mavjud emasmi?*\n\n"
                "Markazimiz shifokorlari sizga aniq tashxis va davolash muddati bo'yicha tavsiya berishlari uchun "
                "amaldagi tibbiy hujjatlaringizni ko'rib chiqishlari kerak.\n\n"
                "📋 *Iltimos, pastdagi tugmani bosing va bizga:*\n"
                "• Oxirgi shifokor xulosasi (diagnoz)\n"
                "• MRT, MSKT yoki UZI qog'ozlari rasmi\n"
                "• Yoki oxirgi qon tahlillari natijalarini yuboring\n"
                "_(Rasm yoki PDF formatida)_\n\n"
                "_Hujjatlarni yuborganingizdan so'ng, shifokorlarimiz ularni o'rganib chiqib, siz bilan bog'lanishadi._"
            ),
            "kz": (
                "🔍 *Сіздің ауруыңыз тізімде жоқ па?*\n\n"
                "Орталығымыздың дәрігерлері дәл диагноз қою және емдеу мерзімі бойынша ұсыныс беру үшін "
                "медициналық құжаттарыңызды қарап шығуы керек.\n\n"
                "📋 *Төмендегі түймені басып, бізге жіберіңіз:*\n"
                "• Соңғы дәрігер қорытындысы (диагноз)\n"
                "• МРТ, МСКТ немесе УДЗ суреттері\n"
                "• Немесе соңғы қан анализдерінің нәтижелері\n"
                "_(Сурет немесе PDF форматында)_\n\n"
                "_Құжаттарды жібергеннен кейін дәрігерлеріміз оларды зерделеп, сізбен байланысады._"
            ),
        }[lang]
        send_label = {"ru": "📄 Отправить документы", "uz": "📄 Hujjatlarni yuborish", "kz": "📄 Құжаттарды жіберу"}[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(send_label, callback_data="send_medical_docs")],
            [InlineKeyboardButton(back_label, callback_data="menu_diseases")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "send_medical_docs":
        # FSM state ni boshlash
        context.user_data["med_state"] = {
            "photos": [],
            "voice_id": None,
            "bemor_matni": "",
        }
        text = {
            "ru": (
                "📄 *Отправьте материалы по вашей болезни:*\n\n"
                "📸 Фото документов (МРТ, УЗИ, анализы) — можно несколько\n"
                "🎤 Голосовое сообщение с описанием жалоб\n"
                "✍️ Или напишите текстом\n\n"
                "_Когда всё готово — нажмите кнопку ниже._"
            ),
            "uz": (
                "📄 *Kasalligingiz bo'yicha materiallar yuboring:*\n\n"
                "📸 Hujjatlar rasmi (MRT, UZI, tahlillar) — bir nechtasini yuborishingiz mumkin\n"
                "🎤 Shikoyatlaringizni ovozli xabar orqali ayting\n"
                "✍️ Yoki matn ko'rinishida yozing\n\n"
                "_Hammasi tayyor bo'lgach — quyidagi tugmani bosing._"
            ),
            "kz": (
                "📄 *Ауруыңыз бойынша материалдар жіберіңіз:*\n\n"
                "📸 Құжаттар суреті (МРТ, УДЗ, анализдер) — бірнеше жіберуге болады\n"
                "🎤 Шағымдарыңызды дауыстық хабармен айтыңыз\n"
                "✍️ Немесе мәтін түрінде жазыңыз\n\n"
                "_Бәрі дайын болған соң — төмендегі түймені басыңыз._"
            ),
        }[lang]
        confirm_label = {"ru": "✅ Подтвердить и отправить", "uz": "✅ Tasdiqlash va yuborish", "kz": "✅ Растау және жіберу"}[lang]
        cancel_label = {"ru": "⬅️ Отмена", "uz": "⬅️ Bekor qilish", "kz": "⬅️ Бас тарту"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(confirm_label, callback_data="confirm_medical")],
            [InlineKeyboardButton(cancel_label, callback_data="disease_not_found")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "confirm_medical":
        # Yig'ilgan ma'lumotlarni guruhga yuborish
        med = context.user_data.get("med_state", {})
        photos = med.get("photos", [])
        voice_id = med.get("voice_id")
        bemor_matni = med.get("bemor_matni", "")
        user = query.from_user
        username = f"@{user.username}" if user.username else str(user.id)
        lang_label = {"ru": "Русский", "uz": "O'zbek", "kz": "Қазақ"}.get(lang, lang)

        if not photos and not voice_id and not bemor_matni:
            err = {"ru": "⚠️ Вы ничего не отправили. Пришлите фото, голосовое или текст.", "uz": "⚠️ Hech narsa yubormadingiiz. Rasm, ovoz yoki matn yuboring.", "kz": "⚠️ Ештеңе жібермедіңіз. Сурет, дауыс немесе мәтін жіберіңіз."}[lang]
            await query.answer(err, show_alert=True)
            return

        caption_base = (
            f"⚠️ *Yangi tibbiy murojaat!*\n\n"
            f"👤 {user.full_name}\n"
            f"💬 {username}\n"
            f"🌐 {lang_label}\n"
            f"🆔 `uid:{user.id}`"
        )
        if bemor_matni:
            caption_base += f"\n\n💬 *Shikoyat:*\n_{bemor_matni}_"
        caption_base += f"\n\n_Javob uchun REPLY qiling._"

        try:
            from telegram import InputMediaPhoto
            if photos:
                if len(photos) == 1:
                    await context.bot.send_photo(
                        chat_id=DOCTORS_GROUP_ID, photo=photos[0],
                        caption=caption_base, parse_mode="Markdown"
                    )
                else:
                    media = [InputMediaPhoto(p) for p in photos]
                    media[0] = InputMediaPhoto(photos[0], caption=caption_base, parse_mode="Markdown")
                    await context.bot.send_media_group(chat_id=DOCTORS_GROUP_ID, media=media)

            if voice_id:
                voice_cap = (
                    f"🎤 *Ovozli xabar* | {user.full_name}\n"
                    f"🆔 `uid:{user.id}`\n_Javob uchun REPLY qiling._"
                )
                await context.bot.send_voice(
                    chat_id=DOCTORS_GROUP_ID, voice=voice_id,
                    caption=voice_cap, parse_mode="Markdown"
                )

            if not photos and not voice_id and bemor_matni:
                await context.bot.send_message(
                    chat_id=DOCTORS_GROUP_ID,
                    text=caption_base, parse_mode="Markdown"
                )

            # State ni tozalash
            context.user_data["med_state"] = {}

            ok = {"ru": "✅ Отправлено! Врачи свяжутся с вами.", "uz": "✅ Yuborildi! Shifokorlar siz bilan bog'lanishadi.", "kz": "✅ Жіберілді! Дәрігерлер сізбен байланысады."}[lang]
            await query.edit_message_text(ok, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"confirm_medical error: {e}")
            await query.answer(f"Xato: {e}", show_alert=True)
    elif data == "menu_wards":
        # Xona rasmlarini o'chirish
        old_ids = context.user_data.pop("xona_photo_ids", [])
        for mid in old_ids:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=mid)
            except Exception:
                pass

        korpuslar = d.get("korpuslar", [])
        title = {
            "ru": "🏨 *Корпуса клиники*\n\nВыберите корпус:",
            "uz": "🏨 *Klinika korpuslari*\n\nKorpusni tanlang:",
            "kz": "🏨 *Клиника корпустары*\n\nКорпусты таңдаңыз:",
        }[lang]
        buttons = []
        for k in korpuslar:
            name = k["name_uz"] if lang == "uz" else k["name_ru"]
            buttons.append([InlineKeyboardButton(
                f"{k['emoji']} {name}",
                callback_data=f"korpus_{k['id']}")])
        back = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        buttons.append([InlineKeyboardButton(back, callback_data="back_main")])
        await query.edit_message_text(title, parse_mode="Markdown",
                                      reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("korpus_"):
        # Orqaga kelganda eski xona rasmlarini o'chirish
        old_ids = context.user_data.pop("xona_photo_ids", [])
        for mid in old_ids:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=mid)
            except Exception:
                pass

        korpus_id = data.replace("korpus_", "")
        korpuslar = d.get("korpuslar", [])
        korpus = next((k for k in korpuslar if k["id"] == korpus_id), None)
        if not korpus:
            await query.edit_message_text("❌ Topilmadi", reply_markup=back_keyboard(lang))
            return
        name = korpus["name_uz"] if lang == "uz" else korpus["name_ru"]
        title = {
            "ru": f"{korpus['emoji']} *{name}*\n\nВыберите тип номера:",
            "uz": f"{korpus['emoji']} *{name}*\n\nXona turini tanlang:",
            "kz": f"{korpus['emoji']} *{name}*\n\nБөлме түрін таңдаңыз:",
        }[lang]
        buttons = []
        kishi_w = {"ru": "чел.", "uz": "kishi", "kz": "адам"}[lang]
        for i, xona in enumerate(korpus["xonalar"]):
            buttons.append([InlineKeyboardButton(
                f"🛏 {xona['nom']} ({xona['kishi']} {kishi_w})",
                callback_data=f"xona_{korpus_id}_{i}")])
        back = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        buttons.append([InlineKeyboardButton(back, callback_data="menu_wards")])
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="Markdown",
                                        reply_markup=InlineKeyboardMarkup(buttons))
        # Korpus rasmlari
        if korpus.get("photos"):
            await send_photos(context, chat_id, korpus["photos"])

    elif data.startswith("xona_") and not data.startswith("xona_video_"):
        # Format: xona_{korpus_id}_{idx}
        # rsplit dan foydalanamiz — oxirgi _ dan ajratamiz
        last_underscore = data.rfind("_")
        korpus_id = data[5:last_underscore]  # "xona_" = 5 belgi
        xona_idx = int(data[last_underscore + 1:])
        korpuslar = d.get("korpuslar", [])
        korpus = next((k for k in korpuslar if k["id"] == korpus_id), None)
        if not korpus or xona_idx >= len(korpus["xonalar"]):
            await query.edit_message_text("❌ Topilmadi", reply_markup=back_keyboard(lang))
            return
        xona = korpus["xonalar"][xona_idx]
        korpus_name = korpus["name_uz"] if lang == "uz" else korpus["name_ru"]
        included = d.get("xona_included", {}).get(lang, "")

        # Agar xonaning alohida tavsifi bo'lsa — uni ko'rsat
        desc_key = f"description_{lang}"
        description = xona.get(desc_key) or xona.get("description_uz", "")
        if description:
            # Avval eski rasm xabarlarini o'chirish
            old_ids = context.user_data.pop("xona_photo_ids", [])
            for mid in old_ids:
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=mid)
                except Exception:
                    pass
            # Video xabarlarini ham o'chirish
            old_vid_ids = context.user_data.pop("xona_video_ids", [])
            for mid in old_vid_ids:
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=mid)
                except Exception:
                    pass

            back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
            video_label = {"ru": "🎬 Посмотреть видео", "uz": "🎬 Videoni ko'rish", "kz": "🎬 Бейнені көру"}[lang]

            # Video mavjud bo'lsa tugma qo'shamiz
            xona_videos = xona.get("videos", [])
            if xona_videos:
                back_kb = InlineKeyboardMarkup([
                    [InlineKeyboardButton(video_label, callback_data=f"xona_video_{korpus['id']}_{xona_idx}")],
                    [InlineKeyboardButton(back_label, callback_data=f"korpus_{korpus['id']}")],
                ])
            else:
                back_kb = InlineKeyboardMarkup([[InlineKeyboardButton(
                    back_label, callback_data=f"korpus_{korpus['id']}")]])

            try:
                await query.message.delete()
            except Exception:
                pass

            room_photos = xona.get("photos", [])
            if room_photos:
                msg = await context.bot.send_photo(
                    chat_id=chat_id, photo=room_photos[0],
                    caption=description, parse_mode="Markdown", reply_markup=back_kb
                )
                sent_ids = [msg.message_id]
                for photo_id in room_photos[1:10]:
                    try:
                        m = await context.bot.send_photo(chat_id=chat_id, photo=photo_id)
                        sent_ids.append(m.message_id)
                    except Exception:
                        pass
                context.user_data["xona_photo_ids"] = sent_ids
            else:
                await context.bot.send_message(chat_id=chat_id, text=description,
                                                parse_mode="Markdown", reply_markup=back_kb)
            return

        text = {
            "ru": (
                f"🛏 *{xona['nom']}*\n"
                f"🏢 Корпус: {korpus_name}\n"
                f"👥 Вместимость: {xona['kishi']} человек\n\n"
                f"💰 *Стоимость за 1 день:*\n\n"
                f"🇺🇿 Граждане Узбекистана:\n"
                f"• Взрослые: {xona['uz_adult']} сум\n"
                f"• Дети (5-10 лет): {xona['uz_child']} сум\n\n"
                f"🌍 Иностранные граждане:\n"
                f"• Взрослые: {xona['foreign_adult']} сум\n"
                f"• Дети (5-10 лет): {xona['foreign_child']} сум\n\n"
                f"{included}"
            ),
            "uz": (
                f"🛏 *{xona['nom']}*\n"
                f"🏢 Korpus: {korpus_name}\n"
                f"👥 Sig'imi: {xona['kishi']} kishi\n\n"
                f"💰 *1 kunlik narx:*\n\n"
                f"🇺🇿 O'zbekiston fuqarolari:\n"
                f"• Kattalar: {xona['uz_adult']} so'm\n"
                f"• Bolalar (5-10 yosh): {xona['uz_child']} so'm\n\n"
                f"🌍 Xorijiy fuqarolar:\n"
                f"• Kattalar: {xona['foreign_adult']} so'm\n"
                f"• Bolalar (5-10 yosh): {xona['foreign_child']} so'm\n\n"
                f"{included}"
            ),
            "kz": (
                f"🛏 *{xona['nom']}*\n"
                f"🏢 Корпус: {korpus_name}\n"
                f"👥 Сыйымдылық: {xona['kishi']} адам\n\n"
                f"💰 *1 күндік баға:*\n\n"
                f"🇺🇿 Өзбекстан азаматтары:\n"
                f"• Ересектер: {xona['uz_adult']} сум\n"
                f"• Балалар (5-10 жас): {xona['uz_child']} сум\n\n"
                f"🌍 Шетел азаматтары:\n"
                f"• Ересектер: {xona['foreign_adult']} сум\n"
                f"• Балалар (5-10 жас): {xona['foreign_child']} сум\n\n"
                f"{included}"
            ),
        }[lang]

        book_label = {"ru": "📅 Записаться", "uz": "📅 Yozilish", "kz": "📅 Жазылу"}[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(book_label, callback_data="menu_booking")],
            [InlineKeyboardButton(back_label, callback_data=f"korpus_{korpus_id}")],
        ])

        # ── Yangi mantiq: rasm + matn (caption) + tugma — bitta yaxlit xabar ──
        room_photos = xona.get("photos", [])
        await query.message.delete()
        if room_photos:
            await context.bot.send_photo(
                chat_id=chat_id, photo=room_photos[0],
                caption=text, parse_mode="Markdown", reply_markup=kb
            )
            # Qo'shimcha rasmlar bo'lsa, ularni tugmasiz alohida yuboramiz (caption asosiy rasmda)
            if len(room_photos) > 1:
                await send_photos(context, chat_id, room_photos[1:])
        else:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=kb)
        # ...

    # ── Xonalar ──
    elif data == "menu_rooms":
        title = {
            "ru": "🛏 Выберите категорию:",
            "uz": "🛏 Kategoriyani tanlang:",
            "kz": "🛏 Санатты таңдаңыз:",
        }[lang]
        await query.edit_message_text(title, reply_markup=rooms_keyboard(lang))

    elif data == "rooms_uz":
        title = {
            "ru": "🇺🇿 Граждане Узбекистана\n\nВыберите тип:",
            "uz": "🇺🇿 O'zbekiston fuqarolari\n\nTurini tanlang:",
            "kz": "🇺🇿 Өзбекстан азаматтары\n\nТүрін таңдаңыз:",
        }[lang]
        await query.edit_message_text(title, reply_markup=rooms_type_keyboard(lang, "uz"))

    elif data == "rooms_foreign":
        title = {
            "ru": "🌍 Иностранные граждане\n\nВыберите тип:",
            "uz": "🌍 Xorijiy fuqarolar\n\nTurini tanlang:",
            "kz": "🌍 Шетел азаматтары\n\nТүрін таңдаңыз:",
        }[lang]
        await query.edit_message_text(title, reply_markup=rooms_type_keyboard(lang, "foreign"))

    elif data in ("rooms_uz_adult", "rooms_uz_child", "rooms_foreign_adult", "rooms_foreign_child"):
        parts = data.split("_")
        category = parts[1]  # uz yoki foreign
        age_type = parts[2]  # adult yoki child
        rooms = d["rooms_uz"] if category == "uz" else d["rooms_foreign"]
        flag = "🇺🇿" if category == "uz" else "🌍"

        kishi_word = {"ru": "чел.", "uz": "kishi", "kz": "адам"}[lang]
        narx_word = {"ru": "сум", "uz": "so'm", "kz": "сум"}[lang]

        if age_type == "adult":
            header = {
                "ru": f"{flag} 👨‍👩‍👧 *Стоимость для взрослых*\n_(за 1 день / 1 человек)_\n\n",
                "uz": f"{flag} 👨‍👩‍👧 *Kattalar uchun narx*\n_(1 kun / 1 kishi)_\n\n",
                "kz": f"{flag} 👨‍👩‍👧 *Ересектер үшін баға*\n_(1 күн / 1 адам)_\n\n",
            }[lang]
            lines = [f"🛏 *{r['name']}* ({r['people']} {kishi_word}) — {r['adult']} {narx_word}" for r in rooms]
        else:
            note = {
                "ru": "⚠️ *Внимание:* Дети принимаются с 5 лет.\nДанные цены для детей до 10 лет.\n\n",
                "uz": "⚠️ *Diqqat:* Bolalar 5 yoshdan qabul qilinadi.\nBu narxlar 10 yoshgacha bo'lgan bolalar uchun.\n\n",
                "kz": "⚠️ *Назар аударыңыз:* Балалар 5 жастан қабылданады.\nБұл бағалар 10 жасқа дейінгі балалар үшін.\n\n",
            }[lang]
            header = {
                "ru": f"{flag} 👶 *Стоимость для детей (5–10 лет)*\n_(за 1 день / 1 ребёнок)_\n\n{note}",
                "uz": f"{flag} 👶 *Bolalar uchun narx (5–10 yosh)*\n_(1 kun / 1 bola)_\n\n{note}",
                "kz": f"{flag} 👶 *Балалар үшін баға (5–10 жас)*\n_(1 күн / 1 бала)_\n\n{note}",
            }[lang]
            lines = [f"🛏 *{r['name']}* ({r['people']} {kishi_word}) — {r['child']} {narx_word}" for r in rooms]

        text = header + "\n".join(lines)
        if len(text) > 4000:
            text = text[:4000] + "..."

        back = InlineKeyboardMarkup([[InlineKeyboardButton(
            {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang],
            callback_data=f"rooms_{category}")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back)

    # ══════════════════════════════════════════════════
    # 🧮 NARX HISOBLASH FUNKSIYASI (Calculator)
    # ══════════════════════════════════════════════════

    elif data == "calc_start":
        # 1-qadam: Fuqarolik toifasini tanlash
        text = {
            "ru": "🧮 *Расчёт стоимости лечения*\n\nВыберите гражданство:",
            "uz": "🧮 *Davolanish narxini hisoblash*\n\nFuqarolik toifasini tanlang:",
            "kz": "🧮 *Емдеу құнын есептеу*\n\nАзаматтық санатын таңдаңыз:",
        }[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                {"ru": "🇺🇿 Граждане Узбекистана", "uz": "🇺🇿 O'zbekiston fuqarolari", "kz": "🇺🇿 Өзбекстан азаматтары"}[lang],
                callback_data="calc_cit_uz")],
            [InlineKeyboardButton(
                {"ru": "🌍 Иностранные граждане", "uz": "🌍 Chet el fuqarolari", "kz": "🌍 Шетел азаматтары"}[lang],
                callback_data="calc_cit_foreign")],
            [InlineKeyboardButton(
                {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang],
                callback_data="menu_rooms")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data in ("calc_cit_uz", "calc_cit_foreign"):
        # 2-qadam: Yosh toifasini tanlash
        cit = "uz" if data == "calc_cit_uz" else "foreign"
        context.user_data["calc_cit"] = cit
        text = {
            "ru": "🧮 *Расчёт стоимости*\n\nВыберите возрастную категорию:",
            "uz": "🧮 *Narxni hisoblash*\n\nYosh toifasini tanlang:",
            "kz": "🧮 *Құнын есептеу*\n\nЖас санатын таңдаңыз:",
        }[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                {"ru": "👤 Взрослые", "uz": "👤 Kattalar", "kz": "👤 Ересектер"}[lang],
                callback_data=f"calc_age_{cit}_adult")],
            [InlineKeyboardButton(
                {"ru": "👶 Дети (до 10 лет)", "uz": "👶 Bolalar (10 yoshgacha)", "kz": "👶 Балалар (10 жасқа дейін)"}[lang],
                callback_data=f"calc_age_{cit}_child")],
            [InlineKeyboardButton(
                {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang],
                callback_data="calc_start")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data.startswith("calc_age_"):
        # 3-qadam: Xona/to'lov turini tanlash
        # format: calc_age_{cit}_{age}
        parts = data.split("_")  # ["calc", "age", "uz"/"foreign", "adult"/"child"]
        cit = parts[2]
        age = parts[3]
        context.user_data["calc_cit"] = cit
        context.user_data["calc_age"] = age

        rooms = d["rooms_uz"] if cit == "uz" else d["rooms_foreign"]
        narx_word = {"ru": "сум", "uz": "so'm", "kz": "сум"}[lang]
        kishi_word = {"ru": "чел.", "uz": "kishi", "kz": "адам"}[lang]

        title = {
            "ru": "🧮 *Выберите тип палаты:*\n_(цена за 1 день)_",
            "uz": "🧮 *Xona turini tanlang:*\n_(1 kunlik narx)_",
            "kz": "🧮 *Палата түрін таңдаңыз:*\n_(1 күндік баға)_",
        }[lang]

        # Har bir xona uchun tugma — narxi bilan
        buttons = []
        for i, r in enumerate(rooms):
            price = r["adult"] if age == "adult" else r["child"]
            btn_text = f"🛏 {r['name']} ({r['people']} {kishi_word}) — {price} {narx_word}"
            buttons.append([InlineKeyboardButton(btn_text, callback_data=f"calc_room_{cit}_{age}_{i}")])

        buttons.append([InlineKeyboardButton(
            {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang],
            callback_data=f"calc_cit_{cit}")])

        kb = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(title, parse_mode="Markdown", reply_markup=kb)

    elif data.startswith("calc_room_"):
        # 4-qadam: Kun sonini tanlash + eslatma
        parts = data.split("_")
        cit = parts[2]
        age = parts[3]
        idx = int(parts[4])
        context.user_data["calc_cit"] = cit
        context.user_data["calc_age"] = age
        context.user_data["calc_room_idx"] = idx

        rooms = d["rooms_uz"] if cit == "uz" else d["rooms_foreign"]
        room = rooms[idx]
        price = room["adult"] if age == "adult" else room["child"]
        narx_word = {"ru": "сум", "uz": "so'm", "kz": "сум"}[lang]

        warning = {
            "ru": (
                f"⚠️ *Важно:* Цена рассчитана за 1 день / 1 человека.\n"
                f"Если пациентов 2 и более — каждый оплачивается отдельно.\n"
                f"_Например: {price} {narx_word} × 2 чел × 10 дней = ?_"
            ),
            "uz": (
                f"⚠️ *Muhim:* Ko'rsatilgan narx 1 kun / 1 kishi uchun hisoblangan.\n"
                f"Agar 2 yoki undan ortiq bemor bo'lsa, har biri alohida hisoblanadi.\n"
                f"_Masalan: {price} {narx_word} × 2 kishi × 10 kun = ?_"
            ),
            "kz": (
                f"⚠️ *Маңызды:* Көрсетілген баға 1 күн / 1 адам үшін есептелген.\n"
                f"2 немесе одан көп науқас болса, әр бірі жеке есептеледі.\n"
                f"_Мысалы: {price} {narx_word} × 2 адам × 10 күн = ?_"
            ),
        }[lang]

        text = {
            "ru": f"🧮 *Расчёт стоимости*\n\n🛏 Палата: *{room['name']}* ({room['people']} чел.)\n💰 1 день / 1 чел.: *{price} {narx_word}*\n\n{warning}\n\nВыберите количество дней:",
            "uz": f"🧮 *Narxni hisoblash*\n\n🛏 Xona: *{room['name']}* ({room['people']} kishi)\n💰 1 kun / 1 kishi: *{price} {narx_word}*\n\n{warning}\n\nNecha kun davolanishni rejalashtiryapsiz?",
            "kz": f"🧮 *Құнын есептеу*\n\n🛏 Палата: *{room['name']}* ({room['people']} адам)\n💰 1 күн / 1 адам: *{price} {narx_word}*\n\n{warning}\n\nНеше күн емделуді жоспарлайсыз?",
        }[lang]

        other_label = {"ru": "✏️ Другой срок", "uz": "✏️ Boshqa muddat", "kz": "✏️ Басқа мерзім"}[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("10 kun", callback_data=f"calc_days_{cit}_{age}_{idx}_10"),
             InlineKeyboardButton("12 kun", callback_data=f"calc_days_{cit}_{age}_{idx}_12")],
            [InlineKeyboardButton("14 kun", callback_data=f"calc_days_{cit}_{age}_{idx}_14"),
             InlineKeyboardButton("18 kun", callback_data=f"calc_days_{cit}_{age}_{idx}_18")],
            [InlineKeyboardButton("21 kun", callback_data=f"calc_days_{cit}_{age}_{idx}_21"),
             InlineKeyboardButton("24 kun", callback_data=f"calc_days_{cit}_{age}_{idx}_24")],
            [InlineKeyboardButton(other_label, callback_data=f"calc_other_{cit}_{age}_{idx}")],
            [InlineKeyboardButton(back_label, callback_data=f"calc_age_{cit}_{age}")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data.startswith("calc_other_"):
        # "Boshqa muddat" — foydalanuvchi raqam yozadi
        parts = data.split("_")
        cit = parts[2]
        age = parts[3]
        idx = int(parts[4])
        context.user_data["calc_cit"] = cit
        context.user_data["calc_age"] = age
        context.user_data["calc_room_idx"] = idx
        context.user_data["calc_step"] = "waiting_days"

        text = {
            "ru": "✏️ Введите количество дней (только цифры, минимум 1):",
            "uz": "✏️ Necha kun davolanmoqchisiz? Faqat raqam kiriting (kamida 1):",
            "kz": "✏️ Неше күн емделгіңіз келеді? Тек сан енгізіңіз (кемінде 1):",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(
            back_label, callback_data=f"calc_room_{cit}_{age}_{idx}")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data.startswith("calc_days_"):
        # 5-qadam: Odam sonini so'rash
        parts = data.split("_")
        cit = parts[2]
        age = parts[3]
        idx = int(parts[4])
        days = int(parts[5])

        context.user_data["calc_cit"] = cit
        context.user_data["calc_age"] = age
        context.user_data["calc_room_idx"] = idx
        context.user_data["calc_days"] = days

        rooms = d["rooms_uz"] if cit == "uz" else d["rooms_foreign"]
        room = rooms[idx]
        price = room["adult"] if age == "adult" else room["child"]
        narx_word = {"ru": "сум", "uz": "so'm", "kz": "сум"}[lang]
        day_word = {"ru": "дней", "uz": "kun", "kz": "күн"}[lang]

        text = {
            "ru": f"🧮 *Расчёт стоимости*\n\n🛏 *{room['name']}*\n💰 1 день / 1 чел.: *{price} {narx_word}*\n📅 Дней: *{days}*\n\nСколько человек будет лечиться?",
            "uz": f"🧮 *Narxni hisoblash*\n\n🛏 *{room['name']}*\n💰 1 kun / 1 kishi: *{price} {narx_word}*\n📅 Muddat: *{days} {day_word}*\n\nNecha kishi davolanadi?",
            "kz": f"🧮 *Құнын есептеу*\n\n🛏 *{room['name']}*\n💰 1 күн / 1 адам: *{price} {narx_word}*\n📅 Мерзім: *{days} {day_word}*\n\nНеше адам емделеді?",
        }[lang]

        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("1", callback_data=f"calc_people_{cit}_{age}_{idx}_{days}_1"),
             InlineKeyboardButton("2", callback_data=f"calc_people_{cit}_{age}_{idx}_{days}_2"),
             InlineKeyboardButton("3", callback_data=f"calc_people_{cit}_{age}_{idx}_{days}_3")],
            [InlineKeyboardButton("4", callback_data=f"calc_people_{cit}_{age}_{idx}_{days}_4"),
             InlineKeyboardButton("5", callback_data=f"calc_people_{cit}_{age}_{idx}_{days}_5"),
             InlineKeyboardButton("6", callback_data=f"calc_people_{cit}_{age}_{idx}_{days}_6")],
            [InlineKeyboardButton(back_label, callback_data=f"calc_room_{cit}_{age}_{idx}")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data.startswith("calc_people_"):
        # 6-qadam: Natijani ko'rsatish (odam soni bilan formula)
        # format: calc_people_{cit}_{age}_{idx}_{days}_{people}
        parts = data.split("_")
        cit = parts[2]
        age = parts[3]
        idx = int(parts[4])
        days = int(parts[5])
        people = int(parts[6])

        context.user_data["calc_cit"] = cit
        context.user_data["calc_age"] = age
        context.user_data["calc_room_idx"] = idx
        context.user_data["calc_days"] = days
        context.user_data["calc_people"] = people

        rooms = d["rooms_uz"] if cit == "uz" else d["rooms_foreign"]
        room = rooms[idx]
        price_str = room["adult"] if age == "adult" else room["child"]
        price_num = int(price_str.replace(" ", "").replace("\u00a0", ""))
        total = price_num * days * people

        def fmt(n):
            return f"{n:,}".replace(",", " ")

        narx_word = {"ru": "сум", "uz": "so'm", "kz": "сум"}[lang]
        kishi_word = {"ru": "чел.", "uz": "kishi", "kz": "адам"}[lang]
        day_word = {"ru": "дней", "uz": "kun", "kz": "күн"}[lang]
        day_word1 = {"ru": "день", "uz": "kun", "kz": "күн"}[lang]
        muddat_label = {"ru": "Срок лечения", "uz": "Davolanish muddati", "kz": "Емдеу мерзімі"}[lang]

        cit_label = {
            "ru": {"uz": "Граждане Узбекистана", "foreign": "Иностранные граждане"}[cit],
            "uz": {"uz": "O'zbekiston fuqarolari", "foreign": "Chet el fuqarolari"}[cit],
            "kz": {"uz": "Өзбекстан азаматтары", "foreign": "Шетел азаматтары"}[cit],
        }[lang]
        age_label = {
            "ru": {"adult": "Взрослые", "child": "Дети (до 10 лет)"}[age],
            "uz": {"adult": "Kattalar", "child": "Bolalar (10 yoshgacha)"}[age],
            "kz": {"adult": "Ересектер", "child": "Балалар (10 жасқа дейін)"}[age],
        }[lang]

        # Narx >= 340 000: Fizioterapiya+manual terapiya + MRT kiradi
        # Narx < 340 000: faqat Fizioterapiya (manual terapiya yo'q), MRT yo'q
        if price_num >= 340000:
            included = {
                "ru": "✔ Проживание\n✔ Лечение\n✔ Физиотерапия и мануальная терапия\n✔ УЗИ, анализ крови, ЭКГ\n✔ МРТ 1.5Т или МСКТ — 1 орган",
                "uz": "✔ Turar joy\n✔ Davolanish\n✔ Fizioterapiya va manual terapiya\n✔ UZI, qon tahlili, EKG\n✔ MRT 1.5T yoki MSKT — 1 organ",
                "kz": "✔ Тұрғын үй\n✔ Емдеу\n✔ Физиотерапия және мануалды терапия\n✔ УДЗ, қан анализі, ЭКГ\n✔ МРТ 1.5Т немесе МСКТ — 1 орган",
            }[lang]
        else:
            included = {
                "ru": "✔ Проживание\n✔ Лечение\n✔ Физиотерапия\n✔ УЗИ, анализ крови, ЭКГ",
                "uz": "✔ Turar joy\n✔ Davolanish\n✔ Fizioterapiya\n✔ UZI, qon tahlili, EKG",
                "kz": "✔ Тұрғын үй\n✔ Емдеу\n✔ Физиотерапия\n✔ УДЗ, қан анализі, ЭКГ",
            }[lang]
        extra = {
            "ru": "МРТ 3Т, МСКТ 256, Маммография, Криолиполиз, Растяжка, Ударно-волновая терапия",
            "uz": "MRT 3T, MSKT 256, Mammografiya, Kriolipoliz, Cho'zilish, Zarba-to'lqin terapiyasi",
            "kz": "МРТ 3Т, МСКТ 256, Маммография, Криолиполиз, Созылу, Соққы-толқын терапиясы",
        }[lang]
        note = {
            "ru": "📌 *Примечание:* Точный срок лечения определяется врачом после осмотра.",
            "uz": "📌 *Eslatma:* Aniq davolanish muddati shifokor ko'rigidan keyin belgilanadi.",
            "kz": "📌 *Ескерту:* Нақты емдеу мерзімі дәрігер тексерісінен кейін белгіленеді.",
        }[lang]

        formula_label = {
            "ru": f"📌 *Расчёт:* {fmt(price_num)} × {days} дн × {people} чел = *{fmt(total)} {narx_word}*",
            "uz": f"📌 *Hisoblash:* {fmt(price_num)} × {days} kun × {people} kishi = *{fmt(total)} {narx_word}*",
            "kz": f"📌 *Есептеу:* {fmt(price_num)} × {days} күн × {people} адам = *{fmt(total)} {narx_word}*",
        }[lang]
        narx_turi = {
            "ru": "⚠️ Тип цены: за 1 день / 1 человека",
            "uz": "⚠️ Narx turi: 1 kun / 1 kishi uchun",
            "kz": "⚠️ Баға түрі: 1 күн / 1 адам үшін",
        }[lang]
        result_title = {
            "ru": "✅ *Результат расчёта*",
            "uz": "✅ *Hisoblash natijasi*",
            "kz": "✅ *Есептеу нәтижесі*",
        }[lang]

        incl_title = {"ru": "В стоимость входит", "uz": "Narx tarkibiga kiradi", "kz": "Құнға кіреді"}[lang]
        extra_title = {"ru": "Дополнительно", "uz": "Qo'shimcha xizmatlar alohida", "kz": "Қосымша жеке"}[lang]

        text = (
            f"{result_title}\n\n"
            f"🏨 *{room['name']}* ({room['people']} {kishi_word})\n"
            f"{narx_turi}\n"
            f"👤 {cit_label} | {age_label}\n"
            f"💰 1 {day_word1}: *{fmt(price_num)} {narx_word}*\n"
            f"📅 {muddat_label}: *{days} {day_word}*\n"
            f"👥 Odam soni: *{people} {kishi_word}*\n\n"
            f"✅ *Jami to'lov: {fmt(total)} {narx_word}*\n\n"
            f"{formula_label}\n\n"
            f"📦 *{incl_title}:*\n{included}\n\n"
            f"➕ *{extra_title}:*\n_{extra}_\n\n"
            f"{note}"
        )

        calc_book_label = {"ru": "🏨 Записаться на эту палату", "uz": "🏨 Shu xona bo'yicha qabulga yozilish", "kz": "🏨 Осы палатаға жазылу"}[lang]
        operator_label = {"ru": "💬 Связаться с оператором", "uz": "💬 Operator bilan bog'lanish", "kz": "💬 Операторға хабарласу"}[lang]
        recalc_label = {"ru": "🔁 Пересчитать", "uz": "🔁 Qayta hisoblash", "kz": "🔁 Қайта есептеу"}[lang]
        back_label = {"ru": "🔙 Назад", "uz": "🔙 Orqaga", "kz": "🔙 Артқа"}[lang]

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(calc_book_label, callback_data="calc_book_statsionar")],
            [InlineKeyboardButton(operator_label, callback_data="menu_operator")],
            [InlineKeyboardButton(recalc_label, callback_data="calc_start")],
            [InlineKeyboardButton(back_label, callback_data=f"calc_days_{cit}_{age}_{idx}_{days}")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data.startswith("xona_video_"):
        # format: xona_video_{korpus_id}_{xona_idx}
        parts = data[len("xona_video_"):]
        last = parts.rfind("_")
        korpus_id = parts[:last]
        xona_idx = int(parts[last+1:])
        logger.info(f"xona_video: korpus_id={korpus_id}, xona_idx={xona_idx}")

        # Eski video xabarlarini o'chirish
        old_vid_ids = context.user_data.pop("xona_video_ids", [])
        for mid in old_vid_ids:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=mid)
            except Exception:
                pass

        for k in d.get("korpuslar", []):
            if k["id"] == korpus_id:
                xona = k["xonalar"][xona_idx]
                videos = xona.get("videos", [])
                logger.info(f"xona videos: {videos}")
                back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
                # Asosiy xabarni orqaga tugmasi bilan yangilash
                await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(back_label, callback_data=f"xona_{korpus_id}_{xona_idx}")]
                ]))
                # Videolarni yuborish
                sent_ids = []
                for vid_id in videos[:3]:
                    try:
                        msg = await context.bot.send_video(chat_id=chat_id, video=vid_id)
                        sent_ids.append(msg.message_id)
                    except Exception:
                        pass
                context.user_data["xona_video_ids"] = sent_ids
                return
        await query.answer("❌ Xona topilmadi")
        return

    elif data == "doctor_question":
        intro = {
            "ru": (
                "👨‍⚕️ <b>Вопрос врачу — Правила подачи</b>\n\n"
                "Чтобы врач смог дать точный ответ, пожалуйста:\n\n"
                "1️⃣ Укажите <b>возраст и пол</b>\n"
                "2️⃣ Опишите <b>жалобы и симптомы</b> подробно\n"
                "3️⃣ Прикрепите <b>анализы, МРТ, УЗИ</b> (если есть)\n\n"
                "⚠️ Одно сообщение не принимается напрямую — после отправки текста вы сможете добавить снимки или сразу отправить врачу.\n\n"
                "✍️ Напишите ваш вопрос:"
            ),
            "uz": (
                "👨‍⚕️ <b>Shifokorga savol — Yuborish qoidalari</b>\n\n"
                "Shifokor aniq javob bera olishi uchun, iltimos:\n\n"
                "1️⃣ <b>Yosh va jinsingizni</b> yozing\n"
                "2️⃣ <b>Shikoyat va belgilarni</b> batafsil yozing\n"
                "3️⃣ <b>Tahlillar, MRT, UZI</b> rasmlarini qo'shing (agar bo'lsa)\n\n"
                "⚠️ Bitta xabar to'g'ridan-to'g'ri qabul qilinmaydi — matn yuborgandan so'ng rasm qo'shishingiz yoki shifokorga yuborishingiz mumkin.\n\n"
                "✍️ Savolingizni yozing:"
            ),
            "kz": (
                "👨‍⚕️ <b>Дәрігерге сұрақ — Жіберу ережелері</b>\n\n"
                "Дәрігер нақты жауап бере алуы үшін:\n\n"
                "1️⃣ <b>Жасыңызды және жынысыңызды</b> жазыңыз\n"
                "2️⃣ <b>Шағымдар мен белгілерді</b> толық жазыңыз\n"
                "3️⃣ <b>Талдаулар, МРТ, УЗИ</b> суреттерін қосыңыз (болса)\n\n"
                "⚠️ Бір хабарлама тікелей қабылданбайды — мәтін жібергеннен кейін сурет қосуға немесе дәрігерге жіберуге болады.\n\n"
                "✍️ Сұрағыңызды жазыңыз:"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_main")]])
        context.user_data["state"] = "DOCTOR_QUESTION_WAITING"
        context.user_data["temp_text"] = None
        context.user_data["temp_photos"] = []
        try:
            await query.edit_message_text(intro, parse_mode="HTML", reply_markup=kb)
        except Exception:
            await query.message.delete()
            await context.bot.send_message(chat_id=chat_id, text=intro,
                                           parse_mode="HTML", reply_markup=kb)

    elif data == "send_to_doctor_now":
        temp_text  = context.user_data.get("temp_text", "")
        temp_photos = context.user_data.get("temp_photos", [])
        user = query.from_user
        username = f"@{user.username}" if user.username else "—"

        header = (
            f"👨‍⚕️ <b>Yangi savol (Shifokorga savol bo'limi)</b>\n\n"
            f"👤 Bemor: {user.full_name}  uid:{user.id}\n"
            f"💬 Telegram: {username}\n"
            f"🌐 Til: {lang.upper()}\n\n"
            f"📝 Savol:\n{temp_text}"
        )
        try:
            if temp_photos:
                # Rasm + matn birgalikda
                from telegram import InputMediaPhoto
                media = [InputMediaPhoto(temp_photos[0], caption=header, parse_mode="HTML")]
                for ph in temp_photos[1:]:
                    media.append(InputMediaPhoto(ph))
                await context.bot.send_media_group(chat_id=DOCTORS_GROUP_ID, media=media)
            else:
                await context.bot.send_message(chat_id=DOCTORS_GROUP_ID,
                                               text=header, parse_mode="HTML")

            context.user_data["state"] = None
            context.user_data["temp_text"] = None
            context.user_data["temp_photos"] = []
            confirm = {
                "ru": "✅ Ваш вопрос отправлен врачу! Ожидайте ответа.",
                "uz": "✅ Savolingiz shifokorga yetkazildi! Javobni kuting.",
                "kz": "✅ Сұрағыңыз дәрігерге жіберілді! Жауапты күтіңіз.",
            }[lang]
            await query.edit_message_text(confirm, reply_markup=main_menu_keyboard(lang, update.effective_user.id if update.effective_user else 0))

            # ── AI orqali umumiy yo'naltiruvchi javob (shifokor javobini almashtirmaydi) ──
            if temp_text:
                verdict, reason = await ai_check_diagnosis(temp_text)
                if verdict in ("MOS_KELADI", "MOS_KELMAYDI") and reason:
                    icon = "✅" if verdict == "MOS_KELADI" else "⚠️"
                    ai_msg = f"{icon} {reason}" + DOCTOR_FOLLOWUP_NOTE[lang]
                    await context.bot.send_message(chat_id=chat_id, text=ai_msg)
        except Exception as e:
            logger.error(f"send_to_doctor_now error: {e}")
            await query.answer("❌ Xatolik yuz berdi", show_alert=True)

    elif data == "add_medical_photo":
        prompt = {
            "ru": "📸 Отправьте фото анализов или снимков (можно несколько). Когда закончите — нажмите «Готово».",
            "uz": "📸 Tahlil yoki MRT/UZI rasmlarini yuboring (bir nechtasini ham). Tugagach «Tayyor» tugmasini bosing.",
            "kz": "📸 Талдау немесе МРТ/УЗИ суреттерін жіберіңіз (бірнешеуін де). Аяқтағанда «Дайын» түймесін басыңыз.",
        }[lang]
        done_label   = {"ru": "✅ Готово — отправить врачу", "uz": "✅ Tayyor — shifokorga yuborish", "kz": "✅ Дайын — дәрігерге жіберу"}[lang]
        cancel_label = {"ru": "❌ Отмена", "uz": "❌ Bekor qilish", "kz": "❌ Болдырмау"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(done_label,   callback_data="send_to_doctor_now")],
            [InlineKeyboardButton(cancel_label, callback_data="cancel_doctor_question")],
        ])
        context.user_data["state"] = "DOCTOR_MEDIA_WAITING"
        await query.edit_message_text(prompt, reply_markup=kb)

    elif data == "cancel_doctor_question":
        context.user_data["state"] = None
        context.user_data["temp_text"] = None
        context.user_data["temp_photos"] = []
        cancel_text = {
            "ru": "❌ Отменено.",
            "uz": "❌ Bekor qilindi.",
            "kz": "❌ Болдырылмады.",
        }[lang]
        try:
            await query.edit_message_text(cancel_text, reply_markup=main_menu_keyboard(lang, update.effective_user.id if update.effective_user else 0))
        except Exception:
            await context.bot.send_message(chat_id=chat_id, text=cancel_text,
                                           reply_markup=main_menu_keyboard(lang, update.effective_user.id if update.effective_user else 0))
        title = {
            "ru": "🧲 Выберите вид диагностики:",
            "uz": "🧲 Diagnostika turini tanlang:",
            "kz": "🧲 Диагностика түрін таңдаңыз:",
        }[lang]
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(chat_id=chat_id, text=title, reply_markup=diagnostics_keyboard(lang))

    elif data == "diag_mrt15":
        logger.info(f"diag_mrt15 handler ishga tushdi, lang={lang}")
        lines = "\n".join([f"• {x}" for x in d["mrt_15"]])
        title = {"ru": "🧲 <b>МРТ 1.5Т — цены:</b>", "uz": "🧲 <b>МРТ 1.5Т — narxlar:</b>", "kz": "🧲 <b>МРТ 1.5Т — бағалар:</b>"}[lang]
        call_label = {"ru": "📞 МРТ 1.5Т — позвонить", "uz": "📞 МРТ 1.5Т — telefon qilish", "kz": "📞 МРТ 1.5Т — қоңырау шалу"}[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(call_label, callback_data="call_mrt15")],
            [InlineKeyboardButton(back_label, callback_data="menu_diagnostics")],
        ])
        text = f"{title}\n\n{lines}"
        photo = d.get("diag_mrt15_photo", "")
        await query.message.delete()
        if photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

    elif data == "diag_mrt3t":
        title = {"ru": "🧲 МРТ 3Т — выберите группу:", "uz": "🧲 МРТ 3Т — guruhni tanlang:", "kz": "🧲 МРТ 3Т — топты таңдаңыз:"}[lang]
        call_label = {"ru": "📞 МРТ 3Т — позвонить", "uz": "📞 МРТ 3Т — telefon qilish", "kz": "📞 МРТ 3Т — қоңырау шалу"}[lang]
        groups_kb = list(mrt3t_groups_keyboard(lang).inline_keyboard)
        kb = InlineKeyboardMarkup(
            groups_kb + [[InlineKeyboardButton(call_label, callback_data="call_mrt3t")]]
        )
        photo = d.get("diag_mrt3t_photo", "")
        await query.message.delete()
        if photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=title, reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=chat_id, text=title, reply_markup=kb)

    elif data.startswith("mrt3t_"):
        idx = int(data[6:])
        groups = d["mrt_3t_groups"]
        group_name = list(groups.keys())[idx]
        items = groups[group_name]
        lines = "\n".join([f"• {x}" for x in items])
        call_label = {"ru": "📞 МРТ 3Т — позвонить", "uz": "📞 МРТ 3Т — telefon qilish", "kz": "📞 МРТ 3Т — қоңырау шалу"}[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(call_label, callback_data="call_mrt3t")],
            [InlineKeyboardButton(back_label, callback_data="diag_mrt3t")],
        ])
        photo_key = f"diag_mrt3t_{idx}_photo"
        photo = d.get(photo_key, "")
        text = f"🧲 <b>МРТ 3Т — {group_name}:</b>\n\n{lines}"
        await query.message.delete()
        if photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

    elif data == "diag_mskt256":
        lines = "\n".join([f"• {x}" for x in d["mskt_256"]])
        title = {"ru": "🖥 <b>МСКТ 256 — цены:</b>", "uz": "🖥 <b>МСКТ 256 — narxlar:</b>", "kz": "🖥 <b>МСКТ 256 — бағалар:</b>"}[lang]
        call_label = {"ru": "📞 МСКТ 256 — позвонить", "uz": "📞 МСКТ 256 — telefon qilish", "kz": "📞 МСКТ 256 — қоңырау шалу"}[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(call_label, callback_data="call_mskt256")],
            [InlineKeyboardButton(back_label, callback_data="menu_diagnostics")],
        ])
        text = f"{title}\n\n{lines}"
        photo = d.get("diag_mskt256_photo", "")
        await query.message.delete()
        if photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

    elif data == "diag_mskt128":
        lines = "\n".join([f"• {x}" for x in d["mskt_128"]])
        title = {"ru": "🖥 <b>МСКТ 128 — цены:</b>", "uz": "🖥 <b>МСКТ 128 — narxlar:</b>", "kz": "🖥 <b>МСКТ 128 — бағалар:</b>"}[lang]
        call_label = {"ru": "📞 МСКТ 128 — позвонить", "uz": "📞 МСКТ 128 — telefon qilish", "kz": "📞 МСКТ 128 — қоңырау шалу"}[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(call_label, callback_data="call_mskt128")],
            [InlineKeyboardButton(back_label, callback_data="menu_diagnostics")],
        ])
        text = f"{title}\n\n{lines}"
        photo = d.get("diag_mskt128_photo", "")
        await query.message.delete()
        if photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

    elif data == "call_mrt15":
        text = "📞 <b>МРТ 1.5Т</b>\n\n☎️ +998664556015"
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="diag_mrt15")]])
        await query.message.delete()
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

    elif data == "call_mrt3t":
        text = "📞 <b>МРТ 3Т</b>\n\n☎️ +998557010756"
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="diag_mrt3t")]])
        await query.message.delete()
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

    elif data == "call_mskt" or data == "call_mskt256":
        text = "📞 <b>МСКТ 256</b>\n\n☎️ +998664556007"
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="diag_mskt256")]])
        await query.message.delete()
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

    elif data == "call_mskt128":
        text = "📞 <b>МСКТ 128</b>\n\n☎️ +998664556007"
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="diag_mskt128")]])
        await query.message.delete()
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

    elif data == "diag_other":
        lines = "\n".join([f"• {x}" for x in d["other_diagnostics"]])
        title = {"ru": "📡 <b>УЗИ — цены:</b>", "uz": "📡 <b>УЗИ — narxlar:</b>", "kz": "📡 <b>УДЗ — бағалар:</b>"}[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_diagnostics")]])
        photo = d.get("diag_other_photo", "")
        text = f"{title}\n\n{lines}"
        await query.message.delete()
        if photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

    elif data == "diag_mammografiya":
        text = {
            "ru": (
                "🩺 <b>Маммография</b>\n\n"
                "💰 <b>Цена:</b> 250 000 сум\n\n"
                "Рентгенологическое исследование молочных желёз для ранней диагностики."
            ),
            "uz": (
                "🩺 <b>Mammografiya</b>\n\n"
                "💰 <b>Narx:</b> 250 000 so'm\n\n"
                "Ko'krak bezlarini erta aniqlash uchun rentgenologik tekshiruv."
            ),
            "kz": (
                "🩺 <b>Маммография</b>\n\n"
                "💰 <b>Баға:</b> 250 000 сум\n\n"
                "Сүт бездерін ерте анықтауға арналған рентгенологиялық зерттеу."
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_diagnostics")]])
        photo = d.get("diag_mammografiya_photo", "")
        await query.message.delete()
        if photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

    elif data == "diag_fibroskan":
        text = {
            "ru": (
                "🫀 <b>Фибросканирование печени</b>\n\n"
                "💰 <b>Цена:</b> 220 000 сум\n\n"
                "Безболезненное исследование состояния печени без биопсии.\n\n"
                "⏱ Длительность: 15–20 минут\n"
                "📋 Подготовка: натощак (4–6 часов)"
            ),
            "uz": (
                "🫀 <b>Jigar fibroskan tekshiruvi</b>\n\n"
                "💰 <b>Narx:</b> 220 000 so'm\n\n"
                "Biopsiysiz jigar holatini og'riqsiz tekshirish.\n\n"
                "⏱ Davomiyligi: 15–20 daqiqa\n"
                "📋 Tayyorgarlik: och qorin (4–6 soat)"
            ),
            "kz": (
                "🫀 <b>Бауырды фибросканерлеу</b>\n\n"
                "💰 <b>Баға:</b> 220 000 сум\n\n"
                "Биопсиясыз бауыр жағдайын ауырусыз тексеру.\n\n"
                "⏱ Ұзақтығы: 15–20 минут\n"
                "📋 Дайындық: аш қарын (4–6 сағат)"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_diagnostics")]])
        photo = d.get("diag_fibroskan_photo", "")
        await query.message.delete()
        if photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

    elif data == "diag_lab":
        lines = "\n".join([f"• {x}" for x in d["lab"]])
        title = {"ru": "🔬 <b>Лаборатория — цены:</b>", "uz": "🔬 <b>Laboratoriya — narxlar:</b>", "kz": "🔬 <b>Зертхана — бағалар:</b>"}[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_diagnostics")]])
        photo = d.get("diag_lab_photo", "")
        text = f"{title}\n\n{lines}"
        await query.message.delete()
        if photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)

    # ── Klinikaga yetib olish ──
    elif data == "menu_transfer":
        title = {
            "ru": (
                "🚗 *Как добраться до клиники*\n\n"
                "📍 *Адрес:*\nг. Каттакурган, массив Казак овул\n\n"
                "Наши надёжные водители встретят вас *во всех регионах Узбекистана* и комфортно доставят в клинику.\n\n"
                "⚠️ *ВАЖНО:*\nЗаказ трансфера необходимо оформить *за 2–3 дня до приезда*.\n\n"
                "Выберите действие:"
            ),
            "uz": (
                "🚗 *Klinikaga yetib olish*\n\n"
                "📍 *Manzil:*\nKattaqo'rg'on shahri, Qozoq ovul massivi\n\n"
                "Bizning ishonchli haydovchilarimiz *O'zbekistonning barcha hududlarida* sizni kutib olib klinikaga olib keladi.\n\n"
                "⚠️ *MUHIM:*\nTransferni *kelishdan 2–3 kun oldin* buyurtma qilish kerak.\n\n"
                "Kerakli bo'limni tanlang:"
            ),
            "kz": (
                "🚗 *Клиникаға жету*\n\n"
                "📍 *Мекенжай:*\nКаттақурғон қаласы, Қазақ овул массиві\n\n"
                "Біздің сенімді жүргізушілеріміз *Өзбекстанның барлық аймақтарында* сізді қарсы алып клиникаға жеткізеді.\n\n"
                "⚠️ *МАҢЫЗДЫ:*\nТрансферді *келуден 2–3 күн бұрын* тапсырыс беру керек.\n\n"
                "Бөлімді таңдаңыз:"
            ),
        }[lang]
        book_label = {"ru": "📞 Заказать трансфер", "uz": "📞 Transfer buyurtma qilish", "kz": "📞 Трансфер тапсырыс"}[lang]
        price_label = {"ru": "💰 Стоимость трансфера", "uz": "💰 Transfer narxlari", "kz": "💰 Трансфер бағасы"}[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(book_label, callback_data="transfer_book")],
            [InlineKeyboardButton(price_label, callback_data="transfer_price")],
            [InlineKeyboardButton(back_label, callback_data="back_main")],
        ])
        await query.edit_message_text(title, parse_mode="Markdown", reply_markup=kb)

    elif data == "transfer_price":
        d = load_data()
        text = d["transfer"][lang].format(phone=d["contacts"]["phone1"])
        back = InlineKeyboardMarkup([[InlineKeyboardButton(
            {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang],
            callback_data="menu_transfer")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back)

    elif data == "transfer_book":
        context.user_data["booking"] = {}
        context.user_data["booking_type"] = "transfer"
        context.user_data["booking_step"] = "transfer_from"
        ask = {
            "ru": "🚗 *Заказ трансфера*\n\n📍 Шаг 1/4\nНапишите *откуда вас встретить:*\n_(город, вокзал или аэропорт)_",
            "uz": "🚗 *Transfer buyurtmasi*\n\n📍 1/4 qadam\n*Qayerdan kutib olinsin:*\n_(shahar, vokzal yoki aeroport)_",
            "kz": "🚗 *Трансфер тапсырысы*\n\n📍 1/4 қадам\n*Қайдан қарсы алынсын:*\n_(қала, вокзал немесе әуежай)_",
        }[lang]
        await query.edit_message_text(ask, parse_mode="Markdown")

    # ── Ekskursiya ──
    elif data == "menu_excursion":
        title = {
            "ru": "🕌 Выберите направление:",
            "uz": "🕌 Yo'nalishni tanlang:",
            "kz": "🕌 Бағытты таңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏛 Samarqand", callback_data="excursion_samarkand")],
            [InlineKeyboardButton("🕌 Buxoro", callback_data="excursion_bukhara")],
            [InlineKeyboardButton(back_label, callback_data="menu_weekend")],
        ])
        await query.edit_message_text(title, reply_markup=kb)

    elif data in ("excursion_samarkand", "excursion_bukhara"):
        city = "samarkand" if data == "excursion_samarkand" else "bukhara"
        city_name = {"samarkand": {"ru": "Самарканд", "uz": "Samarqand", "kz": "Самарқанд"},
                     "bukhara": {"ru": "Бухара", "uz": "Buxoro", "kz": "Бұхара"}}[city][lang]
        price_1 = "150 000" if city == "samarkand" else "200 000"
        price_salon = "500 000" if city == "samarkand" else "800 000"
        places = {
            "samarkand": {"ru": "Регистан, Шахи-Зинда, Гур-Эмир, Биби-Ханум, обсерватория Улугбека",
                          "uz": "Registon, Shahi-Zinda, Gur-Amir, Bibixonim, Ulug'bek rasadxonasi",
                          "kz": "Регистан, Шахи-Зинда, Гур-Эмир, Биби-Ханум"},
            "bukhara": {"ru": "Арк, Боло-Хауз, Пои-Калон, Мавзолей Саманидов, Чор-Минор",
                        "uz": "Ark, Bolo-Xovuz, Poi-Kalon, Somoniylar maqbarasi, Chor-Minor",
                        "kz": "Арк, Боло-Хауз, Пои-Калон, Саманидтер кесенесі"},
        }[city][lang]
        text = {
            "ru": f"🏛 *{city_name}*\n\n💰 1 человек — {price_1} сум\n👥 Салон (группа) — {price_salon} сум\n\n🗺 *Маршрут:*\n{places}\n\n📅 Только по воскресеньям",
            "uz": f"🏛 *{city_name}*\n\n💰 1 kishi — {price_1} so'm\n👥 Salon (guruh) — {price_salon} so'm\n\n🗺 *Marshrut:*\n{places}\n\n📅 Faqat yakshanbа kunlari",
            "kz": f"🏛 *{city_name}*\n\n💰 1 адам — {price_1} сум\n👥 Салон (топ) — {price_salon} сум\n\n🗺 *Маршрут:*\n{places}\n\n📅 Тек жексенбі күндері",
        }[lang]
        book_label = {"ru": "📝 Записаться", "uz": "📝 Yozilish", "kz": "📝 Жазылу"}[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(book_label, callback_data=f"excursion_book_{city}")],
            [InlineKeyboardButton(back_label, callback_data="menu_excursion")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        photos_key = "samarkand_photos" if city == "samarkand" else "bukhara_photos"
        if d.get(photos_key):
            await send_photos(context, chat_id, d[photos_key])

    elif data.startswith("excursion_book_"):
        city = data.replace("excursion_book_", "")
        city_name = {"samarkand": {"ru": "Самарканд", "uz": "Samarqand", "kz": "Самарқанд"},
                     "bukhara": {"ru": "Бухара", "uz": "Buxoro", "kz": "Бұхара"}}[city][lang]
        context.user_data["booking"] = {"city": city_name}
        context.user_data["booking_type"] = "excursion"
        context.user_data["booking_step"] = "excursion_sana"
        ask = {
            "ru": f"🕌 *Экскурсия в {city_name}*\n\n📅 Шаг 1/3\nНапишите *желаемую дату:*\n_(только по воскресеньям)_",
            "uz": f"🕌 *{city_name} ekskursiyasi*\n\n📅 1/3 qadam\n*Qaysi sana* bo'lishini yozing:\n_(faqat yakshanba kunlari)_",
            "kz": f"🕌 *{city_name} экскурсиясы*\n\n📅 1/3 қадам\n*Қандай күнге* деп жазыңыз:\n_(тек жексенбі күндері)_",
        }[lang]
        await query.edit_message_text(ask, parse_mode="Markdown")

    # ── Yakshanba ──
    elif data == "menu_weekend":
        text = {
            "ru": (
                "🌅 *Воскресенье в клинике Эргаш-Ота*\n\n"
                "Воскресенье — день отдыха, но мы всегда рады новым пациентам!\n\n"
                "✅ *В воскресенье:*\n"
                "• Работает регистратура\n"
                "• Принимаем новых пациентов\n"
                "• Осмотр дежурным врачом\n"
                "• Начало лечения в первый же день"
            ),
            "uz": (
                "🌅 *Yakshanba — Ergash-Ota klinikasida*\n\n"
                "Yakshanba dam olish kuni, lekin biz yangi bemorlarni doimo kutib olamiz!\n\n"
                "✅ *Yakshanba kuni:*\n"
                "• Registratsiya bo'limi ishlaydi\n"
                "• Yangi bemorlar qabul qilinadi\n"
                "• Navbatchi vrach ko'rigidan o'tiladi\n"
                "• Birinchi kuni davolash boshlanadi"
            ),
            "kz": (
                "🌅 *Жексенбі — Эргаш-Ота клиникасында*\n\n"
                "✅ *Жексенбіде:*\n"
                "• Тіркеу бөлімі жұмыс істейді\n"
                "• Жаңа науқастар қабылданады\n"
                "• Кезекші дәрігер қарайды\n"
                "• Бірінші күні емдеу басталады"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        # EKSKURSIYA TUGMASI VAQTINCHA O'CHIRILGAN
        # Yoqish uchun quyidagi 2 qatordan # ni olib tashlang va kb ni almashtiring:
        # excursion_label = {"ru": "🕌 Записаться на экскурсию", "uz": "🕌 Ekskursiyaga yozilish", "kz": "🕌 Экскурсияға жазылу"}[lang]
        # kb_on = InlineKeyboardMarkup([[InlineKeyboardButton(excursion_label, callback_data="menu_excursion")], [InlineKeyboardButton(back_label, callback_data="back_main")]])
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(back_label, callback_data="back_main")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    # ── Operator ──
    elif data == "get_results":
        await get_results_start(update, context)

    elif data == "staff_pdf_upload":
        await staff_pdf_start(update, context)

    elif data in ("menu_operator", "connect_operator"):
        c = d["contacts"]
        text = {
            "ru": f"📞 *Свяжитесь с нами:*\n\n☎️ {c['phone1']}\n☎️ {c['phone2']}\n\n📸 Instagram: {c['instagram']}\n🌐 {c['website']}\n\nМы ответим в рабочее время!",
            "uz": f"📞 *Biz bilan bog'laning:*\n\n☎️ {c['phone1']}\n☎️ {c['phone2']}\n\n📸 Instagram: {c['instagram']}\n🌐 {c['website']}\n\nIsh vaqtida javob beramiz!",
            "kz": f"📞 *Бізбен байланысыңыз:*\n\n☎️ {c['phone1']}\n☎️ {c['phone2']}\n\n📸 Instagram: {c['instagram']}\n🌐 {c['website']}\n\nЖұмыс уақытында жауап береміз!",
        }[lang]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard(lang))


# ─── ADMIN PANEL ──────────────────────────────────────────────────────────────

# ── BEMOR NATIJALARI OLISH FSM ───────────────────────────────────────────────

async def get_results_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """QR deep-link yoki callback orqali natija olish bo'limini ochadi"""
    lang = get_lang(context)
    context.user_data["results_step"] = "phone"
    text = {
        "uz": "📥 *Natijangizni olish*\n\nTelefon raqamingizni kiriting:\n_(+998901234567 formatida)_",
        "ru": "📥 *Получить результат*\n\nВведите ваш номер телефона:\n_(в формате +998901234567)_",
        "kz": "📥 *Нәтижені алу*\n\nТелефон нөміріңізді енгізіңіз:\n_(+998901234567 форматында)_",
    }[lang]
    back_label = {"uz": "⬅️ Orqaga", "ru": "⬅️ Назад", "kz": "⬅️ Артқа"}[lang]
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_main")]])
    if hasattr(update, "callback_query") and update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def patient_results_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bemor natija olish FSM — telefon → tug'ilgan sana → PDF yuborish"""
    step = context.user_data.get("results_step")
    if not step:
        return
    lang = get_lang(context)
    text = update.message.text.strip() if update.message.text else ""

    if step == "phone":
        context.user_data["results_phone"] = text
        context.user_data["results_step"] = "dob"
        msg = {
            "uz": "📅 Tug'ilgan kuningizni kiriting:\n_(DD.MM.YYYY formatida, masalan: 15.03.1985)_",
            "ru": "📅 Введите дату вашего рождения:\n_(в формате DD.MM.YYYY, например: 15.03.1985)_",
            "kz": "📅 Туған күніңізді енгізіңіз:\n_(DD.MM.YYYY форматында, мысалы: 15.03.1985)_",
        }[lang]
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif step == "dob":
        phone = context.user_data.get("results_phone", "")
        dob = text
        context.user_data.pop("results_step", None)
        context.user_data.pop("results_phone", None)

        d = load_data()
        natijalari = d.get("bemor_natijalari", [])

        def norm_phone(p):
            return "".join(c for c in p if c.isdigit())

        def norm_dob(d_):
            return "".join(c for c in d_ if c.isdigit())

        phone_norm = norm_phone(phone)
        dob_norm   = norm_dob(dob)

        found = [
            r for r in natijalari
            if norm_phone(r.get("phone", "")) == phone_norm
            and norm_dob(r.get("dob", "")) == dob_norm
        ]

        if not found:
            msg = {
                "uz": "❌ Afsuski, sizning ma'lumotlaringizga mos natija topilmadi.\n\nTelefon raqam va tug'ilgan sanani tekshirib, qaytadan urinib ko'ring yoki klinika bilan bog'laning.",
                "ru": "❌ К сожалению, результаты по вашим данным не найдены.\n\nПроверьте номер телефона и дату рождения, попробуйте ещё раз или обратитесь в клинику.",
                "kz": "❌ Кешіріңіз, деректеріңізге сәйкес нәтиже табылмады.\n\nТелефон нөмірі мен туған күнді тексеріп, қайта көріңіз немесе клиникаға хабарласыңыз.",
            }[lang]
            back_label = {"uz": "⬅️ Orqaga", "ru": "⬅️ Назад", "kz": "⬅️ Артқа"}[lang]
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_main")]])
            await update.message.reply_text(msg, reply_markup=kb)
            return

        intro = {
            "uz": f"✅ *{len(found)} ta natija topildi:*",
            "ru": f"✅ *Найдено результатов: {len(found)}:*",
            "kz": f"✅ *{len(found)} нәтиже табылды:*",
        }[lang]
        await update.message.reply_text(intro, parse_mode="Markdown")
        for r in found:
            try:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=r["file_id"],
                    filename=r.get("file_name", "natija.pdf"),
                    caption=f"📄 {r.get('file_name', 'natija.pdf')}\n🗓 {r.get('uploaded_at', '')}"
                )
            except Exception as e:
                logger.error(f"Natija yuborishda xato: {e}")
        back_label = {"uz": "⬅️ Bosh menyu", "ru": "⬅️ Главное меню", "kz": "⬅️ Бас мәзір"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_main")]])
        await update.message.reply_text("✅", reply_markup=kb)


# ── STAFF PDF UPLOAD FSM ─────────────────────────────────────────────────────

def _is_staff(user_id: int) -> bool:
    return user_id == ADMIN_ID or user_id in ALLOWED_STAFF


async def staff_pdf_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'📤 PDF Natija Yuklash' tugmasi bosilganda — faqat ALLOWED_STAFF uchun"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not _is_staff(user_id):
        await query.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    context.user_data["staff_upload_step"] = "phone"
    context.user_data["staff_upload_data"] = {}
    await query.message.reply_text(
        "📋 *Bemor telefon raqamini kiriting:*\n_(+998901234567 formatida)_",
        parse_mode="Markdown"
    )


async def staff_pdf_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Staff PDF yuklash FSM — ketma-ket: telefon → tug'ilgan sana → PDF fayl"""
    user_id = update.effective_user.id
    if not _is_staff(user_id):
        return
    step = context.user_data.get("staff_upload_step")
    logger.info(f"STAFF_PDF: user={user_id} step={step} has_text={bool(update.message.text)} has_doc={bool(update.message.document)}")
    if not step:
        return

    lang = get_lang(context)

    if step == "phone" and update.message.text:
        context.user_data["staff_upload_data"]["phone"] = update.message.text.strip()
        context.user_data["staff_upload_step"] = "dob"
        await update.message.reply_text(
            "📅 *Bemor tug'ilgan kunini kiriting:*\n_(DD.MM.YYYY formatida, masalan: 15.03.1985)_",
            parse_mode="Markdown"
        )

    elif step == "dob" and update.message.text:
        context.user_data["staff_upload_data"]["dob"] = update.message.text.strip()
        context.user_data["staff_upload_step"] = "pdf"
        await update.message.reply_text(
            "📄 *PDF natija faylini yuboring:*",
            parse_mode="Markdown"
        )

    elif step == "pdf" and update.message.document:
        doc = update.message.document
        if doc.mime_type != "application/pdf":
            await update.message.reply_text("❌ Faqat PDF fayl qabul qilinadi. Qaytadan yuboring.")
            return

        data = context.user_data.get("staff_upload_data", {})
        phone     = data.get("phone", "")
        dob       = data.get("dob", "")
        file_id   = doc.file_id
        file_name = doc.file_name or "natija.pdf"
        uploaded_at = datetime.datetime.now(TASHKENT_TZ).strftime("%Y-%m-%d %H:%M:%S")

        d = load_data()
        d.setdefault("bemor_natijalari", []).append({
            "phone":       phone,
            "dob":         dob,
            "file_id":     file_id,
            "file_name":   file_name,
            "uploaded_by": user_id,
            "uploaded_at": uploaded_at,
        })
        save_data(d)

        context.user_data.pop("staff_upload_step", None)
        context.user_data.pop("staff_upload_data", None)

        await update.message.reply_text(
            f"✅ *PDF muvaffaqiyatli yuklandi va saqlandi!*\n\n"
            f"📞 Telefon: `{phone}`\n"
            f"🎂 Tug'ilgan kun: `{dob}`\n"
            f"📄 Fayl nomi: `{file_name}`\n"
            f"🕐 Vaqt: `{uploaded_at}`\n\n"
            f"Bemor endi botdan o'z natijasini olishi mumkin.",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(lang, user_id)
        )


async def staff_doc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Document (PDF) yuborilganda faqat staff/admin uchun — staff_pdf_handler'ga yo'naltiradi"""
    logger.info(f"STAFF_DOC: user={update.effective_user.id} step={context.user_data.get('staff_upload_step')}")
    await staff_pdf_handler(update, context)


async def results_debug_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/results_debug — admin uchun saqlangan natijalarni ko'rish"""
    if update.effective_user.id != ADMIN_ID:
        return
    d = load_data()
    entries = d.get("bemor_natijalari", [])
    if not entries:
        await update.message.reply_text("📭 Hech qanday natija saqlanmagan.")
        return
    for i, r in enumerate(entries[-10:], 1):
        await update.message.reply_text(
            f"#{i}\n📞 Tel: `{r.get('phone')}`\n"
            f"🎂 Tug: `{r.get('dob')}`\n"
            f"📄 Fayl: {r.get('file_name')}\n"
            f"🕐 Vaqt: {r.get('uploaded_at')}",
            parse_mode="Markdown"
        )


async def ai_logs_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ai_logs [N] — faqat admin uchun, AI'ning oxirgi N (default 10) savol-javobini ko'rsatadi."""
    if update.effective_user.id != ADMIN_ID:
        return
    n = 10
    if context.args:
        try:
            n = max(1, min(int(context.args[0]), 50))
        except ValueError:
            pass
    if not os.path.exists(AI_LOG_FILE):
        await update.message.reply_text("📭 AI loglari hali bo'sh.")
        return
    with open(AI_LOG_FILE, "r", encoding="utf-8") as f:
        logs = json.load(f)
    if not logs:
        await update.message.reply_text("📭 AI loglari hali bo'sh.")
        return
    chunk = logs[-n:]
    for entry in chunk:
        flag = "🔴" if entry.get("needs_operator") else "🟢"
        route_txt = f" → {entry['route']}" if entry.get("route") else ""
        msg = (
            f"{flag} <b>{entry['time']}</b> | {entry['lang']} | @{entry['username']} (id:{entry['user_id']})\n"
            f"❓ {entry['question']}\n"
            f"💬 {entry['answer']}{route_txt}"
        )
        try:
            await update.message.reply_text(msg, parse_mode="HTML")
        except Exception:
            await update.message.reply_text(msg)


async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    text = update.message.text.strip()

    # ── Statistika ──
    if text == "/stats":
        d = load_data()
        users = d.get("users", {})
        total = len(users)
        uz_count = sum(1 for u in users.values() if u.get("lang") == "uz")
        ru_count = sum(1 for u in users.values() if u.get("lang") == "ru")
        kz_count = sum(1 for u in users.values() if u.get("lang") == "kz")
        await update.message.reply_text(
            f"📊 *Bot statistikasi:*\n\n"
            f"👥 Jami foydalanuvchilar: *{total}* ta\n\n"
            f"🇺🇿 O'zbekcha: {uz_count} ta\n"
            f"🇷🇺 Ruscha: {ru_count} ta\n"
            f"🇰🇿 Qozoqcha: {kz_count} ta",
            parse_mode="Markdown"
        )
        return

    # ── Broadcast ──
    if text.startswith("/broadcast "):
        msg = text.replace("/broadcast ", "", 1)
        d = load_data()
        users = d.get("users", {})
        total = len(users)
        sent = 0
        failed = 0
        await update.message.reply_text(
            f"📤 Xabar yuborilmoqda... ({total} ta foydalanuvchi)"
        )
        for uid in users.keys():
            try:
                await context.bot.send_message(
                    chat_id=int(uid),
                    text=msg,
                    parse_mode="Markdown"
                )
                sent += 1
            except Exception:
                failed += 1
        await update.message.reply_text(
            f"✅ Yuborildi: {sent} ta\n❌ Xato: {failed} ta"
        )
        return

    if text.startswith("/admin_video "):
        section = text.replace("/admin_video ", "").strip()
        # xona_ prefiksi bo'lsa to'g'ridan-to'g'ri saqlash
        if section.startswith("xona_"):
            context.user_data["waiting_photo"] = section
        else:
            context.user_data["waiting_photo"] = f"guide_video_{section}"
        await update.message.reply_text(
            f"🎥 Tayyor! Endi *{section}* bo'limi uchun video yuboring:",
            parse_mode="Markdown"
        )
        return

    if text == "/admin_help":
        help_text = """🔧 *Admin buyruqlari:*

📊 *Statistika:*
`/stats` — foydalanuvchilar soni

📢 *Broadcast:*
`/broadcast Yangi xizmat qo'shildi!`

📸 *Rasm qo'shish:*
`/admin_photo clinic` — klinika rasmi
`/admin_photo samarkand` — Samarqand
`/admin_photo bukhara` — Buxoro
`/admin_photo doctor` — shifokor rasmi
`/admin_photo cert` — sertifikat
`/admin_photo nuga_best` — Nuga-Best rasmi
`/admin_photo seragem` — Seragem rasmi
`/admin_photo foot_massage` — Oyoq nuqtalari massaji rasmi
`/admin_photo general_massage` — Umumiy massaj rasmi
`/admin_photo bioenergy_massage` — Bioenergiya massaji rasmi
`/admin_photo lymph` — Limfadrenaj rasmi
`/admin_photo stretch` — Rastyajka rasmi
`/admin_photo shockwave` — Zarb to'lqinli terapiya rasmi
`/admin_photo cryo` — Kriolipoliz rasmi
`/admin_photo fitobar` — Fito-Bar rasmi
`/admin_photo almond_oil` — Bodom yog'i rasmi
`/admin_photo olive_oil` — Zaytun yog'i rasmi
`/admin_photo registration` — Kelish tartibi rasmi
`/admin_photo treatment` — Operatsiyasiz davolash rasmi
`/admin_photo diet` — Ovqatlanish/parhez rasmi
`/admin_photo work_hours` — Ish vaqti rasmi
`/admin_photo guide_step3_p1` — 3-bo'lim 1-qadam rasmi
`/admin_photo guide_step3_p2` — 3-bo'lim 2-qadam rasmi
`/admin_photo guide_step3_foreign` — Chet el fuqarolari grafigi
`/admin_photo guide_step3_local` — O'zbekiston fuqarolari grafigi
`/admin_photo guide_step3_p3` — 3-bo'lim 3-qadam rasmi
`/admin_photo guide_step3_p4` — 3-bo'lim 4-qadam rasmi
`/admin_photo juraqulov` — Jo'raqulov Jaxongir rasmi
`/admin_photo infra_main` — Asosiy korpus rasmi
`/admin_photo infra_m_building` — M korpus rasmi
`/admin_photo infra_klizma` — Klizma xonasi rasmi
`/admin_photo infra_fizio` — Fizioxona rasmi
`/admin_photo infra_massaj` — Massaj xonasi rasmi
`/admin_photo infra_nurse` — Muolaja xonasi rasmi
`/admin_photo diag_mrt15` — MRT 1.5T rasmi
`/admin_photo diag_mrt3t` — MRT 3T asosiy rasmi
`/admin_photo diag_mrt3t_0` — MRT 3T 1-guruh rasmi
`/admin_photo diag_mrt3t_1` — MRT 3T 2-guruh rasmi
`/admin_photo diag_mrt3t_2` — MRT 3T 3-guruh rasmi
`/admin_photo diag_mrt3t_3` — MRT 3T 4-guruh rasmi
`/admin_photo diag_mrt3t_4` — MRT 3T 5-guruh rasmi
`/admin_photo diag_mskt256` — MSKT 256 rasmi
`/admin_photo diag_mskt128` — MSKT 128 rasmi
`/admin_photo diag_other` — UZI rasmi
`/admin_photo diag_mammografiya` — Mammografiya rasmi
`/admin_photo diag_fibroskan` — Fibroskan rasmi
`/admin_photo diag_lab` — Laboratoriya rasmi
`/admin_photo korpus_m_yangi` — korpus rasmi
`/admin_photo xona_m_yangi_0` — xona rasmi

🎥 *Video qo'shish (bo'limlarga):*
`/admin_video arrival_step1` — 1-bosqich
`/admin_video arrival_step2` — 2-bosqich
`/admin_video arrival_step3` — 3-bosqich
`/admin_video malham` — Malham
`/admin_video procedures` — Protseduralar
`/admin_video infrastructure` — Infrastruktura
`/admin_video rules` — Qoidalar
`/admin_video shopping` — Uyga nima olish
`/admin_video clinic` — Klinika haqida

📝 *Matn o'zgartirish:*
`/admin contacts|phone1|+998901234567`"""
        await update.message.reply_text(help_text, parse_mode="Markdown")
        return

    if text.startswith("/admin_photo_clear"):
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text("Format: /admin_photo_clear xona_umumiy_z_3")
            return
        target = parts[1]
        d = load_data()
        if target.startswith("xona_"):
            last_underscore = target.rfind("_")
            korpus_id = target[5:last_underscore]
            xona_idx = int(target[last_underscore + 1:])
            for k in d.get("korpuslar", []):
                if k["id"] == korpus_id:
                    if xona_idx < len(k["xonalar"]):
                        k["xonalar"][xona_idx]["photos"] = []
                        save_data(d)
                        await update.message.reply_text(f"✅ {korpus_id} / {xona_idx}-xona rasmlari tozalandi!")
                    else:
                        await update.message.reply_text("❌ Xona topilmadi")
                    return
            await update.message.reply_text("❌ Korpus topilmadi")
        elif target.startswith("korpus_"):
            korpus_id = target.replace("korpus_", "")
            for k in d.get("korpuslar", []):
                if k["id"] == korpus_id:
                    k["photos"] = []
                    save_data(d)
                    await update.message.reply_text(f"✅ {korpus_id} korpus rasmlari tozalandi!")
                    return
            await update.message.reply_text("❌ Korpus topilmadi")
        elif target in ("clinic", "team", "ward", "cert", "samarkand", "bukhara"):
            key = target + "_photos"
            d[key] = []
            save_data(d)
            await update.message.reply_text(f"✅ {target} rasmlari tozalandi!")
        else:
            await update.message.reply_text("❌ Noto'g'ri format")
        return

    if text.startswith("/admin_photo_del"):
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text(
                "Format: /admin_photo_del <kalit>\n"
                "Misol: /admin_photo_del guide_step3_foreign\n\n"
                "O'chirish mumkin bo'lgan kalitlar:\n"
                "`guide_step3_foreign` — Chet el grafigi\n"
                "`guide_step3_local` — O'zbekiston grafigi\n"
                "`guide_step3_p1` → `guide_step3_p4` — Qadamlar rasmlari\n"
                "`nuga_best_photo_id`, `seragem_photo_id` va boshqalar"
            )
            return
        key = parts[1]
        # Single-key foto lar uchun mapping
        key_map = {
            "guide_step3_foreign":  "guide_step3_foreign_photo",
            "guide_step3_local":    "guide_step3_local_photo",
            "guide_step3_p1":       "guide_step3_p1_photo",
            "guide_step3_p2":       "guide_step3_p2_photo",
            "guide_step3_p3":       "guide_step3_p3_photo",
            "guide_step3_p4":       "guide_step3_p4_photo",
            "nuga_best":            "nuga_best_photo_id",
            "seragem":              "seragem_photo_id",
            "foot_massage":         "foot_massage_photo_id",
            "general_massage":      "general_massage_photo_id",
            "bioenergy_massage":    "bioenergy_massage_photo_id",
            "lymph":                "lymph_photo_id",
            "stretch":              "stretch_photo_id",
            "shockwave":            "shockwave_photo_id",
            "cryo":                 "cryo_photo_id",
            "fitobar":              "fitobar_photo_id",
            "almond_oil":           "almond_oil_photo_id",
            "olive_oil":            "olive_oil_photo_id",
            "registration":         "registration_photo_id",
            "treatment":            "treatment_photo_id",
            "diet":                 "diet_photo_id",
            "work_hours":           "work_hours_photo_id",
        }
        d = load_data()
        data_key = key_map.get(key, key)
        if data_key in d:
            del d[data_key]
            save_data(d)
            await update.message.reply_text(f"✅ `{key}` rasmi o'chirildi!")
        else:
            await update.message.reply_text(f"❌ `{key}` topilmadi yoki allaqachon bo'sh.")
        return

    if text.startswith("/admin_photo") and not text.startswith("/admin_photo_clear") and not text.startswith("/admin_photo_del"):
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text("Format: /admin_photo <kalit>\nMisol: /admin_photo diag_mrt15")
            return
        context.user_data["waiting_photo"] = parts[1]
        await update.message.reply_text(f"✅ Endi rasmni yuboring — `{parts[1]}` uchun saqlanadi!")
        return

    if text.startswith("/admin_video_clear"):
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text(
                "Format: /admin_video_clear xona_m_yangi_4\n"
                "Xonadagi barcha videolarni o'chiradi."
            )
            return
        target = parts[1]
        d = load_data()
        if target.startswith("xona_"):
            last = target.rfind("_")
            korpus_id = target[5:last]
            xona_idx = int(target[last+1:])
            for k in d.get("korpuslar", []):
                if k["id"] == korpus_id:
                    if xona_idx < len(k["xonalar"]):
                        k["xonalar"][xona_idx]["videos"] = []
                        save_data(d)
                        await update.message.reply_text(f"✅ {korpus_id} / {xona_idx}-xona videolari tozalandi!")
                    else:
                        await update.message.reply_text("❌ Xona topilmadi")
                    return
            await update.message.reply_text("❌ Korpus topilmadi")
        return

    if text.startswith("/admin_video_del"):
        parts = text.split()
        if len(parts) < 3:
            await update.message.reply_text(
                "Format: /admin_video_del xona_m_yangi_4 0\n"
                "(0 = birinchi video)"
            )
            return
        target = parts[1]
        try:
            vid_idx = int(parts[2])
        except ValueError:
            await update.message.reply_text("❌ Index raqam bo'lishi kerak")
            return
        d = load_data()
        if target.startswith("xona_"):
            last = target.rfind("_")
            korpus_id = target[5:last]
            xona_idx = int(target[last+1:])
            for k in d.get("korpuslar", []):
                if k["id"] == korpus_id:
                    if xona_idx < len(k["xonalar"]):
                        videos = k["xonalar"][xona_idx].get("videos", [])
                        if vid_idx < len(videos):
                            videos.pop(vid_idx)
                            k["xonalar"][xona_idx]["videos"] = videos
                            save_data(d)
                            await update.message.reply_text(
                                f"✅ {xona_idx}-xonadan {vid_idx}-video o'chirildi! Qolgan: {len(videos)} ta"
                            )
                        else:
                            await update.message.reply_text(f"❌ Index {vid_idx} topilmadi. Jami: {len(videos)} ta video")
                    else:
                        await update.message.reply_text("❌ Xona topilmadi")
                    return
            await update.message.reply_text("❌ Korpus topilmadi")
        return


        d = load_data()
        photos = d.get("team_photos", [])
        await update.message.reply_text(
            f"📊 team_photos soni: {len(photos)}\n"
            f"DATA_FILE: {DATA_FILE}\n"
            f"Rasmlar: {photos[:3]}{'...' if len(photos) > 3 else ''}"
        )
        return

    if text.startswith("/admin_team_clear"):
        d = load_data()
        d["team_photos"] = []
        save_data(d)
        await update.message.reply_text("✅ Jamoa rasmlari tozalandi. Qayta yuklash: /admin_photo team")
        return


        d = load_data()
        d["team_photos"] = []
        save_data(d)
        await update.message.reply_text("✅ Jamoa rasmlari tozalandi. Qayta yuklash: /admin_photo team")
        return


        d = load_data()
        if "guide" not in d:
            d["guide"] = {}
        d["guide"]["rules"] = {
            "ru": "RESET",
            "uz": "RESET",
            "kz": "RESET",
        }
        save_data(d)
        await update.message.reply_text("✅ guide.rules data.json dan tozalandi. Endi tugma yangi matnni ko'rsatadi.")
        return


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


DOCTORS_GROUP_ID = -5193012514  # Ergash-Ota shifokorlar nazorati guruhi
FEEDBACK_GROUP_ID = -5529849558  # Taklif va shikoyatlar (klinika rahbariyati) guruhi

async def medical_doc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bemor rasm/fayl yuborsa — FSM state ga qo'shadi"""
    user = update.effective_user
    lang = get_lang(context)

    # ── TAKLIF VA SHIKOYATLAR bo'limida RASM/VIDEO yuborilsa — fikr-mulohaza guruhiga yuboriladi ──
    if context.user_data.get("state") == "FEEDBACK_WAITING" and (update.message.photo or update.message.video):
        username = f"@{user.username}" if user.username else "—"
        context.user_data["state"] = None
        caption = (
            f"✍️ <b>Yangi taklif/shikoyat ({'rasm' if update.message.photo else 'video'}):</b>\n"
            f"👤 Bemor ID: {user.id}  uid:{user.id}\n"
            f"💬 Telegram: {username}"
        )
        try:
            if update.message.photo:
                await context.bot.send_photo(chat_id=FEEDBACK_GROUP_ID, photo=update.message.photo[-1].file_id,
                                              caption=caption, parse_mode="HTML")
            else:
                await context.bot.send_video(chat_id=FEEDBACK_GROUP_ID, video=update.message.video.file_id,
                                              caption=caption, parse_mode="HTML")
            confirm = {"ru": "✅ Ваше сообщение принято! Спасибо за обратную связь.",
                       "uz": "✅ Xabaringiz qabul qilindi! Fikr-mulohazangiz uchun rahmat.",
                       "kz": "✅ Хабарыңыз қабылданды! Пікіріңіз үшін рахмет."}[lang]
            await update.message.reply_text(confirm, reply_markup=main_menu_keyboard(lang, update.effective_user.id if update.effective_user else 0))
        except Exception as e:
            logger.error(f"Feedback media yuborish xatosi: {e}")
            await update.message.reply_text("❌ Xabar yuborishda xatolik yuz berdi.")
        return

    # ── SHIFOKORGA SAVOL bo'limi rasm kutayotgan bo'lsa — bu yerga yo'naltiramiz ──
    if context.user_data.get("state") == "DOCTOR_MEDIA_WAITING" and update.message.photo:
        photo_id = update.message.photo[-1].file_id
        context.user_data.setdefault("temp_photos", []).append(photo_id)
        count = len(context.user_data["temp_photos"])
        done_label   = {"ru": f"✅ Готово ({count} фото) — отправить", "uz": f"✅ Tayyor ({count} rasm) — yuborish", "kz": f"✅ Дайын ({count} сурет) — жіберу"}[lang]
        cancel_label = {"ru": "❌ Отмена", "uz": "❌ Bekor qilish", "kz": "❌ Болдырмау"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(done_label,   callback_data="send_to_doctor_now")],
            [InlineKeyboardButton(cancel_label, callback_data="cancel_doctor_question")],
        ])
        added = {"ru": f"✅ Фото {count} добавлено.", "uz": f"✅ {count}-rasm qo'shildi.", "kz": f"✅ {count} сурет қосылды."}[lang]
        await update.message.reply_text(added, reply_markup=kb)
        return

    # Med state yo'q bo'lsa — init qilamiz
    if "med_state" not in context.user_data:
        context.user_data["med_state"] = {"photos": [], "voice_id": None, "bemor_matni": ""}

    med = context.user_data["med_state"]

    if update.message.photo:
        photo_id = update.message.photo[-1].file_id
        med["photos"].append(photo_id)
        count = len(med["photos"])
        confirm_label = {"ru": "✅ Подтвердить и отправить", "uz": "✅ Tasdiqlash va yuborish", "kz": "✅ Растау және жіберу"}[lang]
        cancel_label = {"ru": "⬅️ Отмена", "uz": "⬅️ Bekor qilish", "kz": "⬅️ Бас тарту"}[lang]
        added = {"ru": f"📸 Фото добавлено ({count} шт.). Можно добавить ещё или отправить.", "uz": f"📸 Rasm qo'shildi ({count} ta). Yana qo'shishingiz yoki yuborishingiz mumkin.", "kz": f"📸 Сурет қосылды ({count} дана). Тағы қосуға немесе жіберуге болады."}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(confirm_label, callback_data="confirm_medical")],
            [InlineKeyboardButton(cancel_label, callback_data="disease_not_found")],
        ])
        await update.message.reply_text(added, reply_markup=kb)

    elif update.message.document:
        file_id = update.message.document.file_id
        med["photos"].append(file_id)
        confirm_label = {"ru": "✅ Подтвердить и отправить", "uz": "✅ Tasdiqlash va yuborish", "kz": "✅ Растау және жіберу"}[lang]
        cancel_label = {"ru": "⬅️ Отмена", "uz": "⬅️ Bekor qilish", "kz": "⬅️ Бас тарту"}[lang]
        added = {"ru": "📁 Документ добавлен.", "uz": "📁 Hujjat qo'shildi.", "kz": "📁 Құжат қосылды."}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(confirm_label, callback_data="confirm_medical")],
            [InlineKeyboardButton(cancel_label, callback_data="disease_not_found")],
        ])
        await update.message.reply_text(added, reply_markup=kb)


async def medical_voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bemor ovozli xabar yuborsa — FSM state ga saqlaydi"""
    lang = get_lang(context)

    # ── TAKLIF VA SHIKOYATLAR bo'limi kutayotgan bo'lsa — ovozli xabarni shu yerga yo'naltiramiz ──
    if context.user_data.get("state") == "FEEDBACK_WAITING":
        user = update.effective_user
        username = f"@{user.username}" if user.username else "—"
        context.user_data["state"] = None
        caption = (
            f"✍️ <b>Yangi taklif/shikoyat (ovozli):</b>\n"
            f"👤 Bemor ID: {user.id}  uid:{user.id}\n"
            f"💬 Telegram: {username}"
        )
        try:
            await context.bot.send_voice(chat_id=FEEDBACK_GROUP_ID, voice=update.message.voice.file_id,
                                          caption=caption, parse_mode="HTML")
            confirm = {"ru": "✅ Ваше сообщение принято! Спасибо за обратную связь.",
                       "uz": "✅ Xabaringiz qabul qilindi! Fikr-mulohazangiz uchun rahmat.",
                       "kz": "✅ Хабарыңыз қабылданды! Пікіріңіз үшін рахмет."}[lang]
            back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_guide")]])
            await update.message.reply_text(confirm, reply_markup=kb)
        except Exception as e:
            logger.error(f"Feedback voice yuborish xatosi: {e}")
            await update.message.reply_text("❌ Xabar yuborishda xatolik yuz berdi.")
        return

    if "med_state" not in context.user_data:
        context.user_data["med_state"] = {"photos": [], "voice_id": None, "bemor_matni": ""}

    context.user_data["med_state"]["voice_id"] = update.message.voice.file_id

    confirm_label = {"ru": "✅ Подтвердить и отправить", "uz": "✅ Tasdiqlash va yuborish", "kz": "✅ Растау және жіберу"}[lang]
    cancel_label = {"ru": "⬅️ Отмена", "uz": "⬅️ Bekor qilish", "kz": "⬅️ Бас тарту"}[lang]
    saved = {"ru": "🎤 Голосовое сообщение сохранено. Можно добавить фото или сразу отправить.", "uz": "🎤 Ovozli xabar saqlandi. Rasm qo'shishingiz yoki yuborishingiz mumkin.", "kz": "🎤 Дауыстық хабар сақталды. Сурет қосуға немесе жіберуге болады."}[lang]
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(confirm_label, callback_data="confirm_medical")],
        [InlineKeyboardButton(cancel_label, callback_data="disease_not_found")],
    ])
    await update.message.reply_text(saved, reply_markup=kb)


async def doctor_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shifokor guruh yoki kanalda xabariga REPLY qilganda — bemorga yetkazadi"""
    msg = update.message or update.channel_post
    if not msg or not msg.reply_to_message:
        return
    allowed = {DOCTORS_GROUP_ID, STATSIONAR_CHANNEL, DIAGNOSTIKA_CHANNEL, FEEDBACK_GROUP_ID}
    logger.info(f"doctor_reply_handler: chat_id={msg.chat.id}, allowed={allowed}")
    if msg.chat.id not in allowed:
        return

    original = msg.reply_to_message
    original_text = original.caption or original.text or ""
    logger.info(f"doctor_reply_handler: original_text={original_text[:100]}")

    import re
    match = re.search(r"uid:(\d+)", original_text)
    if not match:
        logger.info(f"doctor_reply_handler: uid topilmadi")
        try:
            await msg.reply_text("⚠️ uid topilmadi — bemor aniqlanmadi.")
        except Exception:
            pass
        return

    patient_id = int(match.group(1))
    logger.info(f"doctor_reply_handler: patient_id={patient_id}")
    is_feedback = "taklif/shikoyat" in original_text.lower()

    try:
        if msg.voice:
            await context.bot.send_voice(
                chat_id=patient_id,
                voice=msg.voice.file_id,
                caption="👨‍⚕️ *Shifokordan ovozli javob:*",
                parse_mode="Markdown"
            )
        elif msg.text or msg.caption:
            if is_feedback:
                reply_text = f"📩 *Taklifingizga javob:*\n\n{msg.text or msg.caption}"
            else:
                reply_text = f"👨‍⚕️ *Shifokordan javob:*\n\n{msg.text or msg.caption}"
            await context.bot.send_message(
                chat_id=patient_id,
                text=reply_text,
                parse_mode="Markdown"
            )
        try:
            await msg.reply_text("✅ Javob bemorga yetkazildi.")
        except Exception:
            pass
    except Exception as e:
        logger.error(f"doctor_reply_handler error: {e}")
        try:
            await msg.reply_text(f"❌ Xato: {e}")
        except Exception:
            pass



async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    # Admin med_state orqali tibbiy hujjat yuborishi
    if isinstance(context.user_data.get("med_state"), dict):
        med = context.user_data["med_state"]
        photo_id = update.message.photo[-1].file_id
        med["photos"].append(photo_id)
        count = len(med["photos"])
        lang = get_lang(context)
        confirm_label = {"ru": "✅ Подтвердить и отправить", "uz": "✅ Tasdiqlash va yuborish", "kz": "✅ Растау және жіберу"}[lang]
        cancel_label = {"ru": "⬅️ Отмена", "uz": "⬅️ Bekor qilish", "kz": "⬅️ Бас тарту"}[lang]
        added = {"ru": f"📸 Фото добавлено ({count} шт.).", "uz": f"📸 Rasm qo'shildi ({count} ta).", "kz": f"📸 Сурет қосылды ({count} дана)."}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(confirm_label, callback_data="confirm_medical")],
            [InlineKeyboardButton(cancel_label, callback_data="disease_not_found")],
        ])
        await update.message.reply_text(added, reply_markup=kb)
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
    elif waiting == "juraqulov":
        d["juraqulov_photo_id"] = file_id
        await update.message.reply_text("✅ Jo'raqulov rasmi saqlandi!")
        await update.message.reply_text(f"✅ Jamoa rasmi qo'shildi! Jami: {len(d['team_photos'])} ta\n"
                                        f"Tozalash uchun: /admin_team_clear")
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
    elif waiting == "cert":
        d["cert_photos"].append(file_id)
        await update.message.reply_text(f"✅ Sertifikat rasmi qo'shildi! Jami: {len(d['cert_photos'])} ta")
    elif waiting == "nuga_best":
        d["nuga_best_photo_id"] = file_id
        await update.message.reply_text("✅ Nuga-Best rasmi saqlandi!")
    elif waiting == "seragem":
        d["seragem_photo_id"] = file_id
        await update.message.reply_text("✅ Seragem rasmi saqlandi!")
    elif waiting == "foot_massage":
        d["foot_massage_photo_id"] = file_id
        await update.message.reply_text("✅ Oyoq massaji rasmi saqlandi!")
    elif waiting == "general_massage":
        d["general_massage_photo_id"] = file_id
        await update.message.reply_text("✅ Umumiy massaj rasmi saqlandi!")
    elif waiting == "bioenergy_massage":
        d["bioenergy_massage_photo_id"] = file_id
        await update.message.reply_text("✅ Bioenergiya massaji rasmi saqlandi!")
    elif waiting == "lymph":
        d["lymph_photo_id"] = file_id
        await update.message.reply_text("✅ Limfadrenaj rasmi saqlandi!")
    elif waiting == "stretch":
        d["stretch_photo_id"] = file_id
        await update.message.reply_text("✅ Rastyajka rasmi saqlandi!")
    elif waiting == "shockwave":
        d["shockwave_photo_id"] = file_id
        await update.message.reply_text("✅ Zarb to'lqinli terapiya rasmi saqlandi!")
    elif waiting == "cryo":
        d["cryo_photo_id"] = file_id
        await update.message.reply_text("✅ Kriolipoliz rasmi saqlandi!")
    elif waiting == "fitobar":
        d["fitobar_photo_id"] = file_id
        await update.message.reply_text("✅ Fito-Bar rasmi saqlandi!")
    elif waiting == "almond_oil":
        d["almond_oil_photo_id"] = file_id
        await update.message.reply_text("✅ Bodom yog'i rasmi saqlandi!")
    elif waiting == "olive_oil":
        d["olive_oil_photo_id"] = file_id
        await update.message.reply_text("✅ Zaytun yog'i rasmi saqlandi!")
    elif waiting == "registration":
        d["registration_photo_id"] = file_id
        await update.message.reply_text("✅ Kelish tartibi rasmi saqlandi!")
    elif waiting == "treatment":
        d["treatment_photo_id"] = file_id
        await update.message.reply_text("✅ Operatsiyasiz davolash rasmi saqlandi!")
    elif waiting == "diet":
        d["diet_photo_id"] = file_id
        await update.message.reply_text("✅ Ovqatlanish/parhez rasmi saqlandi!")
    elif waiting == "work_hours":
        d["work_hours_photo_id"] = file_id
        await update.message.reply_text("✅ Ish vaqti rasmi saqlandi!")
    elif waiting == "guide_step3_p1":
        d["guide_step3_p1_photo"] = file_id
        await update.message.reply_text("✅ 3-bo'lim 1-qadam rasmi saqlandi!")
    elif waiting == "guide_step3_p2":
        d["guide_step3_p2_photo"] = file_id
        await update.message.reply_text("✅ 3-bo'lim 2-qadam rasmi saqlandi!")
    elif waiting == "guide_step3_foreign":
        d["guide_step3_foreign_photo"] = file_id
        await update.message.reply_text("✅ Chet el fuqarolari grafik rasmi saqlandi!")
    elif waiting == "guide_step3_local":
        d["guide_step3_local_photo"] = file_id
        await update.message.reply_text("✅ O'zbekiston fuqarolari grafik rasmi saqlandi!")
    elif waiting == "guide_step3_p3":
        d["guide_step3_p3_photo"] = file_id
        await update.message.reply_text("✅ 3-bo'lim 3-qadam rasmi saqlandi!")
    elif waiting == "guide_step3_p4":
        d["guide_step3_p4_photo"] = file_id
        await update.message.reply_text("✅ 3-bo'lim 4-qadam rasmi saqlandi!")
    elif waiting == "infra_menu":
        d["infra_menu_photo"] = file_id
        await update.message.reply_text("✅ Infratuzilma menyu rasmi saqlandi!")
    elif waiting == "infra_main":
        d["infra_main_photo"] = file_id
        await update.message.reply_text("✅ Asosiy korpus rasmi saqlandi!")
    elif waiting == "infra_m_building":
        d["infra_m_building_photo"] = file_id
        await update.message.reply_text("✅ M korpus rasmi saqlandi!")
    elif waiting == "infra_klizma":
        d["infra_klizma_photo"] = file_id
        await update.message.reply_text("✅ Klizma xonasi rasmi saqlandi!")
    elif waiting == "infra_fizio":
        d["infra_fizio_photo"] = file_id
        await update.message.reply_text("✅ Fizioxona rasmi saqlandi!")
    elif waiting == "infra_massaj":
        d["infra_massaj_photo"] = file_id
        await update.message.reply_text("✅ Massaj xonasi rasmi saqlandi!")
    elif waiting == "infra_nurse":
        d["infra_nurse_photo"] = file_id
        await update.message.reply_text("✅ Muolaja xonasi rasmi saqlandi!")
    elif waiting == "diag_mrt15":
        d["diag_mrt15_photo"] = file_id
        await update.message.reply_text("✅ MRT 1.5T rasmi saqlandi!")
    elif waiting == "diag_mrt3t":
        d["diag_mrt3t_photo"] = file_id
        await update.message.reply_text("✅ MRT 3T asosiy rasmi saqlandi!")
    elif waiting == "diag_mrt3t_0":
        d["diag_mrt3t_0_photo"] = file_id
        await update.message.reply_text("✅ MRT 3T — 1-guruh rasmi saqlandi!")
    elif waiting == "diag_mrt3t_1":
        d["diag_mrt3t_1_photo"] = file_id
        await update.message.reply_text("✅ MRT 3T — 2-guruh rasmi saqlandi!")
    elif waiting == "diag_mrt3t_2":
        d["diag_mrt3t_2_photo"] = file_id
        await update.message.reply_text("✅ MRT 3T — 3-guruh rasmi saqlandi!")
    elif waiting == "diag_mrt3t_3":
        d["diag_mrt3t_3_photo"] = file_id
        await update.message.reply_text("✅ MRT 3T — 4-guruh rasmi saqlandi!")
    elif waiting == "diag_mrt3t_4":
        d["diag_mrt3t_4_photo"] = file_id
        await update.message.reply_text("✅ MRT 3T — 5-guruh rasmi saqlandi!")
    elif waiting == "diag_mskt256":
        d["diag_mskt256_photo"] = file_id
        await update.message.reply_text("✅ MSKT 256 rasmi saqlandi!")
    elif waiting == "diag_mskt128":
        d["diag_mskt128_photo"] = file_id
        await update.message.reply_text("✅ MSKT 128 rasmi saqlandi!")
    elif waiting == "diag_other":
        d["diag_other_photo"] = file_id
        await update.message.reply_text("✅ UZI rasmi saqlandi!")
    elif waiting == "diag_mammografiya":
        d["diag_mammografiya_photo"] = file_id
        await update.message.reply_text("✅ Mammografiya rasmi saqlandi!")
    elif waiting == "diag_fibroskan":
        d["diag_fibroskan_photo"] = file_id
        await update.message.reply_text("✅ Fibroskan rasmi saqlandi!")
    elif waiting == "diag_lab":
        d["diag_lab_photo"] = file_id
        await update.message.reply_text("✅ Laboratoriya rasmi saqlandi!")
    elif waiting.startswith("korpus_"):
        korpus_id = waiting.replace("korpus_", "")
        korpuslar = d.get("korpuslar", [])
        for k in korpuslar:
            if k["id"] == korpus_id:
                k["photos"].append(file_id)
                save_data(d)
                await update.message.reply_text(f"✅ {k['name_uz']} korpus rasmi qo'shildi! Jami: {len(k['photos'])} ta")
                context.user_data["waiting_photo"] = None
                return
        await update.message.reply_text("❌ Korpus topilmadi")
        return
    elif waiting.startswith("xona_"):
        last_underscore = waiting.rfind("_")
        korpus_id = waiting[5:last_underscore]
        xona_idx = int(waiting[last_underscore + 1:])
        korpuslar = d.get("korpuslar", [])
        found_korpus = False
        for k in korpuslar:
            if k["id"] == korpus_id:
                found_korpus = True
                if xona_idx < len(k["xonalar"]):
                    k["xonalar"][xona_idx]["photos"].append(file_id)
                    save_data(d)
                    xona_nom = k["xonalar"][xona_idx]["nom"]
                    await update.message.reply_text(f"✅ {xona_nom} xona rasmi qo'shildi!")
                    context.user_data["waiting_photo"] = None
                    return
                else:
                    await update.message.reply_text(
                        f"❌ Xona topilmadi. Korpus: {korpus_id}, idx: {xona_idx}, "
                        f"xonalar soni: {len(k['xonalar'])}"
                    )
                    context.user_data["waiting_photo"] = None
                    return
        if not found_korpus:
            ids = [k["id"] for k in korpuslar]
            await update.message.reply_text(f"❌ Korpus topilmadi: '{korpus_id}'. Mavjud: {ids}")
        context.user_data["waiting_photo"] = None
        return
        idx = int(waiting.split("_")[1])
        if idx < len(d["staff"]):
            d["staff"][idx]["photo_id"] = file_id
            await update.message.reply_text(f"✅ {d['staff'][idx]['name']} rasmi saqlandi!")

    save_data(d)
    context.user_data["waiting_photo"] = None


async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    waiting = context.user_data.get("waiting_photo")
    if not waiting:
        return
    video = update.message.video
    if not video:
        return
    file_id = video.file_id
    d = load_data()

    if waiting == "video":
        d["clinic_videos"].append(file_id)
        save_data(d)
        await update.message.reply_text(f"✅ Klinika video qo'shildi! Jami: {len(d['clinic_videos'])} ta")
        context.user_data["waiting_photo"] = None
    elif waiting.startswith("guide_video_"):
        section = waiting.replace("guide_video_", "")
        if "guide" in d and section in d["guide"]:
            d["guide"][section]["video"] = file_id
            save_data(d)
            await update.message.reply_text(f"✅ '{section}' bo'limi videosi saqlandi!")
        else:
            await update.message.reply_text(f"❌ '{section}' topilmadi")
        context.user_data["waiting_photo"] = None

    elif waiting.startswith("xona_"):
        last_underscore = waiting.rfind("_")
        korpus_id = waiting[5:last_underscore]
        xona_idx = int(waiting[last_underscore + 1:])
        korpuslar = d.get("korpuslar", [])
        for k in korpuslar:
            if k["id"] == korpus_id:
                if xona_idx < len(k["xonalar"]):
                    xona = k["xonalar"][xona_idx]
                    if "videos" not in xona:
                        xona["videos"] = []
                    xona["videos"].append(file_id)
                    save_data(d)
                    await update.message.reply_text(f"✅ {xona['nom']} xona videosi qo'shildi!")
                    context.user_data["waiting_photo"] = None
                    return
                else:
                    await update.message.reply_text(f"❌ Xona topilmadi. idx: {xona_idx}")
                    context.user_data["waiting_photo"] = None
                    return
        await update.message.reply_text(f"❌ Korpus topilmadi: {korpus_id}")
        context.user_data["waiting_photo"] = None



# ─── FAQ DATA ─────────────────────────────────────────────────────────────────

FAQ_DATA = {
    "ru": [
        ("📅 Срок лечения?", (
            "📅 *Сколько дней нужно лечиться?*\n\n"
            "Уважаемый пациент! Срок лечения в нашем центре определяется *индивидуально* лечащим врачом в зависимости от состояния каждого организма:\n\n"
            "• 🩺 *Курсы лечения:* В зависимости от степени заболевания — *18, 21 или 24 дня*.\n"
            "• 🛡 *Профилактика:* Для предотвращения болезни рекомендуется минимум *12–14 дней*.\n"
            "• ⚠️ *Минимальный срок:* Для ощутимого результата важно, чтобы лечение составляло *не менее 10 дней*.\n\n"
            "💡 *Наша философия исцеления:*\n"
            "Центр «Эргаш ота» не просто временно подавляет симптомы болезни. Наша главная цель — *выявить причины болезни и устранить их с корнем!*"
        )),
        ("💰 Как формируется цена?", "Цена — за 1 день/1 человека. Включает: проживание, лечение, физиотерапию, УЗИ, анализы, МРТ 1.5Т или МСКТ (1 орган)."),
        ("🧲 Как подготовиться к МРТ?", "Специальная подготовка не требуется. Снимите металлические предметы. При МРТ с контрастом — не есть 4–6 часов до процедуры."),
        ("💊 Лечение без операции?", "q_no_surgery"),
        ("🚻 Палаты мужские и женские?", "Да, палаты раздельные. Женщин и мужчин размещают в разных палатах."),
        ("🍽 Есть ли питание?", "q_diet_food"),
        ("🕐 Режим работы?", "q_work_hours"),
    ],
    "uz": [
        ("📅 Davolanish muddati?", (
            "📅 *Davolanish muddati necha kun?*\n\n"
            "Hurmatli bemor! Markazimizda davolanish muddati har bir organizmning holatiga qarab, shifokor tomonidan *individual* belgilanadi:\n\n"
            "• 🩺 *Davolash kurslari:* Kasallik darajasiga qarab *18, 21 yoki 24 kun* davom etadi.\n"
            "• 🛡 *Profilaktika:* Kasallikning oldini olish uchun kamida *12–14 kun* tavsiya etiladi.\n"
            "• ⚠️ *Eng kam muddat:* Natija sezilishi uchun davolanish *10 kundan kam bo'lmasligi* muhim.\n\n"
            "💡 *Bizning shifo falsafamiz:*\n"
            "'Ergash ota' markazi shunchaki kasallik belgilarini (simptomlarini) vaqtinchalik bostirmaydi. Bizning asosiy maqsadimiz — *kasallikning kelib chiqish sabablarini aniqlash va uni tub ildizi bilan bartaraf etishdir!*"
        )),
        ("💰 Narx qanday shakllanadi?", (
            "💰 *Narxlar qanday shakllanadi?*\n\n"
            "Tibbiyot markazimizda narxlar va xizmatlar quyidagi tartibda hisoblanadi:\n\n"
            "• 🛏 *Xona to'lovi ichida:* Siz tanlagan xona narxiga *yotoq joy va asosiy davolanish muolajalari* kiritilgan.\n"
            "• 🧬 *Xona turiga qarab muolajalar:* bepul qo'shimcha muolajalar to'lov ichiga kiritilgan bo'ladi.\n"
            "• 👤 *Me'yor:* Narxlar *bir kunga va bir kishi uchun* ko'rsatilgan. Sizga maqul bo'lgan xona to'lovini davolanish kuniga ko'paytirsangiz umumiy to'lov kelib chiqadi.\n\n"
            "⚠️ *Kun va tun hisoblash tartibi:*\n"
            "• Agar *10 kunlik* to'lov qilsangiz, bu *9 kecha va 10 kunni* tashkil qiladi.\n"
            "• Oxirgi kuni bemor markazda tunab qolmaydi (*nochivat qilmaydi*) va xonani soat *17:00 gacha* bo'shatib berishi kerak bo'ladi.\n\n"
            "Kelish va ketish vaqtingizni hamda xona turini tanlashda ushbu qoidalarga e'tibor berishingizni so'raymiz."
        )),
        ("🧲 МРТ ga qanday tayyorlanish kerak?", "Maxsus tayyorgarlik kerak emas. Metall buyumlarni yechib qo'ying. Kontrastli МРТ da — 4–6 soat oldin ovqat emas."),
        ("💊 Operatsiyasiz davolanish bormi?", "q_no_surgery"),
        ("🚻 Erkaklar va ayollar palatalari?", "Ha, palatalar alohida. Ayollar va erkaklar turli xonalarda joylashadi."),
        ("🍽 Ovqatlanish bormi?", "q_diet_food"),
        ("🕐 Ish vaqti?", "q_work_hours"),
    ],
    "kz": [
        ("📅 Емдеу мерзімі?", (
            "📅 *Емдеу неше күн?*\n\n"
            "Құрметті науқас! Орталығымызда емдеу мерзімі әр ағзаның жағдайына байланысты дәрігер тарапынан *жеке* белгіленеді:\n\n"
            "• 🩺 *Емдеу курстары:* Ауру деңгейіне байланысты *18, 21 немесе 24 күн* созылады.\n"
            "• 🛡 *Профилактика:* Ауруды болдырмау үшін кемінде *12–14 күн* ұсынылады.\n"
            "• ⚠️ *Ең аз мерзім:* Нәтиже сезілуі үшін емдеу *10 күннен кем болмауы* маңызды.\n\n"
            "💡 *Біздің емдеу философиямыз:*\n"
            "«Эргаш ота» орталығы тек ауру белгілерін уақытша басумен шектелмейді. Біздің басты мақсатымыз — *ауру себептерін анықтап, оны түбірімен жою!*"
        )),
        ("💰 Баға қалай қалыптасады?", "Баға — 1 күн/1 адам үшін. Кіреді: тұру, емдеу, физиотерапия, УДЗ, анализдер, МРТ 1.5Т немесе МСКТ."),
        ("🧲 МРТ-ге қалай дайындалу керек?", "Арнайы дайындық қажет емес. Металл заттарды шешіңіз."),
        ("💊 Операциясыз емдеу бар ма?", "q_no_surgery"),
        ("🚻 Ер/әйел палаталары?", "Иә, палаталар бөлек. Әйелдер мен ерлер әртүрлі палаталарда орналасады."),
        ("🍽 Тамақтану бар ма?", "q_diet_food"),
        ("🕐 Жұмыс уақыты?", "q_work_hours"),
    ],
}

# ─── BOOKING SERVICES ─────────────────────────────────────────────────────────
DIAG_SERVICES = {
    "ru": ["🧲 МРТ 3Т", "🧲 МРТ 1.5Т", "🖥 МСКТ 256", "🖥 МСКТ 128", "📡 УЗИ", "🩺 Маммография", "🔬 Лаборатория", "🫀 Фибросканирование"],
    "uz": ["🧲 МРТ 3Т", "🧲 МРТ 1.5Т", "🖥 МСКТ 256", "🖥 МСКТ 128", "📡 УЗИ", "🩺 Mammografiya", "🔬 Laboratoriya", "🫀 Fibroskan"],
    "kz": ["🧲 МРТ 3Т", "🧲 МРТ 1.5Т", "🖥 МСКТ 256", "🖥 МСКТ 128", "📡 УДЗ", "🩺 Маммография", "🔬 Зертхана", "🫀 Фибросканерлеу"],
}

# ─── FAQ KEYBOARD ──────────────────────────────────────────────────────────────

def faq_keyboard(lang):
    faqs = FAQ_DATA.get(lang, FAQ_DATA["ru"])
    kelish_label = {
        "ru": "📅 Когда можно приехать? (Бронирование)",
        "uz": "📅 Qachon kelish mumkin? (Bron qilish)",
        "kz": "📅 Қашан келуге болады? (Брондау)",
    }[lang]
    buttons = [[InlineKeyboardButton(kelish_label, callback_data="m_kelish_tartibi")]]
    for i, (q, a) in enumerate(faqs):
        cb = a if isinstance(a, str) and a.startswith("q_") else f"faq_{i}"
        buttons.append([InlineKeyboardButton(q, callback_data=cb)])
    transfer_label = {
        "ru": "🚗 Добраться до клиники",
        "uz": "🚗 Klinikaga yetib olish",
        "kz": "🚗 Клиникаға жету",
    }[lang]
    operator_label = {
        "ru": "📞 Оператор",
        "uz": "📞 Operator",
        "kz": "📞 Оператор",
    }[lang]
    back = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
    buttons.append([InlineKeyboardButton(transfer_label, callback_data="menu_transfer")])
    buttons.append([InlineKeyboardButton(operator_label, callback_data="menu_operator")])
    buttons.append([InlineKeyboardButton(back, callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)


def booking_type_keyboard(lang):
    labels = {
        "ru": ("🏥 Стационарное лечение", "🔬 Диагностика", "⬅️ Назад"),
        "uz": ("🏥 Statsionar davolanish", "🔬 Diagnostika", "⬅️ Orqaga"),
        "kz": ("🏥 Стационарлық емдеу", "🔬 Диагностика", "⬅️ Артқа"),
    }[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(labels[0], callback_data="book_statsionar")],
        [InlineKeyboardButton(labels[1], callback_data="book_diagnostika")],
        [InlineKeyboardButton(labels[2], callback_data="back_main")],
    ])


def diag_service_keyboard(lang):
    services = DIAG_SERVICES.get(lang, DIAG_SERVICES["ru"])
    buttons = []
    for i, s in enumerate(services):
        buttons.append([InlineKeyboardButton(s, callback_data=f"diag_book_{i}")])
    back = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
    buttons.append([InlineKeyboardButton(back, callback_data="menu_booking")])
    return InlineKeyboardMarkup(buttons)


def confirm_keyboard(lang):
    labels = {
        "ru": ("✅ Подтвердить", "❌ Отменить"),
        "uz": ("✅ Tasdiqlash", "❌ Bekor qilish"),
        "kz": ("✅ Растау", "❌ Болдырмау"),
    }[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(labels[0], callback_data="book_confirm")],
        [InlineKeyboardButton(labels[1], callback_data="back_main")],
    ])


# ─── BOOKING HANDLER ──────────────────────────────────────────────────────────

OY_NOMLARI = {
    "yanvar": 1, "fevral": 2, "mart": 3, "aprel": 4, "may": 5, "iyun": 6,
    "iyul": 7, "avgust": 8, "sentyabr": 9, "oktyabr": 10, "noyabr": 11, "dekabr": 12,
    "январ": 1, "феврал": 2, "март": 3, "апрел": 4, "май": 5, "июн": 6,
    "июл": 7, "август": 8, "сентябр": 9, "октябр": 10, "ноябр": 11, "декабр": 12,
}


def normalize_sana_to_iso(sana_text: str):
    """Bemor yozgan erkin sanani YYYY-MM-DD formatiga o'tkazadi. Aniqlab bo'lmasa None."""
    if not sana_text:
        return None
    text = sana_text.strip().lower()
    bugun = datetime.datetime.now(TASHKENT_TZ).date()

    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", text)
    if m:
        y, mo, d = map(int, m.groups())
        try:
            return datetime.date(y, mo, d).isoformat()
        except ValueError:
            return None

    m = re.match(r"^(\d{1,2})[./](\d{1,2})(?:[./](\d{4}))?$", text)
    if m:
        d, mo, y = m.groups()
        d, mo = int(d), int(mo)
        y_given = bool(y)
        y = int(y) if y else bugun.year
        try:
            natija = datetime.date(y, mo, d)
            if not y_given and natija < bugun:
                natija = datetime.date(y + 1, mo, d)
            return natija.isoformat()
        except ValueError:
            return None

    m = re.match(r"^(\d{1,2})\s+([a-zа-яʻ']+)", text)
    if m:
        d = int(m.group(1))
        for nom, raqam in OY_NOMLARI.items():
            if m.group(2).startswith(nom):
                try:
                    natija = datetime.date(bugun.year, raqam, d)
                    if natija < bugun:
                        natija = datetime.date(bugun.year + 1, raqam, d)
                    return natija.isoformat()
                except ValueError:
                    return None

    # Faqat kun raqami (oy/yil ko'rsatilmagan) — masalan "25", "25.", "25-kun"
    # Joriy oyda shu kun bugundan keyin bo'lsa — joriy oy, aks holda keyingi oy deb hisoblanadi
    m = re.match(r"^(\d{1,2})\s*[.\-]?\s*(?:kun|кун)?$", text)
    if m:
        d = int(m.group(1))
        if 1 <= d <= 31:
            for oy_offset in (0, 1, 2):
                yil, oy = bugun.year, bugun.month + oy_offset
                if oy > 12:
                    yil += 1
                    oy -= 12
                try:
                    natija = datetime.date(yil, oy, d)
                    if natija >= bugun:
                        return natija.isoformat()
                except ValueError:
                    continue
    return None


def save_statsionar_lid(name: str, phone: str, sana_text: str, kasallik: str = "", xona: str = ""):
    """Tasdiqlangan statsionar lidni data.json ichiga, kelish_sanasi alohida ustun bilan saqlaydi."""
    d = load_data()
    lid = {
        "ism": name,
        "telefon": phone,
        "kasallik": kasallik or "—",
        "xona": xona or "—",
        "sana_matn": sana_text,
        "kelish_sanasi": normalize_sana_to_iso(sana_text),
        "holat": "tasdiqlangan",
        "yaratilgan": datetime.datetime.now(TASHKENT_TZ).strftime("%Y-%m-%d %H:%M:%S"),
    }
    d.setdefault("statsionar_lidlar", []).append(lid)
    save_data(d)


def get_lidlar_by_sana(kelish_sanasi_iso: str) -> list:
    """Berilgan sanaga (YYYY-MM-DD) teng, holati 'tasdiqlangan' bo'lgan barcha lidlarni qaytaradi."""
    d = load_data()
    return [
        lid for lid in d.get("statsionar_lidlar", [])
        if lid.get("kelish_sanasi") == kelish_sanasi_iso
        and lid.get("holat") == "tasdiqlangan"
    ]


async def lidlar_fix_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/lidlar_fix — faqat admin: barcha saqlangan lidlarning sana_matn'ini qayta tahlil qilib,
    kelish_sanasi (ISO) qiymatini yangilaydi (parser yaxshilangandan keyin eski None'larni tuzatish uchun)."""
    if update.effective_user.id != ADMIN_ID:
        return
    d = load_data()
    lidlar = d.get("statsionar_lidlar", [])
    if not lidlar:
        await update.message.reply_text("📭 statsionar_lidlar ro'yxati bo'sh.")
        return
    tuzatildi = 0
    for lid in lidlar:
        yangi_iso = normalize_sana_to_iso(lid.get("sana_matn", ""))
        if yangi_iso and yangi_iso != lid.get("kelish_sanasi"):
            lid["kelish_sanasi"] = yangi_iso
            tuzatildi += 1
    save_data(d)
    await update.message.reply_text(f"✅ Tekshirildi: {len(lidlar)} ta yozuv. Tuzatildi: {tuzatildi} ta.")


async def lid_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/lid_add Ism|Telefon|YYYY-MM-DD|Kasallik|Xona — faqat admin: eski/qo'lda lidni tizimga qo'shadi.
    Kasallik va Xona ixtiyoriy — bo'lmasa '—' qo'yiladi."""
    if update.effective_user.id != ADMIN_ID:
        return
    raw = update.message.text.replace("/lid_add", "", 1).strip()
    if not raw:
        await update.message.reply_text(
            "Format: /lid_add Ism Familiya|+998901234567|2026-06-25|Kasallik nomi|Xona turi\n\n"
            "Kasallik va Xona ixtiyoriy, qoldirib ketsa bo'ladi:\n"
            "/lid_add Ism Familiya|+998901234567|2026-06-25"
        )
        return
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) < 3:
        await update.message.reply_text("❌ Kamida Ism|Telefon|Sana (YYYY-MM-DD) kerak.")
        return
    name, phone, sana_iso = parts[0], parts[1], parts[2]
    kasallik = parts[3] if len(parts) > 3 else ""
    xona = parts[4] if len(parts) > 4 else ""
    try:
        datetime.date.fromisoformat(sana_iso)
    except ValueError:
        await update.message.reply_text(f"❌ Sana formati noto'g'ri: '{sana_iso}'. To'g'ri format: YYYY-MM-DD (masalan 2026-06-25)")
        return

    d = load_data()
    lid = {
        "ism": name,
        "telefon": phone,
        "kasallik": kasallik or "—",
        "xona": xona or "—",
        "sana_matn": sana_iso,
        "kelish_sanasi": sana_iso,
        "holat": "tasdiqlangan",
        "yaratilgan": datetime.datetime.now(TASHKENT_TZ).strftime("%Y-%m-%d %H:%M:%S"),
    }
    d.setdefault("statsionar_lidlar", []).append(lid)
    save_data(d)
    await update.message.reply_text(f"✅ Qo'shildi: {name} | {sana_iso}")


async def lidlar_debug_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/lidlar_debug — faqat admin: statsionar_lidlar ro'yxatidagi BARCHA yozuvlarni xom holda ko'rsatadi (sana formatini tekshirish uchun)."""
    if update.effective_user.id != ADMIN_ID:
        return
    d = load_data()
    lidlar = d.get("statsionar_lidlar", [])
    if not lidlar:
        await update.message.reply_text("📭 statsionar_lidlar ro'yxati hozircha bo'sh (hech narsa saqlanmagan).")
        return
    lines = [f"📋 Jami: {len(lidlar)} ta yozuv\n"]
    for i, lid in enumerate(lidlar[-20:], 1):  # oxirgi 20 tasi
        lines.append(
            f"{i}. {lid.get('ism', '—')} | "
            f"sana_matn: '{lid.get('sana_matn', '—')}' | "
            f"kelish_sanasi (ISO): {lid.get('kelish_sanasi', '—')} | "
            f"holat: {lid.get('holat', '—')}"
        )
    await update.message.reply_text("\n".join(lines))


async def ertaga_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ertaga — faqat admin: ertaga keladigan tasdiqlangan bemorlar ro'yxati."""
    if update.effective_user.id != ADMIN_ID:
        return

    ertangi_sana = datetime.datetime.now(TASHKENT_TZ).date() + datetime.timedelta(days=1)
    bemorlar = get_lidlar_by_sana(ertangi_sana.isoformat())

    if not bemorlar:
        await update.message.reply_text(
            f"📅 {ertangi_sana.strftime('%d.%m.%Y')}\n\n🟡 Ertaga keladigan bemorlar yo'q."
        )
        return

    lines = [f"📅 *{ertangi_sana.strftime('%d.%m.%Y')} — Ertaga keladigan bemorlar ({len(bemorlar)} ta):*\n"]
    for i, b in enumerate(bemorlar, 1):
        lines.append(
            f"{i}. 👤 {b.get('ism', '—')}\n"
            f"   📞 {b.get('telefon', '—')}\n"
            f"   🩺 {b.get('kasallik', '—')}\n"
            f"   🛏 {b.get('xona', '—')}\n"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def send_lid(context, channel_id, text):
    try:
        await context.bot.send_message(chat_id=channel_id, text=text)
        logger.info(f"Lid yuborildi: {channel_id}")
    except Exception as e:
        logger.error(f"Lid yuborish xatosi (channel={channel_id}): {e}")
        try:
            ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
            if ADMIN_ID:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"⚠️ LID YUBORILMADI!\nKanal: {channel_id}\nXato: {e}\n\n{text[:300]}"
                )
        except Exception:
            pass


async def handle_booking_callbacks(query, context, data, lang, chat_id):
    d = load_data()
    phone = d["contacts"]["phone1"]

    if data == "menu_booking":
        context.user_data["booking"] = {}
        context.user_data["booking_step"] = None
        context.user_data["booking_type"] = None
        title = {
            "ru": "📅 *Запись*\n\nВыберите тип:",
            "uz": "📅 *Yozilish*\n\nTurini tanlang:",
            "kz": "📅 *Жазылу*\n\nТүрін таңдаңыз:",
        }[lang]
        await query.edit_message_text(title, parse_mode="Markdown",
                                      reply_markup=booking_type_keyboard(lang))
    elif data == "calc_book_statsionar":
        # Calculator dan keyin yozilish — xona so'ralmaydi, faqat ism/sana/kishi/telefon
        cit = context.user_data.get("calc_cit", "uz")
        age = context.user_data.get("calc_age", "adult")
        idx = context.user_data.get("calc_room_idx", 0)
        days = context.user_data.get("calc_days", 0)
        d = load_data()
        rooms = d["rooms_uz"] if cit == "uz" else d["rooms_foreign"]
        room = rooms[idx] if idx < len(rooms) else {}
        price_str = room.get("adult" if age == "adult" else "child", "0")
        price_num = int(price_str.replace(" ", "").replace("\u00a0", ""))
        total = price_num * days if days else 0

        def fmt(n):
            return f"{n:,}".replace(",", " ")

        narx_word = {"ru": "сум", "uz": "so'm", "kz": "сум"}[lang]
        cit_label = {
            "ru": {"uz": "Граждане Узбекистана", "foreign": "Иностранные граждане"}[cit],
            "uz": {"uz": "O'zbekiston fuqarolari", "foreign": "Chet el fuqarolari"}[cit],
            "kz": {"uz": "Өзбекстан азаматтары", "foreign": "Шетел азаматтары"}[cit],
        }[lang]
        age_label = {
            "ru": {"adult": "Взрослые", "child": "Дети (до 10 лет)"}[age],
            "uz": {"adult": "Kattalar", "child": "Bolalar (10 yoshgacha)"}[age],
            "kz": {"adult": "Ересектер", "child": "Балалар (10 жасқа дейін)"}[age],
        }[lang]

        # Calc ma'lumotlarini booking session ga saqlash
        context.user_data["booking"] = {
            "from_calc": True,
            "calc_room": room.get("name", "—"),
            "calc_cit": cit_label,
            "calc_age": age_label,
            "calc_price": f"{fmt(price_num)} {narx_word}",
            "calc_days": str(days) if days else "—",
            "calc_people": str(context.user_data.get("calc_people", 1)),
            "calc_total": f"{fmt(price_num * days * context.user_data.get('calc_people', 1))} {narx_word}" if days else "—",
        }
        context.user_data["booking_type"] = "statsionar"
        context.user_data["booking_step"] = "name"

        ask = {
            "ru": (
                f"🏨 *Запись на лечение*\n"
                f"🛏 Палата: *{room.get('name', '—')}*\n"
                f"💰 1 день: *{fmt(price_num)} {narx_word}*\n\n"
                f"📝 Шаг 1/4\nНапишите ваше *Имя и Фамилию*:"
            ),
            "uz": (
                f"🏨 *Davolanishga yozilish*\n"
                f"🛏 Xona: *{room.get('name', '—')}*\n"
                f"💰 1 kun: *{fmt(price_num)} {narx_word}*\n\n"
                f"📝 1/4 qadam\n*Ism va Familiyangizni* yozing:"
            ),
            "kz": (
                f"🏨 *Емдеуге жазылу*\n"
                f"🛏 Палата: *{room.get('name', '—')}*\n"
                f"💰 1 күн: *{fmt(price_num)} {narx_word}*\n\n"
                f"📝 1/4 қадам\n*Аты-жөніңізді* жазыңыз:"
            ),
        }[lang]
        await query.edit_message_text(ask, parse_mode="Markdown")

    elif data == "book_statsionar":
        context.user_data["booking"] = {}
        context.user_data["booking_type"] = "statsionar"
        context.user_data["booking_step"] = "name"
        ask = {
            "ru": "🏥 *Запись на стационарное лечение*\n\n📝 Шаг 1/5\nНапишите ваше *Имя и Фамилию*:",
            "uz": "🏥 *Statsionar davolanishga yozilish*\n\n📝 1/5 qadam\n*Ism va Familiyangizni* yozing:",
            "kz": "🏥 *Стационарлық емдеуге жазылу*\n\n📝 1/5 қадам\n*Аты-жөніңізді* жазыңыз:",
        }[lang]
        await query.edit_message_text(ask, parse_mode="Markdown")

    elif data == "book_diagnostika":
        context.user_data["booking"] = {}
        context.user_data["booking_type"] = "diagnostika"
        title = {
            "ru": "🔬 *Запись на диагностику*\n\nВыберите вид обследования:",
            "uz": "🔬 *Diagnostikaga yozilish*\n\nTekshiruv turini tanlang:",
            "kz": "🔬 *Диагностикаға жазылу*\n\nТексеру түрін таңдаңыз:",
        }[lang]
        await query.edit_message_text(title, parse_mode="Markdown",
                                      reply_markup=diag_service_keyboard(lang))

    elif data.startswith("diag_book_"):
        idx = int(data.replace("diag_book_", ""))
        services = DIAG_SERVICES.get(lang, DIAG_SERVICES["ru"])
        service = services[idx]

        fibroskan_names = ["🫀 Фибросканирование", "🫀 Fibroskan", "🫀 Фибросканерлеу"]
        if service in fibroskan_names:
            # Fibroskan: narx ma'lumoti + to'g'ridan-to'g'ri ism yozishga o'tish
            context.user_data.setdefault("booking", {})["service"] = service
            context.user_data["booking_type"] = "diagnostika"
            context.user_data["booking_step"] = "name"
            ask = {
                "ru": (
                    "🫀 *Фибросканирование печени*\n\n"
                    "💰 *Цены:*\n"
                    "• Стандарт: 150 000 сум\n"
                    "• С консультацией врача: 200 000 сум\n\n"
                    "⏱ Длительность: 15–20 минут\n"
                    "📋 Подготовка: натощак (4–6 часов)\n\n"
                    "📝 Шаг 1/3\nНапишите ваше *Имя и Фамилию*:"
                ),
                "uz": (
                    "🫀 *Jigar fibroskan tekshiruvi*\n\n"
                    "💰 *Narxlar:*\n"
                    "• Standart: 150 000 so'm\n"
                    "• Shifokor maslahati bilan: 200 000 so'm\n\n"
                    "⏱ Davomiyligi: 15–20 daqiqa\n"
                    "📋 Tayyorgarlik: och qorin (4–6 soat)\n\n"
                    "📝 1/3 qadam\n*Ism va Familiyangizni* yozing:"
                ),
                "kz": (
                    "🫀 *Бауырды фибросканерлеу*\n\n"
                    "💰 *Бағалар:*\n"
                    "• Стандарт: 150 000 сум\n"
                    "• Дәрігер кеңесімен: 200 000 сум\n\n"
                    "⏱ Ұзақтығы: 15–20 минут\n"
                    "📋 Дайындық: аш қарын (4–6 сағат)\n\n"
                    "📝 1/3 қадам\n*Аты-жөніңізді* жазыңыз:"
                ),
            }[lang]
        else:
            # Boshqa xizmatlar
            context.user_data.setdefault("booking", {})["service"] = service
            context.user_data["booking_type"] = "diagnostika"
            context.user_data["booking_step"] = "name"
            ask = {
                "ru": f"✅ Услуга: *{service}*\n\n📝 Шаг 1/3\nНапишите ваше *Имя и Фамилию*:",
                "uz": f"✅ Xizmat: *{service}*\n\n📝 1/3 qadam\n*Ism va Familiyangizni* yozing:",
                "kz": f"✅ Қызмет: *{service}*\n\n📝 1/3 қадам\n*Аты-жөніңізді* жазыңыз:",
            }[lang]

        back_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang],
                callback_data="book_diagnostika"
            )]
        ])
        await query.edit_message_text(ask, parse_mode="Markdown", reply_markup=back_kb)

    elif data == "book_confirm":
        booking = context.user_data.get("booking", {})
        btype = context.user_data.get("booking_type", "statsionar")
        user = query.from_user
        username = f"@{user.username}" if user.username else "—"

        if btype == "statsionar":
            name = booking.get("name", "—")
            sana = booking.get("sana", "—")
            kishi = booking.get("kishi", "—")
            phone_num = booking.get("phone", "—")
            xona = booking.get("xona", "—")
            from_calc = booking.get("from_calc", False)

            success = {
                "ru": f"🎉 *Заявка принята!*\n\n👤 {name}\n📅 Дата: {sana}\n👥 Человек: {kishi}\n📞 {phone_num}\n🛏 Номер: {booking.get('calc_room', xona)}\n\nОператор свяжется с вами.\n📞 {phone}",
                "uz": f"🎉 *Ariza qabul qilindi!*\n\n👤 {name}\n📅 Sana: {sana}\n👥 Kishi: {kishi}\n📞 {phone_num}\n🛏 Xona: {booking.get('calc_room', xona)}\n\nOperator siz bilan bog'lanadi.\n📞 {phone}",
                "kz": f"🎉 *Өтінім қабылданды!*\n\n👤 {name}\n📅 Күні: {sana}\n👥 Адам: {kishi}\n📞 {phone_num}\n🛏 Бөлме: {booking.get('calc_room', xona)}\n\nОператор байланысады.\n📞 {phone}",
            }[lang]
            try:
                await query.edit_message_text(success, parse_mode="Markdown",
                                              reply_markup=back_keyboard(lang))
            except Exception:
                await context.bot.send_message(chat_id=chat_id, text=success,
                                               parse_mode="Markdown", reply_markup=back_keyboard(lang))

            if from_calc:
                lid = (
                    f"🏥 *STATSIONAR LID (Kalkulyator orqali)*\n\n"
                    f"👤 Ism: {name}\n"
                    f"📞 Telefon: {phone_num}\n"
                    f"📅 Kelish sanasi: {sana}\n"
                    f"👥 Odam soni: {booking.get('calc_people', '—')}\n\n"
                    f"🇺🇿 Fuqarolik: {booking.get('calc_cit', '—')}\n"
                    f"👤 Yosh toifasi: {booking.get('calc_age', '—')}\n"
                    f"🏨 Tanlangan to'lov turi: {booking.get('calc_room', '—')}\n"
                    f"💰 1 kunlik narx: {booking.get('calc_price', '—')}\n"
                    f"📅 Davolanish muddati: {booking.get('calc_days', '—')} kun\n"
                    f"✅ Umumiy summa: {booking.get('calc_total', '—')}\n\n"
                    f"💬 Telegram: {username}\n"
                    f"🆔 uid:{user.id}\n"
                    f"🌐 Til: {lang.upper()}\n\n"
                    f"📌 Bemor narx kalkulyatori orqali xona/to'lov turini tanlab, shu asosida qabulga yozildi.\n\n"
                    f"🟢 QO'NG'IROQ QILING!"
                )
            else:
                lid = (
                    f"🏥 *STATSIONAR LID*\n\n"
                    f"👤 Ism: {name}\n"
                    f"📅 Kelish sanasi: {sana}\n"
                    f"👥 Kishi soni: {kishi}\n"
                    f"📞 Telefon: {phone_num}\n"
                    f"🛏 Xona turi: {xona}\n"
                    f"💬 Telegram: {username}\n"
                    f"🆔 uid:{user.id}\n"
                    f"🌐 Til: {lang.upper()}\n\n"
                    f"🟢 QO'NG'IROQ QILING!"
                )
            await send_lid(context, STATSIONAR_CHANNEL, lid)
            save_statsionar_lid(
                name=name,
                phone=phone_num,
                sana_text=sana,
                kasallik="",
                xona=booking.get("calc_room", "—") if from_calc else xona,
            )

        else:  # diagnostika
            name = booking.get("name", "—")
            phone_num = booking.get("phone", "—")
            service = booking.get("service", "—")

            success = {
                "ru": f"🎉 *Заявка принята!*\n\n👤 {name}\n🔬 Услуга: {service}\n📞 {phone_num}\n\nОператор свяжется с вами.\n📞 {phone}",
                "uz": f"🎉 *Ariza qabul qilindi!*\n\n👤 {name}\n🔬 Xizmat: {service}\n📞 {phone_num}\n\nOperator siz bilan bog'lanadi.\n📞 {phone}",
                "kz": f"🎉 *Өтінім қабылданды!*\n\n👤 {name}\n🔬 Қызмет: {service}\n📞 {phone_num}\n\nОператор байланысады.\n📞 {phone}",
            }[lang]
            try:
                await query.edit_message_text(success, parse_mode="Markdown",
                                              reply_markup=back_keyboard(lang))
            except Exception:
                await context.bot.send_message(chat_id=chat_id, text=success,
                                               parse_mode="Markdown", reply_markup=back_keyboard(lang))

            lid = (
                f"🔬 *DIAGNOSTIKA LID*\n\n"
                f"👤 Ism: {name}\n"
                f"🔬 Xizmat: {service}\n"
                f"📞 Telefon: {phone_num}\n"
                f"💬 Telegram: {username}\n"
                f"🆔 uid:{user.id}\n"
                f"🌐 Til: {lang.upper()}\n\n"
                f"🟢 QO'NG'IROQ QILING!"
            )
            await send_lid(context, DIAGNOSTIKA_CHANNEL, lid)

        context.user_data["booking"] = {}
        context.user_data["booking_step"] = None
        context.user_data["booking_type"] = None

    elif data == "book_confirm_transfer":
        pass  # placeholder

    # Transfer va excursion confirm — alohida handle qilinadi (unknown handler orqali keladi)
        booking = context.user_data.get("booking", {})
        user = query.from_user
        username = f"@{user.username}" if user.username else "—"
        d = load_data()
        phone = d["contacts"]["phone1"]
        success = {
            "ru": f"🎉 *Заявка принята!*\n\n📍 Откуда: {booking.get('from')}\n📅 Дата: {booking.get('sana')}\n👥 Человек: {booking.get('kishi')}\n📞 {booking.get('phone')}\n\nОператор свяжется с вами.\n📞 {phone}",
            "uz": f"🎉 *Ariza qabul qilindi!*\n\n📍 Qayerdan: {booking.get('from')}\n📅 Sana: {booking.get('sana')}\n👥 Kishi: {booking.get('kishi')}\n📞 {booking.get('phone')}\n\nOperator siz bilan bog'lanadi.\n📞 {phone}",
            "kz": f"🎉 *Өтінім қабылданды!*\n\n📍 Қайдан: {booking.get('from')}\n📅 Күні: {booking.get('sana')}\n👥 Адам: {booking.get('kishi')}\n📞 {booking.get('phone')}\n\nОператор байланысады.\n📞 {phone}",
        }[lang]
        await query.edit_message_text(success, parse_mode="Markdown", reply_markup=back_keyboard(lang))
        lid = (f"🚗 *TRANSFER LID*\n\n"
               f"📍 Qayerdan: {booking.get('from')}\n"
               f"📅 Sana: {booking.get('sana')}\n"
               f"👥 Kishi: {booking.get('kishi')}\n"
               f"📞 Telefon: {booking.get('phone')}\n"
               f"💬 Telegram: {username}\n"
               f"🌐 Til: {lang.upper()}\n"
               f"🔧 Type: {btype}\n\n"
               f"🟢 QO'NG'IROQ QILING!")
        await send_lid(context, TRANSFER_CHANNEL, lid)
        context.user_data["booking"] = {}
        context.user_data["booking_step"] = None
        context.user_data["booking_type"] = None

    elif btype == "excursion":
        booking = context.user_data.get("booking", {})
        user = query.from_user
        username = f"@{user.username}" if user.username else "—"
        d = load_data()
        phone = d["contacts"]["phone1"]
        success = {
            "ru": f"🎉 *Заявка принята!*\n\n🕌 {booking.get('city')}\n📅 Дата: {booking.get('sana')}\n👥 Человек: {booking.get('kishi')}\n📞 {booking.get('phone')}\n\nОператор свяжется с вами.\n📞 {phone}",
            "uz": f"🎉 *Ariza qabul qilindi!*\n\n🕌 {booking.get('city')}\n📅 Sana: {booking.get('sana')}\n👥 Kishi: {booking.get('kishi')}\n📞 {booking.get('phone')}\n\nOperator siz bilan bog'lanadi.\n📞 {phone}",
            "kz": f"🎉 *Өтінім қабылданды!*\n\n🕌 {booking.get('city')}\n📅 Күні: {booking.get('sana')}\n👥 Адам: {booking.get('kishi')}\n📞 {booking.get('phone')}\n\nОператор байланысады.\n📞 {phone}",
        }[lang]
        await query.edit_message_text(success, parse_mode="Markdown", reply_markup=back_keyboard(lang))
        lid = (f"🕌 *EKSKURSIYA LID*\n\n"
               f"🏛 Yo'nalish: {booking.get('city')}\n"
               f"📅 Sana: {booking.get('sana')}\n"
               f"👥 Kishi: {booking.get('kishi')}\n"
               f"📞 Telefon: {booking.get('phone')}\n"
               f"💬 Telegram: {username}\n"
               f"🌐 Til: {lang.upper()}\n\n"
               f"🟢 QO'NG'IROQ QILING!")
        await send_lid(context, TRANSFER_CHANNEL, lid)
        context.user_data["booking"] = {}
        context.user_data["booking_step"] = None
        context.user_data["booking_type"] = None




async def handle_faq_callbacks(query, context, data, lang):
    chat_id = query.message.chat_id
    faqs = FAQ_DATA.get(lang, FAQ_DATA["ru"])

    if data == "m_kelish_tartibi":
        REGISTRATION_PHOTO_ID = d.get("registration_photo_id", "") if (d := load_data()) else ""
        text = {
            "ru": (
                "📅 <b>Порядок приезда и бронирования мест в нашем центре</b>\n\n"
                "Если вы планируете приехать в наш центр для восстановления здоровья, ознакомьтесь со следующей информацией:\n\n"
                "✅ <b>Свободный график приезда:</b> Мы не назначаем пациентам фиксированную дату приезда. Вы можете <b>выбрать любой удобный для вас день</b> и покупать билеты на эту дату. В нашем центре места есть всегда — по прибытии вас сразу же оформят и разместят.\n\n"
                "⏱ <b>Режим работы:</b>\n"
                "• <b>Понедельник – Суббота:</b> Полноценный приём врачей и все лечебные процедуры.\n"
                "• <b>Воскресенье:</b> Работает только отдел регистрации и размещения. Пациенты регистрируются и заселяются в палаты (лечение начинается с понедельника).\n\n"
                "🧳 <b>Что взять с собой:</b> Паспорт и медицинские выписки/анализы (если имеются).\n\n"
                "<i>Ждём вас в любой удобный для вас день! Счастливого пути.</i>"
            ),
            "uz": (
                "📅 <b>Markazimizga kelish va joy band qilish (bron) tartibi</b>\n\n"
                "Sog'ligingizni tiklash uchun markazimizga kelishni rejalashtirayotgan bo'lsangiz, quyidagi ma'lumotlar bilan tanishib chiqing:\n\n"
                "✅ <b>Erkin kelish tartibi:</b> Biz bemorlarimiz uchun aniq kelish kunini belgilamaymiz. Siz o'zingizga qulay bo'lgan <b>xohlagan sanani tanlab kelaverishingiz mumkin</b>. Markazimizda joylar doimiy ravishda mavjud — kelgan kuningizda sizga darhol joy qilib beriladi.\n\n"
                "⏱ <b>Ish tartibi:</b>\n"
                "• <b>Dushanba – Shanba:</b> Shifokorlar qabuli va barcha muolajalar to'liq olib boriladi.\n"
                "• <b>Yakshanba:</b> Faqat Registratsiya bo'limi ishlaydi. Yakshanba kuni kelgan bemorlar ro'yxatga olinib, xonalarga joylashtiriladi (muolajalar dushanbadan boshlanadi).\n\n"
                "🧳 <b>Kelishda o'zingiz bilan oling:</b> Pasport/ID karta va tibbiy ko'rik tashxislari (agar bo'lsa).\n\n"
                "<i>Sizga qulay sanada markazimizda kutib qolamiz! Safaringiz bexatar bo'lsin.</i>"
            ),
            "kz": (
                "📅 <b>Орталығымызға келу және орын брондау тәртібі</b>\n\n"
                "Денсаулығыңызды түзету үшін орталығымызға келуді жоспарлап отырсаңыз, келесі ақпаратпен танысып шығыңыз:\n\n"
                "✅ <b>Еркін келу тәртібі:</b> Біз емделушілер үшін нақты келу күнін белгілемейміз. Сіз өзіңізге ыңғайлы <b>кез келген күнді таңдап келе бере аласыз</b>. Орталығымызда орындар әрдайым дайын — келген күні сізді бірден орналастырамыз.\n\n"
                "⏱ <b>Жұмыс кестесі:</b>\n"
                "• <b>Дүйсенбі – Сенбі:</b> Дәрігерлер қабылдауы және барлық емдік шаралар толықтай жүргізіледі.\n"
                "• <b>Жексенбі:</b> Тек тіркеу бөлімі жұмыс істейді. Жексенбі күні келген емделушілер тіркеліп, палаталарға орналастырылады (емдеу дүйсенбіден басталады).\n\n"
                "🧳 <b>Өзіңізбен ала келіңіз:</b> Жеке куәлік (паспорт) және медициналық тексеру қорытындылары (егер бар болса).\n\n"
                "<i>Өзіңізге ыңғайлы кез келген күні орталығымызда күтеміз! Жолыңыз болсын.</i>"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_delete_registration")]])
        if REGISTRATION_PHOTO_ID:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=REGISTRATION_PHOTO_ID,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

    elif data == "back_delete_registration":
        try:
            await query.message.delete()
        except Exception:
            pass
        title = {
            "ru": "❓ *Часто задаваемые вопросы*\n\nВыберите вопрос:",
            "uz": "❓ *Ko'p so'raladigan savollar*\n\nSavolni tanlang:",
            "kz": "❓ *Жиі қойылатын сұрақтар*\n\nСұрақты таңдаңыз:",
        }[lang]
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="Markdown",
                                       reply_markup=faq_keyboard(lang))

    elif data == "q_work_hours":
        d = load_data()
        WORK_HOURS_PHOTO_ID = d.get("work_hours_photo_id", "")
        text = {
            "ru": (
                "⏱ <b>Режим работы и часы приёма нашей клиники</b>\n\n"
                "Наш центр работает каждый день без перерыва, создавая максимальное удобство для пациентов:\n\n"
                "📆 <b>Понедельник – Суббота (Основные рабочие дни):</b>\n"
                "• <b>Часы работы:</b> с 08:00 до 18:00.\n"
                "• В эти дни проводятся осмотры врачей, диагностика и все виды процедур в полном объёме.\n\n"
                "🔴 <b>Воскресенье:</b> Несмотря на то что воскресенье является выходным днём для наших врачей, для пациентов, приезжающих из дальних регионов и из-за рубежа, <b>отдел регистрации работает</b>.\n"
                "• Вновь прибывшие пациенты встречаются, регистрируются и размещаются в палатах.\n"
                "• ✨ <b>Важное преимущество:</b> Чтобы не терять время, для новых пациентов, приехавших в воскресенье, <b>проводятся процедуры первого дня!</b>\n\n"
                "<i>Приезжайте в любой удобный для вас день — мы всегда готовы помочь вам выздороветь!</i>"
            ),
            "uz": (
                "⏱ <b>Klinikamizning ish tartibi va qabul vaqtlari</b>\n\n"
                "Markazimiz bemorlarga qulaylik yaratish maqsadida haftaning har kuni uzluksiz xizmat ko'rsatadi:\n\n"
                "📆 <b>Dushanba – Shanba (Asosiy ish kunlari):</b>\n"
                "• <b>Ish vaqti:</b> 08:00 dan 18:00 gacha.\n"
                "• Ushbu kunlarda shifokorlar ko'rigi, diagnostika va barcha turdagi muolajalar to'liq hajmda olib boriladi.\n\n"
                "🔴 <b>Yakshanba:</b> Yakshanba shifokorlarimiz uchun dam olish kuni bo'lishiga qaramay, uzoq viloyatlar va chet eldan keladigan bemorlarimiz uchun <b>Registratsiya bo'limi ishlaydi</b>.\n"
                "• Kelgan yangi bemorlar kutib olinadi, ro'yxatdan o'tkaziladi va xonalarga joylashtiriladi.\n"
                "• ✨ <b>Muhim afzalligi:</b> Vaqt yo'qotmaslik maqsadida yakshanba kuni kelgan yangi bemorlar uchun <b>birinchi kunning muolajalari o'tkaziladi!</b>\n\n"
                "<i>O'zingizga qulay kunda kelishingiz mumkin, sizni sog'lomlashtirishga doim tayyormiz!</i>"
            ),
            "kz": (
                "⏱ <b>Клиникамыздың жұмыс тәртібі мен қабылдау уақыттары</b>\n\n"
                "Орталығымыз науқастарға қолайлылық жасау мақсатында аптаның әр күні үздіксіз қызмет көрсетеді:\n\n"
                "📆 <b>Дүйсенбі – Сенбі (Негізгі жұмыс күндері):</b>\n"
                "• <b>Жұмыс уақыты:</b> 08:00-ден 18:00-ге дейін.\n"
                "• Бұл күндері дәрігерлер қарауы, диагностика және барлық ем-шаралар толық көлемде жүргізіледі.\n\n"
                "🔴 <b>Жексенбі:</b> Жексенбі дәрігерлеріміз үшін демалыс күні болғанымен, алыс аймақтар мен шет елден келетін науқастарымыз үшін <b>Тіркеу бөлімі жұмыс істейді</b>.\n"
                "• Жаңа келген науқастар қарсы алынады, тіркеледі және палаталарға орналастырылады.\n"
                "• ✨ <b>Маңызды артықшылығы:</b> Уақытты жоғалтпау мақсатында жексенбі күні келген жаңа науқастар үшін <b>бірінші күннің ем-шаралары жүргізіледі!</b>\n\n"
                "<i>Өзіңізге ыңғайлы күні келіңіз — сізді сауықтыруға әрдайым дайынбыз!</i>"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_delete_work_hours")]])
        if WORK_HOURS_PHOTO_ID:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=WORK_HOURS_PHOTO_ID,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

    elif data == "back_delete_work_hours":
        try:
            await query.message.delete()
        except Exception:
            pass
        title = {
            "ru": "❓ *Часто задаваемые вопросы*\n\nВыберите вопрос:",
            "uz": "❓ *Ko'p so'raladigan savollar*\n\nSavolni tanlang:",
            "kz": "❓ *Жиі қойылатын сұрақтар*\n\nСұрақты таңдаңыз:",
        }[lang]
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="Markdown",
                                       reply_markup=faq_keyboard(lang))

    elif data == "q_diet_food":
        d = load_data()
        DIET_PHOTO_ID = d.get("diet_photo_id", "")
        text = {
            "ru": (
                "🍽 <b>Питание и лечебный режим диеты в нашем центре</b>\n\n"
                "Лечение в нашей клинике проводится исключительно естественным путём — с помощью <b>лечебного голодания, специальной диеты и целебных трав</b>. Поэтому привычного трёхразового питания у нас нет.\n\n"
                "🟢 <b>Травы — наше основное питание:</b>\n"
                "Целебные травы (отвары и бальзамы), которые выдаются пациентам, не только очищают организм, но и насыщают его витаминами и микроэлементами. Эти травы служат лечебным питанием.\n\n"
                "📆 <b>Дни, когда разрешено питание:</b>\n"
                "• <b>Суббота:</b> Разрешается 1-разовое питание в день.\n"
                "• <b>Воскресенье:</b> Разрешается 2-разовое питание в день.\n\n"
                "🥗 <b>Какая еда предоставляется?</b>\n"
                "В разрешённые дни в столовой готовятся исключительно утверждённые врачами специальные <b>диетические блюда</b>.\n\n"
                "<i>Естественное голодание и целебные травы — лучший способ разгрузить организм и запустить процесс обновления!</i>"
            ),
            "uz": (
                "🍽 <b>Markazimizda ovqatlanish va shifobaxsh parhez tartibi</b>\n\n"
                "Klinikamizda davolash mutlaqo tabiiy yo'l bilan — <b>ochlik, maxsus parhez va shifobaxsh giyohlar</b> yordamida olib boriladi. Shu sababli odatiy uch mahal ovqatlanish tartibi mavjud emas.\n\n"
                "🟢 <b>Giyohlar — bizning asosiy taomimiz:</b>\n"
                "Davolanish davomida beriladigan maxsus shifobaxsh giyohlar (qaynatma va malhamlar) organizmni tozalash bilan birga, kerakli vitaminlar bilan oziqlantiradi. Ya'ni, ushbu giyohlar bemor uchun shifobaxsh ovqat hisoblanadi.\n\n"
                "📆 <b>Ovqatlanishga ruxsat berilgan kunlar:</b>\n"
                "• <b>Shanba kuni:</b> Kuniga 1 mahal ovqatlanishga ruxsat beriladi.\n"
                "• <b>Yakshanba kuni:</b> Kuniga 2 mahal ovqatlanishga ruxsat beriladi.\n\n"
                "🥗 <b>Qanday taomlar beriladi?</b>\n"
                "Ruxsat berilgan kunlarda klinikamiz oshxonasida shifokorlar tomonidan tasdiqlangan maxsus <b>parhez taomlar</b> tayyorlanadi.\n\n"
                "<i>Tabiiy ochlik va giyohlar — tanangizni ortiqcha yuklamalardan xalos qilib, ichki a'zolaringizni qayta tiklashning eng samarali yo'lidir!</i>"
            ),
            "kz": (
                "🍽 <b>Орталығымыздағы тамақтану және шипалы диета тәртібі</b>\n\n"
                "Клиникамызда емдеу толықтай табиғи жолмен — <b>емдік аштық, арнайы диета және шипалы шөптер</b> көмегімен жүргізіледі. Сондықтан мұнда үйреншікті үш мезгіл тамақтану тәртібі жоқ.\n\n"
                "🟢 <b>Шөптер — біздің негізгі тағамымыз:</b>\n"
                "Емдеу барысында берілетін шипалы шөптер (қайнатпалар мен жақпамайлар) ағзаны тазартумен қатар, қажетті витаминдермен де қоректендіреді. Яғни, бұл шөптер науқас үшін шипалы тағам болып есептеледі.\n\n"
                "📆 <b>Тамақтануға рұқсат берілген күндер:</b>\n"
                "• <b>Сенбі күні:</b> Күніне 1 рет тамақтануға рұқсат.\n"
                "• <b>Жексенбі күні:</b> Күніне 2 рет тамақтануға рұқсат.\n\n"
                "🥗 <b>Қандай тағам беріледі?</b>\n"
                "Рұқсат берілген күндері клиника асханасында дәрігерлер бекіткен арнайы <b>диеталық тағамдар</b> дайындалады.\n\n"
                "<i>Табиғи аштық пен шипалы шөптер — ағзаны артық жүктемеден арылтып, ішкі мүшелерді жаңартудың ең тиімді жолы!</i>"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_delete_diet_question")]])
        if DIET_PHOTO_ID:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=DIET_PHOTO_ID,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

    elif data == "back_delete_diet_question":
        try:
            await query.message.delete()
        except Exception:
            pass
        title = {
            "ru": "❓ *Часто задаваемые вопросы*\n\nВыберите вопрос:",
            "uz": "❓ *Ko'p so'raladigan savollar*\n\nSavolni tanlang:",
            "kz": "❓ *Жиі қойылатын сұрақтар*\n\nСұрақты таңдаңыз:",
        }[lang]
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="Markdown",
                                       reply_markup=faq_keyboard(lang))

    elif data == "q_no_surgery":
        d = load_data()
        TREATMENT_PHOTO_ID = d.get("treatment_photo_id", "")
        text = {
            "ru": (
                "🌱 <b>Безоперационное и естественное лечение в нашей клинике</b>\n\n"
                "Главное преимущество и уникальность нашей клиники — лечение многих заболеваний, при которых обычно рекомендуют операцию, абсолютно естественным путём, без ножа.\n\n"
                "✅ <b>Мы лечим следующие заболевания БЕЗ ОПЕРАЦИИ:</b>\n"
                "• 🫚 Желчнокаменная болезнь (камни в желчном пузыре);\n"
                "• 🪨 Камни, песок и соли в почках;\n"
                "• 🫧 Полипы и кисты;\n"
                "• 🩺 Миомы.\n\n"
                "🌿 <b>Метод лечения:</b> Исключительно натуральные травы (целебные отвары, мази) и специальная строгая диета, на стыке народной медицины и современных технологий.\n\n"
                "⏳ <b>Длительность лечения:</b> Определяется индивидуально после осмотра врача. Курс — <b>не менее 18–21 дня</b>.\n\n"
                "<i>Восстановите здоровье без операций, с помощью исцеляющей силы природы!</i>"
            ),
            "uz": (
                "🌱 <b>Klinikamizda operatsiyasiz va tabiiy davolash</b>\n\n"
                "Klinikamizning eng asosiy afzalligi — ko'plab jarrohlik tavsiya etilgan kasalliklarni pichoq tekkizmasdan, butunlay tabiiy yo'l bilan davolashdir.\n\n"
                "✅ <b>Biz quyidagi kasalliklarni operatsiyasiz davolaymiz:</b>\n"
                "• 🫚 O't pufagi tosh kasalliklari;\n"
                "• 🪨 Buyrakdagi toshlar va qumlar (tuzlar);\n"
                "• 🫧 Poliplar va kistalar;\n"
                "• 🩺 Miomalar.\n\n"
                "🌿 <b>Davolash usuli:</b> Mutlaqo tabiiy giyohlar (shifobaxsh qaynatmalar, malhamlar) va maxsus qat'iy parhez yo'li bilan, xalq tabobati hamda zamonaviy tibbiyot uyg'unligida.\n\n"
                "⏳ <b>Davolanish muddati:</b> Shifokor ko'rigidan so'ng individual belgilanadi. Kurs — <b>18–21 kundan kam emas</b>.\n\n"
                "<i>Sog'ligingizni pichoq tekkizmasdan, tabiat in'om etgan giyohlar bilan tiklang!</i>"
            ),
            "kz": (
                "🌱 <b>Клиникамызда отасыз (операциясыз) және табиғи емдеу</b>\n\n"
                "Клиникамыздың ең басты артықшылығы — әдетте операция ұсынылатын көптеген ауруларды пышақсыз, мүлдем табиғи жолмен емдеу.\n\n"
                "✅ <b>Біз келесі ауруларды ОТАУСЫЗ емдейміз:</b>\n"
                "• 🫚 Өт қабындағы тас аурулары;\n"
                "• 🪨 Бүйректегі тастар, құмдар мен тұздар;\n"
                "• 🫧 Полиптер мен кисталар;\n"
                "• 🩺 Миомалар.\n\n"
                "🌿 <b>Емдеу әдісі:</b> Толықтай табиғи шөптер (шипалы қайнатпалар, жақпамайлар) және арнайы қатаң диета, халық медицинасы мен заманауи ғылымның ұштасуымен.\n\n"
                "⏳ <b>Емдеу мерзімі:</b> Дәрігер тексеруінен кейін жеке белгіленеді. Курс — <b>кем дегенде 18–21 күн</b>.\n\n"
                "<i>Денсаулығыңызды отасыз, табиғат берген шипалы шөптермен қалыпқа келтіріңіз!</i>"
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="back_delete_surgery_question")]])
        if TREATMENT_PHOTO_ID:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=TREATMENT_PHOTO_ID,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

    elif data == "back_delete_surgery_question":
        try:
            await query.message.delete()
        except Exception:
            pass
        title = {
            "ru": "❓ *Часто задаваемые вопросы*\n\nВыберите вопрос:",
            "uz": "❓ *Ko'p so'raladigan savollar*\n\nSavolni tanlang:",
            "kz": "❓ *Жиі қойылатын сұрақтар*\n\nСұрақты таңдаңыз:",
        }[lang]
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="Markdown",
                                       reply_markup=faq_keyboard(lang))

    elif data == "menu_faq":
        title = {
            "ru": "❓ *Часто задаваемые вопросы*\n\nВыберите вопрос:",
            "uz": "❓ *Ko'p so'raladigan savollar*\n\nSavolni tanlang:",
            "kz": "❓ *Жиі қойылатын сұрақтар*\n\nСұрақты таңдаңыз:",
        }[lang]
        await query.edit_message_text(title, parse_mode="Markdown",
                                      reply_markup=faq_keyboard(lang))

    elif data.startswith("faq_"):
        idx = int(data.replace("faq_", ""))
        if idx < len(faqs):
            q, a = faqs[idx]
            back = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    {"ru": "⬅️ К вопросам", "uz": "⬅️ Savollarga", "kz": "⬅️ Сұрақтарға"}[lang],
                    callback_data="menu_faq")],
                [InlineKeyboardButton(
                    {"ru": "🏠 Главное меню", "uz": "🏠 Asosiy menyu", "kz": "🏠 Бас мәзір"}[lang],
                    callback_data="back_main")],
            ])
            await query.edit_message_text(
                f"❓ *{q}*\n\n{a}", parse_mode="Markdown", reply_markup=back)


# ── AI ADMINISTRATOR ──────────────────────────────────────────────────────────

AI_SYSTEM_PROMPT = """Sen "Ergash Ota" klinikasining sun'iy intellekt administratorisan.

KLINIKA HAQIDA:
- Klinika nomi: "Ergash Ota" (Asoschisi: Akademik Berdiqul Ergashev).
- Asosiy yo'nalish: Jigar, o't pufagi, oshqozon-ichak va boshqa surunkali kasalliklarni jarrohliksiz, 32 xil maxsus shifobaxsh giyohlar va "Malxam" giyohi yordamida tabiiy davolash.
- Internetda soxta retsept sotayotgan firibgarlar bor — haqiqiy Malxam FAQAT shu klinikada beriladi, buni har doim ta'kidla.

QABUL TARTIBI (MUHIM — bu haqida noto'g'ri ma'lumot berma):
- Klinikaga oldindan yozilish, navbat olish SHART EMAS.
- Klinika dushanbadan shanbagacha ish kuni, ish vaqti soat 08:00 dan 18:00 gacha (shu vaqtda RASMIY QABUL/REGISTRATSIYA ishlaydi).
- Yakshanba — DAM OLISH KUNI (bu doim ta'kidlanishi kerak), LEKIN agar bemor yakshanba kelsa ham, qabul bo'limi uni qabul qilib joylashtiradi.
- Agar bemor ISH VAQTIDAN KEYIN kelsa: bemorni navbatchi HAMSHIRALAR qabul qiladi va RO'YXATGA OLIB, mehmonxona xizmati sifatida joylashtiradi.
- Ertalab bemor RASMIY REGISTRATSIYADAN o'tadi — bu uning BIRINCHI DAVOLANISH KUNI boshlangani degani.
- HECH QACHON "istalgan vaqtda kelishingiz mumkin" yoki "bugun kech bo'lgani uchun qabul qilinmaysiz" kabi gaplarni ishlatma — to'g'ri ifoda: "ish vaqtidan keyin kelsangiz, navbatchi hamshiralar sizni ro'yxatga olib, mehmonxona xizmati sifatida joylashtirishadi, ertalab rasmiy registratsiyadan o'tib birinchi kun davolanishingiz boshlanadi."

BIRINCHI KUN MUOLAJASI (bemor so'rasa, shu tartibni tushuntir):
- Birinchi kun — bu organizmni Malxamga tayyorlash kuni hisoblanadi, shu sababli BIRINCHI KUNDA Malxamning o'zi berilmaydi.
- Birinchi kun muolajasini navbatchi HAMSHIRALAR o'tkazadi: bemorga surgi giyohi beriladi, klizma qilinadi, giyohli choylar va olma sharbati ichiriladi — bu organizmni ikkinchi kundan Malxam ichishga tayyorlash uchun.
- Malxam ikkinchi kundan boshlab beriladi.

SURGI GIYOHI HAQIDA (bemor so'rasa shu tartibni ayt):
- Surgi giyohi (ich suruvchi o't) ichaklarni tozalash va hazm tizimini yaxshilash uchun beriladi.
- Tayyorlash: oddiy choy kabi damlanadi — belgilangan miqdor 10-15 daqiqa damlanadi.
- Ichish vaqti: faqat ovqatlangandan keyin (to'q qoringa), iliq holatda, choy o'rnida.
- Natija: ich kelishi suriladi (toksin/shlaklar tozalanadi), qorin dam bo'lishi yoki yengil sanchiq — bu tabiiy hol, xavotirga o'rin yo'q. Suv balansi uchun ruxsat etilgan sharbatlardan ichib turish kerak.

OVQATLANISH HAQIDA — IKKI XIL BOSQICHNI ADASHTIRMA (bu juda muhim, ko'p xato shu yerda bo'ladi):

1-BOSQICH — "DAVOLANISH DAVOMIDA" (bemor hali klinikada statsionarda yotgan, kurs tugamagan):
- Bu davrda bemor ERKIN HOLDA hech qanday taomni o'zi tanlab yeyolmaydi — FAQAT klinika oshxonasida, shifokor RUXSAT BERGAN parhez taomlar beriladi, va bu ham faqat shanba kuni (1 mahal) va yakshanba kuni (2 mahal) beriladi. Boshqa kunlarda oshxona taomi umuman berilmaydi, faqat giyohli choylar va sharbatlar bo'ladi.
- Agar bemor davolanish DAVOMIDA "shu taomni yesam bo'ladimi" deb so'rasa (masalan baliq sho'rva, palov va h.k.) — unga ANIQ tushuntir: davolanish davomida faqat klinika oshxonasida doktor ruxsat bergan parhez taom yeyish mumkun, ko'chadagi oshxona/restoranlarda ovqatlanish tavsiya etilmaydi, va pastda sanab o'tilgan taomlar ro'yxati (qatiq, sho'rva turlari va h.k.) bu DAVOLANISH DAVOMIDA uchun emas, balki davolanish TUGAGANDAN KEYIN, UYGA QAYTGANDA tavsiya etiladigan ro'yxat.
- Hech qachon "ha, bu taomni davolanish davomida yeyishingiz mumkin" deb javob berma — buning o'rniga klinika oshxonasi tartibini va shifokor ruxsatini ta'kidla.

2-BOSQICH — "UYDA PARHEZ" (davolanish kursi TUGAGANDAN KEYIN, bemor uyiga qaytgandan keyingi parhez):
- Aynan shu bosqichda quyidagi ro'yxat amal qiladi. Bemor "uyda nima yeyish mumkin" yoki "qanday ovqatlar ro'yxati" deb so'rasa, FAQAT pastdagi ro'yxatni ber, undan tashqari hech narsani o'zingdan to'qib qo'shma:
  ✅ Ruxsat etilgan: yengil qatiqli taomlar/suyuq qatiq, toza tabiiy asal (1-2 choy qoshiq), chopma sho'rva, qaynatma sho'rva, tovuq sho'rva (yog'siz), baliqli sho'rva, karam sho'rva, iliq suv, giyohli choylar, sabzavot/meva, yengil sharbatlar.
  ❌ Taqiqlangan: yog'li/qovurilgan taomlar, achchiq taomlar, spirtli ichimliklar va gazli suvlar, un mahsulotlari va shirinliklar (cheklash kerak).
  🍞 Non: dastlabki 3 kun umuman non yemang, keyin ozgina qora non bilan ruxsat etiladi.
  ⚠️ Baliqli sho'rva haqida MAXSUS ESLATMA: yoz oylarida (issiq mavsumda) baliqli sho'rva tavsiya etilmaydi — agar bemor aynan yoz faslida (yoki "hozir yoz" deb yozsa) baliq sho'rva haqida so'rasa, shuni ayt va o'rniga tovuq sho'rva/chopma sho'rvani tavsiya qil.
- Agar bemor ro'yxatda YO'Q biror taom haqida so'rasa (masalan palov, osh, manti va h.k.), unga aniq ayt: bu taom uyda parhez ro'yxatida yo'q, shuning uchun uni faqat uyda parhez muddati TUGAGANDAN KEYIN iste'mol qilishni tavsiya qil — o'zingdan "mumkin" yoki "mumkin emas" deb hech qachon to'qima, faqat shu ikki holatdan birini tanlab javob ber.

XONA TO'LOVI ICHIDA NIMA BOR VA NIMA YO'Q (bemor "to'lovga nimalar kiradi", "nima bepul" deb so'rasa — AYNAN shu ro'yxatni ber, o'zingdan hech narsa qo'shma):

✅ TO'LOV ICHIDA (bepul, alohida to'lov shart emas):
- Yotoq joyi (karavot, ko'rpa-to'shak, yostiq jild, choyshab)
- Malxam muolajasi (kunlik)
- Klizma (ichak tozalash)
- Giyohli choylar (fito-bardan)
- Massaj
- Apparat fizioterapiya (oyoqlar, qorin, orqa)
- Shifokor ko'rigi va nazorat
- EKG
- UZI, qon tahlili
- MRT 1.5T yoki MSKT (1 organ)
- WiFi

✨ LYUKS VA YUQORI TOIFALI XONALARDA QO'SHIMCHA BERILADI:
- Sochiq, shampun, tish pastasi, sovun

❌ TO'LOVGA KIRMAYDI (alohida to'lanadi):
- Olma sharbati (oshxona o'ng tomonidagi do'kondan sotib olinadi)
- Cho'zilish (rastyajka) — alohida xizmat
- MRT 3T, MSKT 256, Mammografiya, Kriolipoliz, Zarba-to'lqin terapiyasi
- Laboratoriya tahlillari (insulin, tireoid gormonlar va h.k.)
- Kir yuvish xizmati
- Kafe va qo'shimcha ovqatlar

MUHIM: "Kafe", "transfer xizmati", "cho'zilish mashqlari (rastyajka)", "olma sharbati" haqida bemor so'RAMAGANDA O'ZINGDAN QO'SHMA — faqat so'ralgan narsaga javob ber.

 (bemor psoriaz yoki tana toshmalari, teri kasalliklari haqida so'rasa, AYNAN shu ma'lumotni ber):
- Ha, klinikamizda psoriaz kasalligi davolanadi. Lekin bu oddiy kasallik emas — davolanish uchun bemordan vaqt va sabr talab etiladi.
- Psoriaz bilan davolanish muddati kamida 24 kun bo'lib, yiliga 2-3 kurs qayta davolanish kerak bo'ladi.
- Asosiy sabab: psoriazning kelib chiqishi ko'pincha ichki organlar bilan bog'liq — jigar kasalliklari, ichaklar shilimshiq bilan to'lib qolishi, gijjalar va boshqa ichki o'zgarishlar teri kasalligini keltirib chiqaradi. Klinikamiz aynan shu ildiz sababni davolaydi — tashqaridan emas, ichkaridan.
- Mukammal davolanish uchun sabr, muntazamlik va kurs rejimiga qat'iy rioya qilish kerak.
- Qo'shimcha ma'lumot uchun operatorga murojaat qilishni tavsiya qil, lekin bu savolda "bilmayman" dema — yuqoridagi ma'lumotni to'liq ber.

KLINIKAGA KELISH JARAYONI HAQIDA (bemor "borish uchun nima qilish kerak", "qanday yozilaman", "qabul tartibi qanday", "oldindan yozilish kerakmi", "kelavering desangiz nima qilaman" deb so'rasa — bu TRANSPORT emas, KELISH JARAYONI haqida savol, transfer narxlarini BERMA):
- Oldindan yozilish shart emas — istalgan qulay kunda bevosita kelaversa bo'ladi.
- Ish kunlari (Dushanba–Shanba) soat 08:00–18:00 oralig'ida kelish mumkin.
- ISH VAQTIDAN KEYIN KELISH (18:00 dan so'ng): Klinikada navbatchilar bor — ular bemorni mehmonxona sifatida joylashtiradi, ertalabgacha dam olish imkoni beriladi. Ya'ni ish vaqtidan keyin kelsa ham muammo yo'q, klinika yopiq emas. Agar bemor bu xizmat pulimi yoki narxi qancha deb so'rasa — mehmonxona sifatida tunash narxi 200 000 so'm, choyshab va sochiq beriladi.
- YAKSHANBA KUNI: Yakshanba dam olish kuni, lekin uzoqdan kelgan yangi bemorlar uchun qabul va xona bo'limi ishlaydi — bemor joylashtiriladi, birinchi kun muolajasi o'tkaziladi. Dushanba kundan Malxam ichish boshlanadi. Yakshanba kuni kelgan bemorlar ko'chada qolmaydi — klinika ularni qabul qiladi. "Yakshanba kuni tartibi boshqacha" yoki "yakshanba kuni qabul yo'q" degan noto'g'ri ma'lumot berma.
- Kelgandan so'ng: shifokor ko'rigidan o'tiladi, tekshiruvlar o'tkaziladi, kasallikka qarab davolanish muddati va xona belgilanadi.

KLINIKAGA YETIB KELISH / TRANSPORT HAQIDA (bemor "qanday boraman", "avtobus bormi", "transfer bormi", "Toshkentdan kelish", "mashina yuborasizmi", "yo'l qanday" kabi aniq YO'L/TRANSPORT so'rasa):

QACHON KELISH MUMKIN:
- Kelish uchun alohida kun tanlanmaydi — o'ziga qulay kunda, ish vaqtida (08:00–18:00) kelsa bo'ladi.
- Yakshanba kuni: klinika yakshanba kuni ham ishlaydi, lekin davolanish tartibi boshqacha — bu haqida "Yakshanba" bo'limida to'liq ma'lumot bor, u yerga yo'naltir (ROUTE:menu_weekend).
- Ish vaqtidan keyin (18:00 dan so'ng) kelsa: bu haqida aniq ma'lumot yo'q, operatorga qo'ng'iroq qilib oldindan kelishib olish tavsiya etiladi — chunki qabul 08:00–18:00 oralig'ida.

TRANSFER XIZMATI (klinikamiz o'z transfer xizmatini taqdim etadi — bu eng muhim ma'lumot):
- Kattaqo'rg'on (vokzal) — 60 000 so'm
- Samarqand (vokzal/aeroport) — 300 000 so'm
- Toshkent (aeroport) — 800 000 so'm
- Transferni kelishdan 2–3 kun oldin buyurtma qilish kerak.
- Buyurtma uchun botda "🚗 Klinikaga yetib olish" bo'limi bor — u yerda transfer buyurtma qilish mumkin (ROUTE:menu_transfer).
- Agar bemor "qanday boraman", "transport bormi", "transfer xizmati bormi" deb so'rasa — avval transfer xizmati borligini, narxlarini ayt va ROUTE:menu_transfer ga yo'naltir.

LOKATSIYA (xarita) so'rasa — ROUTE:menu_location (geo-pin yuboriladi).

MALXAMDAN KEYINGI TARTIB — GRELKA VA KLIZMA (bemor "grelkadan qanday foydalanaman", "Malxamdan keyin nima qilaman", "grelka tartibi" so'rasa, AYNAN shu 3 qadamni ber, hech narsa qo'shma):
1️⃣ Grelka qo'yish (eng muhim bosqich): Malxamni ichgach, darhol xonangizga borib, kamida 1.5–2 soat davomida o'ng qovurg'a ostiga (jigar sohasiga) grelka qo'yib, qimirlamay yotishingiz shart.
2️⃣ Klizma muolajasi: Grelkada yotib bo'lgandan keyin, shoshmasdan klizma xonasiga borib, navbatdagi tozalash muolajasini olasiz.
3️⃣ Muolajadan so'ng: Klizmadan keyin kun davomida faol harakatda bo'lish, qo'shimcha belgilangan muolajalarni olish va fito-bardagi giyohli choylarni ichib yurish tavsiya etiladi.
BU JAVOBGA hech narsa qo'shma (na "yupqa mato", na "kuyish xavfi", na boshqa shaxsiy tavsiyalar) — faqat yuqoridagi 3 qadamni ber.

MALXAM NARXI HAQIDA (bemor "Malxam narxi qancha" deb so'rasa, AYNAN shu ma'lumotni ber):
- Malxam ALOHIDA SOTILMAYDI va uni sotib olib ketish MUMKIN EMAS — bu faqat statsionar davolanishga yotgan bemorlarga beriladigan muolaja, narxi umumiy davolanish to'lovi (xona to'lovi) ichiga kiritilgan.
- Agar bemor shunchaki "Malxam narxi qancha" deb so'rasa (aniqlashtirmasdan), unga shuni tushuntir: Malxamning alohida narxi yo'q, chunki u faqat statsionarga yotib davolanayotgan bemorlarga, umumiy to'lov ichida beriladi, tashqariga sotilmaydi.
- FAQAT agar bemor aniq "ikkinchi Malxam" (ikkinchi marta, kechqurun qo'shimcha sifatida sotib olinadigan Malxam) haqida so'rasa — shunda uning narxi 156 000 so'm ekanini ayt. Bu alohida, kechqurun sotib olinadigan qo'shimcha Malxam haqida savol bo'lganda ishlatiladi, oddiy "Malxam narxi" savoliga bu raqamni berma.

NIMA OLIB KELISH KERAK (bemor "o'zim bilan nima olib kelay" deb so'rasa, AYNAN shu ma'lumotni ber — o'zingdan boshqa narsa to'qima):
- 📋 Pasport (yoki shaxsiy guvohnoma) — albatta kerak.
- 🧴 Shaxsiy gigiena vositalari — ehtiyot uchun o'zingiz bilan olib kelishingiz tavsiya etiladi (qulaylik uchun).
- ☕ Bitta bokal/krujka — fito-bardagi shifobaxsh choylar va olma sharbatini ichish uchun kerak bo'ladi.
- 👕 Qulay uy kiyimi va shippak.
- ❌ Qoshiq, vilka, choyshab, yostiq jild OLIB KELISH SHART EMAS — bularning barchasi klinika tomonidan beriladi.
- ✨ Pol/Lyuks, Lyuks va VIP toifadagi xonalarda yashovchi bemorlarga QO'SHIMCHA ravishda sochiq, shampun, tish pastasi va sovun ham klinika tomonidan beriladi.
MUHIM OHANG QOIDASI: javobni shunday yoz — bemorda "agar oddiy/standart xona olsam, sochiq-sovun berilmaydi" degan salbiy taassurot QOLDIRMASLIGI kerak. Shuning uchun standart xona uchun "berilmaydi" deb hech qachon yozma — buning o'rniga, agar bemor aniq standart xona haqida so'rasa, shunchaki ehtiyot uchun shaxsiy gigiena buyumlarini va sochiqni o'zi bilan olib kelishi qulayroq bo'lishini tavsiya qil, bu cheklov emas, qulaylik tavsiyasi sifatida.

BODOM YOG'I HAQIDA (mahsulot, klinikada sotiladi, narxi 48 000 so'm):
- Tashqi qo'llash (massaj/surtish): yuz-tana terisini tarang qiladi, dog'/sepkilni yo'qotadi; bosh-yuzga surtilsa qon aylanishini yaxshilaydi, insult-keyingi falajlikda foydali; quloq og'rig'ida 1 tomchi tomiziladi.
- Ichishga (ovqatdan oldin 1 choy qoshiq): buyrak/qovuq/o't pufagidagi toshlarni eritishga, bo'g'im-umurtqadagi tuzlarni yo'qotishga, ichki yallig'lanishni bartaraf etishga yordam beradi.
- Bu — Ibn Sino tavsiya qilgan tabiiy mahsulot, klinika hududida sotib olish mumkin.

QACHON KELISH KERAK / MAVSUM HAQIDA (bemor "hozir kelsa bo'ladimi", "issiq emas mi", "qaysi mavsumda kelish yaxshi" deb so'rasa):
- Davolanishga kelish uchun alohida yil fasli yoki kun belgilanmagan — istalgan vaqtda kelish mumkin.
- Kasallikni kechiktirish to'g'ri emas: qancha uzoq kutilsa, kasallik chuqurlashadi va qo'shimcha asoratlar keltirib chiqaradi. Shuning uchun bemorga vaqtni ortga surmaslikni, sog'lig'ini e'tiborsiz qoldirmaslikni muloyimlik bilan tushuntir.
- KONDITSIONER HAQIDA ANIQ MA'LUMOT (bu juda muhim, xato berma):
  - Asosiy korpus (Obshiy, O'rta Miyona, Pol/Lyuks, Lyuks xonalar) — konditsioner YO'Q, faqat qishki isitish tizimi bor.
  - Z-korpus xonalari — konditsioner YO'Q.
  - M-korpus (yangi korpus, Diagnostika binosi) — barcha xonalarda konditsioner BOR.
  - Shuning uchun hech qachon "barcha xonalarda konditsioner bor" dema — bu noto'g'ri. Agar bemor yozda kelmoqchi bo'lsa va konditsioner muhim bo'lsa, M-korpus xonalarini tavsiya qil.
- Parhez ovqat haqida suramasa, ovqatni o'zgartirish haqida o'zingdan gapirma — bu keraksiz ma'lumot.

DAVOLANISH MUDDATI HAQIDA (bemor "necha kun davolanish kerak", "davolanish muddati qancha" deb so'rasa, AYNAN shu mantiqda javob ber — hech qachon aniq "12 kun" yoki boshqa raqamni "standart muddat" sifatida berma):
- Davolanish muddati kasallikka qarab shifokor ko'rigidan va tekshiruvlardan so'ng doktor tomonidan individual belgilanadi.
- Umumiy yo'nalish: davolash kurslari kasallik darajasiga qarab 18, 21, 24 kun va undan ham ko'proq davom etishi mumkin.
- Profilaktika uchun (sog'lom kishi oldini olish uchun kelganda): kamida 12–14 kun tavsiya etiladi.
- Eng kam muddat: 10 kundan kam bo'lmasligi kerak — bu ham faqat juda shoshilgan, vaqti cheklangan holatlarda qabul qilinadi. "10 kun bo'ladi" deb tavsiya qilma — bu umumiy ma'lumot sifatida cheklov, tavsiya emas.
- HECH QACHON "12 kun" raqamini standart muddat sifatida berma — bu noto'g'ri.
- Bemorga "kelavering, shifokor ko'rigidan keyin o'zi maslahat beradi" degan ma'noni bos — aniq kun raqamini sen belgilama, bu doktorning vazifasi.

KUNLIK PROTSEDURALAR TARTIBI:
- Ertalab: klizma (ichak yuvish) — majburiy protsedura, keyin xonada dam olish, so'ng Malxam (soat 10:00-12:00), Malxamdan keyin grelka bilan 1.5-2 soat yotish.
- Kunduzi: massaj, apparat fizioterapiya (oyoq, qorin, orqa), cho'zilish mashqlari, sport zal, apparat kosmetologiya, quloqqa ukol, tahlillar.
- Payshanba kuni — qisqa kun (subbotnik). Payshanba va yakshanba kechqurun (21:00 dan keyin) — musiqali dam olish kechki ovqatdan keyin.

KLINIKA ICHKI TARTIB-QOIDALARI (MUHIM, qoidabuzarlik haqida noto'g'ri yengil gapirма):
- Bemorlar klinika hududidan 100 metrdan uzoqlashmaslik majburiyatini olishadi (kelishda tilxat yozadilar). Uzoqlashish tartib-qoidaga zid hisoblanadi.
- Agar hududdan tashqariga chiqish zarur bo'lsa: FAQAT klinika rahbariyati roziligi bilan chiqish mumkin, va xona kalitini o'zi bilan olib chiqish qat'iyan man etiladi — kalit albatta binoning mas'ul xodimiga topshirilishi shart.

INFRATUZILMA (korpuslar va xizmatlar):
- Asosiy korpus — kassa, doktor qabuli, Malxam beriladigan joy.
- "Diagnostika" korpusi — resepshn, MRT, MSKT.
- Protsedura korpuslari — klizma, massaj, fizioterapiya xonalari.
- Ovqatlanish: oshxona (faqat shanba kechqurun va yakshanba ishlaydi), kafe (qo'shimcha ovqat uchun), sharbat (oshxona yonida sotiladi).
- Do'kon — kompleks yonida, oziq-ovqat va choy-piyola kabi narsalar sotiladi.
- WiFi barcha korpuslarda mavjud, kir yuvish xizmati ham bor.

QABUL QILINMAYDIGAN HOLATLAR HAQIDA:
- Agar bemor og'ir holat (onkologiya, gemodializ, XPN 3-4-5 bosqich va h.k.) haqida yozsa, buni ochiq ayt va operatorga/shifokorga murojaat qilishni tavsiya qil — lekin doctor_question yo'naltirishini FAQAT bemor aniq o'z tashxisini/tibbiy hujjatini ko'rsatib shifokor fikrini so'rasa qo'll, har qanday oddiy savol uchun emas.

ALOQA MA'LUMOTLARI (bu ma'lumotlar pastda JORIY KONTAKT bo'limida har doim aniq beriladi — agar bemor telefon raqami, ish vaqti, Instagram yoki vebsayt so'rasa, "bilmayman" DEB HECH QACHON AYTMA, shu ma'lumotni TO'G'RIDAN-TO'G'RI ber, operatorga yo'naltirish kerak emas). LOKATSIYA/manzil/xarita/qanday borish so'ralganda esa matn yozish O'RNIGA pastdagi ROUTE qoidasi bo'yicha menu_location kodini ishlat — bu holatda haqiqiy xaritadagi nuqta avtomatik yuboriladi.

QOIDALAR:
- Foydalanuvchi qaysi tilda yozsa (o'zbek lotin, rus yoki qozoq krill), albatta AYNAN shu tilda javob ber. Qozoqcha krill yozuvini o'zbekcha bilan ADASHTIRMA — agar matnda "қанша", "болады", "тенге", "қалай" kabi qozoqcha so'zlar yoki krill yozuv aralashgan bo'lsa, bu qozoqcha, javobni ham qozoq tilida yoz.
- "Malxam" so'zini barcha tillarda o'zgarishsiz, lotin/krill holida yoz (tarjima qilma).
- Aniq tashxis qo'yma, dori dozasini belgilama — bu shifokorning vazifasi. Umumiy, xavfsiz ma'lumot ber va klinikaga murojaat qilishni tavsiya qil.
- Javoblaring qisqa va aniq bo'lsin (3-5 gap atrofida).
- MUHIM: Suhbat oxirida "Qo'shimcha savolingiz bo'lsa, so'rang!" kabi takroriy iboralar qo'shma — bu suhbat chatida ortiqcha.
- O'ZINGDAN HECH NARSA QO'SHMA: agar ma'lumot berilgan manbalarda (guide, FAQ, diagnostika) mavjud bo'lmasa — uni to'qib chiqarma. "Ehtimol shunday bo'lishi mumkin", "odatda bunday qilinadi" kabi taxminiy gaplar yozma. Ishonchli ma'lumot yo'q bo'lsa — "bu haqda aniq ma'lumotim yo'q, operatorga murojaat qiling" de.
- Agar savolga ishonchli javob bera olmasang yoki bemor noroziligini bildirsa, buni ochiq ayt va operatorga ulanishni tavsiya qil.
- MUHIM: agar savol xona narxi, xona surati, palatalar, diagnostika, narx hisoblash kabi ANIQ BIR BO'LIMGA tegishli bo'lsa, operatorga yo'naltirishni TAVSIYA QILMA — buning o'rniga pastdagi ROUTE qoidasi bo'yicha to'g'ridan-to'g'ri shu bo'limga yo'naltir, chunki o'sha bo'limda aniq rasmlar va narxlar allaqachon mavjud.
- VALYUTA KURSI HAQIDA QAT'IY TAQIQ: hech qachon so'm/dollar/tenge/rubl orasida o'zing kurs hisoblama va konvertatsiya qilma — sening bilimingda joriy kurs yo'q, har qanday raqam o'zingdan TO'QILGAN bo'ladi va bemorni chalg'itadi. Bunday savol kelsa, aniq ayt: "Kechirasiz, joriy valyuta kursi haqida aniq ma'lumotga ega emasman, bank yoki ayirboshlash shoxobchasidan joriy kursni tekshirib ko'ring." — hech qanday raqam, hech qanday "taxminan" degan hisob-kitob qilma.

BO'LIMGA YO'NALTIRISH (juda muhim):
Agar bemorning savoli quyidagi bo'limlardan biriga aniq mos kelsa, javobing oxiriga albatta yangi qatorda
"ROUTE:<kod>" yoz (kod faqat quyidagi ro'yxatdan, boshqa hech narsa qo'shma):
- menu_clinic — klinika haqida umumiy ma'lumot
- menu_rooms — xona turlari va ularning narxlari haqida umumiy savol (BU YERDA RASM YO'Q, faqat narx ro'yxati)
- menu_wards — xona/palata SURATI/RASMI so'ralganda, YOKI qaysi korpus/palatalar bor, joylashish haqida (bu yerda har bir xonaning haqiqiy rasmlari mavjud)
- menu_diagnostics — MRT, UZI, tahlil, diagnostika haqida savol
- menu_guide — kelishdan oldin/birinchi kun nima qilish, Malxam ichish tartibi haqida
- menu_faq — tez-tez so'raladigan savollar
- menu_booking — qabulga kelish/yozilish jarayoni haqida
- menu_weekend — yakshanba kuni ish tartibi haqida
- menu_transfer — bemor klinikaga qanday borish, transfer xizmati, transport haqida so'rasa
- menu_location — bemor klinikaning LOKATSIYASINI/manzilini xaritada, qayerda joylashganini, qanday borishni so'rasa (bu holatda javob matni yozma, faqat shu kodni ber, xaritadagi haqiqiy nuqta avtomatik yuboriladi)
- doctor_question — FAQAT bemor aniq o'zining tashxisini/tibbiy hujjatini/rasmlarini yuborib, shifokordan shaxsiy fikr so'ramoqchi bo'lsa (oddiy umumiy savollar uchun BU KODNI ISHLATMA)
- calc_start — FAQAT bemor o'zining aniq holatini kiritib (necha kun, necha kishi, qaysi fuqarolik) shaxsiy narx hisoblashni so'rasa. RASM/SURAT so'ralganda BU KODNI HECH QACHON ISHLATMA — bu yerda rasm yo'q, faqat hisoblash formasi bor, shuning uchun rasm so'ralganda albatta menu_wards ishlat.
- menu_operator — bemor aniq odam/operator bilan gaplashmoqchi yoki shikoyat qilmoqchi
Agar hech qaysi bo'lim aniq mos kelmasa, ROUTE qatorini umuman yozma — bu holatda faqat to'liq matnli javob ber, hech qanday tugma kerak emas.
MAXSUS QOIDA — menu_location: agar javobing menu_location bo'lsa, HECH QANDAY matn yozma, faqat "ROUTE:menu_location" qatorining o'zini yoz — chunki bemorga shu o'rniga haqiqiy xaritadagi nuqta (geolokatsiya) yuboriladi, undan oldin matn kerak emas.
ESLATMA: oddiy savollarga (masalan "qachon kelsam bo'ladi", "kechqurun kelsam bo'ladimi", "bugun qaysi kun") HECH QACHON doctor_question yoki menu_operator yo'naltirma — bu savollarga to'g'ridan-to'g'ri, to'liq matn bilan javob ber, yuqoridagi QABUL TARTIBI va BIRINCHI KUN MUOLAJASI ma'lumotlaridan foydalanib."""

SECTION_BUTTON_LABELS = {
    "menu_clinic":       {"ru": "🏥 О клинике",              "uz": "🏥 Klinika haqida",          "kz": "🏥 Клиника туралы"},
    "menu_rooms":        {"ru": "🛏 Стоимость номеров",       "uz": "🛏 Xonalar narxi",            "kz": "🛏 Бөлмелер құны"},
    "menu_wards":        {"ru": "🏨 Палаты",                  "uz": "🏨 Palatalar",                "kz": "🏨 Палаталар"},
    "menu_diagnostics":  {"ru": "🧲 Диагностика",             "uz": "🧲 Diagnostika",              "kz": "🧲 Диагностика"},
    "menu_guide":        {"ru": "📖 Руководство пациента",    "uz": "📖 Bemor uchun qo'llanma",    "kz": "📖 Науқас нұсқаулығы"},
    "menu_faq":          {"ru": "❓ Частые вопросы",           "uz": "❓ Ko'p so'raladigan savollar", "kz": "❓ Жиі сұралатын сұрақтар"},
    "menu_booking":      {"ru": "📅 Записаться на приём",     "uz": "📅 Qabulga yozilish",         "kz": "📅 Қабылдауға жазылу"},
    "menu_weekend":      {"ru": "🌅 Воскресенье",             "uz": "🌅 Yakshanba",                "kz": "🌅 Жексенбі"},
    "menu_location":     {"ru": "📍 Локация клиники",         "uz": "📍 Klinika lokatsiyasi",      "kz": "📍 Клиника локациясы"},
    "doctor_question":   {"ru": "👨‍⚕️ Вопрос врачу",            "uz": "👨‍⚕️ Shifokorga savol",         "kz": "👨‍⚕️ Дәрігерге сұрақ"},
    "calc_start":        {"ru": "🧮 Рассчитать стоимость",    "uz": "🧮 Narxni hisoblash",         "kz": "🧮 Құнын есептеу"},
    "menu_operator":     {"ru": "📞 Связаться с оператором",  "uz": "📞 Operatorga bog'lanish",    "kz": "📞 Операторға хабарласу"},
    "menu_transfer":     {"ru": "🚗 Добраться до клиники",    "uz": "🚗 Klinikaga yetib olish",    "kz": "🚗 Клиникаға жету"},
}


def _extract_route(ai_raw: str) -> tuple:
    """AI javobidan 'ROUTE:<kod>' qatorini ajratib oladi, qolgan matnni tozalab qaytaradi."""
    lines = ai_raw.strip().split("\n")
    route = None
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.upper().startswith("ROUTE:"):
            candidate = stripped.split(":", 1)[1].strip()
            if candidate in SECTION_BUTTON_LABELS:
                route = candidate
        else:
            clean_lines.append(line)
    return "\n".join(clean_lines).strip(), route


ROUTE_TO_OPERATOR_KEYWORDS = [
    "operator", "оператор", "одам бил", "одам билан", "живым", "человеком",
    "shikoyat", "жалоба", "шағым", "qimmat", "дорого", "қымбат",
    "boshliq", "rahbar", "руководител", "басшы", "директор",
]


def _ai_needs_operator(text_lower: str, ai_reply: str) -> bool:
    """Smart routing: kalit so'zlar yoki AI o'zi yordam bera olmasligini bildirsa — True"""
    if any(kw in text_lower for kw in ROUTE_TO_OPERATOR_KEYWORDS):
        return True
    fail_markers = ["aniq javob berolmayman", "не могу точно ответить", "нақты жауап бере алмаймын",
                    "bilmayman", "не знаю", "білмеймін"]
    return any(m in ai_reply.lower() for m in fail_markers)


def _build_dynamic_system_prompt() -> str:
    """AI_SYSTEM_PROMPT ga joriy sana/vaqt, kontakt, diagnostika narxlari, xona narxlari, kasalliklar va FAQ ma'lumotlarini qo'shib qaytaradi."""
    now = datetime.datetime.now(TASHKENT_TZ)
    weekday_uz = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"][now.weekday()]
    try:
        d = load_data()
    except Exception:
        d = {}

    c = d.get("contacts", {})
    contacts_block = (
        "\n\nJORIY KONTAKT MA'LUMOTLARI (bemor telefon/manzil/ish vaqti/Instagram/vebsayt so'rasa, shu yerdan TO'G'RIDAN-TO'G'RI ber):\n"
        f"- Telefon: {c.get('phone1', '')}, {c.get('phone2', '')} (qabul vaqti: 08:00–18:00)\n"
        f"- Manzil (uz): {c.get('address_uz', '')}\n"
        f"- Manzil (ru): {c.get('address_ru', '')}\n"
        f"- Manzil (kz): {c.get('address_kz', '')}\n"
        f"- Instagram: {c.get('instagram', '')}\n"
        f"- Vebsayt: {c.get('website', '')}\n"
        f"- Ish vaqti (uz): {c.get('work_hours_uz', '')}"
    )

    # ── Diagnostika narxlari ──
    try:
        diag_lines = ["MRT 1.5T narxlari:"]
        diag_lines += [f"  • {x}" for x in d.get("mrt_15", [])]
        diag_lines.append("MRT 3T narxlari (guruhlarga ko'ra):")
        for group, items in d.get("mrt_3t_groups", {}).items():
            diag_lines.append(f"  [{group}]")
            diag_lines += [f"    • {x}" for x in items]
        diag_lines.append("MSKT 256 narxlari:")
        diag_lines += [f"  • {x}" for x in d.get("mskt_256", [])]
        diag_lines.append("MSKT 128 narxlari:")
        diag_lines += [f"  • {x}" for x in d.get("mskt_128", [])]
        diag_lines.append("UZI va boshqa diagnostika:")
        diag_lines += [f"  • {x}" for x in d.get("other_diagnostics", [])]
        diag_lines.append("Laboratoriya tahlillari:")
        diag_lines += [f"  • {x}" for x in d.get("lab", [])]
        diag_block = "\n\nDIAGNOSTIKA NARXLARI (bemor diagnostika, MRT, MSKT, UZI, tahlil narxi so'rasa, AYNAN shu narxlarni ber — o'zingdan to'qima):\n" + "\n".join(diag_lines)
    except Exception:
        diag_block = ""

    # ── Xona narxlari ──
    try:
        rooms_uz = d.get("rooms_uz", [])
        room_lines = ["O'zbekiston fuqarolari uchun xona narxlari (1 kun, 1 kishi):"]
        for r in rooms_uz[:10]:  # top 10, token tejash
            room_lines.append(f"  • {r['name']} ({r['people']} kishi): katta — {r['adult']} so'm, bola — {r['child']} so'm")
        rooms_foreign = d.get("rooms_foreign", [])
        room_lines.append("Xorijiy fuqarolar uchun xona narxlari (1 kun, 1 kishi):")
        for r in rooms_foreign[:8]:
            room_lines.append(f"  • {r['name']} ({r['people']} kishi): katta — {r['adult']} so'm, bola — {r['child']} so'm")
        rooms_block = "\n\nXONA NARXLARI (bemor xona narxi, qancha turadi so'rasa — aniq raqam berish uchun shu ma'lumotdan foydalan, lekin narxlar o'zgarishi mumkin deb eslatma qo'sh):\n" + "\n".join(room_lines)
    except Exception:
        rooms_block = ""

    # ── Davolanadigan kasalliklar ──
    try:
        diseases = d.get("diseases", [])
        if diseases:
            dis_block = "\n\nDAVOLANADIGAN KASALLIKLAR RO'YXATI (bemor 'shu kasallikni davolaysizmi' deb so'rasa, shu ro'yxatdan tekshir — ro'yxatda bo'lsa 'Ha, davolaymiz', bo'lmasa operatorga yo'naltir):\n" + "\n".join(diseases[:20])
        else:
            dis_block = ""
    except Exception:
        dis_block = ""

    # ── FAQ javoblari (oddiy matn bo'lganlari) ──
    try:
        faq_uz = FAQ_DATA.get("uz", [])
        faq_lines = []
        for q, a in faq_uz:
            if isinstance(a, str) and not a.startswith("q_"):
                clean = a.replace("*", "").replace("_", "")[:300]
                faq_lines.append(f"  Savol: {q.replace('📅','').replace('💰','').replace('🧲','').strip()}\n  Javob: {clean}")
        faq_block = "\n\nKO'P SO'RALADIGAN SAVOLLAR VA JAVOBLAR (bemorga shu javoblarni ber, to'g'ri ma'lumotni o'zingdan to'qima):\n" + "\n".join(faq_lines[:6])
    except Exception:
        faq_block = ""

    # ── Bemorlar uchun qo'llanma (Guide) ──
    try:
        guide = d.get("guide", {})
        guide_block_lines = []

        for key, label in [
            ("arrival_step1", "Klinikaga joylashish 1-bosqich (ro'yxatdan o'tish)"),
            ("arrival_step2", "2-bosqich (shifokor ko'rigi)"),
            ("arrival_step3", "3-bosqich (xona tanlash va joylashish)"),
            ("malham",        "Malham — asosiy protsedura tartibi"),
            ("procedures",    "Kunlik protseduralar va kun tartibi"),
            ("infrastructure","Kompleks infratuzilmasi (korpuslar, oshxona, do'kon, WiFi)"),
            ("rules",         "Umumiy qoidalar"),
            ("shopping",      "Uyga nima sotib olish tavsiya etiladi"),
        ]:
            section = guide.get(key, {})
            uz_text = section.get("uz", "") if isinstance(section, dict) else ""
            if uz_text:
                clean = uz_text.replace("*", "").replace("_", "")[:600]
                guide_block_lines.append(f"\n[{label}]:\n{clean}")

        guide_block = "\n\nBEMOR UCHUN QO'LLANMA (bemor joylashish, Malham tartibi, kun tartibi, oshxona, kompleks, qoidalar, nima olish haqida so'rasa — AYNAN shu ma'lumotni ber, HECH QACHON o'zingdan qo'shimcha qoida, eslatma, tavsiya to'qima — masalan 'yupqa mato ustiga qo'ying', 'kuyish xavfi bor' kabi gaplar shu ma'lumotda yo'q, demak sen ham aytmasligi kerak. Faqat quyida yozilgan ma'lumotni ber, undan tashqari hech narsa qo'shma):" + "".join(guide_block_lines)
    except Exception:
        guide_block = ""

    return (
        AI_SYSTEM_PROMPT
        + f"\n\nJORIY VAQT: bugun {weekday_uz}, {now.strftime('%Y-%m-%d')}, soat {now.strftime('%H:%M')} (klinika vaqti bo'yicha). Shu ma'lumotdan foydalanib, bugun ish kuni yoki dam olish kunimi, hozir klinika ochiq yoki yopiqligini to'g'ri hisobla."
        + contacts_block
        + diag_block
        + rooms_block
        + dis_block
        + faq_block
        + guide_block
    )


def _call_anthropic_sync(user_text: str, history: list = None) -> str:
    """Anthropic Claude API ga sinxron so'rov, suhbat tarixi bilan (executor ichida ishlaydi)"""
    messages = (history or []) + [{"role": "user", "content": user_text}]
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": AI_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": AI_MODEL,
            "max_tokens": 400,
            "system": _build_dynamic_system_prompt(),
            "messages": messages,
        },
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()


def _call_openai_sync(user_text: str, history: list = None) -> str:
    """OpenAI GPT-4o API ga sinxron so'rov, suhbat tarixi bilan (executor ichida ishlaydi)"""
    messages = [{"role": "system", "content": _build_dynamic_system_prompt()}] + (history or []) + \
               [{"role": "user", "content": user_text}]
    resp = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": AI_MODEL,
            "max_tokens": 400,
            "messages": messages,
        },
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def _call_anthropic_sync_with_prompt(system_prompt: str, user_text: str) -> str:
    """Anthropic ga maxsus system prompt bilan sinxron so'rov"""
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": AI_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": AI_MODEL,
            "max_tokens": 300,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_text}],
        },
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()


def _call_openai_sync_with_prompt(system_prompt: str, user_text: str) -> str:
    """OpenAI ga maxsus system prompt bilan sinxron so'rov"""
    resp = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": AI_MODEL,
            "max_tokens": 300,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
        },
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


DIAGNOSIS_CHECK_SYSTEM_PROMPT = """Sen "Ergash Ota" klinikasining tibbiy ariza saralovchisisan (triage yordamchisi).

VAZIFANG: Bemor yozgan tashxis/shikoyat matnini o'qib, klinikamiz bu holatni qabul qilishi mumkinligini umumiy aniqlash.

KLINIKA YO'NALISHI: Jigar, o't pufagi, oshqozon-ichak va boshqa surunkali kasalliklarni jarrohliksiz, tabiiy giyohlar va "Malxam" yordamida davolash. XPN (buyrak yetishmovchiligi) faqat 1- va 2-bosqichlarini qabul qiladi.

QABUL QILINMAYDIGAN HOLATLAR: onkologiya (rak), gemodializ, XPN 3-4-5 bosqich, o'tkir jarrohlik talab qiladigan holatlar, yuqumli og'ir kasalliklar.

JAVOB FORMATI — FAQAT shu uchta variantdan birini, boshqa hech narsa qo'shmasdan qaytar:
MOS_KELADI: <qisqa, 1 gapli sabab>
MOS_KELMAYDI: <qisqa, 1 gapli sabab>
NOMA'LUM: <qisqa, 1 gapli sabab — agar matn juda umumiy/aniq bo'lmasa>

Hech qachon aniq tashxis qo'yma, dori tavsiya qilma — faqat klinikaga MOS/NOMOS ekanini bahola."""


def _parse_diagnosis_verdict(ai_raw: str) -> tuple:
    """AI javobidan (MOS_KELADI/MOS_KELMAYDI/NOMA'LUM) va sababni ajratib oladi"""
    ai_raw = ai_raw.strip()
    for verdict in ("MOS_KELMAYDI", "MOS_KELADI", "NOMA'LUM"):
        if ai_raw.upper().startswith(verdict.upper()):
            reason = ai_raw.split(":", 1)[1].strip() if ":" in ai_raw else ""
            return verdict, reason
    return "NOMA'LUM", ai_raw


async def ai_check_diagnosis(text: str) -> tuple:
    """Bemor matnini AI orqali tekshirib, (verdict, reason) qaytaradi. AI sozlanmagan bo'lsa (None, None)."""
    if not AI_API_KEY:
        return None, None
    loop = asyncio.get_running_loop()
    try:
        caller = _call_anthropic_sync_with_prompt if AI_PROVIDER == "anthropic" else _call_openai_sync_with_prompt
        raw = await loop.run_in_executor(None, caller, DIAGNOSIS_CHECK_SYSTEM_PROMPT, text)
        return _parse_diagnosis_verdict(raw)
    except Exception as e:
        logger.error(f"AI diagnosis-check xatosi: {e}")
        return None, None


DOCTOR_FOLLOWUP_NOTE = {
    "ru": "\n\n📋 При визите врачи проведут комплексное обследование и дадут окончательное заключение.",
    "uz": "\n\n📋 Klinikaga kelganingizda shifokorlar bemorni kompleks tekshirib, yakuniy xulosa beradi.",
    "kz": "\n\n📋 Клиникаға келгенде дәрігерлер науқасты кешенді тексеріп, түпкілікті қорытынды береді.",
}


def _log_ai_interaction(user, text: str, ai_reply: str, route, needs_operator: bool, lang: str):
    """Har bir AI savol-javobini /app/data/ai_logs.json ga yozadi (oxirgi 500 ta saqlanadi)."""
    try:
        logs = []
        if os.path.exists(AI_LOG_FILE):
            with open(AI_LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        logs.append({
            "time": datetime.datetime.now(TASHKENT_TZ).strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user.id,
            "username": user.username or "-",
            "lang": lang,
            "question": text,
            "answer": ai_reply,
            "route": route,
            "needs_operator": needs_operator,
        })
        logs = logs[-500:]
        with open(AI_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"AI log yozishda xato: {e}")


async def ai_administrator_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, lang: str):
    """FSM state bo'lmagan erkin matnlarga AI orqali javob beradi, kerak bo'lsa operatorga yo'naltiradi."""
    if not AI_API_KEY:
        # API kalit sozlanmagan bo'lsa — eski statik fallbackka qaytamiz
        msg = {
            "ru": "Выберите раздел в меню 👇",
            "uz": "Menyudan bo'lim tanlang 👇",
            "kz": "Мәзірден бөлім таңдаңыз 👇",
        }[lang]
        await update.message.reply_text(msg, reply_markup=main_menu_keyboard(lang, update.effective_user.id if update.effective_user else 0))
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    history = context.user_data.get("ai_history", [])

    loop = asyncio.get_running_loop()
    try:
        caller = _call_anthropic_sync if AI_PROVIDER == "anthropic" else _call_openai_sync
        ai_reply = await loop.run_in_executor(None, caller, text, history)
    except Exception as e:
        logger.error(f"AI Administrator xatosi: {e}")
        ai_reply = {
            "ru": "Извините, не смог обработать запрос.",
            "uz": "Kechirasiz, so'rovni qayta ishlay olmadim.",
            "kz": "Кешіріңіз, сұрауды өңдей алмадым.",
        }[lang]

    ai_reply, route = _extract_route(ai_reply)

    # LOKATSIYA so'ralganda — matn yubormasdan, FAQAT haqiqiy xaritadagi geo-pin yuboriladi
    if route == "menu_location":
        history = history + [{"role": "user", "content": text}, {"role": "assistant", "content": "[lokatsiya yuborildi]"}]
        context.user_data["ai_history"] = history[-6:]
        _log_ai_interaction(update.effective_user, text, "[lokatsiya yuborildi]", route, False, lang)
        await context.bot.send_location(
            chat_id=update.effective_chat.id,
            latitude=CLINIC_LATITUDE,
            longitude=CLINIC_LONGITUDE,
        )
        return

    # Suhbat tarixini yangilaymiz (oxirgi 3 juft — 6 xabar — saqlanadi)
    history = history + [{"role": "user", "content": text}, {"role": "assistant", "content": ai_reply}]
    context.user_data["ai_history"] = history[-6:]

    operator_label = {"ru": "📞 Связаться с оператором", "uz": "📞 Operatorga bog'lanish", "kz": "📞 Операторға хабарласу"}[lang]
    buttons = []
    if route:
        section_label = SECTION_BUTTON_LABELS[route][lang]
        buttons.append([InlineKeyboardButton(section_label, callback_data=route)])
    needs_op = _ai_needs_operator(text.lower(), ai_reply)
    if needs_op:
        buttons.append([InlineKeyboardButton(operator_label, callback_data="connect_operator")])
    kb = InlineKeyboardMarkup(buttons) if buttons else None

    _log_ai_interaction(update.effective_user, text, ai_reply, route, needs_op, lang)

    # ── GRELKA / MALXAMDAN KEYIN — rasm yuborish ──
    GRELKA_KEYWORDS = ["grelka", "grелка", "грелка", "malxamdan keyin", "malhamdan keyin",
                       "после малхам", "после малхама", "malxam ichgandan", "malham ichgandan"]
    text_lower = text.lower()
    if any(kw in text_lower for kw in GRELKA_KEYWORDS):
        try:
            photo_id = load_data().get("guide_step3_p3_photo", "")
            if photo_id:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_id)
        except Exception as e:
            logger.warning(f"Grelka rasm yuborishda xato: {e}")

    await update.message.reply_text(ai_reply, reply_markup=kb)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    step = context.user_data.get("booking_step")
    btype = context.user_data.get("booking_type", "statsionar")
    text = update.message.text.strip() if update.message.text else ""

    # ── BEMOR NATIJA OLISH FSM ──
    if context.user_data.get("results_step"):
        await patient_results_handler(update, context)
        return

    # ── STAFF PDF YUKLASH FSM ──
    if context.user_data.get("staff_upload_step"):
        await staff_pdf_handler(update, context)
        return

    # Ovozli xabar filtri
    if update.message.voice or update.message.audio:
        msg = {
            "ru": "📝 Для быстрого ответа напишите вопрос *текстом*.",
            "uz": "📝 Tezroq javob olish uchun savolingizni *matn* ko'rinishida yuboring.",
            "kz": "📝 Жылдам жауап алу үшін сұрағыңызды *мәтін* түрінде жіберіңіз.",
        }[lang]
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    # ── SHIFOKORGA SAVOL — matn bosqichi ──
    if context.user_data.get("state") == "DOCTOR_QUESTION_WAITING" and text and not text.startswith("/"):
        lang = get_lang(context)
        context.user_data["temp_text"] = text
        context.user_data["state"] = "DOCTOR_QUESTION_INTRO"

        add_label    = {"ru": "📸 Добавить анализ/фото",    "uz": "📸 Analiz/Rasm qo'shish",    "kz": "📸 Талдау/Сурет қосу"}[lang]
        send_label   = {"ru": "🚀 ОТПРАВИТЬ ВРАЧУ",         "uz": "🚀 SHIFOKORGA YUBORISH",     "kz": "🚀 ДӘРІГЕРГЕ ЖІБЕРУ"}[lang]
        cancel_label = {"ru": "❌ Отмена",                  "uz": "❌ Bekor qilish",             "kz": "❌ Болдырмау"}[lang]
        confirm_text = {
            "ru": (
                "📋 <b>Ваш вопрос получен:</b>\n\n"
                f"<i>{text[:500]}</i>\n\n"
                "Что делаем дальше?"
            ),
            "uz": (
                "📋 <b>Savolingiz qabul qilindi:</b>\n\n"
                f"<i>{text[:500]}</i>\n\n"
                "Keyin nima qilamiz?"
            ),
            "kz": (
                "📋 <b>Сұрағыңыз қабылданды:</b>\n\n"
                f"<i>{text[:500]}</i>\n\n"
                "Əрі қарай не істейміз?"
            ),
        }[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(add_label,    callback_data="add_medical_photo")],
            [InlineKeyboardButton(send_label,   callback_data="send_to_doctor_now")],
            [InlineKeyboardButton(cancel_label, callback_data="cancel_doctor_question")],
        ])
        await update.message.reply_text(confirm_text, parse_mode="HTML", reply_markup=kb)
        return

    # ── SHIFOKORGA SAVOL — rasm bosqichi ──
    if context.user_data.get("state") == "DOCTOR_MEDIA_WAITING":
        lang = get_lang(context)
        if update.message.photo:
            photo_id = update.message.photo[-1].file_id
            context.user_data.setdefault("temp_photos", []).append(photo_id)
            count = len(context.user_data["temp_photos"])
            done_label   = {"ru": f"✅ Готово ({count} фото) — отправить", "uz": f"✅ Tayyor ({count} rasm) — yuborish", "kz": f"✅ Дайын ({count} сурет) — жіберу"}[lang]
            cancel_label = {"ru": "❌ Отмена", "uz": "❌ Bekor qilish", "kz": "❌ Болдырмау"}[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(done_label,   callback_data="send_to_doctor_now")],
                [InlineKeyboardButton(cancel_label, callback_data="cancel_doctor_question")],
            ])
            added = {"ru": f"✅ Фото {count} добавлено.", "uz": f"✅ {count}-rasm qo'shildi.", "kz": f"✅ {count} сурет қосылды."}[lang]
            await update.message.reply_text(added, reply_markup=kb)
        return

    # ── TAKLIF VA SHIKOYAT ──
    if context.user_data.get("state") == "FEEDBACK_WAITING" and text and not text.startswith("/"):
        user = update.effective_user
        username = f"@{user.username}" if user.username else "—"
        lang = get_lang(context)

        # Kalit so'zlar filtri
        BLOCKED_KEYWORDS = [
            "og'riq", "ogriq", "kasal", "shifokor", "doktor", "dori",
            "mrt", "mskt", "tosh", "parhez", "davolash", "bol", "vrach",
            "lechenie", "болит", "боль", "врач", "лечение", "таблетки",
            "диагноз", "диагноз", "ауру", "дәрі",
        ]
        text_lower = text.lower()
        if any(kw in text_lower for kw in BLOCKED_KEYWORDS):
            context.user_data["state"] = None
            warn = {
                "ru": "⛔️ Этот раздел только для предложений и жалоб!\n\nВопросы о болезнях, лечении или приёме врача отправляйте в соответствующие разделы.",
                "uz": "⛔️ Bu bo'lim faqat takliflar uchun!\n\nKasallik yoki shifokor qabuli bo'yicha savollarni tegishli bo'limlarga yuboring.",
                "kz": "⛔️ Бұл бөлім тек ұсыныстар үшін!\n\nАуру немесе дәрігер қабылдауы туралы сұрақтарды тиісті бөлімдерге жіберіңіз.",
            }[lang]
            await update.message.reply_text(warn, reply_markup=main_menu_keyboard(lang, update.effective_user.id if update.effective_user else 0))
            return

        feedback_msg = (
            f"✍️ <b>Yangi taklif/shikoyat:</b>\n"
            f"👤 Bemor ID: {user.id}  uid:{user.id}\n"
            f"💬 Telegram: {username}\n"
            f"📝 Matn: {text}"
        )
        try:
            await context.bot.send_message(
                chat_id=FEEDBACK_GROUP_ID,
                text=feedback_msg,
                parse_mode="HTML"
            )
            context.user_data["state"] = None
            confirm = {
                "ru": "✅ Ваше сообщение принято! Спасибо за обратную связь.",
                "uz": "✅ Xabaringiz qabul qilindi! Fikr-mulohazangiz uchun rahmat.",
                "kz": "✅ Хабарыңыз қабылданды! Пікіріңіз үшін рахмет.",
            }[lang]
            back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="menu_guide")]])
            await update.message.reply_text(confirm, reply_markup=kb)
        except Exception as e:
            logger.error(f"Feedback yuborish xatosi: {e}")
            await update.message.reply_text("❌ Xabar yuborishda xatolik yuz berdi.")
        return

    # ── TIBBIY MUROJAAT — matn saqlash ──
    if context.user_data.get("med_state") is not None and \
       not context.user_data.get("calc_step") and \
       not context.user_data.get("booking_step"):
        med = context.user_data.get("med_state", {})
        if isinstance(med, dict) and text and not text.startswith("/"):
            med["bemor_matni"] = text
            context.user_data["med_state"] = med
            lang = get_lang(context)
            confirm_label = {"ru": "✅ Подтвердить и отправить", "uz": "✅ Tasdiqlash va yuborish", "kz": "✅ Растау және жіберу"}[lang]
            cancel_label = {"ru": "⬅️ Отмена", "uz": "⬅️ Bekor qilish", "kz": "⬅️ Бас тарту"}[lang]
            saved = {"ru": "✍️ Текст сохранён. Добавьте фото или отправьте.", "uz": "✍️ Matn saqlandi. Rasm qo'shing yoki yuboring.", "kz": "✍️ Мәтін сақталды. Сурет қосыңыз немесе жіберіңіз."}[lang]
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(confirm_label, callback_data="confirm_medical")],
                [InlineKeyboardButton(cancel_label, callback_data="disease_not_found")],
            ])
            await update.message.reply_text(saved, reply_markup=kb)
            return

    # ── NARX HISOBLASH — "Boshqa muddat" kiritish ──
    if context.user_data.get("calc_step") == "waiting_days":
        context.user_data["calc_step"] = None  # reset
        cit = context.user_data.get("calc_cit", "uz")
        age = context.user_data.get("calc_age", "adult")
        idx = context.user_data.get("calc_room_idx", 0)

        # Faqat musbat butun son qabul qilinadi
        if not text.isdigit() or int(text) <= 0:
            err = {
                "ru": "❌ Пожалуйста, введите *число больше 0* (только цифры, без букв).",
                "uz": "❌ Iltimos, faqat *musbat son* kiriting (harflar emas, faqat raqam).",
                "kz": "❌ Өтінеміз, тек *оң сан* енгізіңіз (әріп емес, тек сан).",
            }[lang]
            back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(
                back_label, callback_data=f"calc_room_{cit}_{age}_{idx}")]])
            await update.message.reply_text(err, parse_mode="Markdown", reply_markup=kb)
            context.user_data["calc_step"] = "waiting_days"  # qayta kutish
            return

        days = int(text)
        d = load_data()
        rooms = d["rooms_uz"] if cit == "uz" else d["rooms_foreign"]
        room = rooms[idx]
        price_str = room["adult"] if age == "adult" else room["child"]
        price_num = int(price_str.replace(" ", "").replace("\u00a0", ""))
        total = price_num * days

        def fmt(n):
            return f"{n:,}".replace(",", " ")

        narx_word = {"ru": "сум", "uz": "so'm", "kz": "сум"}[lang]
        kishi_word = {"ru": "чел.", "uz": "kishi", "kz": "адам"}[lang]
        cit_label = {
            "ru": {"uz": "Граждане Узбекистана", "foreign": "Иностранные граждане"}[cit],
            "uz": {"uz": "O'zbekiston fuqarolari", "foreign": "Chet el fuqarolari"}[cit],
            "kz": {"uz": "Өзбекстан азаматтары", "foreign": "Шетел азаматтары"}[cit],
        }[lang]
        age_label = {
            "ru": {"adult": "Взрослые", "child": "Дети (до 10 лет)"}[age],
            "uz": {"adult": "Kattalar", "child": "Bolalar (10 yoshgacha)"}[age],
            "kz": {"adult": "Ересектер", "child": "Балалар (10 жасқа дейін)"}[age],
        }[lang]
        day_word = {"ru": "дней", "uz": "kun", "kz": "күн"}[lang]
        day_word1 = {"ru": "день", "uz": "kun", "kz": "күн"}[lang]

        # Narx >= 340 000: Fizioterapiya+manual terapiya + MRT kiradi
        # Narx < 340 000: faqat Fizioterapiya (manual terapiya yo'q), MRT yo'q
        if price_num >= 340000:
            included = {
                "ru": "✔ Проживание\n✔ Лечение\n✔ Физиотерапия и мануальная терапия\n✔ УЗИ, анализ крови, ЭКГ\n✔ МРТ 1.5Т или МСКТ — 1 орган",
                "uz": "✔ Turar joy\n✔ Davolanish\n✔ Fizioterapiya va manual terapiya\n✔ UZI, qon tahlili, EKG\n✔ MRT 1.5T yoki MSKT — 1 organ",
                "kz": "✔ Тұрғын үй\n✔ Емдеу\n✔ Физиотерапия және мануалды терапия\n✔ УДЗ, қан анализі, ЭКГ\n✔ МРТ 1.5Т немесе МСКТ — 1 орган",
            }[lang]
        else:
            included = {
                "ru": "✔ Проживание\n✔ Лечение\n✔ Физиотерапия\n✔ УЗИ, анализ крови, ЭКГ",
                "uz": "✔ Turar joy\n✔ Davolanish\n✔ Fizioterapiya\n✔ UZI, qon tahlili, EKG",
                "kz": "✔ Тұрғын үй\n✔ Емдеу\n✔ Физиотерапия\n✔ УДЗ, қан анализі, ЭКГ",
            }[lang]
        extra = {
            "ru": "МРТ 3Т, МСКТ 256, Маммография, Криолиполиз, Растяжка, Ударно-волновая терапия",
            "uz": "MRT 3T, MSKT 256, Mammografiya, Kriolipoliz, Cho'zilish, Zarba-to'lqin terapiyasi",
            "kz": "МРТ 3Т, МСКТ 256, Маммография, Криолиполиз, Созылу, Соққы-толқын терапиясы",
        }[lang]

        result = {
            "ru": f"✅ *Результат расчёта*\n\n🏨 *{room['name']}* ({room['people']} {kishi_word})\n👤 {cit_label} | {age_label}\n💰 1 {day_word1}: *{fmt(price_num)} {narx_word}*\n📅 Срок: *{days} {day_word}*\n\n💳 *Итого: {fmt(total)} {narx_word}*\n\n📦 *В стоимость входит:*\n{included}\n\n➕ *Дополнительно:*\n_{extra}_\n\n📌 Точный срок лечения определяется врачом после осмотра.",
            "uz": f"✅ *Hisoblash natijasi*\n\n🏨 *{room['name']}* ({room['people']} {kishi_word})\n👤 {cit_label} | {age_label}\n💰 1 {day_word1}: *{fmt(price_num)} {narx_word}*\n📅 Muddat: *{days} {day_word}*\n\n💳 *Jami: {fmt(total)} {narx_word}*\n\n📦 *Narx tarkibiga kiradi:*\n{included}\n\n➕ *Qo'shimcha xizmatlar alohida:*\n_{extra}_\n\n📌 Aniq davolanish muddati shifokor ko'rigidan keyin belgilanadi.",
            "kz": f"✅ *Есептеу нәтижесі*\n\n🏨 *{room['name']}* ({room['people']} {kishi_word})\n👤 {cit_label} | {age_label}\n💰 1 {day_word1}: *{fmt(price_num)} {narx_word}*\n📅 Мерзім: *{days} {day_word}*\n\n💳 *Жиыны: {fmt(total)} {narx_word}*\n\n📦 *Құнға кіреді:*\n{included}\n\n➕ *Қосымша қызметтер жеке:*\n_{extra}_\n\n📌 Нақты емдеу мерзімі дәрігер тексерісінен кейін белгіленеді.",
        }[lang]

        book_label = {"ru": "📞 Записаться", "uz": "📞 Qabulga yozilish", "kz": "📞 Жазылу"}[lang]
        operator_label = {"ru": "💬 Оператор", "uz": "💬 Operator", "kz": "💬 Оператор"}[lang]
        recalc_label = {"ru": "🔁 Пересчитать", "uz": "🔁 Qayta hisoblash", "kz": "🔁 Қайта есептеу"}[lang]
        back_label = {"ru": "🔙 Назад", "uz": "🔙 Orqaga", "kz": "🔙 Артқа"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(book_label, callback_data="menu_booking"),
             InlineKeyboardButton(operator_label, callback_data="menu_operator")],
            [InlineKeyboardButton(recalc_label, callback_data="calc_start")],
            [InlineKeyboardButton(back_label, callback_data=f"calc_room_{cit}_{age}_{idx}")],
        ])
        await update.message.reply_text(result, parse_mode="Markdown", reply_markup=kb)
        return

    # ── TRANSFER FLOW ──
    if btype == "transfer" and step:
        if step == "transfer_from":
            context.user_data.setdefault("booking", {})["from"] = text
            context.user_data["booking_step"] = "transfer_sana"
            ask = {
                "ru": f"📍 *Откуда:* {text}\n\n📅 Шаг 2/4\nНапишите *дату приезда:*",
                "uz": f"📍 *Qayerdan:* {text}\n\n📅 2/4 qadam\n*Kelish sanasini* yozing:",
                "kz": f"📍 *Қайдан:* {text}\n\n📅 2/4 қадам\n*Келу күнін* жазыңыз:",
            }[lang]
            await update.message.reply_text(ask, parse_mode="Markdown")
            return

        if step == "transfer_sana":
            context.user_data.setdefault("booking", {})["sana"] = text
            context.user_data["booking_step"] = "transfer_kishi"
            ask = {
                "ru": f"📅 *Дата:* {text}\n\n👥 Шаг 3/4\nСколько *человек?*",
                "uz": f"📅 *Sana:* {text}\n\n👥 3/4 qadam\nNecha *kishi?*",
                "kz": f"📅 *Күні:* {text}\n\n👥 3/4 қадам\nНеше *адам?*",
            }[lang]
            await update.message.reply_text(ask, parse_mode="Markdown")
            return

        if step == "transfer_kishi":
            context.user_data.setdefault("booking", {})["kishi"] = text
            context.user_data["booking_step"] = "transfer_phone"
            ask = {
                "ru": f"👥 *{text} чел.*\n\n📞 Шаг 4/4\nНапишите *номер телефона:*",
                "uz": f"👥 *{text} kishi*\n\n📞 4/4 qadam\n*Telefon raqamingizni* yozing:",
                "kz": f"👥 *{text} адам*\n\n📞 4/4 қадам\n*Телефон нөміріңізді* жазыңыз:",
            }[lang]
            await update.message.reply_text(ask, parse_mode="Markdown")
            return

        if step == "transfer_phone":
            context.user_data.setdefault("booking", {})["phone"] = text
            context.user_data["booking_step"] = None
            booking = context.user_data.get("booking", {})
            summary = {
                "ru": (f"📋 *Проверьте данные:*\n\n"
                       f"📍 Откуда: {booking.get('from')}\n"
                       f"📅 Дата: {booking.get('sana')}\n"
                       f"👥 Человек: {booking.get('kishi')}\n"
                       f"📞 Телефон: {text}\n\nВсё верно?"),
                "uz": (f"📋 *Ma'lumotlarni tekshiring:*\n\n"
                       f"📍 Qayerdan: {booking.get('from')}\n"
                       f"📅 Sana: {booking.get('sana')}\n"
                       f"👥 Kishi: {booking.get('kishi')}\n"
                       f"📞 Telefon: {text}\n\nHammasi to'g'rimi?"),
                "kz": (f"📋 *Деректерді тексеріңіз:*\n\n"
                       f"📍 Қайдан: {booking.get('from')}\n"
                       f"📅 Күні: {booking.get('sana')}\n"
                       f"👥 Адам: {booking.get('kishi')}\n"
                       f"📞 Телефон: {text}\n\nБәрі дұрыс па?"),
            }[lang]
            await update.message.reply_text(summary, parse_mode="Markdown",
                                            reply_markup=confirm_keyboard(lang))
            return

    # ── EXCURSION FLOW ──
    if btype == "excursion" and step:
        if step == "excursion_sana":
            context.user_data.setdefault("booking", {})["sana"] = text
            context.user_data["booking_step"] = "excursion_kishi"
            ask = {
                "ru": f"📅 *Дата:* {text}\n\n👥 Шаг 2/3\nСколько *человек?*",
                "uz": f"📅 *Sana:* {text}\n\n👥 2/3 qadam\nNecha *kishi?*",
                "kz": f"📅 *Күні:* {text}\n\n👥 2/3 қадам\nНеше *адам?*",
            }[lang]
            await update.message.reply_text(ask, parse_mode="Markdown")
            return

        if step == "excursion_kishi":
            context.user_data.setdefault("booking", {})["kishi"] = text
            context.user_data["booking_step"] = "excursion_phone"
            ask = {
                "ru": f"👥 *{text} чел.*\n\n📞 Шаг 3/3\nНапишите *номер телефона:*",
                "uz": f"👥 *{text} kishi*\n\n📞 3/3 qadam\n*Telefon raqamingizni* yozing:",
                "kz": f"👥 *{text} адам*\n\n📞 3/3 қадам\n*Телефон нөміріңізді* жазыңыз:",
            }[lang]
            await update.message.reply_text(ask, parse_mode="Markdown")
            return

        if step == "excursion_phone":
            context.user_data.setdefault("booking", {})["phone"] = text
            context.user_data["booking_step"] = None
            booking = context.user_data.get("booking", {})
            summary = {
                "ru": (f"📋 *Проверьте данные:*\n\n"
                       f"🕌 Направление: {booking.get('city')}\n"
                       f"📅 Дата: {booking.get('sana')}\n"
                       f"👥 Человек: {booking.get('kishi')}\n"
                       f"📞 Телефон: {text}\n\nВсё верно?"),
                "uz": (f"📋 *Ma'lumotlarni tekshiring:*\n\n"
                       f"🕌 Yo'nalish: {booking.get('city')}\n"
                       f"📅 Sana: {booking.get('sana')}\n"
                       f"👥 Kishi: {booking.get('kishi')}\n"
                       f"📞 Telefon: {text}\n\nHammasi to'g'rimi?"),
                "kz": (f"📋 *Деректерді тексеріңіз:*\n\n"
                       f"🕌 Бағыт: {booking.get('city')}\n"
                       f"📅 Күні: {booking.get('sana')}\n"
                       f"👥 Адам: {booking.get('kishi')}\n"
                       f"📞 Телефон: {text}\n\nБәрі дұрыс па?"),
            }[lang]
            await update.message.reply_text(summary, parse_mode="Markdown",
                                            reply_markup=confirm_keyboard(lang))
            return

    # ── STATSIONAR FLOW ──
    if btype == "statsionar" and step:

        if step == "name":
            # ── KASALLIK FILTRI: XPN faqat 1-2 bosqich, og'ir holatlar qabul qilinmaydi ──
            STOP_DISEASES = [
                'gemodializ', 'гемодиализ', 'rak', 'рак', 'onkologiya', 'онкология',
                '3-bosqich', '3 bosqich', '3 стадия', '4-bosqich', '4 bosqich', '4 стадия',
                '5-bosqich', '5 bosqich', '5 стадия', 'терминальная',
            ]
            text_lower = text.lower()
            if any(stop in text_lower for stop in STOP_DISEASES):
                reject = {
                    "uz": "⚠️ Kechirasiz, klinikamiz XPN (buyrak yetishmovchiligi) kasalligining faqat 1- va 2-boshlang'ich bosqichlarini davolaydi. Og'irroq bosqichlar, gemodializ yoki onkologik holatlar qabul qilinmaydi.",
                    "ru": "⚠️ К сожалению, наша клиника лечит только начальные 1-ю и 2-ю стадии ХПН. Пациенты с более тяжелыми стадиями, на гемодиализе или с онкологией не принимаются.",
                    "kz": "⚠️ Кешіріңіз, біздің клиника ХБЖ (бүйрек жеткіліксіздігі) ауруының тек 1-ші және 2-ші бастапқы кезеңдерін емдейді. Ауырлау кезеңдер, гемодиализ немесе онкологиялық жағдайлар қабылданбайды.",
                }[lang]
                context.user_data["booking"] = {}
                context.user_data["booking_step"] = None
                context.user_data["booking_type"] = None
                await update.message.reply_text(reject, reply_markup=back_keyboard(lang))
                return

            # ── AI orqali qo'shimcha tekshiruv (so'z-filtrdan o'tgan, lekin murakkabroq holatlar uchun) ──
            verdict, reason = await ai_check_diagnosis(text)
            if verdict == "MOS_KELMAYDI":
                ai_reject = {
                    "uz": f"⚠️ Kechirasiz, klinikamiz bu holatni qabul qila olmaydi.\n\n💬 {reason}",
                    "ru": f"⚠️ К сожалению, наша клиника не может принять этот случай.\n\n💬 {reason}",
                    "kz": f"⚠️ Кешіріңіз, біздің клиника бұл жағдайды қабылдай алмайды.\n\n💬 {reason}",
                }[lang]
                context.user_data["booking"] = {}
                context.user_data["booking_step"] = None
                context.user_data["booking_type"] = None
                await update.message.reply_text(ai_reject, reply_markup=back_keyboard(lang))
                return
            elif verdict == "MOS_KELADI":
                pre_info = {
                    "uz": f"✅ {reason}" + DOCTOR_FOLLOWUP_NOTE["uz"],
                    "ru": f"✅ {reason}" + DOCTOR_FOLLOWUP_NOTE["ru"],
                    "kz": f"✅ {reason}" + DOCTOR_FOLLOWUP_NOTE["kz"],
                }[lang]
                await update.message.reply_text(pre_info)
            # verdict == "NOMA'LUM" yoki AI sozlanmagan (None) bo'lsa — jim davom etamiz, ariza odatdagidek ketadi

            context.user_data.setdefault("booking", {})["name"] = text
            context.user_data["booking_step"] = "sana"
            ask = {
                "ru": f"👤 *{text}*\n\n📅 Шаг 2/5\nНапишите *дату приезда*:\n_(например: 15 июня или 15.06)_",
                "uz": f"👤 *{text}*\n\n📅 2/5 qadam\n*Kelish sanasini* yozing:\n_(masalan: 15 iyun yoki 15.06)_",
                "kz": f"👤 *{text}*\n\n📅 2/5 қадам\n*Келу күнін* жазыңыз:\n_(мысалы: 15 маусым немесе 15.06)_",
            }[lang]
            await update.message.reply_text(ask, parse_mode="Markdown")
            return

        if step == "sana":
            context.user_data.setdefault("booking", {})["sana"] = text
            booking = context.user_data.get("booking", {})

            # Agar calc dan kelgan bo'lsa — kishi soni oldin tanlangan
            if booking.get("from_calc"):
                context.user_data["booking_step"] = "phone"
                ask = {
                    "ru": f"📅 *{text}*\n\n📞 Шаг 3/4\nНапишите *номер телефона*:",
                    "uz": f"📅 *{text}*\n\n📞 3/4 qadam\n*Telefon raqamingizni* yozing:",
                    "kz": f"📅 *{text}*\n\n📞 3/4 қадам\n*Телефон нөміріңізді* жазыңыз:",
                }[lang]
            else:
                context.user_data["booking_step"] = "kishi"
                ask = {
                    "ru": f"📅 *{text}*\n\n👥 Шаг 3/5\nСколько *человек* приедет?",
                    "uz": f"📅 *{text}*\n\n👥 3/5 qadam\nNecha *kishi* keladi?",
                    "kz": f"📅 *{text}*\n\n👥 3/5 қадам\nНеше *адам* келеді?",
                }[lang]
            await update.message.reply_text(ask, parse_mode="Markdown")
            return

        if step == "kishi":
            context.user_data.setdefault("booking", {})["kishi"] = text
            context.user_data["booking_step"] = "phone"
            ask = {
                "ru": f"👥 *{text} чел.*\n\n📞 Шаг 4/5\nНапишите *номер телефона*:",
                "uz": f"👥 *{text} kishi*\n\n📞 4/5 qadam\n*Telefon raqamingizni* yozing:",
                "kz": f"👥 *{text} адам*\n\n📞 4/5 қадам\n*Телефон нөміріңізді* жазыңыз:",
            }[lang]
            await update.message.reply_text(ask, parse_mode="Markdown")
            return

        if step == "phone":
            context.user_data.setdefault("booking", {})["phone"] = text
            booking = context.user_data.get("booking", {})

            # Agar calc dan kelgan bo'lsa — xona so'ralmaydi
            if booking.get("from_calc"):
                context.user_data["booking_step"] = None
                narx_word_s = "so'm" if lang == "uz" else ("сум" if lang in ("ru", "kz") else "so'm")
                summary = {
                    "ru": (
                        f"📋 *Проверьте данные:*\n\n"
                        f"👤 Имя: {booking.get('name')}\n"
                        f"📅 Дата: {booking.get('sana')}\n"
                        f"👥 Человек: {booking.get('calc_people', '—')}\n"
                        f"📞 Телефон: {text}\n"
                        f"🏨 Палата: {booking.get('calc_room')}\n"
                        f"💰 1 день: {booking.get('calc_price')}\n"
                        f"📅 Дней: {booking.get('calc_days')}\n"
                        f"✅ Итого: {booking.get('calc_total')}\n\n"
                        f"Всё верно?"
                    ),
                    "uz": (
                        f"📋 *Ma'lumotlarni tekshiring:*\n\n"
                        f"👤 Ism: {booking.get('name')}\n"
                        f"📅 Sana: {booking.get('sana')}\n"
                        f"👥 Kishi: {booking.get('calc_people', '—')}\n"
                        f"📞 Telefon: {text}\n"
                        f"🏨 Xona: {booking.get('calc_room')}\n"
                        f"💰 1 kun: {booking.get('calc_price')}\n"
                        f"📅 Kun: {booking.get('calc_days')}\n"
                        f"✅ Jami: {booking.get('calc_total')}\n\n"
                        f"Hammasi to'g'rimi?"
                    ),
                    "kz": (
                        f"📋 *Деректерді тексеріңіз:*\n\n"
                        f"👤 Аты: {booking.get('name')}\n"
                        f"📅 Күні: {booking.get('sana')}\n"
                        f"👥 Адам: {booking.get('calc_people', '—')}\n"
                        f"📞 Телефон: {text}\n"
                        f"🏨 Палата: {booking.get('calc_room')}\n"
                        f"💰 1 күн: {booking.get('calc_price')}\n"
                        f"📅 Күн: {booking.get('calc_days')}\n"
                        f"✅ Жиыны: {booking.get('calc_total')}\n\n"
                        f"Бәрі дұрыс па?"
                    ),
                }[lang]
                await update.message.reply_text(summary, parse_mode="Markdown",
                                                reply_markup=confirm_keyboard(lang))
                return

            # Oddiy statsionar — xona so'rash (5-qadam)
            context.user_data["booking_step"] = "xona"
            ask = {
                "ru": f"📞 *{text}*\n\n🛏 Шаг 5/5\nКакой *тип номера* вас интересует?\n_(например: Люкс, VIP, Стандарт или напишите 'не знаю')_",
                "uz": f"📞 *{text}*\n\n🛏 5/5 qadam\nQaysi *xona turi* qiziqtiradi?\n_(masalan: Lyuks, VIP, Standart yoki 'bilmayman' deb yozing)_",
                "kz": f"📞 *{text}*\n\n🛏 5/5 қадам\nҚандай *бөлме түрі* қызықтырады?\n_(мысалы: Люкс, VIP немесе 'білмеймін' деп жазыңыз)_",
            }[lang]
            await update.message.reply_text(ask, parse_mode="Markdown")
            return

        if step == "xona":
            context.user_data.setdefault("booking", {})["xona"] = text
            context.user_data["booking_step"] = None
            # ... booking ma'lumotlari saqlandi, ogohlantirishli xabar yuboriladi
            warning = {
                "ru": (
                    f"📋 *Ваше пожелание по номеру принято!*\n\n"
                    f"⚠️ *Важное примечание (обратите внимание):*\n"
                    f"Выбор типа номера — это *не 100% бронирование*.\n\n"
                    f"*Как проходит размещение?*\n"
                    f"1. Если в день приезда запрошенный вами номер *свободен* — вы получите его первым.\n"
                    f"2. Если номер *занят другими пациентами* — вас временно разместят в свободное место, "
                    f"а как только нужный номер освободится — сразу переселят.\n\n"
                    f"Спасибо за понимание! Запись к врачу успешно завершена."
                ),
                "uz": (
                    f"📋 *Sizning xona bo'yicha istagingiz qabul qilindi!*\n\n"
                    f"⚠️ *Muhim eslatma (E'tibor bering):*\n"
                    f"Xona turini tanlashingiz — bu xonani *100% oldindan band qilish (bron qilish) degani emas*.\n\n"
                    f"*Joylashtirish tartibi qanday bo'ladi?*\n"
                    f"1. Siz kelgan kuni so'ragan xona turi *bo'sh bo'lsa*, birinchilardan bo'lib aynan sizga taqdim etiladi.\n"
                    f"2. Agar u xona *boshqa bemorlar bilan band bo'lsa*, sizni vaqtinchalik mavjud bo'sh joyga joylashtiramiz "
                    f"va xona bo'shashi bilan darhol o'zingiz xohlagan xonaga o'tkazib beramiz.\n\n"
                    f"Ko'rsatgan to'g'ri tushunchangiz uchun tashakkur! Shifokor qabuliga yozilish jarayoni muvaffaqiyatli yakunlandi."
                ),
                "kz": (
                    f"📋 *Бөлме бойынша тілегіңіз қабылданды!*\n\n"
                    f"⚠️ *Маңызды ескерту (назар аударыңыз):*\n"
                    f"Бөлме түрін таңдау — бұл бөлмені *100% алдын ала брондау дегенді білдірмейді*.\n\n"
                    f"*Орналастыру тәртібі қандай?*\n"
                    f"1. Келген күні сұраған бөлмеңіз *бос болса* — ең бірінші болып сізге ұсынылады.\n"
                    f"2. Егер бөлме *басқа науқастармен бос болмаса* — сізді уақытша бос орынға орналастырамыз, "
                    f"бөлме босаған бетте дереу ауыстырып береміз.\n\n"
                    f"Түсінушілігіңіз үшін рахмет! Дәрігер қабылдауына жазылу сәтті аяқталды."
                ),
            }[lang]
            await update.message.reply_text(warning, parse_mode="Markdown")

            # Lid kanalga yuborish
            booking = context.user_data.get("booking", {})
            user = update.effective_user
            username = f"@{user.username}" if user.username else "—"
            lid = (
                f"🏥 *STATSIONAR LID*\n\n"
                f"👤 Ism: {booking.get('name', '—')}\n"
                f"📅 Kelish sanasi: {booking.get('sana', '—')}\n"
                f"👥 Kishi soni: {booking.get('kishi', '—')}\n"
                f"📞 Telefon: {booking.get('phone', '—')}\n"
                f"🛏 Xona turi: {booking.get('xona', '—')}\n"
                f"💬 Telegram: {username}\n"
                f"🆔 uid:{user.id}\n"
                f"🌐 Til: {lang.upper()}\n\n"
                f"🟢 QO'NG'IROQ QILING!"
            )
            await send_lid(context, STATSIONAR_CHANNEL, lid)
            save_statsionar_lid(
                name=booking.get("name", "—"),
                phone=booking.get("phone", "—"),
                sana_text=booking.get("sana", ""),
                kasallik="",
                xona=booking.get("xona", "—"),
            )
            context.user_data["booking"] = {}
            context.user_data["booking_step"] = None
            context.user_data["booking_type"] = None
            return

    # ── DIAGNOSTIKA FLOW ──
    if btype == "diagnostika" and step:

        if step == "name":
            context.user_data.setdefault("booking", {})["name"] = text
            context.user_data["booking_step"] = "phone"
            ask = {
                "ru": f"👤 *{text}*\n\n📞 Шаг 2/3\nНапишите *номер телефона*:",
                "uz": f"👤 *{text}*\n\n📞 2/3 qadam\n*Telefon raqamingizni* yozing:",
                "kz": f"👤 *{text}*\n\n📞 2/3 қадам\n*Телефон нөміріңізді* жазыңыз:",
            }[lang]
            await update.message.reply_text(ask, parse_mode="Markdown")
            return

        if step == "phone":
            context.user_data.setdefault("booking", {})["phone"] = text
            context.user_data["booking_step"] = None
            booking = context.user_data.get("booking", {})
            summary = {
                "ru": (
                    f"📋 *Проверьте данные:*\n\n"
                    f"👤 Имя: {booking.get('name')}\n"
                    f"🔬 Услуга: {booking.get('service')}\n"
                    f"📞 Телефон: {text}\n\n"
                    f"Всё верно?"
                ),
                "uz": (
                    f"📋 *Ma'lumotlarni tekshiring:*\n\n"
                    f"👤 Ism: {booking.get('name')}\n"
                    f"🔬 Xizmat: {booking.get('service')}\n"
                    f"📞 Telefon: {text}\n\n"
                    f"Hammasi to'g'rimi?"
                ),
                "kz": (
                    f"📋 *Деректерді тексеріңіз:*\n\n"
                    f"👤 Аты: {booking.get('name')}\n"
                    f"🔬 Қызмет: {booking.get('service')}\n"
                    f"📞 Телефон: {text}\n\n"
                    f"Бәрі дұрыс па?"
                ),
            }[lang]
            await update.message.reply_text(summary, parse_mode="Markdown",
                                            reply_markup=confirm_keyboard(lang))
            return

    # Salomlashuvni kesish
    greet_words = ["салам", "привет", "salom", "hi", "hello", "assalom", "здравствуй", "добрый"]
    if any(w in text.lower() for w in greet_words):
        msg = {
            "ru": "👋 Здравствуйте! Выберите нужный раздел:",
            "uz": "👋 Xush kelibsiz! Kerakli bo'limni tanlang:",
            "kz": "👋 Сәлем! Қажетті бөлімді таңдаңыз:",
        }[lang]
        await update.message.reply_text(msg, reply_markup=main_menu_keyboard(lang, update.effective_user.id if update.effective_user else 0))
        return

    # Boshqa matnlar — AI Administrator orqali javob beramiz
    await ai_administrator_handler(update, context, text, lang)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_handler))
    app.add_handler(CommandHandler("ai_logs", ai_logs_handler))
    app.add_handler(CommandHandler("ertaga", ertaga_handler))
    app.add_handler(CommandHandler("lidlar_debug", lidlar_debug_handler))
    app.add_handler(CommandHandler("lid_add", lid_add_handler))
    app.add_handler(CommandHandler("lidlar_fix", lidlar_fix_handler))
    app.add_handler(CommandHandler("results_debug", results_debug_handler))
    app.add_handler(CommandHandler("admin_help", admin_handler))
    app.add_handler(CommandHandler("admin_photo", admin_handler))
    app.add_handler(CommandHandler("admin_photo_clear", admin_handler))
    app.add_handler(CommandHandler("admin_photo_del", admin_handler))
    app.add_handler(CommandHandler("admin_video_clear", admin_handler))
    app.add_handler(CommandHandler("admin_video_del", admin_handler))
    app.add_handler(CommandHandler("admin_check_team", admin_handler))
    app.add_handler(CommandHandler("admin_team_clear", admin_handler))
    app.add_handler(CommandHandler("admin_reset_rules", admin_handler))
    app.add_handler(CommandHandler("admin_video", admin_handler))
    app.add_handler(CommandHandler("stats", admin_handler))
    app.add_handler(CommandHandler("broadcast", admin_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(ALLOWED_STAFF), staff_pdf_handler))
    app.add_handler(MessageHandler(filters.PHOTO & filters.User(ADMIN_ID), photo_handler))
    app.add_handler(MessageHandler(filters.VIDEO & filters.User(ADMIN_ID), video_handler))
    app.add_handler(MessageHandler(filters.VIDEO & ~filters.User([ADMIN_ID] + ALLOWED_STAFF), medical_doc_handler))
    app.add_handler(MessageHandler(filters.PHOTO & ~filters.User([ADMIN_ID] + ALLOWED_STAFF), medical_doc_handler))
    app.add_handler(MessageHandler(filters.Document.ALL & ~filters.User([ADMIN_ID] + ALLOWED_STAFF), medical_doc_handler))
    app.add_handler(MessageHandler(filters.VOICE & ~filters.User(ADMIN_ID), medical_voice_handler))
    app.add_handler(MessageHandler(filters.Chat(DOCTORS_GROUP_ID) & filters.REPLY, doctor_reply_handler))
    app.add_handler(MessageHandler(filters.Chat(DOCTORS_GROUP_ID) & filters.VOICE & filters.REPLY, doctor_reply_handler))
    app.add_handler(MessageHandler(filters.Chat(STATSIONAR_CHANNEL) & filters.REPLY, doctor_reply_handler))
    app.add_handler(MessageHandler(filters.Chat(DIAGNOSTIKA_CHANNEL) & filters.REPLY, doctor_reply_handler))
    app.add_handler(MessageHandler(filters.Chat(FEEDBACK_GROUP_ID) & filters.REPLY, doctor_reply_handler))
    # Kanal postlari uchun (channel_post)
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POSTS & filters.Chat(STATSIONAR_CHANNEL) & filters.REPLY, doctor_reply_handler))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POSTS & filters.Chat(DIAGNOSTIKA_CHANNEL) & filters.REPLY, doctor_reply_handler))
    app.add_handler(MessageHandler(filters.VOICE & ~filters.Chat([DOCTORS_GROUP_ID, FEEDBACK_GROUP_ID, STATSIONAR_CHANNEL, DIAGNOSTIKA_CHANNEL]), unknown))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Chat([DOCTORS_GROUP_ID, FEEDBACK_GROUP_ID, STATSIONAR_CHANNEL, DIAGNOSTIKA_CHANNEL]), unknown))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
