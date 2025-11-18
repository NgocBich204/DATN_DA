"""
SNEAKER DATA GENERATOR - RFM SEGMENTATION
Sinh dữ liệu fake cho phân khúc khách hàng
Author: Based on business rules document
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
from collections import defaultdict

# Initialize
fake = Faker('vi_VN')
Faker.seed(42)
np.random.seed(42)

# ============================================================================
# CONFIGURATION & MASTER DATA
# ============================================================================

# Segment Configuration
SEGMENT_CONFIG = {
    'VIP Champions': {
        'ratio': 0.13,  # 13% khách hàng
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

# Province Distribution by Segment
PROVINCE_DIST = {
    'VIP Champions': {
        'Hà Nội': 0.40, 'TP. Hồ Chí Minh': 0.35, 'Đà Nẵng': 0.15,
        'Hải Phòng': 0.07, 'Cần Thơ': 0.03
    },
    'Loyal Customers': {
        'Hà Nội': 0.35, 'TP. Hồ Chí Minh': 0.30, 'Đà Nẵng': 0.12,
        'Hải Phòng': 0.10, 'Cần Thơ': 0.08, 'Khác': 0.05
    },
    'Potential Loyalists': {
        'Hà Nội': 0.30, 'TP. Hồ Chí Minh': 0.25, 'Đà Nẵng': 0.15,
        'Hải Phòng': 0.12, 'Cần Thơ': 0.10, 'Khác': 0.08
    },
    'At Risk': {
        'Hà Nội': 0.28, 'TP. Hồ Chí Minh': 0.24, 'Đà Nẵng': 0.13,
        'Hải Phòng': 0.12, 'Cần Thơ': 0.10, 'Khác': 0.13
    },
    'Hibernating': {
        'Hà Nội': 0.25, 'TP. Hồ Chí Minh': 0.22, 'Đà Nẵng': 0.12,
        'Hải Phòng': 0.10, 'Cần Thơ': 0.11, 'Khác': 0.20
    }
}

# District Mapping
DISTRICTS = {
    'Hà Nội': {
        'premium': ['Ba Đình', 'Hoàn Kiếm', 'Hai Bà Trưng', 'Đống Đa', 'Cầu Giấy', 'Thanh Xuân'],
        'standard': ['Long Biên', 'Tây Hồ', 'Nam Từ Liêm', 'Bắc Từ Liêm', 'Hà Đông']
    },
    'TP. Hồ Chí Minh': {
        'premium': ['Quận 1', 'Quận 2', 'Quận 3', 'Quận 7', 'Bình Thạnh', 'Phú Nhuận', 'Tân Bình'],
        'standard': ['Quận 4', 'Quận 5', 'Quận 6', 'Quận 8', 'Quận 10', 'Thủ Đức', 'Bình Tân']
    },
    'Đà Nẵng': {
        'premium': ['Hải Châu', 'Thanh Khê', 'Sơn Trà'],
        'standard': ['Ngũ Hành Sơn', 'Liên Chiểu', 'Cẩm Lệ']
    },
    'Hải Phòng': {
        'premium': ['Hồng Bàng', 'Lê Chân', 'Ngô Quyền'],
        'standard': ['Kiến An', 'Hải An', 'Đồ Sơn']
    },
    'Cần Thơ': {
        'premium': ['Ninh Kiều', 'Cái Răng'],
        'standard': ['Bình Thủy', 'Ô Môn', 'Thốt Nốt']
    },
    'Khác': {
        'premium': ['Trung tâm'],
        'standard': ['Ngoại thành']
    }
}

# Traffic Sources by Segment
TRAFFIC_DIST = {
    'VIP Champions': {'TikTok': 0.35, 'Instagram': 0.25, 'Facebook': 0.20, 'Google': 0.15, 'Shopee': 0.05},
    'Loyal Customers': {'Facebook': 0.30, 'TikTok': 0.25, 'Instagram': 0.20, 'Google': 0.15, 'Shopee': 0.10},
    'Potential Loyalists': {'TikTok': 0.30, 'Facebook': 0.25, 'Google': 0.20, 'Instagram': 0.15, 'Shopee': 0.10},
    'At Risk': {'Facebook': 0.35, 'Google': 0.25, 'Instagram': 0.15, 'TikTok': 0.15, 'Shopee': 0.10},
    'Hibernating': {'Facebook': 0.40, 'Google': 0.25, 'Shopee': 0.15, 'Instagram': 0.10, 'TikTok': 0.10}
}

# Payment Methods by Segment
PAYMENT_DIST = {
    'VIP Champions': {'Ví điện tử': 0.35, 'Chuyển khoản': 0.30, 'QR Banking': 0.25, 'Thẻ tín dụng': 0.08, 'COD': 0.02},
    'Loyal Customers': {'Ví điện tử': 0.30, 'Chuyển khoản': 0.25, 'QR Banking': 0.20, 'Thẻ tín dụng': 0.15, 'COD': 0.10},
    'Potential Loyalists': {'Chuyển khoản': 0.25, 'Ví điện tử': 0.25, 'QR Banking': 0.20, 'COD': 0.20, 'Thẻ tín dụng': 0.10},
    'At Risk': {'COD': 0.35, 'Chuyển khoản': 0.25, 'Ví điện tử': 0.20, 'QR Banking': 0.15, 'Thẻ tín dụng': 0.05},
    'Hibernating': {'COD': 0.45, 'Chuyển khoản': 0.25, 'Ví điện tử': 0.15, 'QR Banking': 0.10, 'Thẻ tín dụng': 0.05}
}

# Product Catalog
BRANDS = ['Nike', 'Adidas', 'Puma', 'New Balance', 'Converse']

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

# Price Ranges (VNĐ)
PRICE_RANGES = {
    'Nike': {'Performance': (2500000, 4500000), 'Lifestyle': (1800000, 3500000),
             'Street/Retro': (2000000, 5000000), 'Smart': (4000000, 7000000)},
    'Adidas': {'Performance': (2200000, 4000000), 'Lifestyle': (1500000, 3000000),
               'Street/Retro': (3000000, 8000000), 'Smart': (3500000, 6000000)},
    'Puma': {'Performance': (1800000, 3500000), 'Lifestyle': (1200000, 2500000),
             'Street/Retro': (1500000, 3000000), 'Smart': (3000000, 5000000)},
    'New Balance': {'Performance': (2000000, 3800000), 'Lifestyle': (1800000, 3200000),
                    'Street/Retro': (2500000, 4500000), 'Smart': (0, 0)},
    'Converse': {'Performance': (0, 0), 'Lifestyle': (1000000, 2000000),
                 'Street/Retro': (1500000, 2500000), 'Smart': (0, 0)}
}

# Colorways
COLORWAYS = {
    'basic': ['Black', 'White', 'Navy', 'Grey'],
    'trending': ['Sail', 'Cream', 'Vintage White', 'Beige'],
    'bold': ['Red', 'Blue', 'Green', 'Orange', 'Yellow'],
    'limited': ['Collaboration', 'Special Edition', 'Custom']
}

# Product Category Distribution by Segment
CATEGORY_DIST = {
    'VIP Champions': {'Street/Retro': 0.45, 'Performance': 0.30, 'Smart': 0.15, 'Lifestyle': 0.10},
    'Loyal Customers': {'Lifestyle': 0.40, 'Street/Retro': 0.30, 'Performance': 0.25, 'Smart': 0.05},
    'Potential Loyalists': {'Lifestyle': 0.45, 'Street/Retro': 0.30, 'Performance': 0.20, 'Smart': 0.05},
    'At Risk': {'Lifestyle': 0.50, 'Performance': 0.30, 'Street/Retro': 0.18, 'Smart': 0.02},
    'Hibernating': {'Lifestyle': 0.50, 'Performance': 0.30, 'Street/Retro': 0.18, 'Smart': 0.02}
}

# Brand Preference by Segment
BRAND_DIST = {
    'VIP Champions': {'Nike': 0.40, 'Adidas': 0.30, 'New Balance': 0.20, 'Puma': 0.05, 'Converse': 0.05},
    'Loyal Customers': {'Nike': 0.30, 'Adidas': 0.25, 'Puma': 0.20, 'New Balance': 0.15, 'Converse': 0.10},
    'Potential Loyalists': {'Nike': 0.25, 'Adidas': 0.22, 'Puma': 0.20, 'New Balance': 0.18, 'Converse': 0.15},
    'At Risk': {'Nike': 0.22, 'Adidas': 0.20, 'Puma': 0.20, 'New Balance': 0.19, 'Converse': 0.19},
    'Hibernating': {'Nike': 0.20, 'Adidas': 0.20, 'Puma': 0.20, 'New Balance': 0.20, 'Converse': 0.20}
}

# Seasonal Multipliers
SEASONAL_EVENTS = {
    1: {'name': 'Tết', 'multiplier': 1.30},
    2: {'name': 'Tết', 'multiplier': 1.30},
    8: {'name': 'Back to School', 'multiplier': 1.20},
    9: {'name': 'Back to School', 'multiplier': 1.20},
    11: {'name': 'Black Friday', 'multiplier': 1.40}
}

# Hourly Distribution Weights (E-commerce pattern)
HOURLY_WEIGHTS = {
    0: 0.002, 1: 0.001, 2: 0.001, 3: 0.001,  # Late night (very low)
    4: 0.001, 5: 0.002, 6: 0.005, 7: 0.010,  # Early morning (low)
    8: 0.025, 9: 0.040, 10: 0.055, 11: 0.065,  # Morning (rising)
    12: 0.090, 13: 0.080,                      # Lunch peak
    14: 0.055, 15: 0.060, 16: 0.065, 17: 0.070,  # Afternoon
    18: 0.080, 19: 0.095, 20: 0.105, 21: 0.100,  # Evening peak (highest)
    22: 0.070, 23: 0.040                       # Late evening
}

# Day of Week Multipliers
DOW_MULTIPLIER = {
    0: 1.00,  # Monday
    1: 1.08,  # Tuesday
    2: 1.17,  # Wednesday
    3: 1.25,  # Thursday
    4: 1.33,  # Friday
    5: 1.50,  # Saturday (highest)
    6: 1.00   # Sunday
}

# Segment Time Preferences
SEGMENT_TIME_BOOST = {
    'VIP Champions': {
        'evening': [20, 21, 22, 23],  # Boost 20-23h
        'lunch': [12, 13],
        'boost_multiplier': 1.5
    },
    'Loyal Customers': {
        'evening': [19, 20, 21],
        'lunch': [12, 13],
        'boost_multiplier': 1.3
    },
    'Potential Loyalists': {
        'late_night': [21, 22, 23],
        'afternoon': [14, 15, 16],
        'boost_multiplier': 1.6
    },
    'At Risk': {
        'morning': [10, 11],
        'afternoon': [14, 15],
        'boost_multiplier': 1.4
    },
    'Hibernating': {
        'lunch': [12, 13],
        'boost_multiplier': 1.1  # More evenly distributed
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def weighted_choice(choices, weights):
    """Chọn ngẫu nhiên theo trọng số"""
    return random.choices(list(choices), weights=list(weights), k=1)[0]


def is_campaign_day(date):
    """
    Kiểm tra xem ngày có phải ngày campaign/sale không
    """
    month = date.month
    day = date.day
    weekday = date.weekday()

    # Black Friday (last Friday of November)
    if month == 11 and weekday == 4 and day >= 22:
        return True

    # Double 11
    if month == 11 and day == 11:
        return True

    # Tết period (Jan-Feb, first 15 days)
    if month in [1, 2] and day <= 15:
        return True

    # Payday rush (15th and end of month)
    if day in range(14, 17) or day >= 28:
        return True

    return False


def generate_realistic_hour_minute_second(date, segment):
    """
    Sinh giờ:phút:giây realistic dựa trên:
    - Ngày trong tuần
    - Segment khách hàng
    - Campaign day hay không

    Returns: (hour, minute, second)
    """
    # Get day of week multiplier
    dow = date.weekday()
    dow_mult = DOW_MULTIPLIER[dow]

    # Copy và adjust hourly weights
    adjusted_weights = {h: w * dow_mult for h, w in HOURLY_WEIGHTS.items()}

    # Segment-specific time boosts
    if segment in SEGMENT_TIME_BOOST:
        boost_config = SEGMENT_TIME_BOOST[segment]
        multiplier = boost_config['boost_multiplier']

        # Apply boosts to specific hours
        for key, hours in boost_config.items():
            if key != 'boost_multiplier':
                for h in hours:
                    adjusted_weights[h] = adjusted_weights.get(
                        h, 0.01) * multiplier

    # Campaign day boost
    if is_campaign_day(date):
        adjusted_weights[0] *= 3.0   # Midnight rush
        adjusted_weights[9] *= 1.5   # Morning launch
        adjusted_weights[12] *= 1.5  # Lunch check
        adjusted_weights[20] *= 1.8  # Evening peak

    # Normalize weights
    total_weight = sum(adjusted_weights.values())
    if total_weight > 0:
        normalized_weights = {h: w/total_weight for h,
                              w in adjusted_weights.items()}
    else:
        normalized_weights = HOURLY_WEIGHTS

    # Choose hour
    hour = random.choices(
        list(normalized_weights.keys()),
        weights=list(normalized_weights.values()),
        k=1
    )[0]

    # Choose minute with realistic patterns
    minute_pattern = random.choices(
        ['start_of_hour', 'early', 'mid', 'late', 'end_of_hour'],
        weights=[0.10, 0.25, 0.30, 0.30, 0.05],
        k=1
    )[0]

    if minute_pattern == 'start_of_hour':
        minute = random.randint(0, 5)
    elif minute_pattern == 'early':
        minute = random.randint(5, 20)
    elif minute_pattern == 'mid':
        minute = random.randint(20, 40)
    elif minute_pattern == 'late':
        minute = random.randint(40, 55)
    else:  # end_of_hour
        minute = random.randint(55, 59)

    # Random seconds for realism
    second = random.randint(0, 59)

    return hour, minute, second


def generate_age_by_segment(segment):
    """Sinh năm sinh theo segment"""
    age_groups = SEGMENT_CONFIG[segment]['age_groups']
    group = weighted_choice(age_groups.keys(), age_groups.values())

    if group == 'gen_z':
        birth_year = random.randint(1997, 2007)
    elif group == 'millennials':
        birth_year = random.randint(1987, 1996)
    else:  # gen_x
        birth_year = random.randint(1977, 1986)

    birth_date = fake.date_between(
        start_date=datetime(birth_year, 1, 1),
        end_date=datetime(birth_year, 12, 31)
    )
    return birth_date


def generate_phone():
    """Sinh số điện thoại VN hợp lệ"""
    prefixes = ['086', '096', '097', '098', '088', '091',
                '094', '089', '090', '093', '092', '056', '058']
    prefix = random.choice(prefixes)
    number = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return int(prefix + number)


def generate_email(ho_ten):
    """Sinh email từ họ tên"""
    # Bỏ dấu và chuyển thành chữ thường
    from unidecode import unidecode
    name_parts = unidecode(ho_ten.lower()).split()

    # Tạo username
    if len(name_parts) >= 2:
        username = name_parts[-1] + ''.join([p[0] for p in name_parts[:-1]])
    else:
        username = name_parts[0]

    # Thêm số random
    username += str(random.randint(100, 9999))

    # Domain
    domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'fpt.vn', 'viettel.vn']
    domain_weights = [0.60, 0.15, 0.10, 0.10, 0.05]
    domain = weighted_choice(domains, domain_weights)

    return f"{username}@{domain}"


def get_district(province, segment):
    """Lấy quận/huyện theo tỉnh và segment"""
    if province not in DISTRICTS:
        return 'Quận 1'

    # VIP/Loyal ưu tiên premium districts
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
    """
    Sinh ngày + GIỜ:PHÚT:GIÂY mua hàng theo segment
    """
    config = SEGMENT_CONFIG[segment]
    recency_min, recency_max = config['recency_days']

    # Ngày gần nhất (relative to end_date)
    most_recent = end_date - \
        timedelta(days=random.randint(recency_min, recency_max))

    # Phân bổ các đơn hàng còn lại
    dates = [most_recent]

    if num_orders > 1:
        # Tạo khoảng cách giữa các đơn
        days_available = (most_recent - start_date).days
        gap = days_available // (num_orders - 1) if num_orders > 1 else 0

        for i in range(1, num_orders):
            # Thêm variation để realistic hơn
            days_back = gap * i + random.randint(-15, 15)
            date = most_recent - timedelta(days=days_back)

            # Đảm bảo trong range
            if date < start_date:
                date = start_date + timedelta(days=random.randint(0, 30))

            dates.append(date)

    # Sort theo thời gian
    dates.sort()

    # Apply seasonal boost
    adjusted_dates = []
    for date in dates:
        month = date.month
        if month in SEASONAL_EVENTS:
            # Có thể thêm một số đơn trong tháng này
            if random.random() < 0.3:  # 30% chance thêm đơn
                extra_date = date + timedelta(days=random.randint(1, 5))
                if extra_date <= end_date:
                    adjusted_dates.append(extra_date)
        adjusted_dates.append(date)

    # QUAN TRỌNG: Thêm giờ:phút:giây realistic cho mỗi date
    realistic_datetimes = []
    for date in sorted(adjusted_dates):
        hour, minute, second = generate_realistic_hour_minute_second(
            date, segment)

        # Combine date với time realistic
        full_datetime = datetime.combine(
            date.date(),
            datetime.min.time()
        ) + timedelta(hours=hour, minutes=minute, seconds=second)

        realistic_datetimes.append(full_datetime)

    return realistic_datetimes


def select_product(segment, customer_brand_preference=None):
    """Chọn sản phẩm theo segment và brand preference"""
    # Chọn category
    category_probs = CATEGORY_DIST[segment]
    category = weighted_choice(category_probs.keys(), category_probs.values())

    # Chọn brand
    if customer_brand_preference and random.random() < 0.6:  # 60% theo preference
        brand = customer_brand_preference
    else:
        brand_probs = BRAND_DIST[segment]
        brand = weighted_choice(brand_probs.keys(), brand_probs.values())

    # Chọn sản phẩm cụ thể
    products = PRODUCT_CATALOG[brand].get(category, [])
    if not products:
        # Fallback nếu brand không có category này
        category = 'Lifestyle'
        products = PRODUCT_CATALOG[brand].get(category, ['Basic Model'])

    product = random.choice(products)

    # Chọn colorway
    if segment == 'VIP Champions':
        colorway_pool = (COLORWAYS['basic'] * 2 + COLORWAYS['trending'] * 2 +
                         COLORWAYS['bold'] + COLORWAYS['limited'])
    else:
        colorway_pool = (COLORWAYS['basic'] * 3 + COLORWAYS['trending'] * 2 +
                         COLORWAYS['bold'])

    colorway = random.choice(colorway_pool)

    return {
        'brand': brand,
        'category': category,
        'product': product,
        'colorway': colorway
    }


def calculate_price(brand, category, segment):
    """Tính giá sản phẩm"""
    price_range = PRICE_RANGES[brand][category]

    if price_range == (0, 0):  # Không có sản phẩm loại này
        return 0

    base_price = random.randint(price_range[0], price_range[1])

    # VIP có xu hướng mua đắt hơn
    if segment == 'VIP Champions':
        base_price = int(base_price * random.uniform(1.0, 1.3))

    # Làm tròn
    base_price = round(base_price / 10000) * 10000

    return base_price


def calculate_discount(segment, date, base_price):
    """Tính tiền khuyến mãi"""
    month = date.month

    # Base discount theo segment
    if segment == 'VIP Champions':
        base_discount = random.uniform(0.05, 0.10)
    elif segment == 'Loyal Customers':
        base_discount = random.uniform(0.08, 0.15)
    elif segment == 'Potential Loyalists':
        base_discount = random.uniform(0.10, 0.20)
    elif segment == 'At Risk':
        base_discount = random.uniform(0.15, 0.25)
    else:  # Hibernating
        base_discount = random.uniform(0.20, 0.30)

    # Seasonal boost
    if month in SEASONAL_EVENTS:
        base_discount += random.uniform(0.05, 0.15)

    # Flash sale random
    if random.random() < 0.10:  # 10% đơn là flash sale
        base_discount = random.uniform(0.30, 0.50)

    # Cap at 50%
    base_discount = min(base_discount, 0.50)

    discount = int(base_price * base_discount)
    return discount


def calculate_shipping(province, segment):
    """Tính phí vận chuyển"""
    # Free ship probability
    if segment == 'VIP Champions' and random.random() < 0.80:
        return 0
    if segment == 'Loyal Customers' and random.random() < 0.50:
        return 0
    if random.random() < 0.20:  # 20% promotion
        return 0

    # Shipping fee
    if province in ['Hà Nội', 'TP. Hồ Chí Minh', 'Đà Nẵng']:
        base_fee = random.randint(20000, 30000)
    elif province in ['Hải Phòng', 'Cần Thơ']:
        base_fee = random.randint(30000, 40000)
    else:
        base_fee = random.randint(40000, 50000)

    # Express shipping
    if random.random() < 0.15:
        base_fee += random.randint(10000, 20000)

    return base_fee


def generate_sku(brand, product, colorway, gender):
    """Tạo SKU"""
    # Size theo giới tính
    if gender == 'Nam':
        size = random.choice(
            [39, 40, 41, 42, 42, 43, 43, 44, 45])  # Peak at 42-43
    else:
        size = random.choice([35, 36, 37, 37, 38, 38, 39, 40])  # Peak at 37-38

    # Format SKU
    brand_code = brand[:3].upper()
    product_code = product[:3].upper()
    color_code = colorway[:3].upper()

    return f"{brand_code}_{product_code}_{color_code}_{size}"

# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================


def generate_customer_profile(segment, customer_id):
    """Tạo profile khách hàng"""
    config = SEGMENT_CONFIG[segment]

    # Giới tính
    gender_probs = config['gender']
    gender = weighted_choice(gender_probs.keys(), gender_probs.values())

    # Thông tin cá nhân
    if gender == 'Nam':
        ho_ten = fake.name_male()
    else:
        ho_ten = fake.name_female()

    # Tuổi
    ngay_sinh = generate_age_by_segment(segment)

    # Contact
    email = generate_email(ho_ten)
    sdt = generate_phone()

    # Địa chỉ
    province_probs = PROVINCE_DIST[segment]
    tinh_thanh = weighted_choice(
        province_probs.keys(), province_probs.values())
    quan_huyen = get_district(tinh_thanh, segment)

    # Preferences
    traffic_probs = TRAFFIC_DIST[segment]
    preferred_traffic = weighted_choice(
        traffic_probs.keys(), traffic_probs.values())

    payment_probs = PAYMENT_DIST[segment]
    preferred_payment = weighted_choice(
        payment_probs.keys(), payment_probs.values())

    # Brand loyalty (60% chance có brand yêu thích)
    brand_probs = BRAND_DIST[segment]
    favorite_brand = weighted_choice(
        brand_probs.keys(), brand_probs.values()) if random.random() < 0.6 else None

    return {
        'customer_id': customer_id,
        'segment': segment,
        'ho_ten': ho_ten,
        'gioi_tinh': gender,
        'ngay_sinh': ngay_sinh,
        'email': email,
        'sdt': sdt,
        'tinh_thanh': tinh_thanh,
        'quan_huyen': quan_huyen,
        'preferred_traffic': preferred_traffic,
        'preferred_payment': preferred_payment,
        'favorite_brand': favorite_brand
    }


def generate_data(total_customers=15000, start_date='2023-01-01', end_date='2024-12-31'):
    """
    MAIN FUNCTION: Sinh toàn bộ dữ liệu
    """
    print("🚀 Bắt đầu sinh dữ liệu...")

    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')

    all_records = []
    customer_id = 1

    # Duyệt qua từng segment
    for segment, config in SEGMENT_CONFIG.items():
        print(f"\n📊 Segment: {segment}")

        num_customers = int(total_customers * config['ratio'])
        print(f"   Số khách hàng: {num_customers}")

        for i in range(num_customers):
            # Generate customer profile
            customer = generate_customer_profile(segment, customer_id)

            # Số đơn hàng cho customer này
            min_orders, max_orders = config['orders_per_year']
            num_orders = random.randint(min_orders, max_orders)

            # Sinh ngày mua hàng
            order_dates = generate_order_dates(
                segment, num_orders, start_dt, end_dt)

            # Generate orders
            for order_idx, order_date in enumerate(order_dates):
                # Order ID
                order_id = f"DH{order_date.strftime('%Y%m%d')}_{customer_id:05d}_{order_idx:02d}"

                # Số sản phẩm trong đơn
                num_items = weighted_choice([1, 2, 3], [0.70, 0.25, 0.05])
                if segment == 'VIP Champions':
                    num_items = weighted_choice([1, 2, 3], [0.60, 0.30, 0.10])

                # Generate line items
                for item_idx in range(num_items):
                    # Chọn sản phẩm
                    product_info = select_product(
                        segment, customer['favorite_brand'])

                    # Số lượng (hầu hết là 1)
                    so_luong = 1 if random.random() < 0.95 else 2

                    # Giá
                    doanh_thu = calculate_price(
                        product_info['brand'],
                        product_info['category'],
                        segment
                    )

                    if doanh_thu == 0:
                        continue

                    # Khuyến mãi
                    tien_khuyen_mai = calculate_discount(
                        segment, order_date, doanh_thu)

                    # Vận chuyển (chỉ tính cho item đầu tiên)
                    van_chuyen = calculate_shipping(
                        customer['tinh_thanh'], segment) if item_idx == 0 else 0

                    # Doanh thu thuần
                    doanh_thu_thuan = (doanh_thu * so_luong) - \
                        tien_khuyen_mai + van_chuyen

                    # SKU
                    sku = generate_sku(
                        product_info['brand'],
                        product_info['product'],
                        product_info['colorway'],
                        customer['gioi_tinh']
                    )

                    # Traffic & Payment (có variation)
                    if random.random() < 0.7:  # 70% dùng preferred
                        traffic = customer['preferred_traffic']
                        payment = customer['preferred_payment']
                    else:
                        traffic_probs = TRAFFIC_DIST[segment]
                        traffic = weighted_choice(
                            traffic_probs.keys(), traffic_probs.values())
                        payment_probs = PAYMENT_DIST[segment]
                        payment = weighted_choice(
                            payment_probs.keys(), payment_probs.values())

                    # Tạo record
                    record = {
                        'HoTen': customer['ho_ten'],
                        'GioiTinh': customer['gioi_tinh'],
                        'NgaySinh': customer['ngay_sinh'],
                        'Email': customer['email'],
                        'SDT': customer['sdt'],
                        'TinhThanh': customer['tinh_thanh'],
                        'QuanHuyen': customer['quan_huyen'],
                        'DonHang': order_id,
                        'NgayMua': order_date,
                        'Traffic': traffic,
                        'PhuongThucTT': payment,
                        'TenSanPham': product_info['product'],
                        'TenNhomSanPham': product_info['category'],
                        'NhaSanXuat': product_info['brand'],
                        'PhienBan': product_info['colorway'],
                        'SKU': sku,
                        'SoLuong': so_luong,
                        'DoanhThu': doanh_thu,
                        'TienKhuyenMai': tien_khuyen_mai,
                        'VanChuyen': van_chuyen,
                        'DoanhThuThuan': doanh_thu_thuan
                    }

                    all_records.append(record)

            customer_id += 1

            # Progress
            if (i + 1) % 500 == 0:
                print(f"   ✓ Đã tạo {i + 1}/{num_customers} khách hàng")

    print(f"\n✅ Hoàn thành! Tổng số records: {len(all_records)}")

    # Convert to DataFrame
    df = pd.DataFrame(all_records)

    # Sort by date
    df = df.sort_values('NgayMua').reset_index(drop=True)

    return df

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================


def validate_data(df):
    """Kiểm tra chất lượng dữ liệu"""
    print("\n📈 VALIDATION REPORT\n" + "="*60)

    # Basic stats
    print(f"Tổng số records: {len(df):,}")
    print(f"Tổng số khách hàng: {df['Email'].nunique():,}")
    print(f"Tổng số đơn hàng: {df['DonHang'].nunique():,}")
    print(f"Khoảng thời gian: {df['NgayMua'].min()} đến {df['NgayMua'].max()}")

    # Customer analysis
    print("\n--- PHÂN TÍCH KHÁCH HÀNG ---")
    customer_stats = df.groupby('Email').agg({
        'DonHang': 'nunique',
        'DoanhThuThuan': 'sum',
        'NgayMua': lambda x: (x.max() - x.min()).days
    })
    customer_stats.columns = ['SoDonHang', 'TongDoanhThu', 'KhoangThoiGian']

    print(f"Đơn hàng TB/khách: {customer_stats['SoDonHang'].mean():.2f}")
    print(
        f"Doanh thu TB/khách: {customer_stats['TongDoanhThu'].mean():,.0f} VNĐ")

    print("\nPhân phối số đơn hàng:")
    print(customer_stats['SoDonHang'].value_counts().sort_index().head(10))

    # Product analysis
    print("\n--- PHÂN TÍCH SẢN PHẨM ---")
    print("Top 5 nhà sản xuất:")
    print(df['NhaSanXuat'].value_counts().head())

    print("\nTop 5 nhóm sản phẩm:")
    print(df['TenNhomSanPham'].value_counts())

    # Financial analysis
    print("\n--- PHÂN TÍCH TÀI CHÍNH ---")
    print(
        f"Doanh thu thuần TB/đơn: {df.groupby('DonHang')['DoanhThuThuan'].sum().mean():,.0f} VNĐ")
    print(f"Giá trị sản phẩm TB: {df['DoanhThu'].mean():,.0f} VNĐ")
    print(f"Khuyến mãi TB: {df['TienKhuyenMai'].mean():,.0f} VNĐ")
    print(f"Tỷ lệ miễn ship: {(df['VanChuyen'] == 0).mean() * 100:.1f}%")

    # TIME ANALYSIS (NEW!)
    print("\n--- 🕐 PHÂN TÍCH THỜI GIAN (QUAN TRỌNG CHO DASHBOARD) ---")

    # Extract hour from NgayMua
    df['Hour'] = df['NgayMua'].dt.hour
    df['DayOfWeek'] = df['NgayMua'].dt.dayofweek
    df['DayName'] = df['NgayMua'].dt.day_name()

    # Hourly distribution
    print("\n📊 Phân phối theo GIỜ:")
    hourly_dist = df['Hour'].value_counts().sort_index()
    for hour in range(0, 24, 4):  # Show every 4 hours
        count = hourly_dist.get(hour, 0)
        pct = (count / len(df)) * 100
        bar = '█' * int(pct * 2)  # Visual bar
        print(f"  {hour:02d}:00 - {hour+3:02d}:59  {count:5d} ({pct:5.2f}%) {bar}")

    # Peak hours check
    peak_hours_12_14 = df[df['Hour'].isin([12, 13])].shape[0]
    peak_hours_19_21 = df[df['Hour'].isin([19, 20, 21])].shape[0]
    low_hours_0_6 = df[df['Hour'] < 6].shape[0]

    print(
        f"\n✓ Peak lunch (12-14h): {peak_hours_12_14:,} đơn ({peak_hours_12_14/len(df)*100:.1f}%)")
    print(
        f"✓ Peak evening (19-21h): {peak_hours_19_21:,} đơn ({peak_hours_19_21/len(df)*100:.1f}%)")
    print(
        f"✓ Low hours (0-6h): {low_hours_0_6:,} đơn ({low_hours_0_6/len(df)*100:.1f}%)")

    # Day of week distribution
    print("\n📅 Phân phối theo NGÀY TRONG TUẦN:")
    dow_dist = df['DayName'].value_counts()
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        count = dow_dist.get(day, 0)
        pct = (count / len(df)) * 100
        bar = '█' * int(pct / 2)
        emoji = '🔥' if day in ['Friday', 'Saturday'] else ''
        print(f"  {day:10s}  {count:5d} ({pct:5.2f}%) {bar} {emoji}")

    # Check for all-zero times (old problem)
    zero_time_count = df[(df['Hour'] == 0) & (df['NgayMua'].dt.minute == 0) & (
        df['NgayMua'].dt.second == 0)].shape[0]
    print(
        f"\n⚠️ Số đơn có giờ = 00:00:00: {zero_time_count} ({zero_time_count/len(df)*100:.1f}%)")
    if zero_time_count / len(df) > 0.05:  # More than 5%
        print("   ❌ WARNING: Quá nhiều đơn có giờ 00:00:00 - không realistic!")
    else:
        print("   ✅ OK: Phân bổ giờ hợp lý")

    # Segment indicators (rough estimate)
    print("\n--- ƯỚC LƯỢNG SEGMENT ---")
    recent_date = df['NgayMua'].max()
    df['DaysSinceLastPurchase'] = (
        recent_date - df.groupby('Email')['NgayMua'].transform('max')).dt.days

    segment_estimate = df.groupby('Email').agg({
        'DonHang': 'nunique',
        'DoanhThuThuan': 'sum',
        'DaysSinceLastPurchase': 'first'
    })
    segment_estimate.columns = ['Frequency', 'Monetary', 'Recency']

    # Simple rules
    def estimate_segment(row):
        if row['Recency'] <= 30 and row['Frequency'] >= 8 and row['Monetary'] >= 50000000:
            return 'VIP Champions'
        elif row['Recency'] <= 60 and row['Frequency'] >= 5 and row['Monetary'] >= 30000000:
            return 'Loyal Customers'
        elif row['Recency'] <= 45 and row['Frequency'] <= 4 and row['Monetary'] >= 15000000:
            return 'Potential Loyalists'
        elif row['Recency'] >= 60 and row['Frequency'] >= 5:
            return 'At Risk'
        else:
            return 'Hibernating'

    segment_estimate['EstimatedSegment'] = segment_estimate.apply(
        estimate_segment, axis=1)
    print(segment_estimate['EstimatedSegment'].value_counts(
        normalize=True).sort_index())

    print("\n" + "="*60)

# ============================================================================
# MAIN EXECUTION
# ============================================================================


if __name__ == "__main__":
    print("="*60)
    print("     SNEAKER DATA GENERATOR - RFM SEGMENTATION")
    print("="*60)

    # Generate data
    df = generate_data(
        total_customers=15000,
        start_date='2023-01-01',
        end_date='2024-12-31'
    )

    # Validate
    validate_data(df)

    # Export
    output_file = "sneaker_sales_data_generated_3.xlsx"
    df.to_excel(output_file, index=False, sheet_name='Sales Data')
    print(f"\n💾 Đã lưu file: {output_file}")

    # Export CSV backup
    csv_file = "sneaker_sales_data_generated_3.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"💾 Đã lưu file: {csv_file}")

    print("\n✨ HOÀN THÀNH!")
