# analysis/financial_momentum.py

import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from data.data_fetcher import get_momentum_indicators, get_value_indicators, fetch_stock_data_from_db,fetch_stock_data_from_yfinance
from strategies.sortino_ratio import calculate_sortino_ratio
import logging
from datetime import datetime, timedelta
import pytz

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_stock_analysis(tickers):
    """지정된 티커의 모멘텀 및 가치 지표 계산"""
    results = []

    def process_ticker(ticker):
        try:
            # 6개월 데이터 가져오기
            end_date = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d')
            start_date = (datetime.now(pytz.timezone('Asia/Seoul')) - timedelta(days=183)).strftime('%Y-%m-%d')
            
            # DB에서 데이터 조회, 없으면 yfinance 사용
            data = fetch_stock_data_from_db(ticker, start_date, end_date)
            if data.empty:
                logger.warning(f"No DB data for {ticker}, falling back to yfinance")
                data = fetch_stock_data_from_yfinance(ticker, start_date, end_date)
                if not data:
                    return None
            
            # 모멘텀 지표
            momentum = get_momentum_indicators(ticker)
            if not momentum:
                return None
            
            # 가치 지표
            value = get_value_indicators(ticker)
            if not value:
                return None
            
            # Sortino Ratio 계산
            daily_returns = data['Close'].pct_change().dropna()
            sortino_ratio = calculate_sortino_ratio(daily_returns)
            
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
            return None

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_ticker, tickers))
    
    # 유효한 결과만 필터링
    results = [r for r in results if r is not None]
    if not results:
        logger.warning("No valid results obtained")
        return pd.DataFrame()
    
    df = pd.DataFrame(results)
    return df