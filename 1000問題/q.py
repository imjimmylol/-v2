import pandas as pd
import os

# Specify the directory containing the CSV files
directory_path = './5000'

# Get a list of all CSV files in the directory
csv_files = [file for file in os.listdir(directory_path) if file.endswith('.csv')]

# Initialize an empty DataFrame to store the merged data
merged_df = pd.DataFrame()

# Loop through each CSV file and concatenate them vertically
for csv_file in csv_files:
    file_path = os.path.join(directory_path, csv_file)
    df = pd.read_csv(file_path)
    merged_df = pd.concat([merged_df, df], ignore_index=True)

print(merged_df.shape)
# Display the merged DataFrame
merged_df.to_csv('./5000_merged/res.csv', encoding='utf-8')