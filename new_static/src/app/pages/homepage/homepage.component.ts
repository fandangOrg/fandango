import {Component, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {Button, Buttons} from "../../app.config";
import {AppService} from "../../app.service";

@Component({
    selector: 'app-homepage',
    templateUrl: './homepage.component.html',
    styleUrls: ['./homepage.component.scss']
})

export class HomepageComponent implements OnInit {
    typeAnalyze: string;    // TYPE ANALYZE BASED ON BUTTON SELECTED
    inputType: object;  // OBJECT THAT CONTAINS PATTERN AND INPUT TYPE FOR TEXTBOX
    fandangoLogo: string;
    inputPlaceholder: string;   // PLACEHOLDER ON INPUT
    buttonList: Array<Button>;  // BUTTON LIST
    buttonType: Array<string> = ['article', 'image', 'video', 'claim'];

    constructor(private router: Router, private activatedRoute: ActivatedRoute) {
        this.fandangoLogo = 'assets/img/logos/fandango.png';
        this.buttonList = Buttons;
        this.activatedRoute.queryParams.subscribe(params => {
            if (params.search && this.buttonType.includes(params.search)) {
                this.typeAnalyze = params.search;
            } else {
                this.typeAnalyze = 'article';
            }

            this.inputType = AppService.getInputType(this.typeAnalyze);

            const button = this.buttonList.find(obj => {
                return obj['type'] === this.typeAnalyze
            });

            this.inputPlaceholder = (button.placeholder || 'Article URL');
        });
    }

    ngOnInit() {
    }


    // FUNCTION CALLED WHEN BUTTON IS CHANGED
    changeButton(button: Button) {
        this.typeAnalyze = button.type;
        this.inputPlaceholder = button.placeholder;
        this.inputType = AppService.getInputType(button.type);
        this.router.navigate(['homepage'], {queryParams: {'search': button.type}});
    }

    sendInput(form) {
        // ON SUBMIT NAVIGATE TO ANALYZE TYPE WITH URL AS QUERY PARAMS
        if (form.valid)
            this.router.navigate([`analyze/${this.typeAnalyze}`, {url: form.value.url}]);
    }
}
