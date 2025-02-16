import os
import requests
import pickle
import pandas as pd
import streamlit as st

# Function to merge split files into a single file
def merge_files(output_file, input_files):
    """
    Merge split files into one complete file.
    :param output_file: The name of the final merged file.
    :param input_files: List of split files to merge.
    """
    try:
        with open(output_file, 'wb') as outfile:
            for part_file in input_files:
                if os.path.exists(part_file):
                    with open(part_file, 'rb') as infile:
                        outfile.write(infile.read())
                    st.write(f"Merged {part_file}")
                else:
                    st.error(f"File not found: {part_file}")
        st.success("Merging complete!")
    except Exception as e:
        st.error(f"Error during file merging: {e}")

# List of split files (ensure these paths are correct relative to your app)
split_files = [
    f"similarity_chunk_2.zip.{str(i).zfill(3)}" for i in range(1, 21)
]

# Merge files if similarity.pkl doesn't already exist
if not os.path.exists("similarity.pkl"):
    st.info("Merging split files into similarity.pkl...")
    merge_files("similarity.pkl", split_files)

# Load the similarity.pkl file using pickle (joblib removed)
similarity = None
if os.path.exists("similarity.pkl"):
    try:
        with open("similarity.pkl", "rb") as f:
            similarity = pickle.load(f)
        st.info("similarity.pkl loaded successfully using pickle!")
    except Exception as e:
        st.error(f"Error loading similarity.pkl with pickle: {e}")
else:
    st.error("similarity.pkl file not found. Please upload or merge the split files.")

# Function to fetch movie poster
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US')
        data = response.json()
        return f"https://image.tmdb.org/t/p/w500/{data.get('poster_path', 'No+Image')}"
    except Exception:
        return "https://via.placeholder.com/500x750?text=No+Image"

# Function to recommend movies based on similarity
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        recommended_movies = [movies.iloc[i[0]].title for i in movies_list]
        recommended_movies_posters = [fetch_poster(movies.iloc[i[0]].id) for i in movies_list]
        return recommended_movies, recommended_movies_posters
    except Exception as e:
        st.error(f"Error in recommendation: {e}")
        return [], []

# Load the movies data
try:
    with open('movies_dict.pkl', 'rb') as f:
        movies_dict = pickle.load(f)
    movies = pd.DataFrame(movies_dict)
    st.info("movies_dict.pkl loaded successfully!")
except FileNotFoundError:
    st.error("movies_dict.pkl file not found. Please upload the movies data.")
    movies = pd.DataFrame()

# Streamlit app code
st.title('Movie Recommender System')

if not movies.empty:
    selected_movie_name = st.selectbox("Choose a movie:", movies['title'].values)
    if st.button('Recommend'):
        if similarity is not None:
            names, posters = recommend(selected_movie_name)
            cols = st.columns(len(names))
            for idx, col in enumerate(cols):
                col.text(names[idx])
                col.image(posters[idx])
        else:
            st.error("Similarity data is not available. Please check the files.")
else:
    st.error("Movies data is empty. Please upload valid movies data.")