app.controller('indexCtrl', ['$scope', '$http', '$document', 'errorCode', 'crUrl', 'fakeness', 'feedback', 'claim', 'lang', 'alert', '$sce', function ($scope, $http, $document, errorCode, crUrl, fakeness, feedback, claim, lang, alert, $sce) {

    $scope.fakenessDone = false;
    $scope.loadingFakeness = false;
    $scope.loadingAnalyzeUrl = false;
    $scope.feedbackSelected = false;
    $scope.showChart = true;
    // $scope.isVideoEnabled = false;
    // $scope.isImagesEnabled = false;
    // $scope.mediaLoading = false;
    $scope.highlightedText = '';
    $scope.selectedText = '';
    $scope.fakenessColor = '';
    $scope.full_response = {};
    $(".alert").hide();

    $scope.videoAnalysisUrl = videoAnalysisUrl;

    $scope.page = {
        'authors': [],
        'publisher': [],
        'url': '',
        'text': '',
        'title': '',
        'date': '',
        'lang': ''
    };

    $scope.media = {
        'images': [],
        'video': []
    };

    const levelReal = ['true', 'mostly-true', 'half-true'];
    // var levelFalse = ['false', 'pants-fire'];

    angular.element(function () {
        $scope.loading = false;
    });

    $("#gaugeFakeness").on("contextmenu", function () {
        return false;
    });

    $scope.analyzeUrl = function () {
        if (!$scope.page.url)
            return false;

        $scope.loadingAnalyzeUrl = true;
        $scope.fakenessDone = false;

        $scope.media = {
            'images': [],
            'video': []
        };

        var to_send = $scope.page.url;
        crUrl.analyzeUrl(to_send).then(function (response) {
            console.log(response.data);

            $scope.full_response = response.data;

            $scope.page.title = response.data.headline;
            $scope.page.text = response.data.articleBody;
            $scope.page.publisher = response.data.publisher;
            $scope.page.authors = response.data.author;
            $scope.page.date = response.data.dateCreated;
            $scope.page.lang = response.data.language;
            $scope.loadingAnalyzeUrl = false;
        }, function (response) {
            $scope.loadingAnalyzeUrl = false;
        });
    };

    $scope.showSelectedText = function () {
        $scope.selectedText = $scope.getSelectionText();
    };

    $scope.getSelectionText = function () {

        if (window.getSelection) {
            try {
                let ta = $('textarea').get(0);
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

        console.log($scope.selectedText);

        // if ($scope.selectedText.trim() === '' || !$scope.selectedText)
        //     return;

        var to_send = {
            'text': $scope.selectedText
        };

        claim.getClaim(to_send).then(function (response) {
            console.log(response.data);
            $scope.claims = response.data;
        }, function (response) {

        });
    };

    $scope.saveClaim = function (label) {
        var to_send = {
            'claim': $scope.selectedText,
            'label': label
        };

        claim.saveClaim(to_send).then(function (response) {
            alert.showAlert('Success');
        }, function (response) {
            alert.showAlert('Error');
        })
    };

    $scope.getClaimFakeness = function (level) {
        if (levelReal.includes(level))
            return 'text-green';
        else if (level === 'barely-true')
            return 'text-blue';
        else
            return 'text-red';
    };

    $scope.getAuthorColor = function (score) {
        switch (true) {
            case (score < 20):
                return 'text-red';
            case (score < 40):
                return 'text-warning';
            case (score < 80):
                return 'text-yellow';
            case (score > 80):
                return 'text-green';
        }
    };

    $scope.getFakenessColor = function (value) {
        switch (true) {
            case value <= 25:
                return 'bg-danger';
            case value <= 50:
                return 'bg-warning';
            case value <= 75:
                return 'bg-yellow';
            default:
                return 'bg-success'
        }
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

    $scope.clickCb = function (event, tipo, value) {
        if (event.target.checked) {
            $scope.media[tipo].push(value)
        } else {
            let index = $scope.media[tipo].indexOf(value);
            if (index !== -1) $scope.media[tipo].splice(index, 1);
        }
        console.log($scope.media);
    };

    $scope.getDesc = function (key) {
        fakeness.getInfoScore(key).then(function (response) {
            $('#' + key).prop('title', response.data);
            $('#' + key).tooltip('show');
        });
    };

    $scope.embedVideo = function (urlVideo) {
        urlVideo = urlVideo.replace("watch?v=", "embed/");
        return $sce.trustAsResourceUrl(urlVideo);
    };

    $scope.sendFakeness = function () {
        $scope.feedbackSelected = false;
        $scope.fakenessDone = false;
        $('#gaugeFakeness').removeClass('animated fadeIn');
        zingchart.exec('gaugeFakeness', 'destroy');

        $scope.loadingFakeness = true;

        let to_send = angular.copy($scope.full_response);   // PREVENT TWO WAY DATA BINDING

        to_send['images'] = $scope.media.images;
        to_send['video'] = $scope.media.video;

        fakeness.getFakeness(to_send).then(function (response) {
            console.log(response.data);
            $scope.value = response.data.text[0];
            $scope.fakeValue = parseInt($scope.value.FAKE * 100);
            $scope.realValue = parseInt($scope.value.REAL * 100);
            $scope.full_response['video'] = response.data['videos'];
            $scope.full_response['images'] = response.data['images'];
            $scope.fakenessColor = $scope.getFakenessColor($scope.realValue);
            console.log($scope.full_response);

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
        });
    }
}]);
