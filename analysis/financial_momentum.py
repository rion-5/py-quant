import yfinance as yf
import pandas as pd
import numpy as np
import data.data_fetcher as fetch

def fetch_stock_analysis(tickers):
    result = {}
    
    for ticker in tickers:
        #print(f"Processing {ticker}...")
        
        # 모멘텀 지표 가져오기
        momentum = fetch.get_momentum_indicators(ticker)
        
        # 가치 지표 가져오기
        value = fetch.get_value_indicators(ticker)
        
        # 결과 합치기
        result[ticker] = {**momentum, **value}
    
    # 결과를 DataFrame으로 변환
    df = pd.DataFrame(result).T
    
    return df
