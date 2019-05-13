app.factory('fakeness', ['$http', function ($http) {
    return {
        getFakeness: function (to_send) {
            return $http.post(base + "/analyzer", to_send);
        },
        getInfoScore: function (to_send) {
            return $http.get(base + "/info_score?label=" + to_send)
        },
        getImageFakeness: function (media) {
            return $http.get(base + "/ping_image?id=" + media)
        },
        getVideoFakeness: function (media) {
            return $http.get(base + "/ping_image?id=" + media)
        },
        getAuthorFakeness: function (score) {
            switch (true) {
                case (score < 20):
                    return 'text-red';
                case (score < 40):
                    return 'text-warning';
                case (score < 80):
                    return 'text-yellow';
                case (score > 80):
                    return 'text-green';
            }
        },
        getFakenessColor: function (value) {
            switch (true) {
                case value <= 25:
                    return 'bg-danger';
                case value <= 50:
                    return 'bg-warning';
                case value <= 75:
                    return 'bg-yellow';
                default:
                    return 'bg-success'
            }
        }
    };
}]);

app.factory('feedback', ['$http', function ($http) {
    return {
        sendFb: function (to_send) {
            return $http.post(base + "/feedback", to_send);
        }
    };
}]);

app.factory('claim', ['$http', function ($http) {
    return {
        getClaim: function (to_send) {
            return $http.post(base + "/claim", to_send);
        },
        saveClaim: function (to_send) {
            return $http.post(base + "/new_claim_annotated", to_send);
        },
        getFakeness: function (level, listLevel) {
            if (listLevel.includes(level))
                return 'text-green';
            else if (level === 'barely-true')
                return 'text-blue';
            else
                return 'text-red';
        }
    };
}]);

app.factory('chart', function () {
    return {
        renderChart: function (value) {
            zingchart.render({
                id: 'gaugeFakeness',
                data: {
                    "type": "gauge",
                    "background-color": "#f7fafc",
                    "scale-r": {
                        "markers": [
                            {
                                "type": "line",
                                "range": [50],
                                "line-color": "grey",
                                "line-width": 2,
                                "line-style": "dashed",
                                "alpha": 1
                            }
                        ],
                        "aperture": 200,
                        "values": "0:100:25",
                        "center": {
                            "size": 5,
                            "background-color": "#66CCFF #FFCCFF",
                            "border-color": "none"
                        },
                        "ring": {
                            "size": 10,
                            "rules": [
                                {
                                    "rule": "%v >= 0 && %v <= 25",
                                    "background-color": "green"
                                },
                                {
                                    "rule": "%v >= 25 && %v <= 50",
                                    "background-color": "yellow"
                                },
                                {
                                    "rule": "%v >= 50 && %v <= 75",
                                    "background-color": "orange"
                                },
                                {
                                    "rule": "%v >= 75 && %v <=100",
                                    "background-color": "red"
                                }
                            ]
                        },
                        "labels": ["REAL", "", "", "", "FAKE"],  //Scale Labels
                        "item": {  //Scale Label Styling
                            "font-color": "black",
                            "font-family": "Open Sans, serif",
                            "font-size": 13,
                            "font-weight": "bold",   //or "normal"
                            "font-style": "normal",   //or "italic"
                            "offset-r": 0,
                            "angle": "auto"
                        }
                    },
                    gui: {
                        contextMenu: {
                            empty: true
                        }
                    },
                    "plot": {
                        tooltip: {
                            visible: false
                        },
                        "csize": "5%",
                        "size": "100%",
                        "background-color": "#000000"
                    },
                    "series": [
                        {"values": [value]}
                    ]
                },
                height: "100%",
                width: "100%"
            });
        }
    };
});
