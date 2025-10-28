import streamlit as st
import Overview
import lookUpCustomer
import Campaign

# ===============================
# ⚙️ 1. KHỞI TẠO SESSION STATE
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
# 🎨 2. HÀM CSS TÙY CHỈNH GIAO DIỆN
# ===============================
def apply_custom_css():
    """Injects custom CSS for layout refinement and removing Streamlit defaults."""
    st.markdown("""
        <style>
        .st-emotion-cache-dev9y0 {
            visibility: hidden;
            height: 0px !important;
            position: absolute; 
            overflow: hidden;
        }
        .st-emotion-cache-1pxx76n, .main .block-container { 
            padding-top: 0px !important; 
            margin-top: 0px !important; 
        }
        .st-emotion-cache-16ya5l3 { 
            visibility: hidden;
            height: 0px;
            margin: 0px;
            padding: 0px;
        }
        button {
            border-radius: 8px !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            transition: all 0.2s ease-in-out;
            border-width: 2px !important;
            height: 60px; 
            display: flex;
            align-items: center;
            justify-content: center;
        }
        button[data-testid="baseButton-secondary"] {
            background-color: transparent !important;
            border-color: #3d4a5b !important; 
            color: #C2C5CB !important;
        }
        button[data-testid="baseButton-primary"] {
            background-color: #E54D5B !important;
            border-color: #E54D5B !important;
            color: white !important;
            box-shadow: 0 4px 10px rgba(229, 77, 91, 0.4);
        }
        hr {
            border: none;
            border-top: 1px solid #3d4a5b;
            margin-bottom: 0px;
        }
        .st-emotion-cache-1r6r8u4 {
            align-items: center; 
            padding-top: 5px;
            padding-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

# ===============================
# 🧭 3. CẤU HÌNH TRANG STREAMLIT
# ===============================
st.set_page_config(
    page_title="CRM Modun",
    page_icon="📚",
    layout="wide"
)
apply_custom_css()

# ===============================
# 🧭 4. THANH ĐIỀU HƯỚNG
# ===============================
with st.container():
    cols = st.columns([2.5, 1, 1, 1])
    # LOGO + TIÊU ĐỀ
    with cols[0]:
        st.markdown(
            """
            <div style='display: flex; align-items: center; font-size: 2.2rem; font-weight: 700; color: white;'>
                <img src="https://emojicdn.elk.sh/📚?style=twitter" width="40" height="40" style="margin-right: 10px;">
                <span style='color:#E54D5B;'>CRM</span>_modun
            </div>
            """, 
            unsafe_allow_html=True
        )
    # NÚT ĐIỀU HƯỚNG
    with cols[1]:
        if st.button("Tổng quát", use_container_width=True,
                     type=("primary" if st.session_state.page == "Tổng quát" else "secondary")):
            st.session_state.page = "Tổng quát"
            st.rerun()
    with cols[2]:
        if st.button("Tra cứu", use_container_width=True,
                     type=("primary" if st.session_state.page == "Tra cứu" else "secondary")):
            st.session_state.page = "Tra cứu"
            st.rerun()
    with cols[3]:
        if st.button("Chiến dịch", use_container_width=True,
                     type=("primary" if st.session_state.page == "Chiến dịch" else "secondary")):
            st.session_state.page = "Chiến dịch"
            st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

# ===============================
# 🧩 5. LOGIC HIỂN THỊ CÁC TRANG
# ===============================
if st.session_state.page == "Tổng quát":
    Overview.show()

elif st.session_state.page == "Tra cứu":
    # ✅ Giữ nguyên trạng thái để “Xem chi tiết” hoạt động đúng
    if st.session_state.view == "detail":
        lookUpCustomer.show_detail_view()
    else:
        lookUpCustomer.show_list_view()

elif st.session_state.page == "Chiến dịch":
    Campaign.show()
