import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {RouterModule} from '@angular/router';
import {AnalyzeRoutes} from './analyze.routing';
import {ArticleComponent} from './article/article.component';
import {ImageComponent} from './image/image.component';
import {VideoComponent} from './video/video.component';
import {ClaimComponent} from './claim/claim.component';
import {TruncateModule} from 'ng2-truncate';

@NgModule({
    declarations: [
        ArticleComponent,
        ImageComponent,
        VideoComponent,
        ClaimComponent,
    ],
    imports: [
        CommonModule,
        RouterModule.forChild(AnalyzeRoutes),
        TruncateModule
    ]
})
export class AnalyzeModule {
}
