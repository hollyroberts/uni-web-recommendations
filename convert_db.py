# Standalone program to setup SQLite db
# Converts CSV files into tables

import sqlite3
import os

os.remove("database.db")
db = sqlite3.connect("database.db")

# Create tables
db.execute("CREATE TABLE users (id Int, name Varchar)")
db.execute("CREATE TABLE movies (id Int, title Varchar)")
db.execute("CREATE TABLE genres (id Int, genre Varchar)")

db.execute("CREATE TABLE ratings (user_id Int, movie_id Int, rating_score Int)")
db.execute("CREATE TABLE movie_genres (movie_id Int, genre_id Int)")

db.commit()
db.close()
