var app = angular.module('app', ['ngSanitize', 'ui.router']);
var base = "http://192.168.2.161:9800/fandango/v0.3/fakeness";
//var base = "http://fandango.livetech.site/fandango/v0.3/fakeness";

app.filter('capitalize', function () {
    return function (input) {
        return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
    }
});

app.config(['$locationProvider', function ($locationProvider) {
    $locationProvider.hashPrefix('');
}]);

app.config(['$stateProvider', '$urlRouterProvider', function ($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/');

    $stateProvider

        .state('auto', {
            url: '/',
            views: {
                'article_checker': {templateUrl: 'article_checker_auto.html'},
                'annotation': {templateUrl: 'annotation_auto.html',},
            }
        })
        .state('manual', {
            url: '/manual',
            views: {
                'article_checker': {templateUrl: 'article_checker_manual.html'},
                'annotation': {templateUrl: 'annotation_manual.html'},
            }
        })
        .state('domain', {
            url: '/domain',
            views: {
                'article_checker': {templateUrl: 'article_checker_domain.html'},
                'annotation': {templateUrl: 'annotation_domain.html'},
            }
        })
}
]);

