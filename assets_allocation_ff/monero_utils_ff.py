import yfinance as yf

import pandas as pd
import numpy as np
import pandas_datareader.data as reader
import datetime as dt
from pandas.tseries.offsets import MonthEnd
import statsmodels.api as sm

import pypfopt
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt import plotting 
from pypfopt import objective_functions
from pypfopt import black_litterman
from pypfopt import HRPOpt

import scipy.cluster.hierarchy as sch
from scipy.cluster.hierarchy import dendrogram, linkage, cut_tree
from scipy import optimize
from scipy.stats import dirichlet
import cvxpy


### 1
def load_asset_data(account):
    file_name_etf = 'etf_daily_return.csv'
    df_tr = pd.read_csv(file_name_etf, index_col='Dates')
    df_tr.index = pd.to_datetime(df_tr.index)
    
    #just for style scheme
    etf_list = list(df_tr.columns)
    
    if account == 'taxable':
        exclude_etf= ['Emerging Market Bonds - USD']
        etf_list_style = list(filter(lambda x: x not in exclude_etf, etf_list))
    else:
        etf_list_style = etf_list.copy()

    #
    style_df = df_tr[etf_list_style].copy()
    start_dt = str(style_df.index[-1:][0]).split(' ')[0]

    if account == 'taxable':
        tk_list = [
            'IEMG', 
            'VEA', 
            'IVW',
            'IWO',
            'IVE',
            'MTUM',
            'VOO',
            'IWM',
            'IEF',
            'SHV', 
            'VTEB',
            'TIP',
            'HYG',
            'LQD',
            # 'EMB',
            'BNDX',
            'IAU'
        ]
    else: 
         tk_list = [
            'IEMG', 
            'VEA', 
            'IVW',
            'IWO',
            'IVE',
            'MTUM',
            'VOO',
            'IWM',
            'IEF',
            'SHV', 
            'VTEB',
            'TIP',
            'HYG',
            'LQD',
            'EMB',
            'BNDX',
            'IAU'
        ]
        
    
    # updates df with latest prices
    yf_df = yf.download(tk_list, start = start_dt)['Adj Close']
    yf_df = yf_df.pct_change()

    if account == "taxable":
        yf_df = yf_df.rename(columns={
            "IEMG": "Emerging Market Stocks",
            "VEA": "Foreign Developed Stocks",
            "IVW": "US Stocks - Growth (Large Cap)",
            "IWO": "US Stocks - Growth (Small Cap)",
            "IVE": "US Stocks - Value (Large Cap)", 
            "MTUM": "US Stocks - Momentum",
            "VOO": "US Stocks - Size (Large Cap)", 
            "IWM": "US Stocks - Size (Small Cap)",
            "IEF": "US Government Bonds - Long Term",
            "SHV": "US Government Bonds - Short Term",
            "VTEB": "Municipal Bonds",
            "TIP": "TIPS",
            "HYG": "US Corporate Bonds - High Yield", 
            "LQD": "US Corporate Bonds - Investment Grade",
            # "EMB": "Emerging Market Bonds - USD", 
            "BNDX": "Global Aggregate Bonds ex-US",
            "IAU": "Gold"
            })
    else:
        yf_df = yf_df.rename(columns={
            "IEMG": "Emerging Market Stocks",
            "VEA": "Foreign Developed Stocks",
            "IVW": "US Stocks - Growth (Large Cap)",
            "IWO": "US Stocks - Growth (Small Cap)",
            "IVE": "US Stocks - Value (Large Cap)", 
            "MTUM": "US Stocks - Momentum",
            "VOO": "US Stocks - Size (Large Cap)", 
            "IWM": "US Stocks - Size (Small Cap)",
            "IEF": "US Government Bonds - Long Term",
            "SHV": "US Government Bonds - Short Term",
            "VTEB": "Municipal Bonds",
            "TIP": "TIPS",
            "HYG": "US Corporate Bonds - High Yield", 
            "LQD": "US Corporate Bonds - Investment Grade",
            "EMB": "Emerging Market Bonds - USD", 
            "BNDX": "Global Aggregate Bonds ex-US",
            "IAU": "Gold"
            })
    
    style_df = pd.concat([style_df, yf_df[2:]],axis=0)
    style_tr = style_df.copy()
    style_tr = style_tr.dropna()
    style_price = style_tr.copy()
    style_price = (1 + style_price).cumprod() 
    
    asset_m = style_price.resample('M').last()
    first_row = asset_m.iloc[0,:]
    first_row = first_row - 1
    asset_m = asset_m.pct_change()
    asset_m.iloc[0,:] = first_row
    
    return asset_m


