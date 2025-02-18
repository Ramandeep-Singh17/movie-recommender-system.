
import os
import requests
import joblib
import pandas as pd
import streamlit as st

# Function to merge split files into a single file
def merge_files(output_file, input_files):
    """Merge split files into one complete file."""
    try:
        with open(output_file, 'wb') as outfile:
            for part_file in input_files:
                if os.path.exists(part_file):
                    with open(part_file, 'rb') as infile:
                        outfile.write(infile.read())
                    st.write(f"Merged: {part_file}")
                else:
                    st.error(f"File not found: {part_file}")
        st.success("Merging complete!")
    except Exception as e:
        st.error(f"Error during file merging: {e}")

# List of split files
split_files = [f"similarity_chunk_2.zip.{str(i).zfill(3)}" for i in range(1, 21)]

# Merge files if similarity.pkl doesn't already exist
if not os.path.exists("similarity.pkl"):
    st.info("Merging split files into similarity.pkl...")
    merge_files("similarity.pkl", split_files)

# Load the similarity.pkl file using joblib
similarity = None
if os.path.exists("similarity.pkl"):
    try:
        similarity = joblib.load("similarity.pkl")
        st.info("similarity.pkl loaded successfully!")
    except Exception as e:
        st.error(f"Error loading similarity.pkl: {e}")
else:
    st.error("similarity.pkl file not found. Please upload or merge the split files.")

# Function to fetch movie poster
def fetch_poster(movie_id):
    """Fetches the movie poster using TMDB API."""
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US')
        data = response.json()
        poster_path = data.get('poster_path')
        return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Image"
    except Exception:
        return "https://via.placeholder.com/500x750?text=No+Image"

# Function to recommend movies based on similarity
def recommend(movie):
    """Recommends movies based on the given movie title."""
    try:
        if similarity is None:
            st.error("Similarity data is missing!")
            return [], []

        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(enumerate(distances), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_movies_posters = []

        for i in movies_list:
            movie_id = movies.iloc[i[0]].id
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_posters.append(fetch_poster(movie_id))

        return recommended_movies, recommended_movies_posters
    except Exception as e:
        st.error(f"Error in recommendation: {e}")
        return [], []

# Load the movies data
movies = pd.DataFrame()
try:
    with open('movies_dict.pkl', 'rb') as f:
        movies_dict = joblib.load(f)
    movies = pd.DataFrame(movies_dict)
    st.info("movies_dict.pkl loaded successfully!")
except FileNotFoundError:
    st.error("movies_dict.pkl file not found. Please upload the movies data.")

# Streamlit app UI
st.title('🎬 Movie Recommender System')

if not movies.empty:
    selected_movie_name = st.selectbox("Choose a movie:", movies['title'].values)

    if st.button('Recommend'):
        names, posters = recommend(selected_movie_name)

        if names:
            cols = st.columns(len(names))
            for idx, col in enumerate(cols):
                col.text(names[idx])
                col.image(posters[idx])
        else:
            st.error("No recommendations found!")
else:
    st.error("Movies data is empty. Please upload valid movies data.")