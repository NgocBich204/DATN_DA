import streamlit as st
from streamlit_option_menu import option_menu

# Ẩn thanh Deploy 
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden !important;}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
/* ====== Tổng thể ====== */
body, [data-testid="stAppViewContainer"] {
    background-color: #0f1b2b !important;
    color: #cfd8e3 !important;
    font-family: "Segoe UI", "Inter", sans-serif !important;
}

/* ====== Sidebar ====== */
[data-testid="stSidebar"] {
    background-color: #0e1621 !important;
    width: 260px !important;
    padding-top: 0px !important;
}

.sidebar-logo-title {
    display: flex;
    align-items: center;
    margin-left: 10px;
    margin-bottom: 1px;
    margin-top: -70px !important;
}
.sidebar-logo-title span {
    font-size: 24px;
    margin-right: 8px;
}
.sidebar-title-text {
    font-size: 20px;
    font-weight: 600;
    color: #fff;
    font-family: "Segoe UI", "Inter", sans-serif;
    letter-spacing: 0.5px;
}

/* ====== Menu ====== */
.nav-link {
    font-size: 13px !important;
    color: #cfd8e3 !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    margin: 6px 0 !important;
    padding: 8px 10px !important;
}
.nav-link:hover {
    background-color: #16263c !important;
}
.nav-link-selected {
    background-color: #29C5BC !important;
    color: #fff !important;
    font-weight: 600 !important;
    box-shadow: 0 0 10px rgba(41,197,188,0.4);
}
.option-menu-container {
    background-color: transparent !important;
}

/* ====== Header chính ====== */
.header-container {
    background-color: #0e1621;
    padding: 15px 25px;
    border-bottom: 1px solid #1e2b3c;
}
.header-title {
    color: #ffffff;
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 4px;
}
.header-subtitle {
    color: #8fa3c0;
    font-size: 14px;
}

/* ====== Main Content ====== */
.main .block-container {
    padding: 0 !important;
    margin: 0 !important;
}

/* ====== Iframe Fullscreen ====== */
.fullscreen-iframe {
    position: fixed;
    top: 0px; /* không chừa header vì đã ẩn thanh Deploy */
    left: 260px; /* chừa sidebar */
    width: calc(100% - 260px);
    height: 100vh;
    border: none;
    background-color: #0f1b2b;
}
</style>
""", unsafe_allow_html=True)
with st.sidebar:
    st.markdown(
        '<div class="sidebar-logo-title">'
        '<span>📊</span>'
        '<div class="sidebar-title-text">Modum-CRM</div>'
        '</div>',
        unsafe_allow_html=True
    )

    selected = option_menu(
        menu_title=None,
        options=["Tổng Quan", "Phân Tích Phân Khúc", "Hồ Sơ Khách Hàng", "Chiến Lược & Hành Động"],
        icons=["activity", "bar-chart", "user", "target"],
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "#29C5BC", "font-size": "18px"},
            "nav-link": {"text-align": "left", "margin": "4px 0"},
            "nav-link-selected": {"background-color": "#29C5BC", "color": "white"},
        }
    )

def render_header(title, subtitle):
    st.markdown(f"""
    <div class="header-container">
        <div class="header-title">{title}</div>
        <div class="header-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)
if selected == "Tổng Quan":
    render_header("Bảng điều khiển phân tích khách hàng",
                  "Chào mừng trở lại, đây là bức tranh tổng quan về dữ liệu của bạn.")
    st.markdown(
        """
        <iframe class="fullscreen-iframe"
            title="modun_crm_customer"
            src="https://app.powerbi.com/view?r=eyJrIjoiOTg2NjJjMWEtN2YwYS00NTYwLWFkNzktM2MwYzlmYTk1ZmU0IiwidCI6IjZhYzJhZDA2LTY5MmMtNDY2My1iN2FmLWE5ZmYyYTg2NmQwYyIsImMiOjEwfQ%3D%3D&pageName=03ece3ab73482998a992"
            allowFullScreen="true"></iframe>
        """,
        unsafe_allow_html=True
    )

elif selected == "Phân Tích Phân Khúc":
    render_header("Phân tích phân khúc khách hàng",
                  "Khám phá hành vi và giá trị từng nhóm khách hàng của bạn.")
    st.markdown(
        """
        <iframe class="fullscreen-iframe"
            title="modun_crm_customer"
            src="https://app.powerbi.com/view?r=eyJrIjoiOTg2NjJjMWEtN2YwYS00NTYwLWFkNzktM2MwYzlmYTk1ZmU0IiwidCI6IjZhYzJhZDA2LTY5MmMtNDY2My1iN2FmLWE5ZmYyYTg2NmQwYyIsImMiOjEwfQ%3D%3D&pageName=26bd0bdb2879320d049b"
            allowFullScreen="true"></iframe>
        """,
        unsafe_allow_html=True
    )

elif selected == "Hồ Sơ Khách Hàng":
    render_header("Hồ sơ khách hàng 360°",
                  "Thông tin toàn diện về từng khách hàng, lịch sử và tương tác.")
    st.write("🧾 Trang đang được phát triển...")

elif selected == "Chiến Lược & Hành Động":
    render_header("Chiến lược & hành động marketing",
                  "Đề xuất chiến dịch và phân tích hiệu quả theo từng phân khúc.")
    st.write("🚀 Trang đang được phát triển...")
