import streamlit as st
import Overview
import lookUpCustomer
import Campaign

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="CRM Modun",
    page_icon="📚",
    layout="wide"
)

# --- TRẠNG THÁI ỨNG DỤNG ---
if 'page' not in st.session_state:
    st.session_state.page = "Tổng quát"

# --- HEADER + ĐIỀU HƯỚNG ---
cols = st.columns([3, 1, 1, 1], vertical_alignment="bottom")

with cols[0]:
    st.title("📚 CRM_modun")

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

st.divider()

# --- HIỂN THỊ TRANG THEO CHỌN ---
if st.session_state.page == "Tổng quát":
    Overview.show()

elif st.session_state.page == "Tra cứu":
    # Gọi đúng hàm trong lookUpCustomer
    if 'view' not in st.session_state or st.session_state.view == 'list':
        lookUpCustomer.show_list_view()
    else:
        lookUpCustomer.show_detail_view()

elif st.session_state.page == "Chiến dịch":
    Campaign.show()
