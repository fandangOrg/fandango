app.controller('indexCtrl', function ($scope, $http, $document, errorCode, url, fakeness, feedback) {

    $scope.fakenessDone = false;
    $scope.loadingFakeness = false;
    $scope.loadingAnalyzeUrl = false;
    angular.element(function () {
        $scope.loading = false;
    });

    $("#gaugeFakeness").on("contextmenu", function () {
        return false;
    });

    $scope.sendFeedback = function (value) {

        if (value === true) {
            var to_send = {
                'title': $scope.title,
                'text': $scope.text,
                'feedback': checkfeedback(value)
            }
        }
        else {
            var to_send = {
                'title': $scope.title,
                'text': $scope.text,
                'feedback': checkfeedback(value)
            }
        }

        console.log(to_send)

        feedback.sendFb(to_send).then(function (response) {
            console.log(response)
        }, function (response) {
        });
    };

    function checkfeedback (value) {
        console.log(value)
        if ($scope.fakeValue > $scope.realValue) {
            $scope.max = 'fake';
            $scope.min = 'real';
        }
        else {
            $scope.max = 'real';
            $scope.min = 'fake';
        }

        if(value === 'yes')
            return $scope.max
        else
            return $scope.min
    }

    $scope.analyzeUrl = function () {
        if (!$scope.url)
            return false;

        $scope.loadingAnalyzeUrl = true;

        var to_send = $scope.url;

        url.analyzeUrl(to_send).then(function (response) {
            $scope.page = response.data;
            $scope.title = $scope.page.title;
            $scope.text = $scope.page.body;
            $scope.loadingAnalyzeUrl = false;
        }, function (response) {
            $scope.loadingAnalyzeUrl = false;
        });
    };

    $scope.send = function () {
        $scope.fakenessDone = false;
        $('#gaugeFakeness').removeClass('animated fadeIn');
        zingchart.exec('gaugeFakeness', 'destroy');

        if (!$scope.title || !$scope.text)
            return false;

        var to_send = {
            'title': $scope.title,
            'text': $scope.text,
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
                        "aperture": 200,
                        "values": "0:100:20",
                        "center": {
                            "size": 5,
                            "background-color": "#66CCFF #FFCCFF",
                            "border-color": "none"
                        },
                        "ring": {
                            "size": 10,
                            "rules": [
                                {
                                    "rule": "%v >= 0 && %v <= 20",
                                    "background-color": "blue"
                                },
                                {
                                    "rule": "%v >= 20 && %v <= 40",
                                    "background-color": "green"
                                },
                                {
                                    "rule": "%v >= 40 && %v <= 60",
                                    "background-color": "yellow"
                                },
                                {
                                    "rule": "%v >= 60 && %v <= 80",
                                    "background-color": "orange"
                                },
                                {
                                    "rule": "%v >= 80 && %v <=100",
                                    "background-color": "red"
                                }
                            ]
                        },
                        "labels": ["0 %", "20 %", "40 %", "60 %", "80 %", "100 %"],  //Scale Labels
                        "item": {  //Scale Label Styling
                            "font-color": "black",
                            "font-family": "Open Sans, serif",
                            "font-size": 12,
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
});
