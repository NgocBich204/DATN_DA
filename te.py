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

# --- CẤU HÌNH KẾT NỐI SQL SERVER ---
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

# --- DỮ LIỆU CẤU HÌNH (BUSINESS LOGIC) ---
config_data = {
    "objectives": [
        {'id': 'revenue', 'icon': '💰', 'title': 'Tối ưu hóa Doanh thu', 'description': 'Thúc đẩy doanh số từ tệp KH hiện tại, đặc biệt là nhóm có giá trị cao.'},
        {'id': 'awareness', 'icon': '🚀', 'title': 'Tăng Nhận diện & Tương tác', 'description': 'Tiếp cận và tái tương tác với các phân khúc khách hàng hiện có.'},
        {'id': 'conversion', 'icon': '🎯', 'title': 'Gia tăng Tỷ lệ Chuyển đổi', 'description': 'Tối ưu hóa hành trình khách hàng và xử lý các "điểm nghẽn".'},
        {'id': 'launch', 'icon': '✨', 'title': 'Ra mắt Sản phẩm Mới', 'description': 'Giới thiệu SP mới đến các PK có khả năng tiếp nhận cao .'}
    ],
    
    "mockDataOwned": {
        "segments": {
            'revenue': ['Khách hàng VIP'],
            'conversion': ['Khách hàng mới', 'Khách hàng tiềm năng'],
            'awareness': ['Khách hàng có nguy cơ mất', 'Khách hàng yếu'],
            'launch': ['Khách hàng VIP', 'Khách hàng trung thành']
        },
        "tactics": {
            'Khách hàng VIP': {
                'owned': [
                    {'id': 'privilege', 'name': 'Chương trình Đặc quyền (Không giảm giá)', 'desc': 'Early Access, Quà tặng Sinh nhật Vật lý, Freeship Vĩnh viễn.'},
                    {'id': 'upsell_email', 'name': 'Chiến dịch Upsell Cá nhân hóa', 'desc': 'Gửi email tự động giới thiệu sản phẩm cao cấp, phiên bản giới hạn.'},
                    {'id': 'referral', 'name': 'Chương trình Giới thiệu (Referral)', 'desc': 'Biến họ thành đại sứ. Tặng mã giới thiệu cho bạn bè.'}
                ], 'marketplace': []
            },
            'Khách hàng mới': {
                'owned': [
                    {'id': 'onboarding', 'name': 'Chuỗi Email/Zalo Onboarding (Tự động)', 'desc': 'Ngày 1: Cảm ơn, Ngày 3: Cộng đồng, Ngày 7: Mã giảm giá 15% (hạn 3 ngày).'},
                    {'id': 'web_welcome', 'name': 'Cá nhân hóa Trải nghiệm Web', 'desc': 'Hiển thị Popup "Chào mừng trở lại! Dùng mã [WELCOME15]..."'}
                ], 'marketplace': []
            },
            'Khách hàng tiềm năng': {
                 'owned': [
                    {'id': 'onboarding', 'name': 'Chuỗi Email/Zalo Onboarding (Tự động)', 'desc': 'Ngày 1: Cảm ơn, Ngày 3: Cộng đồng, Ngày 7: Mã giảm giá 15% (hạn 3 ngày).'},
                ], 'marketplace': []
            },
            'Khách hàng có nguy cơ mất': {
                'owned': [
                    {'id': 'win_back', 'name': 'Chiến dịch "Win-back" Tự động', 'desc': 'Gửi Email/SMS "Chúng tôi nhớ bạn!" với mã giảm giá giá trị cao (25% hoặc M1T1).'},
                    {'id': 'remarketing_multi', 'name': 'Remarketing Đa nền tảng', 'desc': 'Đẩy tệp email/SĐT sang Facebook/Google Ads với thông điệp BST Mới.'},
                    {'id': 'survey', 'name': 'Khảo sát Khách hàng', 'desc': 'Gửi email khảo sát "Tại sao bạn chưa quay lại?" và tặng voucher 50k.'}
                ], 'marketplace': []
            },
            'Khách hàng yếu': {
                 'owned': [
                    {'id': 'win_back', 'name': 'Chiến dịch "Win-back" Tự động', 'desc': 'Gửi Email/SMS "Chúng tôi nhớ bạn!" với mã giảm giá giá trị cao (25% hoặc M1T1).'},
                ], 'marketplace': []
            },
            'Khách hàng trung thành': {
                'owned': [
                    {'id': 'early_access', 'name': 'Mở bán Sớm (Exclusive Early Access)', 'desc': 'Gửi email/Zalo cho cụm này mua trước công chúng 1-2 ngày.'},
                    {'id': 'cross_sell', 'name': 'Tạo Combo Bán chéo (Cross-sell)', 'desc': 'Tạo combo "Sản phẩm mới + Sản phẩm bán chạy nhất (mà họ hay mua)".'},
                ], 'marketplace': []
            }
        },
        "tacticRecommendations": {
            'Khách hàng VIP': ['privilege', 'upsell_email', 'referral'],
            'Khách hàng mới': ['onboarding', 'web_welcome'],
            'Khách hàng tiềm năng': ['onboarding'],
            'Khách hàng có nguy cơ mất': ['win_back', 'remarketing_multi', 'survey'],
            'Khách hàng yếu': ['win_back'],
            'Khách hàng trung thành': ['early_access', 'cross_sell']
        }
    },
    
    "mockDataMarketplace": {
        "tactics": {
            'owned': [],
            'marketplace': [
                {'id': 'mp_ads', 'name': 'Quảng cáo trả phí (Ads)', 'desc': 'Tiếp thị lại (Cụm Mới) hoặc Tìm kiếm (tệp mới).'},
                {'id': 'mp_flash_sale', 'name': 'Flash Sale', 'desc': 'Kích hoạt Cụm Nguy cơ và Cụm Đã mất.'},
                {'id': 'mp_voucher', 'name': 'Voucher / Coupon', 'desc': 'Công cụ linh hoạt: Gửi chat (VIP) hoặc Follower (Mới).'},
                {'id': 'mp_livestream', 'name': 'Livestream', 'desc': 'Tương tác & chốt đơn tệp Trung thành, Nguy cơ, Mới.'},
                {'id': 'mp_combo', 'name': 'Combo mua kèm (Bundle Deals)', 'desc': 'Tăng AOV cho tất cả các cụm, đặc biệt là VIP, Trung thành.'}
            ]
        }
    }
}

