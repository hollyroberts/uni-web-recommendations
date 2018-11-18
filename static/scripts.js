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
        let status = $("#results-status")[0];
        let table = $("#results-table");

        // Update status
        if (data.length === 0) {
            status.innerHTML = "<h4>No results found for \"" + searchStr + "\"</h4>";
            showTable(false);
            return;
        }
        status.innerHTML = "<p>" + data.length + (data.length === 1 ? " result" : " results") + " found</p>";

        // Update table
        setTableElements(table, data);
        showTable()
    });
}

function setTableElements(table, elements) {
    // Clear existing table data
    table.find("tr:gt(0)").remove();

    for (let movie of elements) {
        let appendStr = "<tr>";
        appendStr += "<td>" + movie + "</td>";
        appendStr += "<td>Test2</td>";
        appendStr += "<td>Test3</td>";
        appendStr += "</tr>";

        table.append(appendStr);
    }
}

function showTable(bool = true) {
    $("#results-table")[0].hidden = !bool;
}