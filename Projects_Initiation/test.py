import pickle
import numpy as np
data_df = pickle.load(open('./pickle_files/data_df.pkl', 'rb'))

dashboard_df = pickle.load(open('./pickle_files/dashboard.pkl', 'rb'))
data_df = pickle.load(open('./pickle_files/data_df.pkl', 'rb'))
pivot_table = pickle.load(open('./pickle_files/pivot_table.pkl', 'rb'))
similarity = pickle.load(open('./pickle_files/similarity.pkl', 'rb'))


# Save the indices to a list
indices_list = list(pivot_table.index)

# Specify the file path for the 'index.txt' file
file_path = 'index.txt'

# Open the file in write mode and write the indices
with open(file_path, 'w') as file:
    for index in indices_list:
        file.write(str(index) + '\n')
def recommend(book_name):
    try:
        
        index_position = np.where(pivot_table.index==book_name)[0][0]
        print(index_position)
        similarity_scores_ = similarity[index_position]
        
        similarity_scores_with_indexes = list(enumerate(similarity_scores_))
        reverse_sorted_similarity_scores_with_indexes = sorted(similarity_scores_with_indexes,reverse=True,key=lambda x:x[1])
        top5_books = reverse_sorted_similarity_scores_with_indexes[0:6]
    
        book_name_suggestion = []
        book_image_url = []
        for i in top5_books:
            
    #         print(dump_df.iloc[i[0]]['Book-Title'])
            data_df[data_df['Book-Title']==pivot_table.index[i[0]]][['Book-Title','Book-Author','Publisher','Image-URL-M']]
            book_image_url.append(data_df[data_df['Book-Title']==pivot_table.index[i[0]]]['Image-URL-M'].values)
            book_name_suggestion.append(pivot_table.index[i[0]])
        
        return book_name_suggestion,book_image_url
    except :
        return False,False
    
print(recommend("Angels & Demons"))
