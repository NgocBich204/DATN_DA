import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import unidecode

# =========================
# ⚙️ KHỞI TẠO
# =========================
fake = Faker("vi_VN")
random.seed(42)

TARGET_ROWS = 60000
START_DATE = datetime(2023, 1, 1)
END_DATE   = datetime(2024, 12, 30)
repeat_rate = 0.55

traffic_sources = ["Direct", "Referral", "Facebook", "Google", "Tiktok"]
payment_methods = ["COD", "Chuyển khoản", "Ví điện tử", "Thẻ tín dụng"]

# =========================
# 🧩 DANH MỤC SẢN PHẨM
# =========================
sneaker_products = [
    ("Air Force 1", "Lifestyle", "Nike"),
    ("Air Jordan 1", "Basketball", "Nike"),
    ("Yeezy Boost 350", "Lifestyle", "Adidas"),
    ("Ultraboost 22", "Running", "Adidas"),
    ("Chuck Taylor All Star", "Classic", "Converse"),
    ("RS-X", "Lifestyle", "Puma"),
    ("574 Core", "Lifestyle", "New Balance"),
    ("FuelCell Rebel", "Running", "New Balance"),
    ("KD15", "Basketball", "Nike"),
    ("Dame 8", "Basketball", "Adidas"),
]
versions = ["Classic", "Limited", "2023 Edition", "Premium", "Street Style"]

# =========================
# 🗺️ ĐỊA CHỈ VIỆT NAM
# =========================
locations = {
    "Hà Nội": ["Ba Đình", "Hoàn Kiếm", "Cầu Giấy", "Thanh Xuân", "Đống Đa"],
    "TP HCM": ["Quận 1", "Quận 3", "Bình Thạnh", "Phú Nhuận", "Thủ Đức"],
    "Đà Nẵng": ["Hải Châu", "Thanh Khê", "Sơn Trà", "Ngũ Hành Sơn"],
    "Hải Phòng": ["Lê Chân", "Ngô Quyền", "Hồng Bàng"],
    "Cần Thơ": ["Ninh Kiều", "Bình Thủy", "Cái Răng"],
}

# =========================
# 👥 TẠO TÊN KHÁCH HÀNG KHÔNG TRÙNG
# =========================
ho_list = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ",
    "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Tạ", "Trương", "Mai", "Đoàn"
]
dem_list = [
    "Văn", "Thị", "Ngọc", "Minh", "Thanh", "Anh", "Thu", "Phúc", "Hải", "Hồng",
    "Quốc", "Tuấn", "Mạnh", "Diệu", "Bảo", "Thùy", "Trung", "Thiện", "Khánh", "Đình"
]
ten_list = [
    "Nam", "Hoa", "Tâm", "Dũng", "Hà", "Trang", "Hương", "Tuấn", "Quân", "Lan",
    "Phương", "Huy", "Linh", "Sơn", "Giang", "Đạt", "Ngân", "Trí", "Vy", "Tú",
    "Đức", "Hạnh", "Phúc", "Tài", "Thảo", "Yến", "Long", "Nhung", "Châu", "Khang"
]

unique_names = set()
while len(unique_names) < 10000:
    name = f"{random.choice(ho_list)} {random.choice(dem_list)} {random.choice(ten_list)}"
    unique_names.add(name)
unique_names = list(unique_names)

# =========================
# KHỞI TẠO DANH SÁCH KHÁCH HÀNG
# =========================
num_customers = 10000
num_repeat = int(num_customers * repeat_rate)
num_one_time = num_customers - num_repeat
customer_types = (["repeat"] * num_repeat) + (["single"] * num_one_time)
random.shuffle(customer_types)

# =========================
# SINH DỮ LIỆU (MỖI ĐƠN = 1 DÒNG)
# =========================
data = []
sku_dict = {}
sku_counter = 1000
order_id_counter = 200000
customer_id_counter = 1

