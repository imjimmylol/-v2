from utils import stprocess
import pandas as pd





if __name__ == "__main__":
    
    df = pd.read_csv("../1223/data/concentration/quote/2020_20230814.csv").dropna()
    df = df.groupby('股號', as_index=False).apply(lambda x: x.sort_values('日期')).reset_index(drop=True)
    
    st_engine = stprocess.StatWindow(df)
    ret, sig, date, tick = st_engine.create_events_st()
    res = st_engine.perform_stat_test()
    res = stprocess.StatWindow.convert_res2_pandas(res)
    res_analysis = stprocess.StatWindow.result_analysis(res)
    print(res_analysis)