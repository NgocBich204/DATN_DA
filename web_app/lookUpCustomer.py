import streamlit as st
import pandas as pd
import datetime
import pyodbc
import numpy as np
import math 

# --- CẤU HÌNH KẾT NỐI SQL SERVER ---
odbc_driver = "ODBC Driver 17 for SQL Server"
server = "localhost\\SQLEXPRESS"
database = "test6"
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
# Hàm định dạng tiền tệ (Helper)
def format_currency(value):
    if pd.isna(value): return "0 ₫"
    return f"{value:,.0f} ₫".replace(",", ".")
# --- CACHING DỮ LIỆU TỪ DB (TỐI ƯU HÓA TỐC ĐỘ TẢI) ---
@st.cache_data(ttl=600)
def load_customer_data_from_db():
    """Load dữ liệu Khách hàng, RFM, Phân khúc và Lịch sử đơn hàng từ SQL Server."""
    try:
        conn = pyodbc.connect(conn_str)  
        # 1. Lấy thông tin cơ bản và phân khúc (DimKhachHang + Customer_Segmentation)
        query_customers = """
        SELECT
            dk.KhachHangID, 
            dk.HoTen AS name,
            dk.SDT AS phone,
            dk.Email AS email,
            dk.TinhThanh,
            dk.QuanHuyen,
            dk.Traffic AS fav_channel,
            dk.NgaySinh,
            cs.PhanKhuc AS group_name,
            cs.Recency,
            cs.Frequency,
            cs.Monetary
        FROM dbo.DimKhachHang dk
        LEFT JOIN dbo.Customer_Segmentation cs ON dk.KhachHangID = cs.KhachHangID
        """
        df_customers = pd.read_sql(query_customers, conn)
        
        # 2. Lấy dữ liệu đơn hàng cuối cùng và tổng chi tiêu (FactDonHang + DimDate)
        query_summary = """
        SELECT 
            KhachHangID,
            MAX(d.NgayMua) AS LastPurchaseDate,
            COUNT(DISTINCT f.DonHang) AS TotalOrders,
            SUM(f.DoanhThuThuan) AS TotalSpend
        FROM dbo.FactDonHang f
        JOIN dbo.DimDate d ON f.DateID = d.DateID
        GROUP BY KhachHangID
        """
        df_summary = pd.read_sql(query_summary, conn)

        # 3. Join dữ liệu lại (Merge trên KhachHangID)
        df = pd.merge(df_customers, df_summary, on='KhachHangID', how='left')
        
        # Ép kiểu rõ ràng các cột ngày tháng về datetime
        df['NgaySinh'] = pd.to_datetime(df['NgaySinh'], errors='coerce')
        df['LastPurchaseDate'] = pd.to_datetime(df['LastPurchaseDate'], errors='coerce')

        # 4. Chuẩn hóa dữ liệu hiển thị
        df['registered'] = df['NgaySinh'].dt.strftime('%d/%m/%Y').fillna('N/A')
        df['address'] = df['QuanHuyen'].fillna('N/A') + ", " + df['TinhThanh'].fillna('N/A')
        df['region'] = np.select(
            [df['TinhThanh'].str.contains('Hà Nội|Hải Phòng', na=False),
             df['TinhThanh'].str.contains('Đà Nẵng|Huế', na=False),
             df['TinhThanh'].str.contains('Hồ Chí Minh|Cần Thơ', na=False)],
            ['Miền Bắc', 'Miền Trung', 'Miền Nam'],
            default='Khác'
        )
        df['group_name'] = df['group_name'].fillna('Chưa phân nhóm')
        
        # Tính toán
        df['last_purchase'] = df['LastPurchaseDate'].dt.strftime('%d/%m/%Y').fillna('N/A')
        df['total_orders'] = df['TotalOrders'].fillna(0).astype(int)
        df['total_spend'] = df['TotalSpend'].fillna(0)
        df['avg_order_value'] = np.where(df['total_orders'] > 0, 
                                         df['total_spend'] / df['total_orders'], 
                                         0)
        
        df['total_spend_str'] = df['total_spend'].apply(format_currency)
        df['avg_order_value_str'] = df['avg_order_value'].apply(format_currency)

        df['status'] = np.select(
            [
                df['group_name'].str.contains('VIP', na=False),
                df['group_name'].str.contains('trung thành|ổn định', na=False),
                df['group_name'].str.contains('tiềm năng|mới', case=False, na=False),
                df['group_name'].str.contains('nguy cơ mất|chăm sóc|yếu', case=False, na=False),
            ],
            [
                'Rất quan trọng', 
                'Hoạt động thường xuyên', 
                'Tiềm năng', 
                'Cần chăm sóc'
            ],
            default='Ít hoạt động'
        )

        # Chỉ lấy các cột cần thiết cho giao diện
        CUSTOMER_DATA = df[[
            "KhachHangID", "name", "total_orders", "total_spend_str", "avg_order_value_str", 
            "last_purchase", "fav_channel", "group_name", "phone", "email", 
            "address", "region", "registered", "status", "Recency", "Frequency", "Monetary"
        ]].rename(columns={'group_name': 'group', 'KhachHangID': 'id'})

        # 5. Lấy lịch sử đơn hàng (Order History)
        query_orders = """
        SELECT 
            f.KhachHangID,
            f.DonHang AS "MÃ ĐH",
            d.NgayMua,
            sp.TenSanPham AS "Sản Phẩm",
            f.SoLuong AS "SL",
            f.DoanhThuThuan AS "DoanhThuThuan",
            dk.Traffic AS "Kênh"
        FROM dbo.FactDonHang f
        JOIN dbo.DimDate d ON f.DateID = d.DateID
        JOIN dbo.DimSP sp ON f.SPID = sp.SPID
        JOIN dbo.DimKhachHang dk ON f.KhachHangID = dk.KhachHangID
        ORDER BY d.NgayMua DESC
        """
        df_orders = pd.read_sql(query_orders, conn)
        
        df_orders['NgayMua'] = pd.to_datetime(df_orders['NgayMua'], errors='coerce')
        
        df_orders['Ngày Mua'] = df_orders['NgayMua'].dt.strftime('%d/%m/%Y %H:%M:%S')
        df_orders['Thành Tiền'] = df_orders['DoanhThuThuan'].apply(format_currency)
        
        agg_orders = df_orders.groupby(['KhachHangID', 'MÃ ĐH', 'Ngày Mua', 'SL', 'Thành Tiền', 'Kênh'])['Sản Phẩm'].apply(lambda x: ', '.join(x.astype(str).unique())).reset_index()
        ORDER_HISTORY_DATA = agg_orders[['KhachHangID', 'MÃ ĐH', 'Ngày Mua', 'Sản Phẩm', 'SL', 'Thành Tiền', 'Kênh']]

        conn.close()
        return CUSTOMER_DATA, ORDER_HISTORY_DATA

    except Exception as e:
        error_msg = str(e)
        if 'ODBC Driver' in error_msg or 'Login failed' in error_msg:
             st.error("Lỗi kết nối CSDL: Vui lòng kiểm tra tên Server, Database, hoặc Driver ODBC đã cài đặt.")
        else:
             st.error(f"Lỗi truy vấn CSDL: {error_msg}")
        return pd.DataFrame(), pd.DataFrame() 
