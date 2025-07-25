# strategies/sortino_ratio.py

import numpy as np
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_sortino_ratio(daily_returns, risk_free_rate=0.01/252):
    """Sortino Ratio 계산"""
    try:
        if daily_returns.empty or len(daily_returns) < 2:
            logger.warning("Insufficient data for Sortino Ratio calculation")
            return None
        
        downside_returns = daily_returns[daily_returns < 0]
        if downside_returns.empty:
            logger.warning("No downside returns for Sortino Ratio calculation")
            return 0.0
        
        expected_return = daily_returns.mean()
        downside_deviation = np.sqrt(np.mean(downside_returns**2))
        if downside_deviation == 0:
            logger.warning("Downside deviation is zero")
            return 0.0
        
        sortino_ratio = (expected_return - risk_free_rate) / downside_deviation * np.sqrt(252)
        return sortino_ratio if not np.isnan(sortino_ratio) else None
    except Exception as e:
        logger.error(f"Error calculating Sortino Ratio: {e}")
        return None
