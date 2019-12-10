import {Component, EventEmitter, OnDestroy, OnInit, Output} from '@angular/core';
import {AnalyzeService} from "../analyze.service";
import {ActivatedRoute, Router} from "@angular/router";
import {ImageInfoLabels} from "../../../app.config";
import {NgxSpinnerService} from "ngx-spinner";
import {AppService} from "../../../app.service";
import {NgbModal} from "@ng-bootstrap/ng-bootstrap";

@Component({
    selector: 'app-image',
    templateUrl: './image.component.html',
    styleUrls: ['./image.component.scss']
})
export class ImageComponent implements OnInit, OnDestroy {

    @Output() showLoading = new EventEmitter<boolean>();
    url: string;
    image: object;
    modalImage: string;
    interval: any;
    imageLabels: object[];
    infoTooltip: string;

    constructor(private http: AnalyzeService, private router: ActivatedRoute, private route: Router, private spinner: NgxSpinnerService, private modalService: NgbModal) {
        this.imageLabels = ImageInfoLabels;

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
                console.log(data);
                const tempImage = data['identifier'];
                this.http.getImageScore(tempImage).subscribe(
                    data => {
                        this.image = data;
                        console.log(this.image);
                        this.showLoading.emit(false);

                        if (this.image['status'] === 'error') {
                            this.route.navigate(['/homepage']);
                            // AppService.showNotification('danger', 'Error occured during analyzing image');
                            AppService.showNotification('danger', `Error during analyzing image, ${this.image['error']}`)
                        } else if (this.image['status'] !== 'done')
                            this.checkStatus(tempImage);
                    }
                )
            }
        )
    }

    showDetailLabel(label: string) {
        this.infoTooltip = null;

        const obj = this.imageLabels.find(value => value['key'] === label);

        this.infoTooltip = obj['value'];

        // this.infoTooltip = Object.keys(this.imageLabels).find(key => this.imageLabels[key] === label);
    }

    zoomImage(modal: any, image: string) {
        this.modalImage = image;
        this.modalService.open(modal, {
            size: 'lg',
            centered: true
        });
    }

    getColor(score: number) {
        return AppService.getScoreColor(score);
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
                    } else if (data['status'] === 'error') {
                        self.route.navigate(['/homepage']);
                        AppService.showNotification('danger', `Error during analyzing image, ${data['error']}`)
                    } else {
                        console.log("ANALYZING -->", data['status']);
                    }
                }
            )
        }, 5000);
    }
}
