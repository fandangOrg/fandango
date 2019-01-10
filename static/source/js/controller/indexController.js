app.controller('indexCtrl',['$scope','$http','$document','errorCode','crUrl','fakeness','feedback','claim', 'lang', function ($scope, $http, $document, errorCode, crUrl, fakeness, feedback, claim, lang) {

    $scope.fakenessDone = false;
    $scope.highlightedText = '';
    $scope.selectedText = '';
    $scope.loadingFakeness = false;
    $scope.loadingAnalyzeUrl = false;
    $scope.feedbackSelected = false;
    $scope.selectedLanguage = "en";

    $scope.page = {
        'author': '',
        'publisher': '',
        'url':'',
        'text':'',
        'title':''
    };

    var levelReal = ['true', 'mostly-true', 'half-true'];
    // var levelFalse = ['false', 'pants-fire'];

    angular.element(function () {
        $("[rel=tooltip]").tooltip({placement: 'left'});
        lang.getLanguages().then(function (response) {
            $scope.languages = response.data;
            $scope.loading = false;
        });
    });


    $("#gaugeFakeness").on("contextmenu", function () {
        return false;
    });

    $scope.showSelectedText = function () {
        $scope.selectedText = $scope.getSelectionText();
    };

    $scope.changeLanguage = function (language) {
        if(language.active === 'False') {
            return;
        }
        else {
            $scope.selectedLanguage = language.language;
        }
    };

    $scope.getSelectionText = function () {

        if (window.getSelection) {
            try {
                var ta = $('textarea').get(0);
                $scope.highlightedText = ta.value.substring(ta.selectionStart, ta.selectionEnd);
                return $scope.highlightedText;
            } catch (e) {
                console.log('Cant get selection text')
            }
        }

        // IF IE
        if (document.selection && document.selection.type != "Control") {
            $scope.highlightedText = document.selection.createRange().text;
        }
    };

    $scope.sendClaim = function () {
        var to_send = {
            'text': $scope.selectedText
        };

        claim.getClaim(to_send).then(function (response) {
            console.log(response.data);
            $scope.claims = response.data;
        }, function (response) {

        });
    };

    $scope.getClaimFakeness = function (level) {
        if (levelReal.includes(level))
            return 'text-green';
        else if (level === 'barely-true')
            return 'text-blue';
        else
            return 'text-red';
    };

    $scope.clear = function () {
        $scope.selectedText = '';
        $scope.claims = null;
    };

    $scope.sendFeedback = function (value) {

        $scope.feedbackSelected = true;

        $("#alert").fadeIn();
        $("#feedback").fadeOut();

        var to_send = {
            'title': $scope.page.title,
            'text': $scope.page.text,
            'label': value
        };

        feedback.sendFb(to_send).then(function (response) {
            console.log(response)
        }, function (response) {
        });
    };

    $scope.analyzeUrl = function () {
        if (!$scope.page.url)
            return false;

        $scope.loadingAnalyzeUrl = true;

        var to_send = $scope.page.url;
        crUrl.analyzeUrl(to_send).then(function (response) {
            console.log(response.data)
            $scope.page.title = response.data.title;
            $scope.page.text = response.data.text;
            $scope.page.publisher = response.data.source_domain;
            $scope.page.author = response.data.authors;
            $scope.loadingAnalyzeUrl = false;
        }, function (response) {
            $scope.loadingAnalyzeUrl = false;
        });
    };

    $scope.send = function () {
        $scope.feedbackSelected = false;
        $scope.fakenessDone = false;
        $('#gaugeFakeness').removeClass('animated fadeIn');
        zingchart.exec('gaugeFakeness', 'destroy');

        if (!$scope.page.title || !$scope.page.text)
            return false;

        var to_send = {
            'title': $scope.page.title,
            'text': $scope.page.text,
            'source': ''
        };

        $scope.loadingFakeness = true;
        fakeness.getFakeness(to_send).then(function (response) {
            $scope.value = response.data[0];
            $scope.fakeValue = parseInt($scope.value.FAKE * 100);
            $scope.realValue = parseInt($scope.value.REAL * 100);

            zingchart.render({
                id: 'gaugeFakeness',
                data: {
                    "type": "gauge",
                    "background-color": "#f7fafc",
                    "scale-r": {
                        "markers": [
                            {
                                "type": "line",
                                "range": [50],
                                "line-color": "grey",
                                "line-width": 2,
                                "line-style": "dashed",
                                "alpha": 1
                            }
                        ],
                        "aperture": 200,
                        "values": "0:100:25",
                        "center": {
                            "size": 5,
                            "background-color": "#66CCFF #FFCCFF",
                            "border-color": "none"
                        },
                        "ring": {
                            "size": 10,
                            "rules": [
                                {
                                    "rule": "%v >= 0 && %v <= 25",
                                    "background-color": "green"
                                },
                                {
                                    "rule": "%v >= 25 && %v <= 50",
                                    "background-color": "yellow"
                                },
                                {
                                    "rule": "%v >= 50 && %v <= 75",
                                    "background-color": "orange"
                                },
                                {
                                    "rule": "%v >= 75 && %v <=100",
                                    "background-color": "red"
                                }
                            ]
                        },
                        "labels": ["REAL", "", "", "", "FAKE"],  //Scale Labels
                        "item": {  //Scale Label Styling
                            "font-color": "black",
                            "font-family": "Open Sans, serif",
                            "font-size": 13,
                            "font-weight": "bold",   //or "normal"
                            "font-style": "normal",   //or "italic"
                            "offset-r": 0,
                            "angle": "auto"
                        }
                    },
                    gui: {
                        contextMenu: {
                            empty: true
                        }
                    },
                    "plot": {
                        tooltip: {
                            visible: false
                        },
                        "csize": "5%",
                        "size": "100%",
                        "background-color": "#000000"
                    },
                    "series": [
                        {"values": [$scope.fakeValue]}
                    ]
                },
                height: "100%",
                width: "100%"
            });
            $scope.fakenessDone = true;
            $scope.loadingFakeness = false;
            $('#gaugeFakeness').addClass('animated fadeIn');
        }, function (response) {
            $scope.fakenessDone = false;
            $scope.loadingFakeness = false;
            console.log(response)
        });
    }
}]);
