import pandas as pd

sheet_id = "14Ep-CmoqWxrMU8HshxthRcdRW8IsXvh3n2-ZHVCzqzQ"

df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")

print(df.head())
