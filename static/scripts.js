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

    // Send AJAX request
    $.get("/search_movies", data, function (data) {
        // Get DOM elements
        let recHeader = $("#page-header-recommend")[0];
        let searchHeader = $("#page-header-search")[0];

        // Update header and button
        recHeader.hidden = true;
        searchHeader.hidden = false;

        maxPage = data['maxPages'];
        let numberOfResults = data['numMovies'];

        // Update status
        if (numberOfResults === 0) {
            changeResultsVisibility(false, "<h4>No results found for \"" + searchStr + "\"</h4>");
            return;
        }

        let statusStr = "<p>" + numberOfResults + (numberOfResults === 1 ? " result" : " results") + " found</p>";

        // Update table
        setTableElements(data['data']);
        changeResultsVisibility(true, statusStr);
        showPagination("searchMovie", page, maxPage)
    });
}

function back() {
    fetchRecs(0);
}

function setTableElements(elements) {
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

        appendStr += String.raw`<td><select class="form-control" onchange="this.form.submit();" onfocus="this.selected = 'No rating'">
                <option value="" selected disabled hidden>No rating</option>`;

        for (let rating = 0.5; rating <= 5; rating += 0.5) {
            appendStr += '<option value="' + rating + '"';

            if (movieRating === rating) {
                appendStr += " selected";
            }

            appendStr += '>' + rating + '</option>';
        }

        appendStr += String.raw`</select></td>`;
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