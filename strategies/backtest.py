import backtrader as bt
import pandas as pd
from data.data_fetcher import fetch_symbols_from_db, fetch_momentum_symbols_from_db, fetch_recent_trading_days_from_db, fetch_stock_data_from_db
from strategies.momentum import filter_and_rank_stocks

# 전략 정의
class MomentumStrategy(bt.Strategy):
    params = (
        ('lookback', 14),
        ('price_min', 100),
        ('price_max', 1000),
        ('volume_min', 8000000),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datavolume = self.datas[0].volume

    def next(self):
        if self.dataclose[0] > self.params.price_min and self.dataclose[0] < self.params.price_max:
            if self.datavolume[0] > self.params.volume_min:
                # 조건을 만족하는 종목에 대해 매수 신호 생성
                self.buy()

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'BUY EXECUTED, {order.data._name}, Date: {bt.num2date(order.executed.dt)}, Price: {order.executed.price}, Cost: {order.executed.value}, Comm: {order.executed.comm}')
            elif order.issell():
                print(f'SELL EXECUTED, {order.data._name}, Date: {bt.num2date(order.executed.dt)}, Price: {order.executed.price}, Cost: {order.executed.value}, Comm: {order.executed.comm}')

# 백테스트 실행
def run_backtest(tickers, start_date, end_date):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MomentumStrategy)

    # 필터링된 종목 데이터 로드
    for ticker in tickers:
        data = fetch_stock_data_from_db(ticker, start_date, end_date)
        
        # Trade_date 열을 datetime 형식으로 변환
        data['Trade_date'] = pd.to_datetime(data['Trade_date'])
        data.set_index('Trade_date', inplace=True)
        
        # NaN 값 제거
        data.dropna(inplace=True)
        
        data_bt = bt.feeds.PandasData(dataname=data, name=ticker)
        cerebro.adddata(data_bt)

    # 초기 자본 설정
    cerebro.broker.setcash(100000.0)

    # 매수/매도 화살표 표시를 위한 observer 추가
    cerebro.addobserver(bt.observers.BuySell)
    cerebro.addobserver(bt.observers.Value)

    # 백테스트 실행
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Ending Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # 결과 시각화
    cerebro.plot(style='candlestick')

if __name__ == "__main__":
    start_date = '2025-01-03'
    end_date = '2025-01-24'
    min_volume = 8000000
    min_price = 100
    max_price = 1000
    top_n = 20
    # 조건에 맞는 종목 리스트 (예시)
    tickers = fetch_momentum_symbols_from_db(
        start_date, end_date, min_volume, min_price, max_price, top_n
    )

    # Filter and rank stocks
    result = filter_and_rank_stocks(tickers, start_date, end_date, min_volume, min_price, max_price, 0.2, 0.2, top_n)
    print(result)
    # print(result['Ticker'])
    run_backtest(result['Ticker'], start_date, end_date)