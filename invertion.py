import pandas as pd

df = pd.read_csv('user.csv')

df_invert = df.pivot('user_id', 'game', 'time')