# --- HÀM XỬ LÝ HÌNH ẢNH ---
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

# --- CÁC HÀM TƯƠNG TÁC VỚI DATABASE ---
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
        df = pd.read_sql("SELECT * FROM Campaign_Manager_UX ORDER BY CampaignID DESC", conn)
        
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
            campaign['dynamicData'] = json.loads(campaign.pop('DynamicData')) if campaign.get('DynamicData') else {}
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

def save_campaign_to_db(form_data, session_data):
    """Lưu chiến dịch mới vào CSDL."""
    conn = get_db_connection()
    if not conn: return False
    
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
            float(form_data['campaign-budget']) if form_data['campaign-budget'] else 0,
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
    if not conn: return
        
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
    if not conn: return []
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

# --- KHỞI TẠO TRẠNG THÁI ---
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
    st.rerun()

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

# --- CÁC HÀM XỬ LÝ LOGIC ---
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

            rich_percentage = df_real_segments[df_real_segments['PhanKhuc'].isin(map_rich)]['SoLuong'].sum() / total_customers * 100
            at_risk_percentage = df_real_segments[df_real_segments['PhanKhuc'].isin(map_at_risk)]['SoLuong'].sum() / total_customers * 100
            new_percentage = df_real_segments[df_real_segments['PhanKhuc'].isin(map_new)]['SoLuong'].sum() / total_customers * 100
            only_new_percentage = df_real_segments[df_real_segments['PhanKhuc'] == 'Khách hàng mới']['SoLuong'].sum() / total_customers * 100

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

        st.session_state.selected_segment = {'id': 'marketplace_logic', 'name': f"Logic: {logic_name}"}
        go_to_step(4)

def select_segment(segment_id, segment_name):
    st.session_state.selected_segment = {'id': segment_id, 'name': segment_name}
    go_to_step(4)

def select_tactic(tactic_id, tactic_name, tactic_type):
    st.session_state.selected_tactic = {'id': tactic_id, 'name': tactic_name, 'type': tactic_type}
    go_to_step(5)

def handle_save_campaign(form_data):
    session_data = {
        'platform': st.session_state.selected_platform,
        'objective': st.session_state.selected_objective,
        'segment': st.session_state.selected_segment,
        'tactic': st.session_state.selected_tactic,
    }
    
    # Thu thập dynamic data và xử lý UploadedFile
    dynamic_data = {}
    for k, v in st.session_state.items():
        if k.startswith('tactic-'):
            # Bỏ qua UploadedFile object (key có '-uploader')
            if k.endswith('-uploader'):
                continue
            # Các giá trị khác giữ nguyên (đã được xử lý trong render_dynamic_form)
            dynamic_data[k] = v
    
    form_data['dynamicData'] = dynamic_data

    success = save_campaign_to_db(form_data, session_data)
    
    if success:
        st.toast(f"Đã lưu chiến dịch: {form_data['campaign-name']}", icon="✅")
        st.cache_data.clear()
        st.session_state.campaigns = load_campaigns_from_db()
        go_to_view('dashboard')
        st.session_state.current_step = 6
    else:
        st.error("Lưu chiến dịch thất bại. Vui lòng kiểm tra lại.")

