# Standalone program to setup SQLite db
# Converts CSV files INTEGERo tables

import sqlite3
import os
import csv

MVLENS_FOLDER = "data"

os.remove("database.db")
db = sqlite3.connect("database.db")

# Create tables
db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY , name Varchar)")
db.execute("CREATE TABLE movies (id INTEGER PRIMARY KEY , title Varchar)")
db.execute("CREATE TABLE genres (id INTEGER PRIMARY KEY , genre Varchar)")

db.execute("CREATE TABLE ratings (user_id INTEGER, movie_id INTEGER, rating_score INTEGER)")
db.execute("CREATE TABLE movie_genres (movie_id INTEGER, genre_id INTEGER)")

# Go through movies.csv
with open(os.path.join(MVLENS_FOLDER, "movies.csv"), 'r', encoding="UTF-8") as file:
    genre_set = set()
    to_movie_db = []

    data = csv.DictReader(file)

    for row in data:
        to_movie_db.append((row['movieId'], row['title']))
        genre_set.update(row['genres'].split('|'))

    genre_set.remove("(no genres listed)")

# Post process genres
genre_tuples = list((i,) for i in sorted(genre_set))
genre_map = {value[0]: index for (index, value) in enumerate(genre_tuples)}

# Add data to movies and genres
db.executemany("INSERT INTO movies (id, title) VALUES (?, ?)", to_movie_db)
db.executemany("INSERT INTO genres (genre) VALUES (?)", genre_tuples)
print(db.execute("SELECT * FROM genres").fetchall())

db.commit()
db.close()
