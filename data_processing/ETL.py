import pandas as pd
import pyodbc
import os
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np

# --- Cấu hình kết nối SQL Server ---
odbc_driver = "ODBC Driver 17 for SQL Server"
server = "localhost\\SQLEXPRESS"
database = "test6"
auth = "windows"
encrypt = "yes"
trust_server_certificate = "yes"

conn_str = (
    f"Driver={{{odbc_driver}}};"
    f"Server={server};"
    f"Database={database};"
    "Trusted_Connection=yes;"
    f"Encrypt={encrypt};"
    f"TrustServerCertificate={trust_server_certificate};"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# --- Đường dẫn và cấu hình ---
raw_folder = r"C:\Users\ngoc bich\Desktop\DATN_DA\raw_data"
file_name = "sneaker_sales_data (1).xlsx"
file_path = os.path.join(raw_folder, file_name)

# --- Đọc dữ liệu từ file Excel ---
df = pd.read_excel(file_path)

# --- Làm sạch dữ liệu ---
df = df.loc[:, ~df.columns.str.contains("Unnamed")]
df = df.dropna(how='all')
df.columns = df.columns.str.strip()

df['NgaySinh'] = pd.to_datetime(df['NgaySinh'], errors='coerce', dayfirst=True)
df['NgayMua'] = pd.to_datetime(df['NgayMua'], errors='coerce', dayfirst=True)

df["Gio"] = df["NgayMua"].dt.hour.fillna(0).astype(int)

df = df.dropna(subset=['NgaySinh', 'NgayMua'])

required_columns = ['HoTen', 'Email', 'SDT', 'SKU', 'DonHang', 'SoLuong', 'DoanhThu']
df = df.dropna(subset=required_columns)

df['SoLuong'] = pd.to_numeric(df['SoLuong'], errors='coerce')
df['DoanhThu'] = pd.to_numeric(df['DoanhThu'], errors='coerce')
df['TienKhuyenMai'] = pd.to_numeric(df['TienKhuyenMai'], errors='coerce').fillna(0)
df['VanChuyen'] = pd.to_numeric(df['VanChuyen'], errors='coerce').fillna(0)
df['DoanhThuThuan'] = pd.to_numeric(df['DoanhThuThuan'], errors='coerce')
df = df.dropna(subset=['SoLuong', 'DoanhThu', 'DoanhThuThuan'])

print(f"Số dòng còn lại sau khi làm sạch: {len(df)}")

# --- Tạo bảng StagingSaleData ---
cursor.execute("""
IF OBJECT_ID('dbo.StagingSaleData', 'U') IS NOT NULL DROP TABLE dbo.StagingSaleData;
CREATE TABLE dbo.StagingSaleData (
    HoTen NVARCHAR(255),
    Email NVARCHAR(255),
    SDT VARCHAR(20),
    GioiTinh NVARCHAR(10),
    NgaySinh DATE,
    DonHang NVARCHAR(50),
    NgayMua DATETIME,
    Traffic NVARCHAR(100),
    TinhThanh NVARCHAR(100),
    QuanHuyen NVARCHAR(100),
    TenSanPham NVARCHAR(255),
    TenNhomSanPham NVARCHAR(100),
    SKU NVARCHAR(50),
    PhienBan NVARCHAR(100),
    NhaSanXuat NVARCHAR(100),
    PhuongThucTT NVARCHAR(100),
    SoLuong INT,
    DoanhThu FLOAT,
    TienKhuyenMai FLOAT,
    VanChuyen FLOAT,
    DoanhThuThuan FLOAT
)
""")
conn.commit()

# --- Ghi dữ liệu sạch vào StagingSaleData (GIỮ CẢ GIỜ) ---
for idx, row in df.iterrows():
    cursor.execute("""
    INSERT INTO dbo.StagingSaleData (
        HoTen, Email, SDT, GioiTinh, NgaySinh, DonHang, NgayMua, Traffic,
        TinhThanh, QuanHuyen, TenSanPham, TenNhomSanPham, SKU, PhienBan,
        NhaSanXuat, PhuongThucTT, SoLuong, DoanhThu, TienKhuyenMai,
        VanChuyen, DoanhThuThuan
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    row.HoTen, row.Email, row.SDT, row.GioiTinh, row.NgaySinh.date(),
    row.DonHang, row.NgayMua, row.Traffic, row.TinhThanh, row.QuanHuyen,
    row.TenSanPham, row.TenNhomSanPham, row.SKU, row.PhienBan,
    row.NhaSanXuat, row.PhuongThucTT, int(row.SoLuong), float(row.DoanhThu),
    float(row.TienKhuyenMai), float(row.VanChuyen), float(row.DoanhThuThuan)
    )
conn.commit()

# --- Tạo bảng Dimension & Fact ---
cursor.execute("""
IF OBJECT_ID('dbo.DimKhachHang', 'U') IS NOT NULL DROP TABLE dbo.DimKhachHang;
CREATE TABLE dbo.DimKhachHang (
    KhachHangID INT IDENTITY(1,1) PRIMARY KEY,
    HoTen NVARCHAR(255),
    Email NVARCHAR(255),
    SDT VARCHAR(20),
    GioiTinh NVARCHAR(10),
    NgaySinh DATE,
    TinhThanh NVARCHAR(100),
    QuanHuyen NVARCHAR(100),
    Traffic NVARCHAR(100)
);

IF OBJECT_ID('dbo.DimNhomSP', 'U') IS NOT NULL DROP TABLE dbo.DimNhomSP;
CREATE TABLE dbo.DimNhomSP (
    NhomSPID INT IDENTITY(1,1) PRIMARY KEY,
    TenNhomSanPham NVARCHAR(100) UNIQUE
);

IF OBJECT_ID('dbo.DimSP', 'U') IS NOT NULL DROP TABLE dbo.DimSP;
CREATE TABLE dbo.DimSP (
    SPID INT IDENTITY(1,1) PRIMARY KEY,
    SKU NVARCHAR(50) UNIQUE,
    TenSanPham NVARCHAR(255),
    NhaSanXuat NVARCHAR(100),
    PhienBan NVARCHAR(100)
);

-- DimDate GIỮ CẢ NGÀY + GIỜ
IF OBJECT_ID('dbo.DimDate', 'U') IS NOT NULL DROP TABLE dbo.DimDate;
CREATE TABLE dbo.DimDate (
    DateID INT IDENTITY(1,1) PRIMARY KEY,
    NgayMua DATETIME,
    Thang INT,
    Quy INT,
    Nam INT
);

IF OBJECT_ID('dbo.FactDonHang', 'U') IS NOT NULL DROP TABLE dbo.FactDonHang;
CREATE TABLE dbo.FactDonHang (
    DonHang NVARCHAR(50),
    KhachHangID INT,
    SPID INT,
    NhomSPID INT,
    DateID INT,
    SoLuong INT,
    DoanhThu FLOAT,
    TienKhuyenMai FLOAT,
    DoanhThuThuan FLOAT,
    VanChuyen FLOAT,
    PRIMARY KEY (DonHang, SPID),
    FOREIGN KEY (KhachHangID) REFERENCES dbo.DimKhachHang(KhachHangID),
    FOREIGN KEY (SPID) REFERENCES dbo.DimSP(SPID),
    FOREIGN KEY (NhomSPID) REFERENCES dbo.DimNhomSP(NhomSPID),
    FOREIGN KEY (DateID) REFERENCES dbo.DimDate(DateID)
);
""")
conn.commit()

# --- Insert dữ liệu vào các bảng dim ---
cursor.execute("""
INSERT INTO dbo.DimKhachHang (HoTen, Email, SDT, GioiTinh, NgaySinh, TinhThanh, QuanHuyen, Traffic)
SELECT HoTen, Email, SDT, GioiTinh, NgaySinh, TinhThanh, QuanHuyen, Traffic FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY Email ORDER BY NgayMua DESC) as rn 
    FROM dbo.StagingSaleData
) sub WHERE rn = 1 AND Email IS NOT NULL
""")
conn.commit()

cursor.execute("""
INSERT INTO dbo.DimNhomSP (TenNhomSanPham)
SELECT DISTINCT TenNhomSanPham FROM dbo.StagingSaleData s
WHERE TenNhomSanPham IS NOT NULL
AND NOT EXISTS (SELECT 1 FROM dbo.DimNhomSP d WHERE d.TenNhomSanPham = s.TenNhomSanPham)
""")
conn.commit()

cursor.execute("""
INSERT INTO dbo.DimSP (SKU, TenSanPham, NhaSanXuat, PhienBan)
SELECT SKU, MIN(TenSanPham), MIN(NhaSanXuat), MIN(PhienBan) 
FROM dbo.StagingSaleData
WHERE SKU IS NOT NULL
GROUP BY SKU
HAVING NOT EXISTS (SELECT 1 FROM dbo.DimSP WHERE SKU = dbo.StagingSaleData.SKU)
""")
conn.commit()

# --- DimDate: giữ nguyên cả ngày + giờ ---
cursor.execute("""
INSERT INTO dbo.DimDate (NgayMua, Thang, Quy, Nam)
SELECT DISTINCT 
    NgayMua,
    MONTH(NgayMua),
    DATEPART(QUARTER, NgayMua),
    YEAR(NgayMua)
