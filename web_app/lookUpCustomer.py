import streamlit as st
import pandas as pd
import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Tra cứu khách hàng 360°",
    layout="wide",
    page_icon="👤"
)

# --- DỮ LIỆU GIẢ (MOCK DATA) ---
MOCK_CUSTOMERS = [
    {
        "id": 1,
        "name": "Nguyễn Văn A",
        "total_orders": 12,
        "total_spend": "15.500.000 ₫",
        "avg_order_value": "1.291.667 ₫",
        "last_purchase": "20/10/2025",
        "fav_channel": "Website",
        "group": "VIP",
        "phone": "0901234567",
        "email": "nguyena@example.com",
        "address": "P. 10, Q. 1, TP. Hồ Chí Minh",
        "region": "Miền Nam",
        "registered": "01/01/2023",
        "status": "Đang hoạt động"
    },
    {
        "id": 2,
        "name": "Trần Thị Bích",
        "total_orders": 8,
        "total_spend": "7.200.000 ₫",
        "avg_order_value": "900.000 ₫",
        "last_purchase": "15/10/2025",
        "fav_channel": "Tại cửa hàng",
        "group": "Trung thành",
        "phone": "0912345678",
        "email": "bichtran@example.com",
        "address": "Q. Ba Đình, Hà Nội",
        "region": "Miền Bắc",
        "registered": "10/05/2022",
        "status": "Đang hoạt động"
    },
    {
        "id": 3,
        "name": "Lê Hoàng C",
        "total_orders": 1,
        "total_spend": "550.000 ₫",
        "avg_order_value": "550.000 ₫",
        "last_purchase": "22/10/2025",
        "fav_channel": "Facebook",
        "group": "Mới",
        "phone": "0987654321",
        "email": "lehoangc@example.com",
        "address": "Q. Hải Châu, Đà Nẵng",
        "region": "Miền Trung",
        "registered": "22/10/2025",
        "status": "Đang hoạt động"
    },
    {
        "id": 4,
        "name": "Phạm Gia Dũng",
        "total_orders": 5,
        "total_spend": "3.100.000 ₫",
        "avg_order_value": "620.000 ₫",
        "last_purchase": "01/05/2025",
        "fav_channel": "Tại cửa hàng",
        "group": "Sắp rời bỏ",
        "phone": "090555666",
        "email": "dungpham@example.com",
        "address": "Q. 1, TP. Hồ Chí Minh",
        "region": "Miền Nam",
        "registered": "12/12/2021",
        "status": "Ít hoạt động"
    }
]

MOCK_ORDER_HISTORY = pd.DataFrame([
    {"MÃ ĐH": "#DH12345", "Ngày Mua": "20/10/2025", "Sản Phẩm": "Áo Sơ Mi Trắng Premium", "SL": 1, "Thành Tiền": "750.000 ₫", "Kênh": "Website"},
    {"MÃ ĐH": "#DH12201", "Ngày Mua": "15/09/2025", "Sản Phẩm": "Quần Jeans Slimfit, Áo Polo", "SL": 2, "Thành Tiền": "2.400.000 ₫", "Kênh": "Tại cửa hàng"},
    {"MÃ ĐH": "#DH11987", "Ngày Mua": "01/09/2025", "Sản Phẩm": "Giày Thể Thao XZ", "SL": 1, "Thành Tiền": "1.800.000 ₫", "Kênh": "Website"},
    {"MÃ ĐH": "#DH11500", "Ngày Mua": "10/08/2025", "Sản Phẩm": "Áo Thun Basic (Set 3)", "SL": 1, "Thành Tiền": "450.000 ₫", "Kênh": "Facebook"},
])

# --- TRẠNG THÁI ỨNG DỤNG (SESSION STATE) ---
if 'view' not in st.session_state:
    st.session_state.view = 'list' 
if 'selected_customer_id' not in st.session_state:
    st.session_state.selected_customer_id = None

# --- HÀM HỖ TRỢ (HELPER FUNCTIONS) ---

def get_badge_markdown(text_value):
    """Mô phỏng 'badge' (huy hiệu) bằng st.markdown."""
    if text_value == "VIP":
        return f":orange[**{text_value}**]"
    elif text_value == "Trung thành":
        return f":green[**{text_value}**]"
    elif text_value == "Mới":
        return f":blue[**{text_value}**]"
    elif text_value == "Sắp rời bỏ":
        return f":red[**{text_value}**]"
    elif text_value == "Đang hoạt động":
        return f":green[**{text_value}**]"
    else:
        return f"**{text_value}**"