def build_html_email(data):
    """Xây dựng nội dung email HTML từ dynamicData."""
    subject = data.get('tactic-email-subject', "Một thông báo mới từ chúng tôi")
    image_data = data.get('tactic-email-image', '')
    body = data.get('tactic-email-body', 'Đây là nội dung email của bạn.')
    button_text = data.get('tactic-email-button-text', 'Xem ngay')
    button_url = data.get('tactic-email-button-url', '#')
    
    body_text = body.replace('\n', '<br>')
    
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
            {"<img src='" + image_data + "' alt='Banner' class='banner'>" if image_data else ""}
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
    try:
        config = st.secrets.email
        sender_email = config.sender_email
        sender_password = config.sender_password
        smtp_server = config.smtp_server
        smtp_port = int(config.smtp_port)
    except Exception:
        st.error("Lỗi: Không tìm thấy cấu hình email trong file .streamlit/secrets.toml.")
        return False

    dynamic_data = campaign.get('dynamicData', {})
    subject, plain_text_body, html_body = build_html_email(dynamic_data)
    
    context = ssl.create_default_context()
    try:
        emails_to_send = email_list[:5] 
        st.warning(f"Đang gửi {len(emails_to_send)} email (Giới hạn 5 email cho demo). Tổng tệp: {len(email_list)} KH.")
        
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
            
            if len(email_list) > 5:
                st.info(f"Đã gửi 5 email demo. (Bỏ qua {len(email_list) - 5} email còn lại).")

        return True
    except smtplib.SMTPException as e:
        st.error(f"Lỗi SMTP: {e}")
        return False
    except Exception as e:
        st.error(f"Lỗi khi gửi email: {e}")
        return False

def activate_campaign(campaign_id):
    """Kích hoạt và Gửi Email."""
    campaign = next((c for c in st.session_state.campaigns if c['id'] == campaign_id), None)
    if not campaign:
        st.error("Không tìm thấy chiến dịch!")
        return

    segment_name = campaign.get('segment')
    if not segment_name or st.session_state.selected_platform != 'owned' or not campaign.get('dynamicData'):
        st.info("Chiến dịch này không phải 'Kênh Sở Hữu' hoặc chưa thiết kế nội dung email. Chỉ kích hoạt trạng thái.")
    else:
        with st.spinner(f"Đang lấy danh sách email cho phân khúc: {segment_name}..."):
            email_list = get_emails_for_segment(segment_name)
        
        if not email_list:
            st.error(f"Không tìm thấy email nào cho phân khúc '{segment_name}'. Chiến dịch vẫn sẽ được kích hoạt.")
        else:
            with st.spinner(f"Đang gửi email đến {len(email_list)} khách hàng..."):
                success = send_email_campaign(campaign, email_list)
                if not success:
                    st.warning("Gửi email thất bại, nhưng chiến dịch VẪN ĐƯỢC KÍCH HOẠT.")
                else:
                    st.success(f"Đã gửi {min(len(email_list), 5)} email demo thành công.")

    update_campaign_status_in_db(campaign_id, '🟢 Đang chạy')
    st.session_state.campaigns = load_campaigns_from_db()
    st.toast(f"Đã kích hoạt chiến dịch", icon="🚀")
    st.rerun()

def show_result_modal(campaign_id):
    st.session_state.editing_campaign_id = campaign_id

def save_campaign_result(campaign_id, revenue):
    update_campaign_status_in_db(campaign_id, '🟡 Đã kết thúc', new_revenue=revenue)
    st.session_state.campaigns = load_campaigns_from_db()
    st.toast(f"Đã cập nhật doanh thu", icon="💰")
    
    if 'editing_campaign_id' in st.session_state:
        del st.session_state.editing_campaign_id
    st.rerun()

