import {Component, EventEmitter, OnInit, Output} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {AnalyzeService} from '../analyze.service';
import {AppService} from '../../../app.service';
import {Article} from './article';

@Component({
    selector: 'app-article',
    templateUrl: './article.component.html',
    styleUrls: ['./article.component.scss']
})
export class ArticleComponent implements OnInit {

    // EMITTER FOR ANALYZE COMPONENT ( PARENT ) TO SHOW SPINNER FOR PRELOADING
    @Output() showLoading = new EventEmitter<boolean>();
    url: string;
    showMore: boolean;
    article: Article;

    constructor(private router: ActivatedRoute, private http: AnalyzeService, private route: Router) {

        this.showMore = false;

        // RETRIEVE URL FROM QUERY PARAMS
        this.url = this.http.retrieveUrl(this.router);

        // IF PARAMS IS UNDEFINED OR NULL REDIRECT TO HOMEPAGE
        if (!this.url) {
            this.route.navigate(['/homepage']);
        }
    }

    ngOnInit() {

        // const x = {
        //     "identified": "335f8db2a7e1751a016d99becd3019c8",
        //     "language": "en",
        //     "headline": "Bernie Sanders announces run for presidency in 2020: 'We're gonna win'",
        //     "body": "Bernie Sanders, the independent senator from Vermont whose 2016 presidential campaign helped energize the progressive movement and
        //     reshaped the Democratic party, has entered the 2020 race for the White House.  Sanders, a self-styled democratic socialist who spent much of his
        //     nearly 30-year congressional career on the political fringe, cast his candidacy as the best way to accomplish the mission he started three years
        //     ago when he ran against Hillary Clinton for the Democratic nomination.  Get a new perspective on the US. Sign up for the morning briefing
        //     Read more  “Together, you and I and our 2016 campaign began the political revolution,” he said in an email announcing his decision to supporters
        //     on Tuesday morning. “Now, it is time to complete that revolution and implement the vision that we fought for.”  Sanders, 77, running as a Democrat again,
        //     believes he can prevail in a crowded and diverse field that includes several female and minority candidates, and then beat Donald Trump,
        //     whom he called on Tuesday “the most dangerous president in modern American history”.  Asked in an interview on CBS on Tuesday morning what would
        //     be different about his 2020 campaign, Sanders replied: “We’re gonna win.”  Whether he can once again capture grassroots support, and whether the
        //     energy of his past campaign will pass to other candidates, will likely be a central factor in determining who Democrats nominate to take on the
        //     sitting president.  The progressive policies Sanders helped popularize in 2016 – Medicare for All, a $15-an-hour federal minimum wage, tuition-free
        //     college, demands to fight climate change more aggressively and to tax the wealthy at a higher rate – have now been broadly embraced by several other
        //     presidential candidates.  Sanders wrore: “Three years ago, during our 2016 campaign, when we brought forth our progressive agenda we were told that
        //     our ideas were ‘radical’ and ‘extreme’. Well, three years have come and gone. And, as result of millions of Americans standing up and fighting back,
        //     all of these policies and more are now supported by a majority of Americans.”  Who's running in 2020? The full list of Democrats vying to take on
        //     Trump Read more  Sanders will face opposition from moderate Democrats and from Republicans who are likely to use his candidacy to paint the party.",
        //     "images": [
        //     {
        //         "calculatedRating": 0,
        //         "calculatedRatingDetail": [],
        //         "contentSize": "43B",
        //         "contentUrl": "https://sb.scorecardresearch.com/p?c1=2&c2=6035250&cv=2.0&cj=1&comscorekw=Bernie+Sanders%2CUS+news%2CDemocrats%2CUS+elections+2020%2CDonald+Trump%2CWorld+news%2CUS+politics",
        //         "encodingFormat": "image/gif",
        //         "identifier": "496515a4711fd6cf03c733c58eb08bc7f3ae40ad62459d95d207c76fda60d7a5",
        //         "status": "done",
        //         "type": "image",
        //         "uploadDate": null
        //     },
        //     {
        //         "calculatedRating": 0,
        //         "calculatedRatingDetail": [],
        //         "contentSize": "42B",
        //         "contentUrl": "https://googleads.g.doubleclick.net/pagead/viewthroughconversion/971225648/?value=0&guid=ON&script=0",
        //         "encodingFormat": "image/gif",
        //         "identifier": "236b70d883189975e9557a2caf6dc643d2018f19dde590e4d73e5ccd14f46132",
        //         "status": "done",
        //         "type": "image",
        //         "uploadDate": null
        //     },
        //     {
        //         "calculatedRating": 0.4304603537,
        //         "calculatedRatingDetail": [
        //             {
        //                 "analyzer": "busterNet",
        //                 "bboxes": [],
        //                 "scores": []
        //             },
        //             {
        //                 "analyzer": "faceForensics",
        //                 "bboxes": [
        //                     [
        //                         348,
        //                         63,
        //                         669,
        //                         384
        //                     ]
        //                 ],
        //                 "scores": [
        //                     0.4271566868
        //                 ]
        //             },
        //             {
        //                 "analyzer": "maskRCNN",
        //                 "bboxes": [
        //                     [
        //                         470,
        //                         851,
        //                         630,
        //                         1100
        //                     ],
        //                     [
        //                         457,
        //                         1025,
        //                         586,
        //                         1197
        //                     ]
        //                 ],
        //                 "scores": [
        //                     0.8797424436,
        //                     0.848706305
        //                 ]
        //             }
        //         ],
        //         "contentSize": "75K",
        //         "contentUrl": "https://i.guim.co.uk/img/media/3d237a03ae3fec77bbc5cb038ff90a70ab563ff9/0_225_5184_3110/master/5184.jpg?width=1200&height=630&quality=85&auto=format&fit=crop&overlay-align=bottom%2Cleft&overlay-width=100p&overlay-base64=L2ltZy9zdGF0aWMvb3ZlcmxheXMvdGctZGVmYXVsdC5wbmc&s=63ca26e730005fbd92732e40fdc60dde",
        //         "encodingFormat": "image/jpeg",
        //         "identifier": "952897f6272339f2ae0ac4d3c319aa62341f68c6fe5dc974cff2d4c2b9bfc4d7",
        //         "status": "done",
        //         "type": "image",
        //         "uploadDate": null
        //     },
        //     {
        //         "calculatedRating": 0,
        //         "calculatedRatingDetail": [],
        //         "contentSize": "35B",
        //         "contentUrl": "https://phar.gu-web.net/count/pvg.gif",
        //         "encodingFormat": "image/gif",
        //         "identifier": "cd2bae46b93790e4034da148380c6a8545db0312ebbcf5c8f9b9d8893362fac5",
        //         "status": "done",
        //         "type": "image",
        //         "uploadDate": null
        //     },
        //     {
        //         "calculatedRating": 0,
        //         "calculatedRatingDetail": [],
        //         "contentSize": "35B",
        //         "contentUrl": "https://phar.gu-web.net/count/pv.gif",
        //         "encodingFormat": "image/gif",
        //         "identifier": "b4fe42595afc3fba410881ab39854f7e73b6fc5c0a787fed60847293dcf86d5a",
        //         "status": "done",
        //         "type": "image",
        //         "uploadDate": null
        //     }
        // ],
        //     "videos": [
        //     {
        //         "contentSize": "28M",
        //         "contentUrl": "https://www.youtube.com/watch?v=s7DRwz0cAt0",
        //         "encodingFormat": "video/mp4",
        //         "first_frame": 0,
        //         "fps": 3,
        //         "identifier": "6104b96c61fc1d836851d672f1f4add1f931a88105d418e182bcbf47f6899dfb",
        //         "last_frame": 0,
        //         "status": "download",
        //         "type": "video",
        //         "uploadDate": "2019-02-19T11:58:16Z"
        //     }
        // ],
        //     "publishers": [
        //     {
        //         "affiliation": "",
        //         "fakenessScore": 62.56,
        //         "name": "The Guardian",
        //         "url": "w"
        //     }
        // ],
        //     "authors": [
        //     {
        //         "affiliation": [
        //             "The Guardian"
        //         ],
        //         "fakenessScore": 53.74,
        //         "jobTitle": "",
        //         "name": "Lauren Gambino",
        //         "url": ""
        //     },
        //     {
        //         "affiliation": [
        //             "The Guardian"
        //         ],
        //         "fakenessScore": 53.74,
        //         "jobTitle": "",
        //         "name": "Tom Mccarthy",
        //         "url": ""
        //     }
        // ],
        //     "textAnalysis": [
        //     {
        //         "0": 0.6261177973,
        //         "1": 0.3738822027,
        //         "title_AVGWordsCounter": 0.1571428571,
        //         "title_PunctuationCounter": 0.0571428571,
        //         "title_StopwordCounter": 0.1428571429,
        //         "title_POSDiversity": 0.1896551724,
        //         "text_AVGSentencesSizeCounter": 29.9,
        //         "text_AVGWordsCounter": 0.1609267376,
        //         "text_PunctuationCounter": 0.020507201,
        //         "text_LexicalDiversity": 0.4464882943,
        //         "text_FleschReadingEase": 47.0400117057,
        //         "text_FKGRadeLevel": 14.1261839465,
        //         "text_POSDiversity": 0.724137931,
        //         "text_StopwordCounter": 0.3386287625,
        //         "text_AveWordxParagraph": 1027,
        //         "text_CountAdv": 0.049137931,
        //         "text_CountAdj": 0.0887931034,
        //         "text_CountPrep_conj": 0.1353448276,
        //         "text_countVerbs": 0.1327586207
        //     }
        // ]
        // }






        // SEND TRUE TO EMIT LISTENER AND SHOW SPINNER
        this.showLoading.emit(true);

        // CRAWLING AND ANALYZE ARTICLE REQUEST
        this.http.analyzeArticle(this.url).subscribe(
            data => {
                this.showLoading.emit(false);

                this.article = new Article(data['identifier'], data['language'], data['headline'], data['articleBody'], data['results']['images'],
                    data['results']['videos'], data['results']['publishers'], data['results']['authors'], data['results']['text']);

                console.log(this.article);

            }, error => {
                this.showLoading.emit(false);
                this.route.navigate(['/homepage']);
                AppService.showNotification('danger', 'Error occured, retry later.');
            }
        );
    }

    analyzeImage(urlImage: string) {
        AppService.prepareUrlToBlankPage(this.route, 'analyze/image', {url: urlImage});
    }
}
