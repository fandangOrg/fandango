
PATH="http://0.0.0.0:5000";

angular
	.module("fandango")
	.factory("Api" ,function($http){
		var factory = {};
		var apiKey =  null;
		factory.searchDomain = function(query) {
			//COMMENT THIS FOR DEMO
			let url=`/api/graph_analysis/ui/domain_analysis/${query}`;
			console.log(url)
			return $http.get(url);
		};
		return factory;
	});
