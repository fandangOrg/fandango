import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {BrowserModule} from '@angular/platform-browser';
import {Routes, RouterModule} from '@angular/router';

import {AnalyzeComponent} from './pages/analyze/analyze.component';
import {HomepageComponent} from './pages/homepage/homepage.component';

const routes: Routes = [
    {
        path: '',
        redirectTo: 'homepage',
        pathMatch: 'full',
    }, {
        path: 'homepage',
        component: HomepageComponent
    },
    {
        path: 'analyze',
        component: AnalyzeComponent,
        loadChildren: './pages/analyze/analyze.module#AnalyzeModule'
    },
    {
        path: '**',
        redirectTo: 'homepage'
    }
];

@NgModule({
    imports: [
        CommonModule,
        BrowserModule,
        RouterModule.forRoot(routes)
    ],
    exports: [],
})
export class AppRoutingModule {
}
