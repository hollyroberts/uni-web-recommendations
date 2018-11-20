function searchMovie() {
    // Form elements
    let searchStr = $("#search-movie-input").val();
    if (searchStr.length === 0) {
        return;
    }
    let recommend = $("#recommend-search-checkbox")[0].checked;

    let data = {
        title: searchStr,
        recommend: recommend
    };

    // Send AJAX request
    $.get("/search_movies", data, function (data) {
        console.log(data);

        // Get DOM elements
        let recHeader = $("#page-header-recommend")[0];
        let searchHeader = $("#page-header-search")[0];

        // Update header and button
        recHeader.hidden = true;
        searchHeader.hidden = false;

        // Update status
        if (data.length === 0) {
            setStatus("<h4>No results found for \"" + searchStr + "\"</h4>");
            changeResultsVisibility(false, true);
            return;
        }
        setStatus("<p>" + data.length + (data.length === 1 ? " result" : " results") + " found</p>");

        // Update table
        setTableElements(data);
        changeResultsVisibility(true, true);
    });
}

function back() {
    alert("Hello");
}

function setTableElements(elements) {
    let table = $("#results-table");

    // Clear existing table data
    table.find("tr:gt(0)").remove();

    for (let movieData of elements) {
        // Movie title
        let appendStr = "<tr>";
        appendStr += "<td>" + movieData[0] + "</td>";

        // Movie genres
        if (movieData[1].length === 0) {
            appendStr += "<td>No genres</td>";
        } else {
            appendStr += "<td>" + movieData[1].join(", ") + "</td>";
        }

        appendStr += "<td>Test3</td>";
        appendStr += "</tr>";

        table.append(appendStr);
    }
}

function changeResultsVisibility(showTable, showStatus) {
    $("#results-table")[0].hidden = !showTable;
    $("#results-status")[0].hidden = !showStatus;
}

function setStatus(html) {
    let status = $("#results-status")[0];
    status.innerHTML = html;
}

function fetchRecs(page = 0) {
    $.get("/recommendations", {page: page}, function (data) {
        if (data.hasOwnProperty("noRatings")) {
            setStatus("<h4>You haven't rated any movies yet, so no recommendations can be generated</h4>");
            changeResultsVisibility(false, true);
        }

        // Update UI
        setTableElements(data);
        changeResultsVisibility(true, false);
    });
}