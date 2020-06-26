angular
    .module("fandango")
    .controller("manual", ['$scope', '$http', 'Api', '$location','$window','$document', function ($scope, $http, Api, $window, $document, $location) {
        $scope.foo="foo";
    }]);
	