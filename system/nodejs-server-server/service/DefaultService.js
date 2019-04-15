'use strict';


/**
 * Find Facts similar to text input, specific category, and similar to optional topics
 * Response will return top 5 Fact documents closest to user provided criteria. A Fact is an Open Data creative work containing data, published by a recognized institution to make information available publicly.
 *
 * info Fact_Request_Interface 
 * returns List
 **/
exports.findFact = function(info) {
  return new Promise(function(resolve, reject) {
    var examples = {};
    examples['application/json'] = [ {
  "topics" : [ "topics", "topics" ],
  "text" : "text",
  "category" : "category",
  "results" : [ {
    "fact" : {
      "datePublished" : "datePublished",
      "identifier" : 0,
      "dateCreated" : "dateCreated",
      "temporalCoverageStart" : "temporalCoverageStart",
      "dateMtemporalCoverageEnd" : "dateMtemporalCoverageEnd",
      "mentions" : [ 6, 6 ],
      "name" : "name",
      "about" : [ "about", "about" ],
      "dateModified" : "dateModified",
      "text" : "text",
      "spatialCoverage" : "spatialCoverage",
      "url" : "url"
    }
  }, {
    "fact" : {
      "datePublished" : "datePublished",
      "identifier" : 0,
      "dateCreated" : "dateCreated",
      "temporalCoverageStart" : "temporalCoverageStart",
      "dateMtemporalCoverageEnd" : "dateMtemporalCoverageEnd",
      "mentions" : [ 6, 6 ],
      "name" : "name",
      "about" : [ "about", "about" ],
      "dateModified" : "dateModified",
      "text" : "text",
      "spatialCoverage" : "spatialCoverage",
      "url" : "url"
    }
  } ]
}, {
  "topics" : [ "topics", "topics" ],
  "text" : "text",
  "category" : "category",
  "results" : [ {
    "fact" : {
      "datePublished" : "datePublished",
      "identifier" : 0,
      "dateCreated" : "dateCreated",
      "temporalCoverageStart" : "temporalCoverageStart",
      "dateMtemporalCoverageEnd" : "dateMtemporalCoverageEnd",
      "mentions" : [ 6, 6 ],
      "name" : "name",
      "about" : [ "about", "about" ],
      "dateModified" : "dateModified",
      "text" : "text",
      "spatialCoverage" : "spatialCoverage",
      "url" : "url"
    }
  }, {
    "fact" : {
      "datePublished" : "datePublished",
      "identifier" : 0,
      "dateCreated" : "dateCreated",
      "temporalCoverageStart" : "temporalCoverageStart",
      "dateMtemporalCoverageEnd" : "dateMtemporalCoverageEnd",
      "mentions" : [ 6, 6 ],
      "name" : "name",
      "about" : [ "about", "about" ],
      "dateModified" : "dateModified",
      "text" : "text",
      "spatialCoverage" : "spatialCoverage",
      "url" : "url"
    }
  } ]
} ];
    if (Object.keys(examples).length > 0) {
      resolve(examples[Object.keys(examples)[0]]);
    } else {
      resolve();
    }
  });
}


/**
 * Find articles similar to an existing article
 * Response will return top 5 Articles closest to user provided criteria.
 *
 * info Article_Request_Interface 
 * returns List
 **/
