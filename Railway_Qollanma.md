# 🚂 Railway Hostingiga Joylashtirish (Deploy) Qo‘llanmasi

Ushbu loyiha **Railway.app** bulutli hostingiga 100% moslashtirildi. Railway avtomatik ravishda GitHub repozitoriyangizdagi o‘zgarishlarni kuzatib boradi va har safar yangi kod yuklanganda (push) avtomatik ishga tushiradi.

---

## ⚡ Qadamma-qadam Ishga Tushirish (3 daqiqada)

### 1-Qadam: Railway saytiga kirish
1. Brauzerda [**railway.com**](https://railway.com/) (yoki [railway.app](https://railway.app/)) saytiga kiring.
2. **"Login"** tugmasini bosing va o‘zingizning GitHub akkauntingiz (**`nematovad933-code`**) orqali kiring.

### 2-Qadam: GitHub repozitoriyasini ulash
1. Asosiy sahifada **"New Project"** (yangi loyiha) tugmasini bosing.
2. **"Deploy from GitHub repo"** bandini tanlang.
3. Ro‘yxatdan **`mexmonxona`** (`nematovad933-code/mexmonxona`) repozitoriyasini tanlang.
4. **"Deploy Now"** tugmasini bosing.

Railway loyihangizdagi `railway.json`, `Procfile` va `requirements.txt` fayllarini avtomatik aniqlaydi va **Gunicorn** orqali serverni ishga tushiradi.

---

### 3-Qadam: Ommaviy Havola (Public Domain) Olish
Dasturingiz internetda barcha uchun ochilishi uchun:
1. Railway ichida loyihangiz (servis) ustiga bosing.
2. **"Settings"** bo‘limiga o‘ting.
3. **"Networking"** bo‘limini toping va **"Generate Domain"** tugmasini bosing.
4. Sizga tayyor internet havolasi beriladi, masalan:
   👉 `https://mexmonxona-production.up.railway.app`

Ushbu havolani ochsangiz, mehmonxona tizimi darhol ishlaydi!

---

### 4-Qadam (Tavsiya etiladi): Ma'lumotlar Bazasini Doimiy Saqlash (Volume)
Railway da har safar yangi versiya chiqqanda xonalar va mehmonlar bazasi o‘chib ketmasligi (doimiy saqlanib qolishi) uchun:
1. Loyihangiz oynasida **"+ New"** tugmasini bosing.
2. **"Volume"** (Disk hajmi) ni tanlang.
3. Ushbu Volume ni mehmonxona servisingizga ulang (Mount path: `/data`).
4. **"Variables"** bo‘limiga o‘tib, quyidagi o‘zgaruvchini kiriting:
   - Kalit (Name): `DATA_DIR`
   - Qiymat (Value): `/data`

*Eslatma: Dastur Railway taqdim etadigan `RAILWAY_VOLUME_MOUNT_PATH` ni ham avtomatik taniy oladi.*

---

## 🛠️ Loyihada Nimalar Moslashtirildi?

1. **`Procfile` va `railway.json`:**
   Ishlab chiqarish (production) darajasidagi yuqori tezlikli **Gunicorn WSGI** serveri sozlandi (`--workers 2 --threads 4 --timeout 120`).
2. **Dinamik Port (`PORT`):**
   Railway tomonidan ajratiladigan ixtiyoriy portni avtomatik aniqlash (`os.environ.get('PORT', 5000)`) o‘rnatildi.
3. **Avtomatik Baza Initsializatsiyasi:**
   Server birinchi marta ishga tushganda SQLite bazasi va xonalar shaxmatkasi avtomatik yaratiladi.
4. **Dockerfile & Nixpacks:**
   Railway ning har qanday build tizimida (Nixpacks yoki Docker) xatosiz yig‘ilish ta'minlandi.
5. **Mahalliy va Bulutli Ishlash:**
   Dastur o‘z kompyuteringizda `Ishga_tushirish.bat` orqali ham, Railway bulutida ham bir xil mukammal ishlayveradi.