###2
def load_factor_data():
    # Load factor data
     
    start = dt.date(1990,7,1)
    
    # monthly
    us_factors = reader.DataReader('F-F_Research_Data_5_Factors_2x3','famafrench',start)[0]
    month_end_list = pd.date_range(start = start, end = None, periods = us_factors.shape[0], freq = 'M')
    us_factors.index = list(month_end_list)
    us_factors = us_factors / 100
    
    dm_factors = reader.DataReader('Developed_ex_US_5_Factors','famafrench',start)[0]
    month_end_list = pd.date_range(start = start, end = None, periods = dm_factors.shape[0], freq = 'M')
    dm_factors.index = list(month_end_list)
    dm_factors = dm_factors / 100
    
    em_factors = reader.DataReader('Emerging_5_Factors','famafrench',start)[0]
    month_end_list = pd.date_range(start = start, end = None, periods = em_factors.shape[0], freq = 'M')
    em_factors.index = list(month_end_list)
    em_factors = em_factors / 100

    return us_factors, dm_factors, em_factors


###3
def make_asset_rf(account):
    if account == 'taxable':
        us_list = [ # 13 assets
        "US Stocks - Growth (Large Cap)", 
        "US Stocks - Growth (Small Cap)",
        "US Stocks - Value (Large Cap)", 
        "US Stocks - Momentum",
        "US Stocks - Size (Large Cap)", 
        "US Stocks - Size (Small Cap)",
        "US Government Bonds - Long Term",
        "US Government Bonds - Short Term",
        "Municipal Bonds", 
        "TIPS",
        "US Corporate Bonds - High Yield", 
        "US Corporate Bonds - Investment Grade",
        "Gold"
        ]
        
        dm_list = [ # 2 assets
        "Foreign Developed Stocks", 
        "Global Aggregate Bonds ex-US"
        ]
        
        em_list = [ # 1 assets
        "Emerging Market Stocks"
        # "Emerging Market Bonds - USD"
        ]
    else:
        us_list = [ # 13 assets
        "US Stocks - Growth (Large Cap)", 
        "US Stocks - Growth (Small Cap)",
        "US Stocks - Value (Large Cap)", 
        "US Stocks - Momentum",
        "US Stocks - Size (Large Cap)", 
        "US Stocks - Size (Small Cap)",
        "US Government Bonds - Long Term",
        "US Government Bonds - Short Term",
        "Municipal Bonds", 
        "TIPS",
        "US Corporate Bonds - High Yield", 
        "US Corporate Bonds - Investment Grade",
        "Gold"
        ]
        
        dm_list = [ # 2 assets
        "Foreign Developed Stocks", 
        "Global Aggregate Bonds ex-US"
        ]
        
        em_list = [ # 2 assets
        "Emerging Market Stocks",
        "Emerging Market Bonds - USD"
        ]

    #dataset
    asset_m = load_asset_data(account)
    us_factors, dm_factors, em_factors = load_factor_data()

    intersection_date = list(set(list(us_factors.index))&set(list(dm_factors.index)))
    intersection_date = list(set(intersection_date)&set(list(em_factors.index)))
    intersection_date = list(set(intersection_date)&set(list(asset_m.index)))
    intersection_date.sort()

    # Dependent Variable
       
    # 1) us
    us_asset = asset_m[us_list]
    # 2) dm ex us
    dm_asset = asset_m[dm_list]
    # 3) em
    em_asset = asset_m[em_list]

    us_asset_rf = us_asset[us_asset.index.isin(intersection_date)]
    us_rf_series = us_factors['RF'][intersection_date]
    for i in us_list:
        us_asset_rf[i] = us_asset_rf[i] - us_rf_series
        
    dm_asset_rf = dm_asset[dm_asset.index.isin(intersection_date)]
    dm_rf_series = dm_factors['RF'][intersection_date]
    for i in dm_list:
        dm_asset_rf[i] = dm_asset_rf[i] - dm_rf_series
        
    em_asset_rf = em_asset[em_asset.index.isin(intersection_date)]
    em_rf_series = em_factors['RF'][intersection_date]    
    for i in em_list:
        em_asset_rf[i] = em_asset_rf[i] - em_rf_series

    return us_asset_rf, dm_asset_rf, em_asset_rf


