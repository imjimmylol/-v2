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