from utils.label import * 
from utils.resprocess import * 
from utils.output import *
import pandas as pd


# config
DIR = './5000'
LABEL = ['個股分析', '預測']
RESPONSE = 13


# read data
with open(f'./response/response{RESPONSE}.txt', 'r', encoding='utf-8') as f:
    data = f.read()


# proccess 
qli = extractq(data)
label = generate_output_binary(LABEL)
q_label_li = batch_label_list(qli, label)


# output
df = pd.DataFrame({'q':qli, 'y':q_label_li})

# file index
max_index = get_m_index(DIR)
output_index = max_index+1

# label str
output_string = '_'.join(LABEL)

filename = f"{output_index}_{output_string}"

df.to_csv(f"./5000/{filename}_response{RESPONSE}.csv")

# print(qli, q_label_li)