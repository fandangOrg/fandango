import {AfterViewInit, Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {Button, Buttons} from "../../app.config";
import {AppService} from "../../app.service";
import {NgbModal} from "@ng-bootstrap/ng-bootstrap";
import {HomepageService} from "./homepage.service";

@Component({
    selector: 'app-homepage',
    templateUrl: './homepage.component.html',
    styleUrls: ['./homepage.component.scss']
})

export class HomepageComponent implements OnInit, AfterViewInit {
    typeAnalyze: string;    // TYPE ANALYZE BASED ON BUTTON SELECTED
    inputType: object;  // OBJECT THAT CONTAINS PATTERN AND INPUT TYPE FOR TEXTBOX
    fandangoLogo: string;
    inputPlaceholder: string;   // PLACEHOLDER ON INPUT
    buttonList: Array<Button>;  // BUTTON LIST
    buttonType: Array<string> = ['article', 'image', 'video', 'claim'];
    imgFile: File;
    uploadLoading: boolean;
    imgUrl: string;

    constructor(private router: Router, private activatedRoute: ActivatedRoute, private modalService: NgbModal, private http: HomepageService) {
        this.fandangoLogo = 'assets/img/logos/fandango.png';
        this.buttonList = Buttons;
        this.imgUrl = '';
        this.imgFile = null;
        this.uploadLoading = false;
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

    ngAfterViewInit() {
    }


    toBase64 = file => new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });

    // FUNCTION CALLED WHEN BUTTON IS CHANGED
    changeButton(button: Button) {
        this.typeAnalyze = button.type;
        this.inputPlaceholder = button.placeholder;
        this.inputType = AppService.getInputType(button.type);
        this.router.navigate(['homepage'], {queryParams: {'search': button.type}});
    }

    showUploadModal(modal) {
        this.modalService.open(modal);
    }

    handleFileUpload(files: FileList) {
        this.imgFile = files.item(0);
    }

    async sendImgUpload() {
        const base64img = await this.toBase64(this.imgFile);

        const to_send = {
            url: this.imgUrl,
            image: base64img
        };

        this.uploadLoading = true;

        this.http.uploadImage(to_send).subscribe(data => {
            console.log(data);
            let result = data;
            result = result['display'].find(key => key.analyzer === 'original');
            this.uploadLoading = false;
            this.router.navigate(['analyze/image', {url: result['display']}]);
        }, error => {
            this.uploadLoading = false;
        })
    }

    sendInput(form) {
        // ON SUBMIT NAVIGATE TO ANALYZE TYPE WITH URL AS QUERY PARAMS
        if (form.valid)
            this.router.navigate([`analyze/${this.typeAnalyze}`, {url: form.value.url}]);
    }
}
