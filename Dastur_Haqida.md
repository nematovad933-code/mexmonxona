# 🏨 Mehmonxona Mehmonlarini Ro‘yxatga Olish va Boshqarish Tizimi

Ushbu dastur zamonaviy mehmonxonalar, mehmon uylari (Guest House) va hostellar uchun qabulxona (Reception) va ma'muriyat faoliyatini to‘liq avtomatlashtirish, tashrif buyuruvchi mehmonlarni ro‘yxatga olish, xonalarga joylashtirish, to‘lovlarni hisob-kitob qilish va barcha ma'lumotlarni xavfsiz saqlash uchun maxsus ishlab chiqilgan.

---

## 🌟 Asosiy Imkoniyatlar

### 1. Mehmonlarni To‘liq Ro‘yxatga Olish (Guest Registration)
* **Shaxsiy ma'lumotlar:**
  * Mehmonning to‘liq F.I.SH (Familiya, Ism, Sharif)
  * Pasport yoki ID-karta seriyasi va raqami
  * JSHSHIR (PINFL — 14 xonali raqam)
  * Tug‘ilgan sanasi va jinsi
  * Fuqaroligi (O‘zbekiston, MDH davlatlari, xorijiy sayyohlar)
  * Telefon raqami va elektron pochta manzili
  * Doimiy yashash manzili
  * Tashrif maqsadi (Sayohat, Ish safari, Davolanish, Mehmon va h.k.)
  * Maxsus talablar va eslatmalar (VIP mehmon, tinch qavat va boshqalar)
* **Avtomatik Pasport Qidiruv (Smart Lookup):**
  * Agar mehmon avval mehmonxonaga kelgan bo‘lsa, pasport raqami kiritilishi bilan uning barcha shaxsiy ma'lumotlari avtomatik to‘ldiriladi!

