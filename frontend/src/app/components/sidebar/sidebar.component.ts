import { Component, Input } from '@angular/core';

import { RouterModule, Router } from '@angular/router';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';

@Component({
    selector: 'app-sidebar',
    imports: [RouterModule, MatListModule, MatIconModule],
    templateUrl: './sidebar.component.html',
    styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent {
  @Input() isCollapsed = false;

  menuItems = [
    { icon: 'home', label: 'Dashboard', route: '/dashboard' },
    { icon: 'calendar_today', label: 'Calendar', route: '/calendar' },
    { icon: 'menu_book', label: 'Books', route: '/books' },
    { icon: 'auto_stories', label: 'Manga', route: '/manga' },
    { icon: 'edit', label: 'Authors', route: '/authors' },
    { icon: 'bookmark', label: 'Want to Read', route: '/want-to-read' },
    { icon: 'layers', label: 'Library Items', route: '/library-items' },
    { icon: 'search', label: 'Search', route: '/search' },
    { icon: 'notifications', label: 'Notifications', route: '/notifications' },
    { icon: 'settings', label: 'Settings', route: '/settings' },
    { icon: 'info', label: 'About', route: '/about' }
  ];

  constructor(private router: Router) {}

  isActive(route: string): boolean {
    return this.router.url === route;
  }
}
