var app = angular.module('app', ['ngSanitize']);
//var base = "/fandango/v0.2/fakeness";
var base = "http://fandango.livetech.site/fandango/v0.2/fakeness";

app.filter('dashless', function () {
    return function (input) {
        if (input) {
            return input.replace('-', ' ');
        }
    }
});

app.filter('capitalize', function () {
    return function (input) {
        return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
    }
});