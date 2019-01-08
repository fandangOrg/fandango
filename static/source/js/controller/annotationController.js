app.controller('annotationCtrl', ['$scope', '$http', '$document', 'errorCode', 'url', 'fakeness', 'feedback', 'lang', 'next', 'update', function ($scope, $http, $document, errorCode, url, fakeness, feedback, lang, next, update) {

    $scope.fakenessDone = false;
    $scope.loadingFakeness = false;
    $scope.loadingAnalyzeUrl = false;
    $scope.feedbackSelected = false;
    $scope.radioSelected = false;

    $scope.page = {
        'author':'',
        'publisher':''
    };

    $scope.selectedLanguage = "en";
    // $scope.categories = ['Category 1','Category 2','Category 3'];
    angular.element(function () {
        $("[rel=tooltip]").tooltip({placement: 'left'});
        lang.getLanguages().then(function (response) {
            $scope.languages = response.data;
            $scope.loading = false;
        });
    });

    $scope.changeLanguage = function (language) {
        if (language.active === 'False') {
            return;
        } else {
            $scope.selectedLanguage = language.language;

            $("#btnStartAnalyze").addClass("animated fadeOut faster");
            setTimeout(function () {
                $("#btnStartAnalyze").remove();
            }, 500);

            $scope.analyzeStarted = true;

            next.goNext($scope.selectedLanguage).then(function (response) {
                $scope.news = response.data; // ----> NEWS : ANNOTATION NEWS
                console.log($scope.news);
                $scope.page.publisher = $scope.news.publish;
                $scope.url = $scope.news.url;
                $scope.title = $scope.news.title;
                $scope.text = $scope.news.text;


                $('.custom-control-input').attr('checked', false);
                $scope.fakeSelected = 'reset';
                $scope.radioSelected = false;
            });
        }
    };

    $scope.sendFeedback = function (value) {

        $scope.feedbackSelected = true;

        $("#alert").fadeIn();
        $("#feedback").fadeOut();

        var to_send = {
            'title': $scope.title,
            'text': $scope.text,
            'label': value
        };

        feedback.sendFb(to_send).then(function (response) {
            console.log(response)
        }, function (response) {
        });
    };

    $scope.sendAnnotation = function () {
        if (!$scope.radioSelected)
            return;

        var to_send = {
            "id": $scope.news.id,
            "label": $scope.fakeSelected
        };

        update.doUpdate(to_send).then(function (response) {
            next.goNext($scope.selectedLanguage).then(function (response) {
                $scope.news = response.data; // ----> NEWS : ANNOTATION NEWS
                console.log($scope.news);
                $scope.page.publisher = $scope.news.publish;
                $scope.url = $scope.news.url;
                $scope.title = $scope.news.title;
                $scope.text = $scope.news.text;


                $('.custom-control-input').attr('checked', false);
                $scope.fakeSelected = 'reset';
                $scope.radioSelected = false;
            });
        });
    };

    $scope.skipAnnotation = function () {
        next.goNext($scope.selectedLanguage).then(function (response) {
            $scope.news = response.data; // ----> NEWS : ANNOTATION NEWS
            console.log($scope.news);
            $scope.page.publisher = $scope.news.publish;
            $scope.url = $scope.news.url;
            $scope.title = $scope.news.title;
            $scope.text = $scope.news.text;


            $('.custom-control-input').attr('checked', false);
            $scope.fakeSelected = 'reset';
            $scope.radioSelected = false;
        });
    };

    $scope.startAnalyze = function () {
        $("#btnStartAnalyze").addClass("animated fadeOut faster");
        setTimeout(function () {
            $("#btnStartAnalyze").remove();
        }, 500);

        next.goNext($scope.selectedLanguage).then(function (response) {
            $scope.news = response.data; // ----> NEWS : ANNOTATION NEWS
            console.log($scope.news);
            $scope.page.publisher = $scope.news.publish;
            $scope.url = $scope.news.url;
            $scope.title = $scope.news.title;
            $scope.text = $scope.news.text;
            $scope.analyzeStarted = true;
        });
    };

    $('input[type=radio]').click(function (e) {
        $scope.radioSelected = true;

        // $(".fa-thumbs-up").removeClass("bounceIn");
        // setTimeout('$(".fa-thumbs-up").addClass("bounceIn")' , 50);
    });

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
}]);
