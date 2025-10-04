import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import unidecode

# =========================
# Khởi tạo
# =========================
fake = Faker("vi_VN")
random.seed(42)

TARGET_ROWS = 60000   # số dòng cần sinh
START_DATE = datetime(2023, 1, 1)
END_DATE   = datetime(2024, 12, 30)

# Nguồn traffic
traffic_sources = ["Direct", "Referral", "Facebook", "Google", "Tiktok"]

# Sản phẩm giày sneaker
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

# Phiên bản
versions = ["Classic", "Limited", "2023 Edition", "Premium", "Street Style"]

# Phương thức thanh toán
payment_methods = ["COD", "Chuyển khoản", "Ví điện tử", "Thẻ tín dụng"]

# Địa chỉ Việt Nam
locations = {
    "Hà Nội": ["Ba Đình", "Hoàn Kiếm", "Cầu Giấy", "Thanh Xuân", "Đống Đa"],
    "TP HCM": ["Quận 1", "Quận 3", "Bình Thạnh", "Phú Nhuận", "Thủ Đức"],
    "Đà Nẵng": ["Hải Châu", "Thanh Khê", "Sơn Trà", "Ngũ Hành Sơn"],
    "Hải Phòng": ["Lê Chân", "Ngô Quyền", "Hồng Bàng"],
    "Cần Thơ": ["Ninh Kiều", "Bình Thủy", "Cái Răng"],
}

# =========================
# Sinh dữ liệu
# =========================
data = []
sku_dict = {}  # Map (TenSanPham, NSX, PhienBan) -> SKU duy nhất
sku_counter = 1000
order_id_counter = 200000
customer_id_counter = 1

while len(data) < TARGET_ROWS:
    # Tạo khách hàng mới
    name = fake.name()
    email = unidecode.unidecode(name).replace(" ", ".").lower() + "@gmail.com"
    gender = random.choice(["Nam", "Nữ"])
    birthday = fake.date_between(datetime(1992,1,1), datetime(2008,12,31))
    sdt = "0" + str(random.randint(900000000, 999999999))  # 1 SDT duy nhất cho KH

    khachhang_id = customer_id_counter
    customer_id_counter += 1

    # Mỗi khách hàng có 1–10 đơn hàng
    num_orders = random.randint(1, 10)
    for j in range(num_orders):
        order_id_counter += 1
        ma_don = order_id_counter

        # Ngày mua
        delta = END_DATE - START_DATE
        ngay_mua = START_DATE + timedelta(days=random.randint(0, delta.days))
        ngay_mua_str = ngay_mua.strftime("%d/%m/%Y")

        # Traffic + Địa chỉ (cho phép KH có nhiều địa chỉ)
        traffic = random.choice(traffic_sources)
        tinh = random.choice(list(locations.keys()))
        quan = random.choice(locations[tinh])

        # Mỗi đơn có 1–3 sản phẩm
        num_products = random.randint(1, 3)
        for k in range(num_products):
            ten_sp, nhom_sp, nsx = random.choice(sneaker_products)
            phien_ban = random.choice(versions)

            # Nếu sản phẩm này chưa có SKU thì tạo mới
            key = (ten_sp, nsx, phien_ban)
            if key not in sku_dict:
                sku_counter += 1
                sku_dict[key] = sku_counter
            sku = sku_dict[key]

            soluong = random.randint(1, 3)
            gia = random.randint(800000, 5000000)
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
# Xuất DataFrame
# =========================
columns = [
    "KhachHangID", "HoTen", "Email", "SDT", "GioiTinh", "NgaySinh",
    "MaDonHang", "NgayMua", "Traffic", "TinhThanh", "QuanHuyen",
    "TenSanPham", "TenNhomSanPham", "SKU", "PhienBan", "NhaSanXuat",
    "PhuongThucTT", "SoLuong", "GiaSP", "DoanhThu", "TienKhuyenMai",
    "VanChuyen", "DoanhThuThuan"
]

df = pd.DataFrame(data, columns=columns)

# Xuất ra file
df.to_csv("sneaker_sales_2023_2024.csv", index=False, encoding="utf-8-sig")
df.to_excel("sneaker_sales_2023_2024.xlsx", index=False)

# =========================
# Thống kê
# =========================
num_customers = df["KhachHangID"].nunique()
num_products_sku = df["SKU"].nunique()
num_products_full = df[["TenSanPham", "NhaSanXuat", "PhienBan"]].drop_duplicates().shape[0]

print("✅ Sinh dữ liệu thành công:", len(df), "dòng")
print(f"👤 Số khách hàng duy nhất: {num_customers}")
print(f"👟 Số sản phẩm duy nhất (SKU): {num_products_sku}")
print(f"📦 Số sản phẩm duy nhất (Tên + NSX + Phiên bản): {num_products_full}")
print(df.head(10))
