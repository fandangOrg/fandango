annotation.factory('errorCode',function () {
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

annotation.factory('crUrl',['$http', function ($http) {
    return {
        analyzeUrl: function (to_send) {
            return $http.post(base + "/cr_url?url="+to_send);
        }
    };
}]);

annotation.factory('lang',['$http', function ($http) {
    return {
        getLanguages: function () {
            return $http.get(base + "/get_languages");
        }
    };
}]);

annotation.factory('update',['$http', function ($http) {
    return {
        doUpdate: function (label) {
            return $http.post(base + "/new_annotation",label);
        }
    };
}]);

annotation.factory('next',['$http', function ($http) {
    return {
        goNext: function (language) {
            return $http.post(base + "/next_news?lang="+language);
        }
    };
}]);


annotation.factory('manual',['$http', function ($http) {
    return {
        manualAnnotation: function (to_send) {
            return $http.post(base + "/new_document_annotation", to_send);
        }
    };
}]);

annotation.factory('domain',['$http', function ($http) {
    return {
        domainAnnotation: function (to_send) {
            return $http.post(base + "/domain_annotation", to_send);
        }
    };
}]);