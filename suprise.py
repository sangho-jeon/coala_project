import surprise
import numpy as np
import pandas as pd
from surprise.model_selection import KFold
from surprise.model_selection import cross_validate



data = pd.read_csv('bbb.csv')

bsl_options = {
    'method': 'als',
    'n_epochs': 5,
    'reg_u': 12,
    'reg_i': 5
}
algo = surprise.BaselineOnly(bsl_options)

print(cross_validate(algo, data))


