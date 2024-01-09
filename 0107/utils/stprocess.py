
import pandas as pd
from tqdm import tqdm
from .XD import *
import numpy as np
import concurrent.futures
from .XD import *
import pymannkendall as mk


class StatWindow:
    
    def __init__(self, df):
        self.original_df = df
        self.backtest_ret_li = []
        self.backtest_signal_li = []
        self.backtest_date_li = []
        
        self.backtest_ret_arr = None
        self.backtest_signal_arr = None
        self.backtest_date_arr = None
        self.backtest_tick_li = []
    
    @staticmethod
    def result_analysis(res_df):
        
        # Group by 'tick' and 'mk_test', then calculate the value counts
        grouped = res_df.groupby(['tick', 'mk_test']).size().unstack(fill_value=0)

        # Calculate the percentage for each group
        grouped_percentage = grouped.div(grouped.sum(axis=1), axis=0) * 100

        # Add a new column for the total count of all outcomes
        grouped_percentage['total_outcomes'] = grouped.sum(axis=1)

        # Reset index to make 'tick' a regular column
        grouped_percentage.reset_index(inplace=True)

        # Rename the columns
        grouped_percentage.columns = ['tick', 'decreasing_percentage', 'increasing_percentage', 'no_trend_percentage', 'total_outcomes']

        # Display the resulting DataFrame
        return grouped_percentage
    
    
    @staticmethod
    def convert_res2_pandas(res):
        _2ddict = {index: value for index, value in enumerate(res)}
        _1ddict = {}
        for i in _2ddict.keys():
            try:
                tick = list(_2ddict[i].keys())[0]
                _1ddict[tick] = _2ddict[i][tick]
            except IndexError:
                continue
        res_df = pd.concat({k: pd.DataFrame(v) for k, v in _1ddict.items()}).reset_index(level=1)
        res_df.columns = ['tick', 'mk_test', 'date']
        res_df['tick'] = res_df.index
        return res_df.reset_index(drop=True)
    
    @staticmethod
    def recursive_intersection(index_list):
        
        '''
        # Sample indexes
        index1 = pd.Index([1, 2, 3, 4, 5])
        index2 = pd.Index([3, 4, 5, 6, 7])
        index3 = pd.Index([5, 6, 7, 8, 9])

        # Perform recursive intersection
        result = recursive_intersection([index1, index2, index3])

        print("Intersection:", result)        
        '''
        if len(index_list) == 1:
            return index_list[0]
        else:
            return index_list[0].intersection(self.recursive_intersection(index_list[1:]))
    

    @staticmethod
    def mutate_basic_cols(df):
        
        df['成交量_1'] = df.groupby('股號', as_index=False)['成交量'].shift(-1)


        df = df.groupby('股號', as_index=False).apply(divide_two_cols)

        df['ret'] = df.groupby('股號')['收盤價'].pct_change()
        df = df.dropna()
        return df
    
    @staticmethod
    def stattest(ret_li: list, signal_li: list, date_li: list, tick: str, post_event_window=10) -> dict:
        res = {}
        i = 0
        
        test_result_tick = {'mk_test':[], 'date':[]}
        while i <= len((ret_li))-post_event_window+1:
            tmp_sig = signal_li[i:i+post_event_window]
            tmp_ret = np.array(ret_li[i:i+post_event_window])
            tmp_date = date_li[i:i+post_event_window]
            
            if tmp_sig[0]==True:
                res_cum_ret = np.cumprod(1 + tmp_ret) - 1
                
                # Change your statics method here ###############
                trend, h, p, z, Tau, s, var_s, slope, intercept =  mk.original_test(res_cum_ret)
                #################################################
                test_result_tick['mk_test'].append(trend)
                test_result_tick['date'].append(tmp_date[0])
                
                res[tick]=test_result_tick
                
            i+=1
            
        return res
    
    def create_events_st(self):
        
        self.original_df = self.mutate_basic_cols(self.original_df)

        
        uq_tick = self.original_df['股號'].unique()
        for tick in tqdm(uq_tick,  desc="Looping ticks", leave=False):
            self.backtest_tick_li.append(tick)
            
            
            df_tick = self.original_df[self.original_df['股號']==tick].reset_index(drop=True)

            # Define your events here ###################
            
            # Event1 量起
            event_1 = df_tick[(df_tick['成交量']>500)&(df_tick['volume_delta_1']>2)].index
            
            # Event2 量起
            # Event 
            
            #############################################
            
            
            
            # get Intersection of Event
            event_common_id = self.recursive_intersection([event_1])
            
            # signal li
            self.backtest_signal_li.append(
                df_tick.index.isin(event_common_id).astype(int).tolist())
            
            # ret li
            self.backtest_ret_li.append(df_tick['ret'].replace(np.inf, 0).tolist())
            
            # date li
            self.backtest_date_li.append(df_tick['日期'].tolist())


        self.backtest_ret_arr = np.array(self.backtest_ret_li, dtype=object)
        self.backtest_signal_arr = np.array(self.backtest_signal_li, dtype=object)
        self.backtest_date_arr = np.array(self.backtest_date_li, dtype=object)
        
        
        return (self.backtest_ret_arr, 
                self.backtest_signal_arr, 
                self.backtest_date_arr, 
                self.backtest_tick_li)
        
    def perform_stat_test(self):
        
        stattest_vec = np.vectorize(self.stattest)
        res = stattest_vec(self.backtest_ret_arr, self.backtest_signal_arr,
                           self.backtest_date_arr, self.backtest_tick_li)
        return res
    
    
        