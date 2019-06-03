import {Component, OnInit} from '@angular/core';
import {Router} from '@angular/router';
import {Button, Buttons} from "../../app.config";

@Component({
    selector: 'app-homepage',
    templateUrl: './homepage.component.html',
    styleUrls: ['./homepage.component.scss']
})

export class HomepageComponent implements OnInit {
    typeAnalyze: string;    // TYPE ANALYZE BASED ON BUTTON SELECTED
    fandangoLogo: string;
    inputPlaceholder: string;   // PLACEHOLDER ON INPUT
    buttonList: Array<Button>;  // BUTTON LIST

    constructor(private router: Router) {
        this.fandangoLogo = 'assets/img/logos/fandango.png';
        this.buttonList = Buttons;
        this.typeAnalyze = 'article';
        this.inputPlaceholder = 'Article URL';
    }

    ngOnInit() {
    }

    sendInput(form) {
        // ON SUBMIT NAVIGATE TO ANALYZE TYPE WITH URL AS QUERY PARAMS
        this.router.navigate([`analyze/${this.typeAnalyze}`, {url: form.url}]);
    }
}
