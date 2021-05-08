'use strict';

const fetch = require('node-fetch');
import rake from 'rake-js'




/**
 * Find Facts similar to text input, specific category, and similar to optional topics
 * Response will return top 5 Fact documents closest to user provided criteria. A Fact is an Open Data creative work containing data, published by a recognized institution to make information available publicly.
 *
 * info Fact_Request_Interface 
 * returns List
 **/


 const stopWords = ["a","able","about","above","abst","accordance","according","accordingly","across","act","actually","added","adj","affected","affecting","affects","after","afterwards","again","against","ah","all","almost","alone","along","already","also","although","always","am","among","amongst","an","and","announce","another","any","anybody","anyhow","anymore","anyone","anything","anyway","anyways","anywhere","apparently","approximately","are","aren","arent","arise","around","as","aside","ask","asking","at","auth","available","away","awfully","b","back","be","became","because","become","becomes","becoming","been","before","beforehand","begin","beginning","beginnings","begins","behind","being","believe","below","beside","besides","between","beyond","biol","both","brief","briefly","but","by","c","ca","came","can","cannot","can't","cause","causes","certain","certainly","co","com","come","comes","contain","containing","contains","could","couldnt","d","date","did","didn't","different","do","does","doesn't","doing","done","don't","down","downwards","due","during","e","each","ed","edu","effect","eg","eight","eighty","either","else","elsewhere","end","ending","enough","especially","et","et-al","etc","even","ever","every","everybody","everyone","everything","everywhere","ex","except","f","far","few","ff","fifth","first","five","fix","followed","following","follows","for","former","formerly","forth","found","four","from","further","furthermore","g","gave","get","gets","getting","give","given","gives","giving","go","goes","gone","got","gotten","h","had","happens","hardly","has","hasn't","have","haven't","having","he","hed","hence","her","here","hereafter","hereby","herein","heres","hereupon","hers","herself","hes","hi","hid","him","himself","his","hither","home","how","howbeit","however","hundred","i","id","ie","if","i'll","im","immediate","immediately","importance","important","in","inc","indeed","index","information","instead","into","invention","inward","is","isn't","it","itd","it'll","its","itself","i've","j","just","k","keep	keeps","kept","kg","km","know","known","knows","l","largely","last","lately","later","latter","latterly","least","less","lest","let","lets","like","liked","likely","line","little","'ll","look","looking","looks","ltd","m","made","mainly","make","makes","many","may","maybe","me","mean","means","meantime","meanwhile","merely","mg","might","million","miss","ml","more","moreover","most","mostly","mr","mrs","much","mug","must","my","myself","n","na","name","namely","nay","nd","near","nearly","necessarily","necessary","need","needs","neither","never","nevertheless","new","next","nine","ninety","no","nobody","non","none","nonetheless","noone","nor","normally","nos","not","noted","nothing","now","nowhere","o","obtain","obtained","obviously","of","off","often","oh","ok","okay","old","omitted","on","once","one","ones","only","onto","or","ord","other","others","otherwise","ought","our","ours","ourselves","out","outside","over","overall","owing","own","p","page","pages","part","particular","particularly","past","per","perhaps","placed","please","plus","poorly","possible","possibly","potentially","pp","predominantly","present","previously","primarily","probably","promptly","proud","provides","put","q","que","quickly","quite","qv","r","ran","rather","rd","re","readily","really","recent","recently","ref","refs","regarding","regardless","regards","related","relatively","research","respectively","resulted","resulting","results","right","run","s","said","same","saw","say","saying","says","sec","section","see","seeing","seem","seemed","seeming","seems","seen","sees","self","selves","sent","seven","several","shall","she","shed","she'll","shes","should","shouldn't","show","showed","shown","showns","shows","significant","significantly","similar","similarly","since","six","slightly","so","some","somebody","somehow","someone","somethan","something","sometime","sometimes","somewhat","somewhere","soon","sorry","specifically","specified","specify","specifying","still","stop","strongly","sub","substantially","successfully","such","sufficiently","suggest","sup","sure	t","take","taken","taking","tell","tends","th","than","thank","thanks","thanx","that","that'll","thats","that've","the","their","theirs","them","themselves","then","thence","there","thereafter","thereby","thered","therefore","therein","there'll","thereof","therere","theres","thereto","thereupon","there've","these","they","theyd","they'll","theyre","they've","think","this","those","thou","though","thoughh","thousand","throug","through","throughout","thru","thus","til","tip","to","together","too","took","toward","towards","tried","tries","truly","try","trying","ts","twice","two","u","un","under","unfortunately","unless","unlike","unlikely","until","unto","up","upon","ups","us","use","used","useful","usefully","usefulness","uses","using","usually","v","value","various","'ve","very","via","viz","vol","vols","vs","w","want","wants","was","wasnt","way","we","wed","welcome","we'll","went","were","werent","we've","what","whatever","what'll","whats","when","whence","whenever","where","whereafter","whereas","whereby","wherein","wheres","whereupon","wherever","whether","which","while","whim","whither","who","whod","whoever","whole","who'll","whom","whomever","whos","whose","why","widely","willing","wish","with","within","without","wont","words","world","would","wouldnt","www","x","y","yes","yet","you","youd","you'll","your","youre","yours","yourself","yourselves","you've","z","zero","a","adesso","ai","al","alla","allo","allora","altre","altri","altro","anche","ancora","avere","aveva","avevano","ben","buono","che","chi","cinque","comprare","con","consecutivi","consecutivo","cosa","cui","da","del","della","dello","dentro","deve","devo","di","doppio","due","e","ecco","fare","fine","fino","fra","gente","giu","ha","hai","hanno","ho","il","indietro	invece","io","la","lavoro","le","lei","lo","loro","lui","lungo","ma","me","meglio","molta","molti","molto","nei","nella","no","noi","nome","nostro","nove","nuovi","nuovo","o","oltre","ora","otto","peggio","pero","persone","piu","poco","primo","promesso","qua","quarto","quasi","quattro","quello","questo","qui","quindi","quinto","rispetto","sara","secondo","sei","sembra	","sembrava","senza","sette","sia","siamo","siete","solo","sono","sopra","soprattutto","sotto","stati","stato","stesso","su","subito","sul","sulla","tanto","te","tempo","terzo","tra","tre","triplo","ultimo","un","una","uno","va","vai","voi","volte","vostro","aan","af","al","als","bij","dan","dat","die","dit","een","en","er","had","heb","hem","het","hij","hoe","hun","ik	in","is","je","kan","me","men","met","mij","nog","nu","of","ons","ook","te","tot","uit","van","was","wat","we","wel","wij","zal","ze","zei","zij","zo","zou","un","una","unas","unos","uno","sobre","todo","también","tras","otro","algún","alguno","alguna","algunos","algunas","ser","es","soy","eres","somos","sois","estoy","esta","estamos","estais","estan","como","en","para","atras","porque","porqué","estado","estaba","ante","antes","siendo","ambos","pero","por","poder","puede","puedo","podemos","podeis","pueden","fui","fue","fuimos","fueron","hacer","hago","hace","hacemos","haceis","hacen","cada","fin","incluso","primero	desde","conseguir","consigo","consigue","consigues","conseguimos","consiguen","ir","voy","va","vamos","vais","van","vaya","gueno","ha","tener","tengo","tiene","tenemos","teneis","tienen","el","la","lo","las","los","su","aqui","mio","tuyo","ellos","ellas","nos","nosotros","vosotros","vosotras","si","dentro","solo","solamente","saber","sabes","sabe","sabemos","sabeis","saben","ultimo","largo","bastante","haces","muchos","aquellos","aquellas","sus","entonces","tiempo","verdad","verdadero","verdadera	cierto",
 "ciertos","cierta","ciertas","de","intentar","intento","intenta","intentas","intentamos","intentais","intentan","dos","bajo","arriba","encima",
 "usar","uso","usas","usa","usamos","usais","usan","emplear","empleo","empleas","emplean","ampleamos","empleais","valor","muy","era","eras","eramos",
 "eran","modo","bien","cual","cuando","donde","mientras","quien","con","entre","sin","trabajo","trabajar","trabajas","trabaja","trabajamos","trabajais",
 "trabajan","podria","podrias","podriamos","podrian","podriais","yo","aquel","alguna","algunas","alguno","algunos","algÃºn","ambos","ampleamos","ante",
 "antes","aquel","aquellas","aquellos","aqui","arriba","atras","bajo","bastante","bien","cada","cierta","ciertas","cierto","ciertos","como","con",
 "conseguimos","conseguir","consigo","consigue","consiguen","consigues","cual","cuando","dentro","desde","donde","dos","el","ellas","ellos","empleais","emplean",
 "emplear","empleas","empleo","en","encima","entonces","entre","era","eramos","eran","eras","eres","es","esta","estaba","estado","estais","estamos","estan","estoy",
 "fin","fue","fueron","fui","fuimos","gueno","ha","hace","haceis","hacemos","hacen","hacer","haces","hago","incluso","intenta","intentais","intentamos","intentan",
 "intentar","intentas","intento","ir","la","largo","las","lo","los","mientras","mio","modo","muchos","muy","nos","nosotros","otro","para","pero","podeis","podemos",
 "poder","podria","podriais","podriamos","podrian","podrias","por","porquÃ©","porque","primero","puede","pueden","puedo","quien","sabe","sabeis","sabemos","saben",
 "saber","sabes","ser","si","siendo","sin","sobre","sois","solamente","solo","somos","soy","su","sus","tambiÃ©n","teneis","tenemos","tener","tengo","tiempo","tiene",
 "tienen","todo","trabaja","trabajais","trabajamos","trabajan","trabajar","trabajas","trabajo","tras","tuyo","ultimo","un","una","unas","uno","unos","usa","usais",
 "usamos","usan","usar","usas","uso","va","vais","valor","vamos","van","vaya","verdad","verdadera","verdadero","vosotras","vosotros","voy","yo","aan","ade","aangaande",
 "aangezien","achte","achter","achterna","af","afgelopen","al","aldaar","aldus","alhoewel","alias","alle","allebei","alleen","alles","als","alsnog","altijd","altoos",
 "ander","andere","anders","anderszins","beetje","behalve","behoudens","beide","beiden","ben","beneden","bent","bepaald","betreffende","bij","bijna","bijv","binnen",
 "binnenin","blijkbaar","blijken","boven","bovenal","bovendien","bovengenoemd","bovenstaand","bovenvermeld","buiten","bv","daar","daardoor","daarheen","daarin",
 "daarna","daarnet","daarom","daarop","daaruit","daarvanlangs","dan","dat","de","deden","deed","der","derde","derhalve","dertig","deze","dhr","die","dikwijls",
 "dit","doch","doe","doen","doet","door","doorgaand","drie","duizend","dus","echter","een","eens","eer","eerdat","eerder","eerlang","eerst","eerste","eigen",
 "eigenlijk","elk","elke","en","enig","enige","enigszins","enkel","er","erdoor","erg","ergens","etc","etcetera","even","eveneens","evenwel","gauw","ge",
 "gedurende","geen","gehad","gekund","geleden","gelijk","gemoeten","gemogen","genoeg","geweest","gewoon","gewoonweg","haar","haarzelf","had","hadden","hare","heb",
 "hebben","hebt","hedden","heeft","heel","hem","hemzelf","hen","het","hetzelfde","hier","hierbeneden","hierboven","hierin","hierna","hierom","hij","hijzelf","hoe",
 "hoewel","honderd","hun","hunne","ieder","iedere","iedereen","iemand","iets","ik","ikzelf","in","inderdaad","inmiddels","intussen","inzake","is","ja","je","jezelf",
 "jij","jijzelf","jou","jouw","jouwe","juist","jullie","kan","klaar","kon","konden","krachtens","kun","kunnen","kunt","laatst","later","liever","lijken","lijkt",
 "maak","maakt","maakte","maakten","maar","mag","maken","me","meer","meest","meestal","men","met","mevr","mezelf","mij","mijn","mijnent","mijner","mijzelf","minder",
 "miss","misschien","missen","mits","mocht","mochten","moest","moesten","moet","moeten","mogen","mr","mrs","mw","na","naar","nadat","nam","namelijk","nee","neem",
 "negen","nemen","nergens","net","niemand","niet","niets","niks","noch","nochtans","nog","nogal","nooit","nu","nv","of","ofschoon","om","omdat","omhoog","omlaag",
 "omstreeks","omtrent","omver","ondanks","onder","ondertussen","ongeveer","ons","onszelf","onze","onzeker","ooit","ook","op","opnieuw","opzij","over","overal",
 "overeind","overige","overigens","paar","pas","per","precies","recent","redelijk","reeds","rond","rondom","samen","sedert","sinds","sindsdien","slechts","sommige",
 "spoedig","steeds","tamelijk","te","tegen","tegenover","tenzij","terwijl","thans","tien","tiende","tijdens","tja","toch","toe","toen","toenmaals","toenmalig",
 "tot","totdat","tussen","twee","tweede","u","uit","uitgezonderd","uw","vaak","vaakwat","van","vanaf","vandaan","vanuit","vanwege","veel","veeleer","veertig",
 "verder","verscheidene","verschillende","vervolgens","via","vier","vierde","vijf","vijfde","vijftig","vol","volgend","volgens","voor","vooraf","vooral",
 "vooralsnog","voorbij","voordat","voordezen","voordien","voorheen","voorop","voorts","vooruit","vrij","vroeg","waar","waarom","waarschijnlijk","wanneer",
 "want","waren","was","wat","we","wederom","weer","weg","wegens","weinig","wel","weldra","welk","welke","werd","werden","werder","wezen","whatever","wie",
 "wiens","wier","wij","wijzelf","wil","wilden","willen","word","worden","wordt","zal","ze","zei","zeker","zelf","zelfde","zelfs","zes","zeven","zich",
 "zichzelf","zij","zijn","zijne","zijzelf","zo","zoals","zodat","zodra","zonder","zou","zouden","zowat","zulk","zulke","zullen","zult", ":", "-", ".", ",", ";", ":"]

 function removeStopWords(query){
    console.log(query)
    let querySplit = query.toLowerCase().split(" ");

    let sanitized = querySplit.filter(function(token){
      return stopWords.indexOf(token) < 0;
    })

    console.log(sanitized.join(" "))
    return sanitized.join(" ");
 }

 function removeStopWordsList(query){
  console.log(query)

  let sanitized = query.filter(function(token){
    return stopWords.indexOf(token) < 0 || stopWords.indexOf(" ") < 0;
  })

  console.log("SAN")
  console.log(sanitized)
  let sliced = sanitized.slice(0, 4)

  console.log(sliced.join(" "))
  return sliced.join(" ");
}

 exports.findFact = function(info) {
  return new Promise(function(resolve, reject) {
    console.log("nnnn")
    var es = {};
    es.query = {};
    es.query.more_like_this = {};
    es.query.more_like_this.min_term_freq = 1;
    es.query.more_like_this.min_doc_freq = 1;
    es.query.more_like_this.fields = ["text"];

    let rake_extract = rake(info.text);
    if (rake_extract.length == 0){
      rake_extract = info.text.split(" ")
    }

    console.log()
    // console.log(rake_extract)
    let rakeSansStop = removeStopWordsList(rake_extract);
    console.log(rakeSansStop)
    // let stripStopWords = removeStopWords(info.text);
    // console.log(rake_extract)
      if (info.topics){
        es.query.more_like_this.like = info.text + " " + info.category + " " + info.topics;
      }
      else{
        es.query.more_like_this.like = rakeSansStop;
      }

     // console.log(es)
 
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

  if (json.hits.total.value > 0){
    json.hits.hits.forEach(function(fact){
      var result = {};
      result.identifier = fact._source.identifier || null;
      result.name = fact._source.name || null;
      result.text = fact._source.text || null;
      result.url = fact._source.url || null;
      result.inLanguage = fact._source.inLanguage || null;
      result.sourceDomain = fact._source.sourceDomain || null;
      result.source = fact._source.source || null;
      result.publishDateEstimated = fact._source.publishDateEstimated || null;
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
              console.log("n1")
              console.log(json)
          
            if (json.hits.total.value > 0){
              console.log("n2")

              var moreLikeThis = {};
              moreLikeThis.size = 5;
              moreLikeThis.query = {};
              moreLikeThis.query.more_like_this = {};
              moreLikeThis.query.more_like_this.min_term_freq = 1;
              moreLikeThis.query.more_like_this.min_doc_freq = 1;
              moreLikeThis.query.more_like_this.fields = [];
              moreLikeThis.query.more_like_this.fields.push("articleBody");
              moreLikeThis.query.more_like_this.fields.push("topic");
              moreLikeThis.query.more_like_this.fields.push("headline");
              moreLikeThis.query.more_like_this.like = {};
              moreLikeThis.query.more_like_this.like._index = "fdg-article";
              // moreLikeThis.query.more_like_this.like._type = "doc";
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
                  console.log("n3")

                  console.log(json)
                  
                  var articles = json.hits.hits;
                  // console.log(articles)
                  var articlePromises = [];

                  articles.forEach(function(article){
                    // console.log("art")
                    // console.log(article)
                    article._source.authors.forEach(function(author){
                      // console.log("auth")
                      // console.log(author)
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
                    // Here we retrieve the fusionScore for each article
                    articlePromises.push(new Promise(function(resolve, reject) {resolve(getCalculatedRating(article._id));}))
                   })



                   //console.log(articlePromises)

                   return Promise.all(articlePromises)
                   .then(function(results){
                    //  console.log(results)
                     
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
              //console.log("here")
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

function createArticleResponse(identifier, articles, authorsRatingAndPublishers){
  var resultPayload = {};
  resultPayload.identifier = identifier;
 // console.log(articles)
 // console.log(authorsAndPublishers)

 // console.log("article listed")

  var authors = [];
  var publishers = [];
  var rating = [];
  // First we separate out authors and publishers into an assoc array of objects
  authorsRatingAndPublishers.forEach(function(arp){
  //  console.log(ap)
    arp.data.forEach(function(data){
    // console.log(data)
    if (data._index == "fdg-ap-person"){ // author
      if (authors[arp.id]){
        authors[arp.id].push(data._source);
      }
      else{
        authors[arp.id] = [];
        authors[arp.id].push(data._source);
      }
    }
    else if (data._index == "fdg-ap-organization"){ // publisher
      if (publishers[arp.id]){
        publishers[arp.id].push(data._source);
      }
      else{
        publishers[arp.id] = [];
        publishers[arp.id].push(data._source);
      }
    }
    else if (data._index == "fdg-article-fusionscore"){ // fusion score
     rating[arp.id] = data._source;
    //  console.log(rating)
    //  console.log("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
    }
  })
  })

  
  var articleResponses = [];
  articles.forEach(function(article){

    // console.log(article)
    
    // Here we construct the response as defined in the API
    var articleResponse = {};
    articleResponse.identifier = article._source.identifier || null;
    articleResponse.url = article._source.url || null;
    articleResponse.topic = article._source.topic || null;
    articleResponse.inLanguage = article._source.inLanguage || null;
    articleResponse.sourceDomain = article._source.sourceDomain || null;
    articleResponse.publishDateEstimated = article._source.publishDateEstimated || null;
    articleResponse.headline = article._source.headline || null;
    articleResponse.articleBody = article._source.articleBody || null;
    articleResponse.dateCreated = article._source.dateCreated || null;
    articleResponse.dateModified = article._source.dateModified || null;
    articleResponse.datePublished = article._source.datePublished || null;

    try{
      articleResponse.author = setAuthorList(article, authors);
    }
    catch(e){
      articleResponse.author = null;
    }
    
   // console.log("auth")
   // console.log(articleResponse.author)
    try{
      articleResponse.publisher = setPublisherList(article, publishers);
    }
    catch(e){
      articleResponse.publisher = null;
    }

    articleResponse.mentions = article._source.mentions || [null];
    articleResponse.contains = article._source.contains || null;
    articleResponse.about = article._source.about || null;
    try{
      articleResponse.calculatedRating = rating[article._id].calculatedRating || null;
    }
    catch(e){
      articleResponse.calculatedRating = null;
    }
    try{
      articleResponse.calculatedRatingDetail = rating[article._id].calculatedRatingDetail || null;
    }
    catch(e){
      articleResponse.calculatedRatingDetail = null;
    }

    articleResponses.push(articleResponse);
  })
  resultPayload.results = articleResponses;
  return resultPayload;  
}
var htmlEntities = {
  nbsp: ' ',
  cent: '¢',
  pound: '£',
  yen: '¥',
  euro: '€',
  copy: '©',
  reg: '®',
  lt: '<',
  gt: '>',
  quot: '"',
  amp: '&',
  apos: '\''
};

function unescapeHTML(str) {
  return str.replace(/\&([^;]+);/g, function (entity, entityCode) {
      var match;

      if (entityCode in htmlEntities) {
          return htmlEntities[entityCode];
          /*eslint no-cond-assign: 0*/
      } else if (match = entityCode.match(/^#x([\da-fA-F]+)$/)) {
          return String.fromCharCode(parseInt(match[1], 16));
          /*eslint no-cond-assign: 0*/
      } else if (match = entityCode.match(/^#(\d+)$/)) {
          return String.fromCharCode(~~match[1]);
      } else {
          return entity;
      }
  });
};

function createClaimResponse(identifier, topics, claims){
  var resultPayload = {};
  resultPayload.identifier = identifier;
  if (topics){
    resultPayload.topics = topics;
  }
  
  var claimResponses = [];
  claims.forEach(function(claim){
    var claimResponse = {};
    claimResponse.author = claim.author || null;

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
    claimResponse.text = unescapeHTML(claim.text) || null;

    try{
      claimResponse.claimReviews = setClaimReviews(claim.claimReviews);
    }
    catch(e){
      claimResponse.claimReviews = null;
    }
    claimResponses.push(claimResponse)
  })
  resultPayload.results = claimResponses;
  return resultPayload;
}

function setClaimReviews(claimReviews){
  var reviews = [];

  claimReviews.forEach(function(review){
  //  console.log(review)
    var claimReview = {};
    claimReview = review._source;
    // claimReview.identifier = review._source.identifier || null;
    // claimReview.claimReviewed = review._source.claimReviewed || null;
    // claimReview.reviewAspect = review._source.reviewAspect || null;
    // claimReview.reviewBody = review._source.reviewBody || null;
    // claimReview.dateCreated = review._source.dateCreated || null;
    // claimReview.dateModified = review._source.dateModified || null;
    // claimReview.datePublished = review._source.datePublished || null;
    // claimReview.aggregateRating = review._source.aggregateRating || null;
    // claimReview.itemReviewed = review._source.itemReviewed || null;
    // claimReview.references = review._source.references || null;
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

  // console.log("here")

   if (info.identifier){
    es.query.match = {};
    es.query.match.identifier = info.identifier;
  }
  else if (info.text){
      es.query.more_like_this = {};
      es.query.more_like_this.min_term_freq = 1;
      es.query.more_like_this.min_doc_freq = 1;
      es.query.more_like_this.fields = ["text"];
      es.query.more_like_this.like = [removeStopWords(info.text)];
      if (info.topics) {
        es.query.more_like_this.fields = ["text", "about"];
        es.query.more_like_this.like = [removeStopWords(info.text), info.topics.toString()];
      }
   }
  //  console.log("asdasdsd")
  //  console.log(JSON.stringify(es))

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
          // console.log("returned")
           return result.json();
       })
       .then(function(json){
        //  console.log(json.hits.total.value)

        if (json.hits.total.value > 0){
        //  console.log("hererer")
         
             if (!info.identifier){
              // console.log("topics")
               
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
               
              //  console.log("id")
                var moreLikeThis = {};
                moreLikeThis.size = 5;
                moreLikeThis.query = {};
                moreLikeThis.query.more_like_this = {};
                moreLikeThis.query.more_like_this.min_term_freq = 1;
                moreLikeThis.query.more_like_this.min_doc_freq = 1;
                moreLikeThis.query.more_like_this.fields = ["text", "about"];
               // moreLikeThis.query.more_like_this.fields.push("text");
                moreLikeThis.query.more_like_this.like = {};
                moreLikeThis.query.more_like_this.like._index = "fdg-claim";
                // moreLikeThis.query.more_like_this.like._type = "doc";
                moreLikeThis.query.more_like_this.like._id = json.hits.hits[0]._id;
 
              //  console.log(JSON.stringify(moreLikeThis))
 
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

                    if (json.hits.total.value > 0){

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
   //   console.log("---------------")
      var claimQuery = {};
      claimQuery.query = {};
      claimQuery.query.match = {};
      claimQuery.query.match.itemReviewed = claim.identifier;

     // console.log(claimQuery)

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
      // console.log("author")
      // console.log(author)
       var authorQuery = {};
       authorQuery.query = {};
       authorQuery.query.match = {};
       authorQuery.query.match.identifier = author;
 
     //  console.log(authorQuery)
 
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
      // console.log("pub")
      // console.log(publisher)
       var publisherQuery = {};
       publisherQuery.query = {};
       publisherQuery.query.match = {};
       publisherQuery.query.match.identifier = publisher;
 
      // console.log(publisherQuery)
 
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

     function getCalculatedRating(articleID){

       var ratingQuery = {};
       ratingQuery.query = {};
       ratingQuery.query.match = {};
       ratingQuery.query.match.identifier = articleID;
 
      // console.log(JSON.stringify(ratingQuery))
 
       var url = "http://localhost:9220/fdg-article-fusionscore/doc/_search"
       return fetch(url,
         {
             method: 'POST',
             body: JSON.stringify(ratingQuery),
             headers:{
                 'Content-Type': 'application/json',
             }
         })
         .then(function(result){
          //  console.log(result.json())
             return result.json();
         })
         .then(function(json){
           console.log(json.hits.hits)
           var response = {};
           response.id = articleID;
           response.data = json.hits.hits;
           return Promise.resolve(response);
         })
     }


