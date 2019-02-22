app.controller('annotationCtrl', ['$scope', '$http', 'crUrl', 'lang', 'annotation','alert', function ($scope, $http, crUrl, lang, annotation, alert) {

    $scope.alertLabel = ''; // STRING TO SHOW ON SUCCESS ALERT
    $scope.selectedLanguage = "en"; // DEFAULT LANGUAGE FOR MENU ON ARTICLE CHECKER
    $scope.optionLanguage = ''; // LANGUAGE ON ANNOTATION OPTION MENU
    $scope.tabSelected = 1; // 1 = AUTO - 2 = - MANUAL - 3 = DOMAIN

    $scope.loadingAnalyzeUrl = false; // FLAG FOR SPINNER ON URL ANALYZING
    $scope.analyzeOk = false; // FLAG FOR SHOW ERROR ON URL ANALYZING
    $scope.newExist = true; // FLAG FOR CHECK IF IS LAST NEWS
    $scope.isLabelSelected = false; // FLAG IF LABEL IS SELECTED
    $scope.isLangSelected = true; // FLAG IF LANGUAGE IS SELECTED
    $(".alert").hide();

    $scope.page = {
        'authors': [],
        'publisher': '',
        'url': '',
        'text': '',
        'title': ''
    };

    // FUNCTIONS DECLARATION

    function resetRadio() {
        $('.custom-control-input').prop('checked', false);
        $scope.isLabelSelected = false;
    }

    function resetLanguage() {
        $('.languageList').prop('selectedIndex', 0);
        $scope.isLangSelected = false;
    }

    function resetField() {
        $scope.page.authors = [];
        $scope.page.title = '';
        $scope.page.text = '';
        $scope.page.url = '';
        $scope.page.publisher = '';
    }



    angular.element(function () {
        lang.getLanguages().then(function (response) {
            $scope.languages = response.data;
            $scope.loading = false;
        });
    });

    $scope.newLabel = function (value) {
        $scope.isLabelSelected = true;
    };

    $scope.newLang = function (value) {
        $scope.optionLanguage = value;
        $scope.isLangSelected = true;
    };

    $scope.changeTab = function (tab) {
        if (tab === $scope.tabSelected)
            return;

        $scope.tabSelected = tab;
        resetField();
        resetRadio();
        resetLanguage();
        $scope.isLabelSelected = false;
        $scope.analyzeStarted = false;
        $scope.analyzeOk = false;
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

    $scope.changeLanguage = function (language) {
        if (language.active === 'False' || $scope.selectedLanguage === language.language) {
            return;
        } else {
            $scope.selectedLanguage = language.language;

            annotation.goNext($scope.selectedLanguage).then(function (response) {

                $scope.changeTextNews(response);

                if (response.data.hasOwnProperty('END')) {
                    $scope.newExist = false;
                    return;
                }

                resetRadio();
                resetLanguage();
                $("#btnStartAnalyze").addClass("animated fadeOut faster");

                setTimeout(function () {
                    $("#btnStartAnalyze").remove();
                }, 500);

                $scope.newExist = true;
                $scope.analyzeStarted = true;
            }, function (response) {
                alert.showAlert('Error');
            });
        }
    };

    $scope.sendAnnotation = function (label, text, tab) {

        switch (tab) {
            case 'auto':

                var to_send = {
                    "id": $scope.news.id,
                    "label": label
                };

                $scope.alertLabel = label;

                annotation.getAutoAnnotation(to_send).then(function (response) {
                    resetRadio();
                    alert.showAlert('Success');
                    annotation.goNext($scope.selectedLanguage).then(function (response) {
                        $scope.changeTextNews(response);

                        if (response.data.hasOwnProperty('END')) {
                            $scope.newExist = false;
                            // showAlert('Warning');
                            return;
                        }

                        $scope.newExist = true;
                    }, function (response) {
                        alert.showAlert('Error');
                    });
                });
                break;

            case 'manual':

                var to_send = {
                    "label": label,
                    "lang": $scope.optionLanguage,
                    "url": $scope.page.url
                };

                $scope.alertLabel = label;

                annotation.getManualAnnotation(to_send).then(function (response) {
                    alert.showAlert('Success');
                    resetRadio();
                    resetLanguage();
                    resetField();
                }, function (response) {
                    alert.showAlert('Error');
                });
                break;

            case 'domain':

                var to_send = {
                    "list_url": text,
                    "label": label,
                    "lang": $scope.optionLanguage
                };

                $scope.alertLabel = label;

                annotation.getDomainAnnotation(to_send).then(function (response) {
                    alert.showAlert('Success');
                    $scope.page.text = '';
                    resetRadio();
                    resetLanguage();
                }, function (response) {
                    alert.showAlert('Error');
                });
        }
    };

    $scope.skipAnnotation = function () {
        annotation.goNext($scope.selectedLanguage).then(function (response) {
            $scope.changeTextNews(response);
            resetRadio();
        }, function (response) {
            alert.showAlert('Error');
        });
    };

    $scope.startAnalyze = function () {
        annotation.goNext($scope.selectedLanguage).then(function (response) {
            $("#btnStartAnalyze").addClass("animated fadeOut faster");

            setTimeout(function () {
                $("#btnStartAnalyze").remove();
            }, 500);

            $scope.changeTextNews(response);
            $scope.analyzeStarted = true;
        }, function (response) {
            alert.showAlert('Error');
        });
    };

    $scope.analyzeUrl = function () {
        if (!$scope.page.url)
            return;

        $scope.loadingAnalyzeUrl = true;

        crUrl.analyzeUrl($scope.page.url).then(function (response) {
            $scope.changeTextNews(response);
            console.log($scope.page);
            $scope.analyzeOk = true;
            $scope.loadingAnalyzeUrl = false;
        }, function (response) {
            alert.showAlert('Error');
            resetField();
            $scope.analyzeOk = false;
            $scope.loadingAnalyzeUrl = false;
        });
    };
}]);
