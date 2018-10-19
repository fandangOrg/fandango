app.controller('indexCtrl', function ($scope, $http, $document, errorCode, call) {

    $scope.value = "";

    var to_send = {
        'title':'ciao',
        'text':'prova',
        'source':''
    };

   call.getCall(to_send).then(function (response) {
       $scope.value = response.data;
       console.log(response)
   }, function (response) {
       console.log(response)
   });
});
