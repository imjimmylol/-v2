import os
import re

def get_m_index(DIR):
    pattern = r'\d+'
    file_names = [f for f in os.listdir(DIR) if f.endswith('.csv')]
    numbers = [int(match) for string in file_names for match in re.findall(pattern, string)]

    if len(numbers)==0:
        return 0
    else:
        max_number = max(numbers)
        return max_number