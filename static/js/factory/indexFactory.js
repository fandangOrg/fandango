angular.module('app').factory('errorCode',function () {
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