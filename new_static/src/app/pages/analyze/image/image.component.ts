import {Component, EventEmitter, OnDestroy, OnInit, Output} from '@angular/core';
import {AnalyzeService} from "../analyze.service";
import {ActivatedRoute, Router} from "@angular/router";
import {Log} from "@angular/core/testing/src/logger";
import {NgxSpinnerService} from "ngx-spinner";
import {AppService} from "../../../app.service";

@Component({
    selector: 'app-image',
    templateUrl: './image.component.html',
    styleUrls: ['./image.component.scss']
})
export class ImageComponent implements OnInit, OnDestroy {

    @Output() showLoading = new EventEmitter<boolean>();
    url: string;
    image: object;
    interval: any;

    constructor(private http: AnalyzeService, private router: ActivatedRoute, private route: Router, private spinner: NgxSpinnerService) {
        this.url = this.http.retrieveUrl(this.router);

        // IF PARAMS IS UNDEFINED OR NULL REDIRECT TO HOMEPAGE
        if (!this.url) {
            this.route.navigate(['/homepage']);
        }
    }

    ngOnDestroy() {
        // this.observableRef.unsubscribe();
        clearInterval(this.interval);
    }

    ngOnInit() {

        this.showLoading.emit(true);

        this.http.analyzeImage(this.url).subscribe(
            data => {
                let tempImage = data['images'][0];
                this.http.getImageScore(data['images'][0]).subscribe(
                    data => {
                        this.image = data;
                        console.log(this.image);
                        this.showLoading.emit(false);

                        if (this.image['status'] !== 'done')
                            this.checkStatus(tempImage);
                    }
                )
            }
        )
    }

    getColor(score: number) {
        return AppService.getScoreColor(score * 100);
    }

    checkStatus(image) {
        const self = this;

        setTimeout(() => this.spinner.show('spinnerImage'), 25);

        self.interval = window.setInterval(function () {
            self.http.getImageScore(image).subscribe(
                data => {
                    if (data['status'] === 'done') {
                        self.image = data;
                        console.log(self.image);
                        setTimeout(() => self.spinner.hide('spinnerImage'), 25);
                        clearInterval(self.interval);
                    } else {
                        console.log("ANALYZING");
                    }
                }
            )
        }, 5000);
    }
}