# --- CÁC HÀM RENDER UI ---
def render_header_and_nav():
    cols = st.columns([3, 1])
    with cols[0]:
        st.title("Module Đề Xuất Chiến Lược")
        st.caption("Vận hành chiến lược marketing cá nhân hóa đa kênh (Phiên bản dữ liệu thật)")
    
    with cols[1]:
        nav_cols = st.columns(2)
        with nav_cols[0]:
            st.button(
                "Tạo Chiến Dịch Mới", 
                on_click=go_to_view, 
                args=('wizard',), 
                use_container_width=True,
                type="primary" if st.session_state.view == 'wizard' else "secondary"
            )
        with nav_cols[1]:
            st.button(
                f"Xem Dashboard ({len(st.session_state.campaigns)})", 
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
    
    valid_steps = [1, 2, 4, 5, 6] if platform == 'marketplace' else [1, 2, 3, 4, 5, 6]
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
                st.markdown(f"<span style='color:grey;'>{step_num}. {step_name}</span>", unsafe_allow_html=True)

def render_step_1():
    st.header("Bước 1: Chọn Nền Tảng Kinh Doanh Chính", divider="blue")
    st.write("Khách hàng của bạn chủ yếu đang ở đâu? Điều này sẽ giúp hệ thống đề xuất kịch bản phù hợp.")
    
    cols = st.columns(2)
    with cols[0]:
        with st.container(border=True):
            st.markdown("### 🌐 Kênh Sở Hữu (Owned)")
            st.write("Doanh nghiệp của tôi có Website, App, CRM riêng và muốn cá nhân hóa trải nghiệm trên các kênh này (Email, Zalo, Web Popup...).")
            st.button("Chọn Kênh Sở Hữu", on_click=select_platform, args=('owned',), use_container_width=True, type="primary")

    with cols[1]:
        with st.container(border=True):
            st.markdown("### 🛍️ Kênh Sàn TMĐT (Marketplace)")
            st.write("Doanh nghiệp của tôi kinh doanh chủ yếu trên các sàn như Shopee, Lazada, Tiki... và muốn tận dụng các công cụ của sàn (Ads, Voucher, Livestream).")
            st.button("Chọn Sàn TMĐT", on_click=select_platform, args=('marketplace',), use_container_width=True, type="primary")

def render_step_2():
    st.button("⬅️ Quay lại chọn Nền Tảng", on_click=go_to_step, args=(1,))
    
    if st.session_state.selected_platform == 'owned':
        st.header("Bước 2: Xác định Mục tiêu Chiến lược (The 'Why')", divider="blue")
        st.write("Chọn mục tiêu kinh doanh cốt lõi để hệ thống đề xuất phân khúc khách hàng phù hợp.")
    else:
        st.header("Bước 2: Hiện trạng Dashboard & Chọn Mục tiêu", divider="blue")
        st.write("Hệ thống đã phân tích dữ liệu khách hàng từ CSDL. Hãy xem hiện trạng và chọn mục tiêu bạn muốn ưu tiên.")
        
        with st.container(border=True):
            st.subheader("Hiện trạng Phân khúc Khách hàng (Từ CSDL)")
            
            df_real = st.session_state.real_segment_data
            if df_real.empty:
                st.error("Không tải được dữ liệu phân khúc thật.")
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
                
                df_real['percentage'] = (df_real['SoLuong'] / df_real['SoLuong'].sum()) * 100
                df_real['color'] = df_real['PhanKhuc'].map(color_map).fillna('#9CA3AF')
                
                distribution = df_real.to_dict('records')
                percentages = [d['percentage'] for d in distribution]
                colors = [d['color'] for d in distribution]
                
                sorted_data = sorted(zip(percentages, colors, distribution), key=lambda x: x[0], reverse=True)
                
                bar_cols = st.columns([p for p, c, d in sorted_data])
                for i, (p, c, d) in enumerate(sorted_data):
                    with bar_cols[i]:
                        st.markdown(f"<div style='background-color:{c}; height: 20px; border-radius: 2px;' title='{d['PhanKhuc']}: {d['percentage']:.1f}%'></div>", unsafe_allow_html=True)
                
                legend_cols = st.columns(len(distribution))
                for i, (p, c, d) in enumerate(sorted_data):
                    with legend_cols[i]:
                        st.markdown(f"<span style='color:{c};'>●</span> **{d['PhanKhuc']}**: {d['percentage']:.1f}% ({d['SoLuong']} KH)", unsafe_allow_html=True)

        st.divider()
        st.subheader("Dựa trên dữ liệu trên, hãy chọn một mục tiêu:")

    objectives = config_data["objectives"]
    cols = st.columns(len(objectives))
    for i, goal in enumerate(objectives):
        with cols[i % len(objectives)]:
            with st.container(border=True):
                st.markdown(f"### {goal['icon']} {goal['title']}")
                st.write(goal['description'])
                st.button(f"Chọn mục tiêu: {goal['title']}", on_click=select_objective, args=(goal['id'], goal['title']), use_container_width=True, key=f"goal_{goal['id']}")

def render_step_3():
    st.button("⬅️ Quay lại chọn Mục tiêu", on_click=go_to_step, args=(2,))
    st.header("Bước 3: Đề xuất Phân khúc Đối tượng (The 'Who')", divider="blue")
    st.write(f"Dựa trên mục tiêu **{st.session_state.selected_objective['title']}**, hệ thống đề xuất các phân khúc sau (từ CSDL):")
    
    goal_id = st.session_state.selected_objective['id']
    segment_names = config_data["mockDataOwned"]["segments"].get(goal_id, [])
    
    df_real = st.session_state.real_segment_data
    if df_real.empty:
        st.error("Không tải được dữ liệu phân khúc thật.")
        return
        
    segments_to_show = df_real[df_real['PhanKhuc'].isin(segment_names)]
    
    if segments_to_show.empty:
        st.warning("Không tìm thấy phân khúc đề xuất trong CSDL cho mục tiêu này.")
        return

    icon_map = {
        'Khách hàng VIP': '👑',
        'Khách hàng trung thành': '💎',
        'Khách hàng ổn định': '👍',
        'Khách hàng tiềm năng': '🌱',
        'Khách hàng mới': '✨',
        'Khách hàng có nguy cơ mất': '😟',
        'Khách hàng yếu': '💔'
    }

    for _, segment in segments_to_show.iterrows():
        seg_name = segment['PhanKhuc']
        seg_icon = icon_map.get(seg_name, '👥')
        
        with st.container(border=True):
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"### {seg_icon} {seg_name}")
                st.caption(f"Định nghĩa (Trung bình): R={segment['R_TB']:.0f} ngày | F={segment['F_TB']:.1f} lần | M={format_currency(segment['M_TB'])}")
            with cols[1]:
                st.button(f"Chọn tệp {seg_name}", on_click=select_segment, args=(seg_name, seg_name), use_container_width=True, type="primary", key=f"seg_{seg_name}")
            
            st.markdown(f"**Thông tin chi tiết (từ CSDL):**")
            detail_cols = st.columns(3)
            detail_cols[0].metric("Số lượng Khách hàng", f"{segment['SoLuong']} KH")
            detail_cols[1].metric("Tổng Doanh thu", format_currency(segment['TongDoanhThu']))
            detail_cols[2].metric("Doanh thu / KH", format_currency(segment['M_TB']))

