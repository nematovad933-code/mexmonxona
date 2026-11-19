import os
import io
import shutil
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import database
import export_excel

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'hotel_management_system_secure_secret_key_2026')

# Baza va dastlabki ma'lumotlarni ishga tushirish (Railway / Gunicorn uchun)
import seed_data
database.init_db()
seed_data.seed_initial_data()

# Custom Jinja filtrlari
@app.template_filter('currency')
def currency_filter(value):
    try:
        val = float(value)
        return f"{val:,.0f}".replace(",", " ")
    except (ValueError, TypeError):
        return value

@app.template_filter('format_date')
def format_date_filter(value):
    if not value:
        return ""
    try:
        # Agar vaqt bilan bo'lsa
        if " " in str(value):
            dt = datetime.strptime(str(value).split(".")[0], "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d.%m.%Y %H:%M")
        dt = datetime.strptime(str(value), "%Y-%m-%d")
        return dt.strftime("%d.%m.%Y")
    except Exception:
        return value

# Barcha sahifalarga sozlamalarni uzatish
@app.context_processor
def inject_settings():
    settings = database.get_hotel_settings()
    now_date = date.today().strftime('%Y-%m-%d')
    return dict(hotel_settings=settings, current_date=now_date)

# ----------------- SAHIFALAR -----------------

@app.route('/')
@app.route('/dashboard')
def dashboard():
    stats = database.get_dashboard_stats()
    today_ops = database.get_today_operations()
    recent_checkins = database.get_recent_checkins(limit=6)
    rooms = database.get_all_rooms()
    return render_template(
        'dashboard.html',
        stats=stats,
        today_ops=today_ops,
        recent_checkins=recent_checkins,
        rooms=rooms,
        active_page='dashboard'
    )

@app.route('/register', methods=['GET', 'POST'])
def register_guest():
    if request.method == 'POST':
        try:
            # Mehmon ma'lumotlari
            guest_data = {
                'full_name': request.form.get('full_name', '').strip(),
                'passport_series_num': request.form.get('passport_series_num', '').strip().upper(),
                'pinfl': request.form.get('pinfl', '').strip(),
                'birth_date': request.form.get('birth_date', ''),
                'gender': request.form.get('gender', 'Erkak'),
                'nationality': request.form.get('nationality', 'O‘zbekiston'),
                'phone': request.form.get('phone', '').strip(),
                'email': request.form.get('email', '').strip(),
                'address': request.form.get('address', '').strip(),
                'notes': request.form.get('notes', '').strip()
            }
            
            # Joylashtirish ma'lumotlari
            room_id = int(request.form.get('room_id'))
            check_in_date = request.form.get('check_in_date')
            check_out_date = request.form.get('check_out_date')
            daily_price = float(request.form.get('daily_price', 0))
            paid_amount = float(request.form.get('paid_amount', 0))
            
            booking_data = {
                'guest_id': request.form.get('guest_id') or None,
                'room_id': room_id,
                'check_in_date': check_in_date,
                'check_in_time': request.form.get('check_in_time', '14:00'),
                'check_out_date': check_out_date,
                'check_out_time': request.form.get('check_out_time', '12:00'),
                'adults': int(request.form.get('adults', 1)),
                'children': int(request.form.get('children', 0)),
                'daily_price': daily_price,
                'paid_amount': paid_amount,
                'payment_method': request.form.get('payment_method', 'Naqd'),
                'purpose': request.form.get('purpose', 'Sayohat'),
                'status': request.form.get('status', 'active'),
                'special_requests': request.form.get('special_requests', '')
            }
            
            res_id = database.create_registration(guest_data, booking_data)
            flash(f"Mehmon '{guest_data['full_name']}' muvaffaqiyatli ro‘yxatga olindi!", "success")
            
            # Agar foydalanuvchi "Saqlash va Chek chiqarish" ni bosgan bo'lsa
            action = request.form.get('action_type', 'save')
            if action == 'print_receipt':
                return redirect(url_for('view_receipt', id=res_id))
            elif action == 'print_card':
                return redirect(url_for('view_registration_card', id=res_id))
            
            return redirect(url_for('guests_list'))
            
        except Exception as e:
            flash(f"Xatolik yuz berdi: {str(e)}", "danger")
            return redirect(url_for('register_guest'))

    # GET so'rovi
    preselected_room_id = request.args.get('room_id', type=int)
    rooms = database.get_all_rooms()
    available_rooms = database.get_available_rooms()
    today_str = date.today().strftime('%Y-%m-%d')
    tomorrow_str = (date.today().fromordinal(date.today().toordinal() + 1)).strftime('%Y-%m-%d')
    
    return render_template(
        'registration.html',
        rooms=rooms,
        available_rooms=available_rooms,
        preselected_room_id=preselected_room_id,
        today=today_str,
        tomorrow=tomorrow_str,
        active_page='register'
    )

