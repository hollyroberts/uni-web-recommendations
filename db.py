import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds

import sqlite3
import re
from collections import OrderedDict

# https://stackoverflow.com/a/5365533
def regexp(expr, item):
    reg = re.compile(expr, re.IGNORECASE)
    return reg.search(item) is not None

class Database:
    DATABASE = "database.db"
    MAX_NUMBER_OF_RESULTS = 50

    COMMON_WORDS = ["the",
                    "of",
                    "and",
                    "a",
                    "to",
                    "in",
                    "is",
                    "you",
                    "that",
                    "it",
                    "he",
                    "was",
                    "for",
                    "on",
                    "are",
                    "as",
                    "with",
                    "his",
                    "they",
                    "I",
                    "at",
                    "be",
                    "this",
                    "have",
                    "from",
                    "or",
                    "one",
                    "had",
                    "by",
                    "word",
                    "but",
                    "not",
                    "what"
                    "all",
                    "were",
                    "we",
                    "when",
                    "your",
                    "can"]

    """
    Returns the id of the user inserted; assumes username is valid
    """
    @classmethod
    def add_user(cls, username):
        with sqlite3.connect(cls.DATABASE) as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO users (name, from_mvl) values (?, ?)", (username, False)).fetchone()
            db.commit()

            return {
                "id": cursor.lastrowid,
                "name": username
            }

    @classmethod
    def search_movies(cls, search_str):
        individual_words = list(cls._get_regex_str(word) for word in search_str.split() if word not in cls.COMMON_WORDS)

        with sqlite3.connect(cls.DATABASE) as db:
            # Create regex function
            db.create_function("REGEXP", 2, regexp)

            full_match_results = db.execute("SELECT * FROM movies WHERE title REGEXP ?", [cls._get_regex_str(search_str)])
            results = OrderedDict(full_match_results.fetchall())

            # Assemble our query to search on each word
            if len(individual_words) > 0:
                query = ' '.join(["OR title REGEXP ?"] * len(individual_words))[3:]
                word_match_results = db.execute("SELECT * FROM movies WHERE " + query, individual_words)
                results.update(word_match_results.fetchall())

            for movie_id in results.keys():
                sql_query = "SELECT genres.genre FROM movies INNER JOIN movie_genres ON movies.id = movie_genres.movie_id AND movies.id = ? INNER JOIN genres ON genres.id = movie_genres.genre_id"
                genres = list(genre[0] for genre in db.execute(sql_query, (movie_id,)).fetchall())

                # Convert dict from movie id --> title
                # into movie id --> [title, genres]
                results[movie_id] = [results[movie_id], genres]

        return list(results.values()[:cls.MAX_NUMBER_OF_RESULTS])

    @classmethod
    def get_users(cls):
        with sqlite3.connect(cls.DATABASE) as db:
            users = db.execute("SELECT * FROM users WHERE NOT from_mvl").fetchall()
            return users

    @classmethod
    def get_user(cls, user_id):
        with sqlite3.connect(cls.DATABASE) as db:
            result = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

            return {
                "id": int(user_id),
                "name": result[1]
            }

    # noinspection PyPep8Naming
    @classmethod
    def get_reccs(cls, user_id: int, page: int = 0):
        with sqlite3.connect("database.db") as db:
            # Get movies from SQL query
            movie_data = pd.read_sql("SELECT user_id, movie_id, rating_score FROM ratings", db)

        # Setup data frames
        ratings_mean_count = pd.DataFrame(movie_data.groupby('movie_id')['rating_score'].mean())
        ratings_mean_count['rating_counts'] = pd.DataFrame(movie_data.groupby('movie_id')['rating_score'].count())

        R_df = movie_data.pivot(index='user_id', columns='movie_id', values='rating_score').fillna(0)
        R = R_df.values

        # Decompose
        user_ratings_mean = np.mean(R, axis=1)
        R_demeaned = R - user_ratings_mean.reshape(-1, 1)
        U, sigma, Vt = svds(R_demeaned, k=20)

        predicted_ratings = np.dot(np.dot(U, np.diag(sigma)), Vt) + user_ratings_mean.reshape(-1, 1)
        preds_df = pd.DataFrame(predicted_ratings, columns=R_df.columns)

        # Sort row descending and retrieve first X results
        ratings_for_user = preds_df.sort_values(by=user_id, ascending=False, axis=1)
        ratings_for_user = ratings_for_user.iloc[user_id:user_id + 1, :cls.MAX_NUMBER_OF_RESULTS]
        print(ratings_for_user)

    # Private functions
    @classmethod
    def _get_regex_str(cls, string: str):
        return f"(^|\W){re.escape(string)}($|\W)"