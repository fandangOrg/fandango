import {Component, EventEmitter, OnInit, Output} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {Button, Buttons} from "../../app.config";

@Component({
    selector: 'app-navbar',
    templateUrl: './navbar.component.html',
    styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit {

    url: string;    // URL INSERT IN NAVBAR INPUT AREA
    @Output() newSearch = new EventEmitter<object>();   // EMITTER WHEN A NEW SEARCH IS MADE FROM THE NAVBAR
    buttonList: Array<Button>;
    typeAnalyze: string;
    fandangoLogo: string;
    inputPlaceholder: string;

    constructor(private router: Router, private activatedRoute: ActivatedRoute) {
        this.fandangoLogo = 'assets/img/logos/fandango.png';
        this.buttonList = Buttons;
        this.inputPlaceholder = '';

        // RETRIEVE TYPE ANALYZE AND URL FROM CHILDREN PARAMS
        this.activatedRoute.children[0].url.subscribe(params => {
            this.typeAnalyze = params[0]['path'];
            this.url = params[0]['parameters']['url'];
        });
    }

    ngOnInit() {
    }

    navigateToHomepage(buttonType: string) {
        if (buttonType !== this.typeAnalyze) {
            this.router.navigate(['homepage'], {queryParams: {'search': buttonType}});
        }
    }

    sendInput() {
        // EMIT ANALYZE EVENT WHEN TRIGGER SEARCH BUTTON ON NAVBAR, SENDING AS PARAMETERS TYPE AND URL TO ANALYZE COMPONENT
        this.newSearch.emit({type: this.typeAnalyze, url: this.url});
    }


}