exports.findSimilarArticles = function(info) {
  return new Promise(function(resolve, reject) {
    var examples = {};
    examples['application/json'] = [ {
  "identifier" : "identifier",
  "results" : [ {
    "article" : {
      "identifier" : 0,
      "articleBody" : "articleBody",
      "author" : [ 6, 6 ],
      "about" : [ "about", "about" ],
      "dateModified" : "dateModified",
      "calculatedRatingDetail" : {
        "authorRating" : 5.962133916683182377482808078639209270477294921875,
        "publishRating" : 1.46581298050294517310021547018550336360931396484375
      },
      "datePublished" : "datePublished",
      "calculatedRating" : 2.3021358869347654518833223846741020679473876953125,
      "contains" : [ 5, 5 ],
      "dateCreated" : "dateCreated",
      "mentions" : [ 5, 5 ],
      "publisher" : [ 1, 1 ],
      "headline" : "headline"
    }
  }, {
    "article" : {
      "identifier" : 0,
      "articleBody" : "articleBody",
      "author" : [ 6, 6 ],
      "about" : [ "about", "about" ],
      "dateModified" : "dateModified",
      "calculatedRatingDetail" : {
        "authorRating" : 5.962133916683182377482808078639209270477294921875,
        "publishRating" : 1.46581298050294517310021547018550336360931396484375
      },
      "datePublished" : "datePublished",
      "calculatedRating" : 2.3021358869347654518833223846741020679473876953125,
      "contains" : [ 5, 5 ],
      "dateCreated" : "dateCreated",
      "mentions" : [ 5, 5 ],
      "publisher" : [ 1, 1 ],
      "headline" : "headline"
    }
  } ]
}, {
  "identifier" : "identifier",
  "results" : [ {
    "article" : {
      "identifier" : 0,
      "articleBody" : "articleBody",
      "author" : [ 6, 6 ],
      "about" : [ "about", "about" ],
      "dateModified" : "dateModified",
      "calculatedRatingDetail" : {
        "authorRating" : 5.962133916683182377482808078639209270477294921875,
        "publishRating" : 1.46581298050294517310021547018550336360931396484375
      },
      "datePublished" : "datePublished",
      "calculatedRating" : 2.3021358869347654518833223846741020679473876953125,
      "contains" : [ 5, 5 ],
      "dateCreated" : "dateCreated",
      "mentions" : [ 5, 5 ],
      "publisher" : [ 1, 1 ],
      "headline" : "headline"
    }
  }, {
    "article" : {
      "identifier" : 0,
      "articleBody" : "articleBody",
      "author" : [ 6, 6 ],
      "about" : [ "about", "about" ],
      "dateModified" : "dateModified",
      "calculatedRatingDetail" : {
        "authorRating" : 5.962133916683182377482808078639209270477294921875,
        "publishRating" : 1.46581298050294517310021547018550336360931396484375
      },
      "datePublished" : "datePublished",
      "calculatedRating" : 2.3021358869347654518833223846741020679473876953125,
      "contains" : [ 5, 5 ],
      "dateCreated" : "dateCreated",
      "mentions" : [ 5, 5 ],
      "publisher" : [ 1, 1 ],
      "headline" : "headline"
    }
  } ]
} ];
    if (Object.keys(examples).length > 0) {
      resolve(examples[Object.keys(examples)[0]]);
    } else {
      resolve();
    }
  });
}


/**
 * Find claims similar to existing claim, and similar to optional topics
 * Response will return top 5 Claims closest to user provided criteria. Each claim in result will contain the claim itself, and a list of all claim reviews of that claim.
 *
 * info Claim_Request_Interface 
 * returns List
 **/
