Personal Favourite Movies Website with Recommendation algorithm

https://kumaran-top-10-movie-site.herokuapp.com/

Using this website, you can add your favourite movies for you and your friends to view, along with a personal rating and review. 
You can add, update, and delete movies, as the data is stored and updated on a linked PostgreSQL database.
All the information on the movies (description, titles, pictures) are retrieved using the TMDB API. 

Furthermore for every movie, you'll receive 5 movie recommendations based on users who also liked this movie and genres. This is done using Pandas, NumPy
and sklearn where cosine similarity is used to determine similarity between movies. All this data is retrieved from a Kaggle dataset.

Topics used here
- Python
- HTML/CSS
- Pandas, Numpy and sklearn
- SQL database configuration
- APIs
- Flask and Boostrap
