import pandas as pd
from tqdm import tqdm
from .XD import *
import numpy as np
import eventstudy as es
import concurrent.futures

class EventStudy:
    
    
    def __init__(self, df):
        self.original_df = df
        self.tick_event_dict = {}
        self.final_res = pd.DataFrame(columns=['AR', 'Std. E. AR', 'CAR', 'Std. E. CAR', 'T-stat', 'P-value',
       'evnet_window', 'EventDate', 'symbol'])
        
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
        



    def create_events(self):

        self.original_df = self.mutate_basic_cols(self.original_df)
        
        uq_tick = self.original_df['股號'].unique()
        
        print('\n')
        print('Processing Create events : ')
        for tick in tqdm(uq_tick,  desc="Looping ticks", leave=False):
            df_tick = self.original_df[self.original_df['股號']==tick].reset_index(drop=True)
            
            # Define your events here ###################
            
            # Event1 量起
            event_1 = df_tick[(df_tick['成交量']>500)&(df_tick['volume_delta_1']>2)].index
            
            
            #############################################
            
            
            # get Intersection of Event
            event_common_id = self.recursive_intersection([event_1])
            
            # get event date
            event_date = df_tick['日期'][event_common_id].to_list()

            # Store result 
            self.tick_event_dict[f'{tick}'] = event_date
        
            
    def perform_es(self, stock_filter_list = [], 
                  event_window = (0,+10), estimation_size = 30, 
                  buffer_size = 30):
        print('\n')
        print('Processing Perform ES : ')
        err = []
        for tick in tqdm(self.tick_event_dict, desc="Looping ticks", leave=False):
            if tick in stock_filter_list:
                
                es.Single.import_returns(path=f'../1230/df/returns_{tick}.csv', date_format = '%Y-%m-%d')
                es.Single.import_FamaFrench(path=f'../1230/df/fama_{tick}.csv', date_format = '%Y-%m-%d')
                
                for ed in self.tick_event_dict[tick]:
                    
                    # Define your Model Here ###################
                    try:
                        event = es.Single.FamaFrench_3factor(
                            security_ticker = str(tick),
                            event_date = np.datetime64(str(ed)),
                            event_window = event_window, 
                            estimation_size = estimation_size, # 注意這個
                            buffer_size = buffer_size,
                            keep_model=False
                        )
                    #############################################
                        tick_res = es_res_tick_process(event=event, ed = ed, tick=tick)
                        self.final_res = pd.concat([self.final_res, tick_res], ignore_index=True) 
                                
                    except:
                        err.append([tick, ed])
                        continue
                
        return self.final_res
        
        
    def perform_es_worker(self, tick, stock_filter_list, event_window, estimation_size, buffer_size):
        if tick in stock_filter_list:
            try:
                es.Single.import_returns(path=f'../1230/df/returns_{tick}.csv', date_format='%Y-%m-%d')
                es.Single.import_FamaFrench(path=f'../1230/df/fama_{tick}.csv', date_format='%Y-%m-%d')
                for ed in self.tick_event_dict[tick]:
                    # Define your Model Here ###################
                    event = es.Single.FamaFrench_3factor(
                        security_ticker=str(tick),
                        event_date=np.datetime64(str(ed)),
                        event_window=event_window,
                        estimation_size=estimation_size,  # 注意這個
                        buffer_size=buffer_size,
                        keep_model=False
                    )
                    #############################################
                    tick_res = es_res_tick_process(event=event, ed=ed, tick=tick)
                    self.final_res = pd.concat([self.final_res, tick_res], ignore_index=True)

            except Exception as e:
                print(f"Error processing {tick} - {ed}: {e}")



    def perform_es_thread(self, stock_filter_list=[], event_window=(0, +10), estimation_size=30, buffer_size=30):
        print('\n')
        print('Processing Perform ES : ')
        err = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.perform_es_worker, tick, stock_filter_list, event_window, estimation_size, buffer_size)
                    for tick in self.tick_event_dict]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error in thread: {e}")
                    err.append(str(e))

        return self.final_res



    
    def process_final_res(self):
        self.final_res = self.final_res.rename(columns={'P-value':'p', 'T-stat':'t'})
        self.final_res['evnet_window'] = self.final_res['evnet_window'].astype(str).astype(int)
        self.final_res['symbol'] = self.final_res['symbol'].astype(str)
        
        
        # final_res.groupby(['symbol', 'EventDate']).filter(lambda x: ((x.p<= 0.05) & (x.evnet_window > 0)).all())
        res_analysis = self.final_res.assign(
            
            # the second position is where to sum
            negative_significant_after_event = np.where((self.final_res['evnet_window']>0) & (self.final_res['t']<0), self.final_res['p']<=0.05, 0),
            positive_significant_after_event = np.where((self.final_res['evnet_window']>0) & (self.final_res['t']>0), self.final_res['p']<=0.05, 0),
            
            
        ).groupby(['EventDate', 'symbol'], as_index=False).agg({'negative_significant_after_event':sum, 'positive_significant_after_event':sum})
        
        
        return res_analysis