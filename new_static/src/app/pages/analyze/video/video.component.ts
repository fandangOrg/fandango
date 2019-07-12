import {Component, EventEmitter, OnDestroy, OnInit, Output, Pipe, PipeTransform} from '@angular/core';
import {AnalyzeService} from "../analyze.service";
import {ActivatedRoute, Router} from "@angular/router";
import {DomSanitizer} from "@angular/platform-browser";
import {NgxSpinnerService} from "ngx-spinner";
import {AppService} from "../../../app.service";

@Pipe({ name: 'urlSafe' })
export class SafePipe implements PipeTransform {
    constructor(private sanitizer: DomSanitizer) {}
    transform(url) {
        return this.sanitizer.bypassSecurityTrustResourceUrl(url);
    }
}

@Component({
    selector: 'app-video',
    templateUrl: './video.component.html',
    styleUrls: ['./video.component.scss']
})
export class VideoComponent implements OnInit, OnDestroy {

    @Output() showLoading = new EventEmitter<boolean>();
    url: string;
    video: object;
    interval: any;

    constructor(private http: AnalyzeService, private router: ActivatedRoute, private route: Router, private sanitizer: DomSanitizer, private spinner: NgxSpinnerService) {
        this.url = this.http.retrieveUrl(this.router);

        // IF PARAMS IS UNDEFINED OR NULL REDIRECT TO HOMEPAGE
        if (!this.url) {
            this.route.navigate(['/homepage']);
        }
    }

    ngOnInit() {
        this.showLoading.emit(true);

        this.http.analyzeVideo(this.url).subscribe(
            data => {
                console.log(data);

                // GET IDENTIFIER AND SEND IT TO ANALYZER SERVICE
                let tempVideo = data['videos'][0];

                this.http.getVideoScore(data['videos'][0]).subscribe(
                    data => {
                        this.video = data;
                        console.log(this.video);
                        this.showLoading.emit(false);

                        // CHECK ANALYZE STATUS
                        if (this.video['status'] === 'error') {
                            this.route.navigate(['/homepage']);
                            AppService.showNotification('danger', `Error occured during analyzing video, ${this.video['error']}`);
                        } else if (this.video['status'] !== 'done')
                            // IF STATUS NOT DONE PING SERVICE EVERY 5 SECONDS
                            this.checkStatus(tempVideo);
                    }
                )
            }
        )
    }

    ngOnDestroy() {
        // this.observableRef.unsubscribe();
        clearInterval(this.interval);
    }

    getColor(score: number) {
        return AppService.getScoreColor(score);
    }

    checkStatus(video) {
        // ASSIGN THIS TO SELF FOR USE IT IN INTERVAL FUNCTION
        const self = this;

        setTimeout(() => this.spinner.show('spinnerVideo'), 25);

        self.interval = window.setInterval(function () {
            self.http.getVideoScore(video).subscribe(
                data => {
                    if (data['status'] === 'done') {
                        self.video = data;
                        console.log(self.video);
                        setTimeout(() => self.spinner.hide('spinnerVideo'), 25);
                        // EXIT FROM LOOP
                        clearInterval(self.interval);
                    } else if (data['status'] === 'error') {
                        self.route.navigate(['/homepage']);
                        AppService.showNotification('danger', `Error occured during analyzing video, ${data['error']}`);
                    } else {
                        console.log("ANALYZING -->", data['status']);
                    }
                }
            )
        }, 5000);
    }

    // checkStatus(video) {
    //      this.observableRef = interval(5000)
    //         .subscribe(() => {
    //             this.http.getVideoScore(video['videos'][0]).subscribe(
    //                 data => {
    //                     if (data['status'] === 'done') {
    //                         console.log("end");
    //                         this.video = data;
    //                         this.observableRef.unsubscribe();
    //                     } else {
    //                         console.log("ANALYZING");
    //                     }
    //                 })
    //         });
    // }

    embedVideo(url) {
        url = url.replace("watch?v=", "embed/");
        return url;
    }

    isEmptyObject(obj){
        return (Object.getOwnPropertyNames(obj).length === 0);
    }

}
