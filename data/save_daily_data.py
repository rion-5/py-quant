import data.fetch_data as fetch

def main():
  aapl = fetch.get_stock_data('AAPL','2025-01-01','2025-01-08')
  print(aapl)

  [(start_date, end_date)] = fetch.get_recent_trading_days()
  start_date = start_date.strftime("%Y-%m-%d")
  end_date = end_date.strftime("%Y-%m-%d")

  us_symbols = fetch.get_stock_symbols()
  
  
  dataframes = []

  for symbol in symbols:
    temp = pd.DataFrame(fetch.get_stock_data(symbol, start_date, end_date))
    print(temp)  # Optional: for debugging
    # Append the dataframe to the list
    dataframes.append(temp)

  # Concatenate all dataframes into one
  result_df = pd.concat(dataframes, ignore_index=True)

  # Print or inspect the final dataframe
  print(result_df)

if __name__ == '__main__':
  main()