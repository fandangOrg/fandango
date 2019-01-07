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

app.factory('fakeness',['$http', function ($http) {
    return {
        getFakeness: function (to_send) {
            return $http.post(base + "/analyzer",to_send);
        }
    };
}]);

app.factory('url',['$http', function ($http) {
    return {
        analyzeUrl: function (to_send) {
            return $http.post(base + "/cr_url?url="+to_send);
        }
    };
}]);

app.factory('lang',['$http', function ($http) {
    return {
        getLanguages: function () {
            return $http.get(base + "/get_languages");
        }
    };
}]);


app.factory('feedback',['$http', function ($http) {
    return {
        sendFb: function (to_send) {
            return $http.post(base + "/feedback", to_send);
        }
    };
}]);

app.factory('claim',['$http', function ($http) {
    return {
        getClaim: function (to_send) {
            return $http.post(base + "/claim", to_send);
        }
    };
}]);