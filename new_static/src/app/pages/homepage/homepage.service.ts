import { Injectable } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {Observable} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class HomepageService {

    constructor(private http: HttpClient) {
    }

    uploadImage(to_send: object): Observable<Object> {
        return this.http.post('/upload_image', to_send);
    }

}
