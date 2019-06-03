import {Injectable} from '@angular/core';

declare var $: any;

@Injectable({
    providedIn: 'root'
})
export class AppService {

    constructor() {
    }

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
            case score <= 25:
                return 'text-danger';
            case score <= 50:
                return 'text-warning';
            case score <= 75:
                return 'text-yellow';
            default:
                return 'text-success'
        }
    }

    static getProgressColor(score: number) {
        switch (true) {
            case score <= 25:
                return 'bg-danger';
            case score <= 50:
                return 'bg-warning';
            case score <= 75:
                return 'bg-yellow';
            default:
                return 'bg-success'
        }
    }
}
