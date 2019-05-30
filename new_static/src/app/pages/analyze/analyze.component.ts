import {Component, OnInit} from '@angular/core';
import {NgxSpinnerService} from 'ngx-spinner';
import {Router} from '@angular/router';
import {AnalyzeService} from './analyze.service';
import {AppService} from '../../app.service';

@Component({
    selector: 'app-search',
    templateUrl: './analyze.component.html',
    styleUrls: ['./analyze.component.scss']
})
export class AnalyzeComponent implements OnInit {

    constructor(private spinner: NgxSpinnerService, private service: AnalyzeService, private router: Router) { }


    ngOnInit() { }

    // LISTENER CALLED FROM ROUTER OUTLET CHILDREN FOR SHOW AND HIDE SPINNER ON LOADING
    // IMPORTANT : EVERY ANALYZE ROUTES HAVE TO CALL THIS METHOD TO SHOW SPINNER!
    onActivate(elementRef) {
        elementRef.showLoading.subscribe(event => {
            // IF TRUE SHOW SPINNER, ELSE HIDE IT
            if (event) {
                this.spinner.show();
            } else {
                this.spinner.hide();
            }
        });
    }

    // LISTENER ON NAVBAR EMITTER
    newSearch(params) {
        AppService.prepareUrlToBlankPage(this.router, `/analyze/${params.type}`,  {url: params.url});
    }

}