###4
def make_expected_return_dict(account, window):

    us_asset_rf, dm_asset_rf, em_asset_rf = make_asset_rf(account)
    us_factors, dm_factors, em_factors = load_factor_data()
    intersection_date = list(us_asset_rf.index)

    # make dictionary of factor and asset return
    us_factors_chopped = us_factors[us_factors.index.isin(intersection_date)]
    dm_factors_chopped = dm_factors[dm_factors.index.isin(intersection_date)]
    em_factors_chopped = em_factors[em_factors.index.isin(intersection_date)]
    
    us_factors_dict = {}
    us_asset_rf_dict = {}
    
    dm_factors_dict = {}
    dm_asset_rf_dict = {}
    
    em_factors_dict = {}
    em_asset_rf_dict = {}
    
    b = len(intersection_date)
    
    for a in range(b-window):      
        us_factors_dict[a] = us_factors_chopped[a:a+window]
        us_asset_rf_dict[a] = us_asset_rf[a:a+window]
        #
        dm_factors_dict[a] = dm_factors_chopped[a:a+window]
        dm_asset_rf_dict[a] = dm_asset_rf[a:a+window]
        #
        em_factors_dict[a] = em_factors_chopped[a:a+window]
        em_asset_rf_dict[a] = em_asset_rf[a:a+window]

    # do OLS
    expected_return_rf_dict = {}

    if account == 'taxable':
        us_list = [ # 13 assets
        "US Stocks - Growth (Large Cap)", 
        "US Stocks - Growth (Small Cap)",
        "US Stocks - Value (Large Cap)", 
        "US Stocks - Momentum",
        "US Stocks - Size (Large Cap)", 
        "US Stocks - Size (Small Cap)",
        "US Government Bonds - Long Term",
        "US Government Bonds - Short Term",
        "Municipal Bonds", 
        "TIPS",
        "US Corporate Bonds - High Yield", 
        "US Corporate Bonds - Investment Grade",
        "Gold"
        ]
        
        dm_list = [ # 2 assets
        "Foreign Developed Stocks", 
        "Global Aggregate Bonds ex-US"
        ]
        
        em_list = [ # 1 assets
        "Emerging Market Stocks"
        # "Emerging Market Bonds - USD"
        ]
    else:
        us_list = [ # 13 assets
        "US Stocks - Growth (Large Cap)", 
        "US Stocks - Growth (Small Cap)",
        "US Stocks - Value (Large Cap)", 
        "US Stocks - Momentum",
        "US Stocks - Size (Large Cap)", 
        "US Stocks - Size (Small Cap)",
        "US Government Bonds - Long Term",
        "US Government Bonds - Short Term",
        "Municipal Bonds", 
        "TIPS",
        "US Corporate Bonds - High Yield", 
        "US Corporate Bonds - Investment Grade",
        "Gold"
        ]
        
        dm_list = [ # 2 assets
        "Foreign Developed Stocks", 
        "Global Aggregate Bonds ex-US"
        ]
        
        em_list = [ # 2 assets
        "Emerging Market Stocks",
        "Emerging Market Bonds - USD"
        ]

    for a in range(b-window):

        expected_returns = pd.DataFrame()    
    
        # us
        for i in us_list:
            y = us_asset_rf_dict[a][i] # Dependent variable
            x = us_factors_dict[a][['Mkt-RF', 'SMB','HML','RMW', 'CMA']]
            X_sm = sm.add_constant(x)
            model = sm.OLS(y, X_sm)
            results = model.fit()
            temp_expected = pd.DataFrame(results.predict(exog = X_sm), columns = [i])
            expected_returns = pd.concat([expected_returns,temp_expected], axis = 1)

        # dm
        for j in dm_list:
            y = dm_asset_rf_dict[a][j] # Dependent variable
            x = dm_factors_dict[a][['Mkt-RF', 'SMB','HML','RMW', 'CMA']]
            X_sm = sm.add_constant(x)
            model = sm.OLS(y, X_sm)
            results = model.fit()
            temp_expected = pd.DataFrame(results.predict(exog = X_sm), columns = [j])
            expected_returns = pd.concat([expected_returns,temp_expected], axis = 1)

        # em
        for k in em_list:
            y = em_asset_rf_dict[a][k] # Dependent variable
            x = em_factors_dict[a][['Mkt-RF', 'SMB','HML','RMW', 'CMA']]
            X_sm = sm.add_constant(x)
            model = sm.OLS(y, X_sm)
            results = model.fit()
            temp_expected = pd.DataFrame(results.predict(exog = X_sm), columns = [k])
            expected_returns = pd.concat([expected_returns,temp_expected], axis = 1)

        expected_return_rf_dict[a] = expected_returns
    
    return expected_return_rf_dict




