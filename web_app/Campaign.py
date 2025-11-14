import streamlit as st
import datetime
import pandas as pd
import pyodbc
import json
import numpy as np
import smtplib
import ssl
from email.message import EmailMessage
import base64
from io import BytesIO
from PIL import Image
from segment_reasoning_logic import SegmentReasoningEngine
odbc_driver = "ODBC Driver 17 for SQL Server"
server = "localhost\\SQLEXPRESS"
database = "test6"
encrypt = "yes"
trust_server_certificate = "yes"

conn_str = (
    f"Driver={{{odbc_driver}}};"
    f"Server={server};"
    f"Database={database};"
    "Trusted_Connection=yes;"
    f"Encrypt={encrypt};"
    f"TrustServerCertificate={trust_server_certificate};"
)
config_data = {
    "objectives": [
        {
            'id': 'revenue',
            'icon': '💰',
            'title': 'Tối ưu hóa cho Doanh thu',
            'description': 'Tập trung vào nhóm khách hàng có khả năng chi tiêu cao, giúp tối đa hóa doanh thu và nâng cao hiệu quả lợi nhuận bền vững.',
            'color': '#10B981',
            'segments_owned': ['Khách hàng VIP', 'Khách hàng trung thành'],
            'why': '1.🎯 Đã có lịch sử mua hàng tốt nên dễ bán\n\n2.📊 Tỷ lệ chuyển đổi cao (25-40%)\n\n3.💎 AOV cao gấp 3-5 lần khách thường\n4.💰 Chi phí marketing thấp (chỉ email)\n\n5.⚡ Không cần ads, automation 100%\n\n6.🚀 ROI cao nhất: 400-600%'
        },
        {
            'id': 'awareness',
            'icon': '🚀',
            'title': 'Tăng Nhận diện Tương tác',
            'description': 'Tái kích hoạt khách hàng ngừng mua để giảm tỷ lệ rời bỏ bên tăng tương tác và khôi phục nguồn doanh thu tiềm năng .',
            'color': '#F59E0B',  # Màu cam
            'segments_owned': ['Khách hàng có nguy cơ mất', 'Khách hàng yếu'],
            'why': '❗ Đang trong giai đoạn "nguy hiểm" (sắp mất vĩnh viễn)\n❗ Từng mua → Có nhu cầu, chỉ cần lý do để quay lại\n❗ Chi phí giữ chân < Chi phí tìm khách mới (1/5 - 1/7)\n❗ Tỷ lệ khôi phục: 15-30% nếu làm đúng'
        },
        {
            'id': 'conversion',
            'icon': '🎯',
            'title': 'Gia tăng Tỷ lệ Chuyển đổi',
            'description': 'Chuyển đổi khách hàng tiềm năng thành khách hàng thực sự bằng cách giảm rào cản và tăng niềm tin bền vững hơn cho khách hàng',
            'color': '#3B82F6',  # Màu xanh dương
            'segments_owned': ['Khách hàng mới', 'Khách hàng tiềm năng'],
            'why': '🚀 Tăng tỷ lệ mua lần 2 từ 15% → 40% (critical milestone)\n🚀 Giảm rào cản mua hàng (giá, trust, urgency)\n🚀 Xây dựng thói quen mua hàng'
        },
        {
            'id': 'launch',
            'icon': '✨',
            'title': 'Ra mắt Sản phẩm Mới',
            'description': 'Tận dụng khách hàng trung thành để tạo hiệu ứng lan tỏa mạnh mẽ, gia tăng uy tín thương hiệu và chứng thực cho sản phẩm mới.',
            'color': '#8B5CF6',  # Màu tím
            'segments_owned': ['Khách hàng VIP', 'Khách hàng trung thành'],
            'why': '✨ Tạo FOMO cực mạnh\n✨ VIP cảm thấy được trân trọng\n✨ Bán được 40-60% stock ngay giai đoạn đầu\n✨ Có UGC + review sớm'
        }
    ],

    "mockDataOwned": {
        "segments": {
            'revenue': ['Khách hàng VIP', 'Khách hàng trung thành'],
            'conversion': ['Khách hàng mới', 'Khách hàng tiềm năng'],
            'awareness': ['Khách hàng có nguy cơ mất', 'Khách hàng yếu'],
            'launch': ['Khách hàng VIP', 'Khách hàng trung thành']
        },

        "tactics": {
            'Khách hàng VIP': {
                'owned': [
                    {
                        'id': 'privilege',
                        'name': '👑 Chương trình Đặc quyền (VIP Club)',
                        'desc': 'Tạo hệ thống tier VIP (Silver, Gold, Platinum) với quyền lợi riêng biệt cho từng cấp độ',
                        'benefit': '💎 Tăng CLV 35-50%',
                        'roi': '400-600%',
                        'cost': 'Thấp: 2-5 triệu/tháng (quà tặng sinh nhật, voucher)',
                        'timeline': '2-3 tuần thiết lập',
                        'kpi': 'Tỷ lệ mua lại trong 90 ngày >60%, AOV +25%, Retention >80%'
                    },
                    {
                        'id': 'upsell_email',
                        'name': '📧 Chiến dịch Upsell Cá nhân hóa',
                        'desc': 'Email tự động đề xuất sản phẩm cao cấp hơn dựa trên lịch sử 3 sản phẩm mua nhiều nhất',
                        'benefit': '💎 Tăng AOV 30-50% mỗi đơn',
                        'roi': '800-1200%',
                        'cost': 'Rất thấp: Chỉ chi phí email (0 VNĐ)',
                        'timeline': '1 tuần automation',
                        'kpi': 'CTR >15%, Conversion >8%, Revenue per email >500k'
                    },
                    {
                        'id': 'referral',
                        'name': '🤝 Chương trình Giới thiệu (Referral)',
                        'desc': 'Biến khách VIP thành đại sứ thương hiệu với link giới thiệu riêng và phần thưởng bậc thang',
                        'benefit': '💎 CAC giảm 70%',
                        'roi': '300-500%',
                        'cost': 'Trung bình: 5-10% doanh thu từ khách mới',
                        'timeline': '2 tuần',
                        'kpi': 'Số referral/VIP >2, Conversion referral >25%, LTV khách referral >20M'
                    }
                ],
                'marketplace': []
            },

            'Khách hàng trung thành': {
                'owned': [
                    {
                        'id': 'onboarding_advanced',
                        'name': '📧 Chuỗi Email Onboarding Nâng cao',
                        'desc': 'Series 5 email trong 30 ngày để đẩy họ lên VIP tier bằng cách tăng tần suất + giá trị đơn hàng',
                        'benefit': '💎 Tăng tần suất mua từ 3 → 5 lần/năm',
                        'roi': '600-800%',
                        'cost': 'Rất thấp (automation)',
                        'timeline': '1 tuần setup',
                        'kpi': 'Open rate >35%, Click rate >12%, Conversion >8%'
                    },
                    {
                        'id': 'cross_sell',
                        'name': '🎁 Chiến dịch Bán chéo (Cross-sell)',
                        'desc': 'Đề xuất category bổ sung dựa trên AI phân tích. Combo 3 món giảm 20%',
                        'benefit': '💎 Tăng AOV 40-60%',
                        'roi': '400-700%',
                        'cost': 'Thấp (giảm giá 20% nhưng bán được 3 món)',
                        'timeline': '1 tuần',
                        'kpi': 'Tỷ lệ add-to-cart combo >20%, Tỷ lệ mua combo 15-25%'
                    },
                    {
                        'id': 'early_access',
                        'name': '⏰ Flash Sale Riêng (VIP Early Access)',
                        'desc': 'Khách Trung thành được mua TRƯỚC 24-48h trong các đợt Sale lớn (11.11, Black Friday)',
                        'benefit': '💎 Tăng Loyalty +35%',
                        'roi': '500-900%',
                        'cost': 'Thấp (chỉ ưu tiên thời gian)',
                        'timeline': '2-3 ngày',
                        'kpi': 'Conversion rate >30%, AOV tăng 45%'
                    }
                ],
                'marketplace': []
            },

            'Khách hàng mới': {
                'owned': [
                    {
                        'id': 'onboarding',
                        'name': '🎯 Chuỗi Email Onboarding',
                        'desc': 'Series 4 email: Ngày 1 (Cảm ơn), Ngày 3 (Tips), Ngày 7 (Mã 15%), Ngày 14 (FOMO)',
                        'benefit': '💎 Tỷ lệ mua lần 2 tăng từ 15% → 40%',
                        'roi': '800-1500%',
                        'cost': 'Rất thấp (automation)',
                        'timeline': '1 tuần',
                        'kpi': 'Second purchase rate >40%'
                    },
                    {
                        'id': 'web_welcome',
                        'name': '🌟 Web Popup Welcome',
                        'desc': 'Popup chào mừng với mã giảm 15% cho lần truy cập thứ 2 sau khi đã mua',
                        'benefit': '💎 Conversion tăng 35%',
                        'roi': '600-1000%',
                        'cost': 'Rất thấp',
                        'timeline': '3-5 ngày',
                        'kpi': 'Popup conversion >10%, Giảm tỷ lệ bỏ giỏ hàng 25%'
                    }
                ],
                'marketplace': []
            },

            'Khách hàng tiềm năng': {
                'owned': [
                    {
                        'id': 'abandoned_cart',
                        'name': '🛒 Abandoned Cart Email',
                        'desc': 'Series 3 email: Sau 2h (nhắc nhở), 24h (mã 10%), 48h (mã 15% + urgency)',
                        'benefit': '💎 Khôi phục 30-40% doanh thu bỏ lỡ',
                        'roi': '500-900%',
                        'cost': 'Thấp',
                        'timeline': '1 tuần',
                        'kpi': 'Cart recovery rate >30%, Conversion 25-35%'
                    }
                ],
                'marketplace': []
            },

            'Khách hàng có nguy cơ mất': {
                'owned': [
                    {
                        'id': 'win_back',
                        'name': '💌 Chiến dịch Win-back "Chúng tôi nhớ bạn"',
                        'desc': 'Series 3 email trong 21 ngày với voucher 25%: Ngày 1 (Quan tâm), Ngày 7 (Xin lỗi + voucher), Ngày 14 (Last chance)',
                        'benefit': '💎 Tỷ lệ khôi phục 20-30%',
                        'roi': '250-400%',
                        'cost': 'Trung bình (voucher 25%)',
                        'timeline': '1 tuần',
                        'kpi': 'Reactivation rate >20%, Email open rate cao (curiousity)'
                    },
                    {
                        'id': 'remarketing_multi',
                        'name': '🎯 Remarketing Đa nền tảng',
                        'desc': 'Kết hợp Email + Facebook Ads + Google Ads + Zalo OA để tiếp cận đa điểm chạm',
                        'benefit': '💎 Tăng brand recall 60%',
                        'roi': '200-350%',
                        'cost': 'Cao (ads budget 500k-1M)',
                        'timeline': '3-5 ngày',
                        'kpi': 'CTR >3%, ROAS >400%, Tỷ lệ chuyển đổi tốt hơn ads thường 5-7 lần'
                    },
                    {
                        'id': 'survey',
                        'name': '📋 Khảo sát Khách hàng',
                        'desc': 'Thu thập feedback với voucher 50k. Khảo sát 5 câu hỏi về lý do không quay lại',
                        'benefit': '💎 Thu thập insight chất lượng',
                        'roi': 'Không trực tiếp, nhưng giá trị insight vô giá',
                        'cost': 'Thấp (50k x số người tham gia)',
                        'timeline': '1 tuần',
                        'kpi': 'Response rate >15%, Tỷ lệ hoàn thành 15-25%'
                    }
                ],
                'marketplace': []
            },

            'Khách hàng yếu': {
                'owned': [
                    {
                        'id': 'last_chance',
                        'name': '💥 "LAST CHANCE" Win-back',
                        'desc': 'Email duy nhất với offer 50% OFF + Freeship trong 24h. Reverse psychology: "Lần cuối"',
                        'benefit': '💎 Tỷ lệ khôi phục 10-15%',
                        'roi': '50-150% (thấp nhưng có hơn mất hoàn toàn)',
                        'cost': 'Cao (50% discount)',
                        'timeline': '1 ngày',
                        'kpi': 'Reactivation >10%. Nếu không mua → Xóa khỏi list'
                    }
                ],
                'marketplace': []
            }
        },

        "tacticRecommendations": {
            'Khách hàng VIP': ['privilege', 'upsell_email', 'referral'],
            'Khách hàng trung thành': ['onboarding_advanced', 'cross_sell', 'early_access'],
            'Khách hàng mới': ['onboarding', 'web_welcome'],
            'Khách hàng tiềm năng': ['abandoned_cart'],
            'Khách hàng có nguy cơ mất': ['win_back', 'remarketing_multi'],
            'Khách hàng yếu': ['last_chance']
        }
    },

    "mockDataMarketplace": {
        "tactics": {
            'owned': [],
            'marketplace': [
                {
                    'id': 'mp_ads',
                    'name': '📱 Quảng cáo trả phí (Ads)',
                    'desc': 'Tiếp thị lại hoặc tìm kiếm khách hàng mới qua Shopee/Lazada Ads',
                    'benefit': '💎 Tiếp cận 1000-5000 KH/ngày',
                    'roi': '300-500%',
                    'cost': '500k-5M/ngày',
                    'kpi': 'CTR 2-4%, CPC, ROAS, CAC 30-50k/khách'
                },
                {
                    'id': 'mp_flash_sale',
                    'name': '⚡ Flash Sale Khủng (40-60% OFF)',
                    'desc': 'Kích hoạt khách hàng nguy cơ mất. Giá giảm sâu = Động lực MẠNH',
                    'benefit': '💎 Traffic tăng 300-500%',
                    'roi': '100-200%',
                    'cost': 'Cao (discount 40-60% + hoa hồng + phí tham gia)',
                    'kpi': 'Sold out rate 80-100%, New followers +200-500'
                },
                {
                    'id': 'mp_voucher',
                    'name': '🎟️ Voucher / Coupon',
                    'desc': 'Công cụ linh hoạt cho mọi phân khúc. 10-15% cho VIP, 30% cho KH mới',
                    'benefit': '💎 Tăng conversion 25-40%',
                    'roi': '400-900%',
                    'cost': '10-30% giá trị đơn',
                    'kpi': 'Redemption rate >40%, Conversion rate 15-25%'
                },
                {
                    'id': 'mp_livestream',
                    'name': '📹 Livestream Bán hàng',
                    'desc': 'Tương tác trực tiếp và chốt đơn. 2h livestream với voucher đột xuất',
                    'benefit': '💎 Doanh thu 40-180M/session',
                    'roi': '300-600%',
                    'cost': 'Cao (Host 2-5M + quà tặng + KM 15%)',
                    'kpi': 'Viewers 500-2000, Orders 50-150, AOV 800k-1.2M'
                },
                {
                    'id': 'mp_combo',
                    'name': '🎁 Combo mua kèm',
                    'desc': 'Tăng giá trị đơn hàng trung bình. Bundle sản phẩm cao cấp hoặc entry-level',
                    'benefit': '💎 AOV tăng 40-120%',
                    'roi': '350-700%',
                    'cost': 'Trung bình (giảm 15-40% tùy combo)',
                    'kpi': 'Bundle take rate 20-50%, LTV tăng'
                }
            ]
        }
    },

    "marketplaceLogic": {
        'revenue': {  # Khi VIP + Trung thành > 35%
            'recommended': ['mp_voucher', 'mp_combo', 'mp_livestream'],
            'message': '💰 Shop có tỷ lệ khách Giàu cao. Đề xuất: Voucher nhẹ + Combo cao cấp + Livestream premium'
        },
        'awareness': {  # Khi Nguy cơ mất + Yếu > 30%
            'recommended': ['mp_flash_sale', 'mp_voucher', 'mp_livestream'],
            'message': '⚠️ Nguy cơ mất khách cao. Đề xuất: Flash Sale sâu + Voucher lớn + Livestream với ưu đãi'
        },
        'conversion': {  # Khi Mới + Tiềm năng > 40%
            'recommended': ['mp_ads', 'mp_voucher', 'mp_combo'],
            'message': '🚀 Nhiều khách mới. Đề xuất: Ads Lookalike + Voucher mới 30% + Combo giá tốt'
        },
        'launch': {  # Ra mắt sản phẩm mới
            'recommended': ['mp_livestream', 'mp_flash_sale', 'mp_voucher'],
            'message': '✨ Ra mắt SP mới. Đề xuất: Livestream launch + Flash Sale ngày đầu + Voucher pre-order'
        }
    }
}


