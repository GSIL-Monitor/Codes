function show_data(url, postdata, data) {
    document.getElementById("url").innerHTML = url;
    document.getElementById("postdata").innerHTML = postdata;
    document.getElementById("data").innerHTML = data;
    document.getElementById("msg").innerHTML = "";
}

function clean_data() {
    document.getElementById("url").innerHTML = "";
    document.getElementById("postdata").innerHTML = "";
    document.getElementById("data").innerHTML = "";
    document.getElementById("msg").innerHTML = "";
}