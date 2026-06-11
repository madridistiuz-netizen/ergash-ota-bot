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
OPERATOR_PHONE = os.getenv("OPERATOR_PHONE", "+998932264567")
STATSIONAR_CHANNEL = int(os.getenv("STATSIONAR_CHANNEL", "-1003991204638"))
DIAGNOSTIKA_CHANNEL = int(os.getenv("DIAGNOSTIKA_CHANNEL", "-1003933653831"))
TRANSFER_CHANNEL = int(os.getenv("TRANSFER_CHANNEL", "-1003939453314"))
DATA_FILE = os.getenv("DATA_FILE", "/app/data/data.json")

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
        "clinic":      "🏥 О клинике",
        "rooms":       "🛏 Стоимость номеров",
        "diagnostics": "🧲 Диагностика",
        "wards":       "🏨 Палаты",
        "guide":       "📖 Инструкция для пациентов",
        "faq":         "❓ Частые вопросы",
        "booking":     "📅 Записаться на приём",
        "transfer":    "🚗 Добраться до клиники",
        "weekend":     "🌅 Воскресенье",
        "operator":    "📞 Оператор",
    },
    "uz": {
        "clinic":      "🏥 Klinika haqida",
        "rooms":       "🛏 Xonalar narxi",
        "diagnostics": "🧲 Diagnostika",
        "wards":       "🏨 Palatalar",
        "guide":       "📖 Bemor uchun qo'llanma",
        "faq":         "❓ Ko'p so'raladigan savollar",
        "booking":     "📅 Qabulga yozilish",
        "transfer":    "🚗 Klinikaga yetib olish",
        "weekend":     "🌅 Yakshanba",
        "operator":    "📞 Operator",
    },
    "kz": {
        "clinic":      "🏥 Клиника туралы",
        "rooms":       "🛏 Бөлмелер бағасы",
        "diagnostics": "🧲 Диагностика",
        "wards":       "🏨 Палаталар",
        "guide":       "📖 Науқас нұсқаулығы",
        "faq":         "❓ Жиі сұрақтар",
        "booking":     "📅 Қабылдауға жазылу",
        "transfer":    "🚗 Клиникаға жету",
        "weekend":     "🌅 Жексенбі",
        "operator":    "📞 Оператор",
    },
}