def image_to_base64(image_file):
    """Chuyển đổi file ảnh upload thành base64 string để lưu vào CSDL"""
    if image_file is None:
        return None
    try:
        img = Image.open(image_file)
        buffered = BytesIO()
        img.save(buffered, format=img.format if img.format else "PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/{img.format.lower() if img.format else 'png'};base64,{img_str}"
    except Exception as e:
        st.error(f"Lỗi xử lý ảnh: {e}")
        return None


def get_db_connection():
    """Tạo kết nối mới đến SQL Server."""
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        st.error(f"Lỗi kết nối CSDL: {e}")
        return None


def init_campaign_db():
    """Khởi tạo bảng Campaign_Manager nếu chưa tồn tại."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            cur.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Campaign_Manager_UX' and xtype='U')
            CREATE TABLE Campaign_Manager_UX (
                CampaignID INT IDENTITY(1,1) PRIMARY KEY,
                Name NVARCHAR(255) NOT NULL,
                Platform NVARCHAR(100),
                Objective NVARCHAR(255),
                Segment NVARCHAR(255),
                Tactic NVARCHAR(255),
                Status NVARCHAR(50) DEFAULT 'Đã lưu',
                Budget REAL DEFAULT 0,
                ActualRevenue REAL DEFAULT 0,
                KPI NVARCHAR(MAX),
                StartDate DATE,
                EndDate DATE,
                Notes NVARCHAR(MAX),
                DynamicData NVARCHAR(MAX)
            )
            """)
        conn.commit()
    except Exception as e:
        st.warning(f"Lỗi khi khởi tạo bảng Campaign_Manager_UX: {e}")
    finally:
        conn.close()


@st.cache_data(ttl=600)
def load_campaigns_from_db():
    """Tải tất cả chiến dịch đã lưu từ CSDL."""
    conn = get_db_connection()
    if not conn:
        return []

    campaigns = []
    try:
        df = pd.read_sql(
            "SELECT * FROM Campaign_Manager_UX ORDER BY CampaignID DESC", conn)

        for _, row in df.iterrows():
            campaign = row.to_dict()
            campaign['id'] = campaign.pop('CampaignID')
            campaign['name'] = campaign.pop('Name')
            campaign['platform'] = campaign.pop('Platform')
            campaign['objective'] = campaign.pop('Objective')
            campaign['segment'] = campaign.pop('Segment')
            campaign['tactic'] = campaign.pop('Tactic')
            campaign['status'] = campaign.pop('Status')
            campaign['budget'] = campaign.pop('Budget')
            campaign['revenue'] = campaign.pop('ActualRevenue')
            campaign['kpi'] = campaign.pop('KPI')
            campaign['startDate'] = str(campaign.pop('StartDate'))
            campaign['endDate'] = str(campaign.pop('EndDate'))
            campaign['notes'] = campaign.pop('Notes')
            campaign['dynamicData'] = json.loads(campaign.pop(
                'DynamicData')) if campaign.get('DynamicData') else {}
            campaigns.append(campaign)

        return campaigns

    except Exception as e:
        st.error(f"Lỗi khi tải chiến dịch từ CSDL: {e}")
        return []
    finally:
        conn.close()


