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

# Tham số
NUM_CUSTOMERS = 5000
START_DATE = datetime(2023, 1, 1)
END_DATE   = datetime(2024, 12, 30)

# Nguồn traffic
traffic_sources = ["Direct", "Referral", "Facebook", "Google", "Tiktok"]

# Sản phẩm & nhóm
products = [
    ("Son môi lì", "Makeup", "MAC"),
    ("Kem nền che khuyết điểm", "Face", "Maybelline"),
    ("Sữa rửa mặt dịu nhẹ", "Skincare", "Innisfree"),
    ("Tẩy trang Micellar", "Tẩy trang", "L’Oréal"),
    ("Phấn phủ kiềm dầu", "Face", "Maybelline"),
    ("Mascara cong dài", "Makeup", "L’Oréal"),
    ("Serum dưỡng ẩm", "Skincare", "Laneige"),
    ("Kem chống nắng SPF50", "Skincare", "Anessa"),
    ("Nước hoa hồng cân bằng", "Skincare", "Hada Labo"),
    ("Dầu gội phục hồi", "Haircare", "Pantene")
]

# Phiên bản ngẫu nhiên
versions = [
    "Default Title",
    "02 Tông Trung Bình",
    "Nâng tông giảm thâm",
    "Dưỡng ẩm ban đêm",
    "Dưỡng trắng sáng da"
]

# Phương thức thanh toán
payment_methods = [
    "Thanh toán khi giao hàng (COD)",
    "Chuyển khoản ngân hàng",
    "Ví điện tử Momo/Zalopay",
    "Thẻ tín dụng/ghi nợ"
]

# Địa chỉ chuẩn (Tỉnh + Quận)
locations = {
    "Hà Nội": ["Ba Đình", "Hoàn Kiếm", "Đống Đa", "Cầu Giấy", "Thanh Xuân", "Tây Hồ", "Long Biên"],
    "TP HCM": ["Quận 1", "Quận 3", "Quận 5", "Bình Thạnh", "Phú Nhuận", "Tân Bình", "Thủ Đức"],
    "Đà Nẵng": ["Hải Châu", "Thanh Khê", "Sơn Trà", "Ngũ Hành Sơn", "Liên Chiểu"],
    "Hải Phòng": ["Lê Chân", "Ngô Quyền", "Hồng Bàng", "Kiến An"],
    "Cần Thơ": ["Ninh Kiều", "Bình Thủy", "Cái Răng", "Ô Môn"],
    "Quảng Ninh": ["Hạ Long", "Cẩm Phả", "Uông Bí", "Móng Cái"],
    "Bắc Ninh": ["TP Bắc Ninh", "Từ Sơn", "Yên Phong", "Tiên Du"],
    "Thanh Hóa": ["TP Thanh Hóa", "Sầm Sơn", "Bỉm Sơn", "Nghi Sơn"],
    "Nghệ An": ["TP Vinh", "Cửa Lò", "Hoàng Mai", "Quỳnh Lưu"],
    "Huế": ["TP Huế", "Hương Thủy", "Hương Trà", "Phong Điền"],
    "Khánh Hòa": ["Nha Trang", "Cam Ranh", "Ninh Hòa"],
    "Bình Dương": ["Thủ Dầu Một", "Thuận An", "Dĩ An", "Bến Cát"],
    "Đồng Nai": ["Biên Hòa", "Long Khánh", "Nhơn Trạch", "Trảng Bom"],
    "Vũng Tàu": ["TP Vũng Tàu", "Bà Rịa", "Long Điền", "Xuyên Mộc"],
    "Kiên Giang": ["Rạch Giá", "Hà Tiên", "Phú Quốc"],
    "An Giang": ["Long Xuyên", "Châu Đốc", "Tân Châu"],
    "Lâm Đồng": ["Đà Lạt", "Bảo Lộc", "Di Linh"],
    "Quảng Nam": ["Tam Kỳ", "Hội An", "Điện Bàn"],
    "Thái Nguyên": ["TP Thái Nguyên", "Sông Công", "Phổ Yên"],
    "Hà Nam": ["Phủ Lý", "Duy Tiên", "Kim Bảng"]
}

# =========================
# Sinh dữ liệu khách hàng
# =========================
customers = []
for i in range(NUM_CUSTOMERS):
    name = fake.name()
    email = unidecode.unidecode(name).replace(" ", ".").lower() + "@gmail.com"
    customers.append({
        "HoTen": name,
        "Email": email
    })

# =========================
# Sinh dữ liệu giao dịch
# =========================
data = []
sku_counter = 100000
order_id_counter = 200000

for cust in customers:
    # Số đơn hàng mỗi khách (nhiều khách mua ít, ít khách mua nhiều)
    num_orders = random.choices([1,2,3,4,5,10,15,20], weights=[40,25,15,10,5,3,1,1])[0]

    for j in range(num_orders):
        order_id_counter += 1
        ma_don = order_id_counter

        # Ngày mua
        delta = END_DATE - START_DATE
        ngay_mua = START_DATE + timedelta(days=random.randint(0, delta.days))
        ngay_mua_str = ngay_mua.strftime("%d/%m/%Y")

        # Traffic + Địa chỉ
        traffic = random.choice(traffic_sources)
        tinh = random.choice(list(locations.keys()))
        quan = random.choice(locations[tinh])

        # Mỗi đơn có thể gồm nhiều sản phẩm
        num_products = random.randint(1, 3)
        for k in range(num_products):
            ten_sp, nhom_sp, nsx = random.choice(products)
            sku_counter += 1
            sku = sku_counter
            phien_ban = random.choice(versions)

            soluong = random.randint(1, 5)
            gia = random.randint(10000, 2000000)
            doanh_thu = gia * soluong
            khuyenmai = int(doanh_thu * random.uniform(0, 0.1))
            van_chuyen = random.choice([0, 15000, 20000, 30000])
            doanh_thu_thuan = doanh_thu - khuyenmai - van_chuyen
            pttt = random.choice(payment_methods)

            data.append([
                cust["KhachHangID"], cust["HoTen"], cust["Email"], ngay_mua_str, traffic,
                tinh, quan, ma_don, ten_sp, nhom_sp, nsx, sku, phien_ban, pttt,
                doanh_thu, khuyenmai, doanh_thu_thuan, soluong, van_chuyen
            ])

# =========================
# Xuất DataFrame
# =========================
columns = [
     "HoTen", "Email", "NgayMua", "Traffic", "TinhThanh", "QuanHuyen", "MaDonHang",
    "TenSanPham", "TenNhomSanPham", "NhaSanXuat", "SKU", "PhienBan", "PhuongThucTT",
    "DoanhThu", "TienKhuyenMai", "DoanhThuThuan", "SoLuong", "VanChuyen"
]

df = pd.DataFrame(data, columns=columns)

# Xuất ra file
df.to_csv("ecommerce_data.csv", index=False, encoding="utf-8-sig")
df.to_excel("ecommerce_data.xlsx", index=False)

print("✅ Sinh dữ liệu thành công:", len(df), "dòng")

