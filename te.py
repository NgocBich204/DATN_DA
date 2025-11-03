"""
🎯 CODE SNIPPETS ĐỂ CẬP NHẬT BƯỚC 3 & 4
Sao chép các đoạn code này vào file hiện tại của bạn
"""

# ============================================================================
# PHẦN 1: CẬP NHẬT config_data (Thay thế toàn bộ phần objectives)
# ============================================================================

config_data = {
    "objectives": [
        {
            'id': 'revenue', 
            'icon': '💰', 
            'title': 'Tối ưu hóa Doanh thu',
            'description': 'Tập trung vào khách hàng ĐÃ CHỨNG MINH khả năng chi tiêu cao',
            'color': '#10B981',
            'segments_owned': ['Khách hàng VIP', 'Khách hàng trung thành'],
            'why': '✅ Đã có lịch sử mua hàng tốt → Dễ bán\n✅ Tỷ lệ chuyển đổi cao (25-40%)\n✅ AOV cao gấp 3-5 lần khách thường\n✅ Chi phí marketing thấp'
        },
        {
            'id': 'awareness', 
            'icon': '🚀', 
            'title': 'Tăng Nhận diện & Tương tác',
            'description': 'Tái kích hoạt khách hàng NGỪNG MUA để giảm tỷ lệ churn',
            'color': '#F59E0B',
            'segments_owned': ['Khách hàng có nguy cơ mất', 'Khách hàng yếu'],
            'why': '❗ Đang trong giai đoạn "nguy hiểm"\n❗ Chi phí giữ chân < Chi phí tìm khách mới (1/5-1/7)\n❗ Tỷ lệ khôi phục: 15-30% nếu làm đúng'
        },
        {
            'id': 'conversion', 
            'icon': '🎯', 
            'title': 'Gia tăng Tỷ lệ Chuyển đổi',
            'description': 'Chuyển đổi khách TIỀM NĂNG thành khách THỰC SỰ',
            'color': '#3B82F6',
            'segments_owned': ['Khách hàng mới', 'Khách hàng tiềm năng'],
            'why': '🚀 Tăng tỷ lệ mua lần 2 từ 15% → 40%\n🚀 Giảm rào cản mua hàng\n🚀 Xây dựng thói quen mua'
        },
        {
            'id': 'launch', 
            'icon': '✨', 
            'title': 'Ra mắt Sản phẩm Mới',
            'description': 'Tận dụng khách hàng TRUNG THÀNH để tạo buzz',
            'color': '#8B5CF6',
            'segments_owned': ['Khách hàng VIP', 'Khách hàng trung thành'],
            'why': '✨ Tạo FOMO và social proof\n✨ Bán được 40-60% stock ngay đầu\n✨ VIP là early adopters tốt nhất'
        }
    ],
    
    # Thêm tactics_owned (Copy từ file đầy đủ - xem HUONG_DAN_CAP_NHAT.md)
    "tactics_owned": {
        # ... (Đã có trong file chi tiết)
    },
    
    # Thêm tactics_marketplace
    "tactics_marketplace": {
        'revenue': [
            {
                'id': 'mp_voucher_light',
                'name': '🎟️ Voucher Giảm giá Nhẹ (10-15%)',
                'desc': 'Khách Giàu mua vì CHẤT LƯỢNG, voucher chỉ là "trigger"',
                'benefit': '💎 Giữ biên lợi nhuận 85-90%',
                'roi': '600-900%',
                'cost': '10-15% giá trị đơn',
                'kpi': 'Conversion 15-25%, AOV ~800k'
            },
            # ... thêm các tactics khác
        ],
        # ... các objectives khác
    }
}

# ============================================================================
# PHẦN 2: CẬP NHẬT render_step_3() - Hiển thị WHY + Metrics
# ============================================================================