# Tải dữ liệu
CUSTOMER_DATA, ORDER_HISTORY_DATA = load_customer_data_from_db()
default_from_date = datetime.date(2021, 1, 1)
default_to_date = datetime.date.today()
if 'lookup_page' not in st.session_state:
    st.session_state.lookup_page = 0

if 'search_term' not in st.session_state:
    st.session_state.search_term = ""

if 'filter_from_date' not in st.session_state:
    st.session_state.filter_from_date = default_from_date

if 'filter_to_date' not in st.session_state:
    st.session_state.filter_to_date = default_to_date

if 'filter_region' not in st.session_state:
    st.session_state.filter_region = "Tất cả"

if 'filter_channel' not in st.session_state:
    st.session_state.filter_channel = "Tất cả"

if 'filter_group' not in st.session_state:
    st.session_state.filter_group = "Tất cả"
# --- HÀM HỖ TRỢ (HELPER FUNCTIONS) ---
def get_badge_markdown(text_value):
    """
    Gán màu sắc cho cả Nhóm KH (Phân khúc) và Tình trạng (Status)
    """
    if text_value == "Rất quan trọng":
        return f":orange[**{text_value}**]"
    elif text_value == "Hoạt động thường xuyên":
        return f":green[**{text_value}**]"
    elif text_value == "Tiềm năng":
        return f":blue[**{text_value}**]"
    elif text_value in ["Cần chăm sóc", "Ít hoạt động"]:
        return f":red[**{text_value}**]" 
    elif text_value in ["Khách hàng VIP", "VIP"]:
        return f":orange[**{text_value}**]"
    elif text_value in ["Khách hàng trung thành", "Trung thành", "Khách hàng ổn định"]:
        return f":green[**{text_value}**]"
    elif text_value in ["Khách hàng tiềm năng", "Mới"]:
        return f":blue[**{text_value}**]"
    elif text_value in ["Khách hàng có nguy cơ mất", "Khách hàng cần chăm sóc", "Khách hàng yếu"]:
        return f":red[**{text_value}**]"
    else:
        return f"**{text_value}**"
