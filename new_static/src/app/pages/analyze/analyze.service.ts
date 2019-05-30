import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';

@Injectable({
    providedIn: 'root'
})
export class AnalyzeService {

    constructor(private http: HttpClient) {
    }

    retrieveUrl(router: any) {
        const params = router.url['value'][0]['parameters']['url'];
        if (params) {
            return params;
        } else {
            return false;
        }
    }

    analyzeArticle(url: string): Observable<Object> {
        return this.http.post('/crawl_and_preprocessing?url=' + url, null);
    }

    analyzeImage(url: string): Observable<Object> {
        return this.http.post('/', url);
    }

    analyzeVideo(url: string): Observable<Object> {
        return this.http.post('/', url);
    }

    analyzeClaim(url: string): Observable<Object> {
        return this.http.post('/', url);
    }

}
