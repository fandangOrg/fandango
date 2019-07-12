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
        return this.http.get(`/crawl_and_preprocessing?url=${url}`);
    }

    preAnalyzeArticle(url: string): Observable<Object> {
        // OLD TRUE PARAMS DISABLE TOPICS ANALYSIS
        return this.http.get(`/crawl_and_preprocessing?url=${url}&old=true`);
    }

    getImageScore(id: string): Observable<Object> {
        return this.http.get('/ping_image?id=' + id);
    }

    analyzeImage(url: string): Observable<Object> {
        return this.http.get('/url_image_score?url=' + url);
    }

    getVideoScore(id: string): Observable<Object> {
        return this.http.get('/ping_video?id=' + id);
    }

    analyzeVideo(url: string): Observable<Object> {
        return this.http.get('/url_video_score?url=' + url);
    }

    analyzeClaim(to_send: object): Observable<any> {
        return this.http.post('/similar_claims', to_send);
    }

}
