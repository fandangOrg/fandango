app.controller('indexCtrl', function ($scope, $http, $document, errorCode, call) {

    $scope.fakenessDone = false;

    angular.element(function () {
        $scope.loading = false;
    });

    $scope.send = function () {
        var to_send = {
            'title':$scope.title,
            'text':$scope.text,
            'source':''
        };

        call.getCall(to_send).then(function (response) {
            $scope.value = response.data[0];
            $scope.fakeValue = parseInt($scope.value.FAKE * 100);
            $scope.realValue = parseInt($scope.value.REAL * 100);

            zingchart.render({
                id : 'gaugeFakeness',
                data : getConfig($scope.fakeValue),
                height : "100%",
                width: "100%"
            });

            $scope.fakenessDone = true;

        }, function (response) {
            $scope.fakenessDone = false;
            console.log(response)
        });
    }
});