def filter_customers(search_term, from_date, to_date, region, channel, group):
    """Lọc danh sách khách hàng theo các tiêu chí"""
    df = CUSTOMER_DATA.copy()
    # Lọc tìm kiếm
    if search_term:
        df = df[
            df['name'].str.contains(search_term, case=False, na=False) |
            df['phone'].str.contains(search_term, case=False, na=False) |
            df['email'].str.contains(search_term, case=False, na=False)
        ] 
    # Lọc theo Khu vực
    if region != "Tất cả":
        df = df[df['region'] == region]

    # Lọc theo Kênh
    if channel != "Tất cả":
        df = df[df['fav_channel'] == channel]
        
    # Lọc theo Nhóm KH
    if group != "Tất cả":
        df = df[df['group'] == group]

    # Lọc theo ngày đăng ký
    is_date_filtered = (from_date != default_from_date) or (to_date != default_to_date)

    if is_date_filtered:
        try:
            df['registered_date'] = pd.to_datetime(df['registered'], format='%d/%m/%Y', errors='coerce')
            
            start_date = np.datetime64(from_date)
            end_date = np.datetime64(to_date) + np.timedelta64(1, 'D') 

            df = df[
                (df['registered_date'].notna()) & 
                (df['registered_date'] >= start_date) &
                (df['registered_date'] < end_date) 
            ]
        except Exception:
            pass 
            
    return df.to_dict('records')


