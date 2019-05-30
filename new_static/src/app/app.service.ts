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
}