FROM dbo.StagingSaleData s
WHERE NgayMua IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM dbo.DimDate d 
    WHERE d.NgayMua = s.NgayMua
)
""")
conn.commit()

# --- MERGE FactDonHang ---
cursor.execute("""
MERGE dbo.FactDonHang AS target
USING (
    SELECT sa.DonHang, kh.KhachHangID, sp.SPID, ns.NhomSPID, d.DateID,
           sa.SoLuong, sa.DoanhThu, sa.TienKhuyenMai, sa.DoanhThuThuan, sa.VanChuyen,
           ROW_NUMBER() OVER (PARTITION BY sa.DonHang, sp.SPID ORDER BY d.DateID DESC) as rn
    FROM dbo.StagingSaleData sa
    JOIN dbo.DimKhachHang kh ON sa.Email = kh.Email
    JOIN dbo.DimSP sp ON sa.SKU = sp.SKU
    JOIN dbo.DimNhomSP ns ON sa.TenNhomSanPham = ns.TenNhomSanPham
    JOIN dbo.DimDate d ON sa.NgayMua = d.NgayMua
) src
ON target.DonHang = src.DonHang AND target.SPID = src.SPID
WHEN MATCHED AND src.rn = 1 THEN 
    UPDATE SET SoLuong = src.SoLuong,
               DoanhThu = src.DoanhThu,
               TienKhuyenMai = src.TienKhuyenMai,
               DoanhThuThuan = src.DoanhThuThuan,
               VanChuyen = src.VanChuyen
