import {Routes} from '@angular/router';
import {ArticleComponent} from './article/article.component';
import {ImageComponent} from './image/image.component';
import {VideoComponent} from './video/video.component';
import {ClaimComponent} from './claim/claim.component';

export const AnalyzeRoutes: Routes = [
    {path: 'article', component: ArticleComponent},
    {path: 'image', component: ImageComponent},
    {path: 'video', component: VideoComponent},
    {path: 'claim', component: ClaimComponent},
    {path: '**', redirectTo: '/homepage', pathMatch: 'full'},
];
