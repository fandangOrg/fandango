app.controller('indexCtrl', ['$scope', '$http', '$document', 'errorCode', 'crUrl', 'fakeness', 'feedback', 'claim', 'lang', 'alert', 'chart', '$sce', function ($scope, $http, $document, errorCode, crUrl, fakeness, feedback, claim, lang, alert, chart, $sce) {

    $scope.fakenessDone = false;
    $scope.loadingFakeness = false;
    $scope.loadingAnalyzeUrl = false;
    $scope.feedbackSelected = false;
    $scope.showChart = false;
    $scope.highlightedText = '';
    $scope.selectedText = '';
    $scope.fakenessColor = '';
    $scope.sirenUrlNew = '';
    $scope.videoAnalysisUrl = videoAnalysisUrl; // CONST IN APP.JS
    $scope.full_response = {};
    $scope.mediaDetails = {};
    $(".alert").hide();


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
        images: [],
        video: []
    };

    const levelReal = ['true', 'mostly-true', 'half-true'];
    // const levelFalse = ['false', 'pants-fire'];

    angular.element(function () {
        $scope.loading = false;
    });

    $("#gaugeFakeness").on("contextmenu", function () {
        return false;
    });

    $scope.analyzeUrl = function () {
        $scope.loadingAnalyzeUrl = true;
        $scope.fakenessDone = false;

        $scope.media.images = [];
        $scope.media.video = [];

        crUrl.analyzeUrl($scope.page.url).then(function (response) {
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
            $scope.sirenUrlNew = sirenUrl.replace('QUERYDACAMBIARE', $scope.full_response.identifier[0]);
            $scope.loadingAnalyzeUrl = false;
        }, function (response) {
            $scope.loadingAnalyzeUrl = false;
            alert.showAlert('Error');
        });
    };

    $scope.showSelectedText = function () {
        $scope.selectedText = $scope.getSelectionText();
    };

    $scope.showMediaDetails = function (video) {
        $scope.mediaDetails = video;
        $('#mediaDetailsModal').modal('show');
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

        let to_send = { 'text': $scope.selectedText };

        claim.getClaim(to_send).then(function (response) {
            console.log(response.data);
            $scope.claims = response.data;
        }, function () {
            alert.showAlert('Error');
        });
    };

    $scope.saveClaim = function (label) {

        let to_send = {
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

    $scope.getFakenessColor = function (value) {
        return fakeness.getFakenessColor(value);
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

        let to_send = {
            'title': $scope.page.title,
            'text': $scope.page.text,
            'label': value
        };

        feedback.sendFb(to_send).then(function (response) {
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
            $scope.page.authors = response.data['authors'];
            $scope.page.publisher = response.data['publishers'];

            $scope.fakenessColor = fakeness.getFakenessColor($scope.realValue);
            chart.renderChart($scope.fakeValue);
            $scope.fakenessDone = true;
            $scope.loadingFakeness = false;
            $('#gaugeFakeness').addClass('animated fadeIn');

            console.log('FAKENESS ->', response.data);
            console.log('PAGE ->', $scope.page);
        }, function (response) {
            $scope.media.images = [];
            $scope.media.video = [];
            $scope.fakenessDone = false;
            $scope.loadingFakeness = false;
            alert.showAlert('Error');
        });
    }
}]);
