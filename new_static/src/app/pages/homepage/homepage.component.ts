import {Component, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {Button, Buttons} from "../../app.config";
import {TitleCasePipe} from "@angular/common";

@Component({
    selector: 'app-homepage',
    templateUrl: './homepage.component.html',
    styleUrls: ['./homepage.component.scss']
})

export class HomepageComponent implements OnInit {
    typeAnalyze: string;    // TYPE ANALYZE BASED ON BUTTON SELECTED
    inputType: object;
    fandangoLogo: string;
    inputPlaceholder: string;   // PLACEHOLDER ON INPUT
    buttonList: Array<Button>;  // BUTTON LIST
    buttonType: Array<string> = ['article', 'image', 'video', 'claim'];

    constructor(private router: Router, private activatedRoute: ActivatedRoute, private titlecasePipe: TitleCasePipe) {
        this.fandangoLogo = 'assets/img/logos/fandango.png';
        this.buttonList = Buttons;
        this.activatedRoute.queryParams.subscribe(params => {
            if (params.search && this.buttonType.includes(params.search)) {
                this.typeAnalyze = params.search;
            } else {
                this.typeAnalyze = 'article';
            }
            this.inputType = this.getInputType(this.typeAnalyze);
            this.inputPlaceholder = (this.titlecasePipe.transform(this.typeAnalyze) || 'Article') + ' URL';
        });
    }

    ngOnInit() {
    }

    getInputType(type: string) {
        if (type === 'claim') {
            return {type: 'text', pattern: ''}
        } else {
            return {type: 'url', pattern: 'https?://.+'}
        }
    }

    changeButton(button: Button) {
        this.typeAnalyze = button.type;
        this.inputPlaceholder = button.placeholder;
        this.inputType = this.getInputType(button.type);
        this.router.navigate(['homepage'], {queryParams: {'search': button.type}});
    }

    sendInput(form) {
        // ON SUBMIT NAVIGATE TO ANALYZE TYPE WITH URL AS QUERY PARAMS
        this.router.navigate([`analyze/${this.typeAnalyze}`, {url: form.url}]);
    }
}
