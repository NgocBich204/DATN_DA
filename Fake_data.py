import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta, time
import unidecode

# =========================
# ⚙️ KHỞI TẠO
# =========================
fake = Faker("vi_VN")
random.seed(42)

TARGET_ROWS = 50000
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 30)
repeat_rate = 0.55

# PHẢI KHAI BÁO TRƯỚC KHI DÙNG
num_customers = 10000
num_repeat = int(num_customers * repeat_rate)
num_single = num_customers - num_repeat

# Nguồn truy cập với trọng số
traffic_sources = [
    ("Tự tìm kiếm", 40),
    ("Bạn bè giới thiệu", 25),
    ("Quảng cáo Facebook", 20),
    ("Email Marketing", 10),
    ("KOL/Influencer", 5)
]

payment_methods = ["COD", "Chuyển khoản", "Ví điện tử", "Thẻ tín dụng"]

# =========================
# 🧩 DANH MỤC SẢN PHẨM
# =========================
sneaker_products = [
    # (Tên SP, Nhóm, NSX, Trọng số bán, Hệ số giá thương hiệu)
    ("Air Force 1", "Lifestyle", "Nike", 30, 1.2),
    ("Air Jordan 1", "Basketball", "Nike", 25, 1.2),
    ("Yeezy Boost 350", "Lifestyle", "Adidas", 15, 1.0),
    ("Ultraboost 22", "Running", "Adidas", 10, 1.0),
    ("Chuck Taylor All Star", "Classic", "Converse", 8, 0.8),
    ("RS-X", "Lifestyle", "Puma", 5, 0.9),
    ("574 Core", "Lifestyle", "New Balance", 3, 0.85),
    ("FuelCell Rebel", "Running", "New Balance", 2, 0.85),
    ("KD15", "Basketball", "Nike", 1.5, 1.2),
    ("Dame 8", "Basketball", "Adidas", 0.5, 1.0),
]

versions = ["Classic", "Limited Edition", "2023 Edition", "Premium", "Street Style"]

# Tạo SKU cố định cho mỗi sản phẩm (1 SP = 1 SKU)
sku_dict = {}
sku_counter = 1000
for ten_sp, nhom_sp, nsx, _, _ in sneaker_products:
    sku_counter += 1
    sku_dict[(ten_sp, nsx)] = sku_counter

# =========================
# 💰 KHUNG GIÁ THEO AOV
# =========================
price_ranges = [
    # (min, max, weight, label)
    (200000, 450000, 50, "Nhỏ"),
    (600000, 1500000, 35, "Trung bình"),
    (2000000, 5000000, 15, "Cao"),
]

