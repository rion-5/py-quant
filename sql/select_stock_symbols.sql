-- 주식심볼 추출
select symbol,name, exchange, etf  from stock_symbols
where exchange  IN ('NASDAQ','NYSE')
and test_issue = false
and financial_status <> 'Deficient'  -- 부실기업 제외 ;