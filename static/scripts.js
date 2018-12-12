let maxPage = 0;

function searchMovie(page = 0) {
    displayLoadingMessage();

    // Form elements
    let searchStr = $("#search-movie-input").val();
    if (searchStr.length === 0) {
        return;
    }
    let recommend = $("#recommend-search-checkbox")[0].checked;

    let data = {
        title: searchStr,
        recommend: recommend,
        page: page
    };

    showSearchHeader();

    // Send AJAX request
    $.get("/search_movies", data, function (data) {
        maxPage = data['maxPages'];
        let totResults = data['totMovies'];
        let startingMovie = data['startingMovie'];

        // Update status
        if (totResults === 0) {
            changeResultsVisibility(false, "<h4>No results found for \"" + searchStr + "\"</h4>");
            return;
        }

        let statusStr = `<p>Showing movies ${startingMovie + 1}-${startingMovie + data['data'].length} out of ${totResults}` + (totResults === 1 ? " result" : " results") + " found</p>";

        // Update table
        setTableElements(data['data']);
        changeResultsVisibility(true, statusStr);
        showPagination("searchMovie", page, maxPage)
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
        let appendStr = "<tr>";
        appendStr += "<td>" + movieTitle + "</td>";

        // Movie genres
        if (movieGenres.length === 0) {
            appendStr += "<td>No genres</td>";
        } else {
            appendStr += "<td>" + movieGenres.join(", ") + "</td>";
        }

        // Rating
        appendStr += `<td><select class="form-control" onchange="updateRating(${movieId}, '${movieTitle}', this.value);" onfocus="this.selected = 'No rating'">`;
        appendStr += `<option value="" selected disabled hidden>No rating</option>`;

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
            appendStr += `<td><button type="button" class="btn btn-danger">Delete</button></td>`
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

    $.get("/recommendations", {page: page}, function (data) {
        // Check response metadata
        if (data.hasOwnProperty("noRatings")) {
            changeResultsVisibility(false, "<h4>You haven't rated any movies yet, so no recommendations can be generated</h4>");
        }

        maxPage = data['maxPages'];

        // Update UI
        setTableElements(data['data']);
        changeResultsVisibility(true, false);
        showPagination("fetchRecs", page, maxPage);
    });
}

function fetchRatings() {
    $.get("/ratings", undefined, function(data) {
        console.log(data);
        changeResultsVisibility(true, false);
        setTableElements(data, true);
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
            alert("Error updating rating - this should never happen");
            return;
        }

        let alertContainer = $("#success-alert");
        $("#alert-text")[0].innerHTML = `Rating for "${movieTitle}" updated to ${rating}/5`;

        alertContainer.fadeTo(2500, 500).slideUp(500, function () {
            alertContainer.slideUp(500);
        });
    });
}

function displayLoadingMessage() {
    disablePagination();
    changeResultsVisibility(false, "<p>Loading movies...</p>");
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

function showSearchHeader(bool = true) {
    // Get DOM elements
    let recHeader = $("#page-header-recommend")[0];
    let searchHeader = $("#page-header-search")[0];

    // Update header and button
    recHeader.hidden = bool;
    searchHeader.hidden = !bool;
}