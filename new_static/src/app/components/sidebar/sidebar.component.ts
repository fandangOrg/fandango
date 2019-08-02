import {Component, OnInit} from '@angular/core';
import {Router} from '@angular/router';

declare interface RouteInfo {
    path: string;
    title: string;
    params: string,
    icon: string;
    class: string;
}

export const ROUTES: RouteInfo[] = [
    {path: '/article', title: 'Article', params: 'article', icon: 'far fa-newspaper text-primary', class: ''},
    {path: '/image', title: 'Image', params: 'image', icon: 'fas fa-image text-blue', class: ''},
    {path: '/video', title: 'Video', params: 'video', icon: 'fas fa-video text-orange', class: ''},
    {path: '/claim', title: 'Claim', params: 'claim', icon: 'fas fa-font text-yellow', class: ''},
];

@Component({
    selector: 'app-sidebar',
    templateUrl: './sidebar.component.html',
    styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent implements OnInit {

    public menuItems: any[];
    public isCollapsed = true;

    constructor(private router: Router) {
    }

    ngOnInit() {
        this.menuItems = ROUTES.filter(menuItem => menuItem);
        this.router.events.subscribe((event) => {
            this.isCollapsed = true;
        });
    }
}