def show_list_view():
    """Vẽ Màn hình 1: Danh sách tra cứu"""
    
    if CUSTOMER_DATA.empty:
        st.warning("Không có dữ liệu khách hàng. Vui lòng kiểm tra kết nối CSDL và đảm bảo file ETL.py đã chạy thành công.")
        return

    # --- TITLE VÀ SEARCH BAR (NGOÀI FORM) ---
    cols = st.columns([3, 2], vertical_alignment="bottom")
    with cols[0]:
        st.title("Tra cứu khách hàng 360°")
    with cols[1]:
        # Search bar ở ngoài form để không bị reset
        search_input = st.text_input(
            "Tìm kiếm",
            placeholder="Nhập tên, SĐT hoặc email...",
            label_visibility="collapsed",
            value=st.session_state.search_term,
            key="search_input_field"
        )
        # Cập nhật search_term ngay khi user gõ
        if search_input != st.session_state.search_term:
            st.session_state.search_term = search_input
            st.session_state.lookup_page = 0  # Reset trang khi search
    
    # --- FORM LỌC ---
        from datetime import datetime, timedelta
        
        # Khởi tạo tất cả session_state
        if 'filter_from_date' not in st.session_state:
            st.session_state.filter_from_date = datetime.now().date() - timedelta(days=365)
        
        if 'filter_to_date' not in st.session_state:
            st.session_state.filter_to_date = datetime.now().date()
        
        if 'filter_region' not in st.session_state:
            st.session_state.filter_region = "Tất cả"
        
        if 'filter_channel' not in st.session_state:
            st.session_state.filter_channel = "Tất cả"
        
        if 'filter_group' not in st.session_state:
            st.session_state.filter_group = "Tất cả"    
    with st.expander("Bộ lọc", expanded=True):
        with st.form("filter_form"):
            cols = st.columns(7, vertical_alignment="bottom") 
            
            with cols[0]:
                from_date_input = st.date_input("Từ ngày", value=st.session_state.filter_from_date) 
            with cols[1]:
                to_date_input = st.date_input("Đến ngày", value=st.session_state.filter_to_date)
            with cols[2]:
                unique_regions = ["Tất cả"] + list(CUSTOMER_DATA["region"].unique())
                region_index = unique_regions.index(st.session_state.filter_region) if st.session_state.filter_region in unique_regions else 0
                selected_region_input = st.selectbox("Khu Vực", unique_regions, index=region_index)
            with cols[3]:
                unique_channels = ["Tất cả"] + list(CUSTOMER_DATA["fav_channel"].unique())
                channel_index = unique_channels.index(st.session_state.filter_channel) if st.session_state.filter_channel in unique_channels else 0
                selected_channel_input = st.selectbox("Kênh Mua Hàng", unique_channels, index=channel_index)
            with cols[4]:
                unique_groups = ["Tất cả"] + list(CUSTOMER_DATA["group"].unique())
                group_index = unique_groups.index(st.session_state.filter_group) if st.session_state.filter_group in unique_groups else 0
                selected_group_input = st.selectbox("Nhóm KH", unique_groups, index=group_index)
            
            with cols[5]:
                reset_pressed = st.form_submit_button("Xóa bộ lọc", use_container_width=True)
            with cols[6]:
                apply_pressed = st.form_submit_button("Áp dụng", type="primary", use_container_width=True)

            # Xử lý khi nhấn nút
            if apply_pressed:
                st.session_state.filter_from_date = from_date_input
                st.session_state.filter_to_date = to_date_input
                st.session_state.filter_region = selected_region_input
                st.session_state.filter_channel = selected_channel_input
                st.session_state.filter_group = selected_group_input
                st.session_state.lookup_page = 0
                st.rerun()

            if reset_pressed:
                st.session_state.search_term = ""
                st.session_state.filter_from_date = default_from_date
                st.session_state.filter_to_date = default_to_date
                st.session_state.filter_region = "Tất cả"
                st.session_state.filter_channel = "Tất cả"
                st.session_state.filter_group = "Tất cả"
                st.session_state.lookup_page = 0
                st.rerun()

    # --- LỌC DỮ LIỆU (Ở NGOÀI FORM) ---
    filtered_customers = filter_customers(
        st.session_state.search_term, 
        st.session_state.filter_from_date, 
        st.session_state.filter_to_date, 
        st.session_state.filter_region, 
        st.session_state.filter_channel, 
        st.session_state.filter_group
    )

    st.divider()
    
    # --- PHÂN TRANG ---
    ITEMS_PER_PAGE = 20
    total_items = len(filtered_customers)
    total_pages = math.ceil(total_items / ITEMS_PER_PAGE)
    
    current_page = st.session_state.lookup_page 
    
    if current_page >= total_pages:
        current_page = total_pages - 1 if total_pages > 0 else 0
        st.session_state.lookup_page = current_page
    
    start_idx = current_page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    
    paged_customers = filtered_customers[start_idx:end_idx]

    st.subheader(f"Kết quả tra cứu ({total_items})")
    
    # Tiêu đề bảng
    cols = st.columns([1, 3, 2, 2, 2, 1])
    cols[0].markdown("**ID**")
    cols[1].markdown("**Tên Khách Hàng**")
    cols[2].markdown("**Tổng Chi Tiêu**")
    cols[3].markdown("**Ngày Mua Gần Nhất**")
    cols[4].markdown("**Nhóm KH**")
    cols[5].markdown("**Xem**")
    st.markdown("---") 

    # Dữ liệu bảng
    if not paged_customers:
        st.info("Không tìm thấy khách hàng nào phù hợp với điều kiện.")
    else:
        for customer in paged_customers:
            cols = st.columns([1, 3, 2, 2, 2, 1], vertical_alignment="center") 
            cols[0].write(customer["id"])
            cols[1].write(customer["name"])
            cols[2].write(customer["total_spend_str"])
            cols[3].write(customer["last_purchase"])
            cols[4].markdown(get_badge_markdown(customer["group"]))
            
            if cols[5].button("👁️", key=f"view_{customer['id']}", help="Xem chi tiết"):
                st.session_state.view = 'detail'
                st.session_state.selected_customer_id = customer['id']
                st.rerun()

    st.divider()

    # Navigation buttons
    cols_nav = st.columns([1, 1, 4, 1, 1])
    
    if cols_nav[0].button("⬅️ Trang trước", disabled=(current_page == 0)):
        st.session_state.lookup_page -= 1
        st.rerun()
        
    if cols_nav[4].button("Trang sau ➡️", disabled=(current_page >= total_pages - 1)):
        st.session_state.lookup_page += 1 
        st.rerun() 
         
    start_display = start_idx + 1
    end_display = min(end_idx, total_items) 
    if total_items > 0:
        cols_nav[2].write(f"Đang hiển thị **{start_display}** đến **{end_display}** (Trang **{current_page + 1}** / **{total_pages}**)")
    else:
        cols_nav[2].write("Không có khách hàng nào.")
    st.text(f"Tổng cộng {len(CUSTOMER_DATA)} khách hàng trong CSDL")


