-- 1. 기본 주식 정보 (변동 없음)
CREATE TABLE stock_info (
    ticker VARCHAR PRIMARY KEY,
    company_name VARCHAR,
    industry VARCHAR,
    sector VARCHAR,
    market_cap BIGINT,
    currency VARCHAR
);

-- -- 2. 가격 및 거래 히스토리 (거래 날짜별로 저장)
-- CREATE TABLE stock_price_history (
--     ticker VARCHAR REFERENCES stocks(ticker),
--     trade_date DATE NOT NULL,
--     current_price NUMERIC,
--     previous_close NUMERIC,
--     day_high NUMERIC,
--     day_low NUMERIC,
--     volume BIGINT,
--     fifty_two_week_high NUMERIC,
--     fifty_two_week_low NUMERIC,
--     PRIMARY KEY (ticker, trade_date) -- 티커+날짜로 고유 값 설정
-- );