def render_step_4():
    back_step = 2 if st.session_state.selected_platform == 'marketplace' else 3
    back_text = "⬅️ Quay lại Dashboard & Mục tiêu" if back_step == 2 else "⬅️ Quay lại chọn Phân khúc"
    st.button(back_text, on_click=go_to_step, args=(back_step,))

    st.header("Bước 4: Đề xuất Kịch bản & Chiến thuật (The 'How')", divider="blue")
    st.write(f"Chọn một kịch bản/chiến thuật cho **{st.session_state.selected_segment['name']}**.")

    if st.session_state.selected_platform == 'owned':
        render_step_4_owned()
    else:
        render_step_4_marketplace()

def render_step_4_owned():
    segment_id = st.session_state.selected_segment['id']
    tactics_data = config_data["mockDataOwned"]["tactics"].get(segment_id, {})
    owned_tactics = tactics_data.get('owned', [])
    recommendations = config_data["mockDataOwned"]["tacticRecommendations"].get(segment_id, [])

    st.subheader("A. Kênh sở hữu (Owned Channels)")
    st.write("Tập trung vào cá nhân hóa sâu và tự động hóa trên website, app, CRM.")
    
    if not owned_tactics:
        st.info("Không có chiến thuật nào được định nghĩa cho phân khúc này.")
        return

    for tactic in owned_tactics:
        is_recommended = tactic['id'] in recommendations
        
        with st.container(border=is_recommended):
            if is_recommended:
                st.markdown("**⭐ ĐỀ XUẤT**")
            st.markdown(f"**{tactic['name']}**")
            st.write(tactic['desc'])
            st.button(
                "Thiết Kế Chiến Dịch", 
                on_click=select_tactic, 
                args=(tactic['id'], tactic['name'], 'owned'), 
                use_container_width=True,
                key=f"tactic_{tactic['id']}",
                type="primary" if is_recommended else "secondary"
            )

def render_step_4_marketplace():
    all_tactics = config_data["mockDataMarketplace"]["tactics"]["marketplace"]
    goal_id = st.session_state.selected_objective['id']
    df_real = st.session_state.real_segment_data
    
    recommendations = []
    
    if not df_real.empty:
        total_customers = df_real['SoLuong'].sum()
        map_rich = ['Khách hàng VIP', 'Khách hàng trung thành']
        map_at_risk = ['Khách hàng có nguy cơ mất', 'Khách hàng yếu']
        map_new = ['Khách hàng mới', 'Khách hàng tiềm năng']

        rich_percentage = df_real[df_real['PhanKhuc'].isin(map_rich)]['SoLuong'].sum() / total_customers * 100
        at_risk_percentage = df_real[df_real['PhanKhuc'].isin(map_at_risk)]['SoLuong'].sum() / total_customers * 100
        new_percentage = df_real[df_real['PhanKhuc'].isin(map_new)]['SoLuong'].sum() / total_customers * 100
        only_new_percentage = df_real[df_real['PhanKhuc'] == 'Khách hàng mới']['SoLuong'].sum() / total_customers * 100

        if goal_id == 'revenue' and rich_percentage > 30:
            recommendations = ['mp_voucher', 'mp_combo', 'mp_livestream']
        elif goal_id == 'awareness' and at_risk_percentage > 30:
            recommendations = ['mp_flash_sale', 'mp_livestream', 'mp_voucher']
        elif goal_id == 'conversion' and (new_percentage > 40 or only_new_percentage > 20):
            recommendations = ['mp_ads', 'mp_voucher', 'mp_combo']
        elif goal_id == 'launch':
            recommendations = ['mp_livestream', 'mp_ads', 'mp_voucher']
        else:
            if goal_id == 'revenue': recommendations = ['mp_combo', 'mp_voucher']
            elif goal_id == 'conversion': recommendations = ['mp_ads', 'mp_voucher']
            elif goal_id == 'awareness': recommendations = ['mp_flash_sale', 'mp_livestream']
            elif goal_id == 'launch': recommendations = ['mp_livestream', 'mp_ads', 'mp_voucher']
            
    st.subheader("B. Kênh Sàn TMĐT (Marketplace)")
    st.write("Tận dụng các công cụ có sẵn của Shopee, Lazada, v.v.")

    for tactic in all_tactics:
        is_recommended = tactic['id'] in recommendations
        
        with st.container(border=is_recommended):
            if is_recommended:
                st.markdown("**⭐ ĐỀ XUẤT**")
            st.markdown(f"**{tactic['name']}**")
            st.write(tactic['desc'])
            st.button(
                "Thiết Kế Chiến Dịch", 
                on_click=select_tactic, 
                args=(tactic['id'], tactic['name'], 'marketplace'), 
                use_container_width=True,
                key=f"tactic_{tactic['id']}",
                type="primary" if is_recommended else "secondary"
            )