def get_base_price():
    """Lấy giá cơ bản theo khung AOV"""
    selected = random.choices(price_ranges, weights=[w for _, _, w, _ in price_ranges])[0]
    min_price, max_price, _, _ = selected
    return random.randint(min_price // 100000, max_price // 100000) * 100000

# =========================
# 🗺️ ĐỊA CHỈ VIỆT NAM CHI TIẾT (Tỉnh > Quận > Xã)
# =========================
locations = {
    ("Hà Nội", 40): {
        "Ba Đình": ["Phường Điện Biên", "Phường Đội Cấn", "Phường Ngọc Hà", "Phường Giảng Võ"],
        "Hoàn Kiếm": ["Phường Hàng Bạc", "Phường Hàng Gai", "Phường Hàng Trống", "Phường Lý Thái Tổ"],
        "Hai Bà Trưng": ["Phường Bạch Đằng", "Phường Minh Khai", "Phường Vĩnh Tuy", "Phường Bách Khoa"],
        "Đống Đa": ["Phường Văn Miếu", "Phường Khương Thượng", "Phường Láng Thượng", "Phường Ô Chợ Dừa"],
        "Tây Hồ": ["Phường Nhật Tân", "Phường Quảng An", "Phường Xuân La", "Phường Bưởi"],
        "Cầu Giấy": ["Phường Dịch Vọng", "Phường Mai Dịch", "Phường Nghĩa Đô", "Phường Trung Hòa"],
        "Thanh Xuân": ["Phường Nhân Chính", "Phường Thanh Xuân Bắc", "Phường Khương Mai", "Phường Kim Giang"],
        "Hoàng Mai": ["Phường Đại Kim", "Phường Định Công", "Phường Giáp Bát", "Phường Lĩnh Nam"],
        "Long Biên": ["Phường Giang Biên", "Phường Đức Giang", "Phường Gia Thụy", "Phường Ngọc Lâm"],
        "Nam Từ Liêm": ["Phường Mỹ Đình 1", "Phường Mỹ Đình 2", "Phường Trung Văn", "Phường Cầu Diễn"],
    },
    ("TP HCM", 30): {
        "Quận 1": ["Phường Bến Nghé", "Phường Bến Thành", "Phường Nguyễn Thái Bình", "Phường Phạm Ngũ Lão"],
        "Quận 3": ["Phường Võ Thị Sáu", "Phường 1", "Phường 2", "Phường 9"],
        "Bình Thạnh": ["Phường 1", "Phường 2", "Phường 11", "Phường 22"],
        "Phú Nhuận": ["Phường 1", "Phường 4", "Phường 15", "Phường 17"],
        "Thủ Đức": ["Phường Linh Trung", "Phường Linh Xuân", "Phường Bình Thọ", "Phường Hiệp Bình Phước"],
        "Quận 7": ["Phường Tân Phú", "Phường Tân Hưng", "Phường Tân Kiểng", "Phường Bình Thuận"],
        "Quận 10": ["Phường 1", "Phường 2", "Phường 4", "Phường 15"],
        "Tân Bình": ["Phường 1", "Phường 2", "Phường 4", "Phường 12"],
        "Gò Vấp": ["Phường 1", "Phường 3", "Phường 8", "Phường 16"],
    },
    ("Đà Nẵng", 15): {
        "Hải Châu": ["Phường Thạch Thang", "Phường Hải Châu 1", "Phường Hòa Thuận Đông", "Phường Thuận Phước"],
        "Thanh Khê": ["Phường Tân Chính", "Phường Thanh Khê Đông", "Phường Hòa Khê", "Phường Vĩnh Trung"],
        "Sơn Trà": ["Phường Thọ Quang", "Phường Nại Hiên Đông", "Phường Mân Thái", "Phường An Hải Bắc"],
        "Ngũ Hành Sơn": ["Phường Mỹ An", "Phường Hòa Hải", "Phường Hòa Quý", "Phường Khuê Mỹ"],
        "Liên Chiểu": ["Phường Hòa Hiệp Bắc", "Phường Hòa Khánh Bắc", "Phường Hòa Minh"],
    },
    ("Hải Phòng", 8): {
        "Hồng Bàng": ["Phường Quán Toan", "Phường Hùng Vương", "Phường Sở Dầu", "Phường Phan Bội Châu"],
        "Ngô Quyền": ["Phường Máy Chai", "Phường Cầu Đất", "Phường Lạch Tray", "Phường Đông Khê"],
        "Lê Chân": ["Phường Cát Dài", "Phường An Biên", "Phường Trần Nguyên Hãn", "Phường Hồ Nam"],
        "Hải An": ["Phường Đông Hải 1", "Phường Đông Hải 2", "Phường Đằng Lâm", "Phường Nam Hải"],
    },
    ("Cần Thơ", 7): {
        "Ninh Kiều": ["Phường Cái Khế", "Phường An Hòa", "Phường Thới Bình", "Phường An Nghiệp"],
        "Bình Thủy": ["Phường Bình Thủy", "Phường Trà An", "Phường Trà Nóc", "Phường Long Hòa"],
        "Cái Răng": ["Phường Lê Bình", "Phường Hưng Phú", "Phường Hưng Thạnh", "Phường Ba Láng"],
        "Ô Môn": ["Phường Châu Văn Liêm", "Phường Thới Hòa", "Phường Thới Long", "Phường Trường Lạc"],
    },
}

# =========================
# 👥 TẠO TÊN KHÁCH HÀNG
# =========================
ho_list = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ",
    "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Tạ", "Trương", "Mai", "Đoàn"
]
dem_nam = ["Văn", "Quốc", "Tuấn", "Mạnh", "Đình", "Hải", "Trung", "Thiện", "Minh", "Anh", "Hoàng", "Đức", "Công", "Xuân", "Duy"]
dem_nu = ["Thị", "Ngọc", "Thu", "Diệu", "Bảo", "Thùy", "Hồng", "Phúc", "Thanh", "Khánh", "Ánh", "Kim", "Huyền", "My", "Như"]
ten_nam = ["Nam", "Dũng", "Tuấn", "Quân", "Huy", "Sơn", "Đạt", "Trí", "Đức", "Long", "Tài", "Khang", "Phúc", "Kiên", "Cường", "Bình", "Thắng", "Hoàng", "Anh"]
ten_nu = ["Hoa", "Tâm", "Hà", "Trang", "Hương", "Lan", "Phương", "Linh", "Giang", "Ngân", "Vy", "Tú", "Hạnh", "Thảo", "Yến", "Nhung", "Châu", "Mai", "Dung", "Nhi"]

