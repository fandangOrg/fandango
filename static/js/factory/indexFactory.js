app.factory('errorCode',function () {
    return {
        errorCode: function(code) {
            switch (code) {
                case 400:
                case 405:
                    return "Invalid input";
                case 500:
                case 0:
                    return "Error occured on the service side";
                case -1:
                    return "Error occured on the server side";
            }
        }
    };
});

app.factory('call',['$http', function ($http) {
    return {
        getCall: function (to_send) {
            return $http.post(base + "/analyzer",to_send);
        }
    };
}]);