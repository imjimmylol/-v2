from utils.label import * 
from utils.resprocess import * 
from utils.output import *
import pandas as pd

DIR = './5000'
response_index_li = [2,3,4,5,6,7,8,9,11,12,14,15,16]
# response_index_li = [8]

for i in response_index_li:
    #### read data
    with open(f'./response/response{i}.txt', 'r', encoding='utf-8') as f:
        data = f.read()

    #### proccess
    
    # extract q
    qli = extractq(data)
    # taglist
    taglist = extract_tags_from_list_p2(qli)
    # print(taglist)
    # print([i for i,x in enumerate(taglist) if x==None])

    # remove some q 
    remove_indices = [i for i,x in enumerate(taglist) if x==None]
    qli = [i for j, i in enumerate(qli) if j not in remove_indices]
    taglist = [i for j, i in enumerate(taglist) if j not in remove_indices]

    q_label_li = list(map(generate_output_binary, taglist))

    #### output
    df = pd.DataFrame({'q':qli, 'y':q_label_li})

    # file index
    max_index = get_m_index(DIR)
    output_index = max_index+1


    # label str

    filename = f"{output_index}_p2"

    # df.to_csv(f"./5000/{filename}_response{RESPONESE}.csv")
    df.to_csv(f"./5000/response{i}_p2.csv")