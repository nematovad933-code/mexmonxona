import sqlite3
import os
from datetime import datetime, date

DB_DIR = os.environ.get('RAILWAY_VOLUME_MOUNT_PATH', os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__))))
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'hotel_database.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Sozlamalar jadvali
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hotel_settings (
        id INTEGER PRIMARY KEY,
        hotel_name TEXT NOT NULL DEFAULT 'Grand Hotel Toshkent',
        hotel_stars INTEGER DEFAULT 4,
        address TEXT DEFAULT 'Toshkent shahri, Amir Temur shox ko‘chasi, 15-uy',
        phone TEXT DEFAULT '+998 71 200-00-00',
        email TEXT DEFAULT 'info@grandhotel.uz',
        inn TEXT DEFAULT '123456789',
        manager_name TEXT DEFAULT 'Administrator',
        currency TEXT DEFAULT 'so‘m',
        checkin_time TEXT DEFAULT '14:00',
        checkout_time TEXT DEFAULT '12:00'
    )
    ''')
    
    # 2. Xonalar jadvali
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT UNIQUE NOT NULL,
        floor INTEGER DEFAULT 1,
        room_type TEXT NOT NULL,
        capacity INTEGER DEFAULT 2,
        daily_price REAL NOT NULL,
        status TEXT DEFAULT 'available',
        amenities TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 3. Mehmonlar jadvali
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS guests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        passport_series_num TEXT NOT NULL,
        pinfl TEXT,
        birth_date TEXT,
        gender TEXT DEFAULT 'Erkak',
        nationality TEXT DEFAULT 'O‘zbekiston',
        phone TEXT NOT NULL,
        email TEXT,
        address TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 4. Band qilish va joylashish (Reservations) jadvali
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_code TEXT UNIQUE,
        guest_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        check_in_date TEXT NOT NULL,
        check_in_time TEXT DEFAULT '14:00',
        check_out_date TEXT NOT NULL,
        check_out_time TEXT DEFAULT '12:00',
        adults INTEGER DEFAULT 1,
        children INTEGER DEFAULT 0,
        daily_price REAL NOT NULL,
        total_days INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        paid_amount REAL DEFAULT 0,
        balance REAL NOT NULL,
        payment_method TEXT DEFAULT 'Naqd',
        purpose TEXT DEFAULT 'Sayohat',
        status TEXT DEFAULT 'active',
        special_requests TEXT,
        actual_check_out TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (guest_id) REFERENCES guests(id) ON DELETE CASCADE,
        FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE RESTRICT
    )
    ''')
    
    # 5. To'lovlar tarixi jadvali
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reservation_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        receipt_number TEXT,
        note TEXT,
        FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE
    )
    ''')
    
    # Dastlabki sozlamalarni kiritish
    cursor.execute('SELECT COUNT(*) FROM hotel_settings')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO hotel_settings (
            id, hotel_name, hotel_stars, address, phone, email, inn, manager_name, currency, checkin_time, checkout_time
        ) VALUES (
            1, 'Grand Hotel Toshkent', 4, 'Toshkent shahri, Amir Temur shox ko‘chasi, 15-uy',
            '+998 71 200-00-00', 'info@grandhotel.uz', '123456789', 'Administrator', 'so‘m', '14:00', '12:00'
        )
        ''')
    
    conn.commit()
    conn.close()

# --- SOZLAMALAR ---
def get_hotel_settings():
    conn = get_db()
    row = conn.execute('SELECT * FROM hotel_settings WHERE id = 1').fetchone()
    conn.close()
    if row:
        return dict(row)
    return {}

def update_hotel_settings(data):
    conn = get_db()
    conn.execute('''
    UPDATE hotel_settings SET
        hotel_name = ?,
        hotel_stars = ?,
        address = ?,
        phone = ?,
        email = ?,
        inn = ?,
        manager_name = ?,
        currency = ?,
        checkin_time = ?,
        checkout_time = ?
    WHERE id = 1
    ''', (
        data.get('hotel_name', 'Grand Hotel Toshkent'),
        int(data.get('hotel_stars', 4)),
        data.get('address', ''),
        data.get('phone', ''),
        data.get('email', ''),
        data.get('inn', ''),
        data.get('manager_name', ''),
        data.get('currency', 'so‘m'),
        data.get('checkin_time', '14:00'),
        data.get('checkout_time', '12:00')
    ))
    conn.commit()
    conn.close()