def main_menu_keyboard(lang):
    labels = MENU_LABELS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(labels["clinic"],      callback_data="menu_clinic")],
        [InlineKeyboardButton(labels["rooms"],       callback_data="menu_rooms")],
        [InlineKeyboardButton(labels["wards"],       callback_data="menu_wards")],
        [InlineKeyboardButton(labels["diagnostics"], callback_data="menu_diagnostics")],
        [InlineKeyboardButton(labels["guide"],       callback_data="menu_guide")],
        [InlineKeyboardButton(labels["faq"],         callback_data="menu_faq")],
        [InlineKeyboardButton(labels["booking"],     callback_data="menu_booking")],
        [InlineKeyboardButton(labels["transfer"],    callback_data="menu_transfer")],
        [InlineKeyboardButton(labels["weekend"],     callback_data="menu_weekend")],
        [InlineKeyboardButton(labels["operator"],    callback_data="menu_operator")],
    ])


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
        [InlineKeyboardButton(labels[8], callback_data="menu_diagnostics")],
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
            "3️⃣ Процедуры и день",
            "4️⃣ Инфраструктура",
            "5️⃣ Правила поведения",
            "6️⃣ Что купить домой",
            "⬅️ Назад",
        ),
        "uz": (
            "1️⃣ Joylashish tartibi",
            "2️⃣ Birinchi kun muolaja tartibi",
            "3️⃣ Protseduralar va kun",
            "4️⃣ Infrastruktura",
            "5️⃣ Qoidalar",
            "6️⃣ Uyga tafsiyaoma",
            "⬅️ Orqaga",
        ),
        "kz": (
            "1️⃣ Орналасу тәртібі",
            "2️⃣ Первый день лечения",
            "3️⃣ Процедуралар және күн",
            "4️⃣ Инфрақұрылым",
            "5️⃣ Ережелер",
            "6️⃣ Үйге ұсыным",
            "⬅️ Артқа",
        ),
    }[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(labels[0], callback_data="guide_arrival")],
        [InlineKeyboardButton(labels[1], callback_data="guide_malham")],
        [InlineKeyboardButton(labels[2], callback_data="guide_procedures")],
        [InlineKeyboardButton(labels[3], callback_data="guide_infrastructure")],
        [InlineKeyboardButton(labels[4], callback_data="guide_rules")],
        [InlineKeyboardButton(labels[5], callback_data="guide_shopping")],
        [InlineKeyboardButton(labels[6], callback_data="back_main")],
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
            "🌿 Malham va muolajalar",
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
            "🌿 Malham va muolajalar",
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
            "🌿 Malham және процедуралар",
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

    await update.message.reply_text(
        "👋 Добро пожаловать / Xush kelibsiz / Қош келдіңіз!\n\n🌐 Выберите язык / Tilni tanlang / Тілді таңдаңыз:",
        reply_markup=lang_keyboard()
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
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

    # ── FAQ ──
    elif data in ("menu_faq",) or data.startswith("faq_"):
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

    elif data in ("menu_booking", "book_statsionar", "book_diagnostika", "calc_book_statsionar") or \
         data.startswith("diag_book_") or data.startswith("excursion_book_"):
        await handle_booking_callbacks(query, context, data, lang, chat_id)

    # ── Bemor qo'llanmasi ──
    elif data == "menu_guide":
        title = {
            "ru": "📖 *Руководство пациента*\n\nВыберите раздел:",
            "uz": "📖 *Bemor uchun qo'llanma*\n\nBo'limni tanlang:",
            "kz": "📖 *Науқас нұсқаулығы*\n\nБөлімді таңдаңыз:",
        }[lang]
        await query.edit_message_text(title, parse_mode="Markdown",
                                      reply_markup=guide_keyboard(lang))

    elif data.startswith("guide_"):
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

    # ── Uyga tafsiyaoma — quyi bo'limlar ──
    elif data == "info_qoidalar":
        text = {
            "uz": (
                "🏥 *'Ergash ota' tibbiyot markazining shifokor tavsiyalari*\n\n"
                "Hurmatli bemor! Markazimizda davolanish kursini yakunlaganingiz bilan tabriklaymiz. "
                "Sog'ligingizni tiklash va natijani mustahkamlash uchun uy sharoitida 14 kundan 24 kungacha "
                "qat'iy parhez saqlashingiz zarur.\n\n"
                "⚠️ *Eng muhim qoidalar:*\n"
                "• Dastlabki 3 kun davomida umuman non iste'mol qilmang!\n"
                "• Jismoniy og'ir ishlar qilish va og'ir yuk ko'tarish mumkin emas."
            ),
            "ru": (
                "🏥 *Рекомендации врача центра «Эргаш ота»*\n\n"
                "Уважаемый пациент! Поздравляем с завершением курса лечения в нашем центре. "
                "Для восстановления здоровья и закрепления результата необходимо строго соблюдать "
                "диету в домашних условиях от 14 до 24 дней.\n\n"
                "⚠️ *Важные правила:*\n"
                "• В первые 3 дня полностью исключите хлеб!\n"
                "• Тяжёлый физический труд и подъём тяжестей запрещены."
            ),
            "kz": (
                "🏥 *«Эргаш ота» орталығы дәрігерінің ұсыныстары*\n\n"
                "Құрметті науқас! Орталығымызда емдеу курсын аяқтағаныңызбен құттықтаймыз. "
                "Денсаулықты қалпына келтіру және нәтижені бекіту үшін үй жағдайында 14 күннен 24 күнге дейін "
                "қатаң диета сақтауыңыз қажет.\n\n"
                "⚠️ *Маңызды ережелер:*\n"
                "• Алғашқы 3 күн нан мүлдем жемеңіз!\n"
                "• Ауыр дене жұмысы және ауыр зат көтеру мүмкін емес."
            ),
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="guide_shopping")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

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
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

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
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

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
            "ru": "🌿 *Malham va muolajalar*\n\nВыберите раздел:",
            "uz": "🌿 *Malham va muolajalar*\n\nBo'limni tanlang:",
            "kz": "🌿 *Malham және процедуралар*\n\nБөлімді таңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        mal_label  = {"ru": "🟢 Malham va tabiiy yog'lar", "uz": "🟢 Malham va tabiiy yog'lar", "kz": "🟢 Malham және табиғи майлар"}[lang]
        muo_label  = {"ru": "🔵 Доп. процедуры",          "uz": "🔵 Qo'shimcha muolajalar",     "kz": "🔵 Қосымша процедуралар"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(mal_label, callback_data="sub_malhamlar")],
            [InlineKeyboardButton(muo_label, callback_data="sub_muolajalar")],
            [InlineKeyboardButton(back_label, callback_data="menu_clinic")],
        ])
        await query.edit_message_text(title, parse_mode="Markdown", reply_markup=kb)

    elif data == "sub_malhamlar":
        title = {
            "ru": "🟢 *Malham va tabiiy yog'lar*\n\nВыберите:",
            "uz": "🟢 *Malham va tabiiy yog'lar*\n\nTanlang:",
            "kz": "🟢 *Malham және табиғи майлар*\n\nТаңдаңыз:",
        }[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        items = [
            ("Malham",                                                                          "mal_malham"),
            ({"ru": "Фито бар",         "uz": "Fito bar",      "kz": "Фито бар"}[lang],       "mal_fitobar"),
            ({"ru": "Миндальное масло", "uz": "Bodom yog'i",   "kz": "Бадам майы"}[lang],     "mal_bodom"),
            ({"ru": "Оливковое масло",  "uz": "Zaytun yog'i",  "kz": "Зәйтүн майы"}[lang],   "mal_zaytun"),
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
            ({"ru": "Общий массаж",            "uz": "Umumiy massaj",                       "kz": "Жалпы массаж"}[lang],                           "muo_massaj"),
            ({"ru": "Серебряные перчатки",     "uz": "Kumush qulqob",                       "kz": "Күміс қолғап"}[lang],                           "muo_kumush"),
            ({"ru": "Лимфодренаж",             "uz": "Limfadrenaj",                         "kz": "Лимфодренаж"}[lang],                            "muo_limfa"),
            ({"ru": "Растяжка",                "uz": "Rastyajka",                           "kz": "Растяжка"}[lang],                               "muo_rastyajka"),
            ({"ru": "Ударно-волновая терапия", "uz": "Zarb to'lqinli terapiya",             "kz": "Соққы-толқынды терапия"}[lang],                 "muo_uwt"),
            ("Robospine",                                                                                           "muo_robospine"),
            ({"ru": "Криолиполиз",             "uz": "Kriolipoliz",                         "kz": "Криолиполиз"}[lang],                            "muo_kriyo"),
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
            ({"ru": "Общий массаж",            "uz": "Umumiy massaj",                       "kz": "Жалпы массаж"}[lang],                           "muo_massaj"),
            ({"ru": "Серебряные перчатки",     "uz": "Kumush qulqob",                       "kz": "Күміс қолғап"}[lang],                           "muo_kumush"),
            ({"ru": "Лимфодренаж",             "uz": "Limfadrenaj",                         "kz": "Лимфодренаж"}[lang],                            "muo_limfa"),
            ({"ru": "Растяжка",                "uz": "Rastyajka",                           "kz": "Растяжка"}[lang],                               "muo_rastyajka"),
            ({"ru": "Ударно-волновая терапия", "uz": "Zarb to'lqinli terapiya",             "kz": "Соққы-толқынды терапия"}[lang],                 "muo_uwt"),
            ("Robospine",                                                                                                        "muo_robospine"),
            ({"ru": "Криолиполиз",             "uz": "Kriolipoliz",                         "kz": "Криолиполиз"}[lang],                            "muo_kriyo"),
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
            ({"ru": "Общий массаж",            "uz": "Umumiy massaj",                       "kz": "Жалпы массаж"}[lang],                           "muo_massaj"),
            ({"ru": "Серебряные перчатки",     "uz": "Kumush qulqob",                       "kz": "Күміс қолғап"}[lang],                           "muo_kumush"),
            ({"ru": "Лимфодренаж",             "uz": "Limfadrenaj",                         "kz": "Лимфодренаж"}[lang],                            "muo_limfa"),
            ({"ru": "Растяжка",                "uz": "Rastyajka",                           "kz": "Растяжка"}[lang],                               "muo_rastyajka"),
            ({"ru": "Ударно-волновая терапия", "uz": "Zarb to'lqinli terapiya",             "kz": "Соққы-толқынды терапия"}[lang],                 "muo_uwt"),
            ("Robospine",                                                                                                        "muo_robospine"),
            ({"ru": "Криолиполиз",             "uz": "Kriolipoliz",                         "kz": "Криолиполиз"}[lang],                            "muo_kriyo"),
        ]
        buttons = [[InlineKeyboardButton(label, callback_data=cb)] for label, cb in items]
        buttons.append([InlineKeyboardButton(back_label, callback_data="malham_va_muolajalar")])
        await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

    elif data in (
        "mal_malham", "mal_fitobar", "mal_bodom", "mal_zaytun", "mal_chuda",
        "muo_massaj", "muo_kumush",
        "muo_limfa", "muo_rastyajka", "muo_uwt", "muo_robospine", "muo_kriyo",
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
        intro = {
            "ru": (
                "👨‍⚕️ *Наша команда*\n\n"
                "В частном медицинском центре «Эргаш ота» работают опытные врачи, медсёстры и специалисты.\n\n"
                "Главная цель нашей команды — индивидуальный подход, качественное обслуживание и искренняя забота о каждом пациенте.\n\n"
                "🏥 *В нашей клинике работают:*\n"
                "✔ Опытные врачи\n"
                "✔ Квалифицированные медсёстры\n"
                "✔ Специалисты диагностики\n"
                "✔ Сотрудники физиотерапии и реабилитации\n\n"
                "💙 Здоровье, комфорт и доверие пациентов — наша главная ценность."
            ),
            "uz": (
                "👨‍⚕️ *Bizning jamoamiz*\n\n"
                "\"Ergash ota\" xususiy tibbiyot markazida tajribali shifokorlar, hamshiralar va mutaxassislar faoliyat olib boradi.\n\n"
                "Bizning jamoamizning asosiy maqsadi — har bir bemorga individual yondashuv, sifatli xizmat va samimiy e'tibor ko'rsatishdir.\n\n"
                "🏥 *Klinikamizda:*\n"
                "✔ Tajribali shifokorlar\n"
                "✔ Malakali hamshiralar\n"
                "✔ Diagnostika mutaxassislari\n"
                "✔ Fizioterapiya va reabilitatsiya xodimlari\n\n"
                "faoliyat yuritadi.\n\n"
                "💙 Biz bemorlarning sog'lig'i, qulayligi va ishonchini eng muhim qadriyat deb bilamiz."
            ),
            "kz": (
                "👨‍⚕️ *Біздің команда*\n\n"
                "«Эргаш ота» жеке медициналық орталығында тәжірибелі дәрігерлер, медбикелер және мамандар жұмыс істейді.\n\n"
                "Командамыздың басты мақсаты — әр науқасқа жеке көзқарас, сапалы қызмет және шынайы қамқорлық.\n\n"
                "🏥 *Клиникамызда жұмыс істейді:*\n"
                "✔ Тәжірибелі дәрігерлер\n"
                "✔ Білікті медбикелер\n"
                "✔ Диагностика мамандары\n"
                "✔ Физиотерапия және реабилитация қызметкерлері\n\n"
                "💙 Науқастардың денсаулығы, жайлылығы және сенімі — біздің басты құндылығымыз."
            ),
        }[lang]
        await query.edit_message_text(intro, parse_mode="Markdown", reply_markup=back_keyboard(lang))
        # Jamoaning rasmlari (admin orqali yuklangan)
        team_photos = d.get("team_photos", [])
        if team_photos:
            await send_photos(context, chat_id, team_photos)
        # Alohida a'zolar (eski tizim)
        for member in staff:
            text = f"👨‍⚕️ *{member['name']}*\n{member['role']}"
            if member.get("photo_id"):
                await context.bot.send_photo(chat_id=chat_id, photo=member["photo_id"], caption=text, parse_mode="Markdown")
            else:
                await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")

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
        await query.edit_message_text(title, parse_mode="Markdown",
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

            await query.edit_message_text(description, parse_mode="Markdown", reply_markup=back_kb)

            # Yangi rasmlarni yuborib, message_id larini saqlab qolish
            if xona.get("photos"):
                sent_ids = []
                for photo_id in xona["photos"][:10]:
                    try:
                        msg = await context.bot.send_photo(chat_id=chat_id, photo=photo_id)
                        sent_ids.append(msg.message_id)
                    except Exception:
                        pass
                context.user_data["xona_photo_ids"] = sent_ids
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
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        # Xona rasmlari
        if xona.get("photos"):
            await send_photos(context, chat_id, xona["photos"])

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

    elif data == "menu_diagnostics":
        title = {
            "ru": "🧲 Выберите вид диагностики:",
            "uz": "🧲 Diagnostika turini tanlang:",
            "kz": "🧲 Диагностика түрін таңдаңыз:",
        }[lang]
        await query.edit_message_text(title, reply_markup=diagnostics_keyboard(lang))

    elif data == "diag_mrt15":
        logger.info(f"diag_mrt15 handler ishga tushdi, lang={lang}")
        lines = "\n".join([f"• {x}" for x in d["mrt_15"]])
        title = {"ru": "🧲 *МРТ 1.5Т — цены:*", "uz": "🧲 *МРТ 1.5Т — narxlar:*", "kz": "🧲 *МРТ 1.5Т — бағалар:*"}[lang]
        call_label = {"ru": "📞 МРТ 1.5Т — позвонить", "uz": "📞 МРТ 1.5Т — telefon qilish", "kz": "📞 МРТ 1.5Т — қоңырау шалу"}[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(call_label, callback_data="call_mrt15")],
            [InlineKeyboardButton(back_label, callback_data="menu_diagnostics")],
        ])
        await query.edit_message_text(f"{title}\n\n{lines}", parse_mode="Markdown", reply_markup=kb)

    elif data == "diag_mrt3t":
        title = {"ru": "🧲 МРТ 3Т — выберите группу:", "uz": "🧲 МРТ 3Т — guruhni tanlang:", "kz": "🧲 МРТ 3Т — топты таңдаңыз:"}[lang]
        call_label = {"ru": "📞 МРТ 3Т — позвонить", "uz": "📞 МРТ 3Т — telefon qilish", "kz": "📞 МРТ 3Т — қоңырау шалу"}[lang]
        groups_kb = list(mrt3t_groups_keyboard(lang).inline_keyboard)
        kb = InlineKeyboardMarkup(
            groups_kb + [[InlineKeyboardButton(call_label, callback_data="call_mrt3t")]]
        )
        await query.edit_message_text(title, reply_markup=kb)

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
        await query.edit_message_text(f"🧲 *МРТ 3Т — {group_name}:*\n\n{lines}",
                                      parse_mode="Markdown", reply_markup=kb)

    elif data == "diag_mskt256":
        lines = "\n".join([f"• {x}" for x in d["mskt_256"]])
        title = {"ru": "🖥 *МСКТ 256 — цены:*", "uz": "🖥 *МСКТ 256 — narxlar:*", "kz": "🖥 *МСКТ 256 — бағалар:*"}[lang]
        call_label = {"ru": "📞 МСКТ 256 — позвонить", "uz": "📞 МСКТ 256 — telefon qilish", "kz": "📞 МСКТ 256 — қоңырау шалу"}[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(call_label, callback_data="call_mskt256")],
            [InlineKeyboardButton(back_label, callback_data="menu_diagnostics")],
        ])
        await query.edit_message_text(f"{title}\n\n{lines}", parse_mode="Markdown", reply_markup=kb)

    elif data == "diag_mskt128":
        lines = "\n".join([f"• {x}" for x in d["mskt_128"]])
        title = {"ru": "🖥 *МСКТ 128 — цены:*", "uz": "🖥 *МСКТ 128 — narxlar:*", "kz": "🖥 *МСКТ 128 — бағалар:*"}[lang]
        call_label = {"ru": "📞 МСКТ 128 — позвонить", "uz": "📞 МСКТ 128 — telefon qilish", "kz": "📞 МСКТ 128 — қоңырау шалу"}[lang]
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(call_label, callback_data="call_mskt128")],
            [InlineKeyboardButton(back_label, callback_data="menu_diagnostics")],
        ])
        await query.edit_message_text(f"{title}\n\n{lines}", parse_mode="Markdown", reply_markup=kb)

    elif data == "call_mrt15":
        text = "📞 *МРТ 1.5Т*\n\n☎️ +998664556015"
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="diag_mrt15")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "call_mrt3t":
        text = "📞 *МРТ 3Т*\n\n☎️ +998557010756"
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="diag_mrt3t")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "call_mskt" or data == "call_mskt256":
        text = "📞 *МСКТ 256*\n\n☎️ +998664556007"
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="diag_mskt256")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "call_mskt128":
        text = "📞 *МСКТ 128*\n\n☎️ +998664556007"
        back_label = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(back_label, callback_data="diag_mskt128")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "diag_other":
        lines = "\n".join([f"• {x}" for x in d["other_diagnostics"]])
        title = {"ru": "📡 *УЗИ — цены:*", "uz": "📡 *УЗИ — narxlar:*", "kz": "📡 *УДЗ — бағалар:*"}[lang]
        await query.edit_message_text(f"{title}\n\n{lines}", parse_mode="Markdown", reply_markup=back_keyboard(lang))

    elif data == "diag_mammografiya":
        text = {
            "ru": (
                "🩺 *Маммография*\n\n"
                "💰 *Цена:* 250 000 сум\n\n"
                "Рентгенологическое исследование молочных желёз для ранней диагностики."
            ),
            "uz": (
                "🩺 *Mammografiya*\n\n"
                "💰 *Narx:* 250 000 so'm\n\n"
                "Ko'krak bezlarini erta aniqlash uchun rentgenologik tekshiruv."
            ),
            "kz": (
                "🩺 *Маммография*\n\n"
                "💰 *Баға:* 250 000 сум\n\n"
                "Сүт бездерін ерте анықтауға арналған рентгенологиялық зерттеу."
            ),
        }[lang]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard(lang))

    elif data == "diag_fibroskan":
        text = {
            "ru": (
                "🫀 *Фибросканирование печени*\n\n"
                "💰 *Цена:* 220 000 сум\n\n"
                "Безболезненное исследование состояния печени без биопсии.\n\n"
                "⏱ Длительность: 15–20 минут\n"
                "📋 Подготовка: натощак (4–6 часов)"
            ),
            "uz": (
                "🫀 *Jigar fibroskan tekshiruvi*\n\n"
                "💰 *Narx:* 220 000 so'm\n\n"
                "Biopsiysiz jigar holatini og'riqsiz tekshirish.\n\n"
                "⏱ Davomiyligi: 15–20 daqiqa\n"
                "📋 Tayyorgarlik: och qorin (4–6 soat)"
            ),
            "kz": (
                "🫀 *Бауырды фибросканерлеу*\n\n"
                "💰 *Баға:* 220 000 сум\n\n"
                "Биопсиясыз бауыр жағдайын ауырусыз тексеру.\n\n"
                "⏱ Ұзақтығы: 15–20 минут\n"
                "📋 Дайындық: аш қарын (4–6 сағат)"
            ),
        }[lang]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard(lang))

    elif data == "diag_lab":
        lines = "\n".join([f"• {x}" for x in d["lab"]])
        title = {"ru": "🔬 *Лаборатория — цены:*", "uz": "🔬 *Laboratoriya — narxlar:*", "kz": "🔬 *Зертхана — бағалар:*"}[lang]
        await query.edit_message_text(f"{title}\n\n{lines}", parse_mode="Markdown", reply_markup=back_keyboard(lang))

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

    if text.startswith("/admin_photo") and not text.startswith("/admin_photo_clear"):
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