def show_detail_view():
    """Màn hình chi tiết khách hàng"""
    customer_id = st.session_state.selected_customer_id
    try:
        customer_df = CUSTOMER_DATA[CUSTOMER_DATA['id'] == customer_id].iloc[0]
        customer = customer_df.to_dict()
        
        order_history = ORDER_HISTORY_DATA[ORDER_HISTORY_DATA['KhachHangID'] == customer_id].drop(columns=['KhachHangID'], errors='ignore')
        
    except IndexError:
        st.error("Không tìm thấy khách hàng. Quay lại danh sách.")
        if st.button("Quay lại"):
            st.session_state.view = 'list'
            st.session_state.selected_customer_id = None
            st.rerun()
        return

    # Navigation Bar
    cols = st.columns([1, 3, 1, 1], vertical_alignment="bottom") 
    with cols[0]:
        if st.button("⬅️ Quay lại", use_container_width=True):
            st.session_state.view = 'list'
            st.session_state.selected_customer_id = None
            st.rerun()
    with cols[2]:
        st.button("✉️ Gửi Email", use_container_width=True)
    with cols[3]:
        st.button("⬇️ Xuất file", use_container_width=True)

    st.title(f"Chi tiết khách hàng: {customer['name']}")
    st.divider()

    # Card 1: Thông tin cơ bản
    with st.container(border=True):
        st.subheader("👤 Thông tin Khách Hàng Cơ Bản")
        
        cols = st.columns([2, 1, 2])
        
        with cols[0]:
            st.markdown(f"**Tên Khách Hàng:** {customer['name']}")
            st.markdown(f"**Số Điện Thoại:** {customer['phone']}")
            st.markdown(f"**Email:** {customer['email']}")
            st.markdown(f"**Địa Chỉ:** {customer['address']}")
        
        with cols[2]:
            st.markdown(f"**Ngày Đăng Ký:** {customer['registered']}")
            st.markdown(f"**Khu Vực:** {customer['region']}")
            st.markdown(f"**Ghi chú:** {get_badge_markdown(customer['status'])}") 
            st.markdown(f"**Nhóm Khách Hàng:** {get_badge_markdown(customer['group'])}") 

    # Card 2: RFM
    with st.container(border=True):
        st.subheader("📊 Phân Tích RFM")
        r_val = customer.get('Recency', 'N/A')
        f_val = customer.get('Frequency', 'N/A')
        m_val = customer.get('Monetary', 'N/A')
        
        cols = st.columns(3)
        cols[0].metric("Recency (Ngày)", f"{r_val}" if r_val != 'N/A' else "N/A")
        cols[1].metric("Frequency (Lần mua)", f"{f_val:.0f}" if isinstance(f_val, (int, float)) else "N/A")
        cols[2].metric("Monetary (Chi tiêu)", f"{m_val:,.0f} ₫".replace(",", ".") if isinstance(m_val, (int, float)) else "N/A")

    st.write("") 
    
    # Card 3: Lịch sử đơn hàng
    with st.container(border=True):
        st.subheader(f"🕒 Lịch Sử Đơn Hàng (Tổng: {len(order_history)} đơn)")
        if order_history.empty:
             st.info("Khách hàng này chưa có đơn hàng nào trong dữ liệu.")
        else:
            st.dataframe(order_history, height=250, use_container_width=True)

    st.write("")

    # Card 4: Ghi chú
    with st.container(border=True):
        st.subheader("💬 Ghi Chú & Lịch Sử Tương Tác")
        
        st.success("**21/10/2025 09:30 - Hỗ trợ (Email)**\n"
                     "\nKhách hàng hỏi về chính sách đổi trả. Đã gửi email xác nhận.")
        st.error("**18/10/2025 14:15 - Sales (Gọi điện)**\n"
                    "\nGọi điện thoại tư vấn SP mới nhưng khách hàng báo bận, hẹn gọi lại sau.")
        st.info("**15/09/2025 11:00 - Cửa hàng**\n"
                     "\nKhách hàng đến mua trực tiếp, rất hài lòng với chất lượng vải.")
        
        st.divider()
        
        st.text_area("Thêm ghi chú nội bộ mới...", height=100)
        st.button("Lưu Ghi Chú", type="primary")