def render_step_3():
    """Bước 3 MỚI với logic WHY và metrics đầy đủ"""
    st.button("⬅️ Quay lại", on_click=go_to_step, args=(2,), key="back_to_step2")
    
    # Lấy objective đã chọn
    selected_obj = next((obj for obj in config_data["objectives"] 
                        if obj['id'] == st.session_state.selected_objective['id']), None)
    
    if not selected_obj:
        st.error("Không tìm thấy mục tiêu!")
        return
    
    # Header với màu theo objective
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {selected_obj['color']} 0%, {selected_obj['color']}dd 100%);
                padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem;'>
        <h2 style='margin:0;'>{selected_obj['icon']} Bước 3: Đề xuất Phân khúc</h2>
        <p style='margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
            Mục tiêu: <strong>{selected_obj['title']}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Hiển thị WHY statement
    with st.container(border=True):
        st.markdown("### 💡 Tại sao chọn phân khúc này?")
        st.markdown(selected_obj['why'])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Load data phân khúc
    df_real = st.session_state.real_segment_data
    segment_names = selected_obj['segments_owned']
    segments_to_show = df_real[df_real['PhanKhuc'].isin(segment_names)]
    
    # Hiển thị từng phân khúc với metrics đầy đủ
    for _, segment in segments_to_show.iterrows():
        seg_name = segment['PhanKhuc']
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    padding: 2rem; border-radius: 15px; margin-bottom: 1rem;'>
            <h3 style='margin: 0 0 1rem 0;'>👥 {seg_name}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # RFM Metrics với gradient
        rfm_cols = st.columns(3)
        
        with rfm_cols[0]:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 1.5rem; border-radius: 12px; text-align: center; color: white;'>
                <div style='font-size: 12px; margin-bottom: 8px;'>⏱️ RECENCY</div>
                <div style='font-size: 32px; font-weight: bold;'>{segment['R_TB']:.0f}</div>
                <div style='font-size: 11px; margin-top: 8px; opacity: 0.9;'>ngày kể từ lần mua cuối</div>
            </div>
            """, unsafe_allow_html=True)
        
        with rfm_cols[1]:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                        padding: 1.5rem; border-radius: 12px; text-align: center; color: white;'>
                <div style='font-size: 12px; margin-bottom: 8px;'>🔄 FREQUENCY</div>
                <div style='font-size: 32px; font-weight: bold;'>{segment['F_TB']:.1f}</div>
                <div style='font-size: 11px; margin-top: 8px; opacity: 0.9;'>lần giao dịch</div>
            </div>
            """, unsafe_allow_html=True)
        
        with rfm_cols[2]:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                        padding: 1.5rem; border-radius: 12px; text-align: center; color: white;'>
                <div style='font-size: 12px; margin-bottom: 8px;'>💰 MONETARY</div>
                <div style='font-size: 28px; font-weight: bold;'>{format_currency(segment['M_TB'])}</div>
                <div style='font-size: 11px; margin-top: 8px; opacity: 0.9;'>giá trị TB/đơn</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Button chọn phân khúc
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.button(
                f"✓ Chọn phân khúc này →",
                on_click=select_segment,
                args=(seg_name, seg_name),
                use_container_width=True,
                type="primary",
                key=f"seg_{seg_name}"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# PHẦN 3: CẬP NHẬT render_step_4_owned() - Card với metrics đầy đủ
# ============================================================================

def render_step_4_owned():
    """Bước 4 Owned MỚI với metrics business đầy đủ"""
    segment_id = st.session_state.selected_segment['id']
    tactics = config_data["tactics_owned"].get(segment_id, [])
    recommendations = config_data.get("recommendations_owned", {}).get(segment_id, [])
    
    if not tactics:
        st.info("ℹ️ Không có chiến thuật cho phân khúc này.")
        return
    
    st.markdown("### 🌐 Chiến thuật cho Kênh Sở hữu")
    st.caption("Tập trung cá nhân hóa sâu và tự động hóa")
    st.markdown("<br>", unsafe_allow_html=True)
    
    for tactic in tactics:
        is_recommended = tactic['id'] in recommendations
        
        # Card với gradient
        st.markdown(f"""
        <div class='tactic-card' style='
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            border: 2px solid {"#667eea" if is_recommended else "transparent"};
            transition: all 0.3s ease;
        '>
        """, unsafe_allow_html=True)
        
        # Badge recommendation
        if is_recommended:
            st.markdown("""
            <div class='recommended-badge' style='
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 0.4rem 1rem;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: bold;
                display: inline-block;
                margin-bottom: 0.5rem;
            '>⭐ ĐỀ XUẤT</div>
            """, unsafe_allow_html=True)
        
        # Header
        st.markdown(f"### {tactic['name']}")
        st.write(tactic['desc'])
        
        st.divider()
        
        # 4 Metrics quan trọng - 2 cột
        cols = st.columns(2)
        
        with cols[0]:
            st.markdown(f"**{tactic['benefit']}**")
            st.markdown(f"**💰 Chi phí:** {tactic['cost']}")
        
        with cols[1]:
            st.markdown(f"**📊 ROI:** {tactic['roi']}")
            st.markdown(f"**⏱️ Timeline:** {tactic['timeline']}")
        
        st.markdown(f"**🎯 KPI:** {tactic['kpi']}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Button CTA
        st.button(
            "🎨 Thiết Kế Chiến Dịch Này →",
            on_click=select_tactic,
            args=(tactic['id'], tactic['name'], 'owned'),
            use_container_width=True,
            type="primary" if is_recommended else "secondary",
            key=f"tactic_{tactic['id']}"
        )
        
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PHẦN 4: CSS MARKETING THEME - Thêm vào render_header_and_nav()
# ============================================================================

def render_header_and_nav():
    """Header với marketing theme"""
    st.markdown("""
    <style>
    /* Main Header Gradient */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    /* Objective Cards */
    .objective-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }
    
    .objective-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }
    
    /* Tactic Cards */
    .tactic-card {
        transition: all 0.3s ease;
    }
    
    .tactic-card:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    
    /* Recommended Badge */
    .recommended-badge {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Progress Bar Enhancement */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style='margin:0; font-size: 2.5rem;'>🎯 Module Chiến Lược Marketing AI</h1>
        <p style='margin:0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.95;'>
            Vận hành chiến lược marketing cá nhân hóa đa kênh dựa trên RFM
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    cols = st.columns(2)
    # ... rest of navigation code

# ============================================================================
# LƯU Ý QUAN TRỌNG
# ============================================================================

"""
📌 HƯỚNG DẪN SỬ DỤNG:

1. Copy config_data mới (có thêm color, why, segments_owned)
2. Copy render_step_3() hoàn toàn mới
3. Copy render_step_4_owned() với card mới
4. Copy CSS vào render_header_and_nav()
5. Test từng bước một

📚 Tham khảo đầy đủ trong:
- HUONG_DAN_CAP_NHAT.md
- CODE_SUMMARY.md
- File code đầy đủ: campaign_marketing_updated.py

💡 Tips:
- Backup code cũ trước khi thay đổi
- Test sau mỗi phần copy
- Kiểm tra CSS rendering
- Verify database connection
"""