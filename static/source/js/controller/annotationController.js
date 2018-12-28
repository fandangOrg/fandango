app.controller('annotationCtrl', ['$scope', '$http', '$document', 'errorCode', 'url', 'fakeness', 'feedback', function ($scope, $http, $document, errorCode, url, fakeness, feedback) {

    $scope.fakenessDone = false;
    $scope.loadingFakeness = false;
    $scope.loadingAnalyzeUrl = false;
    $scope.feedbackSelected = false;
    $scope.language = "uk";
    $scope.categories = ['Category 1','Category 2','Category 3'];

    angular.element(function () {
        $scope.loading = false;
        $('[data-toggle="tooltip"]').tooltip();
    });

    $scope.changeLanguage = function (language) {
        $scope.language = language;
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

        console.log(to_send);

        feedback.sendFb(to_send).then(function (response) {
            console.log(response)
        }, function (response) {
        });
    };

    $scope.sendAnnotation = function () {

        // $(".fa-thumbs-up").removeClass(" bounceIn");
        // setTimeout('$(".fa-thumbs-up").addClass(" bounceIn")' , 500);

        $('.custom-control-input').attr('checked',false);
        $scope.fakeSelected = 'reset';
    };

    $scope.skipAnnotation = function () {
        $('.custom-control-input').attr('checked',false);
        $scope.fakeSelected = 'reset';
    };

    $scope.startAnalyze = function () {
        $("#btnStartAnalyze").addClass("animated fadeOut faster");
        $scope.analyzeStarted = true;
    };

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
