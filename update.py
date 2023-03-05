import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

ticket = yf.Ticker("MSFT")
hist = ticket.history(period="5d")
ticket.get_shares_full(start=datetime.today()-timedelta(days=5), end=None)
print(hist)
plt.plot(hist, color="black")
plt.xticks(rotation=50, fontsize = 'small')
plt.savefig('out.png', bbox_inches='tight')
