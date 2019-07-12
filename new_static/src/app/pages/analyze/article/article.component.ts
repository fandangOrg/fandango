import {Component, EventEmitter, OnInit, Output} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {AnalyzeService} from '../analyze.service';
import {AppService} from '../../../app.service';
import {Article} from './article';
import {sirenUrl} from "../../../app.config";
import {DomSanitizer} from "@angular/platform-browser";
import {NgbModal} from "@ng-bootstrap/ng-bootstrap";

@Component({
    selector: 'app-article',
    templateUrl: './article.component.html',
    styleUrls: ['./article.component.scss']
})
export class ArticleComponent implements OnInit {

    // EMITTER FOR ANALYZE COMPONENT ( PARENT ) TO SHOW SPINNER FOR PRELOADING
    @Output() showLoading = new EventEmitter<boolean>();
    url: string;
    infoTooltip: string;
    sirenUrl: string;
    showMore: boolean;
    isOld: boolean;
    article: Article;

    constructor(private router: ActivatedRoute, private http: AnalyzeService, private route: Router, private sanitizer: DomSanitizer, private modalService: NgbModal) {

        this.showMore = false;
        this.isOld = false;
        this.sirenUrl = sirenUrl;
        // RETRIEVE URL FROM QUERY PARAMS
        this.url = this.http.retrieveUrl(this.router);

        // CHECK IF OLD QUERY PARAMS EXIST
        if (this.router.url['value'][0]['parameters']['old']) {
            this.isOld = true;
        }

        // IF PARAMS IS UNDEFINED OR NULL REDIRECT TO HOMEPAGE
        if (!this.url) {
            this.route.navigate(['/homepage']);
        }
    }

    ngOnInit() {
        // SEND TRUE TO EMIT LISTENER AND SHOW SPINNER
        this.showLoading.emit(true);


        let urlString = null;

        // IF IS OLD PARAMS EXIST MAKE AN ANALYSIS WITHOUT TOPICS
        if (this.isOld) {
            urlString = 'preAnalyzeArticle';
        } else {
            urlString = 'analyzeArticle';
        }

        // CRAWLING AND ANALYZE ARTICLE REQUEST
        this.http[urlString](this.url).subscribe(
            data => {
                console.log(data);
                this.sirenUrl = this.sirenUrl.replace('QUERYDACAMBIARE', this.url);
                this.article = new Article(data['identifier'],data['datePublished'], data['language'], data['headline'], data['articleBody'], data['images'],
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

    preAnalyzeArticle(url: string) {
        AppService.prepareUrlToBlankPage(this.route, 'analyze/article', {url: url, old: true});
    }

    showTextDetailsModal(modal) {
        this.modalService.open(modal);
    }

    showDetailLabel(label: string) {
        this.infoTooltip = null;

        this.http.getDetailInfo(label).subscribe(
            data => {
                // @ts-ignore
                this.infoTooltip = data;
            }, error => {
                this.infoTooltip = 'No info found';
            })
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