print("🔄 Đang tạo danh sách khách hàng...")

# Tạo pool tên trước
name_pool_nam = [(f"{ho} {dem} {ten}", "Nam") 
                 for ho in ho_list 
                 for dem in dem_nam 
                 for ten in ten_nam]
name_pool_nu = [(f"{ho} {dem} {ten}", "Nữ") 
                for ho in ho_list 
                for dem in dem_nu 
                for ten in ten_nu]

# Shuffle để random
random.shuffle(name_pool_nam)
random.shuffle(name_pool_nu)

# Lấy theo tỷ lệ 70% Nam, 30% Nữ
num_male = int(num_customers * 0.7)
num_female = num_customers - num_male

# Nếu không đủ tên, lặp lại pool
while len(name_pool_nam) < num_male:
    name_pool_nam.extend(name_pool_nam[:num_male - len(name_pool_nam)])
while len(name_pool_nu) < num_female:
    name_pool_nu.extend(name_pool_nu[:num_female - len(name_pool_nu)])

unique_names = name_pool_nam[:num_male] + name_pool_nu[:num_female]
random.shuffle(unique_names)

print(f"✅ Đã tạo {len(unique_names)} khách hàng")

# =========================
# 📅 HÀM SINH NGÀY + GIỜ MUA
# =========================
def generate_purchase_datetime(start, end, recency_weight):
    """Sinh ngày giờ mua với ưu tiên cuối tuần và giờ vàng"""
    # Xác định khoảng thời gian dựa trên recency
    if recency_weight > 0.7:
        days_range = 180
        base_date = end - timedelta(days=days_range)
    elif recency_weight > 0.5:
        days_range = 365
        base_date = end - timedelta(days=days_range)
    else:
        days_range = 365
        base_date = start + timedelta(days=180)
    
    max_attempts = 100
    for _ in range(max_attempts):
        random_date = base_date + timedelta(days=random.randint(0, min(days_range, (end - base_date).days)))
        weekday = random_date.weekday()
        
        # Lọc theo ngày trong tuần
        if weekday == 4 and random.random() < 0.85:  # T6
            break
        elif weekday == 5 and random.random() < 0.90:  # T7
            break
        elif weekday == 6 and random.random() < 0.88:  # CN
            break
        elif random.random() < 0.35:  # Ngày thường
            break
    else:
        random_date = base_date + timedelta(days=random.randint(0, min(days_range, (end - base_date).days)))
    
    # Sinh giờ mua: 8h-22h, ưu tiên 20h-22h (giờ vàng)
    hour_weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 1]  # 15 giá trị cho 8h-22h
    hour = random.choices(range(8, 23), weights=hour_weights)[0]
    minute = random.randint(0, 59)
    
    return datetime.combine(random_date, time(hour, minute))

