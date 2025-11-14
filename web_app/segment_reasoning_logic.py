
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class SegmentReasoningEngine:
    """
    Engine tự động tạo lý do chọn phân khúc dựa trên:
    - Đặc điểm RFM của cluster
    - Phân tích so sánh với các cluster khác
    - Best practices trong CRM/Marketing
    """

    def __init__(self):
        # Ngưỡng phân loại (có thể điều chỉnh dựa trên dữ liệu)
        self.recency_thresholds = {
            'very_recent': 30,
            'recent': 90,
            'moderate': 180,
            'long_ago': 365
        }

        self.frequency_thresholds = {
            'very_high': 20,
            'high': 10,
            'moderate': 5,
            'low': 2
        }

        self.monetary_percentiles = {
            'very_high': 90,
            'high': 75,
            'moderate': 50,
            'low': 25
        }

    def analyze_rfm_profile(self, segment_data: pd.DataFrame,
                            all_data: pd.DataFrame) -> Dict:
        """
        Phân tích profile RFM của một segment

        Args:
            segment_data: DataFrame chứa dữ liệu của segment
            all_data: DataFrame chứa toàn bộ dữ liệu để so sánh

        Returns:
            Dict chứa các đặc điểm RFM
        """
        profile = {}

        # Recency Analysis
        avg_recency = segment_data['Recency'].mean()
        median_recency = segment_data['Recency'].median()
        recency_percentile = (
            all_data['Recency'] <= avg_recency).sum() / len(all_data) * 100

        if avg_recency <= self.recency_thresholds['very_recent']:
            profile['recency_level'] = 'rất gần đây'
            profile['recency_score'] = 5
        elif avg_recency <= self.recency_thresholds['recent']:
            profile['recency_level'] = 'gần đây'
            profile['recency_score'] = 4
        elif avg_recency <= self.recency_thresholds['moderate']:
            profile['recency_level'] = 'trung bình'
            profile['recency_score'] = 3
        elif avg_recency <= self.recency_thresholds['long_ago']:
            profile['recency_level'] = 'lâu'
            profile['recency_score'] = 2
        else:
            profile['recency_level'] = 'rất lâu'
            profile['recency_score'] = 1

        profile['avg_recency'] = avg_recency
        profile['recency_percentile'] = recency_percentile

        # Frequency Analysis
        avg_frequency = segment_data['Frequency'].mean()
        median_frequency = segment_data['Frequency'].median()
        frequency_percentile = (
            all_data['Frequency'] <= avg_frequency).sum() / len(all_data) * 100

        if avg_frequency >= self.frequency_thresholds['very_high']:
            profile['frequency_level'] = 'rất cao'
            profile['frequency_score'] = 5
        elif avg_frequency >= self.frequency_thresholds['high']:
            profile['frequency_level'] = 'cao'
            profile['frequency_score'] = 4
        elif avg_frequency >= self.frequency_thresholds['moderate']:
            profile['frequency_level'] = 'trung bình'
            profile['frequency_score'] = 3
        elif avg_frequency >= self.frequency_thresholds['low']:
            profile['frequency_level'] = 'thấp'
            profile['frequency_score'] = 2
        else:
            profile['frequency_level'] = 'rất thấp'
            profile['frequency_score'] = 1

        profile['avg_frequency'] = avg_frequency
        profile['frequency_percentile'] = frequency_percentile

        # Monetary Analysis
        avg_monetary = segment_data['Monetary'].mean()
        median_monetary = segment_data['Monetary'].median()
        monetary_percentile = (
            all_data['Monetary'] <= avg_monetary).sum() / len(all_data) * 100

        if monetary_percentile >= self.monetary_percentiles['very_high']:
            profile['monetary_level'] = 'rất cao'
            profile['monetary_score'] = 5
        elif monetary_percentile >= self.monetary_percentiles['high']:
            profile['monetary_level'] = 'cao'
            profile['monetary_score'] = 4
        elif monetary_percentile >= self.monetary_percentiles['moderate']:
            profile['monetary_level'] = 'trung bình'
            profile['monetary_score'] = 3
        elif monetary_percentile >= self.monetary_percentiles['low']:
            profile['monetary_level'] = 'thấp'
            profile['monetary_score'] = 2
        else:
            profile['monetary_level'] = 'rất thấp'
            profile['monetary_score'] = 1

        profile['avg_monetary'] = avg_monetary
        profile['monetary_percentile'] = monetary_percentile

        # Tính tổng điểm RFM
        profile['total_rfm_score'] = (
            profile['recency_score'] +
            profile['frequency_score'] +
            profile['monetary_score']
        )

        # Phân loại segment dựa trên điểm RFM
        if profile['total_rfm_score'] >= 13:
            profile['segment_tier'] = 'VIP/Champions'
        elif profile['total_rfm_score'] >= 10:
            profile['segment_tier'] = 'Loyal Customers'
        elif profile['total_rfm_score'] >= 7:
            profile['segment_tier'] = 'Potential Loyalists'
        elif profile['total_rfm_score'] >= 5:
            profile['segment_tier'] = 'At Risk'
        else:
            profile['segment_tier'] = 'Lost/Hibernating'

        return profile

    def calculate_segment_characteristics(self, segment_data: pd.DataFrame,
                                          all_data: pd.DataFrame) -> Dict:
        """
        Tính toán các đặc điểm bổ sung của segment
        """
        characteristics = {}

        # Tỷ lệ khách hàng trong segment
        characteristics['size_percentage'] = len(
            segment_data) / len(all_data) * 100

        # Đóng góp doanh thu
        characteristics['revenue_contribution'] = (
            segment_data['Monetary'].sum() / all_data['Monetary'].sum() * 100
        )

        # CLV ước tính (Customer Lifetime Value)
        characteristics['avg_clv'] = segment_data['Monetary'].mean(
        ) * segment_data['Frequency'].mean()

        # Tỷ lệ churn risk (dựa trên Recency)
        high_recency_count = (segment_data['Recency'] > 180).sum()
        characteristics['churn_risk_percentage'] = high_recency_count / \
            len(segment_data) * 100

        # Tính độ đồng nhất của segment (Coefficient of Variation)
        characteristics['recency_cv'] = segment_data['Recency'].std(
        ) / segment_data['Recency'].mean()
        characteristics['frequency_cv'] = segment_data['Frequency'].std(
        ) / segment_data['Frequency'].mean()
        characteristics['monetary_cv'] = segment_data['Monetary'].std(
        ) / segment_data['Monetary'].mean()

        # Độ đồng nhất trung bình (càng thấp càng đồng nhất)
        characteristics['cohesion_score'] = np.mean([
            characteristics['recency_cv'],
            characteristics['frequency_cv'],
            characteristics['monetary_cv']
        ])

        return characteristics

    def generate_segment_reasoning(self, segment_id: int,
                                   segment_data: pd.DataFrame,
                                   all_data: pd.DataFrame,
                                   cluster_centers: np.ndarray = None) -> str:
        """
        Tạo lý do chọn phân khúc dựa trên phân tích RFM và K-means

        Args:
            segment_id: ID của segment
            segment_data: Dữ liệu của segment
            all_data: Toàn bộ dữ liệu
            cluster_centers: Tâm của các cluster từ K-means (optional)

        Returns:
            String chứa lý do chi tiết
        """
        # Phân tích RFM profile
        rfm_profile = self.analyze_rfm_profile(segment_data, all_data)
        characteristics = self.calculate_segment_characteristics(
            segment_data, all_data)

        # Tính CLV trung bình của toàn bộ data để so sánh
        all_data_avg_clv = (
            all_data['Monetary'].mean() * all_data['Frequency'].mean())

        # Bắt đầu xây dựng lý do
        reasons = []

        # 1. Giới thiệu segment
        reasons.append(
            f"**Phân khúc {segment_id}** ({rfm_profile['segment_tier']}) chiếm {characteristics['size_percentage']:.1f}% tổng khách hàng")

        # 2. Phân tích RFM chi tiết
        rfm_analysis = self._build_rfm_analysis(rfm_profile)
        reasons.append(rfm_analysis)

        # 3. Giá trị kinh doanh
        business_value = self._build_business_value_analysis(
            rfm_profile, characteristics, all_data_avg_clv)
        reasons.append(business_value)

        # 4. Đặc điểm hành vi
        behavior_insight = self._build_behavior_insight(
            rfm_profile, characteristics)
        reasons.append(behavior_insight)

        # 5. Chiến lược đề xuất
        strategy = self._build_strategy_recommendation(
            rfm_profile, characteristics)
        reasons.append(strategy)

        # 6. Độ ưu tiên và ROI tiềm năng
        priority = self._build_priority_assessment(
            rfm_profile, characteristics)
        reasons.append(priority)

        return "\n\n".join(reasons)

    def _build_rfm_analysis(self, profile: Dict) -> str:
        """Xây dựng phân tích RFM"""
        analysis_parts = []

        # Recency
        if profile['recency_score'] >= 4:
            analysis_parts.append(
                f"Khách hàng có độ tương tác **{profile['recency_level']}** "
                f"(trung bình {profile['avg_recency']:.0f} ngày), "
                f"thuộc top {100-profile['recency_percentile']:.0f}% khách hàng active nhất"
            )
        else:
            analysis_parts.append(
                f"Khách hàng có xu hướng **ít tương tác** "
                f"(trung bình {profile['avg_recency']:.0f} ngày từ lần mua cuối), "
                f"cần chiến lược re-engagement"
            )

        # Frequency
        if profile['frequency_score'] >= 4:
            analysis_parts.append(
                f"Tần suất mua hàng **{profile['frequency_level']}** "
                f"(trung bình {profile['avg_frequency']:.1f} đơn hàng), "
                f"thể hiện sự trung thành cao"
            )
        elif profile['frequency_score'] >= 3:
            analysis_parts.append(
                f"Tần suất mua hàng **{profile['frequency_level']}** "
                f"({profile['avg_frequency']:.1f} đơn hàng), "
                f"có tiềm năng phát triển thành khách hàng thường xuyên"
            )
        else:
            analysis_parts.append(
                f"Tần suất mua hàng **{profile['frequency_level']}** "
                f"({profile['avg_frequency']:.1f} đơn hàng), "
                f"cần chiến lược khuyến khích mua lại"
            )

        # Monetary
        if profile['monetary_score'] >= 4:
            analysis_parts.append(
                f"Giá trị chi tiêu **{profile['monetary_level']}** "
                f"(${profile['avg_monetary']:,.0f} trung bình), "
                f"thuộc top {100-profile['monetary_percentile']:.0f}% khách hàng có giá trị nhất"
            )
        else:
            analysis_parts.append(
                f"Giá trị chi tiêu **{profile['monetary_level']}** "
                f"(${profile['avg_monetary']:,.0f}), "
                f"có tiềm năng tăng giá trị đơn hàng trung bình"
            )

        return "**📊 Phân tích RFM:**\n" + ". ".join(analysis_parts) + "."

    def _build_business_value_analysis(self, profile: Dict, characteristics: Dict, all_data_avg_clv: float) -> str:
        """Xây dựng phân tích giá trị kinh doanh"""
        parts = []

        # Revenue contribution
        if characteristics['revenue_contribution'] >= 30:
            parts.append(
                f"Đóng góp **{characteristics['revenue_contribution']:.1f}%** tổng doanh thu - là phân khúc **cốt lõi**")
        elif characteristics['revenue_contribution'] >= 15:
            parts.append(
                f"Đóng góp **{characteristics['revenue_contribution']:.1f}%** doanh thu - phân khúc **quan trọng**")
        else:
            parts.append(
                f"Đóng góp **{characteristics['revenue_contribution']:.1f}%** doanh thu với quy mô {characteristics['size_percentage']:.1f}% khách hàng")

        # CLV
        if characteristics['avg_clv'] > all_data_avg_clv * 1.5:
            parts.append(
                f"Customer Lifetime Value ước tính **cao** (${characteristics['avg_clv']:,.0f})")

        # Churn risk
        if characteristics['churn_risk_percentage'] > 40:
            parts.append(
                f"⚠️ Có {characteristics['churn_risk_percentage']:.0f}% khách hàng có **nguy cơ churn cao**")
        elif characteristics['churn_risk_percentage'] < 15:
            parts.append(
                f"✓ Tỷ lệ churn thấp ({characteristics['churn_risk_percentage']:.0f}%), phân khúc **ổn định**")

        return "**💰 Giá trị kinh doanh:**\n" + ". ".join(parts) + "."

    def _build_behavior_insight(self, profile: Dict, characteristics: Dict) -> str:
        """Xây dựng insight về hành vi"""
        insights = []

        # Cohesion (độ đồng nhất)
        if characteristics['cohesion_score'] < 0.5:
            insights.append(
                "Phân khúc có **độ đồng nhất cao** (hành vi tương đồng), dễ dàng targeting")
        elif characteristics['cohesion_score'] > 1.0:
            insights.append(
                "Phân khúc có **độ đa dạng cao**, cần personalization chi tiết hơn")
        else:
            insights.append(
                "Phân khúc có **độ đồng nhất vừa phải**, phù hợp với chiến lược segment-level")

        # Pattern recognition dựa trên RFM combination
        if profile['recency_score'] >= 4 and profile['frequency_score'] >= 4:
            insights.append(
                "Đây là nhóm **khách hàng trung thành cao**, nên focus vào retention và upselling")
        elif profile['recency_score'] <= 2 and profile['frequency_score'] >= 3:
            insights.append(
                "Nhóm **khách hàng đang rời bỏ** (previously loyal), cần win-back campaign khẩn cấp")
        elif profile['recency_score'] >= 4 and profile['frequency_score'] <= 2:
            insights.append(
                "Nhóm **khách hàng mới** hoặc occasional buyers, tiềm năng phát triển thành loyal")
        elif profile['monetary_score'] >= 4 and profile['frequency_score'] <= 2:
            insights.append(
                "Nhóm **big spenders** nhưng mua ít, cần chiến lược tăng frequency")

        return "**🎯 Insight hành vi:**\n" + ". ".join(insights) + "."

    def _build_strategy_recommendation(self, profile: Dict, characteristics: Dict) -> str:
        """Xây dựng chiến lược đề xuất"""
        strategies = []

        # Dựa trên segment tier
        tier = profile['segment_tier']

        if tier == 'VIP/Champions':
            strategies.append(
                "**Chiến lược:** VIP Program, exclusive offers, personalized service")
            strategies.append(
                "**Channels:** Direct contact, premium email, exclusive events")
            strategies.append(
                "**Goal:** Maximize LTV, encourage advocacy, prevent competitor poaching")

        elif tier == 'Loyal Customers':
            strategies.append(
                "**Chiến lược:** Loyalty rewards, cross-sell/upsell, referral programs")
            strategies.append(
                "**Channels:** Email marketing, app notifications, SMS")
            strategies.append(
                "**Goal:** Maintain engagement, increase purchase frequency và basket size")

        elif tier == 'Potential Loyalists':
            strategies.append(
                "**Chiến lược:** Nurturing campaigns, product education, time-limited incentives")
            strategies.append(
                "**Channels:** Email drip campaigns, retargeting ads, educational content")
            strategies.append(
                "**Goal:** Convert sang loyal customers, tăng repeat purchase rate")

        elif tier == 'At Risk':
            strategies.append(
                "**Chiến lược:** Re-engagement campaigns, win-back offers, satisfaction surveys")
            strategies.append(
                "**Channels:** Multi-channel (email + SMS + retargeting), urgent messaging")
            strategies.append(
                "**Goal:** Prevent churn, understand pain points, reactive")

        else:  # Lost/Hibernating
            strategies.append(
                "**Chiến lược:** Win-back campaigns với deep discounts, hoặc deprioritize")
            strategies.append(
                "**Channels:** Low-cost channels (email only), A/B test messages")
            strategies.append(
                "**Goal:** Cost-effective reactivation, hoặc clean database")

        return "**📋 Chiến lược Marketing:**\n" + "\n".join(strategies)

    def _build_priority_assessment(self, profile: Dict, characteristics: Dict) -> str:
        """Đánh giá độ ưu tiên"""
        # Tính điểm ưu tiên (0-100)
        priority_score = 0

        # RFM score (max 40 điểm)
        priority_score += (profile['total_rfm_score'] / 15) * 40

        # Revenue contribution (max 30 điểm)
        priority_score += min(
            characteristics['revenue_contribution'] / 50 * 30, 30)

        # Cohesion score (max 15 điểm) - càng đồng nhất càng dễ target
        priority_score += (1 - min(characteristics['cohesion_score'], 1)) * 15

        # Churn risk (max 15 điểm) - càng rủi ro cao cần ưu tiên càng cao (nếu là segment giá trị)
        if profile['total_rfm_score'] >= 10:  # Chỉ quan tâm churn risk với segment có giá trị
            priority_score += (
                characteristics['churn_risk_percentage'] / 100) * 15

        # Phân loại priority
        if priority_score >= 75:
            priority_level = "🔴 **RẤT CAO** (Critical)"
            roi_potential = "ROI tiềm năng: Rất cao (3-5x)"
        elif priority_score >= 60:
            priority_level = "🟠 **CAO** (High)"
            roi_potential = "ROI tiềm năng: Cao (2-3x)"
        elif priority_score >= 40:
            priority_level = "🟡 **TRUNG BÌNH** (Medium)"
            roi_potential = "ROI tiềm năng: Trung bình (1.5-2x)"
        else:
            priority_level = "🟢 **THẤP** (Low)"
            roi_potential = "ROI tiềm năng: Thấp (<1.5x) - Cân nhắc cost-effectiveness"

        return (
            f"**⚡ Độ ưu tiên: {priority_level}**\n"
            f"Priority Score: {priority_score:.1f}/100\n"
            f"{roi_potential}\n"
            f"**Khuyến nghị:** {'Đầu tư ngân sách marketing cao' if priority_score >= 60 else 'Áp dụng chiến lược cost-effective'}"
        )


