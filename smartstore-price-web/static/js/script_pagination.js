function page(num){
    let urlParams = new URLSearchParams(window.location.search);
    urlParams.set('page', num);
    window.location.search = urlParams.toString();
}