import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import os

record_dir = Path("./record").resolve()
list_dir = Path("./stock_list").resolve()

def plot_graph(name, hist):
    plt.plot(hist['High'], marker="o", color="red", label="High")
    plt.plot(hist['Low'], marker="o", color="green", label="Low")
    plt.plot(hist['Average'], marker="o", color="brown", label="Average")
    plt.xticks(rotation=50, fontsize = 'small')
    plt.ylabel('price')
    plt.xlabel('date')
    plt.legend()
    plt.grid()
    plt.savefig(name+'.png', bbox_inches='tight')

def update_stock(name):
    ticket = yf.Ticker(name)
    hist = ticket.history(period="7d")
    hist['Average'] = hist[['High','Low']].mean(axis=1)
    plot_graph(name, hist)

#init
record_dir.mkdir(parents=True, exist_ok=True)

for f in os.listdir(list_dir):
    print(f)
    f_stem = Path(f).stem
    f_set_dir = record_dir.joinpath(f_stem)
    f_set_dir.mkdir(parents=True, exist_ok=True)
    with open(list_dir.joinpath(f)) as file:
        for line in file:
            os.chdir(f_set_dir)
            stock_name = line.strip()
            update_stock(stock_name)
            os.chdir(record_dir)

exit(1)


