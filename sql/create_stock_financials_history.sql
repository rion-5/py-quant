-- 3. 재무 정보 히스토리 (분기/연도별 저장)
CREATE TABLE stock_financials_history (
    ticker VARCHAR REFERENCES stocks(ticker),
    recorded_at DATE NOT NULL,  -- 재무 정보가 기록된 날짜
    trailing_pe NUMERIC,
    forward_pe NUMERIC,
    book_value NUMERIC,
    price_to_book NUMERIC,
    earnings_growth NUMERIC,
    revenue_growth NUMERIC,
    return_on_assets NUMERIC,
    return_on_equity NUMERIC,
    debt_to_equity NUMERIC,
    PRIMARY KEY (ticker, recorded_at) -- 티커+날짜 조합으로 고유값 설정
);