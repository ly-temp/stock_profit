from dataclasses import dataclass
@dataclass
class YfHistSetting:
    period: str
    interval: str
    def join(self, sep):
        return self.interval+sep+self.period


import pandas as pd
from pathlib import Path    #mkdir -p
import matplotlib.pyplot as plt

get_profit_image = lambda profit: '📈' if profit>=0 else '📉'
class Updater:

    #self.results
    #hist_settings
    def update_results(self, list_f, hist_settings):
        import yfinance as yf

        self.hist_settings = hist_settings

        input_list = pd.read_csv(list_f, names=['code', 'price', 'amount'],
            index_col='code',
            header=None, sep='\t')

        #individual
        self.results = []
        for code, hold in input_list.iterrows():
            ticket = yf.Ticker(code)
            hist = ticket.history(period=hist_settings.period, interval=hist_settings.interval).ffill()
            price_delta = hist.Close - hold.price
            profit = price_delta * hold.amount
            try:
                self.results.append({
                    'info': {
                        'name': ticket.info['longName'],
                        'code': code,
                        'hist_settings': hist_settings
                    },
                    'hist': pd.DataFrame({
                        'high': hist.High,
                        'low': hist.Low,
                        'profit': profit
                    }),
                    'current': {
                        'price': hist.Close.iloc[-1],
                        'profit': profit.iloc[-1],
                        'delta_percent': (hist.Close.iloc[-1]-hold.price)/hold.price *100
                    },
                    'plot': None
                })
            except Exception as e:
                print(e)
                self.results.append({
                    'info': {
                        'name': ticket.info['longName'],
                        'code': code,
                        'hist_settings': hist_settings
                    },
                    'hist': pd.DataFrame({
                        'high': pd.Series([0],index=pd.DatetimeIndex([0])),
                        'low': pd.Series([0],index=pd.DatetimeIndex([0])),
                        'profit': pd.Series([0],index=pd.DatetimeIndex([0]))
                    }),
                    'current': {
                        'price': 0,
                        'profit': 0,
                        'delta_percent': 0
                    },
                    'plot': None
                })

    #matplotlib
    def plot_individual_graph(self, dir):
        Path(dir).mkdir(parents=True, exist_ok=True)
        for result in self.results:

            base_fname = f'{result["info"]["code"]}_{self.hist_settings.join("-")}'
            setting_title_strg = self.hist_settings.join(' / ')

            price_fname = f'{dir}/{base_fname}_price.png'
            result['hist'][['high', 'low']].plot(title=result['info']['name']+'\n'+setting_title_strg, grid=True, ax=plt.gca())
            plt.savefig(price_fname)
            plt.clf()

            profit_fname = f'{dir}/{base_fname}_profit.png'
            result['hist']['profit'].plot(title=result['info']['name']+'\n'+setting_title_strg, grid=True, ax=plt.gca())
            plt.savefig(profit_fname)
            plt.clf()

            result['plot'] = {'price': price_fname, 'profit': profit_fname}

    #self.overall.plot
    #self.overall.profit
    #matplotlib
    def plot_overall_graph(self, dir):
        try:
            overall_profit = sum([result['hist']['profit'] for result in self.results])

            setting_title_strg = self.hist_settings.join(' / ')
            fname = f'{dir}/overall_{self.hist_settings.join("-")}.png'

            overall_profit = overall_profit.ffill()
            overall_profit.plot(title='Overall Profit\n'+setting_title_strg, grid=True, ax=plt.gca())
            plt.savefig(fname)
            plt.clf()

            self.overall={
                'profit': overall_profit,
                'plot': fname
            }
        except Exception as e:
            print(e)
            self.overall={
                'profit': None,
                'plot': f'{dir}/overall_{self.hist_settings.join("-")}.png'
            }


def series_to_html(s, interval):
    try:
        interval = ''.join([i for i in interval if not i.isdigit()])
        match interval:
            case 'm'|'h':
                f_strg = '%H:%M'
            case 'd'|'wk'|'mo':
                f_strg = '%Y-%m-%d'
            case _:
                f_strg = '%Y-%m-%d %H:%M'

        s.index = s.index.strftime(f_strg)
        df = s.round(2).reset_index()
        data_html = df.to_html(index=False, justify='center')
        data_html = ' '.join(data_html.replace('\n', '').replace('\t', '').split())
        return data_html
    except Exception as e:
        print(e)
        return ''

class PeriodIntervalUpdater:

    #self.profit
    #self.namspace
    def get_all_results(self, list_f, hist_settings_list):
        from pathlib import Path

        updaters = []
        self.namespace = Path(list_f).stem
        for hist_settings in hist_settings_list:
            up = Updater()
            up.update_results(list_f, hist_settings)
            up.plot_individual_graph(f'record/{self.namespace}/image')
            up.plot_overall_graph(f'record/{self.namespace}/image')
            updaters.append(up)

        f = open(f'record/{self.namespace}/summary.md', 'w')

        #overall
        #self.current_profit = updaters[0].overall['profit'].iloc[-1]
        #to align with bank cal
        self.current_profit = sum([result['current']['profit'] for result in updaters[0].results])

        f.write(f'## Net Profit [{get_profit_image(self.current_profit)}]:\n')
        f.write(f'### ${self.current_profit:.2f}\n')
        f.write(f'|type|graph|data|\n|:---:|:---:|:---:|\n')
        for up in updaters:
            hist_settings = up.results[0]['info']['hist_settings']
            setting_strg = hist_settings.join(' / ')
            profit_plot_dir = Path(up.overall['plot']).relative_to(f'record/{self.namespace}')

            f.write(f'|{setting_strg}|![net_profit]({profit_plot_dir})|')

            f.write(series_to_html(up.overall['profit'], hist_settings.interval) +'|\n')
        f.write('---\n')

        #individual
        results_same_settings = [up.results for up in updaters]
        for result_same_stock in zip(*results_same_settings):
            written_header = False
            for result in list(result_same_stock):
                if not written_header:
                    code = result['info']['code']
                    name = result['info']['name']
                    profit = result['current']['profit']
                    delta_percent = result['current']['delta_percent']

                    f.write(f'## {code} [{get_profit_image(profit)}] [${profit:.2f}] [{delta_percent:.2f}%]:\n')
                    f.write(f'#### {name}\n')
                    f.write('|price|profit|data|\n|:---:|:---:|:---:|\n')

                    written_header = True

                price_plot_dir = Path(result['plot']['price']).relative_to(f'record/{self.namespace}')
                profit_plot_dir = Path(result['plot']['profit']).relative_to(f'record/{self.namespace}')

                f.write(f'|![price]({price_plot_dir})|![profit]({profit_plot_dir})|')
                f.write(series_to_html(result['hist']['profit'], result['info']['hist_settings'].interval) +'|\n')
            f.write('---\n')

        f.close()


import os
with open('index.md', 'w') as f:
    for l in os.listdir('./stock_list'):
        piu = PeriodIntervalUpdater()
        piu.get_all_results(f'./stock_list/{l}', [
            YfHistSetting(period='1d', interval='30m'),
            YfHistSetting(period='5d', interval='1d'),
            YfHistSetting(period='1mo', interval='1wk')
        ])
        f.write(f'[{piu.namespace}](record/{piu.namespace}/summary.md): [{get_profit_image(piu.current_profit)}] [${piu.current_profit:.2f}]  \n')

