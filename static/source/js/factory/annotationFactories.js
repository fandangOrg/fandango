app.factory('annotation', ['$http', function ($http) {
    return {
        goNext: function (language, author) {
            return $http.post(base + "/next_news?lang=" + language + "&author=" + author);
        },
        getAutoAnnotation: function (label) {
            return $http.post(base + "/new_annotation", label);
        },
        getManualAnnotation: function (to_send) {
            return $http.post(base + "/new_doc_annotation", to_send);
        },
        getDomainAnnotation: function (to_send) {
            return $http.post(base + "/domain_annotation", to_send);
        },
        getCountAnnotation: function (to_send) {
            return $http.post(base + "/counter_annotations", to_send);
        }
    };
}]);