@app.route('/guests')
def guests_list():
    status = request.args.get('status', 'all')
    search = request.args.get('search', '').strip()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    reservations = database.get_all_reservations(
        status=status,
        search=search,
        start_date=start_date,
        end_date=end_date
    )
    
    return render_template(
        'guests.html',
        reservations=reservations,
        current_status=status,
        search_query=search,
        start_date=start_date,
        end_date=end_date,
        active_page='guests'
    )

@app.route('/guest/<int:id>')
def guest_profile(id):
    guest = database.get_guest_by_id(id)
    if not guest:
        flash("Mehmon topilmadi!", "warning")
        return redirect(url_for('guests_list'))
        
    conn = database.get_db()
    reservations = conn.execute('''
    SELECT r.*, rm.room_number, rm.room_type
    FROM reservations r
    JOIN rooms rm ON r.room_id = rm.id
    WHERE r.guest_id = ?
    ORDER BY r.id DESC
    ''', (id,)).fetchall()
    conn.close()
    
    return render_template(
        'guest_profile.html',
        guest=guest,
        reservations=[dict(r) for r in reservations],
        active_page='guests'
    )

@app.route('/reservation/<int:id>/edit', methods=['GET', 'POST'])
def edit_reservation(id):
    res = database.get_reservation_by_id(id)
    if not res:
        flash("Buyurtma topilmadi!", "warning")
        return redirect(url_for('guests_list'))
        
    if request.method == 'POST':
        try:
            # 1. Mehmon ma'lumotlarini yangilash
            database.update_guest(
                res['guest_id'],
                request.form.get('full_name', '').strip(),
                request.form.get('passport_series_num', '').strip().upper(),
                request.form.get('pinfl', '').strip(),
                request.form.get('birth_date', ''),
                request.form.get('gender', 'Erkak'),
                request.form.get('nationality', 'O‘zbekiston'),
                request.form.get('phone', '').strip(),
                request.form.get('email', '').strip(),
                request.form.get('address', '').strip(),
                request.form.get('notes', '').strip()
            )
            
            # 2. Buyurtma ma'lumotlarini yangilash
            booking_update = {
                'room_id': int(request.form.get('room_id')),
                'check_in_date': request.form.get('check_in_date'),
                'check_in_time': request.form.get('check_in_time'),
                'check_out_date': request.form.get('check_out_date'),
                'check_out_time': request.form.get('check_out_time'),
                'adults': int(request.form.get('adults', 1)),
                'children': int(request.form.get('children', 0)),
                'daily_price': float(request.form.get('daily_price', 0)),
                'paid_amount': float(request.form.get('paid_amount', 0)),
                'payment_method': request.form.get('payment_method'),
                'purpose': request.form.get('purpose'),
                'status': request.form.get('status'),
                'special_requests': request.form.get('special_requests', '')
            }
            
            database.update_reservation(id, booking_update)
            flash("Ma'lumotlar muvaffaqiyatli yangilandi!", "success")
            return redirect(url_for('guests_list'))
            
        except Exception as e:
            flash(f"Yangilashda xatolik: {str(e)}", "danger")
            
    rooms = database.get_all_rooms()
    return render_template(
        'guest_edit.html',
        res=res,
        rooms=rooms,
        active_page='guests'
    )

@app.route('/reservation/<int:id>/checkout', methods=['POST'])
def checkout_guest(id):
    final_payment = float(request.form.get('final_payment', 0))
    payment_method = request.form.get('payment_method', 'Naqd')
    
    success = database.checkout_reservation(id, final_payment, payment_method)
    if success:
        flash("Mehmon muvaffaqiyatli ro‘yxatdan chiqarildi (Check-out) va xona tozalash holatiga o‘tkazildi!", "success")
    else:
        flash("Xatolik yuz berdi!", "danger")
    return redirect(url_for('guests_list'))

@app.route('/reservation/<int:id>/add-payment', methods=['POST'])
def add_payment(id):
    amount = float(request.form.get('amount', 0))
    payment_method = request.form.get('payment_method', 'Naqd')
    note = request.form.get('note', '')
    
    if amount <= 0:
        flash("To‘lov summasi 0 dan katta bo‘lishi kerak!", "warning")
    else:
        database.add_payment_to_reservation(id, amount, payment_method, note)
        flash(f"{amount:,.0f} so‘m to‘lov muvaffaqiyatli qabul qilindi!", "success")
        
    return redirect(request.referrer or url_for('guests_list'))

@app.route('/reservation/<int:id>/delete', methods=['POST'])
def delete_reservation(id):
    database.delete_reservation(id)
    flash("Ro‘yxatdan o‘tish ma'lumoti o‘chirildi!", "info")
    return redirect(url_for('guests_list'))

@app.route('/reservation/<int:id>/receipt')
def view_receipt(id):
    res = database.get_reservation_by_id(id)
    if not res:
        flash("Ma'lumot topilmadi!", "warning")
        return redirect(url_for('guests_list'))
        
    payments = database.get_payments_for_reservation(id)
    return render_template('receipt.html', res=res, payments=payments)