def render_dynamic_form(tactic_id, tactic_type):
    st.subheader(f"Cấu hình chi tiết: {st.session_state.selected_tactic['name']}", divider="blue")

    if tactic_type == 'owned':
        st.multiselect("Kênh chạy", ["Email", "SMS", "Zalo OA"], default=["Email"], key="tactic-owned-channels")
        st.text_input("Tiêu đề Email", placeholder="Ưu đãi đặc biệt dành riêng cho bạn!", key="tactic-email-subject")
        
        # THAY ĐỔI CHÍNH: Upload ảnh thay vì link
        uploaded_file = st.file_uploader(
            "Tải lên hình ảnh Banner", 
            type=['png', 'jpg', 'jpeg', 'gif'],
            key="tactic-email-image-uploader",
            help="Chọn file ảnh từ máy tính của bạn"
        )
        
        # Xử lý ảnh upload và lưu vào session state
        if uploaded_file is not None:
            image_base64 = image_to_base64(uploaded_file)
            if image_base64:
                st.session_state['tactic-email-image'] = image_base64
                st.success("✅ Đã tải ảnh thành công!")
                # Hiển thị preview nhỏ
                st.image(uploaded_file, caption="Preview", width=200)
        elif 'tactic-email-image' not in st.session_state:
            st.session_state['tactic-email-image'] = ''
        
        st.text_area("Nội dung tin nhắn", placeholder="Chào bạn,\n\nChúng tôi có một ưu đãi... (Bạn có thể dùng [Tên] để cá nhân hóa)", key="tactic-email-body")
        st.text_input("Tiêu đề nút bấm (CTA)", placeholder="Xem ngay!", key="tactic-email-button-text")
        st.text_input("Link nút bấm (URL)", placeholder="https://shop.com/san-pham-moi", key="tactic-email-button-url")
    
    elif tactic_type == 'marketplace':
        if tactic_id == 'mp_ads':
            st.text_input("Sản phẩm quảng cáo", placeholder="Vd: Áo sơ mi trắng", key="tactic-ads-product")
            st.text_input("Từ khóa mục tiêu (cách nhau bằng dấu phẩy)", placeholder="Vd: áo sơ mi, sơ mi công sở", key="tactic-ads-keywords")
            st.number_input("CPC mong muốn (VNĐ)", min_value=0, step=100, value=1000, key="tactic-ads-cpc")
        
        elif tactic_id == 'mp_flash_sale':
            st.text_input("Sản phẩm tham gia", placeholder="Vd: Giày da nam", key="tactic-fs-product")
            cols = st.columns(2)
            cols[0].number_input("Giá giảm (VNĐ)", min_value=0, value=199000, key="tactic-fs-price")
            cols[1].number_input("Giới hạn số lượng", min_value=0, value=100, key="tactic-fs-limit")
            st.date_input("Ngày Flash Sale", key="tactic-fs-date", value=datetime.date.today())
            st.time_input("Giờ Flash Sale", key="tactic-fs-time", value=datetime.time(12, 0))

        elif tactic_id == 'mp_voucher':
            st.selectbox("Loại Voucher", ["Giảm theo %", "Giảm theo số tiền", "Freeship"], key="tactic-voucher-type")
            cols = st.columns(2)
            cols[0].text_input("Mã giảm giá", placeholder="SHOPVIP10", key="tactic-voucher-code")
            cols[1].number_input("Giá trị (VND hoặc %)", min_value=0, value=10, key="tactic-voucher-value")
            cols = st.columns(2)
            cols[0].number_input("Đơn tối thiểu (VNĐ)", min_value=0, value=99000, key="tactic-voucher-min")
            cols[1].number_input("Lượt dùng tối đa", min_value=0, value=500, key="tactic-voucher-limit")
        
        elif tactic_id == 'mp_livestream':
            st.text_input("Tiêu đề Livestream", placeholder="Siêu Sale 11.11 - Giảm Sốc", key="tactic-live-title")
            st.date_input("Ngày Livestream", key="tactic-live-date", value=datetime.date.today())
            st.time_input("Giờ Livestream", key="tactic-live-time", value=datetime.time(20, 0))
            st.text_area("Kịch bản / Mô tả ngắn", key="tactic-live-script")
            st.text_input("Link sản phẩm ghim (cách nhau bằng dấu phẩy)", placeholder="link1, link2,...", key="tactic-live-products")

        elif tactic_id == 'mp_combo':
            st.text_input("Sản phẩm chính", placeholder="Vd: Áo sơ mi", key="tactic-combo-main")
            st.text_input("Sản phẩm phụ (mua kèm)", placeholder="Vd: Cà vạt", key="tactic-combo-sub")
            st.number_input("Giá combo ưu đãi (VNĐ)", min_value=0, value=249000, key="tactic-combo-price")
        
        else:
            st.info("Chiến thuật này không cần cấu hình chi tiết.")