DOCTORS_GROUP_ID = -5193012514  # Shifokorlar guruhi

async def medical_doc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bemor rasm/fayl yuborsa — FSM state ga qo'shadi"""
    user = update.effective_user
    lang = get_lang(context)

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
    """Shifokor guruhda bemorning xabariga REPLY qilganda — bemorga yetkazadi"""
    msg = update.message
    if not msg or not msg.reply_to_message:
        return
    if msg.chat.id != DOCTORS_GROUP_ID:
        return

    # Asl xabarda uid ni topamiz
    original = msg.reply_to_message
    original_text = original.caption or original.text or ""
    import re
    match = re.search(r"uid:(\d+)", original_text)
    if not match:
        return

    patient_id = int(match.group(1))

    try:
        if msg.voice:
            # Shifokor ovozli javob yubordi
            voice_cap = "👨‍⚕️ *Shifokordan ovozli javob:*"
            await context.bot.send_voice(
                chat_id=patient_id,
                voice=msg.voice.file_id,
                caption=voice_cap,
                parse_mode="Markdown"
            )
        elif msg.text or msg.caption:
            reply_text = f"👨‍⚕️ *Shifokordan javob:*\n\n{msg.text or msg.caption}"
            await context.bot.send_message(
                chat_id=patient_id,
                text=reply_text,
                parse_mode="Markdown"
            )
        await msg.reply_text("✅ Javob bemorga yetkazildi.")
    except Exception as e:
        logger.error(f"doctor_reply_handler error: {e}")
        await msg.reply_text(f"❌ Xato: {e}")



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
    elif waiting == "team":
        d.setdefault("team_photos", []).append(file_id)
        await update.message.reply_text(f"✅ Jamoa rasmi qo'shildi! Jami: {len(d['team_photos'])} ta")
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
        ("💊 Лечение без операции?", "Да. Клиника специализируется на *консервативном лечении* — без операций, с использованием натуральных методов и физиотерапии."),
        ("🚻 Палаты мужские и женские?", "Да, палаты раздельные. Женщин и мужчин размещают в разных корпусах."),
        ("🍽 Есть ли питание?", "Да. Питание входит в программу лечения. Столовая работает по расписанию. Во время лечения — специальная диета."),
        ("📅 Как записаться?", "Запись не обязательна — принимаем без брони. Но лучше сообщить заранее для резервирования места."),
        ("🕐 Режим работы?", "Пн–Сб: 08:00–18:00. Воскресенье: приём новых пациентов."),
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
        ("💊 Operatsiyasiz davolanish bormi?", "Ha. Klinika *konservativ davolash* ga ixtisoslashgan — operatsiyasiz, tabiiy usullar va fizioterapiya bilan."),
        ("🚻 Erkaklar va ayollar palatalari?", "Ha, palatalar alohida. Ayollar va erkaklar turli korpuslarda joylashadi."),
        ("🍽 Ovqatlanish bormi?", "Ha. Ovqatlanish davolash dasturiga kiradi. Oshxona jadval bo'yicha ishlaydi. Davolash vaqtida — maxsus parhez."),
        ("📅 Qanday yozilish kerak?", "Bron shart emas — bronsiz qabul qilamiz. Lekin joy band qilish uchun oldindan xabar berish yaxshiroq."),
        ("🕐 Ish vaqti?", "Du–Shan: 08:00–18:00. Yakshanba: yangi bemorlar qabuli."),
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
        ("💊 Операциясыз емдеу бар ма?", "Иә. Клиника *консервативті емдеуге* маманданған — операциясыз, табиғи әдістермен."),
        ("🚻 Ер/әйел палаталары?", "Иә, палаталар бөлек. Әйелдер мен ерлер әртүрлі корпустарда орналасады."),
        ("🍽 Тамақтану бар ма?", "Иә. Тамақтану емдеу бағдарламасына кіреді."),
        ("📅 Қалай жазылу керек?", "Бронь міндетті емес — бронсыз қабылдаймыз."),
        ("🕐 Жұмыс уақыты?", "Дс–Сб: 08:00–18:00. Жексенбі: жаңа науқастар қабылдауы."),
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
    buttons = []
    for i, (q, _) in enumerate(faqs):
        buttons.append([InlineKeyboardButton(q, callback_data=f"faq_{i}")])
    back = {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga", "kz": "⬅️ Артқа"}[lang]
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

async def send_lid(context, channel_id, text):
    try:
        await context.bot.send_message(chat_id=channel_id, text=text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Lid yuborish xatosi: {e}")


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
            await query.edit_message_text(success, parse_mode="Markdown",
                                          reply_markup=back_keyboard(lang))

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
                    f"🌐 Til: {lang.upper()}\n\n"
                    f"🟢 QO'NG'IROQ QILING!"
                )
            await send_lid(context, STATSIONAR_CHANNEL, lid)

        else:  # diagnostika
            name = booking.get("name", "—")
            phone_num = booking.get("phone", "—")
            service = booking.get("service", "—")

            success = {
                "ru": f"🎉 *Заявка принята!*\n\n👤 {name}\n🔬 Услуга: {service}\n📞 {phone_num}\n\nОператор свяжется с вами.\n📞 {phone}",
                "uz": f"🎉 *Ariza qabul qilindi!*\n\n👤 {name}\n🔬 Xizmat: {service}\n📞 {phone_num}\n\nOperator siz bilan bog'lanadi.\n📞 {phone}",
                "kz": f"🎉 *Өтінім қабылданды!*\n\n👤 {name}\n🔬 Қызмет: {service}\n📞 {phone_num}\n\nОператор байланысады.\n📞 {phone}",
            }[lang]
            await query.edit_message_text(success, parse_mode="Markdown",
                                          reply_markup=back_keyboard(lang))

            lid = (
                f"🔬 *DIAGNOSTIKA LID*\n\n"
                f"👤 Ism: {name}\n"
                f"🔬 Xizmat: {service}\n"
                f"📞 Telefon: {phone_num}\n"
                f"💬 Telegram: {username}\n"
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
    faqs = FAQ_DATA.get(lang, FAQ_DATA["ru"])

    if data == "menu_faq":
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


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    step = context.user_data.get("booking_step")
    btype = context.user_data.get("booking_type", "statsionar")
    text = update.message.text.strip() if update.message.text else ""

    # Ovozli xabar filtri
    if update.message.voice or update.message.audio:
        msg = {
            "ru": "📝 Для быстрого ответа напишите вопрос *текстом*.",
            "uz": "📝 Tezroq javob olish uchun savolingizni *matn* ko'rinishida yuboring.",
            "kz": "📝 Жылдам жауап алу үшін сұрағыңызды *мәтін* түрінде жіберіңіз.",
        }[lang]
        await update.message.reply_text(msg, parse_mode="Markdown")
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
        await update.message.reply_text(msg, reply_markup=main_menu_keyboard(lang))
        return

    # Boshqa matnlar
    msg = {
        "ru": "Выберите раздел в меню 👇",
        "uz": "Menyudan bo'lim tanlang 👇",
        "kz": "Мәзірден бөлім таңдаңыз 👇",
    }[lang]
    await update.message.reply_text(msg, reply_markup=main_menu_keyboard(lang))


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_handler))
    app.add_handler(CommandHandler("admin_help", admin_handler))
    app.add_handler(CommandHandler("admin_photo", admin_handler))
    app.add_handler(CommandHandler("admin_photo_clear", admin_handler))
    app.add_handler(CommandHandler("admin_staff_add", admin_handler))
    app.add_handler(CommandHandler("admin_video", admin_handler))
    app.add_handler(CommandHandler("stats", admin_handler))
    app.add_handler(CommandHandler("broadcast", admin_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.PHOTO & filters.User(ADMIN_ID), photo_handler))
    app.add_handler(MessageHandler(filters.VIDEO & filters.User(ADMIN_ID), video_handler))
    app.add_handler(MessageHandler(filters.PHOTO & ~filters.User(ADMIN_ID), medical_doc_handler))
    app.add_handler(MessageHandler(filters.Document.ALL & ~filters.User(ADMIN_ID), medical_doc_handler))
    app.add_handler(MessageHandler(filters.Document.ALL & filters.User(ADMIN_ID), medical_doc_handler))
    app.add_handler(MessageHandler(filters.VOICE & ~filters.User(ADMIN_ID), medical_voice_handler))
    app.add_handler(MessageHandler(filters.Chat(DOCTORS_GROUP_ID) & filters.REPLY, doctor_reply_handler))
    app.add_handler(MessageHandler(filters.Chat(DOCTORS_GROUP_ID) & filters.VOICE & filters.REPLY, doctor_reply_handler))
    app.add_handler(MessageHandler(filters.VOICE, unknown))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
