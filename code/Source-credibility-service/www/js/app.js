
angular
	.module("fandango", ["ngRoute","ngSanitize","ngMaterial", "ngMessages"])
	.config(['$qProvider', function ($qProvider) {$qProvider.errorOnUnhandledRejections(false);}])
	.config(function($locationProvider, $routeProvider) {
		$locationProvider.html5Mode(true);
		$routeProvider
			.when("/", {
				templateUrl: 'www/views/main.html',
				controller:'main'
			})
			.when('/search/:searchString', {
				templateUrl: 'www/views/main.html',
				controller: 'search',
			})
			.when('/manual', {
				templateUrl: 'www/views/manual_guidelines.html',
				controller: 'manual',
			})
            
	})