###5
def make_asset_rf_dict(account, window):
    us_asset_rf, dm_asset_rf, em_asset_rf = make_asset_rf(account)
    asset_rf = pd.concat([us_asset_rf, dm_asset_rf, em_asset_rf], axis = 1)
    asset_rf_dict = {}

    intersection_date = list(us_asset_rf.index)
    b = len(intersection_date)
    
    for a in range(b-window):
        asset_rf_dict[a] = asset_rf[a:a+window]

    return asset_rf_dict



###6
def make_asset_mapper_dict(account, window):
    us_asset_rf, dm_asset_rf, em_asset_rf = make_asset_rf(account)
    asset_rf = pd.concat([us_asset_rf, dm_asset_rf, em_asset_rf], axis = 1)
    asset_rf_dict = {}

    intersection_date = list(us_asset_rf.index)
    b = len(intersection_date)
    
    for a in range(b-window):
        asset_rf_dict[a] = asset_rf[a:a+window]

    link_dict = {}
    for a in range(b - window):
        temp = asset_rf_dict[a]
        cov,corr = temp.cov(), temp.corr()
        dist = ((1-corr)/2.) ** .5
        link = sch.linkage(dist, 'single')        
        link_dict[a] = link   
        
    cluster_info = pd.DataFrame(index = asset_rf.index[window:], columns = asset_rf.columns)   

    num_of_cluster = 8
    for a in range(b - window):
        cluster_temp = cut_tree(link_dict[a], num_of_cluster)
        cluster_temp = pd.DataFrame(cluster_temp)
        cluster_temp = cluster_temp.T
        cluster_temp.columns = cluster_info.columns
        cluster_info[a:a+1] = cluster_temp
    
    asset_mapper_dict = {}
    date_list = list(cluster_info.index)
    col_list = list(cluster_info.columns)
    
    for i,j in enumerate(date_list):
        temp_map = {}
        
        for k in col_list:
            a = cluster_info[k][j]
        
            if a == 0:
                temp_map[k] = 'cluster_0'
            elif a == 1:
                temp_map[k] = 'cluster_1'
            elif a == 2:
                temp_map[k] = 'cluster_2'
            elif a == 3:
                temp_map[k] = 'cluster_3'
            elif a == 4:
                temp_map[k] = 'cluster_4'
            elif a == 5:
                temp_map[k] = 'cluster_5'
            elif a == 6:
                temp_map[k] = 'cluster_6'
            else:
                temp_map[k] = 'cluster_7'
        
        asset_mapper_dict[i] = temp_map

    return asset_mapper_dict