WHEN NOT MATCHED AND src.rn = 1 THEN
    INSERT (DonHang, KhachHangID, SPID, NhomSPID, DateID, SoLuong, DoanhThu, 
            TienKhuyenMai, DoanhThuThuan, VanChuyen)
    VALUES (src.DonHang, src.KhachHangID, src.SPID, src.NhomSPID, src.DateID, 
            src.SoLuong, src.DoanhThu, src.TienKhuyenMai, src.DoanhThuThuan, src.VanChuyen);
""")
conn.commit()

print("✅ Dữ liệu đã được lưu vào SQL Server (NgayMua có cả ngày + giờ).")


print("ETL cơ bản hoàn thành, tiến hành phân tích RFM ...")

# --- Bước 1-2: Lấy dữ liệu cho phân tích aRFM từ DB ---
query = """
SELECT
    f.KhachHangID,
    f.DonHang,
    d.NgayMua as Ngay, 
    f.DoanhThuThuan
FROM dbo.FactDonHang f
JOIN dbo.DimDate d ON f.DateID = d.DateID
"""
df_rfm = pd.read_sql(query, conn)

# Xử lý dữ liệu ngày
df_rfm["Ngay"] = pd.to_datetime(df_rfm["Ngay"], errors="coerce").fillna(pd.Timestamp("2021-04-04"))

# --- Bước 3: Tính RFM ---
ngay_tham_chieu = df_rfm["Ngay"].max() + pd.Timedelta(days=1)
print(f"📅 Ngày tham chiếu: {ngay_tham_chieu}")

df_rfm_grouped = df_rfm.groupby("KhachHangID").agg(
    NgayMuaGanNhat=("Ngay", "max"),
    SoLanMua=("DonHang", "nunique"),
    TongTien=("DoanhThuThuan", "sum")
).reset_index()

df_rfm_grouped["Recency"] = (ngay_tham_chieu - df_rfm_grouped["NgayMuaGanNhat"]).dt.days
df_rfm_grouped["Frequency"] = df_rfm_grouped["SoLanMua"]
df_rfm_grouped["Monetary"] = df_rfm_grouped["TongTien"]

df_rfm_final = df_rfm_grouped[["KhachHangID", "Recency", "Frequency", "Monetary"]].copy()
# --------------------------------------------------------------
# --- Bước 4: Lưu RFM vào database ---
cursor.execute("""
IF OBJECT_ID('RFM_KhachHang', 'U') IS NULL
BEGIN
    CREATE TABLE RFM_KhachHang (
        KhachHangID INT PRIMARY KEY,
        Recency INT,
        Frequency FLOAT,
        Monetary FLOAT
    );
