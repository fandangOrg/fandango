import {Component, OnInit} from '@angular/core';

@Component({
    selector: 'app-footer',
    templateUrl: './footer.component.html',
    styleUrls: ['./footer.component.scss']
})
export class FooterComponent implements OnInit {

    euLogo: string;

    constructor() {
        this.euLogo = 'assets/img/flags/eu.png';
    }

    ngOnInit() {
    }

}
