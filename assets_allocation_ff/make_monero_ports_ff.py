import monero_utils_ff
from datetime import date
import os


### 0. Pre-settings

# where to put the results
result_path = '/home/shafqat/Downloads/Roboadvisor_Project_Documentation/'

# where the 'etf_daily_return.csv' saved
os.chdir(r'/home/shafqat/Downloads/Roboadvisor_Project_Documentation')

# freq & window settings
freq = 12 #monthly data
window_yr = 5 # 5yrs
window = freq * window_yr


### 1. make monero ports

retirement_port_asset_wgt_dict = monero_utils_ff.make_port_asset_wgt_dict(account='retirement', window = window)
retirement_backtest_wgt = monero_utils_ff.make_backtest_wgt_dict(account = 'retirement', window = window, data_dict = retirement_port_asset_wgt_dict)
retirememt_port_rt = monero_utils_ff.make_portfolio_rt_df(account = 'retirement', data_dict = retirement_backtest_wgt)
retirememt_port_analysis = monero_utils_ff.make_port_analysis_df(retirememt_port_rt)

taxable_port_asset_wgt_dict = monero_utils_ff.make_port_asset_wgt_dict(account='taxable', window = window)
taxable_backtest_wgt = monero_utils_ff.make_backtest_wgt_dict(account = 'taxable', window = window, data_dict = taxable_port_asset_wgt_dict)
taxable_port_rt = monero_utils_ff.make_portfolio_rt_df(account = 'taxable', data_dict = taxable_backtest_wgt)
taxable_port_analysis = monero_utils_ff.make_port_analysis_df(taxable_port_rt)


### 2. export to csv files

today = date.today().strftime('%Y-%m-%d')
result_folder = result_path + today +"_ff"
os.mkdir(result_folder)

file_name = result_folder + '/asset_weights_retirement.csv'
b = len(retirement_port_asset_wgt_dict.keys())
retirement_current_port = retirement_port_asset_wgt_dict[b-1]
retirement_current_port.to_csv(file_name)

file_name = result_folder + '/portfolio_returns_retirement.csv'
retirememt_port_rt.to_csv(file_name)

file_name = result_folder + '/portfolio_advanced_statistics_retirement.csv'
retirememt_port_analysis.to_csv(file_name)

file_name = result_folder + '/asset_weights_taxable.csv'
b = len(taxable_port_asset_wgt_dict.keys())
taxable_current_port = taxable_port_asset_wgt_dict[b-1]
taxable_current_port.to_csv(file_name)

file_name = result_folder + '/portfolio_returns_taxable.csv'
taxable_port_rt.to_csv(file_name)

file_name = result_folder + '/portfolio_advanced_statistics_taxable.csv'
taxable_port_analysis.to_csv(file_name)