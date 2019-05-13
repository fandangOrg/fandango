app.controller('indexCtrl', ['$scope', '$http', '$document', 'errorCode', 'crUrl', 'fakeness', 'feedback', 'claim', 'lang', 'alert', 'chart', '$sce', function ($scope, $http, $document, errorCode, crUrl, fakeness, feedback, claim, lang, alert, chart, $sce) {

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
    $scope.sirenUrlNew = '';
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
        'lang': '',
        'media': {
            'images': [],
            'video': []
        }
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

        let to_send = $scope.page.url;
        crUrl.analyzeUrl(to_send).then(function (response) {
            console.log(response.data);
            $scope.full_response = response.data;

            $scope.page.title = response.data.headline;
            $scope.page.text = response.data.articleBody;
            $scope.page.publisher = response.data.publisher;
            $scope.page.authors = response.data.author;
            $scope.page.date = response.data.dateCreated;
            $scope.page.lang = response.data.language;
            $scope.page.media.images = response.data.images;
            $scope.page.media.video = response.data.video;
            $scope.sirenUrlNew = sirenUrl.replace('QUERYDACAMBIARE',$scope.full_response.identifier[0]);
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
        return claim.getFakeness(level, levelReal);
    };

    $scope.getAuthorColor = function (score) {
        return fakeness.getAuthorFakeness(score);
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
            $(`#${key}`).prop('title', response.data);
            $(`#${key}`).tooltip('show');
        });
    };

    $scope.embedVideo = function (urlVideo) {
        urlVideo = urlVideo.replace("watch?v=", "embed/");
        return $sce.trustAsResourceUrl(urlVideo);
    };


    $scope.getFakenessColor = function (value) {
        return fakeness.getFakenessColor(value);
    };

    $scope.sendFakeness = function () {
        $scope.feedbackSelected = false;
        $scope.fakenessDone = false;
        $('#gaugeFakeness').removeClass('animated fadeIn');
        zingchart.exec('gaugeFakeness', 'destroy');

        let to_send = angular.copy($scope.full_response);   // PREVENT TWO WAY DATA BINDING
        to_send['images'] = $scope.media.images;
        to_send['video'] = $scope.media.video;

        $scope.loadingFakeness = true;

        fakeness.getFakeness(to_send).then(function (response) {
            $scope.fakenessValue = response.data.text[0];
            $scope.fakeValue = parseInt($scope.fakenessValue.FAKE * 100);
            $scope.realValue = parseInt($scope.fakenessValue.REAL * 100);
            $scope.page.media.images = response.data['images'];
            $scope.page.media.video = response.data['videos'];
            $scope.fakenessColor = fakeness.getFakenessColor($scope.realValue);
            chart.renderChart($scope.fakeValue);
            $scope.fakenessDone = true;
            $scope.loadingFakeness = false;
            $('#gaugeFakeness').addClass('animated fadeIn');

            console.log($scope.full_response);
        }, function (response) {
            $scope.fakenessDone = false;
            $scope.loadingFakeness = false;
            alert.showAlert('Error');
        });
    }
}]);
