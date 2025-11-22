import streamlit as st
import streamlit.components.v1 as components
import time
from datetime import datetime


def show():
    # ===================================================
    # CUSTOM CSS - PREMIUM DESIGN
    # ===================================================
    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles */
        * {
            font-family: 'Inter', sans-serif;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Main container */
        .main > div {
            padding-top: 2rem;
            padding-bottom: 0;
        }
        
        /* Custom Header Bar */
        .custom-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header-title {
            color: white;
            font-size: 28px;
            font-weight: 700;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .header-subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
            font-weight: 400;
            margin-top: 4px;
        }
        
        /* Status Bar */
        .status-bar {
            background: white;
            padding: 1rem 2rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }
        
        .status-label {
            font-size: 12px;
            color: #6B7280;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-value {
            font-size: 20px;
            font-weight: 700;
            color: #1F2937;
        }
        
        /* Refresh Button - Floating */
        .refresh-floating {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 9999;
        }
        
        .refresh-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 50%;
            width: 64px;
            height: 64px;
            font-size: 28px;
            cursor: pointer;
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .refresh-btn:hover {
            transform: translateY(-4px) scale(1.05);
            box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5);
        }
        
        .refresh-btn:active {
            transform: translateY(-2px) scale(0.98);
        }
        
        /* Spinning animation */
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .spinning {
            animation: spin 0.8s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        }
        
        /* Dashboard Container */
        .dashboard-container {
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
            position: relative;
        }
        
        /* Loading Overlay */
        .loading-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.95);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        
        .loading-spinner {
            width: 60px;
            height: 60px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        /* Metric Cards */
        .metric-card {
            background: white;
            padding: 1.25rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: all 0.3s;
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
        }
        
        /* Success Toast */
        .success-toast {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10B981;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(16, 185, 129, 0.3);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        /* Expander Styling */
        .streamlit-expanderHeader {
            background: linear-gradient(90deg, #667eea11 0%, #764ba211 100%);
            border-radius: 8px;
            font-weight: 600;
        }
        
        /* Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
        }
        
        /* Info Box */
        .info-box {
            background: linear-gradient(135deg, #667eea11 0%, #764ba211 100%);
            border-left: 4px solid #667eea;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

    # ===================================================
    # SESSION STATE MANAGEMENT
    # ===================================================
    if 'refresh_count' not in st.session_state:
        st.session_state.refresh_count = 0
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    if 'is_loading' not in st.session_state:
        st.session_state.is_loading = False

    # ===================================================
    # CUSTOM HEADER
    # ===================================================
    st.markdown("""
    <div class="custom-header">
        <div>
            <h1 class="header-title">
                <span>📊</span> Dashboard Phân Tích Khách Hàng
            </h1>
            <p class="header-subtitle">Hệ thống CRM thông minh với Power BI</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ===================================================
    # STATUS BAR WITH METRICS
    # ===================================================
    current_time = datetime.now().strftime("%H:%M:%S")
    time_since_refresh = int(time.time() - st.session_state.last_refresh)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="status-label">⏰  hiện tại</div>
            <div class="status-value">{current_time}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="status-label">🔄 Lần Refresh</div>
            <div class="status-value">{st.session_state.refresh_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="status-label">📡 Cập nhật</div>
            <div class="status-value">{time_since_refresh}s trước</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        status_color = "#10B981" if time_since_refresh < 60 else "#F59E0B"
        status_text = "Online" if time_since_refresh < 60 else "Cần refresh"
        st.markdown(f"""
        <div class="metric-card">
            <div class="status-label">🟢 Trạng thái</div>
            <div class="status-value" style="color: {status_color};">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        if st.button("🔄 Refresh Ngay",  type="primary"):
            with st.spinner("⏳ Đang cập nhật dữ liệu..."):
                time.sleep(1)  # Simulate loading
                st.session_state.refresh_count += 1
                st.session_state.last_refresh = time.time()
                st.success("✅ Cập nhật thành công!")
                time.sleep(1)
                st.rerun()

    # ===================================================
    # QUICK ACTIONS BAR
    # ===================================================
    st.markdown("<br>", unsafe_allow_html=True)

    # Timestamp để force reload
    timestamp = int(time.time() * 1000)

    components.html(
        f"""
        <html>
        <head>
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
                height: 100%;
                background: #f8f9fa;
            }}
            
            .dashboard-wrapper {{
                position: relative;
                width: 100%;
                height: 100%;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
            }}
            
            iframe {{
                width: 100%;
                height: 100vh;
                border: none;
                background: white;
            }}
            
            .loading-overlay {{
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(255, 255, 255, 0.98);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                z-index: 1000;
            }}
            
            .loading-spinner {{
                width: 60px;
                height: 60px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                animation: spin 1s cubic-bezier(0.4, 0, 0.2, 1) infinite;
            }}
            
            .loading-text {{
                margin-top: 20px;
                color: #667eea;
                font-size: 16px;
                font-weight: 600;
            }}
            
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            
            @keyframes fadeOut {{
                from {{ opacity: 1; }}
                to {{ opacity: 0; }}
            }}
        </style>
        </head>
        <body>
            <div class="dashboard-wrapper">
                <!-- Loading Overlay -->
                <div class="loading-overlay" id="loading">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">⏳ Đang tải dashboard...</div>
                </div>
                
                <!-- Power BI Iframe -->
                <iframe 
                    id="powerbi-frame"
                    title="dashboard_crm_v1" 
                    src="https://app.powerbi.com/reportEmbed?reportId=5a2d5b8c-dc57-4b6f-9f8f-96e577b47f88&autoAuth=true&ctid=6ac2ad06-692c-4663-b7af-a9ff2a866d0c&actionBarEnabled=true&t={timestamp}" 
                    frameborder="0" 
                    allowFullScreen="true">
                </iframe>
            </div>
            
            <script>
                const iframe = document.getElementById('powerbi-frame');
                const loading = document.getElementById('loading');
                
                // Hide loading when iframe loads
                iframe.addEventListener('load', function() {{
                    setTimeout(() => {{
                        loading.style.animation = 'fadeOut 0.5s ease-out';
                        setTimeout(() => {{
                            loading.style.display = 'none';
                        }}, 500);
                    }}, 1000);
                }});
                
                // Handle errors
                iframe.addEventListener('error', function() {{
                    loading.innerHTML = `
                        <div style="text-align: center;">
                            <div style="font-size: 48px;">⚠️</div>
                            <div style="color: #EF4444; margin-top: 20px; font-weight: 600;">
                                Không thể tải dashboard
                            </div>
                            <div style="color: #6B7280; margin-top: 10px; font-size: 14px;">
                                Vui lòng kiểm tra kết nối hoặc thử lại sau
                            </div>
                        </div>
                    `;
                }});
                
                // Refresh function
                function refreshDashboard() {{
                    loading.style.display = 'flex';
                    loading.style.animation = '';
                    const currentSrc = iframe.src.split('&t=')[0];
                    const newTimestamp = new Date().getTime();
                    iframe.src = currentSrc + '&t=' + newTimestamp;
                }}
            </script>
        </body>
        </html>
        """,
        height=850,
        scrolling=False,
    )

    # ===================================================
    # SETTINGS PANEL (COLLAPSIBLE)
    # ===================================================
    st.markdown("<br><br>", unsafe_allow_html=True)

    with st.expander("⚙️ Cài đặt nâng cao", expanded=False):
        settings_col1, settings_col2 = st.columns(2)

        with settings_col1:
            st.markdown("### 🔄 Tự động refresh")
            auto_refresh = st.toggle("Bật tự động refresh", value=False)

            if auto_refresh:
                refresh_interval = st.slider(
                    "Khoảng thời gian (giây)",
                    min_value=30,
                    max_value=300,
                    value=60,
                    step=30
                )
                st.info(
                    f"⏰ Dashboard sẽ tự động refresh sau mỗi **{refresh_interval}s**")

                # Auto refresh logic
                time.sleep(refresh_interval)
                st.session_state.refresh_count += 1
                st.session_state.last_refresh = time.time()
                st.rerun()

        with settings_col2:
            st.markdown("### 🔔 Thông báo")
            notify_on_refresh = st.toggle("Thông báo khi refresh", value=True)
            notify_sound = st.toggle("Âm thanh thông báo", value=False)

            st.markdown("### 📊 Hiển thị")
            show_metrics = st.toggle("Hiển thị metrics", value=True)
            dark_mode = st.toggle("Chế độ tối (coming soon)",
                                  value=False, disabled=True)


# ===================================================
# MAIN FUNCTION