# =========================
# 🎂 HÀM SINH NGÀY SINH
# =========================
def generate_birthday():
    """Sinh ngày sinh, ưu tiên 20-22 tuổi"""
    age_ranges = [
        (20, 22, 45),
        (23, 25, 25),
        (26, 30, 15),
        (18, 19, 8),
        (31, 35, 5),
        (36, 45, 2),
    ]
    
    selected = random.choices(age_ranges, weights=[w for _, _, w in age_ranges])[0]
    min_age, max_age, _ = selected
    
    birth_year = 2024 - random.randint(min_age, max_age)
    return fake.date_between(datetime(birth_year, 1, 1), datetime(birth_year, 12, 31))

# =========================
# 🏪 HÀM CHỌN ĐỊA ĐIỂM
# =========================
def select_location():
    """Chọn địa điểm: Tỉnh > Quận > Xã"""
    location_keys = list(locations.keys())
    weights = [weight for _, weight in location_keys]
    selected_key = random.choices(location_keys, weights=weights)[0]
    tinh, _ = selected_key
    
    districts = locations[selected_key]
    quan = random.choice(list(districts.keys()))
    xa = random.choice(districts[quan])
    
    return tinh, quan, xa

# =========================
# 🛍️ HÀM CHỌN SẢN PHẨM
# =========================
def select_products(monetary_factor):
    """Chọn sản phẩm cho đơn hàng"""
    weights = [weight for _, _, _, weight, _ in sneaker_products]
    num_products = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
    
    selected = []
    for _ in range(num_products):
        product = random.choices(sneaker_products, weights=weights)[0]
        ten_sp, nhom_sp, nsx, _, brand_factor = product
        
        sku = sku_dict[(ten_sp, nsx)]
        
        # Kiểm tra SKU trùng -> gộp số lượng
        existing = next((p for p in selected if p['sku'] == sku), None)
        if existing:
            existing['soluong'] += random.choices([1, 2, 3], weights=[60, 30, 10])[0]
        else:
            soluong = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
            
            # Tính giá
            base_price = get_base_price()
            gia = int(base_price * brand_factor * monetary_factor)
            
            # 10% sản phẩm premium
            if random.random() < 0.1:
                gia = int(gia * random.uniform(1.5, 2.5))
            
            phien_ban = random.choice(versions)
            
            selected.append({
                'ten_sp': ten_sp,
                'nhom_sp': nhom_sp,
                'nsx': nsx,
                'sku': sku,
                'phien_ban': phien_ban,
                'soluong': soluong,
                'gia': gia
            })
    
    return selected

# =========================
# PHÂN KHÚC KHÁCH HÀNG RFM
# =========================
customer_segments = []

# Champion (10% of repeat)
for _ in range(int(num_repeat * 0.10)):
    customer_segments.append({
        'type': 'champion',
        'num_orders': random.randint(8, 15),
        'recency_weight': 0.9,
        'monetary_factor': random.uniform(1.5, 3.0)
    })

# Loyal (25% of repeat)
for _ in range(int(num_repeat * 0.25)):
    customer_segments.append({
        'type': 'loyal',
        'num_orders': random.randint(5, 8),
        'recency_weight': 0.7,
        'monetary_factor': random.uniform(1.2, 1.8)
    })

# Potential (30% of repeat)
for _ in range(int(num_repeat * 0.30)):
    customer_segments.append({
        'type': 'potential',
        'num_orders': random.randint(3, 5),
        'recency_weight': 0.6,
        'monetary_factor': random.uniform(1.0, 1.5)
    })

# Recent (20% of repeat)
for _ in range(int(num_repeat * 0.20)):
    customer_segments.append({
        'type': 'recent',
        'num_orders': random.randint(2, 3),
        'recency_weight': 0.8,
        'monetary_factor': random.uniform(0.8, 1.2)
    })

