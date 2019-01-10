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

app.factory('fakeness',['$http', function ($http) {
    return {
        getFakeness: function (to_send) {
            return $http.post(base + "/analyzer",to_send);
        }
    };
}]);

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

app.factory('update',['$http', function ($http) {
    return {
        doUpdate: function (label) {
            return $http.post(base + "/new_annotation",label);
        }
    };
}]);

app.factory('next',['$http', function ($http) {
    return {
        goNext: function (language) {
            return $http.post(base + "/next_news?lang="+language);
        }
    };
}]);


app.factory('manual',['$http', function ($http) {
    return {
        manualAnnotation: function (to_send) {
            return $http.post(base + "/new_document_annotation", to_send);
        }
    };
}]);

app.factory('domain',['$http', function ($http) {
    return {
        domainAnnotation: function (to_send) {
            return $http.post(base + "/domain_annotation", to_send);
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