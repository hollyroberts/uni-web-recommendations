let maxPage = 0;
let resultsTypeIsSearch = false;
let updatePage = 0;

let translations = {};

function fetchTranslations(next_func) {
    $.get("/get_translations", {}, function(data) {
        translations = data;
        next_func()
    });
}

function searchMovie(page = 0) {
    displayLoadingMessage();

    // Form elements
    let searchStr = $("#search-movie-input").val();
    if (searchStr.length === 0) {
        return;
    }
    let recommend = $("#recommend-search-checkbox")[0].checked;
    let include_rated_movies = $("#remove-rated-checkbox")[0].checked;

    let data = {
        title: searchStr,
        recommend: recommend,
        include_rated_movies: include_rated_movies,
        page: page
    };

    showSearchHeader();

    // Send AJAX request
    $.get("/search_movies", data, function (response) {
        let server_translations = response['translations'];
        let data = response['results'];

        maxPage = data['maxPages'];
        let totResults = data['totMovies'];
        let startingMovie = data['startingMovie'];

        // Update status
        if (totResults === 0) {
            changeResultsVisibility(false, "<h4>" + server_translations['no_results_found'] + "</h4>");
            return;
        }

        let statusStr = "<p>" + server_translations['results_found'] + "</p>";

        // Update table
        setTableElements(data['data']);
        changeResultsVisibility(true, statusStr);
        showPagination("searchMovie", page, maxPage);

        // Update settings change
        resultsTypeIsSearch = true;
        updatePage = page;
    });
}

function back() {
    fetchRecs(0);
}

function setTableElements(elements, deleteButton = false) {
    let table = $("#results-table");

    // Clear existing table data
    table.find("tr:gt(0)").remove();

    for (let movieData of elements) {
        // Retrieve data
        let movieId = movieData[0];
        let movieTitle = movieData[1];
        let movieGenres = movieData[2];
        let movieRating = movieData[3];

        // Movie title
        let appendStr = "<tr id=table-entry-" + movieId + ">";
        appendStr += "<td>" + movieTitle + "</td>";

        // Movie genres
        if (movieGenres.length === 0) {
            appendStr += "<td>" + translations['no_genres'] + "</td>";
        } else {
            appendStr += "<td>" + movieGenres.join(", ") + "</td>";
        }

        // Rating
        appendStr += `<td><select class="form-control" onchange="updateRating(${movieId}, '${movieTitle}', this.value);" onfocus="this.selected = '${translations['no_rating']}'">`;
        appendStr += `<option value="" selected disabled hidden>${translations['no_rating']}</option>`;

        for (let rating = 0.5; rating <= 5; rating += 0.5) {
            appendStr += '<option value="' + rating + '"';

            if (movieRating === rating) {
                appendStr += " selected";
            }

            appendStr += '>' + rating + '</option>';
        }
        appendStr += String.raw`</select></td>`;

        // Delete button
        if (deleteButton) {
            appendStr += `<td><button type="button" class="btn btn-danger" onclick="deleteRating(${movieId}, '${movieTitle}');">${translations['delete']}</button></td>`
        }

        appendStr += "</tr>";
        table.append(appendStr);
    }
}

function changeResultsVisibility(showTable, status) {
    $("#results-table")[0].hidden = !showTable;

    let statusDOM = $("#results-status")[0];
    if (status === false || status === undefined) {
        statusDOM.hidden = true;
    } else {
        statusDOM.hidden = false;
        statusDOM.innerHTML = status
    }
}

function fetchRecs(page = 0) {
    displayLoadingMessage();
    showSearchHeader(false);

    let include_rated_movies = $("#remove-rated-checkbox")[0].checked;
    let data = {
        page: page,
        include_rated_movies: include_rated_movies
    };

    $.get("/recommendations", data, function (data) {
        // Check response metadata
        if (data.hasOwnProperty("noRatings")) {
            changeResultsVisibility(false, "<h4>" + translations['no_ratings_so_no_reccs'] + "</h4>");
        }

        maxPage = data['maxPages'];

        // Update UI
        setTableElements(data['data']);
        changeResultsVisibility(true, false);
        showPagination("fetchRecs", page, maxPage);

        // Update settings change
        resultsTypeIsSearch = false;
        updatePage = page;
    });
}

function fetchRatings() {
    $.get("/ratings", undefined, function(data) {
        console.log(data);

        if (data.length === 0) {
            changeResultsVisibility(false, translations['have_not_rated']);
        } else {
            changeResultsVisibility(true, false);
            setTableElements(data, true);
        }
    });
}

function updateRating(movieID, movieTitle, rating) {
    let postData = {
        movie_id: movieID,
        rating: rating
    };

    // Send AJAX request
    // noinspection JSUnusedLocalSymbols
    $.post("/update_recommendation", postData, function (_, status) {
        if (status !== "success") {
            alert(translations['error_rating']);
            return;
        }

        let alertContainer = $("#success-alert");
        $("#alert-text")[0].innerHTML = translations['rating_updated'].replace("*", movieTitle).replace("&", rating);

        alertContainer.fadeTo(2500, 500).slideUp(500, function () {
            alertContainer.slideUp(500);
        });
    });
}

function deleteRating(movieID, movieTitle) {
    $.post("/delete_rating", {movie_id: movieID}, function (_, status) {
        if (status !== "success") {
            alert(translations['error_deleting']);
            return;
        }

        let tr = $("#table-entry-" + movieID);
        tr.fadeOut(300, function () {
            tr.remove();

            if ($("#results-table")[0].rows.length <= 1) {
                changeResultsVisibility(false, translations['have_not_rated']);
            }
        });

        let alertContainer = $("#success-alert");
        $("#alert-text")[0].innerHTML = translations['rating_deleted'].replace("*", movieTitle);

        alertContainer.fadeTo(2500, 500).slideUp(500, function () {
            alertContainer.slideUp(500);
        });
    })
}

function displayLoadingMessage() {
    disablePagination();
    changeResultsVisibility(false, "<p>" + translations['loading_movies'] + "</p>");
}

function disablePagination() {
    $("#pagination")[0].innerHTML = "";
}

function showPagination(updateFunction, curPage, maxPage) {
    let htmlStr = "";

    // Back
    if (curPage === 0) {
        htmlStr += `<li class="disabled"><a><span class="glyphicon glyphicon-chevron-left"></span></a></li>`;
    } else {
        htmlStr += `<li><a onclick="${updateFunction}(0)" role="button"><span class="glyphicon glyphicon-chevron-left"></span></a></li>`;
    }

    // Current page
    htmlStr += `<li><a>${curPage + 1}</a></li>`;

    // Next
    if (curPage < maxPage) {
        htmlStr += `<li><a onclick="${updateFunction}(${curPage + 1})" role="button"><span class="glyphicon glyphicon-chevron-right"></span></a></li>`;
    } else {
        htmlStr += `<li class="disabled"><a><span class="glyphicon glyphicon-chevron-right"></span></a></li>`;
    }


    $("#pagination")[0].innerHTML = htmlStr;
}

function updateSearchSettings(recommend) {
    if (recommend && !resultsTypeIsSearch) {
        return;
    }

    if (resultsTypeIsSearch) {
        searchMovie(updatePage);
    } else {
        fetchRecs(updatePage);
    }
}

function showSearchHeader(bool = true) {
    // Get DOM elements
    let recHeader = $("#page-header-recommend")[0];
    let searchHeader = $("#page-header-search")[0];

    // Update header and button
    recHeader.hidden = bool;
    searchHeader.hidden = !bool;
}