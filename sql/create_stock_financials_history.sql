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

-- 재무 정보 (stock_financials_history 테이블)

-- ticker
-- trailing_pe (과거 PER)
-- forward_pe (미래 PER)
-- book_value (주당 순자산)
-- price_to_book (PBR)
-- earnings_growth (이익 성장률)
-- revenue_growth (매출 성장률)
-- return_on_assets (ROA)
-- return_on_equity (ROE)
-- debt_to_equity (부채비율)