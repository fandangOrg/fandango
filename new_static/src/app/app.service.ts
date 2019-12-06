import {Injectable} from '@angular/core';
import {DomSanitizer} from "@angular/platform-browser";

declare var $: any;

@Injectable({
    providedIn: 'root'
})
export class AppService {

    constructor() {
    }

    private static sanitizer: DomSanitizer;

    static showNotification(type: string, message: string) {
        $.notify({
            // options
            message: message
        }, {
            // settings
            type: type,
            placement: {
                from: 'top',
                align: 'left'
            },
        });
    }

    static prepareUrlToBlankPage(routeModule: any, routes: string, queryParams?: object) {
        let url = '';
        if (queryParams) {
            // GENERATE URL WITH PARAMS RECEIVED FROM NAVBAR OR OTHER COMPONENT
            url = routeModule.createUrlTree([routes, queryParams]);
        } else {
            // GENERATE URL WITH PARAMS RECEIVED FROM NAVBAR OR OTHER COMPONENT
            url = routeModule.createUrlTree([routes]);
        }

        // OPEN URL IN NEW BLANK PAGE
        window.open(url.toString(), '_blank');
    }

    static getScoreColor(score: number) {
        switch (true) {
            case score <= 33:
                return 'text-danger';
            case score <= 66:
                return 'text-yellow';
            default:
                return 'text-success'
        }
    }

    static getProgressColor(score: number) {
        switch (true) {
            case score <= 33:
                return 'bg-danger';
            case score <= 66:
                return 'bg-yellow';
            default:
                return 'bg-success'
        }
    }

    // RETRIEVE INPUT TYPE BASED ON BUTTON TYPE CLICKED
    static getInputType(type: string) {
        if (type === 'claim') {
            return {type: 'text', pattern: ''}
        } else if (type === 'image') {
            return {type: 'url', pattern: 'https?:\\/\\/.*\\.(?:png|jpg|jpeg)'}
        } else {
            return {type: 'url', pattern: 'https?://.+'}
        }
    }

    static embedVideo(url) {
        url = url.replace("watch?v=", "embed/");
        return this.sanitizer.bypassSecurityTrustResourceUrl(url);
    }
}
