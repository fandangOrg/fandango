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
    var es = {};
    es.query = {};
    es.query.match = {};
    es.query.match.identifier = info.identifier;

    var url = "http://localhost:9220/fdg-article/_search";
    
    fetch(url,
        {
            method: 'POST',
            body: JSON.stringify(es),
            headers:{
                'Content-Type': 'application/json',
            }
        })
        .then(function(result){
           // console.log(result.json())
            return result.json();
        })
        .then(
            function(json){
              // {
              //   "query": {
              //     "more_like_this" : {
              //       "fields" : ["summary"],
              //       "like" : [
              //       {
              //         "_index" : "fdg-article",
              //         "_type"	: "fdg-article",
              //         "_id" : "AWnnrzwxWtXF38UZYkwc"
              //       }
              //       ]
              //     }
              //   }
                
              // }

            console.log(JSON.stringify(json.hits.hits[0]))

              var moreLikeThis = {};
              moreLikeThis.size = 5;
              moreLikeThis.query = {};
              moreLikeThis.query.more_like_this = {};
              moreLikeThis.query.more_like_this.fields = [];
              moreLikeThis.query.more_like_this.fields.push("*");
              moreLikeThis.query.more_like_this.like = {};
              moreLikeThis.query.more_like_this.like._index = "fdg-article";
              moreLikeThis.query.more_like_this.like._type = "fdg-article";
              moreLikeThis.query.more_like_this.like._id = json.hits.hits[0]._id;

              console.log(JSON.stringify(moreLikeThis))


              fetch(url,
                {
                    method: 'POST',
                    body: JSON.stringify(moreLikeThis),
                    headers:{
                        'Content-Type': 'application/json',
                    }
                })
                .then(function(result){
                   // console.log(result.json())
                    return result.json();
                })
                .then(function(json){

                  console.log(json.hits.hits);
                  var examples = {};
                  examples['application/json'] = [ {
                "identifier" : 0,
                "results" : [ {
                  "article" : {
                    "identifier" : 6,
                    "articleBody" : "articleBody",
                    "author" : [ {
                      "identifier" : 1,
                      "nationality" : "nationality",
                      "gender" : "gender",
                      "affiliation" : [ 5, 5 ],
                      "bias" : "bias",
                      "jobTitle" : "jobTitle",
                      "name" : "name",
                      "url" : "url"
                    }, {
                      "identifier" : 1,
                      "nationality" : "nationality",
                      "gender" : "gender",
                      "affiliation" : [ 5, 5 ],
                      "bias" : "bias",
                      "jobTitle" : "jobTitle",
                      "name" : "name",
                      "url" : "url"
                    } ],
                    "about" : [ "about", "about" ],
                    "dateModified" : "dateModified",
                    "calculatedRatingDetail" : {
                      "authorRating" : 5.63737665663332876420099637471139430999755859375,
                      "publishRating" : 5.962133916683182377482808078639209270477294921875
                    },
                    "datePublished" : "datePublished",
                    "calculatedRating" : 3.61607674925191080461672754609026014804840087890625,
                    "contains" : [ 9, 9 ],
                    "dateCreated" : "dateCreated",
                    "mentions" : [ 7, 7 ],
                    "publisher" : [ {
                      "identifier" : 5,
                      "nationality" : "nationality",
                      "bias" : "bias",
                      "name" : "name",
                      "parentOrganization" : [ 2, 2 ],
                      "url" : "url"
                    }, {
                      "identifier" : 5,
                      "nationality" : "nationality",
                      "bias" : "bias",
                      "name" : "name",
                      "parentOrganization" : [ 2, 2 ],
                      "url" : "url"
                    } ],
                    "headline" : "headline"
                  }
                }, {
                  "article" : {
                    "identifier" : 6,
                    "articleBody" : "articleBody",
                    "author" : [ {
                      "identifier" : 1,
                      "nationality" : "nationality",
                      "gender" : "gender",
                      "affiliation" : [ 5, 5 ],
                      "bias" : "bias",
                      "jobTitle" : "jobTitle",
                      "name" : "name",
                      "url" : "url"
                    }, {
                      "identifier" : 1,
                      "nationality" : "nationality",
                      "gender" : "gender",
                      "affiliation" : [ 5, 5 ],
                      "bias" : "bias",
                      "jobTitle" : "jobTitle",
                      "name" : "name",
                      "url" : "url"
                    } ],
                    "about" : [ "about", "about" ],
                    "dateModified" : "dateModified",
                    "calculatedRatingDetail" : {
                      "authorRating" : 5.63737665663332876420099637471139430999755859375,
                      "publishRating" : 5.962133916683182377482808078639209270477294921875
                    },
                    "datePublished" : "datePublished",
                    "calculatedRating" : 3.61607674925191080461672754609026014804840087890625,
                    "contains" : [ 9, 9 ],
                    "dateCreated" : "dateCreated",
                    "mentions" : [ 7, 7 ],
                    "publisher" : [ {
                      "identifier" : 5,
                      "nationality" : "nationality",
                      "bias" : "bias",
                      "name" : "name",
                      "parentOrganization" : [ 2, 2 ],
                      "url" : "url"
                    }, {
                      "identifier" : 5,
                      "nationality" : "nationality",
                      "bias" : "bias",
                      "name" : "name",
                      "parentOrganization" : [ 2, 2 ],
                      "url" : "url"
                    } ],
                    "headline" : "headline"
                  }
                } ]
              }, {
                "identifier" : 0,
                "results" : [ {
                  "article" : {
                    "identifier" : 6,
                    "articleBody" : "articleBody",
                    "author" : [ {
                      "identifier" : 1,
                      "nationality" : "nationality",
                      "gender" : "gender",
                      "affiliation" : [ 5, 5 ],
                      "bias" : "bias",
                      "jobTitle" : "jobTitle",
                      "name" : "name",
                      "url" : "url"
                    }, {
                      "identifier" : 1,
                      "nationality" : "nationality",
                      "gender" : "gender",
                      "affiliation" : [ 5, 5 ],
                      "bias" : "bias",
                      "jobTitle" : "jobTitle",
                      "name" : "name",
                      "url" : "url"
                    } ],
                    "about" : [ "about", "about" ],
                    "dateModified" : "dateModified",
                    "calculatedRatingDetail" : {
                      "authorRating" : 5.63737665663332876420099637471139430999755859375,
                      "publishRating" : 5.962133916683182377482808078639209270477294921875
                    },
                    "datePublished" : "datePublished",
                    "calculatedRating" : 3.61607674925191080461672754609026014804840087890625,
                    "contains" : [ 9, 9 ],
                    "dateCreated" : "dateCreated",
                    "mentions" : [ 7, 7 ],
                    "publisher" : [ {
                      "identifier" : 5,
                      "nationality" : "nationality",
                      "bias" : "bias",
                      "name" : "name",
                      "parentOrganization" : [ 2, 2 ],
                      "url" : "url"
                    }, {
                      "identifier" : 5,
                      "nationality" : "nationality",
                      "bias" : "bias",
                      "name" : "name",
                      "parentOrganization" : [ 2, 2 ],
                      "url" : "url"
                    } ],
                    "headline" : "headline"
                  }
                }, {
                  "article" : {
                    "identifier" : 6,
                    "articleBody" : "articleBody",
                    "author" : [ {
                      "identifier" : 1,
                      "nationality" : "nationality",
                      "gender" : "gender",
                      "affiliation" : [ 5, 5 ],
                      "bias" : "bias",
                      "jobTitle" : "jobTitle",
                      "name" : "name",
                      "url" : "url"
                    }, {
                      "identifier" : 1,
                      "nationality" : "nationality",
                      "gender" : "gender",
                      "affiliation" : [ 5, 5 ],
                      "bias" : "bias",
                      "jobTitle" : "jobTitle",
                      "name" : "name",
                      "url" : "url"
                    } ],
                    "about" : [ "about", "about" ],
                    "dateModified" : "dateModified",
                    "calculatedRatingDetail" : {
                      "authorRating" : 5.63737665663332876420099637471139430999755859375,
                      "publishRating" : 5.962133916683182377482808078639209270477294921875
                    },
                    "datePublished" : "datePublished",
                    "calculatedRating" : 3.61607674925191080461672754609026014804840087890625,
                    "contains" : [ 9, 9 ],
                    "dateCreated" : "dateCreated",
                    "mentions" : [ 7, 7 ],
                    "publisher" : [ {
                      "identifier" : 5,
                      "nationality" : "nationality",
                      "bias" : "bias",
                      "name" : "name",
                      "parentOrganization" : [ 2, 2 ],
                      "url" : "url"
                    }, {
                      "identifier" : 5,
                      "nationality" : "nationality",
                      "bias" : "bias",
                      "name" : "name",
                      "parentOrganization" : [ 2, 2 ],
                      "url" : "url"
                    } ],
                    "headline" : "headline"
                  }
                } ]
              } ];
    if (Object.keys(examples).length > 0) {
      resolve(examples[Object.keys(examples)[0]]);
    } else {
      resolve();
    }
  })
  .catch(function(error){

  })
  });
})
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
     /******
    * First check if topics exist. If so then we construct ES more_like_this using topics field.
    * If not then we use the _id and * search
    *  */ 
    
   var es = {};
   es.query = {};

   console.log("here")

   if (info.topics){
     es.query.more_like_this = {};
     es.query.more_like_this.fields = ["topics"]
     es.query.more_like_this.like = info.topics;
   }
   else{
     es.query.match = {};
     es.query.match.identifier = info.identifier;
   }
   console.log(JSON.stringify(es))

   var url = "http://localhost:9220/fdg-claim/doc/_search";
   
   fetch(url,
       {
           method: 'POST',
           body: JSON.stringify(es),
           headers:{
               'Content-Type': 'application/json',
           }
       })
       .then(function(result){
           console.log(result.json())
           return result.json();
       })
       .then(function(json){
         
             if (info.topics){
               console.log("topics")
               resolve(json);
             }
             else{
               console.log("id")
               var moreLikeThis = {};
               moreLikeThis.size = 5;
               moreLikeThis.query = {};
               moreLikeThis.query.more_like_this = {};
               moreLikeThis.query.more_like_this.fields = [];
               moreLikeThis.query.more_like_this.fields.push("*");
               moreLikeThis.query.more_like_this.like = {};
               moreLikeThis.query.more_like_this.like._index = "fdg-claim";
               moreLikeThis.query.more_like_this.like._type = "fdg-claim";
               moreLikeThis.query.more_like_this.like._id = json.hits.hits[0]._id;

               console.log(JSON.stringify(moreLikeThis))

               fetch(url,
                 {
                     method: 'POST',
                     body: JSON.stringify(moreLikeThis),
                     headers:{
                         'Content-Type': 'application/json',
                     }
                 })
                 .then(function(result){
                   // console.log(result.json())
                     return result.json();
                 })
                 .then(function(json){
                   console.log(json.hits.hits);
                    var examples = {};
                    examples['application/json'] = [ {
                  "identifier" : 0,
                  "topics" : [ "topics", "topics" ],
                  "results" : [ {
                    "claim" : {
                      "firstAppearance" : 2,
                      "identifier" : 7,
                      "claimReviews" : [ {
                        "datePublished" : "datePublished",
                        "identifier" : 2,
                        "reviewAspect" : "reviewAspect",
                        "claimReviewed" : "claimReviewed",
                        "dateCreated" : "dateCreated",
                        "references" : [ 1, 1 ],
                        "reviewBody" : "reviewBody",
                        "itemReviewed" : 7,
                        "dateModified" : "dateModified",
                        "aggregateRating" : 4.1456080298839363962315474054776132106781005859375
                      }, {
                        "datePublished" : "datePublished",
                        "identifier" : 2,
                        "reviewAspect" : "reviewAspect",
                        "claimReviewed" : "claimReviewed",
                        "dateCreated" : "dateCreated",
                        "references" : [ 1, 1 ],
                        "reviewBody" : "reviewBody",
                        "itemReviewed" : 7,
                        "dateModified" : "dateModified",
                        "aggregateRating" : 4.1456080298839363962315474054776132106781005859375
                      } ],
                      "about" : [ "about", "about" ],
                      "calculatedRatingDetail" : {
                        "authorRating" : 5.63737665663332876420099637471139430999755859375,
                        "publishRating" : 5.962133916683182377482808078639209270477294921875
                      },
                      "dateModified" : "dateModified",
                      "calculatedRating" : 1.46581298050294517310021547018550336360931396484375,
                      "datePublished" : "datePublished",
                      "appearance" : [ 6, 6 ],
                      "dateCreated" : "dateCreated",
                      "mentions" : [ 9, 9 ],
                      "text" : "text",
                      "possiblyRelatesTo" : [ 3, 3 ]
                    }
                  }, {
                    "claim" : {
                      "firstAppearance" : 2,
                      "identifier" : 7,
                      "claimReviews" : [ {
                        "datePublished" : "datePublished",
                        "identifier" : 2,
                        "reviewAspect" : "reviewAspect",
                        "claimReviewed" : "claimReviewed",
                        "dateCreated" : "dateCreated",
                        "references" : [ 1, 1 ],
                        "reviewBody" : "reviewBody",
                        "itemReviewed" : 7,
                        "dateModified" : "dateModified",
                        "aggregateRating" : 4.1456080298839363962315474054776132106781005859375
                      }, {
                        "datePublished" : "datePublished",
                        "identifier" : 2,
                        "reviewAspect" : "reviewAspect",
                        "claimReviewed" : "claimReviewed",
                        "dateCreated" : "dateCreated",
                        "references" : [ 1, 1 ],
                        "reviewBody" : "reviewBody",
                        "itemReviewed" : 7,
                        "dateModified" : "dateModified",
                        "aggregateRating" : 4.1456080298839363962315474054776132106781005859375
                      } ],
                      "about" : [ "about", "about" ],
                      "calculatedRatingDetail" : {
                        "authorRating" : 5.63737665663332876420099637471139430999755859375,
                        "publishRating" : 5.962133916683182377482808078639209270477294921875
                      },
                      "dateModified" : "dateModified",
                      "calculatedRating" : 1.46581298050294517310021547018550336360931396484375,
                      "datePublished" : "datePublished",
                      "appearance" : [ 6, 6 ],
                      "dateCreated" : "dateCreated",
                      "mentions" : [ 9, 9 ],
                      "text" : "text",
                      "possiblyRelatesTo" : [ 3, 3 ]
                    }
                  } ]
                }, {
                  "identifier" : 0,
                  "topics" : [ "topics", "topics" ],
                  "results" : [ {
                    "claim" : {
                      "firstAppearance" : 2,
                      "identifier" : 7,
                      "claimReviews" : [ {
                        "datePublished" : "datePublished",
                        "identifier" : 2,
                        "reviewAspect" : "reviewAspect",
                        "claimReviewed" : "claimReviewed",
                        "dateCreated" : "dateCreated",
                        "references" : [ 1, 1 ],
                        "reviewBody" : "reviewBody",
                        "itemReviewed" : 7,
                        "dateModified" : "dateModified",
                        "aggregateRating" : 4.1456080298839363962315474054776132106781005859375
                      }, {
                        "datePublished" : "datePublished",
                        "identifier" : 2,
                        "reviewAspect" : "reviewAspect",
                        "claimReviewed" : "claimReviewed",
                        "dateCreated" : "dateCreated",
                        "references" : [ 1, 1 ],
                        "reviewBody" : "reviewBody",
                        "itemReviewed" : 7,
                        "dateModified" : "dateModified",
                        "aggregateRating" : 4.1456080298839363962315474054776132106781005859375
                      } ],
                      "about" : [ "about", "about" ],
                      "calculatedRatingDetail" : {
                        "authorRating" : 5.63737665663332876420099637471139430999755859375,
                        "publishRating" : 5.962133916683182377482808078639209270477294921875
                      },
                      "dateModified" : "dateModified",
                      "calculatedRating" : 1.46581298050294517310021547018550336360931396484375,
                      "datePublished" : "datePublished",
                      "appearance" : [ 6, 6 ],
                      "dateCreated" : "dateCreated",
                      "mentions" : [ 9, 9 ],
                      "text" : "text",
                      "possiblyRelatesTo" : [ 3, 3 ]
                    }
                  }, {
                    "claim" : {
                      "firstAppearance" : 2,
                      "identifier" : 7,
                      "claimReviews" : [ {
                        "datePublished" : "datePublished",
                        "identifier" : 2,
                        "reviewAspect" : "reviewAspect",
                        "claimReviewed" : "claimReviewed",
                        "dateCreated" : "dateCreated",
                        "references" : [ 1, 1 ],
                        "reviewBody" : "reviewBody",
                        "itemReviewed" : 7,
                        "dateModified" : "dateModified",
                        "aggregateRating" : 4.1456080298839363962315474054776132106781005859375
                      }, {
                        "datePublished" : "datePublished",
                        "identifier" : 2,
                        "reviewAspect" : "reviewAspect",
                        "claimReviewed" : "claimReviewed",
                        "dateCreated" : "dateCreated",
                        "references" : [ 1, 1 ],
                        "reviewBody" : "reviewBody",
                        "itemReviewed" : 7,
                        "dateModified" : "dateModified",
                        "aggregateRating" : 4.1456080298839363962315474054776132106781005859375
                      } ],
                      "about" : [ "about", "about" ],
                      "calculatedRatingDetail" : {
                        "authorRating" : 5.63737665663332876420099637471139430999755859375,
                        "publishRating" : 5.962133916683182377482808078639209270477294921875
                      },
                      "dateModified" : "dateModified",
                      "calculatedRating" : 1.46581298050294517310021547018550336360931396484375,
                      "datePublished" : "datePublished",
                      "appearance" : [ 6, 6 ],
                      "dateCreated" : "dateCreated",
                      "mentions" : [ 9, 9 ],
                      "text" : "text",
                      "possiblyRelatesTo" : [ 3, 3 ]
                    }
                  } ]
                } ];
                    if (Object.keys(examples).length > 0) {
                      resolve(examples[Object.keys(examples)[0]]);
                    } else {
                      resolve();
                    }
                  })
                  .catch(function(error){
                    console.log(error)
                  })
                  

                }
       })
      })
    }



