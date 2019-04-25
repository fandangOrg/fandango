'use strict';

const fetch = require('node-fetch');


/**
 * Find Facts similar to text input, specific category, and similar to optional topics
 * Response will return top 5 Fact documents closest to user provided criteria. A Fact is an Open Data creative work containing data, published by a recognized institution to make information available publicly.
 *
 * info Fact_Request_Interface 
 * returns List
 **/
exports.findFact = function(info) {
  return new Promise(function(resolve, reject) {
    var es = {};
    es.query = {};
    es.query.more_like_this = {};
    es.query.more_like_this.min_term_freq = 1;
    es.query.more_like_this.min_doc_freq = 1;
    es.query.more_like_this.fields = ["about", "name", "text"];
      if (info.topics){
        es.query.more_like_this.like = info.text + " " + info.category + " " + info.topics;
      }
      else{
        es.query.more_like_this.like = info.text + " " + info.category;
      }

      console.log(es)
 
      var url = "http://localhost:9220/fdg-fact/_search";

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
        .then(function(json){
          console.log(json.hits.hits)
          resolve(createFactResponse(info, json));
        })
        .catch(function(error){
          resolve(error);
        })
  });
}

function createFactResponse(info, json){
  var resultPayload = {};
  resultPayload.text = info.text || null;
  resultPayload.category = info.category || null;
  resultPayload.topics = info.topics || null;
  resultPayload.results = [];

  if (json.hits.total > 0){
    json.hits.hits.forEach(function(fact){
      var result = {};
      result.identifier = fact._source.identifier || null;
      result.name = fact._source.name || null;
      result.text = fact._source.text || null;
      result.url = fact._source.url || null;
      result.about = fact._source.about || null;
      result.mentions = fact._source.mentions || null;
      result.dateCreated = fact._source.dateCreated || null;
      result.dateModified = fact._source.dateModified || null;
      result.datePublished = fact._source.datePublished || null;
      result.temporalCoverageStart = fact._source.temporalCoverageStart || null;
      result.dateMtemporalCoverageEnd = fact._source.dateMtemporalCoverageEnd || null;
      result.spatialCoverage = fact._source.spatialCoverage || null;

      resultPayload.results.push(result);
    })  
  }

  return resultPayload;
  
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
          
            if (json.hits.total > 0){
              var moreLikeThis = {};
              moreLikeThis.size = 5;
              moreLikeThis.query = {};
              moreLikeThis.query.more_like_this = {};
              moreLikeThis.query.more_like_this.min_term_freq = 1;
              moreLikeThis.query.more_like_this.min_doc_freq = 1;
              moreLikeThis.query.more_like_this.fields = [];
              moreLikeThis.query.more_like_this.fields.push("*");
              moreLikeThis.query.more_like_this.like = {};
              moreLikeThis.query.more_like_this.like._index = "fdg-article";
              moreLikeThis.query.more_like_this.like._type = "doc";
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
                    //console.log(result.json())
                    return result.json();
                })
                .then(function(json){
                  
                  var articles = json.hits.hits;
                  var articlePromises = [];

                  //console.log(articles)
                  articles.forEach(function(article){
                    article._source.author.forEach(function(author){
                      var articleAuthorPromise = new Promise(function(resolve, reject) {
                        resolve(getAuthors(article._id, author));
                      });
                      articlePromises.push(articleAuthorPromise);
                    })
                    article._source.publisher.forEach(function(publisher){
                      var articlePublisherPromise = new Promise(function(resolve, reject) {
                        resolve(getPublishers(article._id, publisher));
                      });
                      articlePromises.push(articlePublisherPromise);
                    }) 
                   })

                   //console.log(articlePromises)

                   return Promise.all(articlePromises)
                   .then(function(results){
                     //console.log(results)
                     
                     resolve (createArticleResponse(info.identifier, articles, results));
                   })
                   .catch(function(error){
                     resolve(error)
                   })
              })
              .catch(function(error){
                resolve(error)
              });
            }
            else{
              console.log("here")
              resolve(emptyResponse(info.identifier, null));
            }           
  })
  .catch(function(error){
    resolve(error)
  })
})
}

function emptyResponse(identifier, topics){
  var returnPayload = {};
  returnPayload.identifier = identifier;
  if (topics) {
    returnPayload.topics = topics;
    }
  returnPayload.results = [];
  return returnPayload;
}

