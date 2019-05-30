import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {NavbarComponent} from './navbar/navbar.component';
import {FooterComponent} from './footer/footer.component';
import {RouterModule} from '@angular/router';
import {NgbModule} from '@ng-bootstrap/ng-bootstrap';
import {SpinnerComponent} from './spinner/spinner.component';
import {FormsModule} from '@angular/forms';

@NgModule({
    imports: [
        CommonModule,
        RouterModule,
        NgbModule,
        FormsModule
    ],
    declarations: [
        FooterComponent,
        NavbarComponent,
        SpinnerComponent
    ],
    exports: [
        FooterComponent,
        NavbarComponent,
        SpinnerComponent
    ]
})
export class ComponentsModule {
}
