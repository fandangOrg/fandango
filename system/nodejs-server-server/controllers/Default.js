'use strict';

var utils = require('../utils/writer.js');
var Default = require('../service/DefaultService');

module.exports.findFact = function findFact (req, res, next) {
  var info = req.swagger.params['info'].value;
  Default.findFact(info)
    .then(function (response) {
      utils.writeJson(res, response);
    })
    .catch(function (response) {
      utils.writeJson(res, response);
    });
};

module.exports.findSimilarArticles = function findSimilarArticles (req, res, next) {
  var info = req.swagger.params['info'].value;
  Default.findSimilarArticles(info)
    .then(function (response) {
      utils.writeJson(res, response);
    })
    .catch(function (response) {
      utils.writeJson(res, response);
    });
};

module.exports.findSimilarClaims = function findSimilarClaims (req, res, next) {
  var info = req.swagger.params['info'].value;
  Default.findSimilarClaims(info)
    .then(function (response) {
      utils.writeJson(res, response);
    })
    .catch(function (response) {
      utils.writeJson(res, response);
    });
};
