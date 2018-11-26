var app = angular.module('app', []);
var base = "/fandango/v0.1/fakeness";

// var app = angular.module('app', []);
 //var base = "http://192.168.1.58:9800/fandango/v0.1/fakeness";

app.filter('dashless',function() {
    return function(input) {
        if (input) {
            return input.replace('-', ' ');
        }
    }
});

app.filter('capitalize', function() {
    return function(input) {
        return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
    }
});