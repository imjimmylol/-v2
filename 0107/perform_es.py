from utils import esprocess
import pandas as pd


PARAMS = {
    
    'stock_filter_list':[],
    'event_window':(0,+10),
    'estimation_size':30,
    'buffer_size':30,
    'window_size':10,
    'n_signal':10,
    'positive_sig_percent':0.8
}


if __name__ == "__main__":
    
    
    # Load data
    cn = pd.read_csv("../1223/data/concentration/concentration/2020_20230814.csv", index_col=False).dropna()
    q = pd.read_csv("../1223/data/concentration/quote/2020_20230814.csv", index_col=False).dropna()
    rf = pd.read_csv("../1223/data/concentration/rf/rf.csv").dropna().rename(columns={'日期':'date'})
    df = pd.merge(q, cn, on=['日期', '股號'], how='left')
    df = df.groupby('股號').apply(lambda x: x.sort_values('日期')).reset_index(drop=True)
    
    
    df = pd.merge(q, cn, on=['日期', '股號'], how='left').reset_index(drop=True)

    es_engine = esprocess.EventStudy(df)
    es_engine.create_events()
    es_engine.perform_es(stock_filter_list=['1101', '1102', '1103'])
    res = es_engine.process_final_res()
    
    print(res)
    # es_engine.perform_es()