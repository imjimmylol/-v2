import pandas as pd
import numpy as np
import warnings
from tqdm import tqdm
import itertools
import pymannkendall as mk
import matplotlib.pyplot as plt 
import yfinance as yf
from scipy.stats import wilcoxon
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, cpu_count
import os, sys
from pathlib import Path
import pickle
sys.path.append(str(Path(os.getcwd()).parent.parent / '1226' / 'utils'))
import XD
from utils import multi
warnings.filterwarnings("ignore")

N_P = 10



if __name__ == "__main__":
    
    q = pd.read_csv("../../1223/data/concentration/quote/2020_20230814.csv", index_col=False).dropna()
    brk = pd.read_csv("../../1223/data/concentration/brk/2022_BrkNetAmt.csv", index_col=False).dropna()

    df = pd.merge(q, brk, on=['日期', '股號'], how='left')
    df = df.groupby('股號').apply(lambda x: x.sort_values('日期')).reset_index(drop=True)
    df = df.rename(columns={'漲跌幅(%)':'ret'})
    
    bk_uq_id = df['分點'].unique()

    # Event by broker
    num_processes = min(cpu_count(), len(bk_uq_id))

    with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        list(tqdm(executor.map(multi.process_bk, [bk for bk in bk_uq_id], [df for _ in range(len(bk_uq_id))]), total=len(bk_uq_id)))

    df = df.drop(columns=['indicator_nan'])