function createArticleResponse(identifier, articles, authorsAndPublishers){
  var resultPayload = {};
  resultPayload.identifier = identifier;
  console.log(articles)
  //console.log(authorsAndPublishers)

  var authors = [];
  var publishers = [];
  // First we separate out authors and publishers into an assoc array of objects
  authorsAndPublishers.forEach(function(ap){
    console.log(ap)
    ap.data.forEach(function(data){
    //console.log(data)
    if (data._index == "fdg-ap-person"){ // author
      if (authors[ap.id]){
        authors[ap.id].push(data._source);
      }
      else{
        authors[ap.id] = [];
        authors[ap.id].push(data._source);
      }
    }
    else if (data._index == "fdg-ap-organization"){ // publisher
      if (publishers[ap.id]){
        publishers[ap.id].push(data._source);
      }
      else{
        publishers[ap.id] = [];
        publishers[ap.id].push(data._source);
      }
    }
  })
  })

  var articleResponses = [];
  articles.forEach(function(article){
    // Here we construct the response as defined in the API
    var articleResponse = {};
    articleResponse.identifier = article._source.identifier || null;
    articleResponse.headline = article._source.headline || null;
    articleResponse.articleBody = article._source.articleBody || null;
    articleResponse.dateCreated = article._source.dateCreated || null;
    articleResponse.dateModified = article._source.dateModified || null;
    articleResponse.datePublished = article._source.datePublished || null;

    articleResponse.author = setAuthorList(article, authors);
    articleResponse.publisher = setPublisherList(article, publishers);

    articleResponse.mentions = article._source.mentions || [null];
    articleResponse.contains = article._source.contains || null;
    articleResponse.about = article._source.about || null;
    articleResponse.calculatedRating = article._source.calculatedRating || null;
    articleResponse.calculatedRatingDetail = article._source.calculatedRatingDetail || null;

    articleResponses.push(articleResponse);
  })
  resultPayload.results = articleResponses;
  return resultPayload;  
}

function createClaimResponse(identifier, topics, claims){
  var resultPayload = {};
  resultPayload.identifier = identifier;
  if (topics){
    resultPayload.topics = topics;
  }
  
  var claimResponses = [];
  claims.forEach(function(claim){
    var claimResponse = {};
    claimResponse.identifier = claim.identifier || null;
    claimResponse.about = claim.about || null;
    claimResponse.appearance = claim.appearance || null;
    claimResponse.calculatedRating = claim.calculatedRating || null;
    claimResponse.calculatedRatingDetail = claim.calculatedRatingDetail || null;
    claimResponse.dateCreated = claim.dateCreated || null;
    claimResponse.dateModified = claim.dateModified || null;
    claimResponse.datePublished = claim.datePublished || null;
    claimResponse.firstAppearance = claim.firstAppearance || null;
    claimResponse.mentions = claim.mentions || null;
    claimResponse.possiblyRelatesTo = claim.possiblyRelatesTo || null;
    claimResponse.text = claim.text || null;
    claimResponse.claimReviews = setClaimReviews(claim.claimReviews);
    claimResponses.push(claimResponse)
  })
  resultPayload.results = claimResponses;
  return resultPayload;
}

function setClaimReviews(claimReviews){
  var reviews = [];

  claimReviews.forEach(function(review){
    console.log(review)
    var claimReview = {};
    claimReview.identifier = review._source.identifier || null;
    claimReview.claimReviewed = review._source.claimReviewed || null;
    claimReview.reviewAspect = review._source.reviewAspect || null;
    claimReview.reviewBody = review._source.reviewBody || null;
    claimReview.dateCreated = review._source.dateCreated || null;
    claimReview.dateModified = review._source.dateModified || null;
    claimReview.datePublished = review._source.datePublished || null;
    claimReview.aggregateRating = review._source.aggregateRating || null;
    claimReview.itemReviewed = review._source.itemReviewed || null;
    claimReview.references = review._source.references || null;
    reviews.push(claimReview);
  })
  return reviews;
}

function setAuthorList(article, authors){
  var authorsResponse = [];

  authors[article._id].forEach(function(author){
    var authorResponse = {};
    authorResponse.identifier = author.identifier || null;
    authorResponse.name = author.name || null;
    authorResponse.url = author.url || null;
    authorResponse.nationality = author.nationality || null;
    authorResponse.bias = author.bias || null;
    authorResponse.jobTitle = author.jobTitle || null;
    authorResponse.gender = author.gender || null;
    authorResponse.affiliation = author.affiliation || null;

    authorsResponse.push(authorResponse);
  })
  return authorsResponse;
}

