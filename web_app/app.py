import streamlit as st
import Overview
import lookUpCustomer
import Campaign
import import_data
import home  

def init_session_state():
    defaults = {
        "page": "Home", 
        "view": "list",
        "selected_customer_id": None,
        "search_term": "",
        "sidebar_collapsed": False,
        "show_animation": True
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def apply_custom_css():
    """
    CSS tùy chỉnh với thiết kế hiện đại và sidebar có thể toggle
    """
    sidebar_width = "80px" if st.session_state.sidebar_collapsed else "280px"
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}
        
        header[data-testid="stHeader"],
        footer[data-testid="stFooter"] {{
            visibility: hidden;
            height: 0px;
            margin: 0px;
            padding: 0px;
        }}
        
        .main .block-container {{ 
            padding-top: 1rem !important; 
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 1400px;
            margin: 0 auto;
        }}

        /* Sidebar styling với gradient */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 50%, #334155 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            padding-top: 1.5rem;
            width: {sidebar_width} !important;
            min-width: {sidebar_width} !important;
            max-width: {sidebar_width} !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 4px 0 20px rgba(0,0,0,0.15);
        }}
        
        [data-testid="stSidebar"] > div:first-child {{
            width: {sidebar_width} !important;
            transition: all 0.3s ease-in-out;
        }}
        
        /* Toggle button */
        .toggle-btn {{
            position: fixed;
            left: {sidebar_width};
            top: 20px;
            width: 35px;
            height: 35px;
            background-color: #3b82f6;
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
            background-color: #2563eb;
            transform: translateX(2px);
        }}

        /* === STYLE NÚT ĐIỀU HƯỚNG TRONG SIDEBAR === */
        button[data-testid="baseButton-secondary"],
        button[data-testid="baseButton-primary"] {{
            border-radius: 12px !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: none !important;
            height: 48px !important; 
            width: 100% !important;
            display: flex;
            align-items: center;
            justify-content: flex-start !important;
            padding-left: 20px !important;
            white-space: nowrap;
            overflow: hidden;
            margin-bottom: 6px;
            position: relative;
        }}
        
        /* Nút phụ (không được chọn) */
        button[data-testid="baseButton-secondary"] {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: rgba(255, 255, 255, 0.85) !important;
        }}
        
        button[data-testid="baseButton-secondary"]:hover {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: #ffffff !important;
            transform: translateX(3px);
        }}
        
        /* Nút chính (đang được chọn) */
        button[data-testid="baseButton-primary"] {{
            background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
        }}
        
        button[data-testid="baseButton-primary"]::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 3px;
            height: 65%;
            background-color: #60a5fa;
            border-radius: 0 3px 3px 0;
        }}
        
        /* Sidebar collapsed styles */
        .sidebar-collapsed .menu-text {{
            display: none;
        }}
        
        .sidebar-collapsed button[data-testid="baseButton-secondary"],
        .sidebar-collapsed button[data-testid="baseButton-primary"] {{
            justify-content: center !important;
            padding-left: 0 !important;
            font-size: 1.3rem !important;
        }}
        
        /* Animations */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .animate-fade-in {{
            animation: fadeInUp 0.5s ease-out;
        }}
        
        /* Card styles */
        .modern-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            transition: all 0.3s ease;
            border: 1px solid #e5e7eb;
        }}
        
        .modern-card:hover {{
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        
        /* Gradient text */
        .gradient-text {{
            background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }}
        
        /* Custom metrics */
        [data-testid="metric-container"] {{
            background: white;
            padding: 16px;
            border-radius: 10px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        
        [data-testid="metric-container"] label {{
            color: #6b7280 !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
        }}
        
        [data-testid="metric-container"] [data-testid="stMetricValue"] {{
            color: #111827 !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }}
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #f3f4f6;
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: #9ca3af;
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: #6b7280;
        }}
        
        </style>
        """, unsafe_allow_html=True)

# Cấu hình trang
st.set_page_config(
    page_title="CRM Module - Hệ thống quản lý khách hàng",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Khởi tạo session state
init_session_state()

# Áp dụng custom CSS
apply_custom_css()

# Sidebar Navigation
with st.sidebar:
    # Toggle button
    col1, col2 = st.columns([1, 5])
    with col1:
        toggle_label = "◀" if not st.session_state.sidebar_collapsed else "▶"
        if st.button(toggle_label, key="toggle_sidebar", help="Thu gọn/Mở rộng menu"):
            st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed
            st.rerun()
    
    st.markdown("---")
    
    # Logo và tên app
    if not st.session_state.sidebar_collapsed:
        st.markdown(
            """
            <div style='text-align: center; padding-bottom: 2rem;'>
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            width: 60px; height: 60px; border-radius: 12px; 
                            display: flex; align-items: center; justify-content: center;
                            margin: 0 auto 15px; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);'>
                    <span style='font-size: 1.8rem;'>📊</span>
                </div>
                <div style='color: #ffffff; font-size: 1.4rem; font-weight: 700;'>CRM Module</div>
                <div style='color: rgba(255,255,255,0.6); font-size: 0.75rem; margin-top: 5px;'>
                    Quản lý khách hàng thông minh
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style='display: flex; align-items: center; justify-content: center; padding-bottom: 2rem;'>
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            width: 45px; height: 45px; border-radius: 10px; 
                            display: flex; align-items: center; justify-content: center;'>
                    <span style='font-size: 1.5rem;'>📊</span>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Navigation buttons với icons
    nav_items = [
        {"name": "Home", "icon": "🏠", "label": "Trang chủ"},
        {"name": "Tổng quát", "icon": "📊", "label": "Dashboard"},
        {"name": "Tra cứu", "icon": "🔍", "label": "Tra cứu KH"},
        {"name": "Chiến dịch", "icon": "🎯", "label": "Chiến dịch"},
        {"name": "Import", "icon": "📥", "label": "Import dữ liệu"},
    ]
    
    for item in nav_items:
        btn_text = item["icon"] if st.session_state.sidebar_collapsed else f"{item['icon']} {item['label']}"
        if st.button(
            btn_text, 
            use_container_width=True,
            type=("primary" if st.session_state.page == item["name"] else "secondary"),
            key=f"nav_{item['name'].lower().replace(' ', '_')}"
        ):
            st.session_state.page = item["name"]
            st.session_state.show_animation = True
            st.rerun()
    
    # Footer trong sidebar
    if not st.session_state.sidebar_collapsed:
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; padding: 20px 10px;'>
                <div style='color: rgba(255,255,255,0.5); font-size: 0.7rem;'>
                     CRM Module - Phát triển bởi  Nguyen Thi Ngoc Bich
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Main content area
if st.session_state.page == "Home":
    home.show()
elif st.session_state.page == "Tổng quát":
    Overview.show()
elif st.session_state.page == "Tra cứu":
    if st.session_state.view == "detail":
        lookUpCustomer.show_detail_view()
    else:
        lookUpCustomer.show_list_view()
elif st.session_state.page == "Chiến dịch":
    Campaign.show()
elif st.session_state.page == "Import":
    import_data.show()