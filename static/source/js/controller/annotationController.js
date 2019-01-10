app.controller('annotationCtrl', ['$rootScope', '$scope', '$http', '$document','crUrl', 'lang', 'next', 'update', '$state', 'manual','domain', function ($rootScope, $scope, $http, $document, crUrl, lang, next, update, $state, manual, domain) {


    $scope.loadingAnalyzeUrl = false;
    $scope.selectedLanguage = "en";
    $scope.$state = $state;
    $scope.analyzeOk = false;
    $scope.newExist = true;

    $scope.page = {
        'author': '',
        'publisher': '',
        'url': '',
        'text': '',
        'title': ''
    };

    // RESET VALORI QUANDO SI CAMBIA TAB
    $(window).on('hashchange', function (e) {
        $scope.page.author = '';
        $scope.page.title = '';
        $scope.page.text = '';
        $scope.page.url = '';
        $scope.page.publisher = '';

        $scope.analyzeStarted = false;
        $scope.analyzeOk = false;
    });

    $scope.changeTextNews = function (response) {
        $scope.news = response.data; // ----> NEWS : ANNOTATION NEWS
        console.log($scope.news);
        $scope.page.publisher = $scope.news.source_domain;
        $scope.page.url = $scope.news.url;
        $scope.page.title = $scope.news.title;
        $scope.page.text = $scope.news.text;
        $scope.page.author = $scope.news.authors;

        $('.custom-control-input').attr('checked', false);

    };

    // $scope.categories = ['Category 1','Category 2','Category 3'];
    angular.element(function () {
        $("[rel=tooltip]").tooltip({placement: 'left'});
        lang.getLanguages().then(function (response) {
            $scope.languages = response.data;
            $scope.loading = false;
        });
    });

    $scope.changeLanguage = function (language, tab) {
        if (language.active === 'False') {
            return;
        } else {
            $scope.selectedLanguage = language.language;

            if(tab === 'manual')
                return;


            next.goNext($scope.selectedLanguage).then(function (response) {

                $scope.changeTextNews(response);

                if (response.data.hasOwnProperty('END')) {
                    $scope.newExist = false;
                    return;
                }


                $('.custom-control-input').attr('checked', false);
                $scope.fakeSelected = undefined;
                $("#btnStartAnalyze").addClass("animated fadeOut faster");

                setTimeout(function () {
                    $("#btnStartAnalyze").remove();
                }, 500);

                $scope.newExist = true;
                $scope.analyzeStarted = true;
            });
        }
    };

    $scope.sendDomainAnnotation = function (response) {
        if (!response)
            return;

        var to_send = {
            "list_url": response,
        };

        domain.domainAnnotation(to_send).then(function (response) {
            console.log(response)
        })
    };

    $scope.sendAnnotation = function (response) {
        if (!response)
            return;

        $scope.fakeSelected = response;

        var to_send = {
            "id": $scope.news.id,
            "label": $scope.fakeSelected
        };

        update.doUpdate(to_send).then(function (response) {
            next.goNext($scope.selectedLanguage).then(function (response) {
                $scope.changeTextNews(response);

                $scope.fakeSelected = undefined;
            });
        });
    };

    $scope.sendManualAnnotation = function (response) {

        $scope.fakeSelected = response;

        var to_send = {
            "label": $scope.fakeSelected,
            "lang": $scope.selectedLanguage,
            "url": $scope.page.url
        };

        console.log(to_send);

        manual.manualAnnotation(to_send).then(function (response) {
            console.log(response);

            $('.custom-control-input').attr('checked', false);
            $scope.fakeSelected = undefined;

        });
    };

    $scope.skipAnnotation = function () {
        next.goNext($scope.selectedLanguage).then(function (response) {
            $scope.changeTextNews(response);

            $('.custom-control-input').attr('checked', false);
            $scope.fakeSelected = undefined;
        });
    };

    $scope.startAnalyze = function () {
        $("#btnStartAnalyze").addClass("animated fadeOut faster");
        setTimeout(function () {
            $("#btnStartAnalyze").remove();
        }, 500);
        next.goNext($scope.selectedLanguage).then(function (response) {
            $scope.changeTextNews(response);

            $scope.analyzeStarted = true;
        });
    };

    $scope.analyzeUrl = function (url) {
        if (!url)
            return;

        $scope.loadingAnalyzeUrl = true;
        $scope.page.url = url;
        var to_send = $scope.page.url;

        crUrl.analyzeUrl(to_send).then(function (response) {
            $scope.changeTextNews(response);

            console.log($scope.page);
            $scope.analyzeOk = true;
            $scope.loadingAnalyzeUrl = false;
        }, function (response) {
            $scope.analyzeOk = false;
            $scope.loadingAnalyzeUrl = false;
        });
    };
}]);
