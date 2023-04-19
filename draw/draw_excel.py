import pandas as pd

file_path="./draw_result.xlsx"
sht_names = pd.ExcelFile(file_path).sheet_names # 返回所有 sheet 名称组成的列表

for sht_name in sht_names:
    df = pd.read_excel(file_path, sheet_name=sht_name)
    print(df.info())