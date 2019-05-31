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
        // SEND TRUE TO EMIT LISTENER AND SHOW SPINNER
        this.showLoading.emit(true);

        // CRAWLING AND ANALYZE ARTICLE REQUEST
        this.http.analyzeArticle(this.url).subscribe(
            data => {
                this.showLoading.emit(false);

                // console.log(data);

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

    getProgressColor(value: number) {
        return AppService.getProgressColor(value);
    }

    analyzeImage(urlImage: string) {
        AppService.prepareUrlToBlankPage(this.route, 'analyze/image', {url: urlImage});
    }
}
