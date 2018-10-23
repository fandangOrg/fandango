var app = angular.module('app', []);
var base = "http://192.168.1.49:9800/fandango/v0.1/fakeness";

// var app = angular.module('app', []);
// var base = "http://0.0.0.0:9800/fandango/v0.1/fakeness";

// CONFIG VARIABLES
function getConfig(value) {
    return {
        "type": "gauge",
        "scale-r": {
            "aperture": 200,
            "values": "0:100:20",
            "center": {
                "size": 5,
                "background-color": "#66CCFF #FFCCFF",
                "border-color": "none"
            },
            "ring": {
                "size": 10,
                "rules": [
                    {
                        "rule": "%v >= 0 && %v <= 20",
                        "background-color": "blue"
                    },
                    {
                        "rule": "%v >= 20 && %v <= 40",
                        "background-color": "green"
                    },
                    {
                        "rule": "%v >= 40 && %v <= 60",
                        "background-color": "yellow"
                    },
                    {
                        "rule": "%v >= 60 && %v <= 80",
                        "background-color": "orange"
                    },
                    {
                        "rule": "%v >= 80 && %v <=100",
                        "background-color": "red"
                    }
                ]
            },
            "labels": ["0 %", "20 %", "40 %", "60 %", "80 %", "100 %"],  //Scale Labels
            "item": {  //Scale Label Styling
                "font-color": "black",
                "font-family": "Open Sans, serif",
                "font-size": 12,
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
            "csize": "5%",
            "size": "100%",
            "background-color": "#000000"
        },
        "series": [
            {"values": [value]}
        ]
    };
}
