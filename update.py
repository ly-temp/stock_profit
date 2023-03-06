import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import os

index_html = Path("./index.html").resolve()
index_md = Path("./index.md").resolve()
record_dir = Path("./record").resolve()
list_dir = Path("./stock_list").resolve()
img_dir = Path("image")
summary_md_dir = Path("summary.md")
summary_html_dir = Path("summary.html")


def default_plt_save(name):
    img_name = name+'.png'
    plt.grid()
    plt.legend()
    plt.xticks(rotation=20, fontsize = 'medium')
    plt.savefig(img_name, bbox_inches='tight')
    plt.clf()
    return Path(img_name).resolve()

def plot_price(name, hist):
    plt.plot(hist['High'], marker="o", color="red", label="High")
    plt.plot(hist['Low'], marker="o", color="green", label="Low")
    plt.plot(hist['Average'], marker="o", color="brown", label="Average")
    #plt.ylabel('price')
    #plt.xlabel('date')
    return default_plt_save(name)

def plot_profit(name, hist):
    plt.plot(hist['Profit'], marker="s", color="black", label="Profit")
    return default_plt_save(name)

def update_stock(name, my_price, hold_n, period, interval, plot_datetime_format):
    ticket = yf.Ticker(name)
    hist = ticket.history(period=period, interval=interval)
    hist['Average'] = hist[['High','Low']].mean(axis=1)
    hist['Profit'] = (my_price - hist['Close'])*hold_n

    index_name = hist.index.name
    hist.reset_index(inplace=True)
    hist[index_name] = hist[index_name].dt.strftime(plot_datetime_format)
    hist.set_index(index_name, inplace=True)

    img_prefix = name+"_"+period+"-"+interval
    img_price_dir = plot_price(img_prefix, hist)
    img_profit_dir = plot_profit(img_prefix+'_profit', hist)
    return img_price_dir, img_profit_dir, hist

update_stock_7d = lambda name, my_price, hold_n: update_stock(name, my_price, hold_n, "7d", "1d", "%D")
update_stock_1m = lambda name, my_price, hold_n: update_stock(name, my_price, hold_n, "1d", "30m", "%H:%M")

dir_to_url = lambda abs_dir: '/'+'/'.join(abs_dir.parts[2:])
dir_to_md = lambda abs_dir: '/'+'/'.join(abs_dir.parts[3:])

def write_html(html_f, dir, display_text, type):
    url = dir_to_url(dir)
    match type:
        case 'a':
            html_f.write('<a href="{}">{}</a>'.format(url, display_text))
        case 'i':
            html_f.write('<img src="{}" alt="{}"/>\n'.format(url, display_text))

def write_md(md_f, dir, display_text):
    md = dir_to_md(dir)
    md_f.write('![{}]({})\n'.format(display_text, md))

def write_html_md(html_f, md_f, img_dir, display_text, type):
    write_html(html_f, img_dir, display_text, type)
    write_md(md_f, img_dir, display_text)

mkdir_p = lambda path: path.mkdir(parents=True, exist_ok=True)


#init
mkdir_p(record_dir)

with open(index_html, "w+") as f_index_html:
    with open(index_md, "w+") as f_index_md:

        f_index_html.write('<!DOCTYPE html>\n')
        for f_name in os.listdir(list_dir):
            f_dir = list_dir.joinpath(f_name)

            f_stem = f_dir.stem

            f_set_dir = record_dir.joinpath(f_stem)
            mkdir_p(f_set_dir)

            summary_html_abs_dir = f_set_dir.joinpath(summary_html_dir)
            summary_md_abs_dir = f_set_dir.joinpath(summary_md_dir)

            with open(summary_md_abs_dir, "w+") as summary_md_f:
                with open(summary_html_abs_dir, "w+") as summary_html_f:

                    img_dir = f_set_dir.joinpath(img_dir)
                    mkdir_p(img_dir)

                    df_stock_list = pd.read_csv(f_dir, header=None, names=['Name', 'My_price', 'Hold_n'], sep="\s+", index_col=0)

                    for name, row in df_stock_list.iterrows():
                        #my_price = df_stock_list[df_stock_list['Name'] == name]

                        os.chdir(f_set_dir.joinpath(img_dir))
                        stock_name = name.strip()

                        output_img_price_1m_dir, output_img_profit_1m_dir, hist_1m = update_stock_1m(stock_name, row['My_price'], row['Hold_n'])
                        output_img_price_7d_dir, output_img_profit_7d_dir, hist_7d = update_stock_7d(stock_name, row['My_price'], row['Hold_n'])

                        os.chdir(record_dir)

                        write_html_md(summary_html_f, summary_md_f, img_dir, stock_name, 'i')
                        #img_url = dir_to_url(output_img_price_7d_dir)
                        #img_md = dir_to_md(output_img_price_7d_dir)
                        #summary_html_f.write('<img src="{}" alt="{}"/>\n'.format(img_url, stock_name))
                        #summary_md_f.write('![{}]({})\n'.format(stock_name, img_md))

                write_html(f_index_html, summary_html_abs_dir, f_stem, 'a')
                write_md(f_index_md, summary_md_abs_dir, f_stem)
                #summary_html_url = dir_to_url(summary_html_abs_dir)
                #summary_html_md = dir_to_md(summary_md_abs_dir)
                #f_index_html.write('<a href="{}">{}</a>'.format(summary_html_url, f_stem))
                #f_index_md.write('![{}]({})'.format(f_stem, summary_html_md))

exit(1)


