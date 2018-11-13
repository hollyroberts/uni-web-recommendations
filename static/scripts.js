const settings = {
    "method": "GET",
    "headers": {
        "content-type": "application/json"
    },
};

function searchMovie() {
    let search_str = $("#search-movie-input").val();
    if (search_str.length === 0) {
        return;
    }

    $.get("/search_movies", {title: search_str}, function(data, status) {
       //alert(data);
    });
}