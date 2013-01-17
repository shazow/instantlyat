$(document).ready(function() {
	$("#website").poll({
        url: "/api?",
        data: {function: "get_latest", place: "foo"},
        interval: 10000,
        type: "GET",
        dataType: "json",
        success: function(data) {
			$("#website").get(0).addImages(data);
        }
    });
});