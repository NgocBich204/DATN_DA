import streamlit as st
import Overview
import lookUpCustomer
import Campaign

# ===============================
# ⚙️ 1. KHỞI TẠO SESSION STATE (Giữ nguyên)
# ===============================
def init_session_state():
    defaults = {
        "page": "Tổng quát",
        "view": "list",
        "selected_customer_id": None,
        "search_term": ""
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# ===============================
# 🎨 2. HÀM CSS TÙY CHỈNH GIAO DIỆN (PHIÊN BẢN MỚI)
# ===============================
def apply_custom_css():
    """
    CSS tùy chỉnh cho giao diện mới với sidebar,
    phong cách tươi sáng, năng động.
    """
    st.markdown("""
        <style>
        /* Ẩn header và footer mặc định của Streamlit */
        header[data-testid="stHeader"],
        footer[data-testid="stFooter"] {
            visibility: hidden;
            height: 0px;
            margin: 0px;
            padding: 0px;
        }

        /* Xóa khoảng đệm (padding) ở đầu trang chính */
        .main .block-container { 
            padding-top: 2rem !important; 
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            padding-bottom: 2rem !important;
        }
        
        /* === TÙY CHỈNH SIDEBAR (NAVBAR MỚI) === */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF; /* Nền trắng sạch sẽ */
            border-right: 1px solid #E0E0E0;
            padding-top: 1.5rem;
        }

        /* === STYLE NÚT ĐIỀU HƯỚNG TRONG SIDEBAR === */
        button[data-testid="baseButton-secondary"],
        button[data-testid="baseButton-primary"] {
            border-radius: 8px !important;
            font-size: 1.05rem !important; /* Font thân thiện, dễ đọc */
            font-weight: 600 !important;
            transition: all 0.2s ease-in-out;
            border-width: 2px !important;
            height: 50px !important; 
            width: 100% !important;
            display: flex;
            align-items: center;
            justify-content: flex-start !important; /* Căn lề trái */
            padding-left: 20px !important; /* Thêm padding trái */
        }
        
        /* Nút phụ (không được chọn) */
        button[data-testid="baseButton-secondary"] {
            background-color: transparent !important;
            border-color: transparent !important; /* Không viền */
            color: #495057 !important; /* Màu chữ xám thân thiện */
        }
        button[data-testid="baseButton-secondary"]:hover {
             background-color: #F8F9FA !important; /* Hiệu ứng hover nhẹ */
             color: #007BFF !important;
        }
        
        /* Nút chính (đang được chọn) */
        button[data-testid="baseButton-primary"] {
            background-color: #E6F2FF !important; /* Nền xanh nhạt (tươi sáng) */
            border-color: #007BFF !important; /* Viền xanh */
            color: #007BFF !important; /* Chữ màu xanh */
        }
        
        </style>
        """, unsafe_allow_html=True)

# ===============================
# 🧭 3. CẤU HÌNH TRANG STREAMLIT
# ===============================
st.set_page_config(
    page_title="CRM Modun",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded" # Luôn mở rộng sidebar
)
apply_custom_css() # Gọi hàm CSS đã được cập nhật

# ===============================
# 🧭 4. THANH ĐIỀU HƯỚNG (NAVBAR BÊN TRÁI)
# ===============================
with st.sidebar:
    # LOGO + TIÊU ĐỀ
    st.markdown(
        """
        <div style='display: flex; align-items: center; font-size: 2.2rem; font-weight: 700; color: #1E1E1E; padding-left: 20px; padding-bottom: 1.5rem;'>
            <img src="https://emojicdn.elk.sh/📚?style=twitter" width="40" height="40" style="margin-right: 10px;">
            <span style='color:#007BFF;'>CRM</span>_modun
        </div>
        """, 
        unsafe_allow_html=True
    )

    # NÚT ĐIỀU HƯỚNG
    if st.button("📊 Tổng quát", use_container_width=True,
                type=("primary" if st.session_state.page == "Tổng quát" else "secondary")):
        st.session_state.page = "Tổng quát"
        st.rerun()

    if st.button("🔍 Tra cứu", use_container_width=True,
                type=("primary" if st.session_state.page == "Tra cứu" else "secondary")):
        st.session_state.page = "Tra cứu"
        st.rerun()

    if st.button("🎯 Chiến dịch", use_container_width=True,
                type=("primary" if st.session_state.page == "Chiến dịch" else "secondary")):
        st.session_state.page = "Chiến dịch"
        st.rerun()

# Không còn đường kẻ ngang <hr> nữa

# ===============================
# 🧩 5. LOGIC HIỂN THỊ CÁC TRANG (Giữ nguyên)
# ===============================
if st.session_state.page == "Tổng quát":
    Overview.show()

elif st.session_state.page == "Tra cứu":
    if st.session_state.view == "detail":
        lookUpCustomer.show_detail_view()
    else:
        lookUpCustomer.show_list_view()

elif st.session_state.page == "Chiến dịch":
    Campaign.show()