@st.cache_data(ttl=600)
def load_real_segment_data():
    """Tải dữ liệu phân khúc THẬT từ CSDL."""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()

    try:
        query = """
        SELECT
            PhanKhuc,
            COUNT(KhachHangID) AS SoLuong,
            AVG(Recency) AS R_TB,
            AVG(Frequency) AS F_TB,
            AVG(Monetary) AS M_TB,
            SUM(Monetary) AS TongDoanhThu
        FROM Customer_Segmentation
        WHERE PhanKhuc IS NOT NULL
        GROUP BY PhanKhuc
        """
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu phân khúc: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


def load_detailed_segment_data(segment_name):
    """Lấy dữ liệu CHI TIẾT từng khách hàng của một phân khúc"""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()

    try:
        query = """
        SELECT 
            KhachHangID AS CustomerID,
            Recency,
            Frequency,
            Monetary
        FROM Customer_Segmentation
        WHERE PhanKhuc = ?
        """
        df = pd.read_sql(query, conn, params=[segment_name])
        return df
    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu chi tiết: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


def load_all_customers_for_comparison():
    """Lấy TOÀN BỘ dữ liệu khách hàng để so sánh"""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()

    try:
        query = """
        SELECT 
            KhachHangID AS CustomerID,
            Recency,
            Frequency,
            Monetary,
            PhanKhuc
        FROM Customer_Segmentation
        WHERE PhanKhuc IS NOT NULL
        """
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


def save_campaign_to_db(form_data, session_data):
    """Lưu chiến dịch mới vào CSDL."""
    conn = get_db_connection()
    if not conn:
        return False

    dynamic_data_json = json.dumps(form_data.get('dynamicData', {}))

    try:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO Campaign_Manager_UX
                (Name, Platform, Objective, Segment, Tactic, Status, Budget,
                 KPI, StartDate, EndDate, Notes, DynamicData)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                        form_data['campaign-name'],
                        session_data['platform'],
                        session_data['objective']['title'],
                        session_data['segment']['name'],
                        session_data['tactic']['name'],
                        '📝 Đã lưu',
                        float(form_data['campaign-budget']
                              ) if form_data['campaign-budget'] else 0,
                        form_data['campaign-kpi'],
                        str(form_data['campaign-start-date']),
                        str(form_data['campaign-end-date']),
                        form_data['campaign-notes'],
                        dynamic_data_json
                        )
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Lỗi khi lưu chiến dịch vào CSDL: {e}")
        return False
    finally:
        conn.close()


