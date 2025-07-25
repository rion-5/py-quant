# main.py

import argparse
import logging
from datetime import datetime, timedelta
import pytz
from data.data_fetcher import fetch_momentum_symbols_from_db, fetch_recent_trading_days_from_db
from analysis.financial_momentum import fetch_stock_analysis
from data.database import get_connection
from psycopg2.extras import execute_batch

# Logging 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_to_quant_result(data, trade_date):
    """quant_result 테이블에 지표 데이터 저장"""
    query = """
        INSERT INTO quant_result (trade_date, ticker, six_month_change, rsi, revenue_growth, 
                                 debt_to_equity, pbr, sortino_ratio, average_volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (trade_date, ticker) DO NOTHING;
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                records = [
                    (
                        trade_date,
                        row['Ticker'],
                        row['6M Change'],
                        row['RSI'],
                        row['Revenue Growth'],
                        row['Debt to Equity'],
                        row['PBR'],
                        row['Sortino Ratio'],
                        row['Average Volume']
                    ) for _, row in data.iterrows()
                ]
                execute_batch(cur, query, records)
                conn.commit()
                logger.info(f"Successfully saved {len(records)} records for {trade_date}")
    except Exception as e:
        logger.error(f"Error saving to quant_result: {e}")
        conn.rollback()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate and save momentum stock indicators to quant_result.")
    
    # 기본 파라미터
    result = fetch_recent_trading_days_from_db()
    default_start_date = result.get('start_date', (datetime.now(pytz.timezone('Asia/Seoul')) - timedelta(days=14)).strftime('%Y-%m-%d'))
    default_end_date = result.get('end_date', datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d'))
    default_min_volume = 10000000
    default_min_price = 50
    default_max_price = 1000
    default_min_sortino = -0.5
    default_min_diff_ratio = 0.2
    default_top_n = 20

    # 인자 파싱
    parser.add_argument("--start_date", type=str, default=default_start_date, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, default=default_end_date, help="End date (YYYY-MM-DD)")
    parser.add_argument("--min_volume", type=int, default=default_min_volume, help="Minimum trading volume")
    parser.add_argument("--min_price", type=float, default=default_min_price, help="Minimum stock price")
    parser.add_argument("--max_price", type=float, default=default_max_price, help="Maximum stock price")
    parser.add_argument("--min_sortino", type=float, default=default_min_sortino, help="Minimum Sortino ratio")
    parser.add_argument("--min_diff_ratio", type=float, default=default_min_diff_ratio, help="Minimum price increase ratio")
    parser.add_argument("--top_n", type=int, default=default_top_n, help="Number of top stocks")

    args = parser.parse_args()

    # 모멘텀 종목 추출
    logger.info(f"Fetching momentum symbols for {args.start_date} to {args.end_date}")
    tickers = fetch_momentum_symbols_from_db(
        args.start_date, args.end_date, args.min_volume, args.min_price, args.max_price, args.top_n
    )
    if not tickers:
        logger.warning("No tickers found matching criteria")
        exit(1)

    # 지표 계산
    logger.info(f"Calculating indicators for {len(tickers)} tickers")
    fm_result = fetch_stock_analysis(tickers)
    if fm_result.empty:
        logger.warning("No analysis results obtained")
        exit(1)

    # quant_result 테이블에 저장
    trade_date = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d')
    save_to_quant_result(fm_result, trade_date)
    logger.info(f"Analysis completed and saved for {trade_date}")
    print(fm_result)