import re
label_map = {
    '個股分析':0,
    '多股比較':1,	
    '個股資料查詢':2,	
    '產業':3,
    '大盤':4,
    '實務':5,
    '推薦軟條件':6,	
    '選股硬條件':7,	
    '字典查詢':8,
    '預測':9,	
    '不處理':10,	
    '總經與其他金融工具':11,
    '學習請教':12,
}

def generate_output_binary(input_list, label_map=label_map):
    # 创建一个长度为 13 的列表，初始值为 0
    output_list = [0] * 13

    # 遍历输入列表，将对应位置的值更新为 1
    for label in input_list:
        if label in label_map:
            output_list[label_map[label]] = 1

    return output_list



def extract_tags_from_question_p2(question):
    # 使用正则表达式匹配括号内的标签
    pattern = r'\？\（(.*?)\）'
    matches = re.findall(pattern, question)
    if len(matches)!=0:
        if '、' in matches[0]:
            return matches[0].split('、')
        else:
            return matches
        # return matches[0].split('、')

def extract_tags_from_list_p2(input_list):
    # 对输入列表中的每个问题应用extract_tags_from_question函数
    result_list = [extract_tags_from_question_p2(question) for question in input_list]
    # print(result_list)
    return result_list 


def batch_label_list(qli, labels):
    return [labels for i in range(len(qli))]