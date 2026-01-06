import { Component, OnInit, OnDestroy, ViewChild, HostListener } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MatSidenav, MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { HeaderComponent } from './components/header/header.component';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { NotificationComponent } from './components/notification/notification.component';
import { ToastNotificationComponent } from './components/notifications/toast-notification/toast-notification.component';
import { ThemeService } from './services/theme.service';

const MOBILE_BREAKPOINT = 768;

// Phase 1: Critical Modals
import { DeleteConfirmationComponent } from './components/modals/delete-confirmation/delete-confirmation.component';
import { BookDetailsComponent } from './components/modals/book-details/book-details.component';
import { MangaDetailsComponent } from './components/modals/manga-details/manga-details.component';
import { ImportSuccessComponent } from './components/modals/import-success/import-success.component';

// Phase 2: Root Folder Management
import { AddRootFolderComponent } from './components/modals/add-root-folder/add-root-folder.component';
import { EditRootFolderComponent } from './components/modals/edit-root-folder/edit-root-folder.component';
import { AddRootFolderCollectionComponent } from './components/modals/add-root-folder-collection/add-root-folder-collection.component';
import { FolderBrowserComponent } from './components/modals/folder-browser/folder-browser.component';

// Phase 3: Series Management
import { MoveSeriesComponent } from './components/modals/move-series/move-series.component';
import { VolumeFormComponent } from './components/modals/volume-form/volume-form.component';
import { ChapterFormComponent } from './components/modals/chapter-form/chapter-form.component';
import { EditSeriesComponent } from './components/modals/edit-series/edit-series.component';

// Phase 4: Setup and Advanced
import { SetupWizardComponent } from './components/modals/setup-wizard/setup-wizard.component';
import { LinkRootFolderComponent } from './components/modals/link-root-folder/link-root-folder.component';

@Component({
    selector: 'app-root',
    imports: [
        RouterOutlet,
        MatSidenavModule,
        MatToolbarModule,
        MatButtonModule,
        MatIconModule,
        HeaderComponent,
        SidebarComponent,
        NotificationComponent,
        ToastNotificationComponent,
        // Phase 1: Critical Modals
        DeleteConfirmationComponent,
        BookDetailsComponent,
        MangaDetailsComponent,
        ImportSuccessComponent,
        // Phase 2: Root Folder Management
        AddRootFolderComponent,
        EditRootFolderComponent,
        AddRootFolderCollectionComponent,
        FolderBrowserComponent,
        // Phase 3: Series Management
        MoveSeriesComponent,
        VolumeFormComponent,
        ChapterFormComponent,
        EditSeriesComponent,
        // Phase 4: Setup and Advanced
        SetupWizardComponent,
        LinkRootFolderComponent
    ],
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'Readloom';
  sidebarCollapsed = false;
  isMobile = false;
  @ViewChild('sidenav') sidenav!: MatSidenav;

  constructor(private themeService: ThemeService) {}

  ngOnInit(): void {
    this.themeService.getTheme().subscribe();
    this.checkScreenSize();
  }

  ngOnDestroy(): void {}

  @HostListener('window:resize')
  onResize(): void {
    this.checkScreenSize();
  }

  private checkScreenSize(): void {
    const wasMobile = this.isMobile;
    this.isMobile = window.innerWidth < MOBILE_BREAKPOINT;

    // Close sidebar when switching to mobile
    if (this.isMobile && !wasMobile && this.sidenav?.opened) {
      this.sidenav.close();
    }
    // Open sidebar when switching to desktop (if not manually collapsed)
    if (!this.isMobile && wasMobile && !this.sidebarCollapsed) {
      this.sidenav?.open();
    }
  }

  get sidenavMode(): 'over' | 'side' {
    return this.isMobile ? 'over' : 'side';
  }

  get sidenavOpened(): boolean {
    return this.isMobile ? false : !this.sidebarCollapsed;
  }

  onToggleSidebar(): void {
    if (this.sidenav) {
      this.sidenav.toggle();
    }
    if (!this.isMobile) {
      this.sidebarCollapsed = !this.sidebarCollapsed;
    }
  }
}
