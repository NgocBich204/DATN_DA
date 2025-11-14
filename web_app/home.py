import streamlit as st
import time
from datetime import datetime
import random

def show():
    # Animation effect
    if st.session_state.get('show_animation', True):
        with st.spinner(''):
            time.sleep(0.2)
        st.session_state.show_animation = False
    
    # Hero Section với gradient background
    st.markdown("""
        <div class="animate-fade-in" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     border-radius: 20px; padding: 50px; margin-bottom: 30px; color: white;">
            <div style="text-align: center;">
                <h1 style="font-size: 3rem; font-weight: 800; margin-bottom: 20px; color: white;">
                    Chào mừng đến với CRM Module
                </h1>
                <p style="font-size: 1.2rem; opacity: 0.95; max-width: 700px; margin: 0 auto 30px; line-height: 1.6;">
                    Giải pháp quản lý khách hàng toàn diện - Tối ưu hóa quy trình bán hàng, 
                    nâng cao trải nghiệm khách hàng và thúc đẩy tăng trưởng doanh thu
                </p>
                <div style="display: flex; gap: 15px; justify-content: center;">
                    <button style="
                        background: white;
                        color: #667eea;
                        border: none;
                        padding: 12px 30px;
                        border-radius: 8px;
                        font-size: 1rem;
                        font-weight: 600;
                        cursor: pointer;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    ">🚀 Bắt đầu ngay</button>
                    <button style="
                        background: transparent;
                        color: white;
                        border: 2px solid white;
                        padding: 12px 30px;
                        border-radius: 8px;
                        font-size: 1rem;
                        font-weight: 600;
                        cursor: pointer;
                    ">📖 Hướng dẫn</button>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Main Features Section
    st.markdown("""
        <h2 style="text-align: center; font-size: 2.2rem; font-weight: 700; margin: 40px 0;">
            Tính năng <span class="gradient-text">nổi bật</span>
        </h2>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="modern-card" style="text-align: center; padding: 30px; min-height: 280px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); 
                                 width: 70px; height: 70px; border-radius: 15px; 
                                 display: flex; align-items: center; justify-content: center;
                                 margin: 0 auto 20px; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);">
                        <span style="font-size: 2rem;">📊</span>
                    </div>
                    <h3 style="color: #1f2937; font-size: 1.2rem; margin-bottom: 12px;">Dashboard</h3>
                </div>
                <p style="color: #6b7280; font-size: 0.9rem; line-height: 1.5;">
                    Theo dõi KPIs quan trọng, phân tích xu hướng và đưa ra quyết định với Power BI
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="modern-card" style="text-align: center; padding: 30px; min-height: 280px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); 
                                 width: 70px; height: 70px; border-radius: 15px; 
                                 display: flex; align-items: center; justify-content: center;
                                 margin: 0 auto 20px; box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);">
                        <span style="font-size: 2rem;">🔍</span>
                    </div>
                    <h3 style="color: #1f2937; font-size: 1.2rem; margin-bottom: 12px;">Phân Tích RFM</h3>
                </div>
                <p style="color: #6b7280; font-size: 0.9rem; line-height: 1.5;">
                    Phân khúc khách hàng tự động bằng AI, tìm kiếm thông minh và quản lý profile chi tiết
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="modern-card" style="text-align: center; padding: 30px; min-height: 280px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                                 width: 70px; height: 70px; border-radius: 15px; 
                                 display: flex; align-items: center; justify-content: center;
                                 margin: 0 auto 20px; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);">
                        <span style="font-size: 2rem;">🎯</span>
                    </div>
                    <h3 style="color: #1f2937; font-size: 1.2rem; margin-bottom: 12px;">Chiến Dịch Tự Động</h3>
                </div>
                <p style="color: #6b7280; font-size: 0.9rem; line-height: 1.5;">
                    Tạo và quản lý chiến dịch marketing đa kênh, tự động hóa quy trình và đo lường ROI
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Workflow Section
    st.markdown("""
        <div style="background: #f9fafb; border-radius: 16px; padding: 30px; margin: 30px 0;">
            <h2 style="text-align: center; font-size: 1.8rem; font-weight: 700; margin-bottom: 30px;color: black">
                🔄 Quy trình làm việc
            </h2>
            <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
                <div style="text-align: center; flex: 1; min-width: 150px;">
                    <div style="background: white; width: 60px; height: 60px; border-radius: 50%; 
                                 display: flex; align-items: center; justify-content: center; margin: 0 auto 10px;
                                 box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <span style="font-size: 1.5rem;">📥</span>
                    </div>
                    <div style="font-weight: 600; color: #1f2937;">1. Import Data</div>
                    <div style="color: #6b7280; font-size: 0.85rem;">Excel, CSV, API</div>
                </div>
                <div style="color: #cbd5e1; font-size: 2rem;">→</div>
                <div style="text-align: center; flex: 1; min-width: 150px;">
                    <div style="background: white; width: 60px; height: 60px; border-radius: 50%; 
                                 display: flex; align-items: center; justify-content: center; margin: 0 auto 10px;
                                 box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <span style="font-size: 1.5rem;">🔗</span>
                    </div>
                    <div style="font-weight: 600; color: #1f2937;">2. ETL & AI</div>
                    <div style="color: #6b7280; font-size: 0.85rem;">Clean & Analyze</div>
                </div>
                <div style="color: #cbd5e1; font-size: 2rem;">→</div>
                <div style="text-align: center; flex: 1; min-width: 150px;">
                    <div style="background: white; width: 60px; height: 60px; border-radius: 50%; 
                                 display: flex; align-items: center; justify-content: center; margin: 0 auto 10px;
                                 box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <span style="font-size: 1.5rem;">📊</span>
                    </div>
                    <div style="font-weight: 600; color: #1f2937;">3. Visualize</div>
                    <div style="color: #6b7280; font-size: 0.85rem;">Dashboard & Reports</div>
                </div>
                <div style="color: #cbd5e1; font-size: 2rem;">→</div>
                <div style="text-align: center; flex: 1; min-width: 150px;">
                    <div style="background: white; width: 60px; height: 60px; border-radius: 50%; 
                                 display: flex; align-items: center; justify-content: center; margin: 0 auto 10px;
                                 box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <span style="font-size: 1.5rem;">🎯</span>
                    </div>
                    <div style="font-weight: 600; color: #1f2937;">4. Action</div>
                    <div style="color: #6b7280; font-size: 0.85rem;">Campaigns & Sales</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("""
        <h2 style="font-size: 1.8rem; font-weight: 700; margin: 30px 0 20px;">
            ⚡ Truy cập nhanh
        </h2>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Xem Dashboard", use_container_width=True, key="quick_dashboard"):
            st.session_state.page = "Tổng quát"
            st.rerun()
    
    with col2:
        if st.button("📥 Import dữ liệu", use_container_width=True, key="quick_import"):
            st.session_state.page = "Import"
            st.rerun()
    
    with col3:
        if st.button("🔍 Tra cứu KH", use_container_width=True, key="quick_search"):
            st.session_state.page = "Tra cứu"
            st.rerun()
    
    with col4:
        if st.button("🎯 Tạo chiến dịch", use_container_width=True, key="quick_campaign"):
            st.session_state.page = "Chiến dịch"
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1]) 
   
            
    with col2:
        # Khối Mẹo sử dụng
        st.markdown("""
            <div class="modern-card" style="background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);">
                <h3 style="color: white; font-size: 1.2rem; margin-bottom: 15px;">
                    💡 Mẹo sử dụng
                </h3>
                <button style="
                    margin-top: 15px;
                    background: white;
                    color: #f59e0b;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-size: 0.85rem;
                    font-weight: 600;
                    cursor: pointer;
                    width: 100%;
                ">Tìm hiểu thêm →</button>
            </div>
        """, unsafe_allow_html=True)
    
    with col1:
        # Khối Mẹo sử dụng
        st.markdown("""
            <div class="modern-card" style="background: linear-gradient(180deg, #FCFCFC, #A0A0A0)">
                <h3 style="color: white; font-size: 1.2rem; margin-bottom: 15px;">
                    💬 Chat Support
                </h3>
                <button style="
                    margin-top: 15px;
                    background: white;
                    color: #f59e0b;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-size: 0.85rem;
                    font-weight: 600;
                    cursor: pointer;
                    width: 100%;
                ">📞 Cần hỗ trợ?  →</button>
            </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
        <div style="margin-top: 50px; padding: 20px 0; border-top: 1px solid #e5e7eb; text-align: center;">
            <p style="color: #6b7280; font-size: 0.85rem;">
                © 2025 CRM Module - Phát triển bởi Nguyen Thi Ngoc Bich 
            </p>
            <div style="margin-top: 10px;">
                <a href="#" style="color: #3b82f6; text-decoration: none; margin: 0 10px; font-size: 0.85rem;">📚 Tài liệu</a>
                <a href="#" style="color: #3b82f6; text-decoration: none; margin: 0 10px; font-size: 0.85rem;">🎥 Video hướng dẫn</a>
                <a href="#" style="color: #3b82f6; text-decoration: none; margin: 0 10px; font-size: 0.85rem;">📧 ngocbichnguyen.zf@gmail.com</a>
            </div>
        </div>
    """, unsafe_allow_html=True)
