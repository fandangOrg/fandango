import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {RouterModule} from '@angular/router';
import {AnalyzeRoutes} from './analyze.routing';
import {ArticleComponent} from './article/article.component';
import {ImageComponent} from './image/image.component';
import {SafePipe, VideoComponent} from './video/video.component';
import {ClaimComponent} from './claim/claim.component';
import {TruncateModule} from 'ng2-truncate';
import {NgxJsonViewerModule} from "ngx-json-viewer";
import {NgxSpinnerModule} from "ngx-spinner";
import {NgbModule} from "@ng-bootstrap/ng-bootstrap";


@NgModule({
    declarations: [
        ArticleComponent,
        ImageComponent,
        VideoComponent,
        ClaimComponent,
        SafePipe
    ],
    imports: [
        CommonModule,
        RouterModule.forChild(AnalyzeRoutes),
        TruncateModule,
        NgxJsonViewerModule,
        NgxSpinnerModule,
        NgbModule,
    ]
})
export class AnalyzeModule {
}