def update_campaign_status_in_db(campaign_id, new_status, new_revenue=None):
    """Cập nhật trạng thái hoặc doanh thu."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            if new_revenue is not None:
                cur.execute("UPDATE Campaign_Manager_UX SET Status = ?, ActualRevenue = ? WHERE CampaignID = ?",
                            (new_status, new_revenue, campaign_id))
            else:
                cur.execute("UPDATE Campaign_Manager_UX SET Status = ? WHERE CampaignID = ?",
                            (new_status, campaign_id))
        conn.commit()
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Lỗi khi cập nhật chiến dịch: {e}")
    finally:
        conn.close()


@st.cache_data(ttl=600)
def get_emails_for_segment(segment_name):
    """Lấy danh sách email cho một phân khúc."""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        query = """
        SELECT KH.Email
        FROM DimKhachHang KH
        JOIN Customer_Segmentation CS ON KH.KhachHangID = CS.KhachHangID
        WHERE CS.PhanKhuc = ? AND KH.Email IS NOT NULL AND KH.Email LIKE '%@%'
        """
        df = pd.read_sql(query, conn, params=(segment_name,))
        return df['Email'].tolist()
    except Exception as e:
        st.error(f"Lỗi khi lấy email phân khúc: {e}")
        return []
    finally:
        conn.close()


def init_state():
    defaults = {
        'current_step': 1,
        'selected_platform': None,
        'selected_objective': None,
        'selected_segment': None,
        'selected_tactic': None,
        'view': 'wizard',
        'show_demo_modal': False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if 'campaigns' not in st.session_state:
        st.session_state.campaigns = load_campaigns_from_db()

    if 'stepper_names' not in st.session_state:
        st.session_state.stepper_names = {
            1: "Chọn Nền Tảng", 2: "Chọn Mục Tiêu", 3: "Chọn Phân Khúc",
            4: "Chọn Chiến Thuật", 5: "Thiết Kế", 6: "Hoàn Tất"
        }

    if 'real_segment_data' not in st.session_state:
        st.session_state.real_segment_data = load_real_segment_data()

# --- CÁC HÀM TIỆN ÍCH ---


def format_currency(value):
    try:
        val = float(value)
        return f"{val:,.0f} ₫".replace(",", ".")
    except (ValueError, TypeError, AttributeError):
        return "0 ₫"


def go_to_step(step):
    st.session_state.current_step = step


def go_to_view(view_name):
    st.session_state.view = view_name
    if view_name == 'wizard':
        st.session_state.current_step = 1
        reset_wizard()
    # st.rerun()


def reset_wizard():
    st.session_state.current_step = 1
    st.session_state.selected_platform = None
    st.session_state.selected_objective = None
    st.session_state.selected_segment = None
    st.session_state.selected_tactic = None
    update_stepper_names('owned')


def update_stepper_names(platform):
    if platform == 'owned':
        st.session_state.stepper_names = {
            1: "Chọn Nền Tảng", 2: "Chọn Mục Tiêu", 3: "Chọn Phân Khúc",
            4: "Chọn Chiến Thuật", 5: "Thiết Kế", 6: "Hoàn Tất"
        }
    elif platform == 'marketplace':
        st.session_state.stepper_names = {
            1: "Chọn Nền Tảng", 2: "Dashboard & Mục Tiêu", 3: "(Bỏ qua)",
            4: "Chọn Chiến Dịch", 5: "Thiết Kế", 6: "Hoàn Tất"
        }


def select_platform(platform):
    st.session_state.selected_platform = platform
    update_stepper_names(platform)
    go_to_step(2)


def select_objective(goal_id, goal_title):
    st.session_state.selected_objective = {'id': goal_id, 'title': goal_title}
    df_real_segments = st.session_state.real_segment_data

    if st.session_state.selected_platform == 'owned':
        go_to_step(3)
    elif st.session_state.selected_platform == 'marketplace':
        if df_real_segments.empty:
            st.error("Không thể tải dữ liệu phân khúc thật. Dùng dữ liệu dự phòng.")
            logic_name = 'Đề xuất chung'
        else:
            total_customers = df_real_segments['SoLuong'].sum()

            map_rich = ['Khách hàng VIP', 'Khách hàng trung thành']
            map_at_risk = ['Khách hàng có nguy cơ mất', 'Khách hàng yếu']
            map_new = ['Khách hàng mới', 'Khách hàng tiềm năng']

            rich_percentage = df_real_segments[df_real_segments['PhanKhuc'].isin(
                map_rich)]['SoLuong'].sum() / total_customers * 100
            at_risk_percentage = df_real_segments[df_real_segments['PhanKhuc'].isin(
                map_at_risk)]['SoLuong'].sum() / total_customers * 100
            new_percentage = df_real_segments[df_real_segments['PhanKhuc'].isin(
                map_new)]['SoLuong'].sum() / total_customers * 100
            only_new_percentage = df_real_segments[df_real_segments['PhanKhuc']
                                                   == 'Khách hàng mới']['SoLuong'].sum() / total_customers * 100

            logic_name = 'Đề xuất chung'
            if goal_id == 'revenue' and rich_percentage > 30:
                logic_name = f"Tệp VIP/Trung thành ({rich_percentage:.0f}%)"
            elif goal_id == 'awareness' and at_risk_percentage > 30:
                logic_name = f"Tệp Nguy cơ ({at_risk_percentage:.0f}%)"
            elif goal_id == 'conversion' and (new_percentage > 40 or only_new_percentage > 20):
                logic_name = f"Tệp Mới/Vãng lai ({only_new_percentage:.0f}%)"
            elif goal_id == 'launch':
                logic_name = 'Ra mắt Sản phẩm Mới'
            else:
                logic_name = 'Đề xuất chung theo Mục tiêu'

        st.session_state.selected_segment = {
            'id': 'marketplace_logic', 'name': f"Logic: {logic_name}"}
        go_to_step(4)


def select_segment(segment_id, segment_name):
    st.session_state.selected_segment = {
        'id': segment_id, 'name': segment_name}
    go_to_step(4)


def select_tactic(tactic_id, tactic_name, tactic_type):
    st.session_state.selected_tactic = {
        'id': tactic_id, 'name': tactic_name, 'type': tactic_type}
    go_to_step(5)


def handle_save_campaign(form_data):
    session_data = {
        'platform': st.session_state.selected_platform,
        'objective': st.session_state.selected_objective,
        'segment': st.session_state.selected_segment,
        'tactic': st.session_state.selected_tactic,
    }

    dynamic_data = {}
    for k, v in st.session_state.items():
        if k.startswith('tactic-'):
            if k.endswith('-uploader'):
                continue
            dynamic_data[k] = v

    form_data['dynamicData'] = dynamic_data

    success = save_campaign_to_db(form_data, session_data)

    if success:
        st.toast(
            f"✅ Đã lưu chiến dịch: {form_data['campaign-name']}", icon="✅")
        st.cache_data.clear()
        st.session_state.campaigns = load_campaigns_from_db()
        go_to_view('dashboard')
        st.session_state.current_step = 6
    else:
        st.error("❌ Lưu chiến dịch thất bại. Vui lòng kiểm tra lại.")


def build_html_email(data):
    """Xây dựng nội dung email HTML từ dynamicData."""
    subject = data.get('tactic-email-subject',
                       "Một thông báo mới từ chúng tôi")
    image_data = data.get('tactic-email-image', '')
    body = data.get('tactic-email-body', 'Đây là nội dung email của bạn.')
    button_text = data.get('tactic-email-button-text', 'Xem ngay')
    button_url = data.get('tactic-email-button-url', '#')
    body_text = body.replace('\n', '<br>')
    # Tạo html ảnh ở ngoài f-string để tránh backslash trong biểu thức f-string
    img_html = f"<img src='{image_data}' alt='Banner' class='banner'>" if image_data else ""

    html_content = f"""
    <html>
    <head>
        <style>
            .container {{ font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
            .banner {{ max-width: 100%; height: auto; border-radius: 8px; }}
            .content {{ padding: 20px 0; }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
                background-color: #007bff;
                text-decoration: none;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <p><strong>Tiêu đề: {subject}</strong></p>
            {img_html}
            <div class="content">
                <p>Xin chào,</p>
                <p>{body_text}</p>
            </div>
            <a href="{button_url}" class="button">{button_text}</a>
            <p style="font-size: 12px; color: #888; margin-top: 20px;">Trân trọng,<br>(Tên công ty của bạn)</p>
        </div>
    </body>
    </html>
    """
    plain_text_content = f"""
    Tiêu đề: {subject}
    Xin chào,
    {body}

    {button_text}: {button_url}

    Trân trọng,
    (Tên công ty của bạn)
    """

    return subject, plain_text_content, html_content


def send_email_campaign(campaign, email_list):
    """Soạn và gửi email HTML."""
    # Kiểm tra cấu hình email trong secrets
    try:
        if not hasattr(st, 'secrets') or 'email' not in st.secrets:
            st.error(
                "❌ Chưa cấu hình email! Vui lòng tạo file .streamlit/secrets.toml với cấu hình email.")
            st.info("""
            Tạo file `.streamlit/secrets.toml` với nội dung:
            ```toml
            [email]
            sender_email = "your-email@gmail.com"
            sender_password = "your-app-password"
            smtp_server = "smtp.gmail.com"
            smtp_port = "465"
            ```
            """)
            return False

        config = st.secrets.email
        sender_email = config.sender_email
        sender_password = config.sender_password
        smtp_server = config.smtp_server
        smtp_port = int(config.smtp_port)
    except Exception as e:
        st.error(f"❌ Lỗi đọc cấu hình email: {e}")
        return False

    dynamic_data = campaign.get('dynamicData', {})
    subject, plain_text_body, html_body = build_html_email(dynamic_data)
    # Giới hạn 5 email cho demo
    emails_to_send = email_list[:5]

    if len(email_list) > 5:
        st.info(
            f"ℹ️ Giới hạn gửi 5 email demo. Tổng tệp: {len(email_list)} khách hàng.")

    context = ssl.create_default_context()
    try:
        with st.spinner(f"⏳ Đang gửi email đến {len(emails_to_send)} khách hàng..."):
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(sender_email, sender_password)

                for receiver_email in emails_to_send:
                    msg = EmailMessage()
                    msg['Subject'] = subject
                    msg['From'] = sender_email
                    msg['To'] = receiver_email
                    msg.set_content(plain_text_body)
                    msg.add_alternative(html_body, subtype='html')
                    server.send_message(msg)

        return True

    except smtplib.SMTPAuthenticationError:
        st.error(
            "❌ Lỗi xác thực email! Kiểm tra lại email/password trong secrets.toml")
        st.info(
            "💡 Nếu dùng Gmail, hãy tạo App Password tại: https://myaccount.google.com/apppasswords")
        return False
    except smtplib.SMTPException as e:
        st.error(f"❌ Lỗi SMTP: {e}")
        return False
    except Exception as e:
        st.error(f"❌ Lỗi không xác định khi gửi email: {e}")
        return False


def activate_campaign(campaign_id):
    """Kích hoạt và Gửi Email"""
    campaign = next(
        (c for c in st.session_state.campaigns if c['id'] == campaign_id), None)
    if not campaign:
        st.error("Không tìm thấy chiến dịch!")
        return

    segment_name = campaign.get('segment')
    platform = campaign.get('platform')

    # Kiểm tra xem có phải owned channel và có dynamicData không
    if platform == 'owned' and campaign.get('dynamicData'):
        # Lấy email list
        email_list = get_emails_for_segment(segment_name)

        if not email_list:
            st.session_state['activation_message'] = {
                'type': 'warning',
                'text': f"⚠️ Không tìm thấy email nào cho phân khúc '{segment_name}'. Chỉ kích hoạt trạng thái."
            }
        else:
            # Gửi email
            success = send_email_campaign(campaign, email_list)
            if success:
                st.session_state['activation_message'] = {
                    'type': 'success',
                    'text': f"✅ Đã kích hoạt chiến dịch và gửi {min(len(email_list), 5)} email demo thành công!",
                    'count': min(len(email_list), 5),
                    'total': len(email_list)
                }
            else:
                st.session_state['activation_message'] = {
                    'type': 'warning',
                    'text': "⚠️ Đã kích hoạt chiến dịch nhưng gửi email thất bại."
                }
    else:
        st.session_state['activation_message'] = {
            'type': 'info',
            'text': "ℹ️ Đã kích hoạt chiến dịch! (Không phải owned channel hoặc chưa thiết kế email)"
        }

    # Cập nhật trạng thái trong database
    update_campaign_status_in_db(campaign_id, '🟢 Đang chạy')
    st.session_state.campaigns = load_campaigns_from_db()
    st.session_state['need_rerun'] = True


def show_result_modal(campaign_id):
    st.session_state.editing_campaign_id = campaign_id


def save_campaign_result(campaign_id, revenue):
    update_campaign_status_in_db(
        campaign_id, '🟡 Đã kết thúc', new_revenue=revenue)
    st.session_state.campaigns = load_campaigns_from_db()
    st.toast(f"✅ Đã cập nhật doanh thu", icon="💰")
    if 'editing_campaign_id' in st.session_state:
        del st.session_state.editing_campaign_id
    # st.rerun()


def render_header_and_nav():
    """Header với marketing theme"""
    # CSS Marketing Theme
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
    # Header Gradient
    st.markdown("""
    <div class="main-header">
        <h1 style='margin:0; font-size: 2rem;'>🎯 Module Chiến Lược Quảng Cáo</h1>
        <p style='margin:0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.95;'>
            Vận hành chiến lược quảng cáo cáo nhân hóa đa kênh dựa trên dữ liệu RFM thực tế
        </p>
    </div>
    """, unsafe_allow_html=True)
    # Navigation Buttons
    cols = st.columns(2)
    with cols[0]:
        st.button(
            "➕ Tạo Chiến Dịch Mới",
            on_click=go_to_view,
            args=('wizard',),
            use_container_width=True,
            type="primary" if st.session_state.view == 'wizard' else "secondary"
        )
    with cols[1]:
        campaigns_count = len(st.session_state.campaigns)
        active_count = len(
            [c for c in st.session_state.campaigns if c.get('status') == '🟢 Đang chạy'])
        st.button(
            f"📊 Dashboard ({active_count}/{campaigns_count})",
            on_click=go_to_view,
            args=('dashboard',),
            use_container_width=True,
            type="primary" if st.session_state.view == 'dashboard' else "secondary"
        )
    st.divider()


def render_stepper():
    current_step = st.session_state.current_step
    platform = st.session_state.selected_platform
    names = st.session_state.stepper_names
    valid_steps = [1, 2, 4, 5, 6] if platform == 'marketplace' else [
        1, 2, 3, 4, 5, 6]
    cols = st.columns(len(valid_steps))
    col_idx = 0
    for step_num in sorted(names.keys()):
        if step_num not in valid_steps:
            continue
        step_name = names[step_num]
        col = cols[col_idx]
        col_idx += 1
        with col:
            if step_num < current_step:
                st.markdown(f"**✅ {step_num}. {step_name}**")
            elif step_num == current_step:
                st.markdown(f"🔵 **{step_num}. {step_name}**")
            else:
                st.markdown(
                    f"<span style='color:grey;'>{step_num}. {step_name}</span>", unsafe_allow_html=True)


def render_step_1():
    st.header("Bước 1: Chọn Nền Tảng Kinh Doanh Chính", divider="blue")
    st.write("💡 Khách hàng của bạn chủ yếu đang ở đâu? Điều này sẽ giúp hệ thống đề xuất kịch bản phù hợp.")
    cols = st.columns(2)
    with cols[0]:
        with st.container(border=True):
            st.markdown("### 🌐 Kênh Sở Hữu (Owned)")
            st.write(
                "Doanh nghiệp có Website, App, CRM riêng và muốn cá nhân hóa trải nghiệm trên các kênh này.")
            st.markdown(
                "**Phù hợp với:** Email Marketing, Zalo OA, Web Popup, SMS...")
            st.button("Chọn Kênh Sở Hữu", on_click=select_platform, args=(
                'owned',), use_container_width=True, type="primary")
    with cols[1]:
        with st.container(border=True):
            st.markdown("### 🛍️ Kênh Sàn TMĐT")
            st.write(
                "Kinh doanh chủ yếu trên các sàn và muốn tận dụng công cụ của sàn giúp tăng trưởng .")
            st.markdown(
                "**Phù hợp với:** Shopee, Lazada, Tiki (Ads, Voucher, Livestream...)")
            st.button("Chọn Sàn TMĐT", on_click=select_platform, args=(
                'marketplace',), use_container_width=True, type="primary")


def render_step_2():
    st.button("⬅️ Quay lại", on_click=go_to_step,
              args=(1,), key="back_to_step1")
    if st.session_state.selected_platform == 'owned':
        st.header("Bước 2: Xác định Mục tiêu Chiến lược", divider="blue")
        st.write(
            "🎯 Chọn mục tiêu kinh doanh cốt lõi để hệ thống đề xuất phân khúc khách hàng phù hợp.")
    else:
        st.header("Bước 2: Phân tích Hiện trạng & Chọn Mục tiêu", divider="blue")
        st.write(
            "📊 Hệ thống đã phân tích dữ liệu từ CSDL. Hãy xem hiện trạng và chọn mục tiêu ưu tiên.")
        with st.container(border=True):
            st.subheader("📈 Phân bố Phân khúc Khách hàng")
            df_real = st.session_state.real_segment_data
            if df_real.empty:
                st.error("❌ Không tải được dữ liệu phân khúc.")
            else:
                color_map = {
                    'Khách hàng VIP': '#FACC15',
                    'Khách hàng trung thành': '#3B82F6',
                    'Khách hàng ổn định': '#10B981',
                    'Khách hàng tiềm năng': '#8B5CF6',
                    'Khách hàng mới': '#4ADE80',
                    'Khách hàng có nguy cơ mất': '#EF4444',
                    'Khách hàng yếu': '#F97316'
                }

                df_real['percentage'] = (
                    df_real['SoLuong'] / df_real['SoLuong'].sum()) * 100
                df_real['color'] = df_real['PhanKhuc'].map(
                    color_map).fillna('#9CA3AF')

                distribution = df_real.to_dict('records')
                percentages = [d['percentage'] for d in distribution]
                colors = [d['color'] for d in distribution]

                sorted_data = sorted(
                    zip(percentages, colors, distribution), key=lambda x: x[0], reverse=True)
                # ✅ THÊM 7 DÒNG NÀY
                st.markdown("""
                <style>
                [data-testid="column"] {
                    padding: 0px !important;
                }
                </style>
                """, unsafe_allow_html=True)
                bar_cols = st.columns([p for p, c, d in sorted_data])
                for i, (p, c, d) in enumerate(sorted_data):
                    with bar_cols[i]:
                        st.markdown(
                            f"<div style='background-color:{c}; height: 15px; border-radius: 2px;' title='{d['PhanKhuc']}: {d['percentage']:.1f}%'></div>",
                            unsafe_allow_html=True)

                # ✅ THAY ĐỔI Ở ĐÂY: Dùng cùng tỷ lệ với bar_cols
            legend_cols = st.columns([p for p, c, d in sorted_data])
            for i, (p, c, d) in enumerate(sorted_data):
                with legend_cols[i]:
                    st.markdown(
                        f"""
                        <div style='text-align: center; padding: 0 5px;'>
                            <div style='color:{c}; font-size: 24px; margin-bottom: 5px;'>●</div>
                            <div style='font-size: 15px; font-weight: 600; line-height: 1.3; margin-bottom: 3px;'>
                                {d['PhanKhuc'].replace('Khách hàng', 'KH')}
                            </div>
                            <div style='color:{c}; font-size: 20px; font-weight: bold; margin-bottom: 5px;'>
                                {d['percentage']:.1f}%
                            </div>
                            <div style='color: #666; font-size: 17px;
                            <div style='color:{c}; font-size: 18px; font-weight: bold;'>
                               SL:{d['SoLuong']} 
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        st.subheader("🎯 Chọn mục tiêu dựa trên phân tích:")

    objectives = config_data["objectives"]
    cols = st.columns(len(objectives))
    for i, goal in enumerate(objectives):
        with cols[i % len(objectives)]:
            with st.container(border=True):
                st.markdown(f"### {goal['icon']} {goal['title']}")
                st.write(goal['description'])
                st.button(
                    f"Chọn mục tiêu này",
                    on_click=select_objective,
                    args=(goal['id'], goal['title']),
                    use_container_width=True,
                    key=f"goal_{goal['id']}",
                    type="primary"
                )


def render_step_3():
    """Bước 3 CẢI TIẾN với REASONING ĐỘNG dựa trên RFM + SegmentReasoningEngine"""
    st.button("⬅️ Quay lại", on_click=go_to_step,
              args=(2,), key="back_to_step2")

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

    # Hiển thị WHY statement tổng quan
    with st.container(border=True):
        st.markdown("### 💡 Tại sao chọn chiến lược này?")
        why_lines = [ln.strip() for ln in str(
            selected_obj.get('why', '')).splitlines() if ln.strip()]
        why_lines = why_lines[:6]
        col1, col2 = st.columns(2)
        for idx, ln in enumerate(why_lines):
            target = col1 if idx < 3 else col2
            target.markdown(ln)

    st.markdown("<br>", unsafe_allow_html=True)

    # PHẦN MỚI: KHỞI TẠO REASONING ENGINE
    if 'reasoning_engine' not in st.session_state:
        st.session_state.reasoning_engine = SegmentReasoningEngine()

    reasoning_engine = st.session_state.reasoning_engine

    # Load toàn bộ data để so sánh (cache trong session_state)
    if 'all_customers_data' not in st.session_state:
        with st.spinner("Đang tải dữ liệu khách hàng..."):
            st.session_state.all_customers_data = load_all_customers_for_comparison()

    all_data = st.session_state.all_customers_data

    # HIỂN THỊ TỪNG PHÂN KHÚC VỚI REASONING ĐỘNG
    df_real = st.session_state.real_segment_data
    segment_names = selected_obj['segments_owned']
    segments_to_show = df_real[df_real['PhanKhuc'].isin(segment_names)]

    # Hiển thị từng phân khúc
    for idx, segment in segments_to_show.iterrows():
        seg_name = segment['PhanKhuc']

        with st.container(border=True):
            # HEADER: Tên phân khúc + Nút chọn
            header_cols = st.columns([6, 1])
            with header_cols[0]:
                st.markdown(f"### 👥 {seg_name}")
            with header_cols[1]:
                st.button(
                    "✅ Chọn phân khúc",
                    on_click=select_segment,
                    args=(seg_name, seg_name),
                    use_container_width=True,
                    type="primary",
                    key=f"seg_btn_top_{seg_name}"
                )

            # RFM METRICS (Giữ nguyên như cũ)
            rfm_cols = st.columns(3)

            with rfm_cols[0]:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            padding: 0.6rem ; border-radius: 12px; text-align: center; color: white;'>
                    <div style='font-size: 12px; margin-bottom: 8px;'>⏱️ RECENCY</div>
                    <div style='font-size: 32px; font-weight: bold;'>{segment['R_TB']:.0f}</div>
                    <div style='font-size: 11px; margin-top: 8px; opacity: 0.9;'>ngày kể từ lần mua cuối</div>
                </div>
                """, unsafe_allow_html=True)

            with rfm_cols[1]:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            padding: 0.6rem ; border-radius: 12px; text-align: center; color: white;'>
                    <div style='font-size: 12px; margin-bottom: 8px;'>🔄 FREQUENCY</div>
                    <div style='font-size: 32px; font-weight: bold;'>{segment['F_TB']:.1f}</div>
                    <div style='font-size: 11px; margin-top: 8px; opacity: 0.9;'>lần giao dịch</div>
                </div>
                """, unsafe_allow_html=True)

            with rfm_cols[2]:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                            padding: 0.6rem ; border-radius: 12px; text-align: center; color: white;'>
                    <div style='font-size: 12px; margin-bottom: 8px;'>💰 MONETARY</div>
                    <div style='font-size: 28px; font-weight: bold;'>{format_currency(segment['M_TB'])}</div>
                    <div style='font-size: 11px; margin-top: 8px; opacity: 0.9;'>giá trị TB/đơn</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # PHẦN MỚI: THÊM REASONING ĐỘNG
            with st.expander("📝 **Phân tích chi tiết và đề xuất chiến lược**", expanded=False):
                cache_key = f"reasoning_{seg_name}"

                if cache_key not in st.session_state:
                    with st.spinner(f"Đang phân tích phân khúc {seg_name}..."):
                        segment_detail_data = load_detailed_segment_data(
                            seg_name)

                        if len(segment_detail_data) > 0 and len(all_data) > 0:
                            reasoning = reasoning_engine.generate_segment_reasoning(
                                segment_id=seg_name,
                                segment_data=segment_detail_data,
                                all_data=all_data
                            )
                            st.session_state[cache_key] = reasoning
                        else:
                            st.session_state[cache_key] = "⚠️ Không đủ dữ liệu để phân tích chi tiết."

                reasoning = st.session_state[cache_key]
                st.markdown(reasoning)

            st.markdown("<br>", unsafe_allow_html=True)


def render_step_4():
    """Hàm chính điều phối giữa owned và marketplace"""
    back_step = 2 if st.session_state.selected_platform == 'marketplace' else 3
    st.button("⬅️ Quay lại", on_click=go_to_step,
              args=(back_step,), key="back_to_step3_or_2")

    st.header("Bước 4: Đề xuất Kịch bản & Chiến thuật", divider="blue")
    st.write(
        f"🎯 Chọn kịch bản chiến thuật phù hợp cho **{st.session_state.selected_segment['name']}**")

    if st.session_state.selected_platform == 'owned':
        render_step_4_owned()
    else:
        render_step_4_marketplace()


def render_step_4_owned():
    """Render chiến thuật cho Owned Channels với METRICS ĐẦY ĐỦ"""
    segment_id = st.session_state.selected_segment['id']
    tactics_data = config_data["mockDataOwned"]["tactics"].get(segment_id, {})
    owned_tactics = tactics_data.get('owned', [])
    recommendations = config_data["mockDataOwned"]["tacticRecommendations"].get(
        segment_id, [])

    st.markdown("### 🌐 Kênh sở hữu (Owned Channels)")
    st.caption(
        "Tập trung vào cá nhân hóa sâu và tự động hóa trên website, app, CRM")

    if not owned_tactics:
        st.info("ℹ️ Không có chiến thuật nào được định nghĩa cho phân khúc này.")
        return
    st.markdown("<br>", unsafe_allow_html=True)

    for tactic in owned_tactics:
        is_recommended = tactic['id'] in recommendations

        # Container với border
        with st.container(border=True):
            # Badge recommendation
            if is_recommended:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            color: white; padding: 0.4rem 1rem; border-radius: 20px;
                            font-size: 0.85rem; font-weight: bold; display: inline-block;
                            margin-bottom: 1rem;'>
                    ⭐ ĐỀ XUẤT
                </div>
                """, unsafe_allow_html=True)

            # Header: Tên chiến thuật (trái) + Nút thiết kế (phải) - CÙNG 1 HÀNG
            header_cols = st.columns([6, 1])
            with header_cols[0]:
                st.markdown(f"## {tactic['name']}")
            with header_cols[1]:
                st.button(
                    "🎨 Thiết Kế →",
                    on_click=select_tactic,
                    args=(tactic['id'], tactic['name'], 'owned'),
                    use_container_width=True,
                    key=f"owned_btn_top_{tactic['id']}",
                    type="primary" if is_recommended else "secondary"
                )

            st.divider()

            # Metrics - 2 cột
            cols = st.columns(2)

            with cols[0]:
                st.markdown(f"**{tactic.get('benefit', 'N/A')}**")
                st.markdown(f"**💰 Chi phí:** {tactic.get('cost', 'N/A')}")

            with cols[1]:
                st.markdown(f"**📊 ROI:** {tactic.get('roi', 'N/A')}")
                st.markdown(
                    f"**⏱️ Timeline:** {tactic.get('timeline', 'N/A')}")

            st.markdown(f"**🎯 KPI:** {tactic.get('kpi', 'N/A')}")
            st.markdown("<br>", unsafe_allow_html=True)


def render_step_4_marketplace():
    """Render chiến thuật cho Marketplace với LOGIC THÔNG MINH"""
    all_tactics = config_data["mockDataMarketplace"]["tactics"]["marketplace"]
    goal_id = st.session_state.selected_objective['id']

    # Logic đề xuất thông minh
    marketplace_logic = config_data.get("marketplaceLogic", {})
    logic_for_goal = marketplace_logic.get(goal_id, {})
    recommendations = logic_for_goal.get('recommended', [])
    message = logic_for_goal.get('message', '')

    st.markdown("### 🛍️ Kênh Sàn TMĐT (Marketplace)")
    st.caption("Tận dụng các công cụ có sẵn của Shopee, Lazada, Tiki...")

    # Hiển thị phân tích và đề xuất
    if message:
        st.info(f"💡 **Phân tích:** {message}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Hiển thị tất cả tactics, highlight recommended
    for tactic in all_tactics:
        is_recommended = tactic['id'] in recommendations

        # Container với border
        with st.container(border=True):
            # Badge recommendation
            if is_recommended:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            color: white; padding: 0.4rem 1rem; border-radius: 20px;
                            font-size: 0.85rem; font-weight: bold; display: inline-block;
                            margin-bottom: 1rem;'>
                    ⭐ ĐỀ XUẤT
                </div>
                """, unsafe_allow_html=True)

            # Header: Tên chiến thuật (trái) + Nút thiết kế (phải) - CÙNG 1 HÀNG
            header_cols = st.columns([6, 1])
            with header_cols[0]:
                st.markdown(f"## {tactic['name']}")
            with header_cols[1]:
                st.button(
                    "🎨 Thiết Kế →",
                    on_click=select_tactic,
                    args=(tactic['id'], tactic['name'], 'marketplace'),
                    use_container_width=True,
                    key=f"mp_btn_top_{tactic['id']}",
                    type="primary" if is_recommended else "secondary"
                )

            st.write(tactic.get('desc', ''))
            st.divider()

            # Metrics - 2 cột
            cols = st.columns(2)

            with cols[0]:
                st.markdown(f"**{tactic.get('benefit', 'N/A')}**")
                st.markdown(f"**💰 Chi phí:** {tactic.get('cost', 'N/A')}")

            with cols[1]:
                st.markdown(f"**📊 ROI:** {tactic.get('roi', 'N/A')}")
                st.markdown(f"**🎯 KPI:** {tactic.get('kpi', 'N/A')}")


def render_dynamic_form(tactic_id, tactic_type):
    st.subheader(
        f"⚙️ Cấu hình: {st.session_state.selected_tactic['name']}", divider="blue")

    if tactic_type == 'owned':
        st.multiselect("📢 Kênh chạy", ["Email", "SMS", "Zalo OA"], default=[
                       "Email"], key="tactic-owned-channels")
        st.text_input(
            "📧 Tiêu đề Email", placeholder="Ưu đãi đặc biệt dành riêng cho bạn!", key="tactic-email-subject")

        # Upload ảnh với giao diện đẹp hơn
        st.markdown("---")
        st.markdown("### 🖼️ Hình ảnh Banner Email")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("""
            <div style='
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 10px;
                color: white;
                margin-bottom: 15px;
            '>
                <h4 style='margin: 0 0 10px 0;'>📐 Khuyến nghị kích thước</h4>
                <ul style='margin: 0; padding-left: 20px;'>
                    <li>Kích thước: <strong>600x300px</strong></li>
                    <li>Định dạng: PNG, JPG, GIF</li>
                    <li>Dung lượng: Tối đa 2MB</li>
                    <li>Tỷ lệ: 2:1 (Ngang)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                "Chọn file ảnh từ máy tính",
                type=['png', 'jpg', 'jpeg', 'gif'],
                key="tactic-email-image-uploader",
                help="Click để chọn ảnh banner cho email"
            )

            if uploaded_file is not None:
                image_base64 = image_to_base64(uploaded_file)
                if image_base64:
                    st.session_state['tactic-email-image'] = image_base64
                    st.success("✅ Đã tải ảnh thành công!")
            elif 'tactic-email-image' not in st.session_state:
                st.session_state['tactic-email-image'] = ''

        with col2:
            st.markdown("**👁️ Xem trước Banner**")
            if st.session_state.get('tactic-email-image'):
                with st.container(border=True):
                    st.image(
                        st.session_state['tactic-email-image'],
                        caption="Preview Banner Email",
                        use_container_width=True
                    )
                    if st.button("🗑️ Xóa ảnh", use_container_width=True, type="secondary"):
                        st.session_state['tactic-email-image'] = ''
                        # st.rerun()
            else:
                with st.container(border=True):
                    st.markdown("""
                    <div style='
                        background: #f0f2f6;
                        padding: 60px 20px;
                        border-radius: 8px;
                        text-align: center;
                        color: #666;
                    '>
                        <p style='font-size: 48px; margin: 0;'>🖼️</p>
                        <p style='margin: 10px 0 0 0;'>Chưa có ảnh</p>
                        <p style='margin: 5px 0 0 0; font-size: 12px;'>Tải ảnh lên để xem trước</p>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")
        st.text_area("📝 Nội dung tin nhắn", placeholder="Chào bạn,\n\nChúng tôi có ưu đãi...",
                     key="tactic-email-body", height=150)

        col1, col2 = st.columns(2)
        with col1:
            st.text_input("🔘 Tiêu đề nút (CTA)",
                          placeholder="Xem ngay!", key="tactic-email-button-text")
        with col2:
            st.text_input(
                "🔗 Link nút", placeholder="https://shop.com/san-pham", key="tactic-email-button-url")

    elif tactic_type == 'marketplace':
        # Phần marketplace giữ nguyên...
        if tactic_id == 'mp_ads':
            st.text_input("📦 Sản phẩm quảng cáo",
                          placeholder="Vd: Áo sơ mi trắng", key="tactic-ads-product")
            st.text_input("🔍 Từ khóa (phân cách bằng dấu phẩy)",
                          placeholder="Vd: áo sơ mi, sơ mi công sở", key="tactic-ads-keywords")
            st.number_input("💰 CPC mong muốn (VNĐ)", min_value=0,
                            step=100, value=1000, key="tactic-ads-cpc")

        elif tactic_id == 'mp_flash_sale':
            st.text_input("📦 Sản phẩm tham gia",
                          placeholder="Vd: Giày da nam", key="tactic-fs-product")
            cols = st.columns(2)
            cols[0].number_input(
                "💵 Giá giảm (VNĐ)", min_value=0, value=199000, key="tactic-fs-price")
            cols[1].number_input("📊 Giới hạn số lượng",
                                 min_value=0, value=100, key="tactic-fs-limit")
            st.date_input("📅 Ngày Flash Sale", key="tactic-fs-date",
                          value=datetime.date.today())
            st.time_input("⏰ Giờ Flash Sale", key="tactic-fs-time",
                          value=datetime.time(12, 0))

        elif tactic_id == 'mp_voucher':
            st.selectbox("🎟️ Loại Voucher", [
                         "Giảm theo %", "Giảm theo số tiền", "Freeship"], key="tactic-voucher-type")
            cols = st.columns(2)
            cols[0].text_input(
                "🔖 Mã giảm giá", placeholder="SHOPVIP10", key="tactic-voucher-code")
            cols[1].number_input(
                "💰 Giá trị (VND hoặc %)", min_value=0, value=10, key="tactic-voucher-value")
            cols = st.columns(2)
            cols[0].number_input(
                "📦 Đơn tối thiểu (VNĐ)", min_value=0, value=99000, key="tactic-voucher-min")
            cols[1].number_input(
                "👥 Lượt dùng tối đa", min_value=0, value=500, key="tactic-voucher-limit")

        elif tactic_id == 'mp_livestream':
            st.text_input("📺 Tiêu đề Livestream",
                          placeholder="Siêu Sale 11.11 - Giảm Sốc", key="tactic-live-title")
            st.date_input("📅 Ngày Livestream",
                          key="tactic-live-date", value=datetime.date.today())
            st.time_input("⏰ Giờ Livestream",
                          key="tactic-live-time", value=datetime.time(20, 0))
            st.text_area("📝 Kịch bản / Mô tả",
                         key="tactic-live-script", height=120)
            st.text_input("🔗 Link sản phẩm ghim",
                          placeholder="link1, link2,...", key="tactic-live-products")

        elif tactic_id == 'mp_combo':
            st.text_input("📦 Sản phẩm chính",
                          placeholder="Vd: Áo sơ mi", key="tactic-combo-main")
            st.text_input("➕ Sản phẩm phụ",
                          placeholder="Vd: Cà vạt", key="tactic-combo-sub")
            st.number_input("💰 Giá combo (VNĐ)", min_value=0,
                            value=249000, key="tactic-combo-price")

        else:
            st.info("ℹ️ Chiến thuật này không cần cấu hình chi tiết.")


def render_step_5():
    st.button("⬅️ Quay lại", on_click=go_to_step,
              args=(4,), key="back_to_step4")
    st.header("Bước 5: Trình Dựng Chiến Dịch", divider="blue")
    st.write("🎨 Cấu hình chi tiết cho chiến dịch. Dữ liệu sẽ được lưu vào CSDL.")

    # Hiển thị modal demo
    if st.session_state.get('show_demo_modal', False):
        render_demo_modal()

    with st.container(border=True):
        render_dynamic_form(
            st.session_state.selected_tactic['id'], st.session_state.selected_tactic['type'])

    st.divider()

    with st.form(key="campaign_builder_form"):
        st.subheader("📋 Cấu hình chung")
        form_data = {}
        cols = st.columns(2)

        form_data['campaign-name'] = cols[0].text_input(
            "📝 Tên Chiến Dịch",
            value=f"[{st.session_state.selected_tactic['name']}] - {st.session_state.selected_objective['title']}"
        )
        form_data['campaign-segment'] = cols[1].text_input(
            "👥 Gửi Đến",
            value=st.session_state.selected_segment['name'],
            disabled=True
        )

        cols = st.columns(2)
        form_data['campaign-budget'] = cols[0].number_input(
            "💰 Tổng Ngân Sách (VNĐ)", min_value=0, step=100000, value=0)
        form_data['campaign-kpi'] = cols[1].text_input(
            "🎯 Mục Tiêu KPI", placeholder="Ví dụ: 50 đơn hàng")

        cols = st.columns(2)
        form_data['campaign-start-date'] = cols[0].date_input(
            "📅 Ngày Bắt Đầu", value=datetime.date.today())
        form_data['campaign-end-date'] = cols[1].date_input(
            "📅 Ngày Kết Thúc", value=datetime.date.today() + datetime.timedelta(days=7))

        form_data['campaign-notes'] = st.text_area("📝 Ghi Chú Nội Bộ")

        cols_btn = st.columns(2)
        submitted = cols_btn[0].form_submit_button(
            "💾 Lưu vào CSDL", use_container_width=True, type="primary")
        demo_clicked = cols_btn[1].form_submit_button(
            "👁️ Xem Demo", use_container_width=True, type="secondary")

        if submitted:
            for key in st.session_state:
                if key.startswith('tactic-'):
                    form_data[key] = st.session_state[key]
            handle_save_campaign(form_data)

        if demo_clicked:
            st.session_state.show_demo_modal = True
            st.rerun()


def render_demo_modal():
    """Modal xem demo chiến dịch"""
    @st.dialog("🎬 Xem Demo Chiến Dịch", width="large")
    def show_demo_dialog():
        # Thu thập dữ liệu
        dynamic_data = {}
        for key in st.session_state:
            if key.startswith('tactic-'):
                dynamic_data[key] = st.session_state[key]

        data = {
            'name': "Bản xem trước (Chưa lưu)",
            'objective': st.session_state.selected_objective.get('title', 'N/A'),
            'dynamicData': dynamic_data,
            'platform': st.session_state.selected_platform
        }

        st.header(f"📧 {data.get('name')}")
        st.subheader(f"🎯 Chủ đề: {data.get('objective')}")
        st.divider()

        platform = data.get('platform')

        # ==== KÊNH OWNED (WEB) ====
        if platform == 'owned':
            subject = dynamic_data.get(
                'tactic-email-subject', 'Chưa có tiêu đề')
            image_data = dynamic_data.get('tactic-email-image', '')
            body = dynamic_data.get('tactic-email-body', 'Chưa có nội dung')
            button_text = dynamic_data.get(
                'tactic-email-button-text', 'Xem ngay')
            button_url = dynamic_data.get('tactic-email-button-url', '#')

            st.markdown("### 📬 Xem trước Email gửi đến khách hàng:")

            # Container preview email
            with st.container():
                # Header
                st.markdown(f"""
                <div style='
                    background: #f8f9fa;
                    padding: 15px 20px;
                    border-radius: 8px 8px 0 0;
                    border: 1px solid #dee2e6;
                    border-bottom: 2px solid #007bff;
                '>
                    <strong style='color: #333; font-size: 18px;'>📧 {subject}</strong>
                </div>
                """, unsafe_allow_html=True)

                # Banner nếu có
                if image_data:
                    st.markdown(f"""
                    <div style='
                        text-align: center;
                        padding: 20px;
                        background: white;
                        border-left: 1px solid #dee2e6;
                        border-right: 1px solid #dee2e6;
                    '>
                        <img src="{image_data}" style='
                            max-width: 80%;
                            height: auto;
                            border-radius: 8px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        '>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style='
                        background: #e9ecef;
                        padding: 60px 20px;
                        text-align: center;
                        color: #6c757d;
                        border-left: 1px solid #dee2e6;
                        border-right: 1px solid #dee2e6;
                    '>
                        <p style='font-size: 30px; margin: 0;'>🖼️</p>
                        <p style='margin: 10px 0 0 0;'>Chưa có ảnh banner</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Content
                st.markdown(f"""
                <div style='
                    background: white;
                    padding: 30px 20px;
                    border-left: 1px solid #dee2e6;
                    border-right: 1px solid #dee2e6;
                '>
                    <p style='color: #495057; font-size: 15px; line-height: 1.8; margin: 0 0 15px 0;'>
                        Xin chào,
                    </p>
                    <p style='color: #495057; font-size: 15px; line-height: 1.8; margin: 0;'>
                        {body.replace(chr(10), '<br>')}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # CTA Button
                st.markdown(f"""
                <div style='
                    background: white;
                    padding: 20px;
                    text-align: center;
                    border-left: 1px solid #dee2e6;
                    border-right: 1px solid #dee2e6;
                '>
                    <a href='{button_url}' style='
                        display: inline-block;
                        background: #007bff;
                        color: white;
                        padding: 12px 30px;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 16px;
                    '>{button_text}</a>
                </div>
                """, unsafe_allow_html=True)

                # Footer
                st.markdown("""
                <div style='
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    border: 1px solid #dee2e6;
                    border-radius: 0 0 8px 8px;
                '>
                    <p style='color: #6c757d; font-size: 13px; margin: 0;'>
                        Trân trọng,<br>
                        <strong>BichNgoc sneaker</strong>
                    </p>
                </div>
                """, unsafe_allow_html=True)

        # ==== KÊNH MARKETPLACE (SÀN TMĐT) ====
        elif platform == 'marketplace':
            st.markdown("### 🛍️ Thông Tin Chiến Dịch TMĐT")

            # Lấy tactic_id từ session_state
            tactic_id = st.session_state.selected_tactic.get(
                'id', '') if st.session_state.selected_tactic else ''

            with st.container():
                # Header
                st.markdown("""
                <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            padding: 20px; border-radius: 8px; color: white; text-align: center;'>
                    <h2 style='margin: 0;'>🎯 Chi Tiết Chiến Dịch</h2>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Voucher
                if 'voucher' in tactic_id.lower():
                    st.markdown("#### 🎫 Thông tin Voucher")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(
                            f"**Loại voucher:** {dynamic_data.get('tactic-voucher-type', 'N/A')}")
                        st.info(
                            f"**Mã giảm giá:** {dynamic_data.get('tactic-voucher-code', 'N/A')}")
                    with col2:
                        st.success(
                            f"**Giá trị:** {dynamic_data.get('tactic-voucher-value', 'N/A')}")
                        st.success(
                            f"**Đơn tối thiểu:** {dynamic_data.get('tactic-voucher-min', 'N/A')} VNĐ")
                    st.warning(
                        f"**Lượt dùng tối đa:** {dynamic_data.get('tactic-voucher-limit', 'N/A')} lượt")

                # Flash Sale
                elif 'flash' in tactic_id.lower():
                    st.markdown("#### ⚡ Thông tin Flash Sale")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(
                            f"**Sản phẩm:** {dynamic_data.get('tactic-fs-product', 'N/A')}")
                        st.success(
                            f"**Giá sale:** {dynamic_data.get('tactic-fs-price', 'N/A')} VNĐ")
                    with col2:
                        st.warning(
                            f"**Số lượng:** {dynamic_data.get('tactic-fs-limit', 'N/A')} sản phẩm")
                        st.info(
                            f"**Thời gian:** {dynamic_data.get('tactic-fs-date', 'N/A')} {dynamic_data.get('tactic-fs-time', '')}")

                # Ads
                elif 'ads' in tactic_id.lower():
                    st.markdown("#### 📱 Thông tin Quảng Cáo")
                    st.info(
                        f"**Sản phẩm quảng cáo:** {dynamic_data.get('tactic-ads-product', 'N/A')}")
                    st.success(
                        f"**Từ khóa:** {dynamic_data.get('tactic-ads-keywords', 'N/A')}")
                    st.warning(
                        f"**CPC mong muốn:** {dynamic_data.get('tactic-ads-cpc', 'N/A')} VNĐ")

                # Livestream
                elif 'livestream' in tactic_id.lower():
                    st.markdown("#### 📺 Thông tin Livestream")
                    st.info(
                        f"**Tiêu đề:** {dynamic_data.get('tactic-live-title', 'N/A')}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.success(
                            f"**Ngày:** {dynamic_data.get('tactic-live-date', 'N/A')}")
                    with col2:
                        st.success(
                            f"**Giờ:** {dynamic_data.get('tactic-live-time', 'N/A')}")
                    if dynamic_data.get('tactic-live-script'):
                        st.text_area("Kịch bản:", dynamic_data.get(
                            'tactic-live-script', 'N/A'), height=100, disabled=True)

                # Combo
                elif 'combo' in tactic_id.lower():
                    st.markdown("#### 📦 Thông tin Combo Deal")
                    st.info(
                        f"**Sản phẩm chính:** {dynamic_data.get('tactic-combo-main', 'N/A')}")
                    st.info(
                        f"**Sản phẩm phụ:** {dynamic_data.get('tactic-combo-sub', 'N/A')}")
                    st.success(
                        f"**Giá combo:** {dynamic_data.get('tactic-combo-price', 'N/A')} VNĐ")

                # Default
                else:
                    st.markdown("#### ⚙️ Cấu hình chi tiết")
                    for key, value in dynamic_data.items():
                        if key.startswith('tactic-') and value:
                            display_key = key.replace(
                                'tactic-', '').replace('-', ' ').title()
                            st.write(f"**{display_key}:** {value}")

        # Nút đóng
        st.divider()
        if st.button("✖️ Đóng", use_container_width=True):
            st.session_state.show_demo_modal = False
            st.rerun()

    # Gọi dialog
    show_demo_dialog()


def render_dashboard_view():
    """Dashboard chính"""
    # Xử lý thông báo sau khi kích hoạt
    if st.session_state.get('need_rerun', False):
        st.session_state['need_rerun'] = False

        if 'activation_message' in st.session_state:
            msg = st.session_state['activation_message']
            msg_type = msg.get('type', 'info')
            msg_text = msg.get('text', '')

            if msg_type == 'success':
                st.success(msg_text)
            elif msg_type == 'warning':
                st.warning(msg_text)
            elif msg_type == 'error':
                st.error(msg_text)
            else:
                st.info(msg_text)

            del st.session_state['activation_message']

    st.header("📊 Bước 6: Quản trị Hiệu suất & Tối ưu", divider="blue")
    st.write("Theo dõi hiệu suất của tất cả các chiến dịch đã lưu trong CSDL")

    if 'editing_campaign_id' in st.session_state:
        render_result_modal()

    if 'demo_campaign_id_dashboard' in st.session_state:
        render_dashboard_demo_modal()

    campaigns = st.session_state.campaigns
    if not campaigns:
        st.info("ℹ️ Chưa có chiến dịch nào. Hãy tạo chiến dịch mới!")
        return

    cols = st.columns([3, 2, 1, 1, 1, 1, 1, 1])
    headers = ["Tên Chiến Dịch", "Phân Khúc", "Ngân Sách",
               "Doanh Thu", "ROI", "Hành Động", "Trạng Thái", "Demo"]
    for col, header in zip(cols, headers):
        col.markdown(f"**{header}**")

    st.divider()

    for i, campaign in enumerate(campaigns):
        budget = campaign.get('budget', 0)
        revenue = campaign.get('revenue', 0)
        roi = "N/A"
        roi_color = "gray"

        if budget > 0:
            roi_val = ((revenue - budget) / budget) * 100
            roi = f"{roi_val:.0f}%"
            roi_color = "green" if roi_val >= 0 else "red"
        elif revenue > 0:
            roi = "∞"
            roi_color = "green"

        cols = st.columns([3, 2, 1, 1, 1, 1, 1, 1])

        cols[0].markdown(f"**{campaign.get('name', 'N/A')}**")
        cols[0].caption(f"{campaign.get('tactic', 'N/A')}")

        cols[1].write(campaign.get('segment', 'N/A'))
        cols[2].write(format_currency(budget))
        cols[3].write(format_currency(revenue))
        cols[4].markdown(
            f"<span style='color:{roi_color}; font-weight:bold;'>{roi}</span>", unsafe_allow_html=True)

        campaign_id = campaign['id']
        campaign_status = campaign.get('status', 'N/A')

        with cols[5]:
            if campaign_status == '📝 Đã lưu':
                st.button("▶️ Kích hoạt", key=f"act_{i}", on_click=activate_campaign, args=(
                    campaign_id,), use_container_width=True)
            elif campaign_status == '🟢 Đang chạy':
                st.button("📝 Nhập KQ", key=f"res_{i}", on_click=show_result_modal, args=(
                    campaign_id,), use_container_width=True)
            elif campaign_status == '🟡 Đã kết thúc':
                st.button("✏️ Xem/Sửa", key=f"res_{i}", on_click=show_result_modal, args=(
                    campaign_id,), use_container_width=True)

        cols[6].write(campaign_status)

        with cols[7]:
            if st.button("👁️", key=f"demo_{i}", help="Xem demo", use_container_width=True):
                st.session_state.demo_campaign_id_dashboard = campaign_id
                # st.rerun()

        st.divider()


def render_dashboard_demo_modal():
    """Modal demo trên dashboard"""
    campaign_id = st.session_state.demo_campaign_id_dashboard
    campaign = next(
        (c for c in st.session_state.campaigns if c['id'] == campaign_id), None)

    if not campaign:
        del st.session_state.demo_campaign_id_dashboard
        return

    @st.dialog("🎬 Demo Chiến Dịch", width="large")
    def show_dashboard_demo():
        st.header(f"📧 {campaign.get('name')}")
        st.subheader(f"🎯 {campaign.get('objective')}")
        st.divider()

        dynamic_data = campaign.get('dynamicData', {})
        platform = campaign.get('platform')

        if platform == 'owned':
            subject = dynamic_data.get(
                'tactic-email-subject', 'Chưa có tiêu đề')
            image_data = dynamic_data.get('tactic-email-image', '')
            body = dynamic_data.get('tactic-email-body', 'Chưa có nội dung')
            button_text = dynamic_data.get(
                'tactic-email-button-text', 'Xem ngay')
            button_url = dynamic_data.get('tactic-email-button-url', '#')

            st.markdown("### 📬 Email đã gửi đến khách hàng:")

            # Container preview email
            with st.container():
                # Header
                st.markdown(f"""
                <div style='
                    background: #f8f9fa;
                    padding: 15px 20px;
                    border-radius: 8px 8px 0 0;
                    border: 1px solid #dee2e6;
                    border-bottom: 2px solid #28a745;
                '>
                    <strong style='color: #333; font-size: 18px;'>📧 {subject}</strong>
                </div>
                """, unsafe_allow_html=True)

                # Banner nếu có
                if image_data:
                    st.markdown(f"""
                    <div style='
                        text-align: center;
                        padding: 10px;
                        background: white;
                        border-left: 1px solid #dee2e6;
                        border-right: 1px solid #dee2e6;
                    '>
                        <img src="{image_data}" style='
                            max-width: 80%;
                            height: 70%;
                            border-radius: 8px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        '>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style='
                        background: #e9ecef;
                        padding: 60px 20px;
                        text-align: center;
                        color: #6c757d;
                        border-left: 1px solid #dee2e6;
                        border-right: 1px solid #dee2e6;
                    '>
                        <p style='font-size: 40px; margin: 0;'>🖼️</p>
                        <p style='margin: 10px 0 0 0;'>Không có ảnh banner</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Content
                st.markdown(f"""
                <div style='
                    background: white;
                    padding: 30px 20px;
                    border-left: 1px solid #dee2e6;
                    border-right: 1px solid #dee2e6;
                '>
                    <p style='color: #495057; font-size: 15px; line-height: 1.8; margin: 0 0 15px 0;'>
                        Xin chào,
                    </p>
                    <p style='color: #495057; font-size: 15px; line-height: 1.8; margin: 0;'>
                        {body.replace(chr(10), '<br>')}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # CTA Button
                st.markdown(f"""
                <div style='
                    background: white;
                    padding: 20px;
                    text-align: center;
                    border-left: 1px solid #dee2e6;
                    border-right: 1px solid #dee2e6;
                '>
                    <a href='{button_url}' style='
                        display: inline-block;
                        background: #28a745;
                        color: white;
                        padding: 12px 30px;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 16px;
                    '>{button_text}</a>
                </div>
                """, unsafe_allow_html=True)

                # Footer
                st.markdown("""
                <div style='
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    border: 1px solid #dee2e6;
                    border-radius: 0 0 8px 8px;
                '>
                    <p style='color: #6c757d; font-size: 13px; margin: 0;'>
                        Trân trọng,<br>
                        <strong>Đội ngũ Marketing</strong>
                    </p>
                </div>
                """, unsafe_allow_html=True)

            st.success("✅ Email này đã được gửi đến khách hàng trong phân khúc")
        else:
            st.markdown("### ⚙️ Cấu hình chi tiết:")
            st.json(dynamic_data, expanded=True)
        st.divider()
        if st.button("✖️ Đóng", use_container_width=True):
            del st.session_state.demo_campaign_id_dashboard
            # st.rerun()
    show_dashboard_demo()


def render_result_modal():
    """Modal nhập kết quả"""
    if 'editing_campaign_id' in st.session_state:
        campaign_id = st.session_state.editing_campaign_id
        campaign = next(
            (c for c in st.session_state.campaigns if c['id'] == campaign_id), None)

        if campaign:
            @st.dialog("💰 Nhập Kết Quả Thực Tế", width="medium")
            def show_result_dialog():
                st.write(
                    f"Nhập doanh thu thực tế từ chiến dịch **{campaign['name']}** để tính toán ROI.")

                revenue = st.number_input(
                    "💵 Doanh thu Thực tế (VNĐ)",
                    min_value=0,
                    value=int(campaign['revenue']
                              ) if campaign['revenue'] > 0 else 0,
                    step=100000,
                    key=f"revenue_input_{campaign_id}"
                )

                cols = st.columns(2)
                if cols[0].button("💾 Lưu Kết Quả", type="primary", use_container_width=True):
                    save_campaign_result(campaign_id, revenue)
                if cols[1].button("✖️ Hủy bỏ", use_container_width=True):
                    del st.session_state.editing_campaign_id
                    # st.rerun()

            show_result_dialog()


def show():
    """Hàm chính được gọi bởi app.py"""
    init_campaign_db()
    init_state()
    render_header_and_nav()

    if st.session_state.view == 'wizard':
        render_stepper()
        st.divider()

        step = st.session_state.current_step
        if step == 1:
            render_step_1()
        elif step == 2:
            render_step_2()
        elif step == 3:
            render_step_3()
        elif step == 4:
            render_step_4()
        elif step == 5:
            render_step_5()

    elif st.session_state.view == 'dashboard':
        st.session_state.current_step = 6
        render_stepper()
        st.divider()
        render_dashboard_view()


if __name__ == "__main__":
    st.set_page_config(
        layout="wide", page_title="Module Chiến dịch Marketing", page_icon="🎯")
    show()