###6-2
def make_upper_bnd_dict():
    upper_bnd = {}
    upper_bnd[0] = {
        "cluster_0": 0.30, 
        "cluster_1": 0.30, 
        "cluster_2": 0.30, 
        "cluster_3": 0.30,
        "cluster_4": 0.30,
        "cluster_5": 0.30,
        "cluster_6": 0.30,
        "cluster_7": 0.30
        }
    upper_bnd[1] = {
        "cluster_0": 0.40, 
        "cluster_1": 0.40, 
        "cluster_2": 0.40, 
        "cluster_3": 0.40,
        "cluster_4": 0.40,
        "cluster_5": 0.40,
        "cluster_6": 0.40,
        "cluster_7": 0.40
        }
    upper_bnd[2] = {
        "cluster_0": 0.50, 
        "cluster_1": 0.50, 
        "cluster_2": 0.50, 
        "cluster_3": 0.50,
        "cluster_4": 0.50,
        "cluster_5": 0.50,
        "cluster_6": 0.50,
        "cluster_7": 0.50
        }
    upper_bnd[3] = {
        "cluster_0": 0.60, 
        "cluster_1": 0.60, 
        "cluster_2": 0.60, 
        "cluster_3": 0.60,
        "cluster_4": 0.60,
        "cluster_5": 0.60,
        "cluster_6": 0.60,
        "cluster_7": 0.60
        }
    upper_bnd[4] = {
        "cluster_0": 0.70, 
        "cluster_1": 0.70, 
        "cluster_2": 0.70, 
        "cluster_3": 0.70,
        "cluster_4": 0.70,
        "cluster_5": 0.70,
        "cluster_6": 0.70,
        "cluster_7": 0.70
        }
    upper_bnd[5] = {
        "cluster_0": 0.80, 
        "cluster_1": 0.80, 
        "cluster_2": 0.80, 
        "cluster_3": 0.80,
        "cluster_4": 0.80,
        "cluster_5": 0.80,
        "cluster_6": 0.80,
        "cluster_7": 0.80
        }
    upper_bnd[6] = {
        "cluster_0": 0.80, 
        "cluster_1": 0.80, 
        "cluster_2": 0.80, 
        "cluster_3": 0.80,
        "cluster_4": 0.80,
        "cluster_5": 0.80,
        "cluster_6": 0.80,
        "cluster_7": 0.80
        }
    upper_bnd[7] = {
        "cluster_0": 0.80, 
        "cluster_1": 0.80, 
        "cluster_2": 0.80, 
        "cluster_3": 0.80,
        "cluster_4": 0.80,
        "cluster_5": 0.80,
        "cluster_6": 0.80,
        "cluster_7": 0.80
        }
    upper_bnd[8] = {
        "cluster_0": 0.90, 
        "cluster_1": 0.90, 
        "cluster_2": 0.90, 
        "cluster_3": 0.90,
        "cluster_4": 0.90,
        "cluster_5": 0.90,
        "cluster_6": 0.90,
        "cluster_7": 0.90
        }
    upper_bnd[9] = {
        "cluster_0": 0.95, 
        "cluster_1": 0.95, 
        "cluster_2": 0.95, 
        "cluster_3": 0.95,
        "cluster_4": 0.95,
        "cluster_5": 0.95,
        "cluster_6": 0.95,
        "cluster_7": 0.95
        }

    return upper_bnd

###6-2
#lower_bounds # for diversification, I set the minimun wgt to each clusters

def make_lower_bnd_dict():
    lower_bnd = {
        "cluster_0": 0.01, 
        "cluster_1": 0.01, 
        "cluster_2": 0.01, 
        "cluster_3": 0.01,
        "cluster_4": 0.01,
        "cluster_5": 0.01,
        "cluster_6": 0.01,
        "cluster_7": 0.01
        }
    return lower_bnd



