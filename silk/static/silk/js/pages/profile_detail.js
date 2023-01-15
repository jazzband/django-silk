function createViz() {
    var profileDotURL = JSON.parse(document.getElementById("profileDotURL").textContent);

    $.get(
        profileDotURL,
        { cutoff: $('#percent').val() },
        function (response) {
            var svg = '#graph-div';
            $(svg).html(Viz(response.dot));
            $(svg + ' svg').attr('width', 960).attr('height', 600);
            svgPanZoom(svg + ' svg', { controlIconsEnabled: true });
        }
    );
}
createViz();
