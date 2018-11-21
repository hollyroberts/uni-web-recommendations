# Standalone program to setup SQLite db
# Converts CSV files into tables
# This takes a fair chunk of memory (~5-6GB), and takes about a minute or so to run

import sqlite3
import os
import csv
import sys

MVLENS_FOLDER = "data"

if os.path.exists("database.db"):
    os.remove("database.db")
db = sqlite3.connect("database.db")

# Create tables
db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY , name VARCHAR, from_mvl BOOLEAN)")
db.execute("CREATE TABLE movies (id INTEGER PRIMARY KEY , title VARCHAR)")
db.execute("CREATE TABLE genres (id INTEGER PRIMARY KEY , genre VARCHAR)")

db.execute("CREATE TABLE movie_genres (movie_id INTEGER, genre_id INTEGER)")
db.execute("CREATE TABLE ratings (user_id INTEGER, movie_id INTEGER, rating_score FLOAT, UNIQUE (user_id, movie_id) ON CONFLICT REPLACE)")

# Go through movies.csv
with open(os.path.join(MVLENS_FOLDER, "movies.csv"), 'r', encoding="UTF-8") as file:
    genre_dict = {}
    number_of_genres = 0

    movie_data = []
    movie_genre_data = []

    data = csv.DictReader(file)

    for row in data:
        movie_data.append((row['movieId'], row['title']))

        genres_in_movie = row['genres'].split('|')
        if "(no genres listed)" in genres_in_movie:
            genres_in_movie.remove("(no genres listed)")

        for genre in genres_in_movie:
            # Add to dictionary if genre doesn't exist
            if genre not in genre_dict:
                number_of_genres += 1
                genre_dict[genre] = number_of_genres

            # Add to obj
            movie_genre_data.append((row['movieId'], genre_dict[genre]))

# Invert genres
genre_data = list((index, genre) for (genre, index) in genre_dict.items())

# Add data to movies, genres, and movie genres
db.executemany("INSERT INTO movies (id, title) VALUES (?, ?)", movie_data)
db.executemany("INSERT INTO genres (id, genre) VALUES (?, ?)", genre_data)
db.executemany("INSERT INTO movie_genres (movie_id, genre_id) VALUES (?, ?)", movie_genre_data)

# Go through ratings.csv
with open(os.path.join(MVLENS_FOLDER, "ratings.csv"), 'r', encoding="UTF-8") as file:
    users = [1]
    max_user = 0

    rating_data = []

    data = csv.DictReader(file)

    for row in data:
        rating_data.append((row['userId'], row['movieId'], row['rating']))

        max_user = max(max_user, int(row['userId']))
        if max_user > users[-1]:
            users.append(max_user)

# Create dummy users and ensure users increase constantly
user_data = []

for index, user_id in enumerate(users):
    if index + 1 != user_id:
        print(f"Error on ensuring user continuity: {user_id}")
        sys.exit(-1)

    user_data.append((user_id, user_id, True))
print(f"Number of users: {max_user}")

# Fill in users and ratings
db.executemany("INSERT INTO users (id, name, from_mvl) VALUES (?, ?, ?)", user_data)
db.executemany("INSERT INTO ratings (user_id, movie_id, rating_score) VALUES (?, ?, ?)", rating_data)

db.commit()
db.close()

