app.controller('indexCtrl', function ($scope, $http, $document, errorCode, call) {

    $scope.fakenessDone = false;
    $scope.loadingFakeness = false;
    angular.element(function () {
        $scope.loading = false;
    });

    $scope.send = function () {

        $('#gaugeFakeness').removeClass('animated fadeIn');
        zingchart.exec('gaugeFakeness', 'destroy');

        if (!$scope.title || !$scope.source || !$scope.text)
            return false;

        var to_send = {
            'title': $scope.title,
            'text': $scope.text,
            'source': ''
        };

        $scope.loadingFakeness = true;

        call.getCall(to_send).then(function (response) {
            $scope.value = response.data[0];
            $scope.fakeValue = parseInt($scope.value.FAKE * 100);
            $scope.realValue = parseInt($scope.value.REAL * 100);

            zingchart.render({
                id: 'gaugeFakeness',
                data: getConfig($scope.fakeValue),
                height: "100%",
                width: "100%"
            });

            $scope.loadingFakeness = false;
            $('#gaugeFakeness').addClass('animated fadeIn');

        }, function (response) {
            $scope.loadingFakeness = false;
            console.log(response)
        });
    }
});