# At Risk (15% of repeat)
for _ in range(num_repeat - len(customer_segments)):
    customer_segments.append({
        'type': 'at_risk',
        'num_orders': random.randint(3, 6),
        'recency_weight': 0.2,
        'monetary_factor': random.uniform(1.0, 1.5)
    })

# Single customers
for _ in range(num_single):
    customer_segments.append({
        'type': 'single',
        'num_orders': 1,
        'recency_weight': random.uniform(0.3, 0.9),
        'monetary_factor': random.uniform(0.5, 1.5)
    })

random.shuffle(customer_segments)

print(f"✅ Đã tạo {len(customer_segments)} phân khúc khách hàng")

# =========================
# SINH DỮ LIỆU
# =========================
data = []
order_id_counter = 200000
customer_id_counter = 1

print("\n🔄 Đang sinh dữ liệu đơn hàng...")
progress_step = max(1, len(customer_segments) // 10)

for i, segment in enumerate(customer_segments):
    if len(data) >= TARGET_ROWS:
        break
    
    # Hiển thị tiến trình
    if i > 0 and i % progress_step == 0:
        print(f"  ⏳ Đã xử lý {i}/{len(customer_segments)} khách hàng ({len(data):,} dòng)")
    
    name, gender = unique_names[i]
    email = unidecode.unidecode(name).replace(" ", ".").lower() + "@gmail.com"
    birthday = generate_birthday()
    sdt = "0" + str(random.randint(900000000, 999999999))
    khachhang_id = customer_id_counter
    customer_id_counter += 1
    
    num_orders = segment['num_orders']
    recency_weight = segment['recency_weight']
    monetary_factor = segment['monetary_factor']
    
    # Sinh các đơn hàng
    for _ in range(num_orders):
        if len(data) >= TARGET_ROWS:
            break
        
        order_id_counter += 1
        ma_don = order_id_counter
        
        # Sinh thời gian mua
        thoi_gian_mua = generate_purchase_datetime(START_DATE, END_DATE, recency_weight)
        ngay_mua_str = thoi_gian_mua.strftime("%d/%m/%Y")
        thoi_gian_mua_str = thoi_gian_mua.strftime("%d/%m/%Y %H:%M")
        
        # Chọn traffic, địa điểm
        traffic = random.choices([t for t, _ in traffic_sources], weights=[w for _, w in traffic_sources])[0]
        tinh, quan, xa = select_location()
        pttt = random.choice(payment_methods)
        
        # Chọn sản phẩm
        products = select_products(monetary_factor)
        
        # Tạo dòng cho mỗi sản phẩm
        for product in products:
            gia = product['gia']
            soluong = product['soluong']
            
            doanh_thu = gia * soluong
            khuyenmai = int(doanh_thu * random.uniform(0, 0.3))
            van_chuyen = random.choice([0, 15000, 20000, 30000, 40000])
            doanh_thu_thuan = doanh_thu - khuyenmai - van_chuyen
            
            data.append([
                khachhang_id, name, email, sdt, gender, birthday.strftime("%d/%m/%Y"),
                ma_don, ngay_mua_str, thoi_gian_mua_str, traffic, tinh, quan, xa,
                product['ten_sp'], product['nhom_sp'], product['sku'], product['phien_ban'], product['nsx'],
                pttt, soluong, gia, doanh_thu, khuyenmai, van_chuyen, doanh_thu_thuan
            ])

print(f"\n✅ Đã sinh {len(data):,} dòng dữ liệu")

# =========================
# XUẤT DỮ LIỆU
# =========================
columns = [
    "KhachHangID", "HoTen", "Email", "SDT", "GioiTinh", "NgaySinh",
    "MaDonHang", "NgayMua", "ThoiGianMua", "Traffic", "TinhThanh", "QuanHuyen", "PhuongXa",
    "TenSanPham", "TenNhomSanPham", "SKU", "PhienBan", "NhaSanXuat",
    "PhuongThucTT", "SoLuong", "GiaSP", "DoanhThu", "TienKhuyenMai",
    "VanChuyen", "DoanhThuThuan"
]

print("📝 Đang tạo DataFrame...")
df = pd.DataFrame(data, columns=columns)
df["KhachHangID"] = df["KhachHangID"].astype(str)

print("💾 Đang xuất file Excel...")
df.to_excel("sneaker_sales_data_final.xlsx", index=False)

# =========================
# THỐNG KÊ
# =========================
print("\n" + "=" * 70)
print("✅ SINH DỮ LIỆU THÀNH CÔNG - SNEAKER SALES DATA")
print("=" * 70)

num_customers_actual = df["KhachHangID"].nunique()
num_orders = df["MaDonHang"].nunique()
repeat_customers = df.groupby("KhachHangID")["MaDonHang"].nunique()
ty_le_quay_lai = (repeat_customers[repeat_customers > 1].count() / num_customers_actual) * 100

print(f"\n📊 THỐNG KÊ TỔNG QUAN:")
print(f"  • Tổng số dòng: {len(df):,}")
print(f"  • Số đơn hàng: {num_orders:,}")
print(f"  • Số khách hàng: {num_customers_actual:,}")
print(f"  • Tỷ lệ khách quay lại: {ty_le_quay_lai:.2f}%")
print(f"  • Doanh thu thuần trung bình: {df['DoanhThuThuan'].mean():,.0f} VNĐ")

# Giới tính
gender_dist = df.groupby('GioiTinh')['KhachHangID'].nunique()
print(f"\n👥 PHÂN BỐ GIỚI TÍNH:")
for gender, count in gender_dist.items():
    pct = (count / num_customers_actual) * 100
    print(f"  • {gender}: {count:,} KH ({pct:.1f}%)")

# Ngày trong tuần
df['NgayMuaDate'] = pd.to_datetime(df['NgayMua'], format='%d/%m/%Y')
df['DayOfWeek'] = df['NgayMuaDate'].dt.dayofweek
day_names = {0: 'T2', 1: 'T3', 2: 'T4', 3: 'T5', 4: 'T6', 5: 'T7', 6: 'CN'}
weekday_dist = df.groupby('DayOfWeek')['MaDonHang'].nunique()
print(f"\n📅 PHÂN BỐ THEO NGÀY TRONG TUẦN:")
for day, count in weekday_dist.items():
    pct = (count / num_orders) * 100
    print(f"  • {day_names[day]}: {count:,} đơn ({pct:.1f}%)")

# Giờ mua hàng
df['ThoiGianMuaDT'] = pd.to_datetime(df['ThoiGianMua'], format='%d/%m/%Y %H:%M')
df['Hour'] = df['ThoiGianMuaDT'].dt.hour
hour_dist = df.groupby('Hour')['MaDonHang'].nunique()
print(f"\n⏰ PHÂN BỐ GIỜ MUA (TOP 5):")
for hour, count in hour_dist.sort_values(ascending=False).head(5).items():
    pct = (count / num_orders) * 100
    print(f"  • {hour}h: {count:,} đơn ({pct:.1f}%)")

# Độ tuổi
df['NgaySinhDate'] = pd.to_datetime(df['NgaySinh'], format='%d/%m/%Y')
df['Age'] = 2024 - df['NgaySinhDate'].dt.year
age_bins = [0, 20, 23, 26, 31, 100]
age_labels = ['<20', '20-22', '23-25', '26-30', '31+']
df['AgeGroup'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels, right=False)
age_dist = df.groupby('AgeGroup')['KhachHangID'].nunique()
print(f"\n🎂 PHÂN BỐ ĐỘ TUỔI:")
for age_group, count in age_dist.items():
    pct = (count / num_customers_actual) * 100
    print(f"  • {age_group} tuổi: {count:,} KH ({pct:.1f}%)")

# Khu vực
location_dist = df.groupby('TinhThanh')['MaDonHang'].nunique().sort_values(ascending=False)
print(f"\n🗺️ PHÂN BỐ THEO KHU VỰC:")
for tinh, count in location_dist.items():
    pct = (count / num_orders) * 100
    print(f"  • {tinh}: {count:,} đơn ({pct:.1f}%)")

# Traffic
traffic_dist = df.groupby('Traffic')['MaDonHang'].nunique().sort_values(ascending=False)
print(f"\n📱 NGUỒN TRUY CẬP:")
for traffic, count in traffic_dist.items():
    pct = (count / num_orders) * 100
    print(f"  • {traffic}: {count:,} đơn ({pct:.1f}%)")

# Sản phẩm
product_dist = df.groupby('TenSanPham')['SoLuong'].sum().sort_values(ascending=False)
print(f"\n🛍️ TOP 5 SẢN PHẨM BÁN CHẠY:")
for i, (product, qty) in enumerate(product_dist.head(5).items(), 1):
    pct = (qty / df['SoLuong'].sum()) * 100
    print(f"  {i}. {product}: {qty:,} sp ({pct:.1f}%)")

# Thương hiệu
brand_dist = df.groupby('NhaSanXuat')['DoanhThu'].sum().sort_values(ascending=False)
print(f"\n🏷️ DOANH THU THEO THƯƠNG HIỆU:")
for brand, revenue in brand_dist.items():
    pct = (revenue / df['DoanhThu'].sum()) * 100
    print(f"  • {brand}: {revenue:,.0f} VNĐ ({pct:.1f}%)")

# SKU
print(f"\n🔖 THỐNG KÊ SKU:")
print(f"  • Số SKU duy nhất: {df['SKU'].nunique()}")
print(f"  • Số sản phẩm duy nhất: {df['TenSanPham'].nunique()}")

# Sản phẩm trên đơn
products_per_order = df.groupby('MaDonHang').size()
print(f"\n📦 SẢN PHẨM TRÊN MỖI ĐƠN:")
for num_products in sorted(products_per_order.unique()):
    count = (products_per_order == num_products).sum()
    pct = (count / num_orders) * 100
    print(f"  • {num_products} SP: {count:,} đơn ({pct:.1f}%)")

# Phân tích RFM
print(f"\n💎 PHÂN TÍCH RFM:")
rfm = df.groupby('KhachHangID').agg({
    'NgayMuaDate': 'max',
    'MaDonHang': 'nunique',
    'DoanhThuThuan': 'sum'
})
rfm['Recency'] = (df['NgayMuaDate'].max() - rfm['NgayMuaDate']).dt.days
rfm['Frequency'] = rfm['MaDonHang']
rfm['Monetary'] = rfm['DoanhThuThuan']

print(f"  • Recency trung bình: {rfm['Recency'].mean():.0f} ngày")
print(f"  • Frequency trung bình: {rfm['Frequency'].mean():.2f} đơn/KH")
print(f"  • Monetary trung bình: {rfm['Monetary'].mean():,.0f} VNĐ/KH")

# Phân khúc khách hàng
order_counts = df.groupby('KhachHangID')['MaDonHang'].nunique()
print(f"\n👥 PHÂN KHÚC KHÁCH HÀNG:")
segments = {
    'Champions (8-15 đơn)': (order_counts >= 8).sum(),
    'Loyal (5-7 đơn)': ((order_counts >= 5) & (order_counts < 8)).sum(),
    'Potential (3-4 đơn)': ((order_counts >= 3) & (order_counts < 5)).sum(),
    'Recent (2 đơn)': (order_counts == 2).sum(),
    'Single (1 đơn)': (order_counts == 1).sum(),
}
for segment_name, count in segments.items():
    pct = (count / num_customers_actual) * 100
    print(f"  • {segment_name}: {count:,} KH ({pct:.1f}%)")

print("\n" + "=" * 70)
print("🎉 Hoàn tất! File: sneaker_sales_data_final.xlsx")
print("=" * 70)