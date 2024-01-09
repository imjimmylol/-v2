import pandas as pd
import numpy as np

def divide_two_cols(df_sub):
    df_sub['volume_delta_1'] = df_sub['成交量_1'] / df_sub['成交量']
    return df_sub


def es_res_tick_process(event, ed, tick):
    tick_res = event.results(decimals=[3,5,3,5,2,2])
    tick_res['evnet_window'] = tick_res.index
    tick_res['EventDate'] =  np.datetime64(ed)
    tick_res['symbol'] = tick
    tick_res = tick_res.reset_index(drop=True)
    
    return tick_res