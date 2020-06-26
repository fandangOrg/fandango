angular
    .module("fandango")
    .controller("search", ['$scope', '$http', 'Api', '$location','$window','$document', '$routeParams', function ($scope, $http, Api, $window, $document, $location, $routeParams) {
        $scope.highlighted = false;
        $scope.tweets = []
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
                    Api.searchDomain($scope.query).then(
                        function (data) {
                            $scope.searching = false;
                            $scope.whoIsFeatures = data.data.whois_features;
                            $scope.whoIsImportance = data.data.whois_importance;
                            $scope.suffixData = data.data.suffix_information;
                            /*$scope.suffixData={
                                "name": ".com",
                                "entity": "commercial",
                                "administrator": "Education",
                                "idn": "Yes",
                                "dnssec": "Yes",
                                "sld": "Yes",
                                "ipv6": "Yes",
                                "importance_weight": 0.3
                            };*/
                            $scope.neo4jData = data.data.neo4j_features;
                            $scope.info = data.data;
                            console.log($scope.info);
                            console.log($scope.neo4jData);
                            delete $scope.info.whois_features;
                            delete $scope.info.whois_importance;
                            delete $scope.info.suffix_information;
                            delete $scope.info.neo4j_features;
                            $scope.ponder();
                            if (!$scope.info) {
                                $(".empty").show();
                            }
                            setTimeout(function () {
                                $(".btn-search i").addClass("fa-search");
                                $(".btn-search i").removeClass("fa-sync");
                                $(".btn-search i").removeClass("fa-spin");
                                $("body").css("overflow-y", "scroll");
                                $(".results").slideDown(1000);

                            }, 2000);
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
        $scope.ponder = function () {
            $scope.general = {
                "Scope": $scope.info.location,
                "Media Type": $scope.info.media_type,
                "Topics": $scope.info.media_focus,
                "Language": $scope.info.language.toString().replace("[",
                    "").replace("]", "").replace(",", ", "),
                "Platform": $scope.info.platform.toString().replace("[",
                    "").replace("]", "").replace(",",
                    ", ").replace("N/A", "Online"),
                "Is it a malicious url?": ($scope.info.malicious) ? "Yes" : "No",
            };
            $scope.whoIsAnalysis = {
                "Name of the domain": $scope.whoIsFeatures.domain_name.toString().toLowerCase(),
                "Online since:": $scope.whoIsFeatures.creation_date,
                "Online until:": $scope.whoIsFeatures.expiration_date,
                "Website name from URL": $scope.whoIsFeatures.name,
                "Website name from <a href='https://www.ultratools.com/tools/ipWhoisLookup'>WhoIsIP</a>":
                $scope.whoIsFeatures.whois_name,
                "Country from URL": $scope.whoIsFeatures.country,
                "Country from <a href='https://www.ultratools.com/tools/ipWhoisLookup'>WhoIsIP</a>":
                $scope.whoIsFeatures.whois_country,
                "Who owns the website": $scope.whoIsFeatures.org,

            };
            $scope.suffix = {
                "Suffix domain": $scope.suffixData.name,
                "Suffix entity": $scope.suffixData.entity,
                "Suffix administrator": $scope.suffixData.administrator,
                "<span data-toggle='tooltip' title='Internationalized domain name'>IDN</span>":
                $scope.suffixData.idn,
                "<span data-toggle='tooltip' title='Domain Name System Security Extensions'>DNSSEC</span>":
                $scope.suffixData.dnssec,
                "<span data-toggle='tooltip' title='Second-level domain'>SLD</span>":
                $scope.suffixData.sld,
                "IPv6": $scope.suffixData.ipv6
            };
            $scope.algorithm = {
                "<span data-toggle='tooltip' title='The older the domain, the higher the level of trustworthiness.'>Age of the domain</span>": {
                    value: (($scope.whoIsImportance.date < 0) ? "N/A" : $scope.whoIsImportance.date + " month" +
                        (($scope.whoIsImportance.date <= 1) ? "" : "s")),
                    weight: $scope.whoIsImportance.date_importance
                },
                "<span data-toggle='tooltip' title='The higher the number of months for the expiration date, the higher the level of \ntrustworthiness.'>When is it going to expire?</span>": {
                    value: (($scope.whoIsImportance.exp_date < 0) ? "N/A" : $scope.whoIsImportance.exp_date + " month" +
                        (($scope.whoIsImportance.exp_date <= 1) ? "" : "s")),
                    weight: $scope.whoIsImportance.exp_date_importance
                }
                ,
                "<span data-toggle='tooltip' title='If the country is known, the level of trustworthiness is increased and viceversa.'>Country verification</span>": {
                    value: (($scope.whoIsImportance.country <= 0) ? "No" : "Yes"),
                    weight: $scope.whoIsImportance.country_importance
                },
                "<span data-toggle='tooltip' title='If the name of the domain is known regarding Whois, the level of trustworthiness \nis increased and viceversa.'>Name verification</span>": {
                    value: (($scope.whoIsImportance.name <= 0) ? "No" : "Yes"),
                    weight: $scope.whoIsImportance.name_importance
                },
                "<span data-toggle='tooltip' title='If the url is safe, the level of trustworthiness is increased and viceversa.'>Maliciousness</span>": {
                    value: ($scope.info.malicious) ? "Yes" : "No",
                    weight: $scope.info.malicious_importance
                },
                "<span data-toggle='tooltip' title='Depending on the type of the media, the level of trustworthiness will increase or \nnot.'>Media type</span>": {
                    value: $scope.info.media_type,
                    weight: $scope.info.media_type_importance
                },
                "<span data-toggle='tooltip' title='It measures the rank of non-anonymous authors\nwhether the domain is available in the database.\nIf not, the rank is not computed. The higher the value,\nthe higher the level of trustworthiness.'>Non-Anonymous rank</span>": {
                    value: ($scope.neo4jData.anonymous_rank<0)?"N/A":$scope.neo4jData.anonymous_rank,
                    weight: $scope.neo4jData.anonymous_rank_importance
                },
                "<span data-toggle='tooltip' title='It measures the importance of the domain in the network\n whether the domain is available in the database.\nIf not the rank is not computed. The higher the value, \nthe higher the level of trustworthiness.'>Centrality rank</span>": {
                    value: ($scope.neo4jData.centrality_rank<0)?"N/A":$scope.neo4jData.centrality_rank,
                    weight: $scope.neo4jData.centrality_rank_importance
                },

            };
            $scope.suffixIcon={
                idn: {
                    string:"IDN",
                    data:$scope.suffixData.idn==="Yes",
                    style:($scope.suffixData.idn==="Yes")?'color:black;font-weight: bold;':''
                },
                dnssec:  {
                    string:"DNSSEC",
                    data:$scope.suffixData.dnssec==="Yes",
                    style:($scope.suffixData.dnssec==="Yes")?'color:black;font-weight: bold;':''
                },
                sld:  {
                    string:"SLD",
                    data:$scope.suffixData.sld==="Yes",
                    style:($scope.suffixData.sld==="Yes")?'color:black;font-weight: bold;':''
                },
                ipv6:  {
                    string:"IPv6",
                    data:$scope.suffixData.ipv6==="Yes",
                    style:($scope.suffixData.ipv6==="Yes")?'color:black;font-weight: bold;':''
                }
            };


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
        	$scope.query = $routeParams.searchString;
        	$scope.search();
        	console.log("SEARCHED USING PARAMS")
        });
    }]);
	