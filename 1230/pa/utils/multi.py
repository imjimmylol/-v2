import pandas as  pd
import numpy as np
import os, sys
from pathlib import Path
import itertools
from tqdm import tqdm
import pymannkendall as mk
from multiprocessing import Pool
from functools import partial
from concurrent.futures import ThreadPoolExecutor


def get_indcum_parallel(col_ret, col_abnormal, num_period, num_threads=8):
    res_p = []
    res = []
    i = 0

    def process_chunk(start, end):
        nonlocal res, res_p

        for i in range(start, end):
            tmp_sig = col_abnormal[i:i+num_period]
            tmp_ret = col_ret[i:i+num_period]

            if tmp_sig.iloc[0] == True:
                res.extend(list(np.cumprod(1 + tmp_ret.values) - 1))
                res_p.append(list(np.cumprod(1 + tmp_ret.values) - 1))
                i += num_period
                continue
            else:
                res.append(tmp_ret.iloc[0])
                i += 1

        return res, res_p

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        chunk_size = len(col_abnormal) // num_threads
        futures = []

        for i in range(0, len(col_abnormal), chunk_size):
            future = executor.submit(process_chunk, i, min(i + chunk_size, len(col_abnormal)))
            futures.append(future)

        for future in futures:
            chunk_res, chunk_res_p = future.result()
            res.extend(chunk_res)
            res_p.extend(chunk_res_p)

    if i > len(col_abnormal) - num_period + 1:
        if tmp_sig.iloc[0] == True:
            res.extend(list(np.cumprod(1 + col_abnormal[i:].values) - 1))
            res_p.append(list(np.cumprod(1 + col_abnormal[i:].values) - 1))
        else:
            res.extend(col_ret[i:])

    return res, res_p

def process_bk(bk, df):
    if bk:
        signal_id = df[((df['買賣超金額'].notnull()) | df['買賣超金額'].notna()) & (df['分點'] == f'{bk}')].index
        df[f'indicator_{bk}'] = df.index.isin(signal_id).astype(int)
        

def process_tick(tick, bk, g_df, N_P):
    result_trend = {}
    tmp = g_df.get_group(tick)
    try:
        # calculate cumulative event related return
        c, cp = get_indcum_parallel(col_ret=tmp['ret'], col_abnormal=tmp[f'indicator_{bk}'], num_period=N_P)
        tmp[f'cumret_{bk}_{N_P}'] = c

        # perform test
        cp = list(k for k, _ in itertools.groupby(cp))

        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(mk.original_test, l): i for i, l in enumerate(cp)}

        for future in concurrent.futures.as_completed(futures):
            i = futures[future]
            try:
                trend, h, p, z, Tau, s, var_s, slope, intercept = future.result()
                result_trend[f'{i}_trend'] = trend
            except Exception as e:
                pass

        if len(result_trend) != 0:
            return tick, result_trend

    except KeyError:
        pass

def get_res_by_tick_parallel(stock_uq_id, bk, g_df, N_P, num_processes=8):
    stock_uq_id = stock_uq_id[:]
    res_tick = {}
    with Pool(num_processes) as pool, tqdm(total=len(stock_uq_id)) as pbar:
        process_func = partial(process_tick, bk=bk, g_df=g_df, N_P=N_P)
        results = list(tqdm(pool.imap(process_func, stock_uq_id), total=len(stock_uq_id)))

    for result in results:
        if result:
            tick, result_trend = result
            res_tick[tick] = result_trend
            pbar.update(1)

    return res_tick