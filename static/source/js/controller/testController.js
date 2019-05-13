app.controller('testCtrl', ['$scope', '$http', 'lang', '$sce', function ($scope, $http, lang, $sce) {

    $scope.selectedLanguage = "en";
    $scope.full_response = {};

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

    angular.element(function () {
        lang.getLanguages().then(function (response) {
            $scope.languages = response.data;
            //TODO
            $scope.nextNews();
        });
    });

    $scope.nextNews = function () {
        annotation.goNext($scope.selectedLanguage).then(function (response) {

            $scope.changeTextNews(response);

            // CONTROLLO SE ESISTE UNA NEWS PER LA LINGUA SELEZIONATA
            if (response.data.hasOwnProperty('END')) {
                console.log("END");
            }

            $scope.loading = false;
        }, function (response) {
        });
    };

    $scope.changeLanguage = function (language) {
        if (language.active === 'False' || $scope.selectedLanguage === language.language) {
            return;
        } else {
            $scope.selectedLanguage = language.language;
            $scope.nextNews();
        }
    };

    $scope.changeTextNews = function (response) {
        $scope.news = response.data; // ----> NEWS : ANNOTATION NEWS
        console.log($scope.news);
        $scope.page.authors = $scope.news.authors;
        $scope.page.title = $scope.news.title;
        $scope.page.text = $scope.news.text;
        $scope.page.url = $scope.news.url;
        $scope.page.publisher = $scope.news.source_domain;
    };

    $scope.embedVideo = function (urlVideo) {
        urlVideo = urlVideo.replace("watch?v=", "embed/");
        return $sce.trustAsResourceUrl(urlVideo);
    };
}]);
