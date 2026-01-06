import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent)
  },
  {
    path: 'collections',
    loadComponent: () => import('./pages/collections/collections.component').then(m => m.CollectionsComponent)
  },
  {
    path: 'collection-detail/:id',
    loadComponent: () => import('./pages/collection-detail/collection-detail.component').then(m => m.CollectionDetailComponent)
  },
  {
    path: 'library',
    loadComponent: () => import('./pages/library/library.component').then(m => m.LibraryComponent)
  },
  {
    path: 'library-items',
    loadComponent: () => import('./pages/library-items/library-items.component').then(m => m.LibraryItemsComponent)
  },
  {
    path: 'books',
    loadComponent: () => import('./pages/books/books.component').then(m => m.BooksComponent)
  },
  {
    path: 'books/:id',
    loadComponent: () => import('./pages/book-detail/book-detail.component').then(m => m.BookDetailComponent)
  },
  {
    path: 'manga',
    loadComponent: () => import('./pages/manga/manga.component').then(m => m.MangaComponent)
  },
  {
    path: 'manga/series/:id',
    loadComponent: () => import('./pages/series-detail/series-detail.component').then(m => m.SeriesDetailComponent)
  },
  {
    path: 'want-to-read',
    loadComponent: () => import('./pages/want-to-read/want-to-read.component').then(m => m.WantToReadComponent)
  },
  {
    path: 'calendar',
    loadComponent: () => import('./pages/calendar/calendar.component').then(m => m.CalendarComponent)
  },
  {
    path: 'authors',
    loadComponent: () => import('./pages/authors/authors.component').then(m => m.AuthorsComponent)
  },
  {
    path: 'author-detail/:id',
    loadComponent: () => import('./pages/author-detail/author-detail.component').then(m => m.AuthorDetailComponent)
  },
  {
    path: 'series-detail/:id',
    loadComponent: () => import('./pages/series-detail/series-detail.component').then(m => m.SeriesDetailComponent)
  },
  {
    path: 'search',
    loadComponent: () => import('./pages/search/search.component').then(m => m.SearchComponent)
  },
  {
    path: 'notifications',
    loadComponent: () => import('./pages/notifications/notifications.component').then(m => m.NotificationsComponent)
  },
  {
    path: 'notification-demo',
    loadComponent: () => import('./components/notifications/notification-manager/notification-manager.component').then(m => m.NotificationManagerComponent)
  },
  {
    path: 'settings',
    loadComponent: () => import('./pages/settings/settings.component').then(m => m.SettingsComponent)
  },
  {
    path: 'about',
    loadComponent: () => import('./pages/about/about.component').then(m => m.AboutComponent)
  },
  {
    path: 'recently-read',
    loadComponent: () => import('./pages/library/library.component').then(m => m.LibraryComponent)
  },
  {
    path: 'favorites',
    loadComponent: () => import('./pages/library/library.component').then(m => m.LibraryComponent)
  },
  {
    path: '**',
    redirectTo: 'dashboard'
  }
];
