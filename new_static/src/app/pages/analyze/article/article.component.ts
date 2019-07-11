import {Component, EventEmitter, OnInit, Output} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {AnalyzeService} from '../analyze.service';
import {AppService} from '../../../app.service';
import {Article} from './article';
import {sirenUrl} from "../../../app.config";
import {DomSanitizer} from "@angular/platform-browser";

@Component({
    selector: 'app-article',
    templateUrl: './article.component.html',
    styleUrls: ['./article.component.scss']
})
export class ArticleComponent implements OnInit {

    // EMITTER FOR ANALYZE COMPONENT ( PARENT ) TO SHOW SPINNER FOR PRELOADING
    @Output() showLoading = new EventEmitter<boolean>();
    url: string;
    sirenUrl: string;
    showMore: boolean;
    article: Article;

    constructor(private router: ActivatedRoute, private http: AnalyzeService, private route: Router, private sanitizer: DomSanitizer) {

        this.showMore = false;
        this.sirenUrl = sirenUrl;
        // RETRIEVE URL FROM QUERY PARAMS
        this.url = this.http.retrieveUrl(this.router);

        // IF PARAMS IS UNDEFINED OR NULL REDIRECT TO HOMEPAGE
        if (!this.url) {
            this.route.navigate(['/homepage']);
        }
    }

