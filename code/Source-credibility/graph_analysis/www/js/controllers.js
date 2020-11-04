angular
    .module("fandango")
    .controller("manual", ['$scope', '$http', 'Api', '$location','$window','$document', function ($scope, $http, Api, $window, $document, $location) {}])
    .controller("main", ['$scope', '$http', 'Api', '$location','$window','$document', '$routeParams', function ($scope, $http, Api, $window, $document, $location, $routeParams) {
        $scope.highlighted = false;
        $scope.twitterShowData = {}
        $scope.query = ""
        $scope.searching = false;
        $scope.keyPress = function (keyEvent) {
            if (keyEvent.which === 13) {
                $scope.search();
            }
        };
        $scope.main_color = "grey";
        $scope.search = function () {
            
            if ($scope.query != "") {
                $(".error").hide();
                $(".empty").hide();
                if (!$scope.searching) {
                    $scope.searching = true;
                    $(".btn-search i").removeClass("fa-search");
                    $(".btn-search i").addClass("fa-sync");
                    $(".btn-search i").addClass("fa-spin");
                    $(".s004 legend").slideUp(1000);
                    $('body').css('background', '#fff');
                    console.log("BEFORE API SEARCH DOMAIN")
                    Api.searchDomain($scope.query).then(
                        function (data) {
                            console.log(data)
                            $scope.searching = false;
                            $scope.twitterData = data.data.twitter_information;
                            $scope.generalData = data.data.source_information;
                            $scope.neo4jData = data.data.neo4j_information;
                            if (!data.data) {
                                $(".empty").show();
                            }
                            $scope.formatData();
                            setTimeout(function () {
                                $(".btn-search i").addClass("fa-search");
                                $(".btn-search i").removeClass("fa-sync");
                                $(".btn-search i").removeClass("fa-spin");
                                $("body").css("overflow-y", "scroll");
                                $(".results").slideDown(1000);

                            }, 2000);
                            console.log("FINISHED")
                        },
                        function (error) {
                            $(".btn-search i").addClass("fa-search");
                            $(".btn-search i").removeClass("fa-sync");
                            $(".btn-search i").removeClass("fa-spin");
                            $scope.searching = false;
                            console.log(error);
                            $(".error").show();
                            $(".feed").hide();
                            $(".results").slideDown(1000);

                        }
                    );
                    $(".fandango-logo").slideUp(1000, function () {
                        $('.s004').css('min-height', 0);
                    });
                    $(".s004 input").animate({
                        "min-height": "50px"
                    }, 1000, function () {
                    });

                }
            }
        };
       
        $scope.highlight = function (group) {
            if (!$scope.highlighted) {
                $scope.highlighted = true;
                $("." + group).addClass("highlighted");
                $(".blur").show();
            } else {
                $scope.highlighted = false;
                $(".news").removeClass("highlighted");
                $(".blur").hide();
            }
        };
        
        $scope.formatData = function () {
        	 
        	$scope.generalShowData = {
				"Location": $scope.generalData.location,
				"Media Type": $scope.generalData.media_type,
				"Media Focus": $scope.generalData.media_focus,
				"Language": $scope.generalData.language,
				"Platform": $scope.generalData.platform,
				"Malicious": $scope.generalData.malicious
        	}
        	
        	$scope.neo4jShowData = {
    			"Page Rank": $scope.neo4jData.page_rank,
    			"Suffix Rank": $scope.neo4jData.suffix_rank,
    			"Text Rank": $scope.neo4jData.text_rank,
    			"Twitter Rank": $scope.neo4jData.twitter_rank,
    			"Trustworthiness": $scope.neo4jData.trustworthiness
        	}
        };


        //STICKY-TOP (SEE MAIN.HTML)

        $(window).scroll( function() {
            console.log("Scrolling...");

            console.log($(document));

            if ($(document).scrollTop() > 97 && $(document)[0].documentElement.scrollTop > 97) {
                console.log("Shrinking...");
                $("#feed-top")
                    .addClass(($(document).width()>=768)? "feed-top-sm":"feed-top-sm feed-top-tight")
                    .removeClass("feed-top");
                $("#top-title").removeClass("display-1");
            } else {
                console.log("Growing...");
                $("#feed-top")
                    .addClass("feed-top")
                    .removeClass("feed-top-sm feed-top-tight");
                $("#top-title").addClass("display-1");
            }
        });
        
        
        $scope.$on('$viewContentLoaded', function(){
            //Here your view content is fully loaded !!
            let areRouteParamsEmpty = Object.keys($routeParams).length === 0 && $routeParams.constructor === Object
            console.log(areRouteParamsEmpty)
            if (!areRouteParamsEmpty){
                $scope.query = $routeParams.publisher
                console.log($routeParams.publisher)
                $scope.search();
                console.log("SEARCHED USING PARAMS")
            }
        	
        });
        
    }]);
	