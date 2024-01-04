import numpy as np


def divide_two_cols(df_sub):
    df_sub['volume_delta_1'] = df_sub['成交量_1'] / df_sub['成交量']
    return df_sub



def get_vol_increase_id(df_sub, thres = 500):
    df_sub['vol_increase_id'] = df_sub[(df_sub['成交量']>thres)&(df_sub['volume_delta_1']>2)].index
    return df_sub

def get_indicator(df_sub):
    df_sub['indicator'] = df_sub.index.isin(df_sub['vol_increase_id']).astype(int)
    return df_sub

def get_abnormal(df_sub):
    df_sub['abnormal'] = (df_sub['indicator'].shift(1) == 0) & (df_sub['indicator'] == 1)
    return df_sub





def get_indcum(col_ret, col_abnormal, num_period):

    res_p = []
    res = []
    i = 0

    while i <= len(col_abnormal)-num_period+1:
        # print(i)
        tmp_sig = col_abnormal[i:i+num_period]
        tmp_ret = col_ret[i:i+num_period]

        if tmp_sig.iloc[0]==True:
            res.extend(list(np.cumprod(1 + tmp_ret.values) - 1))
            res_p.append(list(np.cumprod(1 + tmp_ret.values) - 1))
            # print(list(np.cumprod(1 + tmp_ret.values) - 1))
            i += num_period
            next

        else: 
            # print(tmp_ret.iloc[0])
            res.append(tmp_ret.iloc[0])
            i += 1
            
    if i > len(col_abnormal)-num_period+1:
        if tmp_sig.iloc[0]==True:
            res.extend(list(np.cumprod(1 + col_abnormal[i:].values) - 1))
            res_p.append(list(np.cumprod(1 + col_abnormal[i:].values) - 1))
        else:
        # res.extend(tmp_ret)
        # print(len(col_ret[i:]))
            res.extend(col_ret[i:])

    return res, res_p


