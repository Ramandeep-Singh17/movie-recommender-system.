import pandas as pd
import streamlit as st
import pickle
import requests
import os

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
                with open(part_file, 'rb') as infile:
                    outfile.write(infile.read())
        st.success("Merging complete!")
    except Exception as e:
        st.error(f"Error during file merging: {e}")

# List of 20 split files
split_files = [
    "similarity_chunk_2.zip.001", "similarity_chunk_2.zip.002", "similarity_chunk_2.zip.003", "similarity_chunk_2.zip.004",
    "similarity_chunk_2.zip.005", "similarity_chunk_2.zip.006", "similarity_chunk_2.zip.007", "similarity_chunk_2.zip.008",
    "similarity_chunk_2.zip.009", "similarity_chunk_2.zip.010", "similarity_chunk_2.zip.011", "similarity_chunk_2.zip.012",
    "similarity_chunk_2.zip.013", "similarity_chunk_2.zip.014", "similarity_chunk_2.zip.015", "similarity_chunk_2.zip.016",
    "similarity_chunk_2.zip.017", "similarity_chunk_2.zip.018", "similarity_chunk_2.zip.019", "similarity_chunk_2.zip.020"
]

# Merge files if similarity.pkl doesn't already exist
if not os.path.exists("similarity.pkl"):
    st.info("Merging split files into similarity.pkl...")
    merge_files("similarity.pkl", split_files)

# Load the similarity.pkl file
similarity = None
if os.path.exists("similarity.pkl"):
    try:
        with open('similarity.pkl', 'rb') as f:
            similarity = pickle.load(f)
        st.info("Similarity.pkl loaded successfully!")
    except Exception as e:
        st.error(f"Error loading similarity.pkl: {e}")
else:
    st.error("similarity.pkl file not found. Please upload or merge the split files.")

# Function to fetch movie poster
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US')
        data = response.json()

        # Check if poster_path exists, otherwise return a placeholder image
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    except Exception as e:
        return "https://via.placeholder.com/500x750?text=No+Image"  # In case of any error, return a placeholder image

# Function to recommend movies based on similarity
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters

# Load the movies data
try:
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
except FileNotFoundError:
    st.error("movies_dict.pkl file not found. Please upload the movies data.")
    movies = pd.DataFrame()

# Streamlit app code
st.title('Movie Recommender System')

selected_movie_name = st.selectbox("Choose a movie:", movies['title'].values)

if st.button('Recommend'):
    if similarity is not None and not movies.empty:
        names, posters = recommend(selected_movie_name)

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.text(names[0])
            st.image(posters[0])

        with col2:
            st.text(names[1])
            st.image(posters[1])

        with col3:
            st.text(names[2])
            st.image(posters[2])

        with col4:
            st.text(names[3])
            st.image(posters[3])

        with col5:
            st.text(names[4])
            st.image(posters[4])
    else:
        st.error("Similarity data or movie data not available. Please check the files.")
