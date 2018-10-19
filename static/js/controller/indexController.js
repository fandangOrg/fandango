app.controller('indexCtrl', function ($scope, $http, $document, errorCode, call) {

    $scope.send = function () {

        var to_send = {
            'title':$scope.title,
            'text':$scope.text,
            'source':''
        };

        console.log(to_send);

        call.getCall(to_send).then(function (response) {
            $scope.value = response.data[0];
            console.log($scope.value);
            $scope.fakeValue = parseInt($scope.value.FAKE * 100);
            $scope.realValue = parseInt($scope.value.REAL * 100);

            var myConfig8 = {
                "type":"gauge",
                "scale-r":{
                    "aperture":200,
                    "values":"0:100:20",
                    "center":{
                        "size":5,
                        "background-color":"#66CCFF #FFCCFF",
                        "border-color":"none"
                    },
                    "ring":{
                        "size":10,
                        "rules":[
                            {
                                "rule":"%v >= 0 && %v <= 20",
                                "background-color":"blue"
                            },
                            {
                                "rule":"%v >= 20 && %v <= 40",
                                "background-color":"green"
                            },
                            {
                                "rule":"%v >= 40 && %v <= 60",
                                "background-color":"yellow"
                            },
                            {
                                "rule":"%v >= 60 && %v <= 80",
                                "background-color":"orange"
                            },
                            {
                                "rule":"%v >= 80 && %v <=100",
                                "background-color":"red"
                            }
                        ]
                    },
                    "labels":["0 %","20 %","40 %","60 %","80 %","100 %"],  //Scale Labels
                    "item":{  //Scale Label Styling
                        "font-color":"purple",
                        "font-family":"Georgia, serif",
                        "font-size":12,
                        "font-weight":"bold",   //or "normal"
                        "font-style":"normal",   //or "italic"
                        "offset-r":0,
                        "angle":"auto"
                    }
                },
                "plot":{
                    "csize":"5%",
                    "size":"100%",
                    "background-color":"#000000"
                },
                "series":[
                    {"values":[$scope.fakeValue]}
                ]
            };

            zingchart.render({
                id : 'myChart',
                data : myConfig8,
                height : "100%",
                width: "100%"
            });

        }, function (response) {
            console.log(response)
        });
    }
});
