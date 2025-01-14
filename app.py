import pandas as pd
import streamlit as st
import pickle
import requests


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
    # Get movie index
    movie_index = movies[movies['title'] == movie].index[0]

    # Get movie similarity scores
    distances = similarity[movie_index]

    # Get top 5 recommended movies
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []  # List to store recommended movie titles
    recommended_movies_posters = []  # List to store recommended movie posters

    # Loop to get movie names and posters
    for i in movies_list:
        movie_id = movies.iloc[i[0]].id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters


# Load the movies data and similarity matrix
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit UI setup
st.title('Movie Recommender System')

# Dropdown menu to select a movie
selected_movie_name = st.selectbox("How would you like to be contacted?", movies['title'].values)

# When the button is clicked, recommend movies
if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    # Display the recommendations in columns
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

        import os
        import zipfile
        import requests


        def download_and_extract_files():
            # List of URLs to your zip parts hosted on GitHub
            zip_parts = [
                "https://github.com/your_username/your_repo/raw/main/part1.zip",
                "https://github.com/your_username/your_repo/raw/main/part2.zip",
                # Add all parts here
            ]

            # Create a directory to store the downloaded files
            os.makedirs("data", exist_ok=True)

            # Download each part
            for i, url in enumerate(zip_parts):
                print(f"Downloading {url}...")
                response = requests.get(url)
                with open(f"data/part{i + 1}.zip", "wb") as f:
                    f.write(response.content)

            # Combine the zip files into the original .pkl file
            with open("data/similarity.pkl", "wb") as outfile:
                for i in range(len(zip_parts)):
                    with open(f"data/part{i + 1}.zip", "rb") as infile:
                        outfile.write(infile.read())

            # Extract the similarity.pkl if needed
            with zipfile.ZipFile("data/similarity.pkl", "r") as zip_ref:
                zip_ref.extractall("data")


        # Call the function to download and extract the files
        if not os.path.exists("data/similarity.pkl"):
            download_and_extract_files()