END
""")
conn.commit()

for _, row in df_rfm_final.iterrows():
    cursor.execute("""
        MERGE RFM_KhachHang AS target
        USING (SELECT ? AS KhachHangID, ? AS Recency, ? AS Frequency, ? AS Monetary) AS source
        ON target.KhachHangID = source.KhachHangID
        WHEN MATCHED THEN
            UPDATE SET Recency = source.Recency,
                       Frequency = source.Frequency,
                       Monetary = source.Monetary
        WHEN NOT MATCHED THEN
            INSERT (KhachHangID, Recency, Frequency, Monetary)
            VALUES (source.KhachHangID, source.Recency, source.Frequency, source.Monetary);
    """, row.KhachHangID, int(row.Recency), float(row.Frequency), float(row.Monetary))
conn.commit()
print("✅ Đã cập nhật bảng RFM_KhachHang!")

# ----------------------------------------------------------------------------------------
# --- Bước 5: Chuẩn hóa dữ liệu ---
X = df_rfm_final[["Recency", "Frequency", "Monetary"]]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# --- Bước 6: Tìm số cụm tối ưu ---
sse = []
sil_scores = []
K_range = range(2, 10)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    sse.append(kmeans.inertia_)
    sil_scores.append(silhouette_score(X_scaled, kmeans.labels_))

# Vẽ biểu đồ Elbow và Silhouette
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.plot(K_range, sse, marker="o")
plt.xlabel("Số cụm K")
plt.ylabel("SSE")
plt.title("Elbow Method")

plt.subplot(1, 2, 2)
plt.plot(K_range, sil_scores, marker="o", color="orange")
plt.xlabel("Số cụm K")
plt.ylabel("Silhouette Score")
plt.title("Silhouette Score")
plt.tight_layout()
plt.show()

print("\n📊 Silhouette Score cho từng K:")
for k, score in zip(K_range, sil_scores):
    print(f"K={k}, Silhouette Score={score:.3f}")

# --- Tự động tìm điểm khuỷu tay bằng phương pháp Knee ---
def tim_diem_khuyu_tay_kneedle(K_range, sse):
    # Chuẩn hóa dữ liệu
    k_norm = (np.array(K_range) - min(K_range)) / (max(K_range) - min(K_range))
    sse_norm = (np.array(sse) - min(sse)) / (max(sse) - min(sse))
    
    x1, y1 = k_norm[0], sse_norm[0]
    x2, y2 = k_norm[-1], sse_norm[-1]
    khoang_cach = []
    for i in range(len(k_norm)):
        x0, y0 = k_norm[i], sse_norm[i]
        d = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1) / np.sqrt((y2-y1)**2 + (x2-x1)**2)
        khoang_cach.append(d)
    elbow_idx = np.argmax(khoang_cach)
    return K_range[elbow_idx], khoang_cach


optimal_k, distances = tim_diem_khuyu_tay_kneedle(K_range, sse)

print("\n" + "="*60)
print("🔍 TÌM K TỐI ƯU - PHƯƠNG PHÁP KNEEDLE (ELBOW)")
print("="*60)
print(f"✅ K tối ưu được phát hiện: {optimal_k}")
print(f"📊 Khoảng cách các điểm đến đường thẳng:")
for k, dist in zip(K_range, distances):
    marker = " ← ĐIỂM KHUỶU TAY" if k == optimal_k else ""
    print(f"   K={k}: {dist:.4f}{marker}")
print("="*60)


plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.plot(K_range, sse, marker="o", linewidth=2, markersize=8)
plt.plot([K_range[0], K_range[-1]], [sse[0], sse[-1]], 'r--', linewidth=1, alpha=0.5, label='Đường thẳng tham chiếu')
plt.scatter([optimal_k], [sse[list(K_range).index(optimal_k)]], 
            color='red', s=300, zorder=5, marker='*', 
            label=f'Điểm khuỷu tay: K={optimal_k}', edgecolors='black', linewidths=2)
plt.xlabel("Số cụm K", fontsize=12)
plt.ylabel("SSE (Sum of Squared Errors)", fontsize=12)
plt.title("Elbow Method - Phương pháp Kneedle", fontsize=14, fontweight='bold')
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.bar(K_range, distances, color='skyblue', edgecolor='black')
plt.bar([optimal_k], [distances[list(K_range).index(optimal_k)]], 
        color='red', edgecolor='black', label=f'K tối ưu = {optimal_k}')
plt.xlabel("Số cụm K", fontsize=12)
plt.ylabel("Khoảng cách đến đường thẳng", fontsize=12)
plt.title("Khoảng cách từ các điểm đến đường thẳng", fontsize=14, fontweight='bold')
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.show()

print(f"\n✅ HỆ THỐNG TỰ ĐỘNG CHỌN K = {optimal_k}")
print(f"   💡 Nếu muốn thay đổi, hãy bỏ comment dòng bên dưới và chọn K thủ công")

# optimal_k = 4  # Bỏ comment dòng này nếu muốn tự chọn

# --- Bước 7: Chạy K-Means với K đã chọn ---
kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df_rfm_final["Cluster"] = kmeans.fit_predict(X_scaled)

print(f"\n📊 Đã phân thành {optimal_k} cụm")
print(df_rfm_final.head(10))
# ------------------------------------------------------------------
# --- Bước 8: Tự động gán tên phân khúc ---
cluster_summary = df_rfm_final.groupby("Cluster")[["Recency", "Frequency", "Monetary"]].mean()

r_max = cluster_summary['Recency'].max()
f_max = cluster_summary['Frequency'].max()
m_max = cluster_summary['Monetary'].max()

cluster_summary['R_Score'] = 1 - (cluster_summary['Recency'] / r_max)
cluster_summary['F_Score'] = cluster_summary['Frequency'] / f_max
cluster_summary['M_Score'] = cluster_summary['Monetary'] / m_max

cluster_summary['RFM_Score'] = (cluster_summary['R_Score'] + cluster_summary['F_Score'] + cluster_summary['M_Score']) / 3

cluster_ranking = cluster_summary.sort_values('RFM_Score', ascending=False)

def tu_dong_gan_phan_khuc(optimal_k, cluster_ranking):
    if optimal_k == 2:
        ten_phan_khuc = ["Khách hàng tốt", "Khách hàng yếu"]
    elif optimal_k == 3:
        ten_phan_khuc = ["Khách hàng VIP", "Khách hàng trung bình", "Khách hàng yếu"]
    elif optimal_k == 4:
        ten_phan_khuc = ["Khách hàng VIP", "Khách hàng trung thành", "Khách hàng tiềm năng", "Khách hàng có nguy cơ mất"]
    elif optimal_k == 5:
        ten_phan_khuc = ["Khách hàng VIP", "Khách hàng trung thành", "Khách hàng ổn định", "Khách hàng cần chăm sóc", "Khách hàng có nguy cơ mất"]
    elif optimal_k == 6:
        ten_phan_khuc = ["Khách hàng VIP", "Khách hàng trung thành", "Khách hàng tiềm năng", "Khách hàng ổn định", "Khách hàng cần chăm sóc", "Khách hàng có nguy cơ mất"]
    else:
        ten_phan_khuc = [f"Phân khúc {i+1} (Điểm cao)" if i == 0 else f"Phân khúc {i+1} (Điểm thấp)" if i == optimal_k-1 else f"Phân khúc {i+1}" for i in range(optimal_k)]

    phan_khuc_mapping = {}
    for idx, (cluster_id, row) in enumerate(cluster_ranking.iterrows()):
        phan_khuc_mapping[cluster_id] = ten_phan_khuc[idx]
    return phan_khuc_mapping

phan_khuc_mapping = tu_dong_gan_phan_khuc(optimal_k, cluster_ranking)

df_rfm_final["PhanKhuc"] = df_rfm_final["Cluster"].map(phan_khuc_mapping)

print("\n📊 Phân bổ khách hàng theo phân khúc:")
print(df_rfm_final["PhanKhuc"].value_counts().sort_index())

print("\n📋 Mẫu dữ liệu với phân khúc:")
print(df_rfm_final.head(20))

# --- Bước 9: Lưu kết quả vào database ---
cursor.execute("""
IF OBJECT_ID('Customer_Segmentation', 'U') IS NULL
BEGIN
    CREATE TABLE Customer_Segmentation (
        KhachHangID INT PRIMARY KEY,
        Recency INT,
        Frequency FLOAT,
        Monetary FLOAT,
        Cluster INT,
        PhanKhuc NVARCHAR(100)
    );