for i, customer_type in enumerate(customer_types):
    name = unique_names[i]
    email = unidecode.unidecode(name).replace(" ", ".").lower() + "@gmail.com"
    gender = "Nam" if any(x in name for x in ["Văn", "Tuấn", "Quân", "Huy", "Đức", "Long", "Trí"]) else "Nữ"
    birthday = fake.date_between(datetime(1996,1,1), datetime(2008,12,31))
    sdt = "0" + str(random.randint(900000000, 999999999))
    khachhang_id = customer_id_counter
    customer_id_counter += 1

    # Số đơn hàng mỗi khách
    if customer_type == "single":
        num_orders = 1
    else:
        num_orders = random.choices(
            [2, 3, 4, 5, 6, 7, 8, 9, 10],
            weights=[25, 20, 15, 12, 10, 8, 5, 3, 2]
        )[0]

    for j in range(num_orders):
        order_id_counter += 1
        ma_don = order_id_counter

        delta = END_DATE - START_DATE
        ngay_mua = START_DATE + timedelta(days=random.randint(0, delta.days))
        ngay_mua_str = ngay_mua.strftime("%d/%m/%Y")

        traffic = random.choice(traffic_sources)
        tinh = random.choice(list(locations.keys()))
        quan = random.choice(locations[tinh])

        # Chọn ngẫu nhiên 1 sản phẩm duy nhất cho đơn hàng
        ten_sp, nhom_sp, nsx = random.choice(sneaker_products)
        phien_ban = random.choice(versions)
        key = (ten_sp, nsx, phien_ban)
        if key not in sku_dict:
            sku_counter += 1
            sku_dict[key] = sku_counter
        sku = sku_dict[key]

        # Sinh giá trị bán
        gia = random.choice([800000, 1200000, 1800000, 2500000, 3000000, 4000000, 5000000])
        soluong = random.choices([1, 2, 3, 4, 5], weights=[40, 25, 15, 10, 10])[0]
        if random.random() < 0.1:
            gia *= random.choice([1.5, 2, 2.5])

        doanh_thu = gia * soluong
        khuyenmai = int(doanh_thu * random.uniform(0, 0.3))
        van_chuyen = random.choice([0, 15000, 20000, 30000, 40000])
        doanh_thu_thuan = doanh_thu - khuyenmai - van_chuyen
        pttt = random.choice(payment_methods)

        data.append([
            khachhang_id, name, email, sdt, gender, birthday.strftime("%d/%m/%Y"),
            ma_don, ngay_mua_str, traffic, tinh, quan,
            ten_sp, nhom_sp, sku, phien_ban, nsx,
            pttt, soluong, gia, doanh_thu, khuyenmai, van_chuyen, doanh_thu_thuan
        ])

        if len(data) >= TARGET_ROWS:
            break
    if len(data) >= TARGET_ROWS:
        break

# =========================
# 📦 XUẤT DỮ LIỆU
# =========================
columns = [
    "KhachHangID", "HoTen", "Email", "SDT", "GioiTinh", "NgaySinh",
    "MaDonHang", "NgayMua", "Traffic", "TinhThanh", "QuanHuyen",
    "TenSanPham", "TenNhomSanPham", "SKU", "PhienBan", "NhaSanXuat",
    "PhuongThucTT", "SoLuong", "GiaSP", "DoanhThu", "TienKhuyenMai",
    "VanChuyen", "DoanhThuThuan"
]

df = pd.DataFrame(data, columns=columns)
df["KhachHangID"] = df["KhachHangID"].astype(str)
df.to_excel("sneaker_sales_fact_donhang.xlsx", index=False)

# =========================
# 🧾 THỐNG KÊ
# =========================
num_customers = df["KhachHangID"].nunique()
num_orders = df["MaDonHang"].nunique()
num_names = df["HoTen"].nunique()
repeat_customers = df.groupby("KhachHangID")["MaDonHang"].nunique()
ty_le_quay_lai = (repeat_customers[repeat_customers > 1].count() / num_customers) * 100
dup_orders = df.duplicated(subset=["MaDonHang"]).sum()

print(f"✅ Sinh dữ liệu thành công: {len(df)} dòng")
print(f"📦 Số đơn hàng duy nhất: {num_orders}")
print(f"👤 Số khách hàng duy nhất: {num_customers}")
print(f"🧍‍♂️ Số tên khách hàng duy nhất: {num_names}")
print(f"🔁 Tỷ lệ khách hàng quay lại: {ty_le_quay_lai:.2f}%")
print(f"🛡️ Dòng trùng mã đơn: {dup_orders}")