    ngOnInit() {
        // SEND TRUE TO EMIT LISTENER AND SHOW SPINNER
        this.showLoading.emit(true);

        //  this.article = {
        //     "identified": "1fea3e555d102bc8b6e81821c46694e8",
        //     "language": "it",
        //     "headline": "Italia-Francia a Nizza in segno amicizia - Ultima Ora",
        //     "body": "(ANSA) - PARIGI, 15 FEB - \"Non voglio fare ingerenze nel dibattito tra governo italiano e governo francese, ma voglio dire molto chiaramente che nei settori della cultura, dell'economia, dell'industria, nel campo sociale o nel campo sportivo abbiamo una storia condivisa: siamo le due sorelle della latinità affacciate sulle sponde del Mediterraneo. Nulla intaccherà le nostre relazioni amichevoli e fraterne\". Lo ha detto il sindaco di Nizza, Christian Estrosi, nel giorno della manifestazione dinanzi alla statua di Garibaldi per ribadire l'amicizia italo-francese, da lui indetta dopo la crisi diplomatica Parigi e Roma. \"Qualunque siano le spacconate dei governi - ha aggiunto il sindaco - noi continueremo in modo fraterno con i nostri amici italiani\".  \"Siamo una comunità unica, che devono continuare a guardare alle proprie radici comuni per costruire insieme un futuro fatto di crescita e di sviluppo\", ha sottolineato il sindaco di Cuneo Federico Borgna, presente alla cerimonia.  ",
        //     "images": [
        //         {
        //             "calculatedRating": 22.9552450486,
        //             "calculatedRatingDetail": [
        //                 {
        //                     "analyzer": "busterNet",
        //                     "bboxes": [],
        //                     "scores": []
        //                 },
        //                 {
        //                     "analyzer": "faceForensics",
        //                     "bboxes": [
        //                         [
        //                             325,
        //                             218,
        //                             361,
        //                             254
        //                         ],
        //                         [
        //                             8,
        //                             228,
        //                             60,
        //                             280
        //                         ],
        //                         [
        //                             156,
        //                             204,
        //                             199,
        //                             247
        //                         ]
        //                     ],
        //                     "scores": [
        //                         89.2082877457,
        //                         17.4379050732,
        //                         97.3491983488
        //                     ]
        //                 },
        //                 {
        //                     "analyzer": "maskRCNN",
        //                     "bboxes": [
        //                         [
        //                             56,
        //                             66,
        //                             464,
        //                             686
        //                         ]
        //                     ],
        //                     "scores": [
        //                         0.8672714233
        //                     ]
        //                 }
        //             ],
        //             "contentSize": "78K",
        //             "contentUrl": "http://www.ansa.it/webimages/img_700/2019/2/15/6f70005a8f7f141e823c853349233e33.jpg",
        //             "encodingFormat": "image/jpeg",
        //             "identifier": "90e988b98a01ef872fd64e9a02bdbff82e7c51af7b4b50e59027fb486aef1b7a",
        //             "status": "done",
        //             "type": "image",
        //             "uploadDate": "2019-02-15T13:23:17Z"
        //         },
        //         {
        //             "calculatedRating": 0.316487511,
        //             "calculatedRatingDetail": [
        //                 {
        //                     "analyzer": "busterNet",
        //                     "bboxes": [],
        //                     "scores": []
        //                 },
        //                 {
        //                     "analyzer": "faceForensics",
        //                     "bboxes": [],
        //                     "scores": []
        //                 },
        //                 {
        //                     "analyzer": "maskRCNN",
        //                     "bboxes": [
        //                         [
        //                             22,
        //                             50,
        //                             324,
        //                             448
        //                         ]
        //                     ],
        //                     "scores": [
        //                         0.949462533
        //                     ]
        //                 }
        //             ],
        //             "contentSize": "38K",
        //             "contentUrl": "http://www.ansa.it/webimages/img_457x/2019/2/15/6f70005a8f7f141e823c853349233e33.jpg",
        //             "encodingFormat": "image/jpeg",
        //             "identifier": "e8ddd5d8b1bc84635f37da7ffd83fb559ec094e947e8a6bb922ed76881657c95",
        //             "status": "done",
        //             "type": "image",
        //             "uploadDate": "2019-02-15T13:23:17Z"
        //         },
        //         {
        //             "calculatedRating": 71.5249518553,
        //             "calculatedRatingDetail": [
        //                 {
        //                     "analyzer": "busterNet",
        //                     "bboxes": [],
        //                     "scores": []
        //                 },
        //                 {
        //                     "analyzer": "faceForensics",
        //                     "bboxes": [],
        //                     "scores": []
        //                 },
        //                 {
        //                     "analyzer": "maskRCNN",
        //                     "bboxes": [
        //                         [
        //                             5,
        //                             4,
        //                             76,
        //                             110
        //                         ]
        //                     ],
        //                     "scores": [
        //                         0.8542514443
        //                     ]
        //                 }
        //             ],
        //             "contentSize": "5K",
        //             "contentUrl": "http://www.ansa.it/webimages/img_115x80/2019/6/3/1da87eee6d52c27c6560f746aa5d3ce6.jpg",
        //             "encodingFormat": "image/jpeg",
        //             "identifier": "c32dcc45652d189bfe2f584a8dfb794939776d3c3c453e4489532c36649df128",
        //             "status": "done",
        //             "type": "image",
        //             "uploadDate": "2019-06-03T06:55:09Z"
        //         },
        //         {
        //             "calculatedRating": 0,
        //             "calculatedRatingDetail": [],
        //             "contentSize": "43B",
        //             "contentUrl": "http://b.scorecardresearch.com/p?c1=2&c2=18389568&cv=2.0&cj=1",
        //             "encodingFormat": "image/gif",
        //             "identifier": "7a12b13271ae26844c1c261601b368a2d39291578826492474c41eb81b6cf0d7",
        //             "status": "done",
        //             "type": "image",
        //             "uploadDate": null
        //         },
        //         {
        //             "calculatedRating": 0.4689925909,
        //             "calculatedRatingDetail": [
        //                 {
        //                     "analyzer": "faceForensics",
        //                     "bboxes": [],
        //                     "scores": []
        //                 },
        //                 {
        //                     "analyzer": "maskRCNN",
        //                     "bboxes": [
        //                         [
        //                             2,
        //                             4,
        //                             27,
        //                             30
        //                         ]
        //                     ],
        //                     "scores": [
        //                         0.9379851818
        //                     ]
        //                 }
        //             ],
        //             "contentSize": "877B",
        //             "contentUrl": "https://cdn.flipboard.com/badges/flipboard_srrw.png",
        //             "encodingFormat": "image/png",
        //             "identifier": "ef089224fe7921367838ab782e091e556f21eb344e45915e18a314154403b551",
        //             "status": "done",
        //             "type": "image",
        //             "uploadDate": "2018-02-07T22:03:58Z"
        //         },
        //         {
        //             "calculatedRating": 0,
        //             "calculatedRatingDetail": [],
        //             "contentSize": "44B",
        //             "contentUrl": "http://secure-it.imrworldwide.com/cgi-bin/m?ci=ansa-it&cg=0&cc=0&ts=noscript",
        //             "encodingFormat": "image/gif",
        //             "identifier": "275aad315ff6ac1d4c1f8c1f5e1e14a202845db2e8a8d8da28ff4fb9861cb665",
        //             "status": "done",
        //             "type": "image",
        //             "uploadDate": null
        //         },
        //         {
        //             "calculatedRating": 74.1702497005,
        //             "calculatedRatingDetail": [
        //                 {
        //                     "analyzer": "busterNet",
        //                     "bboxes": [],
        //                     "scores": []
        //                 },
        //                 {
        //                     "analyzer": "faceForensics",
        //                     "bboxes": [],
        //                     "scores": []
        //                 },
        //                 {
        //                     "analyzer": "maskRCNN",
        //                     "bboxes": [
        //                         [
        //                             4,
        //                             21,
        //                             74,
        //                             109
        //                         ]
        //                     ],
        //                     "scores": [
        //                         0.774892509
        //                     ]
        //                 }
        //             ],
        //             "contentSize": "3K",
        //             "contentUrl": "http://www.ansa.it/webimages/img_115x80/2019/6/3/2742926fc9583b0a907ccff48986b1a3.jpg",
        //             "encodingFormat": "image/jpeg",
        //             "identifier": "27d0023d8884f67fbf554e582348208a53d1e8b8990e78c0c746758e3c7defe0",
        //             "status": "done",
        //             "type": "image",
        //             "uploadDate": "2019-06-03T07:02:40Z"
        //         },
        //         {
        //             "calculatedRating": 100,
        //             "calculatedRatingDetail": [
        //                 {
        //                     "analyzer": "busterNet",
        //                     "bboxes": [],
        //                     "scores": []
        //                 },
        //                 {
        //                     "analyzer": "faceForensics",
        //                     "bboxes": [],
        //                     "scores": []
        //                 },
        //                 {
        //                     "analyzer": "maskRCNN",
        //                     "bboxes": [],
        //                     "scores": []
        //                 }
        //             ],
        //             "contentSize": "19K",
        //             "contentUrl": "http://www.ansa.it/webimages/img_300x200/2019/6/3/c5bd31c78b2b066a80d35cdc0877b850.jpg",
        //             "encodingFormat": "image/jpeg",
        //             "identifier": "99f2bced09e47579d66fefa708215c4131f1bc9f50d53e9667269f9514b60c07",
        //             "status": "done",
        //             "type": "image",
        //             "uploadDate": "2019-06-03T07:05:34Z"
        //         }
        //     ],
        //     "videos": [],
        //     "publishers": [
        //         {
        //             "affiliation": "",
        //             "fakenessScore": 59.75,
        //             "name": "Ansa",
        //             "url": [
        //                 "w"
        //             ]
        //         }
        //     ],
        //     "authors": [
        //         {
        //             "affiliation": [
        //                 "Ansa"
        //             ],
        //             "fakenessScore": 53.74,
        //             "jobTitle": "",
        //             "name": "Redazione Ansa",
        //             "url": ""
        //         }
        //     ],
        //     "textAnalysis": [
        //         {
        //             "0": 0.4975730428,
        //             "1": 0.5024269572,
        //             "title_AVGWordsCounter": 0.1698113208,
        //             "title_PunctuationCounter": 0.0377358491,
        //             "title_StopwordCounter": 0.1818181818,
        //             "title_POSDiversity": 0.0862068966,
        //             "text_AVGSentencesSizeCounter": 35.2,
        //             "text_AVGWordsCounter": 0.1503531786,
        //             "text_PunctuationCounter": 0.0332996973,
        //             "text_LexicalDiversity": 0.7102272727,
        //             "text_FleschReadingEase": 19.6922272727,
        //             "text_FKGRadeLevel": 19.2573181818,
        //             "text_POSDiversity": 0.2931034483,
        //             "text_StopwordCounter": 0.0284090909,
        //             "text_AveWordxParagraph": 144,
        //             "text_CountAdv": 0.0057471264,
        //             "text_CountAdj": 0.0402298851,
        //             "text_CountPrep_conj": 0.0114942529,
        //             "text_countVerbs": 0
        //         }
        //     ]
        // };

        // CRAWLING AND ANALYZE ARTICLE REQUEST
        this.http.analyzeArticle(this.url).subscribe(
            data => {
                console.log(data);
                this.sirenUrl = this.sirenUrl.replace('QUERYDACAMBIARE', this.url);
                this.article = new Article(data['identifier'], data['language'], data['headline'], data['articleBody'], data['images'],
                    data['videos'], data['results']['publishers'], data['results']['authors'], data['results']['text'], data['similarnews']);

                this.showLoading.emit(false);
                console.log(this.article);

            }, error => {
                this.showLoading.emit(false);
                this.route.navigate(['/homepage']);
                // AppService.showNotification('danger', `Error occured, status: ${error.statusText}`);
                AppService.showNotification('danger', 'Error occured during analyzing article, check URL or retry later');
            }
        );
    }

    getProgressColor(value: number) {
        return AppService.getProgressColor(value);
    }

    getScoreColor(value: number) {
        return AppService.getScoreColor(value);
    }

    embedVideo(url) {
        url = url.replace("watch?v=", "embed/");
        return this.sanitizer.bypassSecurityTrustResourceUrl(url);
    }

    embedVideoThumb(url) {
        let urlSubstring = '';
        if (url.includes('?'))
            urlSubstring = url.substring(url.lastIndexOf("/") + 1, url.lastIndexOf("?"));
        else
            urlSubstring = url.substring(url.lastIndexOf("/") + 1);

        return `https://img.youtube.com/vi/${urlSubstring}/hqdefault.jpg`;
    }

    analyzeImage(urlImage: string) {
        AppService.prepareUrlToBlankPage(this.route, 'analyze/image', {url: urlImage});
    }

    analyzeVideo(urlVideo: string) {
        AppService.prepareUrlToBlankPage(this.route, 'analyze/video', {url: urlVideo});
    }
}
