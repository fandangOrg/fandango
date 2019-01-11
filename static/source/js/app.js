const index = angular.module('index', ['ngSanitize']);
const annotation = angular.module('annotation', ['ui.router']);

const base = "http://192.168.2.161:9800/fandango/v0.3/fakeness";
//var base = "http://fandango.livetech.site/fandango/v0.3/fakeness";

index.filter('capitalize', function () {
    return function (input) {
        return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
    }
});

annotation.filter('capitalize', function () {
    return function (input) {
        return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
    }
});

annotation.config(['$locationProvider', function ($locationProvider) {
    $locationProvider.hashPrefix('');
}]);

annotation.config(['$stateProvider', '$urlRouterProvider', function ($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/');

    $stateProvider
        .state('auto', {
            url: '/',
            views: {
                'article_checker': {templateUrl: 'article_checker_auto.html'},
                'annotation': {templateUrl: 'annotation_auto.html'},
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

