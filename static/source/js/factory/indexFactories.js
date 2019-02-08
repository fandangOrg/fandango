app.factory('fakeness',['$http', function ($http) {
    return {
        getFakeness: function (to_send) {
            return $http.post(base + "/analyzer",to_send);
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
        },
        saveClaim: function (to_send) {
            return $http.post(base + "/new_claim_annotated", to_send);
        }
    };
}]);
