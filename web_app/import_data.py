import streamlit as st
import pandas as pd
import os
from datetime import datetime


def show():
    """Trang Import dữ liệu - Giao diện thân thiện"""

    # ===================================================
    # CUSTOM CSS - THIẾT KẾ THÂN THIỆN
    # ===================================================
    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        /* Header chính */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
        }
        
        .main-header h1 {
            color: white;
            font-size: 28px;
            font-weight: 700;
            margin: 0;
        }
        
        .main-header p {
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
            margin-top: 8px;
        }
        
        /* Step Card */
        .step-card {
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
            border-left: 4px solid #667eea;
        }
        
        .step-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 1rem;
        }
        
        .step-number {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 16px;
        }
        
        .step-title {
            font-size: 18px;
            font-weight: 600;
            color: #1F2937;
            margin: 0;
        }
        
        .step-subtitle {
            font-size: 14px;
            color: #6B7280;
            margin-top: 4px;
        }
        
        /* Option Card */
        .option-card {
            background: #F9FAFB;
            border: 2px solid #E5E7EB;
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .option-card:hover {
            border-color: #667eea;
            background: #F0F4FF;
        }
        
        .option-card.selected {
            border-color: #667eea;
            background: linear-gradient(135deg, #667eea11 0%, #764ba211 100%);
        }
        
        .option-title {
            font-weight: 600;
            color: #1F2937;
            font-size: 15px;
            margin-bottom: 4px;
        }
        
        .option-desc {
            font-size: 13px;
            color: #6B7280;
        }
        
        /* Status Message */
        .status-success {
            background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
            border-left: 4px solid #10B981;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-success .icon {
            font-size: 18px;
        }
        
        .status-success .text {
            color: #065F46;
            font-size: 14px;
            font-weight: 500;
        }
        
        .status-processing {
            background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
            border-left: 4px solid #3B82F6;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-processing .text {
            color: #1E40AF;
            font-size: 14px;
            font-weight: 500;
        }
        
        /* Warning Box */
        .warning-box {
            background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
            border-left: 4px solid #F59E0B;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .warning-box .title {
            font-weight: 600;
            color: #92400E;
            font-size: 14px;
            margin-bottom: 4px;
        }
        
        .warning-box .desc {
            color: #A16207;
            font-size: 13px;
        }
        
        /* Info Box */
        .info-box {
            background: linear-gradient(135deg, #EDE9FE 0%, #DDD6FE 100%);
            border-left: 4px solid #8B5CF6;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .info-box .text {
            color: #5B21B6;
            font-size: 13px;
        }
        
        /* Progress Steps */
        .progress-container {
            background: #F9FAFB;
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 1rem;
        }
        
        .progress-step {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 0.75rem 0;
            border-bottom: 1px solid #E5E7EB;
        }
        
        .progress-step:last-child {
            border-bottom: none;
        }
        
        .progress-icon {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }
        
        .progress-icon.done {
            background: #D1FAE5;
            color: #10B981;
        }
        
        .progress-icon.processing {
            background: #DBEAFE;
            color: #3B82F6;
        }
        
        .progress-icon.waiting {
            background: #F3F4F6;
            color: #9CA3AF;
        }
        
        .progress-text {
            font-size: 14px;
            color: #374151;
        }
        
        /* Result Card */
        .result-card {
            background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            margin: 1.5rem 0;
        }
        
        .result-card h2 {
            color: #065F46;
            font-size: 24px;
            margin-bottom: 0.5rem;
        }
        
        .result-card p {
            color: #047857;
            font-size: 14px;
        }
        
        /* Metric Card */
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }
        
        .metric-card .value {
            font-size: 28px;
            font-weight: 700;
            color: #667eea;
        }
        
        .metric-card .label {
            font-size: 13px;
            color: #6B7280;
            margin-top: 4px;
        }
        
        /* Button Styling */
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
        }
        
        /* File Uploader */
        .stFileUploader > div {
            border-radius: 12px;
        }
        
        /* Dataframe */
        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
        }
    </style>
    """, unsafe_allow_html=True)

    # ===================================================
    # HEADER
    # ===================================================
    st.markdown("""
    <div class="main-header">
        <h1>📥 Thêm Dữ liệu Mới</h1>
        <p>Tải lên file Excel hoặc CSV để cập nhật hệ thống</p>
    </div>
    """, unsafe_allow_html=True)

    # ===================================================
    # BƯỚC 1: CHỌN FILE
    # ===================================================
    st.markdown("""
    <div class="step-card">
        <div class="step-header">
            <div class="step-number">1</div>
            <div>
                <h3 class="step-title">Chọn file dữ liệu</h3>
                <p class="step-subtitle">Hỗ trợ file Excel (.xlsx) hoặc CSV (.csv)</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Kéo thả file vào đây hoặc click để chọn",
        type=['xlsx', 'csv'],
        help="File cần có các cột thông tin khách hàng và đơn hàng",
        label_visibility="collapsed"
    )

    if uploaded_file:
        # Hiển thị thông tin file
        file_size_kb = uploaded_file.size / 1024
        if file_size_kb > 1024:
            file_size_display = f"{file_size_kb / 1024:.1f} MB"
        else:
            file_size_display = f"{file_size_kb:.1f} KB"

        st.markdown(f"""
        <div class="status-success">
            <span class="icon">✅</span>
            <span class="text">Đã chọn: <strong>{uploaded_file.name}</strong> ({file_size_display})</span>
        </div>
        """, unsafe_allow_html=True)

        try:
            # Đọc preview
            if uploaded_file.name.endswith('.csv'):
                df_preview = pd.read_csv(uploaded_file, nrows=10)
            else:
                df_preview = pd.read_excel(uploaded_file, nrows=10)

            # Hiển thị thống kê
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="value">{len(df_preview.columns)}</div>
                    <div class="label">Số cột dữ liệu</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="value">10</div>
                    <div class="label">Dòng xem trước</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            with st.expander("👀 Xem trước dữ liệu", expanded=True):
                st.dataframe(df_preview, use_container_width=True,
                             hide_index=True)

            uploaded_file.seek(0)

        except Exception as e:
            st.error(f"❌ Không thể đọc file. Vui lòng kiểm tra lại định dạng file.")
            return

        # ===================================================
        # BƯỚC 2: CHỌN CÁCH XỬ LÝ
        # ===================================================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="step-card">
            <div class="step-header">
                <div class="step-number">2</div>
                <div>
                    <h3 class="step-title">Bạn muốn xử lý dữ liệu như thế nào?</h3>
                    <p class="step-subtitle">Chọn cách thức phù hợp với nhu cầu của bạn</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        import_mode = st.radio(
            "Chọn cách xử lý:",
            options=[
                "🔄 Làm mới hoàn toàn",
                "➕ Bổ sung thêm",
                "🧠 Tự động cập nhật"
            ],
            captions=[
                "Xóa toàn bộ dữ liệu cũ, thay bằng dữ liệu mới",
                "Giữ nguyên dữ liệu cũ, thêm dữ liệu mới vào cuối",
                "Thông minh: thêm mới nếu chưa có, cập nhật nếu đã tồn tại"
            ],
            label_visibility="collapsed"
        )

        # Xử lý mode và hiển thị thông báo phù hợp
        if "Làm mới hoàn toàn" in import_mode:
            selected_mode = "replace"
            st.markdown("""
            <div class="warning-box">
                <div class="title">⚠️ Lưu ý quan trọng</div>
                <div class="desc">Toàn bộ dữ liệu cũ sẽ bị xóa và thay thế bằng dữ liệu mới. 
                Hãy chắc chắn bạn đã sao lưu dữ liệu nếu cần.</div>
            </div>
            """, unsafe_allow_html=True)
        elif "Bổ sung thêm" in import_mode:
            selected_mode = "append"
            st.markdown("""
            <div class="info-box">
                <div class="text">💡 Dữ liệu mới sẽ được thêm vào sau dữ liệu hiện có. 
                Phù hợp khi bạn muốn bổ sung thêm khách hàng hoặc đơn hàng mới.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            selected_mode = "upsert"
            st.markdown("""
            <div class="info-box">
                <div class="text">🧠 Hệ thống sẽ tự động nhận diện: thêm mới nếu chưa có, 
                cập nhật nếu đã tồn tại. Đây là cách an toàn và thông minh nhất.</div>
            </div>
            """, unsafe_allow_html=True)

        # ===================================================
        # BƯỚC 3: BẮT ĐẦU
        # ===================================================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="step-card">
            <div class="step-header">
                <div class="step-number">3</div>
                <div>
                    <h3 class="step-title">Sẵn sàng chưa?</h3>
                    <p class="step-subtitle">Nhấn nút bên dưới để bắt đầu xử lý dữ liệu</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1.5, 1, 1.5])
        with col1:
            start_import = st.button(
                "🚀 Bắt đầu xử lý",
                type="primary",
                use_container_width=True
            )
        with col2:
            if st.button("🔄 Đặt lại", use_container_width=True):
                st.rerun()

        # ===================================================
        # XỬ LÝ IMPORT
        # ===================================================
        if start_import:
            # Lưu file
            raw_folder = "raw_data"
            if not os.path.exists(raw_folder):
                os.makedirs(raw_folder)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"import_{timestamp}_{uploaded_file.name}"
            file_path = os.path.join(raw_folder, file_name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.markdown(f"""
            <div class="status-success">
                <span class="icon">💾</span>
                <span class="text">File đã được lưu thành công</span>
            </div>
            """, unsafe_allow_html=True)

            # Import ETL
            from etl_core import ETLPipeline

            # Progress container
            progress_container = st.container()
            progress_bar = st.progress(0)
            status_area = st.empty()

            try:
                # Bước 1: Khởi tạo
                status_area.markdown("""
                <div class="status-processing">
                    <span class="icon">⚙️</span>
                    <span class="text">Đang chuẩn bị hệ thống...</span>
                </div>
                """, unsafe_allow_html=True)

                base_dir = os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__)))
                config_path = os.path.join(
                    base_dir, "data_processing", "etl_config.json")

                if not os.path.exists(config_path):
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    config_path = os.path.join(current_dir, "etl_config.json")
                    if not os.path.exists(config_path):
                        parent_dir = os.path.dirname(current_dir)
                        config_path = os.path.join(
                            parent_dir, "etl_config.json")
                        if not os.path.exists(config_path):
                            st.error(
                                "❌ Không tìm thấy file cấu hình hệ thống!")
                            st.stop()

                pipeline = ETLPipeline(config_path=config_path)
                progress_bar.progress(5)

                # Bước 2: Kết nối
                status_area.markdown("""
                <div class="status-processing">
                    <span class="icon">🔗</span>
                    <span class="text">Đang kết nối hệ thống...</span>
                </div>
                """, unsafe_allow_html=True)

                success, msg = pipeline.connect_db()
                if not success:
                    st.error(f"❌ {msg}")
                    st.stop()
                progress_bar.progress(10)

                # Bước 3: Đọc file
                status_area.markdown("""
                <div class="status-processing">
                    <span class="icon">📖</span>
                    <span class="text">Đang đọc và kiểm tra dữ liệu...</span>
                </div>
                """, unsafe_allow_html=True)

                success, msg, df = pipeline.read_and_clean_excel(file_path)
                if not success:
                    st.error(f"❌ {msg}")
                    pipeline.close_db()
                    st.stop()
                progress_bar.progress(20)

                # Bước 4: Xử lý dữ liệu thô
                status_area.markdown("""
                <div class="status-processing">
                    <span class="icon">📥</span>
                    <span class="text">Đang xử lý dữ liệu thô...</span>
                </div>
                """, unsafe_allow_html=True)

                success, msg = pipeline.load_to_staging(mode=selected_mode)
                if not success:
                    st.error(f"❌ {msg}")
                    pipeline.close_db()
                    st.stop()
                progress_bar.progress(35)

                # Bước 5: Tạo bảng phụ trợ
                status_area.markdown("""
                <div class="status-processing">
                    <span class="icon">🏗️</span>
                    <span class="text">Đang tổ chức dữ liệu...</span>
                </div>
                """, unsafe_allow_html=True)

                success, msg = pipeline.create_dimension_tables(
                    mode=selected_mode)
                if not success:
                    st.error(f"❌ {msg}")
                    pipeline.close_db()
                    st.stop()
                progress_bar.progress(50)

                # Bước 6: Tạo bảng chính
                status_area.markdown("""
                <div class="status-processing">
                    <span class="icon">📊</span>
                    <span class="text">Đang tổng hợp dữ liệu...</span>
                </div>
                """, unsafe_allow_html=True)

                success, msg = pipeline.create_fact_table()
                if not success:
                    st.error(f"❌ {msg}")
                    pipeline.close_db()
                    st.stop()
                progress_bar.progress(65)

                # Bước 7: Phân tích RFM
                status_area.markdown("""
                <div class="status-processing">
                    <span class="icon">📈</span>
                    <span class="text">Đang phân tích hành vi khách hàng...</span>
                </div>
                """, unsafe_allow_html=True)

                success, msg, df_rfm = pipeline.calculate_rfm()
                if not success:
                    st.error(f"❌ {msg}")
                    pipeline.close_db()
                    st.stop()
                progress_bar.progress(80)

                # Bước 8: Phân nhóm khách hàng
                status_area.markdown("""
                <div class="status-processing">
                    <span class="icon">🎯</span>
                    <span class="text">Đang phân nhóm khách hàng...</span>
                </div>
                """, unsafe_allow_html=True)

                success, msg, segment_stats = pipeline.kmeans_clustering(
                    df_rfm, auto_k=True)
                if not success:
                    st.error(f"❌ {msg}")
                    pipeline.close_db()
                    st.stop()
                progress_bar.progress(95)

                # Hoàn thành
                pipeline.close_db()
                progress_bar.progress(100)

                # Xóa cache
                st.cache_data.clear()

                # Xóa status processing
                status_area.empty()

                # ===================================================
                # HIỂN THỊ KẾT QUẢ
                # ===================================================
                st.balloons()

                st.markdown("""
                <div class="result-card">
                    <h2>🎉 Hoàn thành!</h2>
                    <p>Dữ liệu đã được xử lý và cập nhật vào hệ thống thành công</p>
                </div>
                """, unsafe_allow_html=True)

                # Thống kê kết quả
                st.markdown("### 📊 Tóm tắt kết quả")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="value">{len(df):,}</div>
                        <div class="label">Dòng dữ liệu đã xử lý</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="value">{len(df_rfm):,}</div>
                        <div class="label">Khách hàng được phân tích</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="value">{pipeline.optimal_k}</div>
                        <div class="label">Nhóm khách hàng</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Phân bổ nhóm khách hàng
                if segment_stats:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("### 👥 Phân bổ nhóm khách hàng")

                    cols = st.columns(len(segment_stats) if len(
                        segment_stats) <= 4 else 4)
                    for idx, (segment_name, count) in enumerate(segment_stats.items()):
                        col_idx = idx % len(cols)
                        with cols[col_idx]:
                            st.metric(
                                label=f"🏷️ {segment_name}",
                                value=f"{count:,}"
                            )

                # Hướng dẫn tiếp theo
                st.markdown("---")
                st.markdown("""
                <div class="info-box">
                    <div class="text">💡 <strong>Tiếp theo:</strong> Bạn có thể xem Dashboard để theo dõi 
                    tổng quan hoặc Tra cứu để tìm kiếm thông tin khách hàng cụ thể.</div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 Xem Dashboard", type="primary", use_container_width=True):
                        st.session_state.page = "Tổng quát"
                        st.rerun()
                with col2:
                    if st.button("🔍 Tra cứu khách hàng", use_container_width=True):
                        st.session_state.page = "Tra cứu"
                        st.rerun()

            except Exception as e:
                st.error(f"❌ Có lỗi xảy ra: {str(e)}")
                st.exception(e)
                if 'pipeline' in locals():
                    pipeline.close_db()

    else:
        # Chưa upload file
        st.markdown("""
        <div class="info-box">
            <div class="text">📌 Chọn file Excel hoặc CSV ở trên để bắt đầu. 
            File cần chứa thông tin khách hàng và đơn hàng.</div>
        </div>
        """, unsafe_allow_html=True)

        # Hướng dẫn định dạng file
        with st.expander("📋 Hướng dẫn định dạng file", expanded=False):
            st.markdown("""
            **File của bạn nên có các cột sau:**
            
            | Cột | Mô tả | Ví dụ |
            |-----|-------|-------|
            | HoTen | Tên khách hàng | Nguyễn Văn A |
            | Email | Email liên hệ | nguyenvana@email.com |
            | SDT | Số điện thoại | 0901234567 |
            | DonHang | Mã đơn hàng | DH001 |
            | NgayMua | Ngày mua hàng | 2024-01-15 |
            | SKU | Mã sản phẩm | SP001 |
            | TenSanPham | Tên sản phẩm | Giày Nike Air |
            | DoanhThuThuan | Doanh thu | 1500000 |
            
            💡 **Lưu ý:** Tên cột có thể khác nhưng cần có đủ các thông tin cơ bản trên.
            """)
