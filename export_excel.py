import io
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from database import get_all_reservations, get_hotel_settings

def generate_guests_excel(status=None, search=None):
    """
    Mehmonlar va ularning joylashuv ma'lumotlarini Excel formatida yaratadi
    va BytesIO oqimi (buffer) sifatida qaytaradi.
    """
    settings = get_hotel_settings()
    reservations = get_all_reservations(status=status, search=search)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Mehmonlar ro'yxati"
    
    # Grid lines ko'rinishi
    ws.views.sheetView[0].showGridLines = True
    
    # Ranglar va shriftlar
    navy_header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    gold_fill = PatternFill(start_color="F59E0B", end_color="F59E0B", fill_type="solid")
    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    total_fill = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
    
    font_title = Font(name="Segoe UI", size=16, bold=True, color="1E3A8A")
    font_subtitle = Font(name="Segoe UI", size=10, italic=True, color="475569")
    font_header = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    font_data = Font(name="Segoe UI", size=10)
    font_bold = Font(name="Segoe UI", size=10, bold=True)
    
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )
    
    double_bottom_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='double', color='000000')
    )
    
    # 1. Mehmonxona nomi va sarlavha
    hotel_name = settings.get('hotel_name', 'Grand Hotel')
    ws.merge_cells('A1:S1')
    ws['A1'] = f"MEHMONXONA MEHMONLARI RO‘YXATI — {hotel_name.upper()}"
    ws['A1'].font = font_title
    ws['A1'].alignment = Alignment(horizontal="center", vertical="center")
    
    ws.merge_cells('A2:S2')
    export_time_str = datetime.now().strftime('%d.%m.%Y %H:%M')
    ws['A2'] = f"Hujjat yaratilgan vaqt: {export_time_str} | Telefon: {settings.get('phone', '')} | Manzil: {settings.get('address', '')}"
    ws['A2'].font = font_subtitle
    ws['A2'].alignment = Alignment(horizontal="center", vertical="center")
    
    ws.row_dimensions[1].height = 32
    ws.row_dimensions[2].height = 20
    ws.row_dimensions[3].height = 10
    
    # 2. Ustun sarlavhalari
    headers = [
        "№",
        "Buyurtma kodi",
        "Mehmon F.I.SH",
        "Pasport / ID",
        "JSHSHIR",
        "Telefon",
        "Fuqaroligi",
        "Xona",
        "Xona toifasi",
        "Kirish sanasi",
        "Chiqish sanasi",
        "Kunlar",
        "Kunlik narx",
        "Jami summa",
        "To‘langan",
        "Qoldiq qarz",
        "To‘lov turi",
        "Holati",
        "Tashrif maqsadi"
    ]
    
    ws.row_dimensions[4].height = 28
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_idx, value=header)
        cell.font = font_header
        cell.fill = navy_header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
        
    # 3. Ma'lumotlarni to'ldirish
    current_row = 5
    total_revenue_sum = 0
    total_paid_sum = 0
    total_balance_sum = 0
    
    status_uz = {
        'active': 'Yashamoqda (Faol)',
        'checked_out': 'Chiqib ketgan',
        'reserved': 'Band qilingan',
        'cancelled': 'Bekor qilingan'
    }
    
    for idx, r in enumerate(reservations, 1):
        total_revenue_sum += float(r['total_amount'])
        total_paid_sum += float(r['paid_amount'])
        total_balance_sum += float(r['balance'])
        
        row_data = [
            idx,
            r.get('booking_code', ''),
            r.get('full_name', ''),
            r.get('passport_series_num', ''),
            r.get('pinfl', ''),
            r.get('phone', ''),
            r.get('nationality', ''),
            r.get('room_number', ''),
            r.get('room_type', ''),
            r.get('check_in_date', ''),
            r.get('check_out_date', ''),
            int(r.get('total_days', 1)),
            float(r.get('daily_price', 0)),
            float(r.get('total_amount', 0)),
            float(r.get('paid_amount', 0)),
            float(r.get('balance', 0)),
            r.get('payment_method', ''),
            status_uz.get(r.get('status'), r.get('status', '')),
            r.get('purpose', '')
        ]
        
        ws.row_dimensions[current_row].height = 22
        is_even = (idx % 2 == 0)
        
        for col_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=current_row, column=col_idx, value=val)
            cell.font = font_data
            cell.border = thin_border
            if is_even:
                cell.fill = zebra_fill
                
            # Raqamli formatlar va tekislash
            if col_idx in [1, 10, 11, 12]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx in [13, 14, 15, 16]:
                cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal="right", vertical="center")
            elif col_idx in [2, 4, 6]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")
                
        current_row += 1
        
    # 4. Yakuniy qator (Total)
    ws.row_dimensions[current_row].height = 25
    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=13)
    sum_label_cell = ws.cell(row=current_row, column=1, value="JAMI SUMMALAR:")
    sum_label_cell.font = font_bold
    sum_label_cell.alignment = Alignment(horizontal="right", vertical="center")
    
    # Border va rang berish birlashtirilgan kataklarga
    for c in range(1, 14):
        c_cell = ws.cell(row=current_row, column=c)
        c_cell.fill = total_fill
        c_cell.border = double_bottom_border
        
    # Jami summa
    cell_tot = ws.cell(row=current_row, column=14, value=total_revenue_sum)
    cell_tot.font = font_bold
    cell_tot.fill = total_fill
    cell_tot.number_format = '#,##0'
    cell_tot.alignment = Alignment(horizontal="right", vertical="center")
    cell_tot.border = double_bottom_border
    
    # Jami to'langan
    cell_paid = ws.cell(row=current_row, column=15, value=total_paid_sum)
    cell_paid.font = font_bold
    cell_paid.fill = total_fill
    cell_paid.number_format = '#,##0'
    cell_paid.alignment = Alignment(horizontal="right", vertical="center")
    cell_paid.border = double_bottom_border
    
    # Jami qoldiq qarz
    cell_bal = ws.cell(row=current_row, column=16, value=total_balance_sum)
    cell_bal.font = font_bold
    cell_bal.fill = total_fill
    cell_bal.number_format = '#,##0'
    cell_bal.alignment = Alignment(horizontal="right", vertical="center")
    cell_bal.border = double_bottom_border
    
    for c in range(17, 20):
        c_cell = ws.cell(row=current_row, column=c)
        c_cell.fill = total_fill
        c_cell.border = double_bottom_border
        
    # 5. Ustun kengliklarini avtomatik to'g'rilash
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            # Sarlavha birlashgan qatorlarini hisobga olmaslik
            if cell.row in [1, 2, current_row]:
                continue
            if cell.value:
                val_str = str(cell.value)
                max_len = max(max_len, len(val_str))
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)
        
    # Birinchi ustun torroq bo'lsin
    ws.column_dimensions['A'].width = 6
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 28
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