### 2. Xonalar Boshqaruvi va Shaxmatka (Interactive Room Grid)
* **Xonalar holati vizual ranglar bilan ko‘rsatiladi:**
  * 🟢 **Yashil (Bo‘sh):** Toza va yangi mehmonni qabul qilishga tayyor xonalar
  * 🔴 **Qizil (Band):** Hozirda mehmon yashayotgan xonalar (mehmon ismi va ketish sanasi bilan)
  * 🟡 **Sariq (Tozalanmoqda):** Chiqib ketganidan keyin tozalash jarayonidagi xonalar
  * ⚪ **Kulrang (Ta'mirda):** Profilaktika yoki ta'mirdagi xonalar
* **Xonalarni boshqarish:** Yangi xona qo‘shish, xona toifalari (Standart, Lyuks, VIP, Family), qavati, sig‘imi va kunlik narxlarini tahrirlash.
* Bo‘sh xonani tanlaganda bir klik bilan to‘g‘ridan-to‘g‘ri mehmonni joylashtirish formasi ochiladi.

### 3. Moliyaviy Hisob-kitob va To‘lovlar Tizimi
* **Avtomatik hisob-kitob:**
  * Kirish va chiqish sanalari kiritilganda umumiy kunlar soni avtomatik hisoblanadi.
  * Xona tanlanganda uning kunlik narxi va umumiy summa avtomatik chiqariladi (`Kunlik narx × Kunlar soni = Jami summa`).
  * To‘langan summa kiritilganda qoldiq qarz avtomatik ranglar bilan ko‘rsatiladi.
* **To‘lov turlari:** Naqd pul, Plastik karta (Uzcard/Humo), Payme/Click/Oson, Bank o‘tkazmasi, Valyuta (USD).
* **Bo‘lib-bo‘lib to‘lash:** Mehmon yashash davrida yoki chiqish vaqtida qo‘shimcha to‘lovlarni qabul qilish imkoniyati.

### 4. Chiqarish va Rasmiy Hujjatlar (Print & Documents)
* 🧾 **To‘lov Cheki (Kvitansiya / Invoice):** Mehmonxona rekvizitlari, sanalar, to‘lovlar tarixi, muhr va imzo joylari bilan tayyor professional kvitansiya. Brauzer orqali to‘g‘ridan-to‘g‘ri printerdan yoki PDF qilib chiqarish mumkin (Ctrl + P).
* 📋 **Mehmon Ro‘yxatga Olish Kartochkasi (Forma / Anketa):** Mehmonxonaning ichki tartib-qoidalari va mehmon roziligi imzosi bilan rasmiy ro‘yxatga olish hujjati.
* 📊 **Excel Hisobot (Eksport):** Barcha mehmonlar ro‘yxati, to‘lovlari, qarzdorliklari va xonalari bo‘yicha to‘liq hisobotni bir klik bilan `.xlsx` formatida yuklab olish.

### 5. Boshqaruv Paneli (Dashboard & Analytics)
* Bugungi faol mehmonlar soni
* Bo‘sh va band xonalar hisobi, bandlik foizi (%)
* Bugun kelganlar va ketishi kerak bo‘lganlar ro‘yxati
* Bugungi va oylik umumiy tushum
* Qoldiq qarzdorliklar bo‘yicha monitoring

### 6. Mehmonxona Sozlamalari va Baza Zaxirasi
* Mehmonxona nomi, yulduzlari, manzili, telefonlari, INN va rahbariyat ma'lumotlarini sozlash.
* Standart kirish (14:00) va chiqish (12:00) vaqtlarini belgilash.
* Ma'lumotlar bazasining zaxira nusxasini (`.db` fayl) bir tugma bilan yuklab olish.

---

## 🚀 Dasturni Ishga Tushirish

### Eng Oson Usul (1-Klik):
Fayllar joylashgan papkada **`Ishga_tushirish.bat`** fayli ustiga sichqoncha bilan ikki marta bosing.

Dastur avtomatik tarzda:
1. Kerakli kutubxonalarni tekshiradi;
2. Ma'lumotlar bazasini sozlaydi;
3. Serverni ishga tushiradi;
4. Standart brauzeringizda tizimni avtomatik ochadi: **`http://localhost:5000`**

### Qo‘lda Ishga Tushirish (Terminal orqali):
```bash
python run.py
```
yoki:
```bash
python app.py
```

---

## 📁 Dastur Tuzilishi

```
ilova yaratish/
│
├── app.py                     # Asosiy Flask web-server va barcha marshrutlar
├── database.py                # SQLite ma'lumotlar bazasi va SQL so'rovlar
├── seed_data.py               # Namunaviy xonalar va mehmonlar bazasi
├── export_excel.py            # Professional Excel (.xlsx) hisobot generatori
├── run.py                     # Avtomatik brauzer ochuvchi va waitress server
├── Ishga_tushirish.bat        # Windows uchun bitta klikda ishga tushirish
├── requirements.txt           # Kerakli Python kutubxonalari
│
├── static/
│   ├── css/
│   │   └── style.css          # Zamonaviy, toza va to‘liq avtonom dizayn
│   └── js/
│       └── app.js             # Interaktiv hisob-kitoblar, qidiruv va modallar
│
└── templates/
    ├── base.html              # Barcha sahifalarning asosiy dizayn shabloni
    ├── dashboard.html         # Asosiy boshqaruv paneli va tezkor statistika
    ├── registration.html      # Yangi mehmonni ro‘yxatga olish formasi
    ├── guests.html            # Mehmonlarning to‘liq jadvali va filtrlari
    ├── guest_profile.html     # Tanlangan mehmon profili va barcha tashriflari
    ├── guest_edit.html        # Mehmon va buyurtma ma'lumotlarini tahrirlash
    ├── rooms.html             # Xonalar shaxmatkasi va interaktiv xarita
    ├── receipt.html           # Chop etishga mo‘ljallangan to‘lov kvitansiyasi
    ├── registration_card.html # Mehmon ro‘yxatga olish anketasi (A4 chop etish)
    └── settings.html          # Mehmonxona sozlamalari va ma'lumotlar bazasi zaxirasi
```

---

## 🔒 Xavfsizlik va Ma'lumotlar Saqlanishi
Dastur **SQLite3** orqali to‘liq lokal ravishda ishlaydi. Ma'lumotlar tashqi serverlarga yuborilmaydi, internet talab qilinmaydi va foydalanuvchining o‘z kompyuterida 100% xavfsiz saqlanadi.