exports.findSimilarClaims = function(info) {
  return new Promise(function(resolve, reject) {
    var examples = {};
    examples['application/json'] = [ {
  "identifier" : "identifier",
  "topics" : [ "topics", "topics" ],
  "results" : [ {
    "claimReviews" : [ {
      "datePublished" : "datePublished",
      "identifier" : 3,
      "reviewAspect" : "reviewAspect",
      "claimReviewed" : "claimReviewed",
      "dateCreated" : "dateCreated",
      "references" : [ 7, 7 ],
      "reviewBody" : "reviewBody",
      "itemReviewed" : 4,
      "dateModified" : "dateModified",
      "aggregateRating" : 2.027123023002321833274663731572218239307403564453125
    }, {
      "datePublished" : "datePublished",
      "identifier" : 3,
      "reviewAspect" : "reviewAspect",
      "claimReviewed" : "claimReviewed",
      "dateCreated" : "dateCreated",
      "references" : [ 7, 7 ],
      "reviewBody" : "reviewBody",
      "itemReviewed" : 4,
      "dateModified" : "dateModified",
      "aggregateRating" : 2.027123023002321833274663731572218239307403564453125
    } ],
    "claim" : {
      "calculatedRating" : 6.02745618307040320615897144307382404804229736328125,
      "datePublished" : "datePublished",
      "firstAppearance" : 5,
      "identifier" : 2.3021358869347654518833223846741020679473876953125,
      "appearance" : [ 0, 0 ],
      "dateCreated" : "dateCreated",
      "mentions" : [ 7, 7 ],
      "about" : [ "about", "about" ],
      "calculatedRatingDetail" : {
        "authorRating" : 5.962133916683182377482808078639209270477294921875,
        "publishRating" : 1.46581298050294517310021547018550336360931396484375
      },
      "dateModified" : "dateModified",
      "text" : "text",
      "possiblyRelatesTo" : [ 9, 9 ]
    }
  }, {
    "claimReviews" : [ {
      "datePublished" : "datePublished",
      "identifier" : 3,
      "reviewAspect" : "reviewAspect",
      "claimReviewed" : "claimReviewed",
      "dateCreated" : "dateCreated",
      "references" : [ 7, 7 ],
      "reviewBody" : "reviewBody",
      "itemReviewed" : 4,
      "dateModified" : "dateModified",
      "aggregateRating" : 2.027123023002321833274663731572218239307403564453125
    }, {
      "datePublished" : "datePublished",
      "identifier" : 3,
      "reviewAspect" : "reviewAspect",
      "claimReviewed" : "claimReviewed",
      "dateCreated" : "dateCreated",
      "references" : [ 7, 7 ],
      "reviewBody" : "reviewBody",
      "itemReviewed" : 4,
      "dateModified" : "dateModified",
      "aggregateRating" : 2.027123023002321833274663731572218239307403564453125
    } ],
    "claim" : {
      "calculatedRating" : 6.02745618307040320615897144307382404804229736328125,
      "datePublished" : "datePublished",
      "firstAppearance" : 5,
      "identifier" : 2.3021358869347654518833223846741020679473876953125,
      "appearance" : [ 0, 0 ],
      "dateCreated" : "dateCreated",
      "mentions" : [ 7, 7 ],
      "about" : [ "about", "about" ],
      "calculatedRatingDetail" : {
        "authorRating" : 5.962133916683182377482808078639209270477294921875,
        "publishRating" : 1.46581298050294517310021547018550336360931396484375
      },
      "dateModified" : "dateModified",
      "text" : "text",
      "possiblyRelatesTo" : [ 9, 9 ]
    }
  } ]
}, {
  "identifier" : "identifier",
  "topics" : [ "topics", "topics" ],
  "results" : [ {
    "claimReviews" : [ {
      "datePublished" : "datePublished",
      "identifier" : 3,
      "reviewAspect" : "reviewAspect",
      "claimReviewed" : "claimReviewed",
      "dateCreated" : "dateCreated",
      "references" : [ 7, 7 ],
      "reviewBody" : "reviewBody",
      "itemReviewed" : 4,
      "dateModified" : "dateModified",
      "aggregateRating" : 2.027123023002321833274663731572218239307403564453125
    }, {
      "datePublished" : "datePublished",
      "identifier" : 3,
      "reviewAspect" : "reviewAspect",
      "claimReviewed" : "claimReviewed",
      "dateCreated" : "dateCreated",
      "references" : [ 7, 7 ],
      "reviewBody" : "reviewBody",
      "itemReviewed" : 4,
      "dateModified" : "dateModified",
      "aggregateRating" : 2.027123023002321833274663731572218239307403564453125
    } ],
    "claim" : {
      "calculatedRating" : 6.02745618307040320615897144307382404804229736328125,
      "datePublished" : "datePublished",
      "firstAppearance" : 5,
      "identifier" : 2.3021358869347654518833223846741020679473876953125,
      "appearance" : [ 0, 0 ],
      "dateCreated" : "dateCreated",
      "mentions" : [ 7, 7 ],
      "about" : [ "about", "about" ],
      "calculatedRatingDetail" : {
        "authorRating" : 5.962133916683182377482808078639209270477294921875,
        "publishRating" : 1.46581298050294517310021547018550336360931396484375
      },
      "dateModified" : "dateModified",
      "text" : "text",
      "possiblyRelatesTo" : [ 9, 9 ]
    }
  }, {
    "claimReviews" : [ {
      "datePublished" : "datePublished",
      "identifier" : 3,
      "reviewAspect" : "reviewAspect",
      "claimReviewed" : "claimReviewed",
      "dateCreated" : "dateCreated",
      "references" : [ 7, 7 ],
      "reviewBody" : "reviewBody",
      "itemReviewed" : 4,
      "dateModified" : "dateModified",
      "aggregateRating" : 2.027123023002321833274663731572218239307403564453125
    }, {
      "datePublished" : "datePublished",
      "identifier" : 3,
      "reviewAspect" : "reviewAspect",
      "claimReviewed" : "claimReviewed",
      "dateCreated" : "dateCreated",
      "references" : [ 7, 7 ],
      "reviewBody" : "reviewBody",
      "itemReviewed" : 4,
      "dateModified" : "dateModified",
      "aggregateRating" : 2.027123023002321833274663731572218239307403564453125
    } ],
    "claim" : {
      "calculatedRating" : 6.02745618307040320615897144307382404804229736328125,
      "datePublished" : "datePublished",
      "firstAppearance" : 5,
      "identifier" : 2.3021358869347654518833223846741020679473876953125,
      "appearance" : [ 0, 0 ],
      "dateCreated" : "dateCreated",
      "mentions" : [ 7, 7 ],
      "about" : [ "about", "about" ],
      "calculatedRatingDetail" : {
        "authorRating" : 5.962133916683182377482808078639209270477294921875,
        "publishRating" : 1.46581298050294517310021547018550336360931396484375
      },
      "dateModified" : "dateModified",
      "text" : "text",
      "possiblyRelatesTo" : [ 9, 9 ]
    }
  } ]
} ];
    if (Object.keys(examples).length > 0) {
      resolve(examples[Object.keys(examples)[0]]);
    } else {
      resolve();
    }
  });
}

