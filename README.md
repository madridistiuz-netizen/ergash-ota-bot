# 🏥 Эргаш-Ота Telegram Bot

## O'rnatish bo'yicha qo'llanma (Uzbek)

---

### 1-QADAM: BotFather'dan token olish

1. Telegramda **@BotFather** ni oching
2. `/newbot` yozing
3. Bot nomi yozing: `Эргаш-Ота`
4. Bot username yozing: `ergashota_bot` (yoki boshqa)
5. **TOKEN** olasiz — uni saqlang!

---

### 2-QADAM: Admin ID olish

1. Telegramda **@userinfobot** ni oching
2. `/start` yozing
3. Sizning **ID raqamingiz** chiqadi — uni saqlang!

---

### 3-QADAM: Railway.app'ga o'rnatish (BEPUL)

1. **https://railway.app** ga kiring
2. GitHub bilan ro'yxatdan o'ting
3. **"New Project"** → **"Deploy from GitHub repo"**
4. Bu fayllarni yuklang (GitHub'ga push qiling)
5. **Variables** bo'limiga quyidagilarni kiriting:

```
BOT_TOKEN = sizning_tokeningiz
ADMIN_ID = sizning_id_raqamingiz
OPERATOR_PHONE = +998932264566
```

6. Deploy tugmasini bosing ✅

---

### 4-QADAM: Botni ishga tushirish

Railway deploy bo'lgach, Telegramda botingizga `/start` yozing!

---

## Admin buyruqlari

Bot ishga tushgach, siz Telegram orqali ma'lumotlarni o'zgartira olasiz:

### Telefon raqamini o'zgartirish:
```
/admin contacts|phone1|+998901234567
```

### Manzilni o'zgartirish (rus tilida):
```
/admin contacts|address_ru|г. Каттакурган, ул. Новая 1
```

### Transfer narxini o'zgartirish:
```
/admin transfer|ru|🚗 Стоимость трансфера:\n\n• Каттакурган — 70 000 сум\n• Самарканд — 350 000 сум
```

### Ekskursiya ma'lumotini o'zgartirish:
```
/admin excursion|uz|🕌 Ekskursiya...\n\nyangi matn
```

### Barcha admin buyruqlarni ko'rish:
```
/admin_help
```

---

## Barcha o'zgartirilishi mumkin bo'lgan bo'limlar:

| Bo'lim | Kalitlar |
|--------|----------|
| `contacts` | `phone1`, `phone2`, `address_ru`, `address_uz`, `address_kz`, `work_hours_ru`, `work_hours_uz`, `work_hours_kz`, `instagram`, `website` |
| `doctor` | `name_ru`, `name_uz`, `name_kz`, `title_ru`, `title_uz`, `title_kz` |
| `transfer` | `ru`, `uz`, `kz` |
| `excursion` | `ru`, `uz`, `kz` |
| `weekend` | `ru`, `uz`, `kz` |
| `included` | `ru`, `uz`, `kz` |

---

## Muhim eslatma

`\n` — yangi qator belgisi. Matn yozganingizda `\n` qo'ying:
```
/admin transfer|uz|🚗 Transfer:\n\n• Kattaqo'rg'on — 60 000\n• Samarqand — 300 000
```

---

## Инструкция на русском

### Шаг 1: Получить токен от BotFather
1. Откройте **@BotFather** в Telegram
2. Напишите `/newbot`
3. Введите название: `Эргаш-Ота`
4. Введите username: `ergashota_bot`
5. Сохраните полученный **TOKEN**

### Шаг 2: Получить свой Admin ID
1. Откройте **@userinfobot**
2. Напишите `/start`
3. Сохраните ваш **ID**

### Шаг 3: Деплой на Railway.app
1. Зайдите на **https://railway.app**
2. Войдите через GitHub
3. Создайте новый проект из репозитория
4. В разделе **Variables** укажите:
   - `BOT_TOKEN` = ваш токен
   - `ADMIN_ID` = ваш ID
   - `OPERATOR_PHONE` = +998932264566
5. Нажмите Deploy ✅
