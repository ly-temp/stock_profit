import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import os
from io import StringIO
import shutil

root_dir = Path("./").resolve()
index_md = Path("./index.md").resolve()
record_dir = Path("./record").resolve()
list_dir = Path("./stock_list").resolve()
img_dir = Path("./image")
summary_md_dir = Path("summary.md")

shutil.rmtree(record_dir)

def get_yahoo_longname(symbol):
    import urllib
    import json
    response = urllib.request.urlopen(f'https://query1.finance.yahoo.com/v1/finance/search?q={symbol}')
    content = response.read()
    data = json.loads(content.decode('utf8'))['quotes'][0]['longname']
    return data

def default_plt_save(name, title):
    img_name = name+'.png'
    plt.title(title)
    plt.grid()
    plt.legend()
    plt.xticks(rotation=20, fontsize = 'medium')
    plt.savefig(img_name, bbox_inches='tight')
    plt.clf()
    return img_name

def plot_price(name, hist, title):
    plt.plot(hist['High'], marker="o", color="red", label="High")
    plt.plot(hist['Low'], marker="o", color="green", label="Low")
    plt.plot(hist['Average'], marker="o", color="brown", label="Average")
    #plt.ylabel('price')
    #plt.xlabel('date')
    return default_plt_save(name, title)

def plot_profit(name, hist, title):
    plt.plot(hist['Profit'], marker="s", color="black", label="Profit")
    return default_plt_save(name, title)

get_img_prefix_from_setting = lambda filename, setting: filename+"_"+setting[0]+"-"+setting[1]
def update_stock(name, company_name, my_price, hold_n, setting):
    period, interval, plot_datetime_format = setting

    ticket = yf.Ticker(name)

    hist = ticket.history(period=period, interval=interval)
    hist['Average'] = hist[['High','Low']].mean(axis=1)
    hist['Profit'] = (hist['Close'] - my_price)*hold_n

    index_name = hist.index.name
    hist.reset_index(inplace=True)
    hist[index_name] = hist[index_name].dt.strftime(plot_datetime_format)
    hist.set_index(index_name, inplace=True)

    #img_prefix = name+"_"+period+"-"+interval
    img_prefix = get_img_prefix_from_setting(name, setting)
    img_price_dir = plot_price(img_prefix, hist, company_name)
    img_profit_dir = plot_profit(img_prefix+'_profit', hist, company_name)
    return {'img_price_dir': img_price_dir,
            'img_profit_dir': img_profit_dir, 
            'hist': hist
            }

def get_profit_emoji(profit):
    if float(profit) < 0:
        return ':heavy_minus_sign:'
    return ':heavy_plus_sign:'

stock_setting_list = [["1d", "30m", "%H:%M"], ["7d", "1d", "%D"]]

update_stock_with_setting = lambda name, company_name, my_price, hold_n, stock_setting: update_stock(name, company_name, my_price, hold_n, stock_setting)

#rel_dir_to_md = lambda rel_dir: '/'.join(Path(rel_dir).parts[3:])

#def write_html(html_f, dir, display_text, type):
#    url = dir_to_url(dir)
#    match type:
#        case 'a':
#            html_f.write('<a href="{}">{}</a>'.format(url, display_text))
#        case 'i':
#            html_f.write('<img src="{}" alt="{}"/>\n'.format(url, display_text))

def write_link(md_f, rel_dir, display_text):
    md_f.write(f"[{display_text}]({rel_dir})")

def write_img(md_f, rel_dir, display_text):
    md_f.write('!')
    write_link(md_f, rel_dir, display_text)


#def write_html_md(html_f, md_f, img_dir, display_text, type):
#    write_html(html_f, img_dir, display_text, type)
#    write_md(md_f, img_dir, display_text)

mkdir_p = lambda path: path.mkdir(parents=True, exist_ok=True)
round_standarize = lambda value: "%.2f" % round(value, 2)

#init
mkdir_p(record_dir)

