"""
Module ETL Core - Xử lý import dữ liệu từ Excel vào SQL Server
Chuyển đổi từ file ETL.py gốc thành class để tích hợp Streamlit
"""

import pandas as pd
import pyodbc
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import json
from datetime import datetime


class ETLPipeline:
    """Class xử lý toàn bộ quy trình ETL"""
    
    def __init__(self, config_path="etl_config.json"):
        """Khởi tạo với config"""
        # Đọc config
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.config = config['sqlserver']
        self.conn_str = self._build_connection_string()
        self.conn = None
        self.cursor = None
        
        # Biến lưu trạng thái
        self.df_clean = None
        self.optimal_k = None
        
    def _build_connection_string(self):
        """Tạo connection string từ config"""
        return (
            f"Driver={{{self.config['odbc_driver']}}};"
            f"Server={self.config['server']};"
            f"Database={self.config['database']};"
            "Trusted_Connection=yes;"
            f"Encrypt={self.config['encrypt']};"
            f"TrustServerCertificate={self.config['trust_server_certificate']};"
        )
    
    def connect_db(self):
        """Kết nối database"""
        try:
            self.conn = pyodbc.connect(self.conn_str)
            self.cursor = self.conn.cursor()
            return True, "✅ Kết nối database thành công"
        except Exception as e:
            return False, f"❌ Lỗi kết nối: {str(e)}"
    
    def close_db(self):
        """Đóng kết nối"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def read_and_clean_excel(self, file_path):
        """
        Đọc và làm sạch file Excel
        Copy từ ETL.py: dòng 30-60
        """
        try:
            # Đọc file
            df = pd.read_excel(file_path)
            
            # Làm sạch
            df = df.loc[:, ~df.columns.str.contains("Unnamed")]
            df = df.dropna(how='all')
            df.columns = df.columns.str.strip()
            
            # Chuyển đổi ngày tháng
            df['NgaySinh'] = pd.to_datetime(df['NgaySinh'], errors='coerce', dayfirst=True)
            df['NgayMua'] = pd.to_datetime(df['NgayMua'], errors='coerce', dayfirst=True)
            df = df.dropna(subset=['NgaySinh', 'NgayMua'])
            
            # Validate cột bắt buộc
            required_columns = ['HoTen', 'Email', 'SDT', 'SKU', 'DonHang', 'SoLuong', 'DoanhThu']
            df = df.dropna(subset=required_columns)
            
            # Chuyển đổi số
            df['SoLuong'] = pd.to_numeric(df['SoLuong'], errors='coerce')
            df['DoanhThu'] = pd.to_numeric(df['DoanhThu'], errors='coerce')
            df['TienKhuyenMai'] = pd.to_numeric(df['TienKhuyenMai'], errors='coerce').fillna(0)
            df['VanChuyen'] = pd.to_numeric(df['VanChuyen'], errors='coerce').fillna(0)
            df['DoanhThuThuan'] = pd.to_numeric(df['DoanhThuThuan'], errors='coerce')
            df = df.dropna(subset=['SoLuong', 'DoanhThu', 'DoanhThuThuan'])
            
            self.df_clean = df
            
            return True, f"✅ Đọc file thành công! Số dòng: {len(df)}", df
            
        except Exception as e:
            return False, f"❌ Lỗi đọc file: {str(e)}", None
    
    def load_to_staging(self, mode="replace"):
        """
        Load dữ liệu vào bảng Staging
        mode: 'replace' (xóa hết), 'append' (thêm vào)
        """
        try:
            # Tạo bảng Staging nếu chưa có
            if mode == "replace":
                self.cursor.execute("""
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
            self.conn.commit()
            
            # Insert dữ liệu
            for idx, row in self.df_clean.iterrows():
                self.cursor.execute("""
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
            self.conn.commit()
            
            return True, f"✅ Load {len(self.df_clean)} dòng vào Staging"
            
        except Exception as e:
            self.conn.rollback()
            return False, f"❌ Lỗi load Staging: {str(e)}"
    
    def create_dimension_tables(self, mode="replace"):
        """
        Tạo các bảng Dimension từ Staging
        mode: 'replace' (DROP & CREATE), 'append' (chỉ INSERT mới)
        """
        try:
            # Nếu mode = replace → Xóa và tạo lại bảng
            if mode == "replace":
                self.cursor.execute("""
                IF OBJECT_ID('dbo.FactDonHang', 'U') IS NOT NULL DROP TABLE dbo.FactDonHang;
                IF OBJECT_ID('dbo.DimKhachHang', 'U') IS NOT NULL DROP TABLE dbo.DimKhachHang;
                IF OBJECT_ID('dbo.DimNhomSP', 'U') IS NOT NULL DROP TABLE dbo.DimNhomSP;
                IF OBJECT_ID('dbo.DimSP', 'U') IS NOT NULL DROP TABLE dbo.DimSP;
                IF OBJECT_ID('dbo.DimDate', 'U') IS NOT NULL DROP TABLE dbo.DimDate;
                
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
                
                CREATE TABLE dbo.DimNhomSP (
                    NhomSPID INT IDENTITY(1,1) PRIMARY KEY,
                    TenNhomSanPham NVARCHAR(100) UNIQUE
                );
                
                CREATE TABLE dbo.DimSP (
                    SPID INT IDENTITY(1,1) PRIMARY KEY,
                    SKU NVARCHAR(50) UNIQUE,
                    TenSanPham NVARCHAR(255),
                    NhaSanXuat NVARCHAR(100),
                    PhienBan NVARCHAR(100)
                );
                
                CREATE TABLE dbo.DimDate (
                    DateID INT IDENTITY(1,1) PRIMARY KEY,
                    NgayMua DATETIME,
                    Thang INT,
                    Quy INT,
                    Nam INT
                );
                
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
            
            self.conn.commit()
            
            # Insert dữ liệu vào Dim (chung cho cả replace và append)
            self.cursor.execute("""
            INSERT INTO dbo.DimKhachHang (HoTen, Email, SDT, GioiTinh, NgaySinh, TinhThanh, QuanHuyen, Traffic)
            SELECT HoTen, Email, SDT, GioiTinh, NgaySinh, TinhThanh, QuanHuyen, Traffic FROM (
                SELECT *, ROW_NUMBER() OVER (PARTITION BY Email ORDER BY NgayMua DESC) as rn 
                FROM dbo.StagingSaleData
            ) sub WHERE rn = 1 AND Email IS NOT NULL
            AND NOT EXISTS (SELECT 1 FROM dbo.DimKhachHang WHERE Email = sub.Email)
            """)
            
            self.cursor.execute("""
            INSERT INTO dbo.DimNhomSP (TenNhomSanPham)
            SELECT DISTINCT TenNhomSanPham FROM dbo.StagingSaleData s
            WHERE TenNhomSanPham IS NOT NULL
            AND NOT EXISTS (SELECT 1 FROM dbo.DimNhomSP d WHERE d.TenNhomSanPham = s.TenNhomSanPham)
            """)
            
            self.cursor.execute("""
            INSERT INTO dbo.DimSP (SKU, TenSanPham, NhaSanXuat, PhienBan)
            SELECT SKU, MIN(TenSanPham), MIN(NhaSanXuat), MIN(PhienBan) 
            FROM dbo.StagingSaleData
            WHERE SKU IS NOT NULL
            GROUP BY SKU
            HAVING NOT EXISTS (SELECT 1 FROM dbo.DimSP WHERE SKU = dbo.StagingSaleData.SKU)
            """)
            
            self.cursor.execute("""
            INSERT INTO dbo.DimDate (NgayMua, Thang, Quy, Nam)
            SELECT DISTINCT 
                NgayMua,
                MONTH(NgayMua),
                DATEPART(QUARTER, NgayMua),
                YEAR(NgayMua)
            FROM dbo.StagingSaleData s
            WHERE NgayMua IS NOT NULL
            AND NOT EXISTS (SELECT 1 FROM dbo.DimDate d WHERE d.NgayMua = s.NgayMua)
            """)
            
            self.conn.commit()
            
            return True, "✅ Tạo Dimension tables thành công"
            
        except Exception as e:
            self.conn.rollback()
            return False, f"❌ Lỗi tạo Dim: {str(e)}"
    
    def create_fact_table(self):
        """Tạo bảng Fact từ Staging + Dim"""
        try:
            self.cursor.execute("""
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
            self.conn.commit()
            
            return True, "✅ Tạo Fact table thành công"
            
        except Exception as e:
            self.conn.rollback()
            return False, f"❌ Lỗi tạo Fact: {str(e)}"
    
    def calculate_rfm(self):
        """Tính RFM từ FactDonHang"""
        try:
            query = """
            SELECT
                f.KhachHangID,
                f.DonHang,
                d.NgayMua as Ngay, 
                f.DoanhThuThuan
            FROM dbo.FactDonHang f
            JOIN dbo.DimDate d ON f.DateID = d.DateID
            """
            df_rfm = pd.read_sql(query, self.conn)
            
            df_rfm["Ngay"] = pd.to_datetime(df_rfm["Ngay"], errors="coerce").fillna(pd.Timestamp("2021-04-04"))
            
            ngay_tham_chieu = df_rfm["Ngay"].max() + pd.Timedelta(days=1)
            
            df_rfm_grouped = df_rfm.groupby("KhachHangID").agg(
                NgayMuaGanNhat=("Ngay", "max"),
                SoLanMua=("DonHang", "nunique"),
                TongTien=("DoanhThuThuan", "sum")
            ).reset_index()
            
            df_rfm_grouped["Recency"] = (ngay_tham_chieu - df_rfm_grouped["NgayMuaGanNhat"]).dt.days
            df_rfm_grouped["Frequency"] = df_rfm_grouped["SoLanMua"]
            df_rfm_grouped["Monetary"] = df_rfm_grouped["TongTien"]
            
            df_rfm_final = df_rfm_grouped[["KhachHangID", "Recency", "Frequency", "Monetary"]].copy()
            
            # Lưu vào DB
            self.cursor.execute("""
            IF OBJECT_ID('RFM_KhachHang', 'U') IS NULL
            CREATE TABLE RFM_KhachHang (
                KhachHangID INT PRIMARY KEY,
                Recency INT,
                Frequency FLOAT,
                Monetary FLOAT
            )
            """)
            self.conn.commit()
            
            for _, row in df_rfm_final.iterrows():
                self.cursor.execute("""
                MERGE RFM_KhachHang AS target
                USING (SELECT ? AS KhachHangID, ? AS Recency, ? AS Frequency, ? AS Monetary) AS source
                ON target.KhachHangID = source.KhachHangID
                WHEN MATCHED THEN
                    UPDATE SET Recency = source.Recency, Frequency = source.Frequency, Monetary = source.Monetary
                WHEN NOT MATCHED THEN
                    INSERT (KhachHangID, Recency, Frequency, Monetary)
                    VALUES (source.KhachHangID, source.Recency, source.Frequency, source.Monetary);
                """, row.KhachHangID, int(row.Recency), float(row.Frequency), float(row.Monetary))
            self.conn.commit()
            
            return True, f"✅ Tính RFM cho {len(df_rfm_final)} khách hàng", df_rfm_final
            
        except Exception as e:
            return False, f"❌ Lỗi tính RFM: {str(e)}", None
    
    def kmeans_clustering(self, df_rfm, auto_k=True, manual_k=6):
        """
        Phân cụm KMeans
        auto_k=True: Tự động tìm K tối ưu
        auto_k=False: Dùng manual_k
        """
        try:
            # Chuẩn hóa
            X = df_rfm[["Recency", "Frequency", "Monetary"]]
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Tìm K tối ưu nếu auto
            if auto_k:
                sse = []
                K_range = range(2, 10)
                
                for k in K_range:
                    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                    kmeans.fit(X_scaled)
                    sse.append(kmeans.inertia_)
                
                # Phương pháp Kneedle
                k_norm = (np.array(K_range) - min(K_range)) / (max(K_range) - min(K_range))
                sse_norm = (np.array(sse) - min(sse)) / (max(sse) - min(sse))
                
                x1, y1 = k_norm[0], sse_norm[0]
                x2, y2 = k_norm[-1], sse_norm[-1]
                khoang_cach = []
                for i in range(len(k_norm)):
                    x0, y0 = k_norm[i], sse_norm[i]
                    d = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1) / np.sqrt((y2-y1)**2 + (x2-x1)**2)
                    khoang_cach.append(d)
                
                optimal_k = K_range[np.argmax(khoang_cach)]
            else:
                optimal_k = manual_k
            
            self.optimal_k = optimal_k
            
            # Chạy KMeans
            kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
            df_rfm["Cluster"] = kmeans.fit_predict(X_scaled)
            
            # Gán tên phân khúc
            cluster_summary = df_rfm.groupby("Cluster")[["Recency", "Frequency", "Monetary"]].mean()
            
            r_max = cluster_summary['Recency'].max()
            f_max = cluster_summary['Frequency'].max()
            m_max = cluster_summary['Monetary'].max()
            
            cluster_summary['R_Score'] = 1 - (cluster_summary['Recency'] / r_max)
            cluster_summary['F_Score'] = cluster_summary['Frequency'] / f_max
            cluster_summary['M_Score'] = cluster_summary['Monetary'] / m_max
            cluster_summary['RFM_Score'] = (cluster_summary['R_Score'] + cluster_summary['F_Score'] + cluster_summary['M_Score']) / 3
            
            cluster_ranking = cluster_summary.sort_values('RFM_Score', ascending=False)
            
            # Tên phân khúc theo K
            if optimal_k == 4:
                ten_phan_khuc = ["Khách hàng VIP", "Khách hàng trung thành", "Khách hàng tiềm năng", "Khách hàng có nguy cơ mất"]
            elif optimal_k == 5:
                ten_phan_khuc = ["Khách hàng VIP", "Khách hàng trung thành", "Khách hàng mới", "Khách hàng cần chăm sóc", "Khách hàng có nguy cơ mất"]
            elif optimal_k == 6:
                ten_phan_khuc = ["Khách hàng VIP", "Khách hàng trung thành", "Khách hàng tiềm năng", "Khách hàng mới", "Khách hàng cần chăm sóc", "Khách hàng yếu"]
            else:
                ten_phan_khuc = [f"Phân khúc {i+1}" for i in range(optimal_k)]
            
            phan_khuc_mapping = {cluster_id: ten_phan_khuc[idx] for idx, (cluster_id, row) in enumerate(cluster_ranking.iterrows())}
            df_rfm["PhanKhuc"] = df_rfm["Cluster"].map(phan_khuc_mapping)
            
            # Lưu vào DB
            self.cursor.execute("""
            IF OBJECT_ID('Customer_Segmentation', 'U') IS NULL
            CREATE TABLE Customer_Segmentation (
                KhachHangID INT PRIMARY KEY,
                Recency INT,
                Frequency FLOAT,
                Monetary FLOAT,
                Cluster INT,
                PhanKhuc NVARCHAR(100)
            )
            """)
            self.conn.commit()
            
            for _, row in df_rfm.iterrows():
                self.cursor.execute("""
                MERGE Customer_Segmentation AS target
                USING (SELECT ? AS KhachHangID, ? AS Recency, ? AS Frequency, 
                              ? AS Monetary, ? AS Cluster, ? AS PhanKhuc) AS source
                ON target.KhachHangID = source.KhachHangID
                WHEN MATCHED THEN
                    UPDATE SET Recency = source.Recency, Frequency = source.Frequency,
                               Monetary = source.Monetary, Cluster = source.Cluster, PhanKhuc = source.PhanKhuc
                WHEN NOT MATCHED THEN
                    INSERT (KhachHangID, Recency, Frequency, Monetary, Cluster, PhanKhuc)
                    VALUES (source.KhachHangID, source.Recency, source.Frequency, 
                            source.Monetary, source.Cluster, source.PhanKhuc);
                """, row.KhachHangID, int(row.Recency), float(row.Frequency), 
                    float(row.Monetary), int(row.Cluster), row.PhanKhuc)
            self.conn.commit()
            
            # Thống kê
            segment_stats = df_rfm["PhanKhuc"].value_counts().to_dict()
            
            return True, f"✅ Phân cụm thành {optimal_k} nhóm", segment_stats
            
        except Exception as e:
            return False, f"❌ Lỗi phân cụm: {str(e)}", None
    
    def run_full_pipeline(self, file_path, mode="replace"):
        """
        Chạy toàn bộ ETL pipeline
        Trả về: (success, message, stats)
        """
        stats = {}
        
        # 1. Connect DB
        success, msg = self.connect_db()
        if not success:
            return False, msg, stats
        stats['connect'] = msg
        
        # 2. Read & Clean
        success, msg, df = self.read_and_clean_excel(file_path)
        if not success:
            self.close_db()
            return False, msg, stats
        stats['read'] = msg
        stats['total_rows'] = len(df)
        
        # 3. Load to Staging
        success, msg = self.load_to_staging(mode)
        if not success:
            self.close_db()
            return False, msg, stats
        stats['staging'] = msg
        
        # 4. Create Dim
        success, msg = self.create_dimension_tables(mode)
        if not success:
            self.close_db()
            return False, msg, stats
        stats['dim'] = msg
        
        # 5. Create Fact
        success, msg = self.create_fact_table()
        if not success:
            self.close_db()
            return False, msg, stats
        stats['fact'] = msg
        
        # 6. RFM
        success, msg, df_rfm = self.calculate_rfm()
        if not success:
            self.close_db()
            return False, msg, stats
        stats['rfm'] = msg
        stats['total_customers'] = len(df_rfm)
        
        # 7. KMeans
        success, msg, segment_stats = self.kmeans_clustering(df_rfm, auto_k=True)
        if not success:
            self.close_db()
            return False, msg, stats
        stats['kmeans'] = msg
        stats['segments'] = segment_stats
        
        self.close_db()
        
        return True, "✅ ETL hoàn thành!", stats