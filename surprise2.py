import pandas as pd

ratings = pd.read_csv('user.csv')

from surprise import Reader, Dataset

reader = Reader(rating_scale=(0.5, 5.0))
data = Dataset.load_from_df(ratings[['user_id', 'game ', 'play_time']], reader)

data.split(n_folds=5)

from surprise import model_selection
from surprise import SVD
from surprise import NMF
from surprise import KNNBasic

# svd
algo = SVD()
print(model_selection(algo, data, measures=['RMSE']))

# nmf
# algo = NMF()
# evaluate(algo, data, measures=['RMSE'])
#
# algo = KNNBasic()
# evaluate(algo, data, measures=['RMSE'])

