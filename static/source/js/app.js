const app = angular.module('app', ['ngSanitize']);

const videoAnalysisUrl = 'http://195.251.117.224:8000/';
const base = "http://192.168.2.185:9800/fandango/v0.3/fakeness";
// const base = "/fandango/v0.3/fakeness";

app.filter('capitalize', function () {
    return function (input) {
        return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
    }
});