END
ELSE
BEGIN
    IF NOT EXISTS (SELECT * FROM sys.columns 
                   WHERE object_id = OBJECT_ID('Customer_Segmentation') 
                   AND name = 'PhanKhuc')
    BEGIN
        ALTER TABLE Customer_Segmentation ADD PhanKhuc NVARCHAR(100);
    END
END
""")
conn.commit()

for _, row in df_rfm_final.iterrows():
    cursor.execute("""
        MERGE Customer_Segmentation AS target
        USING (SELECT ? AS KhachHangID, ? AS Recency, ? AS Frequency, 
                      ? AS Monetary, ? AS Cluster, ? AS PhanKhuc) AS source
        ON target.KhachHangID = source.KhachHangID
        WHEN MATCHED THEN
            UPDATE SET Recency = source.Recency,
                       Frequency = source.Frequency,
                       Monetary = source.Monetary,
                       Cluster = source.Cluster,
                       PhanKhuc = source.PhanKhuc
        WHEN NOT MATCHED THEN
            INSERT (KhachHangID, Recency, Frequency, Monetary, Cluster, PhanKhuc)
            VALUES (source.KhachHangID, source.Recency, source.Frequency, 
                    source.Monetary, source.Cluster, source.PhanKhuc);
    """, row.KhachHangID, int(row.Recency), float(row.Frequency), 
        float(row.Monetary), int(row.Cluster), row.PhanKhuc)
conn.commit()
print("\n✅ Đã lưu kết quả phân cụm và phân khúc vào database!")

# --- Bước 10: Visualization ---

import seaborn as sns

plt.figure(figsize=(14, 5))

# Biểu đồ 1: Phân bổ phân khúc
plt.subplot(1, 3, 1)
phan_khuc_counts = df_rfm_final["PhanKhuc"].value_counts()
colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(phan_khuc_counts)))
phan_khuc_counts.plot(kind="bar", color=colors)
plt.title(f"Phân bổ {optimal_k} phân khúc khách hàng")
plt.xlabel("Phân khúc")
plt.ylabel("Số lượng khách hàng")
plt.xticks(rotation=45, ha='right')

# Biểu đồ 2: Recency vs Monetary
plt.subplot(1, 3, 2)
for segment in df_rfm_final["PhanKhuc"].unique():
    data = df_rfm_final[df_rfm_final["PhanKhuc"] == segment]
    plt.scatter(data["Recency"], data["Monetary"], label=segment, alpha=0.6)
plt.xlabel("Recency (ngày)")
plt.ylabel("Monetary (VND)")
plt.title("Recency vs Monetary")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)

# Biểu đồ 3: Frequency vs Monetary
plt.subplot(1, 3, 3)
for segment in df_rfm_final["PhanKhuc"].unique():
    data = df_rfm_final[df_rfm_final["PhanKhuc"] == segment]
    plt.scatter(data["Frequency"], data["Monetary"], label=segment, alpha=0.6)
plt.xlabel("Frequency (lần mua)")
plt.ylabel("Monetary (VND)")
plt.title("Frequency vs Monetary")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)

plt.tight_layout()
plt.show()

# Tổng kết phân khúc
print("\n" + "="*60)
print("📊 TỔNG KẾT PHÂN KHÚC KHÁCH HÀNG")
print("="*60)
final_summary = df_rfm_final.groupby("PhanKhuc").agg(
    SoLuong=("KhachHangID", "count"),
    R_TrungBinh=("Recency", "mean"),
    F_TrungBinh=("Frequency", "mean"),
    M_TrungBinh=("Monetary", "mean")
).round(2)
print(final_summary)
print("="*60)

# Đóng kết nối
cursor.close()
conn.close()
