
angular
	.module("fandango", ["ngRoute",'ngSanitize'])
	.config(['$qProvider', function ($qProvider) {$qProvider.errorOnUnhandledRejections(false);}])
	.config(function($locationProvider, $routeProvider) {
		$locationProvider.html5Mode(true);
		$routeProvider
			.when("/", {
				templateUrl: 'www/views/main.html',
				controller:'main'

			})
	})