# --- XONALAR (ROOMS) ---
def get_all_rooms():
    conn = get_db()
    rooms = conn.execute('''
    SELECT r.*, 
           res.id as current_reservation_id,
           res.booking_code,
           g.full_name as current_guest_name,
           g.phone as current_guest_phone,
           res.check_in_date,
           res.check_out_date
    FROM rooms r
    LEFT JOIN reservations res ON r.id = res.room_id AND res.status = 'active'
    LEFT JOIN guests g ON res.guest_id = g.id
    ORDER BY r.floor ASC, r.room_number ASC
    ''').fetchall()
    conn.close()
    return [dict(r) for r in rooms]

def get_available_rooms():
    conn = get_db()
    rooms = conn.execute('''
    SELECT * FROM rooms 
    WHERE status = 'available'
    ORDER BY floor ASC, room_number ASC
    ''').fetchall()
    conn.close()
    return [dict(r) for r in rooms]

def get_room_by_id(room_id):
    conn = get_db()
    room = conn.execute('SELECT * FROM rooms WHERE id = ?', (room_id,)).fetchone()
    conn.close()
    return dict(room) if room else None

def add_room(room_number, floor, room_type, capacity, daily_price, status='available', amenities='', description=''):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO rooms (room_number, floor, room_type, capacity, daily_price, status, amenities, description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (room_number, floor, room_type, capacity, daily_price, status, amenities, description))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def update_room(room_id, room_number, floor, room_type, capacity, daily_price, status, amenities, description):
    conn = get_db()
    conn.execute('''
    UPDATE rooms SET
        room_number = ?,
        floor = ?,
        room_type = ?,
        capacity = ?,
        daily_price = ?,
        status = ?,
        amenities = ?,
        description = ?
    WHERE id = ?
    ''', (room_number, floor, room_type, capacity, daily_price, status, amenities, description, room_id))
    conn.commit()
    conn.close()

def update_room_status(room_id, status):
    conn = get_db()
    conn.execute('UPDATE rooms SET status = ? WHERE id = ?', (status, room_id))
    conn.commit()
    conn.close()

def delete_room(room_id):
    conn = get_db()
    conn.execute('DELETE FROM rooms WHERE id = ?', (room_id,))
    conn.commit()
    conn.close()

# --- MEHMONLAR (GUESTS) ---
def get_all_guests(search_query=None):
    conn = get_db()
    if search_query:
        param = f"%{search_query.strip()}%"
        guests = conn.execute('''
        SELECT g.*, COUNT(r.id) as total_visits, MAX(r.check_in_date) as last_visit
        FROM guests g
        LEFT JOIN reservations r ON g.id = r.guest_id
        WHERE g.full_name LIKE ? OR g.passport_series_num LIKE ? OR g.phone LIKE ? OR g.pinfl LIKE ?
        GROUP BY g.id
        ORDER BY g.id DESC
        ''', (param, param, param, param)).fetchall()
    else:
        guests = conn.execute('''
        SELECT g.*, COUNT(r.id) as total_visits, MAX(r.check_in_date) as last_visit
        FROM guests g
        LEFT JOIN reservations r ON g.id = r.guest_id
        GROUP BY g.id
        ORDER BY g.id DESC
        ''').fetchall()
    conn.close()
    return [dict(g) for g in guests]

def get_guest_by_id(guest_id):
    conn = get_db()
    guest = conn.execute('SELECT * FROM guests WHERE id = ?', (guest_id,)).fetchone()
    conn.close()
    return dict(guest) if guest else None

def find_guest_by_passport(passport):
    conn = get_db()
    clean_p = passport.strip().upper()
    guest = conn.execute('SELECT * FROM guests WHERE UPPER(REPLACE(passport_series_num, " ", "")) = UPPER(REPLACE(?, " ", ""))', (clean_p,)).fetchone()
    conn.close()
    return dict(guest) if guest else None

def add_guest(full_name, passport_series_num, pinfl, birth_date, gender, nationality, phone, email, address, notes):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO guests (full_name, passport_series_num, pinfl, birth_date, gender, nationality, phone, email, address, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (full_name.strip(), passport_series_num.strip().upper(), pinfl.strip() if pinfl else '',
          birth_date, gender, nationality, phone.strip(), email.strip() if email else '', address, notes))
    conn.commit()
    guest_id = cursor.lastrowid
    conn.close()
    return guest_id

