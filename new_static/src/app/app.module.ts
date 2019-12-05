import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {Injectable, NgModule} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {HTTP_INTERCEPTORS, HttpClientModule, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';
import {RouterModule} from '@angular/router';
import {AppComponent} from './app.component';
import {NgbModule} from '@ng-bootstrap/ng-bootstrap';
import {AppRoutingModule} from './app.routing';
import {environment} from '../environments/environment';
import {Observable} from 'rxjs';
import {ComponentsModule} from './components/components.module';
import {AnalyzeComponent} from './pages/analyze/analyze.component';
import {HomepageComponent} from './pages/homepage/homepage.component';
import {NgxSpinnerModule} from 'ngx-spinner';

// BASE URL FOR HTTP REQUEST
@Injectable()
export class Interceptor implements HttpInterceptor {

    baseUrl = environment.baseUrl;

    intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        const url = this.baseUrl;
        req = req.clone({
            url: url + req.url
        });
        return next.handle(req);
    }
}

@NgModule({
    imports: [
        BrowserAnimationsModule,
        FormsModule,
        HttpClientModule,
        ComponentsModule,
        NgbModule,
        RouterModule,
        AppRoutingModule,
        NgxSpinnerModule
    ],
    declarations: [
        AppComponent,
        HomepageComponent,
        AnalyzeComponent
    ],
    providers: [{provide: HTTP_INTERCEPTORS, useClass: Interceptor, multi: true}],
    bootstrap: [AppComponent]
})
export class AppModule {
}
