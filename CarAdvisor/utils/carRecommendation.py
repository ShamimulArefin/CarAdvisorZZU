import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

df = pd.read_csv('vehicles2_rec.csv')

def recommended_cars(features):
    made, color_group, type_group, price_range, transmission = features

    # Matching the type with the dataset and reset the index
    data = df.loc[(df['color_group']==color_group) 
                  & (df['type_group']==type_group) 
                  & ((df['price']>=price_range[0]) & (df['price']<=price_range[1]))
                  & (df['transmission'] == transmission)]  
    data.reset_index(level=0, inplace=True)
  
    # Convert the index into series
    indices = pd.Series(data.index, index=data['Made'])
    
    # Converting the car manufacturer country into vectors and used unigram
    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 1), min_df=1, stop_words='english')
    tfidf_matrix = tf.fit_transform(data['Made'])
    
    # Calculating the similarity measures based on Cosine Similarity
    c_similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # Get the index corresponding to original_manufacturer
    idx = indices[made]
    
    # Get the pairwise similarity scores
    similarity_score = list(enumerate(c_similarity[idx]))
    
    # Sort the cars
    similarity_score = sorted(similarity_score, reverse=True)
    
    # Scores of the 6 most similar cars 
    similarity_score = similarity_score[0:6]
    
    # Car indices
    car_indices = [i[0] for i in similarity_score]
   
    # Top 6 car recommendations
    rec = data[['price', 'Made', 'manufacturer', 'model', 'type', 'year', 'Age', 'condition', 'fuel', 'transmission', 'drive', 'paint_color']].iloc[car_indices]
    
    col_names = ['Price $', 'Made', 'Manufacturer', 'Model', 'Car Type', 'Year', 'Age', 'Condition', 'Fuel','Transmission', 'Drive Type', 'Paint Color']

    return [rec, col_names]