def show_list_view():
    """Vẽ Màn hình 1: Danh sách tra cứu"""
    
    cols = st.columns([3, 2], vertical_alignment="bottom") 
    with cols[0]:
        st.title("Tra cứu khách hàng 360°")
    with cols[1]:
        st.text_input(
            "Tìm kiếm",
            placeholder="Nhập tên, SĐT hoặc email...",
            label_visibility="collapsed"
        )
        
    with st.expander("Bộ lọc", expanded=True):
        cols = st.columns(7, vertical_alignment="bottom") 
        with cols[0]:
            st.date_input("Từ ngày", datetime.date(2025, 1, 1))
        with cols[1]:
            st.date_input("Đến ngày", datetime.date.today())
        with cols[2]:
            st.selectbox("Khu Vực", ["Tất cả", "Miền Bắc", "Miền Trung", "Miền Nam"])
        with cols[3]:
            st.selectbox("Kênh Mua Hàng", ["Tất cả", "Tại cửa hàng", "Website", "Facebook"])
        with cols[4]:
            st.selectbox("Nhóm Khách Hàng", ["Tất cả", "VIP", "Trung thành", "Mới", "Sắp rời bỏ"])
        with cols[5]:
            st.button("Xóa bộ lọc", use_container_width=True)
        with cols[6]:
            st.button("Áp dụng bộ lọc", type="primary", use_container_width=True)

    st.divider()

    st.subheader(f"Kết quả tra cứu ({len(MOCK_CUSTOMERS)})")

    # Tiêu đề bảng
    cols = st.columns([1, 3, 2, 2, 2, 1])
    cols[0].markdown("**STT**")
    cols[1].markdown("**Tên Khách Hàng**")
    cols[2].markdown("**Tổng Chi Tiêu**")
    cols[3].markdown("**Ngày Mua Gần Nhất**")
    cols[4].markdown("**Nhóm KH**")
    cols[5].markdown("**Xem**")
    st.markdown("---") 

    # Dữ liệu bảng
    for i, customer in enumerate(MOCK_CUSTOMERS):
        cols = st.columns([1, 3, 2, 2, 2, 1], vertical_alignment="center") 
        cols[0].write(customer["id"])
        cols[1].write(customer["name"])
        cols[2].write(customer["total_spend"])
        cols[3].write(customer["last_purchase"])
        cols[4].markdown(get_badge_markdown(customer["group"]))
        
        if cols[5].button("👁️", key=f"view_{customer['id']}", help="Xem chi tiết"):
            st.session_state.view = 'detail'
            st.session_state.selected_customer_id = customer['id']
            st.rerun()

    st.divider()
    st.text(f"Hiển thị 1 đến {len(MOCK_CUSTOMERS)} của {len(MOCK_CUSTOMERS)} khách hàng")


def show_detail_view():
    """Vẽ Màn hình 2: Chi tiết khách hàng"""
    
    customer_id = st.session_state.selected_customer_id
    try:
        customer = next(c for c in MOCK_CUSTOMERS if c['id'] == customer_id)
    except StopIteration:
        st.error("Không tìm thấy khách hàng. Quay lại danh sách.")
        if st.button("Quay lại"):
            st.session_state.view = 'list'
            st.rerun()
        return

    # 1. Thanh điều hướng (Navigation Bar)
    # Bố cục này đã đúng: [Nút] [Khoảng trống] [Nút] [Nút]
    cols = st.columns([1, 3, 1, 1], vertical_alignment="bottom") 
    with cols[0]:
        if st.button("⬅️ Quay lại", use_container_width=True):
            st.session_state.view = 'list'
            st.session_state.selected_customer_id = None
            st.rerun()
    # cols[1] là khoảng trống
    with cols[2]:
        st.button("✉️ Gửi Email", use_container_width=True)
    with cols[3]:
        st.button("⬇️ Xuất Dữ Liệu", use_container_width=True)

    # 2. Tiêu đề chính
    st.title(f"Chi tiết khách hàng: {customer['name']}")
    st.divider()

    # 3. Layout chính (1 Cột)
    
    # Card 1: Thông tin Khách Hàng Cơ Bản
    with st.container(border=True):
        st.subheader("👤 Thông tin Khách Hàng Cơ Bản")
        
        # === SỬA LỖI: Chia cột [2, 1, 2] để tạo khoảng trống ở giữa ===
        # Tỉ lệ [Cột trái] - [Khoảng trống] - [Cột phải]
        cols = st.columns([2, 1, 2])
        
        # Cột 1 (Bên trái)
        with cols[0]:
            st.markdown(f"**Tên Khách Hàng:** {customer['name']}")
            st.markdown(f"**Số Điện Thoại:** {customer['phone']}")
            st.markdown(f"**Email:** {customer['email']}")
            st.markdown(f"**Địa Chỉ:** {customer['address']}")
        
        # cols[1] được để trống cố ý để tạo khoảng cách
        
        # Cột 2 (Bên phải)
        with cols[2]:
            st.markdown(f"**Ngày Đăng Ký:** {customer['registered']}")
            st.markdown(f"**Khu Vực:** {customer['region']}")
            st.markdown(f"**Tình Trạng:** {get_badge_markdown(customer['status'])}")
            st.markdown(f"**Nhóm Khách Hàng:** {get_badge_markdown(customer['group'])}")

    st.write("") # Thêm khoảng trắng

    # Card 2: Lịch Sử Đơn Hàng
    with st.container(border=True):
        st.subheader("🕒 Lịch Sử Đơn Hàng")
        st.dataframe(MOCK_ORDER_HISTORY, height=250, use_container_width=True)

    st.write("") # Thêm khoảng trắng

    # Card 3: Ghi Chú & Lịch Sử Tương Tác
    with st.container(border=True):
        st.subheader("💬 Ghi Chú & Lịch Sử Tương Tác")
        
        st.success("**21/10/2025 09:30 - Hỗ trợ (Email)**\n"
                   "\nKhách hàng hỏi về chính sách đổi trả cho ĐH #DH12345. Đã gửi email xác nhận.")
        st.error("**18/10/2025 14:15 - Sales (Gọi điện)**\n"
                 "\nGọi điện thoại tư vấn SP mới nhưng khách hàng báo bận, hẹn gọi lại sau.")
        st.info("**15/09/2025 11:00 - Cửa hàng**\n"
                "\nKhách hàng đến mua trực tiếp, rất hài lòng với chất lượng vải của Quần Jeans Slimfit.")
        
        st.divider()
        
        st.text_area("Thêm ghi chú nội bộ mới...", height=100)
        st.button("Lưu Ghi Chú", type="primary")

# --- LUỒNG CHẠY CHÍNH ---
if st.session_state.view == 'list':
    show_list_view()
elif st.session_state.view == 'detail':
    show_detail_view()

