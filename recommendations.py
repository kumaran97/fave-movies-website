import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

def clean_data(user_movie):

    # Initialize csv data to dataframes
    rating_data = pd.read_csv('ratings.csv')
    movie_database = pd.read_csv('movies.csv')

    # Clean data
    rating_data = rating_data.drop(columns=['timestamp'])
    ratings_df = pd.pivot(data=rating_data, index='userId', columns='movieId', values='rating')

    no_movies_voted = rating_data.groupby('userId')['rating'].agg('count')
    ratings_df = ratings_df.reindex(no_movies_voted[no_movies_voted >= 50].index)

    ratings_df = ratings_df.fillna(0)

    movie_database['just_title'] = movie_database['title'].str[:-7]

    # Use user movie to further manipulate data
    if user_movie[:4] == "The ":
        user_movie = user_movie[4:]
        user_movie = f"{user_movie}, The"
    user_movie_id = movie_database[movie_database['just_title'].str.lower() == user_movie.lower()].movieId
    try:
        user_movie_id = user_movie_id.item()
        user_movie_genre = movie_database[movie_database['movieId'] == user_movie_id].genres.item()

        # Manipulate dataframes based on the user movie
        user_movie_df = ratings_df.loc[ratings_df[user_movie_id] >= 4]
        user_movie_df.drop(columns=[user_movie_id], inplace=True)
        user_movie_df = user_movie_df.replace(0, np.NaN)

        avg_user_movie_df = pd.DataFrame(user_movie_df.mean())
        avg_user_movie_df.reset_index(inplace=True)

        recommend_df = pd.concat([avg_user_movie_df, movie_database], axis=1)
        recommend_df.dropna(inplace=True)
        recommend_df = recommend_df[recommend_df['just_title'] != user_movie]
        recommend_df.iloc[:, ~recommend_df.columns.duplicated()]

        return recommend_df, user_movie_genre

    except ValueError:

        return None


def find_recommendations(df, genre):

    # Using sklearn for cosine similarity between user movie genre and rest of movies
    tfidf = TfidfVectorizer()
    vectorizer = tfidf.fit_transform(df['genres'])
    vectorizer_user = tfidf.transform([genre])

    cos_sim = cosine_similarity(vectorizer, vectorizer_user)

    df['genre_similarity'] = cos_sim
    df.rename(columns={0: "score"}, inplace=True)
    df.sort_values(by=['genre_similarity', 'score'], ascending=[False, False], inplace=True)
    df = df[:5]
    reco_list = df['just_title']

    return reco_list






