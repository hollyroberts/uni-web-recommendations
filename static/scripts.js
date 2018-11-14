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

    $.get("/search_movies", data, function(data, status) {
       //alert(data);
    });
}