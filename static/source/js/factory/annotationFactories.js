app.factory('annotation',['$http', function ($http) {
    return {
        goNext: function (language) {
            return $http.post(base + "/next_news?lang="+language);
        },
        getAutoAnnotation: function (label) {
            return $http.post(base + "/new_annotation",label);
        },
        getManualAnnotation: function (to_send) {
            return $http.post(base + "/new_doc_annotation", to_send);
        },
        getDomainAnnotation: function (to_send) {
            return $http.post(base + "/domain_annotation", to_send);
        }
    };
}]);
