
var app = angular.module("fandango",  ['angularMoment']);
app.controller("dashboard", ['$scope', '$interval','$http','moment',function($scope,$interval,$http,moment) {
  $scope.services = [];
  $scope.url= http:0.0.0.0:5001 /* "http://40.114.234.51:5000/";  */
  $scope.error=null;
  $scope.time= new Date();
  $scope.externals=[];
  $scope.ready=false;
  $scope.logs=[]
  $interval(function() {
	 $scope.refresh;
	 $scope.time= new Date();
    },600000)

  $scope.refresh = function() {
		$http({
		    method : "GET",
		      url : $scope.url+"status"
		  }).then(function mySuccess(response) {
		    $scope.logs = response.data.logs;
		    $scope.services=response.data.services;
		    $scope.externals=response.data.externals;
		    $scope.time=new Date(response.data.time*1000);
		    $scope.ready=response.data.ready;
		  }, function myError(response) {
		    $scope.error = response.statusText;
		  });  

	}
	 $scope.refresh();

	$scope.play = function(type,service) {
		$http({
		    method : "GET",
		      url : $scope.url+service+"/"+type+"/start"
		  }).then(function mySuccess(response) {
		    $scope.logs = response.data.logs;
		    $scope.services=response.data.services;
            $scope.externals=response.data.externals;
		    $scope.time=new Date(response.data.time*1000);
		    $scope.ready=response.data.ready;

		  }, function myError(response) {
		    $scope.error = response.statusText;
		  });  
	}
	$scope.stop = function(type,service) {
		$http({
		    method : "GET",
		      url : $scope.url+service+"/"+type+"/stop"
		  }).then(function mySuccess(response) {
		    $scope.logs = response.data.logs;
		    $scope.services=response.data.services;
		    $scope.externals=response.data.externals;
		    $scope.time=new Date(response.data.time*1000);
		    $scope.ready=response.data.ready;
		  }, function myError(response) {
		    $scope.error = response.statusText;
		  });  
	}
  
}]);