function setPublisherList(article, publishers){
  var publishersResponse = [];

  publishers[article._id].forEach(function(publisher){
    var publisherResponse = {};
    publisherResponse.identifier = publisher.identifier || null;
    publisherResponse.name = publisher.name || null;
    publisherResponse.url = publisher.url || null;
    publisherResponse.nationality = publisher.nationality || null;
    publisherResponse.bias = publisher.bias || null;
    publisherResponse.parentOrganization = publisher.parentOrganization || null;

    publishersResponse.push(publisherResponse);
  })
  return publishersResponse;
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
      es.query.more_like_this.min_term_freq = 1;
      es.query.more_like_this.min_doc_freq = 1;
      es.query.more_like_this.fields = ["about"];
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
          //  console.log(result.json())
           return result.json();
       })
       .then(function(json){

        if (json.hits.total > 0){
         console.log("hererer")
         
             if (info.topics){
               console.log("topics")
               // 
               var claims = json.hits.hits;
                   var claimPromises = [];

                   claims.forEach(function(claim){
                    var claimPromise = new Promise(function(resolve, reject) {
                      resolve(getClaimReviews(claim._source));
                    });
                    claimPromises.push(claimPromise);
                   })

                   return Promise.all(claimPromises)
                   .then(function(results){                     
                    resolve (createClaimResponse(info.identifier, info.topics, results));
                   })
                   .catch(function(error){
                     resolve(error)
                   })
             }
             else{
               
                console.log("id")
                var moreLikeThis = {};
                moreLikeThis.size = 5;
                moreLikeThis.query = {};
                moreLikeThis.query.more_like_this = {};
                moreLikeThis.query.more_like_this.min_term_freq = 1;
                moreLikeThis.query.more_like_this.min_doc_freq = 1;
                moreLikeThis.query.more_like_this.fields = [];
                moreLikeThis.query.more_like_this.fields.push("*");
                moreLikeThis.query.more_like_this.like = {};
                moreLikeThis.query.more_like_this.like._index = "fdg-claim";
                moreLikeThis.query.more_like_this.like._type = "doc";
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
                      return result.json();
                  })
                  .then(function(json){
                    // For Each claim we get in result set, fetch associated claim reviews

                    if (json.hits.total > 0){

                    var claims = json.hits.hits;
                    var claimPromises = [];


 
                    claims.forEach(function(claim){
                     var claimPromise = new Promise(function(resolve, reject) {
                       resolve(getClaimReviews(claim._source));
                     });
                     claimPromises.push(claimPromise);
                    })
 
                    return Promise.all(claimPromises)
                    .then(function(results){
                      resolve (createClaimResponse(info.identifier, info.topics, results));
                    })
                  }
                    else{
                      resolve(emptyResponse(info.identifier, info.topics));
                    }
                   })
                   .catch(function(error){
                     console.log(error)
                   })
                  
                }
              }
              else{
                resolve(emptyResponse(info.identifier, info.topics));
              }
       })
       .catch(function(error){
         resolve(error)
       })
      })
    }

    function getClaimReviews(claim){
     // console.log(claim)
      console.log("---------------")
      var claimQuery = {};
      claimQuery.query = {};
      claimQuery.query.match = {};
      claimQuery.query.match.itemReviewed = claim.identifier;

      console.log(claimQuery)

      var url = "http://localhost:9220/fdg-claim-review/doc/_search"
      return fetch(url,
        {
            method: 'POST',
            body: JSON.stringify(claimQuery),
            headers:{
                'Content-Type': 'application/json',
            }
        })
        .then(function(result){
          // console.log(result.json())
            return result.json();
        })
        .then(function(json){
          //console.log(json.hits.hits)
          claim.claimReviews = json.hits.hits;
          return Promise.resolve(claim);
        })
    }

    function getAuthors(articleID, author){
      // console.log(claim)
       console.log(author)
       var authorQuery = {};
       authorQuery.query = {};
       authorQuery.query.match = {};
       authorQuery.query.match.identifier = author;
 
       console.log(authorQuery)
 
       var url = "http://localhost:9220/fdg-ap-person/doc/_search"
       return fetch(url,
         {
             method: 'POST',
             body: JSON.stringify(authorQuery),
             headers:{
                 'Content-Type': 'application/json',
             }
         })
         .then(function(result){
           // console.log(result.json())
             return result.json();
         })
         .then(function(json){
           //console.log(json.hits.hits)
           var response = {};
           response.id = articleID;
           response.data = json.hits.hits;
           return Promise.resolve(response);
         })
     }

     function getPublishers(articleID, publisher){
      // console.log(claim)
       console.log(publisher)
       var publisherQuery = {};
       publisherQuery.query = {};
       publisherQuery.query.match = {};
       publisherQuery.query.match.identifier = publisher;
 
       console.log(publisherQuery)
 
       var url = "http://localhost:9220/fdg-ap-organization/doc/_search"
       return fetch(url,
         {
             method: 'POST',
             body: JSON.stringify(publisherQuery),
             headers:{
                 'Content-Type': 'application/json',
             }
         })
         .then(function(result){
           // console.log(result.json())
             return result.json();
         })
         .then(function(json){
           //console.log(json.hits.hits)
           var response = {};
           response.id = articleID;
           response.data = json.hits.hits;
           return Promise.resolve(response);
         })
     }