# ===========================
# CÁCH SỬ DỤNG
# ===========================

def example_usage():
    """
    Ví dụ sử dụng SegmentReasoningEngine
    """
    # Giả sử bạn đã có data với RFM và cluster labels
    import pandas as pd

    # Sample data (thay bằng data thực của bạn)
    data = pd.DataFrame({
        'CustomerID': range(1000),
        'Recency': np.random.randint(1, 400, 1000),
        'Frequency': np.random.randint(1, 50, 1000),
        'Monetary': np.random.uniform(100, 10000, 1000),
        'Cluster': np.random.randint(0, 4, 1000)  # Từ K-means
    })

    # Khởi tạo engine
    reasoning_engine = SegmentReasoningEngine()

    # Tạo lý do cho từng segment
    for cluster_id in data['Cluster'].unique():
        segment_data = data[data['Cluster'] == cluster_id]

        print(f"\n{'='*80}")
        print(f"SEGMENT {cluster_id}")
        print('='*80)

        reasoning = reasoning_engine.generate_segment_reasoning(
            segment_id=cluster_id,
            segment_data=segment_data,
            all_data=data
        )

        print(reasoning)
        print()


# Fix cho global variable
def _build_business_value_analysis_fixed(self, profile: Dict, characteristics: Dict, all_data_avg_clv: float) -> str:
    """Xây dựng phân tích giá trị kinh doanh (fixed version)"""
    parts = []

    # Revenue contribution
    if characteristics['revenue_contribution'] >= 30:
        parts.append(
            f"Đóng góp **{characteristics['revenue_contribution']:.1f}%** tổng doanh thu - là phân khúc **cốt lõi**")
    elif characteristics['revenue_contribution'] >= 15:
        parts.append(
            f"Đóng góp **{characteristics['revenue_contribution']:.1f}%** doanh thu - phân khúc **quan trọng**")
    else:
        parts.append(
            f"Đóng góp **{characteristics['revenue_contribution']:.1f}%** doanh thu với quy mô {characteristics['size_percentage']:.1f}% khách hàng")

    # CLV
    if characteristics['avg_clv'] > all_data_avg_clv * 1.5:
        parts.append(
            f"Customer Lifetime Value ước tính **cao** (${characteristics['avg_clv']:,.0f})")

    # Churn risk
    if characteristics['churn_risk_percentage'] > 40:
        parts.append(
            f"⚠️ Có {characteristics['churn_risk_percentage']:.0f}% khách hàng có **nguy cơ churn cao**")
    elif characteristics['churn_risk_percentage'] < 15:
        parts.append(
            f"✓ Tỷ lệ churn thấp ({characteristics['churn_risk_percentage']:.0f}%), phân khúc **ổn định**")

    return "**💰 Giá trị kinh doanh:**\n" + ". ".join(parts) + "."


if __name__ == "__main__":
    example_usage()