def render_step_5():
    st.button("⬅️ Quay lại chọn Chiến thuật", on_click=go_to_step, args=(4,))
    st.header("Bước 5: Trình Dựng Chiến Dịch (Campaign Builder)", divider="blue")
    st.write("Cấu hình chi tiết cho chiến dịch của bạn. Dữ liệu sẽ được lưu vào CSDL.")

    # Hiển thị modal demo nếu được kích hoạt
    if st.session_state.get('show_demo_modal', False):
        render_demo_modal()

    with st.container(border=True):
        render_dynamic_form(st.session_state.selected_tactic['id'], st.session_state.selected_tactic['type'])
    
    st.divider()

    with st.form(key="campaign_builder_form"):
        st.subheader("Cấu hình chung")
        form_data = {}
        cols = st.columns(2)
        
        form_data['campaign-name'] = cols[0].text_input(
            "Tên Chiến Dịch", 
            value=f"[{st.session_state.selected_tactic['name']}] - {st.session_state.selected_objective['title']}"
        )
        form_data['campaign-segment'] = cols[1].text_input(
            "Gửi Đến (Phân Khúc / Logic)", 
            value=st.session_state.selected_segment['name'], 
            disabled=True
        )
        
        cols = st.columns(2)
        form_data['campaign-budget'] = cols[0].number_input("Tổng Ngân Sách (VNĐ)", min_value=0, step=100000, value=0)
        form_data['campaign-kpi'] = cols[1].text_input("Mục Tiêu KPI", placeholder="Ví dụ: 50 đơn hàng")
        
        cols = st.columns(2)
        form_data['campaign-start-date'] = cols[0].date_input("Ngày Bắt Đầu", value=datetime.date.today())
        form_data['campaign-end-date'] = cols[1].date_input("Ngày Kết Thúc", value=datetime.date.today() + datetime.timedelta(days=7))
        
        form_data['campaign-notes'] = st.text_area("Ghi Chú Nội Bộ")

        cols_btn = st.columns(2)
        submitted = cols_btn[0].form_submit_button("Lưu Chiến dịch vào CSDL", use_container_width=True, type="primary")
        demo_clicked = cols_btn[1].form_submit_button("Xem Demo Chiến dịch", use_container_width=True, type="secondary")
        
        if submitted:
            for key in st.session_state:
                if key.startswith('tactic-'):
                    form_data[key] = st.session_state[key]
            handle_save_campaign(form_data)
        
        if demo_clicked:
            st.session_state.show_demo_modal = True
            st.rerun()

def render_demo_modal():
    """Hiển thị modal demo cho chiến dịch"""
    
    @st.dialog("🎬 Xem Demo Chiến Dịch", width="large")
    def show_demo_dialog():
        # Thu thập dữ liệu từ session state
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
        st.subheader(f"Chủ đề: {data.get('objective')}")
        st.divider()
        
        platform = data.get('platform')
        
        if platform == 'owned':
            subject = dynamic_data.get('tactic-email-subject', '')
            image_data = dynamic_data.get('tactic-email-image', '')
            body = dynamic_data.get('tactic-email-body', '')
            button_text = dynamic_data.get('tactic-email-button-text', '')
            button_url = dynamic_data.get('tactic-email-button-url', '')
            
            st.markdown("### 📬 Nội dung Email Demo:")
            
            with st.container(border=True):
                if subject:
                    st.markdown(f"**Tiêu đề:** {subject}")
                    st.divider()
                
                if image_data:
                    try:
                        st.image(image_data, use_container_width=True)
                    except Exception:
                        st.warning("Không thể hiển thị ảnh banner")
                
                if body:
                    st.markdown("**Nội dung:**")
                    st.write(body.replace('\n', '\n\n'))
                
                if button_text and button_url:
                    st.markdown("---")
                    st.link_button(button_text, button_url, use_container_width=True, type="primary")
                
                st.caption("_Email này được tạo tự động từ hệ thống Campaign Manager_")
        else:
            st.markdown("### ⚙️ Cấu hình chi tiết:")
            st.json(dynamic_data, expanded=True)
        
        st.divider()
        if st.button("Đóng", use_container_width=True):
            st.session_state.show_demo_modal = False
            st.rerun()
    
    show_demo_dialog()

