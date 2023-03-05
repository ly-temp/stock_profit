import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import os

record_dir = Path("./record").resolve()
list_dir = Path("./stock_list").resolve()
img_dir = Path("image")
summary_dir = Path("summary.md")

def plot_graph(name, hist):
    img_name = name+'.png'

    plt.plot(hist['High'], marker="o", color="red", label="High")
    plt.plot(hist['Low'], marker="o", color="green", label="Low")
    plt.plot(hist['Average'], marker="o", color="brown", label="Average")
    plt.xticks(rotation=50, fontsize = 'small')
    #plt.ylabel('price')
    #plt.xlabel('date')
    plt.grid()
    plt.legend()
    plt.savefig(img_name, bbox_inches='tight')
    plt.clf()
    return img_name

def update_stock(name):
    ticket = yf.Ticker(name)
    hist = ticket.history(period="7d")
    hist['Average'] = hist[['High','Low']].mean(axis=1)
    img_name = plot_graph(name, hist)
    return Path(img_name).resolve()

mkdir_p = lambda path: path.mkdir(parents=True, exist_ok=True)
#init
mkdir_p(record_dir)

for f in os.listdir(list_dir):
    print(f)
    f_stem = Path(f).stem

    f_set_dir = record_dir.joinpath(f_stem)
    mkdir_p(f_set_dir)

    with open(f_set_dir.joinpath(summary_dir), "w+") as summary_f:

        img_dir = f_set_dir.joinpath(img_dir)
        mkdir_p(img_dir)

        with open(list_dir.joinpath(f)) as file:
            for line in file:
                os.chdir(f_set_dir.joinpath(img_dir))
                stock_name = line.strip()
                output_img_dir = update_stock(stock_name)
                os.chdir(record_dir)
                img_url = "https://raw.githubusercontent.com/"+os.environ['GITHUB_REPOSITORY']+'/'+'/'.join(output_img_dir.parts[3:])
                summary_f.write("![{}]({})\n".format(stock_name, img_url))
    

exit(1)