with open(index_md, "w+") as f_index_md:
    for f_name in os.listdir(list_dir):
        os.chdir(record_dir)
        f_set_dir = Path(Path(f_name).stem)
        mkdir_p(f_set_dir)
        os.chdir(f_set_dir)

        with open(summary_md_dir, "w+") as summary_md_f:
            mkdir_p(img_dir)

            df_stock_list = pd.read_csv(list_dir.joinpath(f_name), header=None, names=['Name', 'My_price', 'Hold_n'], sep="\s+", index_col=0)

            last_profit_list = []
            hist_profit_list = [pd.DataFrame()]*len(stock_setting_list)     #from differnt stock setting
            summary_md_f_buffer = StringIO()
            for name, row in df_stock_list.iterrows():
                #my_price = df_stock_list[df_stock_list['Name'] == name]
                company_name = get_yahoo_longname(name)

                os.chdir(img_dir)
                stock_name = name.strip()

                stock_data_list = []
                for stock_setting in stock_setting_list:
                    stock_data_list.append(update_stock_with_setting(stock_name, company_name, row['My_price'], row['Hold_n'], stock_setting))
                #stock_30m = update_stock_30m(stock_name, row['My_price'], row['Hold_n'])
                #stock_7d = update_stock_7d(stock_name, row['My_price'], row['Hold_n'])

                os.chdir("../")

                def write_profit_table(stock_data):
                    round_hist = stock_data['hist']
                    round_hist['Profit'] = round_hist['Profit'].map('{:.2f}'.format)
                    profit_table = round_hist['Profit'].reset_index().to_html(index=False).replace('\n', '')
                    summary_md_f_buffer.write(f"|{profit_table}")

                def write_stock(stock_data):
                    write_img(summary_md_f_buffer, img_dir.joinpath(stock_data['img_price_dir']), "price: "+company_name)
                    summary_md_f_buffer.write('|')
                    write_img(summary_md_f_buffer, img_dir.joinpath(stock_data['img_profit_dir']), "profit: "+company_name)
                    write_profit_table(stock_data)

                def append_hist_profit(hist_list, add_list):
                    if hist_list.empty:
                        return add_list
                    return hist_list + add_list

                for i in range(len(stock_setting_list)):
                    hist_profit_list[i] = append_hist_profit(hist_profit_list[i], stock_data_list[i]['hist']['Profit'])

                #choose stock_setting_list[0] as most recent record
                last_record = stock_data_list[0]['hist'].iloc[-1]
                last_profit_per_n = last_record['Close'] - row['My_price']
                last_profit = (last_profit_per_n*row['Hold_n'])
                last_profit_list.append(last_profit)

                round_last_profit = round_standarize(last_profit)
                profit_percentage = round_standarize(last_profit_per_n/row['My_price']*100)

                summary_md_f_buffer.write(f"## {name} [${round_last_profit}] [{profit_percentage}%]:\n#### {company_name}\n")
                summary_md_f_buffer.write('|price|profit|data|\n|:---:|:---:|:---:|\n|')
                for stock_data in stock_data_list:
                    write_stock(stock_data)
                    summary_md_f_buffer.write('|\n|')
                summary_md_f_buffer.write('|\n---\n')

            os.chdir(img_dir)
            profit_img_dir_list = []
            for i in range(len(hist_profit_list)):
                img_prefix = get_img_prefix_from_setting("Net_Profit", stock_setting_list[i])
                profit_img_dir_list.append(plot_profit(img_prefix, hist_profit_list[i].to_frame(), img_prefix))
            os.chdir("../")

            net_last_profit = round_standarize(sum(last_profit_list))
            net_last_profit_emoji = get_profit_emoji(net_last_profit)   #check +/-, no need exact decimal place

            net_profit_buff = StringIO()
            net_profit_buff.write(f"## Net Profit [{net_last_profit_emoji}]:\n### ${net_last_profit}\n")
            for i, profit_img_dir in enumerate(profit_img_dir_list):
                column_name = stock_setting_list[i][1] + " / " + stock_setting_list[i][0]
                net_profit_buff.write(f"|{column_name}")
            net_profit_buff.write("|\n")
            for i in range(len(profit_img_dir_list)):
                net_profit_buff.write("|:---:")
            net_profit_buff.write("|\n")
            for i, profit_img_dir in enumerate(profit_img_dir_list):
                net_profit_buff.write("|")
                write_img(net_profit_buff, img_dir.joinpath(profit_img_dir), Path(profit_img_dir).stem)
            net_profit_buff.write("|\n---\n")

            net_profit_buff.seek(0)
            shutil.copyfileobj(net_profit_buff, summary_md_f, -1)
            net_profit_buff.close()

            summary_md_f_buffer.seek(0)
            shutil.copyfileobj(summary_md_f_buffer, summary_md_f, -1)
            summary_md_f_buffer.close()

            summary_md_rel_dir = Path(record_dir.stem).joinpath(f_set_dir, summary_md_dir)
            write_link(f_index_md, summary_md_rel_dir, f_set_dir)
            f_index_md.write(f": [{net_last_profit_emoji}] [${net_last_profit}]\n")

