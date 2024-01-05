import pandas as pd
import numpy as np

def process_bk(bk, df):
    try:
        signal_id = df[((df['買賣超金額'].notnull()) | df['買賣超金額'].notna()) & (df['分點'] == f'{bk}')].index
        df[f'indicator_{bk}'] = df.index.isin(signal_id).astype(int)
    except:
        df[f'indicator_{bk}'] = 0

            

        

def element_to_2d_array(element):
    return np.array(element, dtype=object)


def transpose_element(element):
    return np.transpose(element)

def _2list(x):
    return x[0].astype('float64').tolist()

def get_indcum(ret1darr,ind1darr, num_period=10):
    res = np.array([])
    i = 0
    while i <= len(ind1darr)-num_period+1:
        tmp_sig = ind1darr[i:i+num_period]
        tmp_ret = ret1darr[i:i+num_period]
        
        if tmp_sig[0]==True:
            res = np.append(res, np.cumprod(1 + tmp_ret) - 1)
            # print(np.cumprod(1 + tmp_ret) - 1)
            # print(list(np.cumprod(1 + tmp_ret.values) - 1))
            i += num_period
            next

        else: 
            # print(tmp_ret.iloc[0])
            res = np.append(res, tmp_ret[0])
            i += 1
            
    if i > len(ind1darr)-num_period+1:
        if tmp_sig[0]==True:
            res = np.append(res, np.cumprod(1 + ind1darr[i:]) - 1)
        else:
            res = np.append(res, ret1darr[i:])
    return res