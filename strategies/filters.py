import pandas as pd

# 거래량 필터
def filter_by_volume(data, min_volume):
    return data['Volume'].mean() >= min_volume

# 주가 범위 필터
def filter_by_price_range(data, min_price, max_price):
    return min_price <= data['Close'].min() <= max_price and min_price <= data['Close'].max() <= max_price

# 최고가와 최저가 차이 필터
def filter_by_price_diff(data, min_diff_ratio):
    price_diff_ratio = (data['Close'].max() - data['Close'].min()) / data['Close'].min()
    return price_diff_ratio >= min_diff_ratio

# 필터 적용 함수
def apply_filters(data, min_volume, min_price, max_price, min_diff_ratio):
    return (
        filter_by_volume(data, min_volume) and
        filter_by_price_range(data, min_price, max_price) and
        filter_by_price_diff(data, min_diff_ratio)
    )
