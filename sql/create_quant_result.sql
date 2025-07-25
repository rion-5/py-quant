CREATE TABLE quant_result (
    id SERIAL PRIMARY KEY,
    trade_date DATE NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    six_month_change FLOAT,
    rsi FLOAT,
    revenue_growth FLOAT,
    debt_to_equity FLOAT,
    pbr FLOAT,
    sortino_ratio FLOAT,
    average_volume FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(trade_date, ticker)
);
CREATE INDEX idx_quant_result_date_ticker ON quant_result(trade_date, ticker);