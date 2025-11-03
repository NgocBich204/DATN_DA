import streamlit as st
import Overview
import lookUpCustomer
import Campaign
def init_session_state():
    defaults = {
        "page": "Tổng quát",
        "view": "list",
        "selected_customer_id": None,
        "search_term": "",
        "sidebar_collapsed": False 
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()
def apply_custom_css():
    """
    CSS tùy chỉnh với sidebar có thể toggle
    """
    sidebar_width = "80px" if st.session_state.sidebar_collapsed else "290px"
    
    st.markdown(f"""
        <style>
        /* Ẩn header và footer mặc định của Streamlit */
        header[data-testid="stHeader"],
        footer[data-testid="stFooter"] {{
            visibility: hidden;
            height: 0px;
            margin: 0px;
            padding: 0px;
        }}
        .main .block-container {{ 
            padding-top: 0.5rem !important; 
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            padding-bottom: 2rem !important;
        }}

        [data-testid="stSidebar"] {{
            background-color: #FFFFFF;
            border-right: 1px solid #E0E0E0;
            padding-top: 1.5rem;
            width: {sidebar_width} !important;
            min-width: {sidebar_width} !important;
            max-width: {sidebar_width} !important;
            transition: all 0.3s ease-in-out;
        }}
        
        [data-testid="stSidebar"] > div:first-child {{
            width: {sidebar_width} !important;
            transition: all 0.3s ease-in-out;
        }}
        .toggle-btn {{
            position: fixed;
            left: {sidebar_width};
            top: 20px;
            width: 40px;
            height: 40px;
            background-color: #007BFF;
            border: none;
            border-radius: 0 8px 8px 0;
            cursor: pointer;
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 2px 0 10px rgba(0,0,0,0.2);
            transition: all 0.3s ease-in-out;
        }}
        
        .toggle-btn:hover {{
            background-color: #0056b3;
            width: 45px;
        }}

        /* === STYLE NÚT ĐIỀU HƯỚNG TRONG SIDEBAR === */
        button[data-testid="baseButton-secondary"],
        button[data-testid="baseButton-primary"] {{
            border-radius: 8px !important;
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            transition: all 0.2s ease-in-out;
            border-width: 2px !important;
            height: 50px !important; 
            width: 100% !important;
            display: flex;
            align-items: center;
            justify-content: flex-start !important;
            padding-left: 20px !important;
            white-space: nowrap;
            overflow: hidden;
        }}
        
        /* Nút phụ (không được chọn) */
        button[data-testid="baseButton-secondary"] {{
            background-color: transparent !important;
            border-color: transparent !important;
            color: #495057 !important;
        }}
        button[data-testid="baseButton-secondary"]:hover {{
             background-color: #F8F9FA !important;
             color: #007BFF !important;
        }}
        
        /* Nút chính (đang được chọn) */
        button[data-testid="baseButton-primary"] {{
            background-color: #E6F2FF !important;
            border-color: #007BFF !important;
            color: #007BFF !important;
        }}
        .sidebar-collapsed .menu-text {{
            display: none;
        }}
        
        .sidebar-collapsed button[data-testid="baseButton-secondary"],
        .sidebar-collapsed button[data-testid="baseButton-primary"] {{
            justify-content: center !important;
            padding-left: 0 !important;
            font-size: 1.5rem !important;
        }}
        
        </style>
        """, unsafe_allow_html=True)
st.set_page_config(
    page_title="CRM_modun",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_custom_css()
with st.sidebar:
    col1, col2 = st.columns([1, 4])
    with col1:
        toggle_label = "◀" if not st.session_state.sidebar_collapsed else "▶"
        if st.button(toggle_label, key="toggle_sidebar", help="Thu gọn/Mở rộng menu"):
            st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed
            st.rerun()
    st.markdown("---")
    if not st.session_state.sidebar_collapsed:
        st.markdown(
            """
            <div style='display: flex; align-items: center; font-size: 2rem; font-weight: 700; color: #1E1E1E; padding-left: 20px; padding-bottom: 1.5rem;'>
                <img src="https://emojicdn.elk.sh/📚?style=twitter" width="40" height="40" style="margin-right: 10px;">
                <span style='color:#007BFF;'>CRM</span>_modun
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style='display: flex; align-items: center; justify-content: center; padding-bottom: 1rem;'>
                <img src="https://emojicdn.elk.sh/📚?style=twitter" width="60" height="45">
            </div>
            """, 
            unsafe_allow_html=True
        )
    btn_text_1 = "📊" if st.session_state.sidebar_collapsed else "📊 Tổng quát"
    if st.button(btn_text_1, use_container_width=True,
                type=("primary" if st.session_state.page == "Tổng quát" else "secondary"),
                key="nav_overview"):
        st.session_state.page = "Tổng quát"
        st.rerun()

    # Nút Tra cứu
    btn_text_2 = "🔍" if st.session_state.sidebar_collapsed else "🔍 Tra cứu"
    if st.button(btn_text_2, use_container_width=True,
                type=("primary" if st.session_state.page == "Tra cứu" else "secondary"),
                key="nav_lookup"):
        st.session_state.page = "Tra cứu"
        st.rerun()

    # Nút Chiến dịch
    btn_text_3 = "🎯" if st.session_state.sidebar_collapsed else "🎯 Chiến dịch"
    if st.button(btn_text_3, use_container_width=True,
                type=("primary" if st.session_state.page == "Chiến dịch" else "secondary"),
                key="nav_campaign"):
        st.session_state.page = "Chiến dịch"
        st.rerun()
if st.session_state.page == "Tổng quát":
    Overview.show()

elif st.session_state.page == "Tra cứu":
    if st.session_state.view == "detail":
        lookUpCustomer.show_detail_view()
    else:
        lookUpCustomer.show_list_view()

elif st.session_state.page == "Chiến dịch":
    Campaign.show()
