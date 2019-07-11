import {Component, EventEmitter, OnInit, Output} from '@angular/core';
import {ActivatedRoute, Router} from "@angular/router";
import {AnalyzeService} from "../analyze.service";
import {Claim} from "./claim";
import {AppService} from "../../../app.service";

@Component({
    selector: 'app-claim',
    templateUrl: './claim.component.html',
    styleUrls: ['./claim.component.scss']
})
export class ClaimComponent implements OnInit {

    @Output() showLoading = new EventEmitter<boolean>();
    url: string;
    claims: Claim[];

    constructor(private router: ActivatedRoute, private http: AnalyzeService, private route: Router) {
        this.url = this.http.retrieveUrl(this.router);

        // IF PARAMS IS UNDEFINED OR NULL REDIRECT TO HOMEPAGE
        if (!this.url) {
            this.route.navigate(['/homepage']);
        }
    }

    ngOnInit() {
        this.showLoading.emit(true);

        const to_send = {
            'identifier': '',
            'text': this.url,
            'topics': []
        };

        // CRAWLING AND ANALYZE ARTICLE REQUEST
        this.http.analyzeClaim(to_send).subscribe(
            data => {
                console.log(data);
                this.claims = data;
                this.showLoading.emit(false);
            }, error => {
                this.showLoading.emit(false);
                this.route.navigate(['/homepage']);
                // AppService.showNotification('danger', `Error occured, status: ${error.statusText}`);
                AppService.showNotification('danger', 'Error occured during retrieve claims');
            });
    }

}
