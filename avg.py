import pandas as pd
from io import StringIO
import os

TERM_BOLD_START = "\033[1m"
TERM_BOLD_END = "\033[0m"

data_all_coins = """
ordertxid,pair,type,price,cost,vol
O1,BTC/EUR,buy,10000,1000,0.1
O2,BTC/EUR,sell,15000,1500,0.1
O6,BTC/EUR,buy,14000,1400,0.1
OP,BTC/EUR,sell,16000,800,0.05
OA,BTC/EUR,sell,16000,400,0.025
OR,XRP/EUR,buy,0.49,147,300
"""

files_in_dir = os.listdir()
trades_file = next((file for file in files_in_dir if file.startswith("trades")), None)

if trades_file:
    with open(trades_file, 'r') as file:
        data_all_coins = file.read()
        print("READING FROM FILE >", TERM_BOLD_START, file.name, TERM_BOLD_END, "\033[0m<. Make sure that is the current file.\n")
else:
    print("No file provided.", TERM_BOLD_START, "SHOWING EXAMPLE DATA", TERM_BOLD_END)
    print("Put a file with 'trades' in its name like 'trades.csv' into this dir and run again.\n")

df_all_coins = pd.read_csv(StringIO(data_all_coins))

def calculate_avg_entry_price_and_value(df, pair):
    buys = df[(df['type'] == 'buy') & (df['pair'] == pair)]
    sells = df[(df['type'] == 'sell') & (df['pair'] == pair)]
    
    total_bought_volume = buys['vol'].sum()
    total_sold_volume = sells['vol'].sum()
    net_holding_volume = total_bought_volume - total_sold_volume
    
    last_price = df[df['pair'] == pair].iloc[-1]['price']
    
    total_buy_cost = buys['cost'].sum()
    if total_bought_volume == 0:
        return 0, 0
    adjusted_total_buy_cost = total_buy_cost - (total_sold_volume * (total_buy_cost / total_bought_volume))
    
    avg_entry_price = 0
    current_holdings_value = 0
    if net_holding_volume > 0:
        avg_entry_price = adjusted_total_buy_cost / net_holding_volume
        current_holdings_value = net_holding_volume * last_price
    
    return avg_entry_price, current_holdings_value

unique_pairs = df_all_coins['pair'].unique()
avg_entry_prices_and_values = {pair: calculate_avg_entry_price_and_value(df_all_coins, pair) for pair in unique_pairs}

def print_avg_entry_prices_and_values(avg_prices_and_values):
    sorted_avg_prices_and_values = sorted(avg_prices_and_values.items(), key=lambda x: x[1][1], reverse=True)
    for pair, (price, value) in sorted_avg_prices_and_values:
        if value < 0.1:
            print(f"{pair:<8} - Small amount")
            continue
        if price < 0.01:
            leading_zeros = len(str(price).split('.')[1].lstrip('0'))  # Count leading zeros after decimal
            decimal_places = 2 + leading_zeros if leading_zeros > 0 else 2
            price_format = f"{price:.{decimal_places}f} EXPERIMENTAL DUE TO SMALL VALUE!"
        else:
            price_format = f"{price:.2f}"
        print(f"{pair:<8} - Average Entry Price: {price_format}")

print_avg_entry_prices_and_values(avg_entry_prices_and_values)

