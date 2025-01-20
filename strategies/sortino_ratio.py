import numpy as np

# Sortino Ratio 계산 함수
def calculate_sortino_ratio(returns, risk_free_rate=0.0):
    negative_returns = returns[returns < 0]
    downside_deviation = np.sqrt(np.mean(negative_returns ** 2))
    excess_return = np.mean(returns) - risk_free_rate
    sortino_ratio = excess_return / downside_deviation if downside_deviation != 0 else 0
    return sortino_ratio