###7
def make_port_asset_wgt_dict(account, window):    

    vol_list = []    
    for i in range(10):
        vol_list.append('{:.1f}%'.format(6+i)) # changed

    #
    expected_return_rf_dict = make_expected_return_dict(account, window)
    #
    asset_mapper_dict = make_asset_mapper_dict(account, window)
    upper_bnd = make_upper_bnd_dict()
    lower_bnd = make_lower_bnd_dict()

    #
    us_asset_rf, dm_asset_rf, em_asset_rf = make_asset_rf(account)
    asset_rf = pd.concat([us_asset_rf, dm_asset_rf, em_asset_rf], axis = 1)
    asset_rf_dict = {}
    intersection_date = list(us_asset_rf.index)
    b = len(intersection_date)    
    for a in range(b-window):
        asset_rf_dict[a] = asset_rf[a:a+window]


    ff_wgt_dict = {} #ff for "Fama-French"
    ff_riskreturn_dict = {}

    rf = 0 #because it is already substracted to asset_rf

    for a in range(b - window):
        wgt_temp = []
        riskreturn_temp = []


        for i in range(10):
            # vol_tgt = round((6 + i * 1.2) / 100,3) # changed
            vol_tgt = (6 + i) / 100
            freq = 12 #monthly
            mu = ((1 + expected_return_rf_dict[a].mean()) ** freq) - 1
            s = risk_models.risk_matrix(asset_rf_dict[a], method="ledoit_wolf_single_factor", returns_data=True, frequency=freq)
        
            ef = EfficientFrontier(mu, s) #, solver="ECOS")
            ef.add_sector_constraints(asset_mapper_dict[a], lower_bnd, upper_bnd[i])
        
            raw_wgt = ef.efficient_risk(vol_tgt)
            wgt_temp.append(ef.clean_weights())
            riskreturn_temp.append(ef.portfolio_performance(risk_free_rate = rf))
    
        ff_wgt_dict[a] = wgt_temp
        ff_riskreturn_dict[a] = riskreturn_temp

    for a in range(b - window):
        ff_wgt_dict[a] = pd.DataFrame(ff_wgt_dict[a])
        ff_wgt_dict[a].index = vol_list
    
    return ff_wgt_dict

###8
# data_dict: result of 'make_port_asset_wgt_dict(account=, window = )'

def make_backtest_wgt_dict(account, window, data_dict):
    
    us_asset_rf, dm_asset_rf, em_asset_rf = make_asset_rf(account)
    asset_rf = pd.concat([us_asset_rf, dm_asset_rf, em_asset_rf], axis = 1)
    b = len(asset_rf.index)

    port_list = list(data_dict[0].index) 

    ff_backtest_wgt = {}
    
    for i, k in enumerate(port_list):
        temp_df = pd.DataFrame()   
        
        for j in range(b - window):
            temp = pd.DataFrame.from_dict(data_dict[j].loc[k]) #, orient = 'index', columns = [j])
            temp = temp.T
            temp_df = pd.concat([temp_df, temp], axis = 0)
            
        temp_df.index = asset_rf[window:][:(b-window)].index
    
        #saving last row(it will be dropped after shift(1))
        temp_last_row = pd.DataFrame(temp_df[-1:])
        last_month_end = temp_last_row.index[0] + pd.offsets.MonthEnd(1)
        temp_last_row.rename(index = {temp_last_row.index[0] : last_month_end}, inplace = True)
    
        # the time lag of factor data release is assumed to be 1M
        temp_df = temp_df.shift(1) 
        temp_df = temp_df[1:]
        temp_df = pd.concat([temp_df, temp_last_row])
        ff_backtest_wgt[k] = temp_df    
    
    return ff_backtest_wgt

###9
# data_dict: result of 'make_backtest_wgt_dict(account=, window=, data_dict=)'

