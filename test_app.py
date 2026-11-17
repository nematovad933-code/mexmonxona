import unittest
from datetime import date, timedelta
from app import app
import database

class HotelAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        database.init_db()

    def test_01_dashboard(self):
        """Dashboard sahifasi to'g'ri ochilishini tekshirish"""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Boshqaruv Paneli", response.data)
        self.assertIn(b"Hozirgi Mehmonlar", response.data)
        print("✓ Dashboard sahifasi muvaffaqiyatli tekshirildi.")

    def test_02_registration_get(self):
        """Ro'yxatga olish formasi to'g'ri ochilishini tekshirish"""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Mehmonning Shaxsiy", response.data)
        self.assertIn(b"Joylashtirish va Xona Tanlash", response.data)
        print("✓ Ro'yxatga olish GET so'rovi muvaffaqiyatli.")

    def test_03_registration_post(self):
        """Yangi mehmonni ro'yxatga olish (POST) test qilish"""
        today = date.today().strftime('%Y-%m-%d')
        next_week = (date.today() + timedelta(days=3)).strftime('%Y-%m-%d')
        
        # Bo'sh xonani topamiz
        available = database.get_available_rooms()
        self.assertTrue(len(available) > 0, "Kamida bitta bo'sh xona bo'lishi kerak")
        test_room = available[0]
        
        form_data = {
            'full_name': 'Testov Test Testovich',
            'passport_series_num': 'AC9988771',
            'pinfl': '12345678901234',
            'birth_date': '1990-01-01',
            'gender': 'Erkak',
            'nationality': 'O‘zbekiston',
            'phone': '+998 90 999 88 77',
            'email': 'test@example.com',
            'address': 'Toshkent shahar, Chilonzor tumani',
            'notes': 'Test mehmon',
            'room_id': test_room['id'],
            'check_in_date': today,
            'check_in_time': '14:00',
            'check_out_date': next_week,
            'check_out_time': '12:00',
            'adults': 1,
            'children': 0,
            'daily_price': test_room['daily_price'],
            'paid_amount': test_room['daily_price'] * 2, # 3 kundan 2 kunlik to'langan
            'payment_method': 'Naqd',
            'purpose': 'Ish safari',
            'status': 'active',
            'special_requests': 'Tinch xona',
            'action_type': 'save'
        }
        
        response = self.client.post('/register', data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Testov Test Testovich", response.data)
        print("✓ Yangi mehmon muvaffaqiyatli ro'yxatga olindi.")

    def test_04_passport_lookup_api(self):
        """Pasport bo'yicha API qidiruvini tekshirish"""
        response = self.client.get('/api/guest-by-passport?passport=AC9988771')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['found'])
        self.assertEqual(data['guest']['full_name'], 'Testov Test Testovich')
        print("✓ Pasport qidiruv API muvaffaqiyatli tekshirildi.")

    def test_05_guests_list_and_filters(self):
        """Mehmonlar ro'yxati va filtrlarni tekshirish"""
        response = self.client.get('/guests?status=active')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Testov Test Testovich", response.data)
        
        response_debtors = self.client.get('/guests?status=debtors')
        self.assertEqual(response_debtors.status_code, 200)
        self.assertIn(b"Testov Test Testovich", response_debtors.data)
        
        response_search = self.client.get('/guests?search=Testov')
        self.assertEqual(response_search.status_code, 200)
        self.assertIn(b"AC9988771", response_search.data)
        print("✓ Mehmonlar ro'yxati va filtrlari muvaffaqiyatli tekshirildi.")

    def test_06_add_payment_and_checkout(self):
        """Qo'shimcha to'lov va Check-out amallarini tekshirish"""
        # Testov mehmonining buyurtmasini olamiz
        reservations = database.get_all_reservations(search='AC9988771')
        self.assertTrue(len(reservations) > 0)
        res_id = reservations[0]['id']
        balance = reservations[0]['balance']
        
        # 1. Qo'shimcha to'lov qo'shish
        pay_res = self.client.post(f'/reservation/{res_id}/add-payment', data={
            'amount': balance,
            'payment_method': 'Karta (Uzcard/Humo)',
            'note': 'To‘liq to‘lov'
        }, follow_redirects=True)
        self.assertEqual(pay_res.status_code, 200)
        
        updated_res = database.get_reservation_by_id(res_id)
        self.assertEqual(updated_res['balance'], 0.0)
        
        # 2. Check-out qilish
        checkout_res = self.client.post(f'/reservation/{res_id}/checkout', data={
            'final_payment': 0,
            'payment_method': 'Naqd'
        }, follow_redirects=True)
        self.assertEqual(checkout_res.status_code, 200)
        
        final_res = database.get_reservation_by_id(res_id)
        self.assertEqual(final_res['status'], 'checked_out')
        print("✓ Qo'shimcha to'lov va Check-out amallari to'liq ishladi.")

    def test_07_receipt_and_card_views(self):
        """Chek va Mehmon kartochkasi sahifalarini tekshirish"""
        reservations = database.get_all_reservations()
        res_id = reservations[0]['id']
        
        receipt_res = self.client.get(f'/reservation/{res_id}/receipt')
        self.assertEqual(receipt_res.status_code, 200)
        self.assertIn(b"TO\xe2\x80\x98LOV CHEKI", receipt_res.data)
        
        card_res = self.client.get(f'/reservation/{res_id}/card')
        self.assertEqual(card_res.status_code, 200)
        self.assertIn(b"MEHMONNI RO\xe2\x80\x98YXATGA OLISH KARTASI", card_res.data)
        print("✓ Chek va Mehmon kartochkasi shablonlari muvaffaqiyatli tekshirildi.")

    def test_08_rooms_management(self):
        """Xonalar boshqaruvi va yangi xona qo'shish"""
        rooms_res = self.client.get('/rooms')
        self.assertEqual(rooms_res.status_code, 200)
        self.assertIn(b"Xonalar Holati va Shaxmatka", rooms_res.data)
        
        # Yangi xona qo'shish
        add_res = self.client.post('/rooms/add', data={
            'room_number': '999',
            'floor': 4,
            'room_type': 'Penthouse Test',
            'capacity': 3,
            'daily_price': 1200000,
            'status': 'available',
            'amenities': 'Wi-Fi, Jacuzzi',
            'description': 'Test xona'
        }, follow_redirects=True)
        self.assertEqual(add_res.status_code, 200)
        self.assertIn(b"999", add_res.data)
        print("✓ Xonalar boshqaruvi muvaffaqiyatli tekshirildi.")

    def test_09_excel_export_and_backup(self):
        """Excel eksport va baza zaxirasi yuklab olishni tekshirish"""
        excel_res = self.client.get('/export/excel')
        self.assertEqual(excel_res.status_code, 200)
        self.assertTrue(len(excel_res.data) > 1000)
        self.assertEqual(excel_res.content_type, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        backup_res = self.client.get('/backup/db')
        self.assertEqual(backup_res.status_code, 200)
        self.assertTrue(len(backup_res.data) > 0)
        print("✓ Excel eksport va Baza zaxira nusxasi muvaffaqiyatli yuklandi.")

    def test_10_settings_update(self):
        """Sozlamalarni yangilashni tekshirish"""
        settings_res = self.client.post('/settings', data={
            'hotel_name': 'Grand Hotel Tashkent Deluxe',
            'hotel_stars': 5,
            'currency': 'so‘m',
            'address': 'Amir Temur ko‘chasi, 15',
            'phone': '+998 71 200 00 00',
            'email': 'info@grandhotel.uz',
            'inn': '987654321',
            'manager_name': 'Boshqaruvchi',
            'checkin_time': '14:00',
            'checkout_time': '12:00'
        }, follow_redirects=True)
        self.assertEqual(settings_res.status_code, 200)
        self.assertIn(b"Grand Hotel Tashkent Deluxe", settings_res.data)
        print("✓ Sozlamalar muvaffaqiyatli yangilandi.")

if __name__ == '__main__':
    unittest.main()

