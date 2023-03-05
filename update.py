import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os

record_dir = "record"
list_dir = "stock_list"

#init
if not os.path.exists(record_dir):
    os.makedirs(record_dir)

for filename in os.listdir(list_dir):
    print(filename)

exit(1)

ticket = yf.Ticker("MSFT")
hist = ticket.history(period="7d")
hist['Average'] = hist[['High','Low']].mean(axis=1)
plt.plot(hist['High'], marker="o", color="red", label="High")
plt.plot(hist['Low'], marker="o", color="green", label="Low")
plt.plot(hist['Average'], marker="o", color="brown", label="Average")
plt.xticks(rotation=50, fontsize = 'small')
plt.ylabel('price')
plt.xlabel('date')
plt.legend()
plt.grid()
plt.savefig('price.png', bbox_inches='tight')
