app.factory('errorCode',function () {
    return {
        errorCode: function(code) {
            switch (code) {
                case 400:
                case 405:
                    return "Invalid input";
                case 500:
                case 0:
                case -1:
                    return "Error occured on the service side";
            }
        }
    };
});

app.factory('crUrl',['$http', function ($http) {
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