def render_dashboard_view():
    st.header("📊 Bước 6: Quản trị Hiệu suất & Tối ưu (Dữ liệu thật)", divider="blue")
    st.write("Theo dõi hiệu suất của tất cả các chiến dịch đã lưu trong CSDL.")
        
    if 'editing_campaign_id' in st.session_state:
        render_result_modal()
    
    if 'demo_campaign_id_dashboard' in st.session_state:
        render_dashboard_demo_modal()
        
    campaigns = st.session_state.campaigns
    if not campaigns:
        st.info("Chưa có chiến dịch nào trong CSDL. Hãy tạo một chiến dịch mới!")
        return

    cols = st.columns([3, 2, 1, 1, 1, 1, 1, 1])
    headers = ["Tên Chiến Dịch", "Phân Khúc", "Ngân Sách", "Doanh Thu", "ROI", "Hành Động", "Trạng Thái", "Demo"]
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
        cols[4].markdown(f"<span style='color:{roi_color}; font-weight:bold;'>{roi}</span>", unsafe_allow_html=True)
        
        campaign_id = campaign['id']
        campaign_status = campaign.get('status', 'N/A')

        with cols[5]:
            if campaign_status == '📝 Đã lưu':
                st.button("Kích hoạt", key=f"act_{i}", on_click=activate_campaign, args=(campaign_id,), use_container_width=True)
            elif campaign_status == '🟢 Đang chạy':
                st.button("Nhập KQ", key=f"res_{i}", on_click=show_result_modal, args=(campaign_id,), use_container_width=True)
            elif campaign_status == '🟡 Đã kết thúc':
                st.button("Xem/Sửa", key=f"res_{i}", on_click=show_result_modal, args=(campaign_id,), use_container_width=True)
        
        cols[6].write(campaign_status)
        
        with cols[7]:
            if st.button("👁️", key=f"demo_{i}", help="Xem demo chiến dịch", use_container_width=True):
                st.session_state.demo_campaign_id_dashboard = campaign_id
                st.rerun()
        
        st.divider()

def render_dashboard_demo_modal():
    """Modal demo cho dashboard"""
    campaign_id = st.session_state.demo_campaign_id_dashboard
    campaign = next((c for c in st.session_state.campaigns if c['id'] == campaign_id), None)
    
    if not campaign:
        del st.session_state.demo_campaign_id_dashboard
        return
    
    @st.dialog("🎬 Demo Chiến Dịch", width="large")
    def show_dashboard_demo():
        st.header(f"📧 {campaign.get('name')}")
        st.subheader(f"Chủ đề: {campaign.get('objective')}")
        st.divider()
        
        dynamic_data = campaign.get('dynamicData', {})
        platform = campaign.get('platform')
        
        if platform == 'owned':
            subject = dynamic_data.get('tactic-email-subject', '')
            image_data = dynamic_data.get('tactic-email-image', '')
            body = dynamic_data.get('tactic-email-body', '')
            button_text = dynamic_data.get('tactic-email-button-text', '')
            button_url = dynamic_data.get('tactic-email-button-url', '')
            
            st.markdown("### 📬 Nội dung Email:")
            
            with st.container(border=True):
                if subject:
                    st.markdown(f"**Tiêu đề:** {subject}")
                    st.divider()
                
                if image_data:
                    try:
                        st.image(image_data, use_container_width=True)
                    except Exception:
                        st.warning("Không thể hiển thị ảnh banner")
                
                if body:
                    st.markdown("**Nội dung:**")
                    st.write(body.replace('\n', '\n\n'))
                
                if button_text and button_url:
                    st.markdown("---")
                    st.link_button(button_text, button_url, use_container_width=True, type="primary")
                
                st.caption("_Email này được gửi đến khách hàng từ hệ thống_")
        else:
            st.markdown("### ⚙️ Cấu hình chi tiết:")
            st.json(dynamic_data, expanded=True)
        
        st.divider()
        if st.button("Đóng", use_container_width=True):
            del st.session_state.demo_campaign_id_dashboard
            st.rerun()
    
    show_dashboard_demo()

def render_result_modal():
    """Modal nhập kết quả chiến dịch"""
    if 'editing_campaign_id' in st.session_state:
        campaign_id = st.session_state.editing_campaign_id
        campaign = next((c for c in st.session_state.campaigns if c['id'] == campaign_id), None)
        
        if campaign:
            @st.dialog("💰 Nhập Kết Quả Thực Tế", width="medium")
            def show_result_dialog():
                st.write(f"Nhập doanh thu thực tế thu về từ chiến dịch **{campaign['name']}** để hệ thống tính toán ROI.")
                
                revenue = st.number_input(
                    "Doanh thu Thực tế (VNĐ)", 
                    min_value=0, 
                    value=int(campaign['revenue']) if campaign['revenue'] > 0 else 0,
                    step=100000,
                    key=f"revenue_input_{campaign_id}"
                )
                
                cols = st.columns(2)
                if cols[0].button("Lưu Kết Quả", type="primary", use_container_width=True):
                    save_campaign_result(campaign_id, revenue)
                if cols[1].button("Hủy bỏ", use_container_width=True):
                    del st.session_state.editing_campaign_id
                    st.rerun()
            
            show_result_dialog()

def show():
    """Hàm này được gọi bởi app.py"""
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
    st.set_page_config(layout="wide", page_title="Test Module Chiến dịch")
    show()