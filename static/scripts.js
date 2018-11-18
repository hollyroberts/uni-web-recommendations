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
        console.log(data)

        let container = $("#results-container")[0];
        if (data.length === 0) {
            container.innerHTML = "<p>No results found</p>";
            return;
        }

        let htmlString = "<p>" + data.length + (data.length === 1 ? " result" : " results") + " found</p>";

        container.innerHTML = htmlString;
    });
}