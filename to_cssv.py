import pandas as pd

df = pd.read_json("data.json")
df.to_csv("train_data.csv", index = False)