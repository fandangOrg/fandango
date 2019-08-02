import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {NavbarComponent} from './navbar/navbar.component';
import {FooterComponent} from './footer/footer.component';
import {RouterModule} from '@angular/router';
import {NgbModule} from '@ng-bootstrap/ng-bootstrap';
import {SpinnerComponent} from './spinner/spinner.component';
import {FormsModule} from '@angular/forms';
import {SidebarComponent} from "./sidebar/sidebar.component";

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
        SidebarComponent,
        SpinnerComponent
    ],
    exports: [
        FooterComponent,
        NavbarComponent,
        SidebarComponent,
        SpinnerComponent
    ]
})
export class ComponentsModule {
}
