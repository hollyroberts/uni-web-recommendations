import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds

import sqlite3
import re
from collections import OrderedDict
import math

# https://stackoverflow.com/a/5365533
def regexp(expr, item):
    reg = re.compile(expr, re.IGNORECASE)
    return reg.search(item) is not None

# noinspection SqlResolve
class Database:
    DATABASE = "database.db"
    MAX_NUMBER_OF_RESULTS = 30
    LATENT_FACTORS = 50

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
    def search_movies(cls, search_str, user_id, page: int = 0, recommend: bool = True):
        individual_words = list(cls._get_regex_str(word) for word in search_str.split() if word not in cls.COMMON_WORDS)

        with sqlite3.connect(cls.DATABASE) as db:
            # Create regex function
            db.create_function("REGEXP", 2, regexp)

            full_match_results = db.execute("SELECT id FROM movies WHERE title REGEXP ?", [cls._get_regex_str(search_str)])
            movie_ids = set(x[0] for x in full_match_results.fetchall())

            # Assemble our query to search on each word
            if len(individual_words) > 0:
                query = ' '.join(["OR title REGEXP ?"] * len(individual_words))[3:]
                word_match_results = db.execute("SELECT id FROM movies WHERE " + query, individual_words)
                movie_ids.update(x[0] for x in word_match_results.fetchall())

        # Trim to page
        num_movies = len(movie_ids)
        starting_movie = page * cls.MAX_NUMBER_OF_RESULTS
        movie_ids = list(movie_ids)[starting_movie: starting_movie + cls.MAX_NUMBER_OF_RESULTS]

        if recommend:
            movie_reccs = cls.get_all_user_reccs(user_id)

            if not isinstance(movie_reccs, dict):
                movie_ids = list(int(movie_id) for movie_id in movie_reccs if movie_id in movie_ids)

        return cls.get_movies_paginated(movie_ids, user_id, num_movies, starting_movie)

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
    def get_all_user_reccs(cls, user_id):
        with sqlite3.connect(cls.DATABASE) as db:
            # Check if we've rated anything first
            has_ratings = db.execute("SELECT COUNT(*) FROM ratings WHERE user_id = ?", (user_id,)).fetchone()
            if has_ratings[0] == 0:
                return {"noRatings": True}

            # Get movies from SQL query
            movie_data = pd.read_sql("SELECT user_id, movie_id, rating_score FROM ratings", db)

        # Setup data frames
        R_df = movie_data.pivot(index='user_id', columns='movie_id', values='rating_score').fillna(0)
        R = R_df.values

        # Decompose
        user_ratings_mean = np.mean(R, axis=1)
        R_demeaned = R - user_ratings_mean.reshape(-1, 1)
        U, sigma, Vt = svds(R_demeaned, k=cls.LATENT_FACTORS)

        predicted_ratings = np.dot(np.dot(U, np.diag(sigma)), Vt) + user_ratings_mean.reshape(-1, 1)
        preds_df = pd.DataFrame(predicted_ratings, columns=R_df.columns)

        # Sort row descending and retrieve row of results
        ratings_for_user = preds_df.sort_values(by=user_id - 1, ascending=False, axis=1)
        ratings_for_user = ratings_for_user.iloc[user_id - 1:user_id, :]

        return ratings_for_user.columns.values

    @classmethod
    def get_movie_ratings_for_user(cls, user_id: int):
        with sqlite3.connect(cls.DATABASE) as db:
            movies_rated = db.execute("SELECT movie_id FROM ratings WHERE user_id = ? ORDER BY rating_score DESC", [user_id]).fetchall()
        movies_rated = list(x[0] for x in movies_rated)

        return cls.get_movies(movies_rated, user_id)

    @classmethod
    def get_reccs(cls, user_id: int, page: int = 0):
        full_reccs = cls.get_all_user_reccs(user_id)
        if isinstance(full_reccs, dict):
            return full_reccs

        num_movies = len(full_reccs)
        starting_movie = page * cls.MAX_NUMBER_OF_RESULTS
        page_reccs = full_reccs[starting_movie: starting_movie + cls.MAX_NUMBER_OF_RESULTS]

        return cls.get_movies_paginated(page_reccs.tolist(), user_id, num_movies, starting_movie)

    @classmethod
    def get_movies(cls, list_of_ids, user_id):
        with sqlite3.connect(cls.DATABASE) as db:
            results = db.execute("SELECT * FROM movies WHERE id in " + cls._list_to_sql(list_of_ids))
            movie_data = OrderedDict(results.fetchall())
            movie_data = cls._add_extra_info(movie_data, user_id)

        data_to_send = []
        for movie_id in list_of_ids:
            item = [movie_id]
            item.extend(movie_data[movie_id])
            data_to_send.append(item)

        return data_to_send

    @classmethod
    def get_movies_paginated(cls, list_of_ids, user_id, num_movies, starting_movie):
        movie_data = cls.get_movies(list_of_ids, user_id)
        max_pages = math.ceil(num_movies / cls.MAX_NUMBER_OF_RESULTS) - 1

        return {"maxPages": max_pages,
                "totMovies": num_movies,
                "startingMovie": starting_movie,
                "data": movie_data}

    @classmethod
    def number_of_users(cls):
        with sqlite3.connect(cls.DATABASE) as db:
            return db.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    @classmethod
    def update_rating(cls, user_id: int, movie_id: int, rating: float):
        with sqlite3.connect(cls.DATABASE) as db:
            exists = db.execute("SELECT COUNT(*) FROM ratings WHERE user_id = ? AND movie_id = ?", (user_id, movie_id)).fetchone()[0] == 1

            if exists:
                db.execute("UPDATE ratings SET rating_score = ? WHERE user_id = ? AND movie_id = ?", (rating, user_id, movie_id))
            else:
                db.execute("INSERT INTO ratings (user_id, movie_id, rating_score) VALUES (?, ?, ?)", (user_id, movie_id, rating))

    # Private functions
    @classmethod
    def _get_regex_str(cls, string: str):
        return f"(^|\W){re.escape(string)}($|\W)"

    @classmethod
    def _add_extra_info(cls, movie_data: OrderedDict, user_id: int):
        with sqlite3.connect(cls.DATABASE) as db:
            for movie_id in movie_data.keys():
                sql_query = "SELECT genres.genre FROM movies INNER JOIN movie_genres ON movies.id = movie_genres.movie_id AND movies.id = ? INNER JOIN genres ON genres.id = movie_genres.genre_id"
                genres = list(genre[0] for genre in db.execute(sql_query, (movie_id,)).fetchall())

                rating = db.execute("SELECT rating_score FROM ratings WHERE user_id = ? AND movie_id = ?", (user_id, movie_id)).fetchone()

                # Convert dict from movie id --> title
                # into movie id --> [title, [genre1, genre2, ...], rating]
                movie_data[movie_id] = [movie_data[movie_id], genres, rating[0] if rating is not None else None]
        
        return movie_data

    @classmethod
    def _list_to_sql(cls, list_of_ids):
        # Ugly hack to get data how we want
        return "(" + ", ".join(map(str, list_of_ids)) + ")"