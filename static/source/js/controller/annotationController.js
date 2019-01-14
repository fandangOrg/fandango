app.controller('annotationCtrl', ['$scope', '$http', 'crUrl', 'lang', 'annotation', function ($scope, $http, crUrl, lang, annotation) {

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
        'author': '',
        'publisher': '',
        'url': '',
        'text': '',
        'title': ''
    };

    $scope.newLabel = function (value) {
        $scope.isLabelSelected = true;
    };

    $scope.newLang = function (value) {
        $scope.optionLanguage = value;
        $scope.isLangSelected = true;
    };

    angular.element(function () {
        lang.getLanguages().then(function (response) {
            $scope.languages = response.data;
            $scope.loading = false;
        });
    });

    function resetRadio() {
        $('.custom-control-input').prop('checked', false);
        $scope.isLabelSelected = false;
    }

    function resetLanguage() {
        $('.languageList').prop('selectedIndex', 0);
        $scope.isLangSelected = false;
    }

    function showAlert(esito) {
        $("#alert" + esito).fadeTo(1500, 500).slideUp(500, function () {
            $(".alert").slideUp(500);
        });
    }

    $scope.changeTab = function (tab) {
        if (tab === $scope.tabSelected)
            return;

        $scope.tabSelected = tab;
        $scope.page.author = '';
        $scope.page.title = '';
        $scope.page.text = '';
        $scope.page.url = '';
        $scope.page.publisher = '';
        resetRadio();
        resetLanguage();
        $scope.isLabelSelected = false;
        $scope.analyzeStarted = false;
        $scope.analyzeOk = false;
    };

    $scope.changeTextNews = function (response) {
        $scope.news = response.data; // ----> NEWS : ANNOTATION NEWS
        console.log($scope.news);
        $scope.page.author = $scope.news.authors;
        $scope.page.title = $scope.news.title;
        $scope.page.text = $scope.news.text;
        $scope.page.url = $scope.news.url;
        $scope.page.publisher = $scope.news.source_domain;
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
                showAlert('Error');
            });
        }
    };

    $scope.sendAnnotation = function (label, text, tab) {

        switch (tab) {
            case 'auto':
                if (!$scope.isLabelSelected)
                    return;

                var to_send = {
                    "id": $scope.news.id,
                    "label": label
                };

                $scope.alertLabel = label;

                annotation.getAutoAnnotation(to_send).then(function (response) {
                    resetRadio();
                    showAlert('Success');
                    annotation.goNext($scope.selectedLanguage).then(function (response) {
                        $scope.changeTextNews(response);

                        if (response.data.hasOwnProperty('END')) {
                            $scope.newExist = false;
                            return;
                        }

                        $scope.newExist = true;
                    }, function (response) {
                        showAlert('Error');
                    });
                });
                break;

            case 'manual':
                if (!$scope.isLabelSelected || !$scope.isLangSelected) // TEXT PER MANUAL CONTIENE LA LINGUA INVECE CHE IL CONTENUTO DELLA NEWS
                    return;

                var to_send = {
                    "label": label,
                    "lang": $scope.optionLanguage,
                    "url": $scope.page.url
                };

                $scope.alertLabel = label;

                annotation.getManualAnnotation(to_send).then(function (response) {
                    showAlert('Success');
                    resetRadio();
                    resetLanguage();
                    console.log(response);
                }, function (response) {
                    showAlert('Error');
                });
                break;

            case 'domain':
                if (!text || !$scope.isLabelSelected || !$scope.isLangSelected)
                    return;

                var to_send = {
                    "list_url": text,
                    "label": label,
                    "lang": $scope.optionLanguage
                };

                $scope.alertLabel = label;

                annotation.getDomainAnnotation(to_send).then(function (response) {
                    showAlert('Success');
                    $scope.page.text = '';
                    resetRadio();
                    resetLanguage();
                    console.log(response);
                }, function (response) {
                    showAlert('Error');
                });
        }
    };

    $scope.skipAnnotation = function () {
        annotation.goNext($scope.selectedLanguage).then(function (response) {
            $scope.changeTextNews(response);
            resetRadio();
        }, function (response) {
            showAlert('Error');
        });
    };

    $scope.startAnalyze = function () {
        $("#btnStartAnalyze").addClass("animated fadeOut faster");
        setTimeout(function () {
            $("#btnStartAnalyze").remove();
        }, 500);
        annotation.goNext($scope.selectedLanguage).then(function (response) {
            $scope.changeTextNews(response);
            $scope.analyzeStarted = true;
        }, function (response) {
            showAlert('Error');
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
            showAlert('Error');
            $scope.analyzeOk = false;
            $scope.loadingAnalyzeUrl = false;
        });
    };
}]);
