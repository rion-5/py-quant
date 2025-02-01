import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

class StockAnalyzer:
    def __init__(self, ticker):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        self.history = self.stock.history(period="1y")  # 1년치 데이터
        self.info = self.stock.info

    def get_momentum_indicators(self):
        """ 모멘텀 투자 관련 지표 계산 """
        close_prices = self.history['Close']

        # RSI 계산
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # 52주 고점 대비 현재 주가 비율
        high_52w = close_prices.rolling(window=252).max()
        current_price = close_prices.iloc[-1]
        high_52w_ratio = current_price / high_52w.iloc[-1]

        # 이동평균선 (60일, 200일)
        ma_60 = close_prices.rolling(window=60).mean().iloc[-1]
        ma_200 = close_prices.rolling(window=200).mean().iloc[-1]

        # 최근 1개월, 3개월, 6개월, 1년 수익률
        returns = {
            "1M Change": (close_prices.iloc[-1] - close_prices.iloc[-21]) / close_prices.iloc[-21] * 100,
            "3M Change": (close_prices.iloc[-1] - close_prices.iloc[-63]) / close_prices.iloc[-63] * 100,
            "6M Change": (close_prices.iloc[-1] - close_prices.iloc[-126]) / close_prices.iloc[-126] * 100,
            "1Y Change": (close_prices.iloc[-1] - close_prices.iloc[0]) / close_prices.iloc[0] * 100
        }

        return {
            "RSI": rsi.iloc[-1] if not rsi.isna().iloc[-1] else "N/A",
            "52W High Ratio": high_52w_ratio,
            "60-Day MA": ma_60,
            "200-Day MA": ma_200,
            **returns
        }, rsi

    def get_value_indicators(self):
        """ 가치 투자 관련 지표 가져오기 """
        return {
            "PER": self.info.get("trailingPE", "N/A"),
            "PBR": self.info.get("priceToBook", "N/A"),
            "EPS": self.info.get("epsTrailingTwelveMonths", "N/A"),
            "ROE": self.info.get("returnOnEquity", "N/A"),
            "Revenue Growth": self.info.get("revenueGrowth", "N/A"),
            "Debt to Equity": self.info.get("debtToEquity", "N/A")
        }

    def plot_charts(self):
        """ 주가, RSI, 상승률 차트 그리기 """
        close_prices = self.history['Close']
        ma_60 = close_prices.rolling(window=60).mean()
        ma_200 = close_prices.rolling(window=200).mean()

        _, rsi = self.get_momentum_indicators()
        
        # 최근 상승률 계산
        returns = {
            "1M Change": (close_prices.iloc[-1] - close_prices.iloc[-21]) / close_prices.iloc[-21] * 100,
            "3M Change": (close_prices.iloc[-1] - close_prices.iloc[-63]) / close_prices.iloc[-63] * 100,
            "6M Change": (close_prices.iloc[-1] - close_prices.iloc[-126]) / close_prices.iloc[-126] * 100,
            "1Y Change": (close_prices.iloc[-1] - close_prices.iloc[0]) / close_prices.iloc[0] * 100
        }

        # 그래프 그리기
        fig, axs = plt.subplots(3, 1, figsize=(10, 12))

        # 📈 주가 차트
        axs[0].plot(close_prices, label="Close Price", color="black")
        axs[0].plot(ma_60, label="60-Day MA", linestyle="dashed", color="blue")
        axs[0].plot(ma_200, label="200-Day MA", linestyle="dashed", color="red")
        axs[0].set_title(f"{self.ticker} Stock Price with Moving Averages")
        axs[0].legend()

        # 📊 RSI 차트
        axs[1].plot(rsi, label="RSI", color="purple")
        axs[1].axhline(70, linestyle="dashed", color="red", alpha=0.5)
        axs[1].axhline(30, linestyle="dashed", color="green", alpha=0.5)
        axs[1].set_title(f"{self.ticker} RSI Indicator")
        axs[1].legend()

        # 📉 주가 상승률 바 차트
        axs[2].bar(returns.keys(), returns.values(), color=["gray", "blue", "green", "red"])
        axs[2].set_title(f"{self.ticker} Recent Returns (%)")

        plt.tight_layout()
        plt.show()

    def summarize(self):
        """ 모멘텀 및 가치 투자 지표 요약 출력 """
        print(f"\n===== {self.ticker} Stock Analysis =====")
        print("\n📈 Momentum Indicators:")
        for key, value in self.get_momentum_indicators()[0].items():
            print(f"  {key}: {value}")

        print("\n💰 Value Indicators:")
        for key, value in self.get_value_indicators().items():
            print(f"  {key}: {value}")

        # 차트 시각화 실행
        self.plot_charts()

# 사용 예제
ticker = "TSLA"
analyzer = StockAnalyzer(ticker)
analyzer.summarize()
