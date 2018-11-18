function searchMovie() {
    // Form elements
    let search_str = $("#search-movie-input").val();
    if (search_str.length === 0) {
        return;
    }
    let recommend = $("#recommend-search-checkbox")[0].checked;

    let data = {
        title: search_str,
        recommend: recommend
    };

    $.get("/search_movies", data, function (data) {
        console.log(data);

        let status = $("#results-container")[0];
        if (data.length === 0) {
            status.innerHTML = "<h4>No results found</h4>";
            return;
        }

        status.innerHTML = "<p>" + data.length + (data.length === 1 ? " result" : " results") + " found</p>";
    });
}