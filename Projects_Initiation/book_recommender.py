import pickle
import numpy as np

dashboard_df = pickle.load(open('./pickle_files/dashboard.pkl','rb'))
## This below dashboard_df needs to be the landing page when user enters the website.
# -> print(dashboard_df[['Book-Title','Image-URL-M','Book-Author','Publisher']])


data_df = pickle.load(open('./pickle_files/data_df.pkl','rb'))
# -> print(data_df)

pivot_table = pickle.load(open('./pickle_files/pivot_table.pkl','rb'))
# -> print(pivot_table)


similarity = pickle.load(open('./pickle_files/similarity.pkl','rb'))
# -> print(similarity.shape)

##Then users click on recommends button above . then another page open in that page where user
## inputs book name and we recommend the user.
def dashboards_data():
    return dashboard_df[['Book-Title','Image-URL-M','Book-Author','Publisher']]



def recommend(book_name):
    try:
        index_position = np.where(pivot_table.index==book_name)[0][0]
    
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





if __name__ == '__main__':
    books,book_image_url = recommend(' The Two Towers (The Lord of the Rings, Part 2)')
    