@app.route('/reservation/<int:id>/card')
def view_registration_card(id):
    res = database.get_reservation_by_id(id)
    if not res:
        flash("Ma'lumot topilmadi!", "warning")
        return redirect(url_for('guests_list'))
    return render_template('registration_card.html', res=res)

# ----------------- XONALAR BOSHQARUVI -----------------

@app.route('/rooms')
def rooms_management():
    rooms = database.get_all_rooms()
    stats = database.get_dashboard_stats()
    return render_template(
        'rooms.html',
        rooms=rooms,
        stats=stats,
        active_page='rooms'
    )

@app.route('/rooms/add', methods=['POST'])
def add_new_room():
    try:
        room_number = request.form.get('room_number', '').strip()
        floor = int(request.form.get('floor', 1))
        room_type = request.form.get('room_type', 'Standart')
        capacity = int(request.form.get('capacity', 2))
        daily_price = float(request.form.get('daily_price', 0))
        status = request.form.get('status', 'available')
        amenities = request.form.get('amenities', '')
        description = request.form.get('description', '')
        
        database.add_room(room_number, floor, room_type, capacity, daily_price, status, amenities, description)
        flash(f"{room_number}-raqamli yangi xona qo‘shildi!", "success")
    except Exception as e:
        flash(f"Xonani qo‘shishda xatolik: {str(e)}", "danger")
    return redirect(url_for('rooms_management'))

@app.route('/rooms/<int:id>/edit', methods=['POST'])
def edit_room(id):
    try:
        room_number = request.form.get('room_number', '').strip()
        floor = int(request.form.get('floor', 1))
        room_type = request.form.get('room_type')
        capacity = int(request.form.get('capacity', 2))
        daily_price = float(request.form.get('daily_price', 0))
        status = request.form.get('status')
        amenities = request.form.get('amenities', '')
        description = request.form.get('description', '')
        
        database.update_room(id, room_number, floor, room_type, capacity, daily_price, status, amenities, description)
        flash(f"{room_number}-raqamli xona ma'lumotlari yangilandi!", "success")
    except Exception as e:
        flash(f"Xatolik: {str(e)}", "danger")
    return redirect(url_for('rooms_management'))

@app.route('/rooms/<int:id>/status', methods=['POST'])
def change_room_status(id):
    new_status = request.form.get('status')
    database.update_room_status(id, new_status)
    flash("Xona holati yangilandi!", "success")
    return redirect(url_for('rooms_management'))

@app.route('/rooms/<int:id>/delete', methods=['POST'])
def delete_room(id):
    try:
        database.delete_room(id)
        flash("Xona o‘chirildi!", "info")
    except Exception as e:
        flash("Xonani o‘chirib bo‘lmadi. Ehtimol ushbu xonada arxivlangan buyurtmalar mavjud.", "danger")
    return redirect(url_for('rooms_management'))

# ----------------- SOZLAMALAR VA BAZA -----------------

@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    if request.method == 'POST':
        data = {
            'hotel_name': request.form.get('hotel_name'),
            'hotel_stars': request.form.get('hotel_stars'),
            'address': request.form.get('address'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'inn': request.form.get('inn'),
            'manager_name': request.form.get('manager_name'),
            'currency': request.form.get('currency', 'so‘m'),
            'checkin_time': request.form.get('checkin_time', '14:00'),
            'checkout_time': request.form.get('checkout_time', '12:00')
        }
        database.update_hotel_settings(data)
        flash("Mehmonxona sozlamalari muvaffaqiyatli saqlandi!", "success")
        return redirect(url_for('settings_page'))
        
    settings = database.get_hotel_settings()
    return render_template('settings.html', settings=settings, active_page='settings')

@app.route('/backup/db')
def backup_database():
    db_path = database.DB_PATH
    if os.path.exists(db_path):
        with open(db_path, 'rb') as f:
            data = io.BytesIO(f.read())
        filename = f"hotel_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        return send_file(data, as_attachment=True, download_name=filename, mimetype="application/x-sqlite3")
    flash("Baza fayli topilmadi!", "danger")
    return redirect(url_for('settings_page'))

# ----------------- EXCEL VA HISOBOTLAR -----------------

@app.route('/export/excel')
def export_excel_route():
    status = request.args.get('status', 'all')
    search = request.args.get('search', '').strip()
    excel_stream = export_excel.generate_guests_excel(status=status, search=search)
    
    filename = f"mehmonlar_royxati_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return send_file(
        excel_stream,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename
    )

# ----------------- API TEZKOR QIDIRUV -----------------

@app.route('/api/guest-by-passport')
def api_guest_by_passport():
    passport = request.args.get('passport', '').strip()
    if not passport:
        return jsonify({'found': False})
        
    guest = database.find_guest_by_passport(passport)
    if guest:
        return jsonify({'found': True, 'guest': guest})
    return jsonify({'found': False})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Mehmonxona boshqaruv tizimi ishga tushmoqda (Port: {port})...")
    print(f"Brauzer orqali oching: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
