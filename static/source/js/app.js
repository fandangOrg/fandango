const app = angular.module('app', ['ngSanitize']);

var base = "http://192.168.2.185:9800/fandango/v0.3/fakeness";
// var base = "/fandango/v0.3/fakeness";

app.filter('capitalize', function () {
    return function (input) {
        return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
    }
});
