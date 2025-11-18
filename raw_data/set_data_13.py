"""
SCRIPT SINH 13,000 RECORDS - SNEAKER E-COMMERCE DATA
Realistic time distribution cho Power BI Dashboard

Author: AI Data Analyst
Purpose: ĐATN - Customer Segmentation & Marketing Analytics
Date: November 2024
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
from collections import defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================

# Target
TARGET_RECORDS = 13000
ESTIMATED_CUSTOMERS = 2300  # Will generate ~13K records

# Date range
START_DATE = '2023-01-01'
END_DATE = '2024-12-31'

# Initialize
fake = Faker('vi_VN')
Faker.seed(42)
np.random.seed(42)

print("="*80)
print("  SNEAKER E-COMMERCE DATA GENERATOR - 13,000 RECORDS")
print("="*80)
print(f"\nTarget: {TARGET_RECORDS:,} records")
print(f"Customers: ~{ESTIMATED_CUSTOMERS:,}")
print(f"Period: {START_DATE} to {END_DATE}\n")

# ============================================================================
# MASTER DATA & CONFIGURATION
# ============================================================================

# Segment Configuration
SEGMENT_CONFIG = {
    'VIP Champions': {
        'ratio': 0.13,
        'orders_per_year': (8, 15),
        'total_value_per_year': (50_000_000, 100_000_000),
        'recency_days': (0, 30),
        'age_groups': {'gen_z': 0.7, 'millennials': 0.3},
        'gender': {'Nam': 0.6, 'Nữ': 0.4}
    },
    'Loyal Customers': {
        'ratio': 0.23,
        'orders_per_year': (5, 8),
        'total_value_per_year': (30_000_000, 50_000_000),
        'recency_days': (0, 60),
        'age_groups': {'gen_z': 0.6, 'millennials': 0.4},
        'gender': {'Nam': 0.55, 'Nữ': 0.45}
    },
    'Potential Loyalists': {
        'ratio': 0.28,
        'orders_per_year': (2, 4),
        'total_value_per_year': (15_000_000, 30_000_000),
        'recency_days': (0, 45),
        'age_groups': {'gen_z': 0.5, 'millennials': 0.4, 'gen_x': 0.1},
        'gender': {'Nam': 0.5, 'Nữ': 0.5}
    },
    'At Risk': {
        'ratio': 0.17,
        'orders_per_year': (5, 8),
        'total_value_per_year': (30_000_000, 50_000_000),
        'recency_days': (60, 180),
        'age_groups': {'millennials': 0.5, 'gen_z': 0.3, 'gen_x': 0.2},
        'gender': {'Nam': 0.45, 'Nữ': 0.55}
    },
    'Hibernating': {
        'ratio': 0.19,
        'orders_per_year': (1, 2),
        'total_value_per_year': (5_000_000, 15_000_000),
        'recency_days': (180, 600),
        'age_groups': {'millennials': 0.4, 'gen_x': 0.4, 'gen_z': 0.2},
        'gender': {'Nam': 0.4, 'Nữ': 0.6}
    }
}

# Province Distribution
PROVINCE_DIST = {
    'VIP Champions': {'Hà Nội': 0.40, 'TP. Hồ Chí Minh': 0.35, 'Đà Nẵng': 0.15, 'Hải Phòng': 0.07, 'Cần Thơ': 0.03},
    'Loyal Customers': {'Hà Nội': 0.35, 'TP. Hồ Chí Minh': 0.30, 'Đà Nẵng': 0.12, 'Hải Phòng': 0.10, 'Cần Thơ': 0.08, 'Khác': 0.05},
    'Potential Loyalists': {'Hà Nội': 0.30, 'TP. Hồ Chí Minh': 0.25, 'Đà Nẵng': 0.15, 'Hải Phòng': 0.12, 'Cần Thơ': 0.10, 'Khác': 0.08},
    'At Risk': {'Hà Nội': 0.28, 'TP. Hồ Chí Minh': 0.24, 'Đà Nẵng': 0.13, 'Hải Phòng': 0.12, 'Cần Thơ': 0.10, 'Khác': 0.13},
    'Hibernating': {'Hà Nội': 0.25, 'TP. Hồ Chí Minh': 0.22, 'Đà Nẵng': 0.12, 'Hải Phòng': 0.10, 'Cần Thơ': 0.11, 'Khác': 0.20}
}

# Districts
DISTRICTS = {
    'Hà Nội': {'premium': ['Ba Đình', 'Hoàn Kiếm', 'Hai Bà Trưng', 'Đống Đa', 'Cầu Giấy', 'Thanh Xuân'],
               'standard': ['Long Biên', 'Tây Hồ', 'Nam Từ Liêm', 'Bắc Từ Liêm', 'Hà Đông']},
    'TP. Hồ Chí Minh': {'premium': ['Quận 1', 'Quận 2', 'Quận 3', 'Quận 7', 'Bình Thạnh', 'Phú Nhuận', 'Tân Bình'],
                        'standard': ['Quận 4', 'Quận 5', 'Quận 6', 'Quận 8', 'Quận 10', 'Thủ Đức', 'Bình Tân']},
    'Đà Nẵng': {'premium': ['Hải Châu', 'Thanh Khê', 'Sơn Trà'], 'standard': ['Ngũ Hành Sơn', 'Liên Chiểu', 'Cẩm Lệ']},
    'Hải Phòng': {'premium': ['Hồng Bàng', 'Lê Chân', 'Ngô Quyền'], 'standard': ['Kiến An', 'Hải An', 'Đồ Sơn']},
    'Cần Thơ': {'premium': ['Ninh Kiều', 'Cái Răng'], 'standard': ['Bình Thủy', 'Ô Môn', 'Thốt Nốt']},
    'Khác': {'premium': ['Trung tâm'], 'standard': ['Ngoại thành']}
}

# Traffic Sources
TRAFFIC_DIST = {
    'VIP Champions': {'TikTok': 0.35, 'Instagram': 0.25, 'Facebook': 0.20, 'Google': 0.15, 'Shopee': 0.05},
    'Loyal Customers': {'Facebook': 0.30, 'TikTok': 0.25, 'Instagram': 0.20, 'Google': 0.15, 'Shopee': 0.10},
    'Potential Loyalists': {'TikTok': 0.30, 'Facebook': 0.25, 'Google': 0.20, 'Instagram': 0.15, 'Shopee': 0.10},
    'At Risk': {'Facebook': 0.35, 'Google': 0.25, 'Instagram': 0.15, 'TikTok': 0.15, 'Shopee': 0.10},
    'Hibernating': {'Facebook': 0.40, 'Google': 0.25, 'Shopee': 0.15, 'Instagram': 0.10, 'TikTok': 0.10}
}

# Payment Methods
PAYMENT_DIST = {
    'VIP Champions': {'Ví điện tử': 0.35, 'Chuyển khoản': 0.30, 'QR Banking': 0.25, 'Thẻ tín dụng': 0.08, 'COD': 0.02},
    'Loyal Customers': {'Ví điện tử': 0.30, 'Chuyển khoản': 0.25, 'QR Banking': 0.20, 'Thẻ tín dụng': 0.15, 'COD': 0.10},
    'Potential Loyalists': {'Chuyển khoản': 0.25, 'Ví điện tử': 0.25, 'QR Banking': 0.20, 'COD': 0.20, 'Thẻ tín dụng': 0.10},
    'At Risk': {'COD': 0.35, 'Chuyển khoản': 0.25, 'Ví điện tử': 0.20, 'QR Banking': 0.15, 'Thẻ tín dụng': 0.05},
    'Hibernating': {'COD': 0.45, 'Chuyển khoản': 0.25, 'Ví điện tử': 0.15, 'QR Banking': 0.10, 'Thẻ tín dụng': 0.05}
}

# Product Catalog
PRODUCT_CATALOG = {
    'Nike': {
        'Performance': ['Pegasus', 'ZoomX', 'Vaporfly'],
        'Lifestyle': ['Air Force 1', 'Air Max', 'Cortez'],
        'Street/Retro': ['Dunk', 'Jordan 1', 'Blazer'],
        'Smart': ['Adapt BB']
    },
    'Adidas': {
        'Performance': ['Ultraboost', 'Solarboost'],
        'Lifestyle': ['Stan Smith', 'Superstar', 'Gazelle'],
        'Street/Retro': ['Yeezy', 'Forum', 'Campus'],
        'Smart': ['4D Fusio']
    },
    'Puma': {
        'Performance': ['Velocity', 'Deviate'],
        'Lifestyle': ['Suede', 'Cali', 'Mayze'],
        'Street/Retro': ['RS-X', 'Slipstream'],
        'Smart': ['Fi Self-Lacing']
    },
    'New Balance': {
        'Performance': ['FuelCell', 'Fresh Foam'],
        'Lifestyle': ['327', '530'],
        'Street/Retro': ['550', '574', '990'],
        'Smart': []
    },
    'Converse': {
        'Performance': [],
        'Lifestyle': ['Chuck Taylor', 'One Star'],
        'Street/Retro': ['Chuck 70', 'Run Star Hike', 'Weapon'],
        'Smart': []
    }
}

# Price Ranges
PRICE_RANGES = {
    'Nike': {'Performance': (2500000, 4500000), 'Lifestyle': (1800000, 3500000), 'Street/Retro': (2000000, 5000000), 'Smart': (4000000, 7000000)},
    'Adidas': {'Performance': (2200000, 4000000), 'Lifestyle': (1500000, 3000000), 'Street/Retro': (3000000, 8000000), 'Smart': (3500000, 6000000)},
    'Puma': {'Performance': (1800000, 3500000), 'Lifestyle': (1200000, 2500000), 'Street/Retro': (1500000, 3000000), 'Smart': (3000000, 5000000)},
    'New Balance': {'Performance': (2000000, 3800000), 'Lifestyle': (1800000, 3200000), 'Street/Retro': (2500000, 4500000), 'Smart': (0, 0)},
    'Converse': {'Performance': (0, 0), 'Lifestyle': (1000000, 2000000), 'Street/Retro': (1500000, 2500000), 'Smart': (0, 0)}
}

# Colorways
COLORWAYS = ['Black', 'White', 'Navy', 'Grey', 'Sail', 'Cream',
             'Vintage White', 'Beige', 'Red', 'Blue', 'Green', 'Orange']

# Category Distribution by Segment
CATEGORY_DIST = {
    'VIP Champions': {'Street/Retro': 0.45, 'Performance': 0.30, 'Smart': 0.15, 'Lifestyle': 0.10},
    'Loyal Customers': {'Lifestyle': 0.40, 'Street/Retro': 0.30, 'Performance': 0.25, 'Smart': 0.05},
    'Potential Loyalists': {'Lifestyle': 0.45, 'Street/Retro': 0.30, 'Performance': 0.20, 'Smart': 0.05},
    'At Risk': {'Lifestyle': 0.50, 'Performance': 0.30, 'Street/Retro': 0.18, 'Smart': 0.02},
    'Hibernating': {'Lifestyle': 0.50, 'Performance': 0.30, 'Street/Retro': 0.18, 'Smart': 0.02}
}

# Brand Distribution
BRAND_DIST = {
    'VIP Champions': {'Nike': 0.40, 'Adidas': 0.30, 'New Balance': 0.20, 'Puma': 0.05, 'Converse': 0.05},
    'Loyal Customers': {'Nike': 0.30, 'Adidas': 0.25, 'Puma': 0.20, 'New Balance': 0.15, 'Converse': 0.10},
    'Potential Loyalists': {'Nike': 0.25, 'Adidas': 0.22, 'Puma': 0.20, 'New Balance': 0.18, 'Converse': 0.15},
    'At Risk': {'Nike': 0.22, 'Adidas': 0.20, 'Puma': 0.20, 'New Balance': 0.19, 'Converse': 0.19},
    'Hibernating': {'Nike': 0.20, 'Adidas': 0.20, 'Puma': 0.20, 'New Balance': 0.20, 'Converse': 0.20}
}

# HOURLY WEIGHTS (E-commerce pattern)
HOURLY_WEIGHTS = {
    0: 0.002, 1: 0.001, 2: 0.001, 3: 0.001,
    4: 0.001, 5: 0.002, 6: 0.005, 7: 0.010,
    8: 0.025, 9: 0.040, 10: 0.055, 11: 0.065,
    12: 0.090, 13: 0.080, 14: 0.055, 15: 0.060,
    16: 0.065, 17: 0.070, 18: 0.080, 19: 0.095,
    20: 0.105, 21: 0.100, 22: 0.070, 23: 0.040
}

# Day of Week Multipliers
DOW_MULTIPLIER = {0: 1.00, 1: 1.08, 2: 1.17,
                  3: 1.25, 4: 1.33, 5: 1.50, 6: 1.00}

# Segment Time Preferences
SEGMENT_TIME_BOOST = {
    'VIP Champions': {'evening': [20, 21, 22, 23], 'lunch': [12, 13], 'boost_multiplier': 1.5},
    'Loyal Customers': {'evening': [19, 20, 21], 'lunch': [12, 13], 'boost_multiplier': 1.3},
    'Potential Loyalists': {'late_night': [21, 22, 23], 'afternoon': [14, 15, 16], 'boost_multiplier': 1.6},
    'At Risk': {'morning': [10, 11], 'afternoon': [14, 15], 'boost_multiplier': 1.4},
    'Hibernating': {'lunch': [12, 13], 'boost_multiplier': 1.1}
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def weighted_choice(choices, weights):
    """Chọn ngẫu nhiên theo trọng số"""
    return random.choices(list(choices), weights=list(weights), k=1)[0]


def is_campaign_day(date):
    """Kiểm tra ngày campaign"""
    month, day, weekday = date.month, date.day, date.weekday()
    if month == 11 and weekday == 4 and day >= 22:
        return True  # Black Friday
    if month == 11 and day == 11:
        return True  # Double 11
    if month in [1, 2] and day <= 15:
        return True  # Tết
    if day in range(14, 17) or day >= 28:
        return True  # Payday
    return False


def generate_realistic_hour_minute_second(date, segment):
    """Sinh giờ:phút:giây realistic"""
    dow = date.weekday()
    dow_mult = DOW_MULTIPLIER[dow]

    adjusted_weights = {h: w * dow_mult for h, w in HOURLY_WEIGHTS.items()}

    if segment in SEGMENT_TIME_BOOST:
        boost_config = SEGMENT_TIME_BOOST[segment]
        multiplier = boost_config['boost_multiplier']
        for key, hours in boost_config.items():
            if key != 'boost_multiplier':
                for h in hours:
                    adjusted_weights[h] = adjusted_weights.get(
                        h, 0.01) * multiplier

    if is_campaign_day(date):
        adjusted_weights[0] *= 3.0
        adjusted_weights[9] *= 1.5
        adjusted_weights[12] *= 1.5
        adjusted_weights[20] *= 1.8

    total_weight = sum(adjusted_weights.values())
    normalized_weights = {h: w/total_weight for h,
                          w in adjusted_weights.items()}

    hour = random.choices(list(normalized_weights.keys()),
                          weights=list(normalized_weights.values()), k=1)[0]

    minute_pattern = random.choices(['start_of_hour', 'early', 'mid', 'late', 'end_of_hour'],
                                    weights=[0.10, 0.25, 0.30, 0.30, 0.05], k=1)[0]

    if minute_pattern == 'start_of_hour':
        minute = random.randint(0, 5)
    elif minute_pattern == 'early':
        minute = random.randint(5, 20)
    elif minute_pattern == 'mid':
        minute = random.randint(20, 40)
    elif minute_pattern == 'late':
        minute = random.randint(40, 55)
    else:
        minute = random.randint(55, 59)

    second = random.randint(0, 59)
    return hour, minute, second


def generate_age_by_segment(segment):
    """Sinh năm sinh"""
    age_groups = SEGMENT_CONFIG[segment]['age_groups']
    group = weighted_choice(age_groups.keys(), age_groups.values())
    if group == 'gen_z':
        birth_year = random.randint(1997, 2007)
    elif group == 'millennials':
        birth_year = random.randint(1987, 1996)
    else:
        birth_year = random.randint(1977, 1986)
    return fake.date_between(start_date=datetime(birth_year, 1, 1), end_date=datetime(birth_year, 12, 31))


def generate_phone():
    """Sinh SĐT VN"""
    prefixes = ['086', '096', '097', '098', '088', '091',
                '094', '089', '090', '093', '092', '056', '058']
    return int(random.choice(prefixes) + ''.join([str(random.randint(0, 9)) for _ in range(7)]))


def generate_email(ho_ten):
    """Sinh email"""
    try:
        from unidecode import unidecode
        name_parts = unidecode(ho_ten.lower()).split()
        if len(name_parts) >= 2:
            username = name_parts[-1] + \
                ''.join([p[0] for p in name_parts[:-1]])
        else:
            username = name_parts[0]
        username += str(random.randint(100, 9999))
        domains = ['gmail.com', 'yahoo.com',
                   'outlook.com', 'fpt.vn', 'viettel.vn']
        return f"{username}@{weighted_choice(domains, [0.60, 0.15, 0.10, 0.10, 0.05])}"
    except:
        return fake.email()


def get_district(province, segment):
    """Lấy quận/huyện"""
    if province not in DISTRICTS:
        return 'Quận 1'
    if segment in ['VIP Champions', 'Loyal Customers']:
        pool = DISTRICTS[province]['premium'] + DISTRICTS[province]['standard']
        weights = [0.7] * len(DISTRICTS[province]['premium']) + \
            [0.3] * len(DISTRICTS[province]['standard'])
    else:
        pool = DISTRICTS[province]['premium'] + DISTRICTS[province]['standard']
        weights = [0.3] * len(DISTRICTS[province]['premium']) + \
            [0.7] * len(DISTRICTS[province]['standard'])
    return weighted_choice(pool, weights)


def generate_order_dates(segment, num_orders, start_date, end_date):
    """Sinh ngày + giờ mua hàng"""
    config = SEGMENT_CONFIG[segment]
    recency_min, recency_max = config['recency_days']
    most_recent = end_date - \
        timedelta(days=random.randint(recency_min, recency_max))
    dates = [most_recent]

    if num_orders > 1:
        days_available = (most_recent - start_date).days
        gap = days_available // (num_orders - 1) if num_orders > 1 else 0
        for i in range(1, num_orders):
            days_back = gap * i + random.randint(-15, 15)
            date = most_recent - timedelta(days=days_back)
            if date < start_date:
                date = start_date + timedelta(days=random.randint(0, 30))
            dates.append(date)

    dates.sort()
    adjusted_dates = []
    for date in dates:
        if date.month in [1, 2, 8, 9, 11] and random.random() < 0.3:
            extra_date = date + timedelta(days=random.randint(1, 5))
            if extra_date <= end_date:
                adjusted_dates.append(extra_date)
        adjusted_dates.append(date)

    realistic_datetimes = []
    for date in sorted(adjusted_dates):
        hour, minute, second = generate_realistic_hour_minute_second(
            date, segment)
        full_datetime = datetime.combine(date.date(), datetime.min.time(
        )) + timedelta(hours=hour, minutes=minute, seconds=second)
        realistic_datetimes.append(full_datetime)

    return realistic_datetimes


def select_product(segment, customer_brand_preference=None):
    """Chọn sản phẩm"""
    category_probs = CATEGORY_DIST[segment]
    category = weighted_choice(category_probs.keys(), category_probs.values())

    if customer_brand_preference and random.random() < 0.6:
        brand = customer_brand_preference
    else:
        brand_probs = BRAND_DIST[segment]
        brand = weighted_choice(brand_probs.keys(), brand_probs.values())

    products = PRODUCT_CATALOG[brand].get(category, [])
    if not products:
        category = 'Lifestyle'
        products = PRODUCT_CATALOG[brand].get(category, ['Basic Model'])

    product = random.choice(products)
    colorway = random.choice(COLORWAYS)

    return {'brand': brand, 'category': category, 'product': product, 'colorway': colorway}


def calculate_price(brand, category, segment):
    """Tính giá"""
    price_range = PRICE_RANGES[brand][category]
    if price_range == (0, 0):
        return 0
    base_price = random.randint(price_range[0], price_range[1])
    if segment == 'VIP Champions':
        base_price = int(base_price * random.uniform(1.0, 1.3))
    return round(base_price / 10000) * 10000


def calculate_discount(segment, date, base_price):
    """Tính khuyến mãi"""
    if segment == 'VIP Champions':
        base_discount = random.uniform(0.05, 0.10)
    elif segment == 'Loyal Customers':
        base_discount = random.uniform(0.08, 0.15)
    elif segment == 'Potential Loyalists':
        base_discount = random.uniform(0.10, 0.20)
    elif segment == 'At Risk':
        base_discount = random.uniform(0.15, 0.25)
    else:
        base_discount = random.uniform(0.20, 0.30)

    if date.month in [1, 2, 8, 9, 11]:
        base_discount += random.uniform(0.05, 0.15)
    if random.random() < 0.10:
        base_discount = random.uniform(0.30, 0.50)

    return int(base_price * min(base_discount, 0.50))


def calculate_shipping(province, segment):
    """Tính ship"""
    if segment == 'VIP Champions' and random.random() < 0.80:
        return 0
    if segment == 'Loyal Customers' and random.random() < 0.50:
        return 0
    if random.random() < 0.20:
        return 0

    if province in ['Hà Nội', 'TP. Hồ Chí Minh', 'Đà Nẵng']:
        base_fee = random.randint(20000, 30000)
    elif province in ['Hải Phòng', 'Cần Thơ']:
        base_fee = random.randint(30000, 40000)
    else:
        base_fee = random.randint(40000, 50000)

    if random.random() < 0.15:
        base_fee += random.randint(10000, 20000)
    return base_fee


def generate_sku(brand, product, colorway, gender):
    """Tạo SKU"""
    size = random.choice([39, 40, 41, 42, 42, 43, 43, 44, 45]) if gender == 'Nam' else random.choice(
        [35, 36, 37, 37, 38, 38, 39, 40])
    return f"{brand[:3].upper()}_{product[:3].upper()}_{colorway[:3].upper()}_{size}"


def generate_customer_profile(segment, customer_id):
    """Tạo profile khách hàng"""
    config = SEGMENT_CONFIG[segment]
    gender_probs = config['gender']
    gender = weighted_choice(gender_probs.keys(), gender_probs.values())
    ho_ten = fake.name_male() if gender == 'Nam' else fake.name_female()
    ngay_sinh = generate_age_by_segment(segment)
    email = generate_email(ho_ten)
    sdt = generate_phone()

    province_probs = PROVINCE_DIST[segment]
    tinh_thanh = weighted_choice(
        province_probs.keys(), province_probs.values())
    quan_huyen = get_district(tinh_thanh, segment)

    traffic_probs = TRAFFIC_DIST[segment]
    preferred_traffic = weighted_choice(
        traffic_probs.keys(), traffic_probs.values())

    payment_probs = PAYMENT_DIST[segment]
    preferred_payment = weighted_choice(
        payment_probs.keys(), payment_probs.values())

    brand_probs = BRAND_DIST[segment]
    favorite_brand = weighted_choice(
        brand_probs.keys(), brand_probs.values()) if random.random() < 0.6 else None

    return {
        'customer_id': customer_id, 'segment': segment, 'ho_ten': ho_ten, 'gioi_tinh': gender,
        'ngay_sinh': ngay_sinh, 'email': email, 'sdt': sdt, 'tinh_thanh': tinh_thanh,
        'quan_huyen': quan_huyen, 'preferred_traffic': preferred_traffic,
        'preferred_payment': preferred_payment, 'favorite_brand': favorite_brand
    }

# ============================================================================
# MAIN GENERATION
# ============================================================================


def generate_data(total_customers, start_date, end_date):
    """Main function sinh dữ liệu"""
    print(f"🚀 Bắt đầu sinh dữ liệu...\n")

    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')

    all_records = []
    customer_id = 1

    for segment, config in SEGMENT_CONFIG.items():
        print(f"📊 Segment: {segment}")
        num_customers = int(total_customers * config['ratio'])
        print(f"   Số khách hàng: {num_customers}")

        for i in range(num_customers):
            customer = generate_customer_profile(segment, customer_id)
            min_orders, max_orders = config['orders_per_year']
            num_orders = random.randint(min_orders, max_orders)
            order_dates = generate_order_dates(
                segment, num_orders, start_dt, end_dt)

            for order_idx, order_date in enumerate(order_dates):
                order_id = f"DH{order_date.strftime('%Y%m%d')}_{customer_id:05d}_{order_idx:02d}"
                num_items = weighted_choice([1, 2, 3], [0.70, 0.25, 0.05])
                if segment == 'VIP Champions':
                    num_items = weighted_choice([1, 2, 3], [0.60, 0.30, 0.10])

                for item_idx in range(num_items):
                    product_info = select_product(
                        segment, customer['favorite_brand'])
                    so_luong = 1 if random.random() < 0.95 else 2
                    doanh_thu = calculate_price(
                        product_info['brand'], product_info['category'], segment)
                    if doanh_thu == 0:
                        continue

                    tien_khuyen_mai = calculate_discount(
                        segment, order_date, doanh_thu)
                    van_chuyen = calculate_shipping(
                        customer['tinh_thanh'], segment) if item_idx == 0 else 0
                    doanh_thu_thuan = (doanh_thu * so_luong) - \
                        tien_khuyen_mai + van_chuyen
                    sku = generate_sku(
                        product_info['brand'], product_info['product'], product_info['colorway'], customer['gioi_tinh'])

                    if random.random() < 0.7:
                        traffic = customer['preferred_traffic']
                        payment = customer['preferred_payment']
                    else:
                        traffic_probs = TRAFFIC_DIST[segment]
                        traffic = weighted_choice(
                            traffic_probs.keys(), traffic_probs.values())
                        payment_probs = PAYMENT_DIST[segment]
                        payment = weighted_choice(
                            payment_probs.keys(), payment_probs.values())

                    record = {
                        'HoTen': customer['ho_ten'], 'GioiTinh': customer['gioi_tinh'],
                        'NgaySinh': customer['ngay_sinh'], 'Email': customer['email'],
                        'SDT': customer['sdt'], 'TinhThanh': customer['tinh_thanh'],
                        'QuanHuyen': customer['quan_huyen'], 'DonHang': order_id,
                        'NgayMua': order_date, 'Traffic': traffic, 'PhuongThucTT': payment,
                        'TenSanPham': product_info['product'], 'TenNhomSanPham': product_info['category'],
                        'NhaSanXuat': product_info['brand'], 'PhienBan': product_info['colorway'],
                        'SKU': sku, 'SoLuong': so_luong, 'DoanhThu': doanh_thu,
                        'TienKhuyenMai': tien_khuyen_mai, 'VanChuyen': van_chuyen,
                        'DoanhThuThuan': doanh_thu_thuan
                    }
                    all_records.append(record)

            customer_id += 1
            if (i + 1) % 500 == 0:
                print(f"   ✓ Đã tạo {i + 1}/{num_customers} khách hàng")
        print()

    print(f"✅ Hoàn thành! Tổng số records: {len(all_records):,}\n")
    df = pd.DataFrame(all_records)
    df = df.sort_values('NgayMua').reset_index(drop=True)
    return df

# ============================================================================
# EXECUTE
# ============================================================================


if __name__ == "__main__":
    # Generate
    df = generate_data(ESTIMATED_CUSTOMERS, START_DATE, END_DATE)

    # Trim to exact target if needed
    if len(df) > TARGET_RECORDS:
        print(
            f"⚠️ Generated {len(df):,} records, trimming to {TARGET_RECORDS:,}...")
        df = df.sample(n=TARGET_RECORDS, random_state=42).sort_values(
            'NgayMua').reset_index(drop=True)
        print(f"✓ Final count: {len(df):,} records\n")

    # Quick validation
    print("="*80)
    print("  QUICK VALIDATION")
    print("="*80)
    print(f"\nTotal records: {len(df):,}")
    print(f"Customers: {df['Email'].nunique():,}")
    print(f"Orders: {df['DonHang'].nunique():,}")
    print(f"Date range: {df['NgayMua'].min()} to {df['NgayMua'].max()}")

    # Time check
    df['Hour'] = df['NgayMua'].dt.hour
    zero_time = df[(df['NgayMua'].dt.hour == 0) & (
        df['NgayMua'].dt.minute == 0) & (df['NgayMua'].dt.second == 0)].shape[0]
    peak_hours = df[df['Hour'].isin([19, 20, 21])].shape[0]

    print(f"\n⏰ TIME DISTRIBUTION:")
    print(f"   00:00:00: {zero_time:,} ({zero_time/len(df)*100:.1f}%)")
    print(f"   Peak 19-21h: {peak_hours:,} ({peak_hours/len(df)*100:.1f}%)")

    if zero_time == 0:
        print(f"   ✅ PERFECT: 0% tại 00:00:00!")

    # Export
    print(f"\n💾 EXPORTING FILES...")
    print("="*80)

    output_excel = "sneaker_sales_data_13000_records.xlsx"
    output_csv = "sneaker_sales_data_13000_records.csv"

    df.to_excel(output_excel, index=False, sheet_name='Sales Data')
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')

    print(f"\n✅ Excel: {output_excel} ({len(df):,} records)")
    print(f"✅ CSV: {output_csv}")

    print("\n" + "="*80)
    print("  🎉 HOÀN THÀNH! FILE READY CHO POWER BI!")
    print("="*80)
    print(f"\nNext steps:")
    print(f"1. Import {output_excel} vào Power BI")
    print(f"2. Check NgayMua column = Date/Time type")
    print(f"3. Create hourly analysis visuals")
    print(f"4. Enjoy realistic dashboard! 📊✨")
    print("="*80 + "\n")
