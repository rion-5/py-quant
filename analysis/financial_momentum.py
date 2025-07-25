# analysis/financial_momentum.py

import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from data.data_fetcher import get_momentum_indicators, get_value_indicators, fetch_stock_data_from_db,fetch_stock_data_from_yfinance
from strategies.sortino_ratio import calculate_sortino_ratio
import logging
from datetime import datetime, timedelta
import pytz
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from data.database import get_connection
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def normalize_series(series):
    """Min-Max 정규화"""
    if series.isna().all() or len(series) < 2:
        return series.fillna(0)
    min_val, max_val = series.min(), series.max()
    if max_val == min_val:
        return series.fillna(0)
    return (series - min_val) / (max_val - min_val)

def calculate_weighted_score(df):
    """가중치 점수 계산"""
    weights = {
        '6M Change': 0.3,
        'RSI': 0.2,
        'Revenue Growth': 0.2,
        'Debt to Equity': 0.1,
        'PBR': 0.1,
        'Sortino Ratio': 0.05,
        'Average Volume': 0.05
    }
    
    # 정규화
    normalized = pd.DataFrame()
    normalized['6M Change'] = normalize_series(df['6M Change'])
    normalized['RSI'] = df['RSI'] / 100  # RSI는 0~100이므로 간단히 나눔
    normalized['Revenue Growth'] = normalize_series(df['Revenue Growth'])
    normalized['Debt to Equity'] = normalize_series(1 / (df['Debt to Equity'] + 1e-10))  # 낮을수록 유리
    normalized['PBR'] = normalize_series(1 / (df['PBR'] + 1e-10))  # 낮을수록 유리
    normalized['Sortino Ratio'] = normalize_series(df['Sortino Ratio'])
    normalized['Average Volume'] = normalize_series(df['Average Volume'])
    
    # 가중치 점수 계산
    score = sum(normalized[col] * weight for col, weight in weights.items())
    return score

def fetch_stock_analysis(tickers, start_date, end_date, min_volume, min_price, max_price, min_sortino, min_diff_ratio):
    """지정된 티커의 모멘텀 및 가치 지표 계산"""
    results = []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), 
           retry=retry_if_exception_type(Exception))
    def fetch_with_retry(ticker):
        try:
            # 6개월 데이터 가져오기
            end_date_dt = pd.to_datetime(end_date)
            start_date_dt = end_date_dt - timedelta(days=183)
            
            # DB에서 데이터 조회
            data = fetch_stock_data_from_db(ticker, start_date_dt, end_date_dt)
            if data.empty:
                logger.warning(f"No DB data for {ticker}, falling back to yfinance")
                data = fetch_stock_data_from_yfinance(ticker, start_date_dt, end_date_dt)
                if data.empty:
                    return None
            
            # 필터 조건 적용
            if (data['Volume'].mean() < min_volume or
                data['Close'].iloc[-1] < min_price or
                data['Close'].iloc[-1] > max_price):
                return None

            # Price Increase Ratio 계산
            price_increase_ratio = (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]
            if price_increase_ratio < min_diff_ratio:
                return None

            # Sortino Ratio 계산
            daily_returns = data['Close'].pct_change().dropna()
            sortino_ratio = calculate_sortino_ratio(daily_returns)
            if sortino_ratio is None or sortino_ratio < min_sortino:
                return None
            
            # 모멘텀 지표
            momentum = get_momentum_indicators(ticker)
            if not momentum:
                return None
            
            # 가치 지표 (DB 우선 조회)
            value = fetch_value_indicators_from_db(ticker)
            if not value:
                logger.warning(f"No DB financials for {ticker}, falling back to yfinance")
                value = get_value_indicators(ticker)
                if not value:
                    return None
            
            # 평균 거래량
            avg_volume = data['Volume'].mean() if not data['Volume'].empty else None
            
            return {
                'Ticker': ticker,
                '6M Change': momentum.get('6M Change'),
                'RSI': momentum.get('RSI'),
                'Revenue Growth': value.get('Revenue Growth'),
                'Debt to Equity': value.get('Debt to Equity'),
                'PBR': value.get('PBR'),
                'Sortino Ratio': sortino_ratio,
                'Average Volume': avg_volume
            }
        except Exception as e:
            logger.error(f"Error processing {ticker}: {e}")
            raise

    with ThreadPoolExecutor(max_workers=3) as executor:
        for ticker in tickers:
            result = fetch_with_retry(ticker)
            if result:
                results.append(result)
            time.sleep(0.5)
    
    if not results:
        logger.warning("No valid results obtained")
        return pd.DataFrame()
    
    df = pd.DataFrame(results)
    df['Weighted Score'] = calculate_weighted_score(df)
    return df

def fetch_value_indicators_from_db(ticker):
    """DB에서 펀더멘털 지표 조회"""
    query = """
        SELECT revenue_growth, debt_to_equity, pbr
        FROM quant_result
        WHERE ticker = %s
        ORDER BY trade_date DESC
        LIMIT 1;
    """
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (ticker,))
                result = cur.fetchone()
                if result:
                    return {
                        'Revenue Growth': result['revenue_growth'],
                        'Debt to Equity': result['debt_to_equity'],
                        'PBR': result['pbr']
                    }
                return {}
    except Exception as e:
        logger.error(f"Error fetching DB financials for {ticker}: {e}")
        return {}