def make_portfolio_rt_df(account, data_dict):
    asset_m =load_asset_data(account)
    
    # time lag of the data release(1M) is considered
    date_list = list(data_dict['6.0%'].index)
    asset_m_test = asset_m[asset_m.index.isin(date_list)]
    
    ff_portfolio_rt = pd.DataFrame()
    port_list = list(data_dict.keys())

    for i,j in enumerate(port_list):
        temp_rt = asset_m_test * data_dict[j]
        temp_rt = temp_rt.sum(axis = 1)
        ff_portfolio_rt[j] = temp_rt
        
    ew_rt = asset_m_test * (1/asset_m_test.shape[1])
    ew_rt = ew_rt.sum(axis = 1)
    ff_portfolio_rt['EW'] = ew_rt
    
    traditional_rt = asset_m_test["US Stocks - Size (Large Cap)"] * (0.6) + asset_m_test["US Government Bonds - Long Term"] * (0.4)
    ff_portfolio_rt['60/40'] = traditional_rt
    
    ff_portfolio_rt

    return ff_portfolio_rt

###10
# data_df: result of 'make_portfolio_rt_df(account = , data_dict = )'

def make_port_analysis_df(data_df):

    # Load Mkt-RF, RF data
    start = dt.date(1990,7,1)
    factors = reader.DataReader('F-F_Research_Data_5_Factors_2x3','famafrench',start)[0]
    month_end_list = pd.date_range(start = start, end = None, periods = factors.shape[0], freq = 'M')
    factors.index = list(month_end_list)
    factors = factors / 100

    intersection_date = list(set(list(factors.index))&set(list(data_df.index)))
    intersection_date.sort()
    
    factors = factors[factors.index.isin(intersection_date)]
    data_df = data_df[data_df.index.isin(intersection_date)]

    rf_series = factors['RF']
    mkt_series = factors['Mkt-RF']

    ## asset statistics
    beta = {}
    alpha = {}
    expected_return = {}
    historical_return = {}
    historical_vol = {}
    
    freq = 12 # monthly data
    rf = ((1 + rf_series.mean()) ** freq - 1) * 100
    rm_rf = ((1 + mkt_series.mean()) ** freq - 1) * 100
    
    col_list = list(data_df.columns)
    
    for i in col_list:
        b, a = np.polyfit(mkt_series, data_df[i], 1)
        beta[i] = b    
        alpha[i] = a * 100
        expected_return[i] = rf + b * (rm_rf)
        historical_return[i] = ((1 + data_df[i].mean()) ** freq - 1) * 100
        historical_vol[i] = data_df[i].std() * ((freq)**(1/2)) * 100

    alpha_df = pd.DataFrame.from_dict(alpha, orient = 'index', columns = ['Alpha']) 
    beta_df = pd.DataFrame.from_dict(beta, orient = 'index', columns = ['Beta'])
    expected_return_df = pd.DataFrame.from_dict(expected_return, orient = 'index', columns = ['Expected Return(CAPM)'])
    historical_return_df = pd.DataFrame.from_dict(historical_return, orient = 'index', columns = ['Historical Return'])
    historical_vol_df = pd.DataFrame.from_dict(historical_vol, orient = 'index', columns = ['Historical Volatility'])
    
    port_stats = pd.concat([alpha_df, beta_df,expected_return_df, historical_return_df, historical_vol_df], axis = 1)
    port_stats['Sharpe Ratio'] = port_stats['Historical Return'] / port_stats['Historical Volatility']
   
    # MDD for past 3 years
    port_price = data_df.copy()
    port_price = (1+port_price).cumprod()
    roll_max = port_price.rolling(36, min_periods=1).max()
    monthly_drawdown = port_price/roll_max - 1.0
    max_drawdown = monthly_drawdown.rolling(36, min_periods=1).min()
    mdd = max_drawdown[-1:].T * 100
    mdd.columns = ['MDD']

    port_stats = pd.concat([port_stats,mdd], axis = 1)
    
    return port_stats






