import pandas as pd

file_stats = 'C:/Users/hlio4/Desktop/Players_Categorized_stats.xlsx'
file_salaries = 'C:/Users/hlio4/Desktop/Players salaries.xlsx'

stats_df = pd.read_excel(file_stats)
salaries_df = pd.read_excel(file_salaries)

merged_df = pd.merge(stats_df, salaries_df, on='Player', how='outer')

columns_to_drop = [
    'Unnamed: 21', 'Unnamed: 22', 'Unnamed: 23', 'Unnamed: 24', 'Unnamed: 25',
    'Unnamed: 26', 'Unnamed: 27', 'Unnamed: 28', 'Unnamed: 29', 'Unnamed: 30',
    'Age.1', 'RkOv', '%D', '#', 'Position_y', 'Age_y', 'Team_y',
     '2025/26', '2026/27', '2027/28'
]

merged_df.drop(columns=columns_to_drop, errors='ignore', inplace=True)

print("Column headers after merge and drop:")
print(merged_df.columns)

if '2024/25' in merged_df.columns:
    merged_df['2024/25'].fillna(500, inplace=True)
else:
    print("The column '2024/25' does not exist in the merged DataFrame.")


output_file = 'C:/Users/hlio4/Desktop/Combined_Players_Data33.xlsx'
merged_df.to_excel(output_file, index=False)

print(f"Το αρχείο δημιουργήθηκε: {output_file}")



