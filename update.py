import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

ticket = yf.Ticker("MSFT")
hist = ticket.history(period="5d")
ticket.get_shares_full(start=datetime.today()-timedelta(days=5), end=None)
print(hist)
