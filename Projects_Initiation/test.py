import pickle
data_df = pickle.load(open('./pickle_files/data_df.pkl', 'rb'))
print(data_df['Book-Title'].iloc[67:90])