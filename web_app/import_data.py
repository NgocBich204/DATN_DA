import streamlit as st
import pandas as pd
import os
from datetime import datetime


def show():
    """Trang Import dữ liệu"""
    st.title("📥 Import Dữ liệu vào Hệ thống")
    st.markdown("---")
    st.subheader("📂 Bước 1: Chọn file Excel")
    uploaded_file = st.file_uploader(
        "Chọn file .xlsx hoặc .csv",
        type=['xlsx', 'csv'],
        help="File phải chứa các cột: HoTen, Email, SDT, DonHang, NgayMua, SKU, TenSanPham, DoanhThuThuan..."
    )
    if uploaded_file:
        st.success(
            f"✅ File: **{uploaded_file.name}** ({uploaded_file.size / 1024:.2f} KB)")
        try:
            if uploaded_file.name.endswith('.csv'):
                df_preview = pd.read_csv(uploaded_file, nrows=10)
            else:
                df_preview = pd.read_excel(uploaded_file, nrows=10)

            st.info(
                f"📊 Số cột: **{len(df_preview.columns)}** | Preview 10 dòng đầu:")
            st.dataframe(df_preview, use_container_width=True)
            uploaded_file.seek(0)
        except Exception as e:
            st.error(f"❌ Lỗi đọc file: {e}")
            return
        st.markdown("---")
        st.subheader("⚙️ Bước 2: Chọn chế độ import")
        import_mode = st.radio(
            "Chọn cách xử lý dữ liệu:",
            options=[
                "🗑️ Xóa dữ liệu cũ và thay thế hoàn toàn (Replace)",
                "➕ Chỉ thêm dữ liệu mới (Append)",
                "🔄 Cập nhật thông minh (Upsert)"
            ],
            help="""
            - Replace: Xóa tất cả dữ liệu cũ, import dữ liệu mới hoàn toàn
            - Append: Giữ dữ liệu cũ, thêm dữ liệu mới vào
            - Upsert: Cập nhật nếu đã tồn tại, thêm mới nếu chưa có
            """
        )
        if "Replace" in import_mode:
            selected_mode = "replace"
            st.warning("⚠️ **Cảnh báo:** Tất cả dữ liệu hiện tại sẽ bị xóa!")
        elif "Append" in import_mode:
            selected_mode = "append"
            st.info("ℹ️ Dữ liệu mới sẽ được thêm vào, dữ liệu cũ được giữ nguyên")
        else:
            selected_mode = "upsert"
            st.info("ℹ️ Dữ liệu sẽ được cập nhật thông minh (update + insert)")
        st.markdown("---")
        st.subheader("🚀 Bước 3: Bắt đầu import")
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            start_import = st.button(
                "🚀 Bắt đầu Import", type="primary", use_container_width=True)
        with col2:
            if st.button("🔄 Làm mới", use_container_width=True):
                st.rerun()
        if start_import:
            raw_folder = "raw_data"
            if not os.path.exists(raw_folder):
                os.makedirs(raw_folder)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"import_{timestamp}_{uploaded_file.name}"
            file_path = os.path.join(raw_folder, file_name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ File đã lưu vào: `{file_path}`")
            from etl_core import ETLPipeline
            progress_container = st.container()
            status_text = st.empty()
            progress_bar = st.progress(0)
            try:
                status_text.info("🔧 Đang khởi tạo ETL Pipeline...")
                base_dir = os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__)))
                config_path = os.path.join(
                    base_dir, "data_processing", "etl_config.json")
                if not os.path.exists(config_path):
                    st.error(
                        f"❌ Không tìm thấy file config tại: {config_path}")
                    st.info("📍 Đang thử tìm ở vị trí khác...")
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    config_path = os.path.join(current_dir, "etl_config.json")
                    if not os.path.exists(config_path):
                        parent_dir = os.path.dirname(current_dir)
                        config_path = os.path.join(
                            parent_dir, "etl_config.json")
                        if not os.path.exists(config_path):
                            st.error(
                                "❌ Không tìm thấy file etl_config.json ở bất kỳ vị trí nào!")
                            st.info(
                                f"📍 Đã tìm kiếm tại:\n- {os.path.join(base_dir, 'data_processing', 'etl_config.json')}\n- {os.path.join(current_dir, 'etl_config.json')}\n- {os.path.join(parent_dir, 'etl_config.json')}")
                            st.stop()
                st.success(f"✅ Đã tìm thấy config: {config_path}")
                pipeline = ETLPipeline(config_path=config_path)
                progress_bar.progress(5)
                status_text.info("🔗 Đang kết nối database...")
                success, msg = pipeline.connect_db()
                if not success:
                    st.error(msg)
                    st.stop()
                st.success(msg)
                progress_bar.progress(10)
                status_text.info("📖 Đang đọc và làm sạch dữ liệu...")
                success, msg, df = pipeline.read_and_clean_excel(file_path)
                if not success:
                    st.error(msg)
                    pipeline.close_db()
                    st.stop()
                st.success(msg)
                progress_bar.progress(20)
                status_text.info("📥 Đang load dữ liệu vào Staging table...")
                success, msg = pipeline.load_to_staging(mode=selected_mode)
                if not success:
                    st.error(msg)
                    pipeline.close_db()
                    st.stop()
                st.success(msg)
                progress_bar.progress(35)
                status_text.info("🏗️ Đang tạo Dimension tables...")
                success, msg = pipeline.create_dimension_tables(
                    mode=selected_mode)
                if not success:
                    st.error(msg)
                    pipeline.close_db()
                    st.stop()
                st.success(msg)
                progress_bar.progress(50)
                status_text.info("📊 Đang tạo Fact table...")
                success, msg = pipeline.create_fact_table()
                if not success:
                    st.error(msg)
                    pipeline.close_db()
                    st.stop()
                st.success(msg)
                progress_bar.progress(65)
                status_text.info("📈 Đang tính toán RFM...")
                success, msg, df_rfm = pipeline.calculate_rfm()
                if not success:
                    st.error(msg)
                    pipeline.close_db()
                    st.stop()
                st.success(msg)
                progress_bar.progress(80)
                # Bước 7: Phân cụm KMeans
                status_text.info("🎯 Đang phân cụm khách hàng với KMeans...")
                success, msg, segment_stats = pipeline.kmeans_clustering(
                    df_rfm, auto_k=True)
                if not success:
                    st.error(msg)
                    pipeline.close_db()
                    st.stop()
                st.success(msg)
                progress_bar.progress(95)
                # Đóng kết nối
                pipeline.close_db()
                progress_bar.progress(100)

                # ========== 🔥 PHẦN MỚI: XÓA CACHE & HIỂN THỊ THÔNG BÁO ==========
                status_text.success("✅ **Import hoàn thành!**")

                # 🔥 DÒNG QUAN TRỌNG NHẤT - Xóa cache cũ
                st.cache_data.clear()

                # 🎉 Hiệu ứng celebration
                st.balloons()

                # 📢 Thông báo chi tiết
                st.markdown("---")
                st.success(
                    "🎉 **IMPORT THÀNH CÔNG!**\n\n"
                    "Dữ liệu mới đã được:\n"
                    "✅ Lưu vào Database\n"
                    "✅ Xóa cache Streamlit\n"
                    "✅ Sẵn sàng hiển thị trên các trang khác"
                )

                # 📊 Kết quả Import
                st.markdown("---")
                st.subheader("📊 Kết quả Import")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        label="📈 Số dòng dữ liệu",
                        value=f"{len(df):,}"
                    )
                with col2:
                    st.metric(
                        label="👥 Số khách hàng",
                        value=f"{len(df_rfm):,}"
                    )
                with col3:
                    st.metric(
                        label="🏷️ Số phân khúc",
                        value=pipeline.optimal_k
                    )

                # Phân bổ phân khúc
                st.markdown("---")
                st.markdown("### 👥 Phân bổ khách hàng theo phân khúc:")

                if segment_stats:
                    # Hiển thị phân khúc dạng metrics (đẹp hơn)
                    cols = st.columns(len(segment_stats) if len(
                        segment_stats) <= 4 else 4)
                    for idx, (segment_name, count) in enumerate(segment_stats.items()):
                        col_idx = idx % len(cols)
                        with cols[col_idx]:
                            st.metric(
                                label=f"🏷️ {segment_name}",
                                value=f"{count:,}"
                            )

                # ========== 🔥 PHẦN MỚI: HƯỚNG DẪN & NÚT CHUYỂN TRANG ==========
                st.markdown("---")
                st.info(
                    "💡 Các trang khác sẽ tự động cập nhật dữ liệu mới "
                    "khi bạn truy cập lần tới. Cache đã được làm mới!"
                )

                # Nút chuyển trang với khuyến nghị
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 Xem Dashboard (dữ liệu mới)",
                                 type="primary", use_container_width=True,
                                 help="Dashboard sẽ tự động tải dữ liệu vừa import"):
                        st.session_state.page = "Tổng quát"
                        st.rerun()

                with col2:
                    if st.button("🔍 Tra cứu khách hàng (dữ liệu mới)",
                                 use_container_width=True,
                                 help="Tra cứu sẽ tự động tải dữ liệu vừa import"):
                        st.session_state.page = "Tra cứu"
                        st.rerun()

            except Exception as e:
                st.error(f"❌ Lỗi trong quá trình xử lý: {str(e)}")
                st.exception(e)
                if 'pipeline' in locals():
                    pipeline.close_db()
    else:
        st.info("📌 Vui lòng upload file Excel để bắt đầu")
