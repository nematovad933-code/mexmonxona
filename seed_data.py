from database import init_db, get_db, add_room, create_registration
from datetime import date, timedelta

def seed_initial_data():
    init_db()
    conn = get_db()
    cursor = conn.cursor()
    
    # Xonalar sonini tekshirish
    cursor.execute('SELECT COUNT(*) FROM rooms')
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("Dastlabki xonalar bazaga yuklanmoqda...")
        # 1-qavat: Standart va Ekonom
        add_room("101", 1, "Standart 1 kishilik", 1, 250000, "available", "Wi-Fi, TV, Konditsioner, Dush", "1-qavat, qulay va shinam 1 kishilik xona")
        add_room("102", 1, "Standart 2 kishilik", 2, 350000, "available", "Wi-Fi, TV, Konditsioner, Dush, Minibar", "1-qavat, 2 kishilik alohida karavotlar")
        add_room("103", 1, "Standart 2 kishilik", 2, 350000, "available", "Wi-Fi, TV, Konditsioner, Dush", "1-qavat, katta ikki kishilik karavot (King size)")
        add_room("104", 1, "Ekonom 3 kishilik", 3, 400000, "available", "Wi-Fi, TV, Dush", "1-qavat, hamyonbop 3 kishilik oilaviy xona")
        add_room("105", 1, "Standart 2 kishilik", 2, 350000, "cleaning", "Wi-Fi, TV, Konditsioner, Dush", "1-qavat, tozalash jarayonida")
        
        # 2-qavat: Polulyuks va Lyuks
        add_room("201", 2, "Polulyuks (Junior Suite)", 2, 500000, "available", "Wi-Fi, Smart TV, Konditsioner, Balkon, Safe, Minibar", "2-qavat, shahar manzarasi bilan")
        add_room("202", 2, "Polulyuks (Junior Suite)", 2, 500000, "available", "Wi-Fi, Smart TV, Konditsioner, Safe, Minibar", "2-qavat, hovli manzarasi")
        add_room("203", 2, "Lyuks (Deluxe Suite)", 2, 750000, "available", "Wi-Fi, Smart TV, Konditsioner, Jacuzzi, Safe, Minibar, Balkon", "2-qavat, lyuks ta'mirlangan xona")
        add_room("204", 2, "Oila (Family Room)", 4, 650000, "available", "Wi-Fi, 2x Smart TV, 2x Konditsioner, Katta dush, Safe", "2-qavat, 2 xonali oilaviy lyuks")
        add_room("205", 2, "Standart 2 kishilik", 2, 350000, "maintenance", "Wi-Fi, TV, Konditsioner", "2-qavat, profilaktika / ta'mirlash")
        
        # 3-qavat: VIP va Prezident Suite
        add_room("301", 3, "VIP Suite", 2, 1000000, "available", "Wi-Fi, 4K Smart TV, Djakuzi, Minibar, Balkon, Panoramik oyna", "3-qavat, eng yuqori darajadagi xizmat")
        add_room("302", 3, "Prezident Suite (Penthouse)", 4, 1800000, "available", "Wi-Fi, 4K Smart TV, Jacuzzi, Oshxona, Terrasa, Safe, Minibar", "3-qavat, hashamatli shinam penthouse")
        
        print("Xonalar muvaffaqiyatli qo'shildi!")
        
        # Namunaviy mehmonlar kiritish
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=2)
        next_week = today + timedelta(days=5)
        
        guest_1 = {
            'full_name': 'Aliyev Sardor Rustamovich',
            'passport_series_num': 'AA1234567',
            'pinfl': '31201950000012',
            'birth_date': '1995-04-12',
            'gender': 'Erkak',
            'nationality': 'O‘zbekiston',
            'phone': '+998 90 123 45 67',
            'email': 'sardor.aliyev@mail.uz',
            'address': 'Samarqand shahri, Registon ko‘chasi 12',
            'notes': 'Doimiy mijoz, sokin xonani xush ko‘radi'
        }
        booking_1 = {
            'room_id': 2, # Xona 102
            'check_in_date': yesterday.strftime('%Y-%m-%d'),
            'check_in_time': '14:00',
            'check_out_date': tomorrow.strftime('%Y-%m-%d'),
            'check_out_time': '12:00',
            'adults': 2,
            'children': 0,
            'daily_price': 350000,
            'paid_amount': 700000, # 3 kun x 350000 = 1050000, 700000 to'langan, 350000 qoldiq
            'payment_method': 'Karta (Uzcard/Humo)',
            'purpose': 'Ish safari',
            'status': 'active',
            'special_requests': 'Ertalabki nonushta xonaga soat 08:30 da yetkazilsin'
        }
        create_registration(guest_1, booking_1)
        
        guest_2 = {
            'full_name': 'Smith John Robert',
            'passport_series_num': 'P8923412',
            'pinfl': '',
            'birth_date': '1988-10-25',
            'gender': 'Erkak',
            'nationality': 'AQSH (United States)',
            'phone': '+1 555 019 2834',
            'email': 'john.smith@example.com',
            'address': 'New York, 5th Avenue 450',
            'notes': 'Xorijiy sayyoh, ingliz tilida muloqot'
        }
        booking_2 = {
            'room_id': 8, # Xona 203 (Lyuks)
            'check_in_date': today.strftime('%Y-%m-%d'),
            'check_in_time': '11:30',
            'check_out_date': next_week.strftime('%Y-%m-%d'),
            'check_out_time': '12:00',
            'adults': 1,
            'children': 0,
            'daily_price': 750000,
            'paid_amount': 3750000, # To'liq to'langan
            'payment_method': 'Valyuta (USD)',
            'purpose': 'Sayohat',
            'status': 'active',
            'special_requests': 'Tog‘ va shahar bo‘ylab ekskursiya xizmati kerak'
        }
        create_registration(guest_2, booking_2)
        
        print("Namunaviy mehmonlar muvaffaqiyatli joylashtirildi!")
        
    conn.close()

if __name__ == '__main__':
    seed_initial_data()

