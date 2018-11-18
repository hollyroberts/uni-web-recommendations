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
            table.hidden = true;
            return;
        }
        status.innerHTML = "<p>" + data.length + (data.length === 1 ? " result" : " results") + " found</p>";

        // Clear existing table data
        table.find("tr:gt(0)").remove();

        for (let movie of data) {
            let appendStr = "<tr>";
            appendStr += "<td>Test1</td>";
            appendStr += "<td>Test2</td>";
            appendStr += "<td>Test3</td>";
            appendStr += "</tr>";

            table.append(appendStr);
        }

        table.hidden = false;
    });
}