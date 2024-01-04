import re

def extractq(s):
    '''
    Input

    str : chatgpt response 
    e.g 
    1. 如何識別潛在的高風險高回報ETFs，並評估其與傳統低風險ETF之間的平衡策略？
    2. ETF的流動性如何影響我作為一名散戶投資者進入和退出市場的時機？

    Output

    list : [q1, q2 ...]
    '''
    res = []
    pattern = r'\d+\.\s(.*)'
    matches = re.findall(pattern, s)

    for match in matches:
        res.append(match)

    return res


