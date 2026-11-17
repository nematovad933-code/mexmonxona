// Mehmonxona Boshqaruv Tizimi - Frontend Logika

document.addEventListener('DOMContentLoaded', () => {
    initRegistrationCalculations();
    initPassportLookup();
    initModalHandlers();
    initAlertDismissal();
    initLiveSearch();
});

// 1. Ro'yxatga olish formasida kunlar, narx va qoldiqni avtomatik hisoblash
function initRegistrationCalculations() {
    const checkInInput = document.getElementById('check_in_date');
    const checkOutInput = document.getElementById('check_out_date');
    const roomSelect = document.getElementById('room_id');
    const dailyPriceInput = document.getElementById('daily_price');
    const paidAmountInput = document.getElementById('paid_amount');
    
    // Ko'rsatkich elementlari
    const totalDaysDisplay = document.getElementById('display_total_days');
    const totalAmountDisplay = document.getElementById('display_total_amount');
    const balanceDisplay = document.getElementById('display_balance');
    const hiddenTotalAmount = document.getElementById('hidden_total_amount');
    
    if (!checkInInput || !checkOutInput || !roomSelect || !dailyPriceInput) return;
    
    // Xona tanlanganda uning narxini avtomatik to'ldirish
    roomSelect.addEventListener('change', () => {
        const selectedOption = roomSelect.options[roomSelect.selectedIndex];
        const price = selectedOption.getAttribute('data-price');
        if (price) {
            dailyPriceInput.value = price;
            recalculateTotals();
        }
    });
    
    // Sanalar yoki narx o'zgarganda qayta hisoblash
    [checkInInput, checkOutInput, dailyPriceInput, paidAmountInput].forEach(elem => {
        if (elem) {
            elem.addEventListener('input', recalculateTotals);
            elem.addEventListener('change', recalculateTotals);
        }
    });
    
    function recalculateTotals() {
        const inDateVal = checkInInput.value;
        const outDateVal = checkOutInput.value;
        
        let days = 1;
        if (inDateVal && outDateVal) {
            const d1 = new Date(inDateVal);
            const d2 = new Date(outDateVal);
            const diffTime = d2 - d1;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            days = diffDays > 0 ? diffDays : 1;
        }
        
        const dailyPrice = parseFloat(dailyPriceInput.value) || 0;
        const total = days * dailyPrice;
        const paid = parseFloat(paidAmountInput ? paidAmountInput.value : 0) || 0;
        const balance = total - paid;
        
        if (totalDaysDisplay) totalDaysDisplay.textContent = days + " kun";
        if (totalAmountDisplay) totalAmountDisplay.textContent = formatNumber(total) + " so'm";
        if (balanceDisplay) {
            balanceDisplay.textContent = formatNumber(balance) + " so'm";
            if (balance > 0) {
                balanceDisplay.style.color = "var(--danger)";
            } else {
                balanceDisplay.style.color = "var(--success)";
            }
        }
        if (hiddenTotalAmount) hiddenTotalAmount.value = total;
    }
    
    // Boshlang'ich hisoblash
    recalculateTotals();
}

// 2. Pasport orqali avval kelgan mehmonni avtomatik topish
function initPassportLookup() {
    const passportInput = document.getElementById('passport_series_num');
    if (!passportInput) return;
    
    const lookupBadge = document.getElementById('passport_lookup_status');
    
    passportInput.addEventListener('blur', async () => {
        const passport = passportInput.value.trim();
        if (passport.length < 5) return;
        
        try {
            if (lookupBadge) lookupBadge.textContent = "Qidirilmoqda...";
            const res = await fetch(`/api/guest-by-passport?passport=${encodeURIComponent(passport)}`);
            const data = await res.json();
            
            if (data.found && data.guest) {
                const g = data.guest;
                const nameInput = document.getElementById('full_name');
                const phoneInput = document.getElementById('phone');
                const pinflInput = document.getElementById('pinfl');
                const birthInput = document.getElementById('birth_date');
                const genderSelect = document.getElementById('gender');
                const nationInput = document.getElementById('nationality');
                const emailInput = document.getElementById('email');
                const addressInput = document.getElementById('address');
                const guestIdInput = document.getElementById('guest_id');
                
                if (nameInput) nameInput.value = g.full_name;
                if (phoneInput) phoneInput.value = g.phone;
                if (pinflInput && g.pinfl) pinflInput.value = g.pinfl;
                if (birthInput && g.birth_date) birthInput.value = g.birth_date;
                if (genderSelect && g.gender) genderSelect.value = g.gender;
                if (nationInput && g.nationality) nationInput.value = g.nationality;
                if (emailInput && g.email) emailInput.value = g.email;
                if (addressInput && g.address) addressInput.value = g.address;
                if (guestIdInput) guestIdInput.value = g.id;
                
                if (lookupBadge) {
                    lookupBadge.textContent = "✓ Doimiy mehmon: " + g.full_name;
                    lookupBadge.className = "badge badge-success";
                }
            } else {
                if (lookupBadge) {
                    lookupBadge.textContent = "Yangi mehmon";
                    lookupBadge.className = "badge badge-info";
                }
            }
        } catch (e) {
            console.error(e);
        }
    });
}

// 3. Modal oynalar boshqaruvi
function initModalHandlers() {
    // Modalni ochish tugmalari
    document.querySelectorAll('[data-modal-target]').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-modal-target');
            const modal = document.getElementById(targetId);
            if (modal) {
                // Agar tugmada qo'shimcha parametrlar bo'lsa (masalan action URL, guest name, balance)
                const actionUrl = btn.getAttribute('data-action');
                if (actionUrl) {
                    const form = modal.querySelector('form');
                    if (form) form.action = actionUrl;
                }
                const guestName = btn.getAttribute('data-guest-name');
                const guestNameElem = modal.querySelector('.modal-guest-name');
                if (guestName && guestNameElem) guestNameElem.textContent = guestName;
                
                const balanceVal = btn.getAttribute('data-balance');
                const balanceInput = modal.querySelector('.modal-balance-input');
                const balanceText = modal.querySelector('.modal-balance-text');
                if (balanceVal) {
                    if (balanceInput) balanceInput.value = balanceVal;
                    if (balanceText) balanceText.textContent = formatNumber(parseFloat(balanceVal)) + " so'm";
                }
                
                modal.classList.add('active');
            }
        });
    });
    
    // Modalni yopish tugmalari
    document.querySelectorAll('[data-modal-close]').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal-overlay');
            if (modal) modal.classList.remove('active');
        });
    });
    
    // Modal foni bosilganda yopish
    document.querySelectorAll('.modal-overlay').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.remove('active');
        });
    });
}

// 4. Alertlarni yopish
function initAlertDismissal() {
    document.querySelectorAll('.alert-close-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const alert = btn.closest('.alert');
            if (alert) alert.remove();
        });
    });
}

// 5. Jadvalda jonli qidiruv
function initLiveSearch() {
    const searchInput = document.getElementById('table_live_search');
    const table = document.getElementById('guests_table');
    if (!searchInput || !table) return;
    
    searchInput.addEventListener('input', () => {
        const query = searchInput.value.toLowerCase().trim();
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(query)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

// Yordamchi raqam formatlash funksiyasi
function formatNumber(num) {
    return Number(num).toLocaleString('ru-RU');
}

