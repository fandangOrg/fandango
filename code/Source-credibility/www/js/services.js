
PATH="http://51.138.37.2:5000";

angular
	.module("fandango")
	.factory("Api" ,function($http){
		var factory = {};
		var apiKey =  null;
		factory.search = function(query) {
			url=PATH+"search";
			return $http.post(url,query);
		};
		factory.searchDomain = function(query) {
			//COMMENT THIS FOR DEMO
			url=PATH + "/graph_analysis/ui/domain_analysis";
			console.log(url);
			//query=query.split(" ");
			console.log(query);
			data={"domain": query};
			return $http.post(url,data);

			//UNCOMMENT THIS FOR DEMO
			//return $http.get("www/output_twitter.json");
			
		};
		return factory;
	});
