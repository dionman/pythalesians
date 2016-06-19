import datetime

import numpy
import pandas
from pythalesians.util.loggermanager import LoggerManager

from pythalesians.backtest.popular.strategytemplate import StrategyTemplate # generatic backtesting class

from pythalesians.market.requests.backtestrequest import BacktestRequest    # for specifying parameters of backtest
from pythalesians.market.loaders.lighttimeseriesfactory import LightTimeSeriesFactory  # for downloading mkt data
from pythalesians.market.requests.timeseriesrequest import TimeSeriesRequest           # parameters for downloading mkt data

from pythalesians.timeseries.techind.techindicator import TechIndicator     # calculating technical indicators

from pythalesians.graphics.graphs.plotfactory import PlotFactory


class StrategyFXCTA_Example(StrategyTemplate):
    def __init__(self):
        super(StrategyTemplate, self).__init__()
        self.logger = LoggerManager().getLogger(__name__)

        ##### FILL IN WITH YOUR OWN PARAMETERS FOR display, dumping, TSF etc.
        self.tsfactory = LightTimeSeriesFactory()
        self.DUMP_CSV = 'output_data/'
        self.DUMP_PATH = 'output_data/' + datetime.date.today().strftime("%Y%m%d") + ' '
        self.FINAL_STRATEGY = 'Thalesians FX CTA'
        self.SCALE_FACTOR = 1  #  specify plot size multiplier (should be larger on 4K monitors!)

        return

    ###### Parameters and signal generations (need to be customised for every model)
    def fill_backtest_request(self):

        ##### FILL IN WITH YOUR OWN BACKTESTING PARAMETERS
        br = BacktestRequest()

        # get all asset data
        br.start_date = "04 Jan 1989"                # start date of backtest
        br.finish_date = datetime.datetime.utcnow()  # end date of backtest
        br.spot_tc_bp = 0.5                          # bid/ask spread in basis point
        br.ann_factor = 252                          # number of points in year (working)

        br.plot_start = "01 Apr 2015"                # when to start plotting
        br.calc_stats = True                         # add stats to legends of plots
        br.write_csv = False                         # write CSV output
        br.plot_interim = True                       # plot at various stages of process
        br.include_benchmark = True                  # plot trading returns versus benchmark

        # have vol target for each signal
        br.signal_vol_adjust = True                  # vol adjust weighting for asset vol
        br.signal_vol_target = 0.1                   # 10% vol target for each asset
        br.signal_vol_max_leverage = 5               # maximum leverage of 5
        br.signal_vol_periods = 20                   # calculate realised vol over 20 periods
        br.signal_vol_obs_in_year = 252              # number of periods in year
        br.signal_vol_rebalance_freq = 'BM'          # reweight at end of month
        br.signal_vol_resample_freq = None

        # have vol target for portfolio
        br.portfolio_vol_adjust = True               # vol adjust for portfolio
        br.portfolio_vol_target = 0.1                # portfolio vol target is 10%
        br.portfolio_vol_max_leverage = 5            # max leverage of 5
        br.portfolio_vol_periods = 20                # calculate realised vol over 20 periods
        br.portfolio_vol_obs_in_year = 252           # number of periods in year
        br.portfolio_vol_rebalance_freq = 'BM'       # reweight at end of month
        br.portfolio_vol_resample_freq = None

        # tech params
        br.tech_params.sma_period = 200              # use 200D SMA later

        return br

    def fill_assets(self):
        ##### FILL IN WITH YOUR ASSET DATA

        # for FX basket
        full_bkt = ['EURUSD', 'USDJPY', 'GBPUSD', 'AUDUSD', 'USDCAD',
                    'NZDUSD', 'USDCHF', 'USDNOK', 'USDSEK']

        basket_dict = {}

        for i in range(0, len(full_bkt)):
            basket_dict[full_bkt[i]] = [full_bkt[i]]

        basket_dict['Thalesians FX CTA'] = full_bkt

        br = self.fill_backtest_request()

        self.logger.info("Loading asset data...")

        vendor_tickers = ['FRED/DEXUSEU', 'FRED/DEXJPUS', 'FRED/DEXUSUK', 'FRED/DEXUSAL', 'FRED/DEXCAUS',
                          'FRED/DEXUSNZ', 'FRED/DEXSZUS', 'FRED/DEXNOUS', 'FRED/DEXSDUS']

        time_series_request = TimeSeriesRequest(
            start_date=br.start_date,  # start date
            finish_date=br.finish_date,  # finish date
            freq='daily',  # daily data
            data_source='quandl',  # use Quandl as data source
            tickers=full_bkt,  # ticker (Thalesians)
            fields=['close'],  # which fields to download
            vendor_tickers=vendor_tickers,  # ticker (Quandl)
            vendor_fields=['close'],  # which Bloomberg fields to download
            cache_algo='internet_load_return')  # how to return data

        asset_df = self.tsfactory.harvest_time_series(time_series_request)

        # signalling variables
        spot_df = asset_df
        spot_df2 = None

        return asset_df, spot_df, spot_df2, basket_dict

    def construct_signal(self, spot_df, spot_df2, tech_params, br):

        ##### FILL IN WITH YOUR OWN SIGNALS

        # use technical indicator to create signals
        # (we could obviously create whatever function we wanted for generating the signal dataframe)
        tech_ind = TechIndicator()
        tech_ind.create_tech_ind(spot_df, 'SMA', tech_params); signal_df = tech_ind.get_signal()

        return signal_df

    def construct_strategy_benchmark(self):

        ###### FILL IN WITH YOUR OWN BENCHMARK

        tsr_indices = TimeSeriesRequest(
            start_date = '01 Jan 1980',                     # start date
            finish_date = datetime.datetime.utcnow(),       # finish date
            freq = 'daily',                                 # daily data
            data_source = 'quandl',                         # use Quandl as data source
            tickers = ["EURUSD"],                           # tickers to download
            vendor_tickers=['FRED/DEXUSEU'],
            fields = ['close'],                             # which fields to download
            vendor_fields = ['close'],
            cache_algo = 'cache_algo_return')               # how to return data)

        df = self.tsfactory.harvest_time_series(tsr_indices)

        df.columns = [x.split(".")[0] for x in df.columns]

        return df


if __name__ == '__main__':

# just change "False" to "True" to run any of the below examples

    # create a FX CTA strategy then chart the returns, leverage over time
    if True:
        strategy = StrategyFXCTA_Example()

        strategy.construct_strategy()

    strategy.plot_strategy_pnl()  # plot the final strategy
    strategy.plot_strategy_group_benchmark_pnl()        # plot all the cumulative P&Ls of each component

    # pf = PlotFactory()
    # pf.plot_line_graph(pandas.DataFrame(numpy.random.rand(100,10)))