def update_guest(guest_id, full_name, passport_series_num, pinfl, birth_date, gender, nationality, phone, email, address, notes):
    conn = get_db()
    conn.execute('''
    UPDATE guests SET
        full_name = ?,
        passport_series_num = ?,
        pinfl = ?,
        birth_date = ?,
        gender = ?,
        nationality = ?,
        phone = ?,
        email = ?,
        address = ?,
        notes = ?
    WHERE id = ?
    ''', (full_name.strip(), passport_series_num.strip().upper(), pinfl.strip() if pinfl else '',
          birth_date, gender, nationality, phone.strip(), email.strip() if email else '', address, notes, guest_id))
    conn.commit()
    conn.close()

def delete_guest(guest_id):
    conn = get_db()
    conn.execute('DELETE FROM guests WHERE id = ?', (guest_id,))
    conn.commit()
    conn.close()

# --- BAND QILISH VA JOYLASHTIRISH (RESERVATIONS) ---
import random
import time

def generate_booking_code():
    now = datetime.now()
    rand_suffix = random.randint(1000, 9999)
    return f"GH-{now.strftime('%y%m%d')}-{now.strftime('%H%M%S')}-{rand_suffix}"

def create_registration(guest_data, booking_data):
    """
    Mehmonni va uning joylashuvini bir vaqtda yaratish yoki mavjud mehmonni yangilash
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Mehmonni tekshirish yoki yaratish
    guest_id = booking_data.get('guest_id')
    passport = guest_data.get('passport_series_num', '').strip().upper()
    
    if guest_id:
        # Mavjud mehmonni yangilash
        cursor.execute('''
        UPDATE guests SET
            full_name = ?, passport_series_num = ?, pinfl = ?, birth_date = ?,
            gender = ?, nationality = ?, phone = ?, email = ?, address = ?, notes = ?
        WHERE id = ?
        ''', (
            guest_data['full_name'], passport, guest_data.get('pinfl', ''),
            guest_data.get('birth_date', ''), guest_data.get('gender', 'Erkak'),
            guest_data.get('nationality', 'O‘zbekiston'), guest_data['phone'],
            guest_data.get('email', ''), guest_data.get('address', ''),
            guest_data.get('notes', ''), guest_id
        ))
    else:
        # Pasport bo'yicha qidirib ko'ramiz
        existing = cursor.execute(
            'SELECT id FROM guests WHERE UPPER(REPLACE(passport_series_num, " ", "")) = UPPER(REPLACE(?, " ", ""))',
            (passport,)
        ).fetchone()
        
        if existing:
            guest_id = existing[0]
            cursor.execute('''
            UPDATE guests SET
                full_name = ?, pinfl = ?, birth_date = ?,
                gender = ?, nationality = ?, phone = ?, email = ?, address = ?, notes = ?
            WHERE id = ?
            ''', (
                guest_data['full_name'], guest_data.get('pinfl', ''),
                guest_data.get('birth_date', ''), guest_data.get('gender', 'Erkak'),
                guest_data.get('nationality', 'O‘zbekiston'), guest_data['phone'],
                guest_data.get('email', ''), guest_data.get('address', ''),
                guest_data.get('notes', ''), guest_id
            ))
        else:
            cursor.execute('''
            INSERT INTO guests (full_name, passport_series_num, pinfl, birth_date, gender, nationality, phone, email, address, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                guest_data['full_name'], passport, guest_data.get('pinfl', ''),
                guest_data.get('birth_date', ''), guest_data.get('gender', 'Erkak'),
                guest_data.get('nationality', 'O‘zbekiston'), guest_data['phone'],
                guest_data.get('email', ''), guest_data.get('address', ''),
                guest_data.get('notes', '')
            ))
            guest_id = cursor.lastrowid
            
    # 2. Kunlar va umumiy summani hisoblash
    check_in_date = booking_data['check_in_date']
    check_out_date = booking_data['check_out_date']
    
    d1 = datetime.strptime(check_in_date, '%Y-%m-%d')
    d2 = datetime.strptime(check_out_date, '%Y-%m-%d')
    total_days = max(1, (d2 - d1).days)
    
    daily_price = float(booking_data['daily_price'])
    total_amount = total_days * daily_price
    paid_amount = float(booking_data.get('paid_amount', 0))
    balance = total_amount - paid_amount
    booking_code = generate_booking_code()
    
    # 3. Reservation qo'shish
    cursor.execute('''
    INSERT INTO reservations (
        booking_code, guest_id, room_id, check_in_date, check_in_time,
        check_out_date, check_out_time, adults, children, daily_price,
        total_days, total_amount, paid_amount, balance, payment_method,
        purpose, status, special_requests
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        booking_code, guest_id, booking_data['room_id'],
        check_in_date, booking_data.get('check_in_time', '14:00'),
        check_out_date, booking_data.get('check_out_time', '12:00'),
        int(booking_data.get('adults', 1)), int(booking_data.get('children', 0)),
        daily_price, total_days, total_amount, paid_amount, balance,
        booking_data.get('payment_method', 'Naqd'),
        booking_data.get('purpose', 'Sayohat'),
        booking_data.get('status', 'active'),
        booking_data.get('special_requests', '')
    ))
    reservation_id = cursor.lastrowid
    
    # 4. Agar boshlang'ich to'lov qilingan bo'lsa, to'lovlar jadvaliga kiritish
    if paid_amount > 0:
        cursor.execute('''
        INSERT INTO payments (reservation_id, amount, payment_method, receipt_number, note)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            reservation_id, paid_amount, booking_data.get('payment_method', 'Naqd'),
            f"REC-{booking_code}", "Dastlabki to‘lov (Ro‘yxatdan o‘tishda)"
        ))
    
    # 5. Xonaning holatini yangilash (agar status 'active' bo'lsa 'occupied' ga o'tkazish)
    if booking_data.get('status', 'active') == 'active':
        cursor.execute('UPDATE rooms SET status = "occupied" WHERE id = ?', (booking_data['room_id'],))
        
    conn.commit()
    conn.close()
    return reservation_id

def get_reservation_by_id(reservation_id):
    conn = get_db()
    res = conn.execute('''
    SELECT r.*,
           g.full_name, g.passport_series_num, g.pinfl, g.birth_date, g.gender,
           g.nationality, g.phone, g.email, g.address, g.notes as guest_notes,
           rm.room_number, rm.room_type, rm.floor, rm.amenities as room_amenities
    FROM reservations r
    JOIN guests g ON r.guest_id = g.id
    JOIN rooms rm ON r.room_id = rm.id
    WHERE r.id = ?
    ''', (reservation_id,)).fetchone()
    conn.close()
    return dict(res) if res else None

def get_all_reservations(status=None, search=None, start_date=None, end_date=None):
    conn = get_db()
    query = '''
    SELECT r.*,
           g.full_name, g.passport_series_num, g.phone, g.nationality,
           rm.room_number, rm.room_type
    FROM reservations r
    JOIN guests g ON r.guest_id = g.id
    JOIN rooms rm ON r.room_id = rm.id
    WHERE 1=1
    '''
    params = []
    
    if status and status != 'all':
        if status == 'debtors':
            query += ' AND r.balance > 0 AND r.status = "active"'
        else:
            query += ' AND r.status = ?'
            params.append(status)
            
    if search:
        p = f"%{search.strip()}%"
        query += ' AND (g.full_name LIKE ? OR g.passport_series_num LIKE ? OR g.phone LIKE ? OR rm.room_number LIKE ? OR r.booking_code LIKE ?)'
        params.extend([p, p, p, p, p])
        
    if start_date:
        query += ' AND r.check_in_date >= ?'
        params.append(start_date)
        
    if end_date:
        query += ' AND r.check_out_date <= ?'
        params.append(end_date)
        
    query += ' ORDER BY r.id DESC'
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_reservation(reservation_id, data):
    conn = get_db()
    cursor = conn.cursor()
    
    # Eskisini olish
    old = cursor.execute('SELECT * FROM reservations WHERE id = ?', (reservation_id,)).fetchone()
    if not old:
        conn.close()
        return False
        
    check_in_date = data.get('check_in_date', old['check_in_date'])
    check_out_date = data.get('check_out_date', old['check_out_date'])
    d1 = datetime.strptime(check_in_date, '%Y-%m-%d')
    d2 = datetime.strptime(check_out_date, '%Y-%m-%d')
    total_days = max(1, (d2 - d1).days)
    
    daily_price = float(data.get('daily_price', old['daily_price']))
    total_amount = total_days * daily_price
    paid_amount = float(data.get('paid_amount', old['paid_amount']))
    balance = total_amount - paid_amount
    new_room_id = int(data.get('room_id', old['room_id']))
    new_status = data.get('status', old['status'])
    
    # Agar xona o'zgarsa, eski xonani bo'shatib, yangisini band qilish
    if old['room_id'] != new_room_id:
        cursor.execute('UPDATE rooms SET status = "available" WHERE id = ?', (old['room_id'],))
        if new_status == 'active':
            cursor.execute('UPDATE rooms SET status = "occupied" WHERE id = ?', (new_room_id,))
            
    cursor.execute('''
    UPDATE reservations SET
        room_id = ?,
        check_in_date = ?,
        check_in_time = ?,
        check_out_date = ?,
        check_out_time = ?,
        adults = ?,
        children = ?,
        daily_price = ?,
        total_days = ?,
        total_amount = ?,
        paid_amount = ?,
        balance = ?,
        payment_method = ?,
        purpose = ?,
        status = ?,
        special_requests = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (
        new_room_id, check_in_date, data.get('check_in_time', old['check_in_time']),
        check_out_date, data.get('check_out_time', old['check_out_time']),
        int(data.get('adults', old['adults'])), int(data.get('children', old['children'])),
        daily_price, total_days, total_amount, paid_amount, balance,
        data.get('payment_method', old['payment_method']),
        data.get('purpose', old['purpose']),
        new_status, data.get('special_requests', old['special_requests']),
        reservation_id
    ))
    
    # Agar status o'zgarsa
    if old['status'] != new_status:
        if new_status == 'checked_out':
            cursor.execute('UPDATE rooms SET status = "cleaning" WHERE id = ?', (new_room_id,))
        elif new_status == 'active':
            cursor.execute('UPDATE rooms SET status = "occupied" WHERE id = ?', (new_room_id,))
        elif new_status == 'cancelled':
            cursor.execute('UPDATE rooms SET status = "available" WHERE id = ?', (new_room_id,))
            
    conn.commit()
    conn.close()
    return True

def checkout_reservation(reservation_id, final_payment_amount=0, payment_method='Naqd'):
    conn = get_db()
    cursor = conn.cursor()
    
    res = cursor.execute('SELECT * FROM reservations WHERE id = ?', (reservation_id,)).fetchone()
    if not res:
        conn.close()
        return False
        
    final_payment_amount = float(final_payment_amount)
    new_paid = res['paid_amount'] + final_payment_amount
    new_balance = res['total_amount'] - new_paid
    
    # To'lov qo'shish agar summa > 0 bo'lsa
    if final_payment_amount > 0:
        cursor.execute('''
        INSERT INTO payments (reservation_id, amount, payment_method, receipt_number, note)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            reservation_id, final_payment_amount, payment_method,
            f"REC-{res['booking_code']}-OUT", "Yakuniy to‘lov (Chiqish vaqtida)"
        ))
        
    # Statusni o'zgartirish
    cursor.execute('''
    UPDATE reservations SET
        status = 'checked_out',
        paid_amount = ?,
        balance = ?,
        actual_check_out = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (new_paid, new_balance, reservation_id))
    
    # Xonani tozalash holatiga o'tkazish
    cursor.execute('UPDATE rooms SET status = "cleaning" WHERE id = ?', (res['room_id'],))
    
    conn.commit()
    conn.close()
    return True

def add_payment_to_reservation(reservation_id, amount, payment_method, note=''):
    conn = get_db()
    cursor = conn.cursor()
    
    res = cursor.execute('SELECT * FROM reservations WHERE id = ?', (reservation_id,)).fetchone()
    if not res:
        conn.close()
        return False
        
    amount = float(amount)
    new_paid = res['paid_amount'] + amount
    new_balance = res['total_amount'] - new_paid
    
    cursor.execute('''
    INSERT INTO payments (reservation_id, amount, payment_method, receipt_number, note)
    VALUES (?, ?, ?, ?, ?)
    ''', (
        reservation_id, amount, payment_method,
        f"REC-{res['booking_code']}-P", note or "Qo‘shimcha to‘lov"
    ))
    
    cursor.execute('''
    UPDATE reservations SET
        paid_amount = ?,
        balance = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (new_paid, new_balance, reservation_id))
    
    conn.commit()
    conn.close()
    return True

def get_payments_for_reservation(reservation_id):
    conn = get_db()
    payments = conn.execute('SELECT * FROM payments WHERE reservation_id = ? ORDER BY id ASC', (reservation_id,)).fetchall()
    conn.close()
    return [dict(p) for p in payments]

def delete_reservation(reservation_id):
    conn = get_db()
    cursor = conn.cursor()
    res = cursor.execute('SELECT room_id, status FROM reservations WHERE id = ?', (reservation_id,)).fetchone()
    if res and res['status'] == 'active':
        cursor.execute('UPDATE rooms SET status = "available" WHERE id = ?', (res['room_id'],))
    cursor.execute('DELETE FROM reservations WHERE id = ?', (reservation_id,))
    conn.commit()
    conn.close()
    return True

# --- DASHBOARD VA STATISTIKA ---
def get_dashboard_stats():
    conn = get_db()
    today_str = date.today().strftime('%Y-%m-%d')
    
    # Xonalar statistikasi
    total_rooms = conn.execute('SELECT COUNT(*) FROM rooms').fetchone()[0]
    available_rooms = conn.execute('SELECT COUNT(*) FROM rooms WHERE status = "available"').fetchone()[0]
    occupied_rooms = conn.execute('SELECT COUNT(*) FROM rooms WHERE status = "occupied"').fetchone()[0]
    cleaning_rooms = conn.execute('SELECT COUNT(*) FROM rooms WHERE status = "cleaning"').fetchone()[0]
    maintenance_rooms = conn.execute('SELECT COUNT(*) FROM rooms WHERE status = "maintenance"').fetchone()[0]
    
    occupancy_rate = round((occupied_rooms / total_rooms * 100), 1) if total_rooms > 0 else 0
    
    # Bugungi faol mehmonlar
    active_guests = conn.execute('SELECT COUNT(*) FROM reservations WHERE status = "active"').fetchone()[0]
    
    # Bugun keluvchilar (Check-in today)
    today_checkins = conn.execute('SELECT COUNT(*) FROM reservations WHERE check_in_date = ? AND status = "active"', (today_str,)).fetchone()[0]
    
    # Bugun ketuvchilar (Check-out today)
    today_checkouts = conn.execute('SELECT COUNT(*) FROM reservations WHERE check_out_date = ? AND status = "active"', (today_str,)).fetchone()[0]
    
    # Umumiy qarzdorlik
    total_debt = conn.execute('SELECT COALESCE(SUM(balance), 0) FROM reservations WHERE status = "active" AND balance > 0').fetchone()[0]
    
    # Bugungi tushum (Payments made today)
    today_income = conn.execute('''
    SELECT COALESCE(SUM(amount), 0) FROM payments 
    WHERE DATE(payment_date) = ?
    ''', (today_str,)).fetchone()[0]
    
    # Oylik umumiy tushum
    current_month_str = date.today().strftime('%Y-%m')
    monthly_income = conn.execute('''
    SELECT COALESCE(SUM(amount), 0) FROM payments 
    WHERE strftime('%Y-%m', payment_date) = ?
    ''', (current_month_str,)).fetchone()[0]
    
    # Jami ro'yxatga olingan mehmonlar soni
    total_guests = conn.execute('SELECT COUNT(*) FROM guests').fetchone()[0]
    
    conn.close()
    
    return {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'cleaning_rooms': cleaning_rooms,
        'maintenance_rooms': maintenance_rooms,
        'occupancy_rate': occupancy_rate,
        'active_guests': active_guests,
        'today_checkins': today_checkins,
        'today_checkouts': today_checkouts,
        'total_debt': total_debt,
        'today_income': today_income,
        'monthly_income': monthly_income,
        'total_guests': total_guests
    }

def get_recent_checkins(limit=5):
    conn = get_db()
    rows = conn.execute('''
    SELECT r.*, g.full_name, g.phone, g.passport_series_num, rm.room_number, rm.room_type
    FROM reservations r
    JOIN guests g ON r.guest_id = g.id
    JOIN rooms rm ON r.room_id = rm.id
    ORDER BY r.id DESC
    LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_today_operations():
    conn = get_db()
    today_str = date.today().strftime('%Y-%m-%d')
    
    # Bugun kelganlar / kelishi kerak bo'lganlar
    checkins = conn.execute('''
    SELECT r.*, g.full_name, g.phone, rm.room_number
    FROM reservations r
    JOIN guests g ON r.guest_id = g.id
    JOIN rooms rm ON r.room_id = rm.id
    WHERE r.check_in_date = ?
    ORDER BY r.check_in_time ASC
    ''', (today_str,)).fetchall()
    
    # Bugun chiqishi kerak bo'lganlar
    checkouts = conn.execute('''
    SELECT r.*, g.full_name, g.phone, rm.room_number
    FROM reservations r
    JOIN guests g ON r.guest_id = g.id
    JOIN rooms rm ON r.room_id = rm.id
    WHERE r.check_out_date = ? AND r.status = 'active'
    ORDER BY r.check_out_time ASC
    ''', (today_str,)).fetchall()
    
    conn.close()
    return {
        'checkins': [dict(c) for c in checkins],
        'checkouts': [dict(c) for c in checkouts]
    }
