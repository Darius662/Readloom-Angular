import { Component, OnInit } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatChipsModule } from '@angular/material/chips';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { ModalService } from '../../services/modal.service';
import { CollectionService } from '../../services/collection.service';
import { RootFolderService } from '../../services/root-folder.service';
import { NotificationService } from '../../services/notification.service';
import { MaterialNotificationService } from '../../services/material-notification.service';
import { ToastNotificationService } from '../../services/toast-notification.service';
import { ConfirmationService } from '../../services/confirmation.service';
import { AddCollectionModalComponent } from '../../components/modals/add-collection-modal/add-collection-modal.component';
import { EditCollectionModalComponent } from '../../components/modals/edit-collection-modal/edit-collection-modal.component';
import { AddRootFolderModalComponent } from '../../components/modals/add-root-folder-modal/add-root-folder-modal.component';
import { EditRootFolderModalComponent } from '../../components/modals/edit-root-folder-modal/edit-root-folder-modal.component';
import { LinkRootFolderModalComponent } from '../../components/modals/link-root-folder-modal/link-root-folder-modal.component';
import { MetadataProvidersConfigComponent } from '../../components/modals/metadata-providers-config/metadata-providers-config.component';
import { AIProvidersConfigComponent } from '../../components/modals/ai-providers-config/ai-providers-config.component';

interface GeneralSettings {
  host: string;
  port: number;
  urlBase: string;
  taskInterval: number;
  metadataCache: number;
}

interface CollectionUI {
  id: number;
  name: string;
  description?: string;
  type?: string;
  content_type?: string;
  is_default?: boolean;
  itemsCount?: number;
  created_at?: string;
  updated_at?: string;
}

interface RootFolderUI {
  id: number;
  name: string;
  path: string;
  content_type: string;
  created_at?: string;
  updated_at?: string;
}

interface SeriesUI {
  id: number;
  title: string;
  content_type: string;
}

interface CalendarSettings {
  defaultView: string;
  firstDayOfWeek: string;
  calendarRange: number;
  calendarRefresh: number;
  highlightOwned: boolean;
}

interface LoggingSettings {
  level: string;
  maxFileSize: number;
  backupCount: number;
}

interface NotificationSettings {
  notifyNewVolumes: boolean;
  notifyNewChapters: boolean;
  notifyDaysBefore: string;
  browserEnabled: boolean;
  emailEnabled: boolean;
  emailAddress?: string;
  discordEnabled: boolean;
  discordWebhook?: string;
  telegramEnabled: boolean;
  telegramBotToken?: string;
  telegramChatId?: string;
}

interface Integrations {
  homeAssistantUrl?: string;
  homeAssistantToken?: string;
  homarrUrl?: string;
  metadataProviders?: string[];
  aiProvider?: string;
}

interface DataSyncSettings {
  enableAutoSync: boolean;
  syncOnStartup: boolean;
  autoSyncInterval: string;
  authorMergeMode: boolean;
  bookMergeMode: boolean;
  mangaMergeMode: boolean;
}

@Component({
    selector: 'app-settings',
    imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatSlideToggleModule,
    MatSelectModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatTabsModule,
    MatTableModule,
    MatTooltipModule,
    MatChipsModule,
    MatGridListModule,
    MatDialogModule
  ],
    templateUrl: './settings.component.html',
    styleUrls: ['./settings.component.css']
})
export class SettingsComponent implements OnInit {
  title = 'Settings';
  error: string | null = null;
  activeTab = 'general';
  isLoading = false;

  // Tab index mapping for Angular Material tabs
  private tabMap = {
    'general': 0,
    'collections': 1,
    'calendar': 2,
    'logging': 3,
    'integrations': 4,
    'data-sync': 5,
    'notifications': 6
  };

  getTabIndex(): number {
    return this.tabMap[this.activeTab as keyof typeof this.tabMap] || 0;
  }

  setActiveTab(index: number): void {
    const tabKeys = Object.keys(this.tabMap);
    if (index >= 0 && index < tabKeys.length) {
      this.activeTab = tabKeys[index];
    }
  }

  generalSettings: GeneralSettings = {
    host: '0.0.0.0',
    port: 7227,
    urlBase: '',
    taskInterval: 60,
    metadataCache: 7
  };

  calendarSettings: CalendarSettings = {
    defaultView: 'month',
    firstDayOfWeek: '1',
    calendarRange: 14,
    calendarRefresh: 12,
    highlightOwned: true
  };

  loggingSettings: LoggingSettings = {
    level: 'INFO',
    maxFileSize: 10,
    backupCount: 5
  };

  notificationSettings: NotificationSettings = {
    notifyNewVolumes: true,
    notifyNewChapters: true,
    notifyDaysBefore: '1',
    browserEnabled: true,
    emailEnabled: false,
    emailAddress: '',
    discordEnabled: false,
    discordWebhook: '',
    telegramEnabled: false,
    telegramBotToken: '',
    telegramChatId: ''
  };

  integrations: Integrations = {
    homeAssistantUrl: '',
    homeAssistantToken: '',
    homarrUrl: '',
    metadataProviders: [],
    aiProvider: ''
  };

  dataSyncSettings: DataSyncSettings = {
    autoSyncInterval: '60',
    enableAutoSync: true,
    syncOnStartup: true,
    authorMergeMode: false,
    bookMergeMode: false,
    mangaMergeMode: false
  };

  collections: CollectionUI[] = [];
  rootFolders: RootFolderUI[] = [];
  
  selectedCollection: CollectionUI | null = null;
  selectedCollectionRootFolders: RootFolderUI[] = [];
  selectedCollectionSeries: SeriesUI[] = [];

  displayedCollectionsColumns: string[] = ['name', 'description', 'type', 'is_default', 'actions'];
  displayedRootFoldersColumns: string[] = ['name', 'path', 'content_type', 'actions'];

  constructor(
    private modalService: ModalService,
    private collectionService: CollectionService,
    private rootFolderService: RootFolderService,
    private notificationService: NotificationService,
    private materialNotificationService: MaterialNotificationService,
    private toastNotificationService: ToastNotificationService,
    private confirmationService: ConfirmationService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.loadSettings();
  }

  private loadSettings(): void {
    this.loadCollections();
    this.loadRootFolders();
  }

  private loadCollections(): void {
    this.collectionService.getCollections().subscribe({
      next: (collections) => {
        this.collections = collections;
      },
      error: (err) => {
        this.notificationService.error('Failed to load collections');
        console.error('Error loading collections:', err);
      }
    });
  }

  private loadRootFolders(): void {
    this.rootFolderService.getRootFolders().subscribe({
      next: (rootFolders) => {
        this.rootFolders = rootFolders;
      },
      error: (err) => {
        this.notificationService.error('Failed to load root folders');
        console.error('Error loading root folders:', err);
      }
    });
  }

  onSaveSettings(): void {
    // Save general settings to backend
    console.log('Saving general settings:', this.generalSettings);
  }

  onAddCollection(): void {
    const dialogRef = this.dialog.open(AddCollectionModalComponent, {
      width: '450px',
      disableClose: false
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result?.action === 'save') {
        this.collectionService.createCollection(result.data).subscribe({
          next: () => {
            this.notificationService.success('Collection added successfully');
            this.loadCollections();
          },
          error: (err) => {
            this.notificationService.error('Failed to add collection');
            console.error('Error adding collection:', err);
          }
        });
      }
    });
  }

  onEditCollection(collection: CollectionUI): void {
    const dialogRef = this.dialog.open(EditCollectionModalComponent, {
      width: '450px',
      panelClass: 'edit-collection-dialog',
      disableClose: false,
      data: {
        collection: collection
      }
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.notificationService.success('Collection updated successfully');
        this.loadCollections();
      }
    });
  }

  onDeleteCollection(collection: CollectionUI): void {
    this.confirmationService.confirmDelete(collection.name).subscribe(confirmed => {
      if (confirmed) {
        this.collectionService.deleteCollection(collection.id).subscribe({
          next: () => {
            this.notificationService.success('Collection deleted successfully');
            this.loadCollections();
          },
          error: (err) => {
            this.notificationService.error('Failed to delete collection');
            console.error('Error deleting collection:', err);
          }
        });
      }
    });
  }

  onAddRootFolder(): void {
    const dialogRef = this.dialog.open(AddRootFolderModalComponent, {
      width: '450px',
      disableClose: false
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result?.action === 'save') {
        this.rootFolderService.createRootFolder(result.data).subscribe({
          next: () => {
            this.notificationService.success('Root folder added successfully');
            this.loadRootFolders();
          },
          error: (err) => {
            this.notificationService.error('Failed to add root folder');
            console.error('Error adding root folder:', err);
          }
        });
      }
    });
  }

  onEditRootFolder(folder: RootFolderUI): void {
    const dialogRef = this.dialog.open(EditRootFolderModalComponent, {
      width: '450px',
      panelClass: 'edit-root-folder-dialog',
      disableClose: false,
      data: folder
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result?.action === 'update') {
        this.rootFolderService.updateRootFolder(result.data.id, result.data).subscribe({
          next: () => {
            this.notificationService.success('Root folder updated successfully');
            this.loadRootFolders();
          },
          error: (err) => {
            this.notificationService.error('Failed to update root folder');
            console.error('Error updating root folder:', err);
          }
        });
      }
    });
  }

  onDeleteRootFolder(folder: RootFolderUI): void {
    this.confirmationService.confirmDelete(folder.name).subscribe(confirmed => {
      if (confirmed) {
        this.rootFolderService.deleteRootFolder(folder.id).subscribe({
          next: () => {
            this.notificationService.success('Root folder deleted successfully');
            this.loadRootFolders();
          },
          error: (err) => {
            this.notificationService.error('Failed to delete root folder');
            console.error('Error deleting root folder:', err);
          }
        });
      }
    });
  }

  onViewCollection(collection: CollectionUI): void {
    this.selectedCollection = collection;
    this.loadCollectionDetails(collection.id);
  }

  onCloseCollectionDetails(): void {
    this.selectedCollection = null;
    this.selectedCollectionRootFolders = [];
    this.selectedCollectionSeries = [];
  }

  private loadCollectionDetails(collectionId: number): void {
    // Load root folders assigned to this collection
    this.collectionService.getCollectionRootFolders(collectionId).subscribe({
      next: (folders) => {
        this.selectedCollectionRootFolders = folders;
      },
      error: (err) => {
        this.notificationService.error('Failed to load collection root folders');
        console.error('Error loading collection root folders:', err);
      }
    });

    // Load series in this collection
    this.collectionService.getCollectionSeries(collectionId).subscribe({
      next: (series) => {
        this.selectedCollectionSeries = series;
      },
      error: (err) => {
        this.notificationService.error('Failed to load collection series');
        console.error('Error loading collection series:', err);
      }
    });
  }

  onLinkRootFolder(): void {
    if (!this.selectedCollection) return;

    // Get available root folders (not already linked)
    const linkedFolderIds = this.selectedCollectionRootFolders.map(f => f.id);
    const availableFolders = this.rootFolders.filter(f => !linkedFolderIds.includes(f.id));

    if (availableFolders.length === 0) {
      this.notificationService.warning('All root folders are already linked to this collection');
      return;
    }

    // Open dialog to select root folder
    const dialogRef = this.dialog.open(LinkRootFolderModalComponent, {
      width: '450px',
      disableClose: false,
      data: { availableFolders }
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result?.action === 'link' && this.selectedCollection) {
        this.collectionService.linkRootFolder(this.selectedCollection.id, result.rootFolderId).subscribe({
          next: () => {
            this.notificationService.success('Root folder linked successfully');
            this.loadCollectionDetails(this.selectedCollection!.id);
          },
          error: (err) => {
            this.notificationService.error('Failed to link root folder');
            console.error('Error linking root folder:', err);
          }
        });
      }
    });
  }

  onUnlinkRootFolder(folder: RootFolderUI): void {
    if (!this.selectedCollection) return;

    this.collectionService.unlinkRootFolder(this.selectedCollection.id, folder.id).subscribe({
      next: () => {
        this.notificationService.success('Root folder unlinked successfully');
        this.loadCollectionDetails(this.selectedCollection!.id);
      },
      error: (err) => {
        this.notificationService.error('Failed to unlink root folder');
        console.error('Error unlinking root folder:', err);
      }
    });
  }

  // Settings Save/Load Methods
  saveGeneralSettings(): void {
    this.notificationService.success('General settings saved successfully');
    // TODO: Implement actual API call
  }

  resetGeneralSettings(): void {
    this.generalSettings = {
      host: '0.0.0.0',
      port: 7227,
      urlBase: '',
      taskInterval: 60,
      metadataCache: 7
    };
    this.notificationService.info('General settings reset to defaults');
  }

  saveCalendarSettings(): void {
    this.notificationService.success('Calendar settings saved successfully');
    // TODO: Implement actual API call
  }

  saveLoggingSettings(): void {
    this.notificationService.success('Logging settings saved successfully');
    // TODO: Implement actual API call
  }

  saveDataSyncSettings(): void {
    this.notificationService.success('Data sync settings saved successfully');
    // TODO: Implement actual API call
  }

  triggerSyncNow(): void {
    this.notificationService.info('Data sync triggered');
    // TODO: Implement actual sync
  }

  syncAuthorReadme(): void {
    this.notificationService.info('Author README sync triggered');
    // TODO: Implement actual Author README sync
  }

  syncBookReadme(): void {
    this.notificationService.info('Book README sync triggered');
    // TODO: Implement actual Book README sync
  }

  syncMangaReadme(): void {
    this.notificationService.info('Manga README sync triggered');
    // TODO: Implement actual Manga README sync
  }

  configureIntegration(type: string): void {
    if (type === 'metadataProviders') {
      this.openMetadataProvidersConfig();
    } else if (type === 'aiProviders') {
      this.openAIProvidersConfig();
    } else {
      this.notificationService.warning(`Unknown integration type: ${type}`);
    }
  }

  testIntegration(type: string): void {
    this.notificationService.info(`Testing ${type} integration...`);
    // TODO: Implement integration testing
  }

  saveNotificationSettings(): void {
    this.notificationService.success('Notification settings saved successfully');
    // TODO: Implement actual API call
  }

  // Material NotificationManager Methods
  showMaterialSuccess(): void {
    this.materialNotificationService.success('[Material] Operation completed successfully!');
  }

  showMaterialError(): void {
    this.materialNotificationService.error('[Material] An error occurred. Please try again.');
  }

  showMaterialWarning(): void {
    this.materialNotificationService.warning('[Material] This action cannot be undone.');
  }

  showMaterialInfo(): void {
    this.materialNotificationService.info('[Material] Here is some helpful information.');
  }

  showMaterialConfirm(): void {
    // TODO: Implement confirmation dialog with proper service
    this.materialNotificationService.info('[Material] Confirm dialog feature coming soon');
  }

  clearMaterialNotifications(): void {
    this.materialNotificationService.clearAll();
  }

  showMaterialMultiple(): void {
    this.materialNotificationService.success('[Material] First notification - Success!');
    setTimeout(() => {
      this.materialNotificationService.warning('[Material] Second notification - Warning!');
    }, 500);
    setTimeout(() => {
      this.materialNotificationService.info('[Material] Third notification - Info');
    }, 1000);
  }

  showMaterialLong(): void {
    const longMessage = '[Material] This is a longer notification message to test how the Material notification system handles text wrapping and layout with more content. It should display nicely without breaking the layout.';
    this.materialNotificationService.info(longMessage);
  }

  // Toast Notification Methods
  showToastSuccess(): void {
    this.toastNotificationService.success('[Toast] Operation completed successfully!');
  }

  showToastError(): void {
    this.toastNotificationService.error('[Toast] An error occurred. Please try again.');
  }

  showToastWarning(): void {
    this.toastNotificationService.warning('[Toast] This action cannot be undone.');
  }

  showToastInfo(): void {
    this.toastNotificationService.info('[Toast] Here is some helpful information.');
  }

  showToastConfirm(): void {
    // TODO: Implement confirmation dialog with proper service
    this.toastNotificationService.info('[Toast] Confirm dialog feature coming soon');
  }

  clearToastNotifications(): void {
    this.toastNotificationService.clearAll();
  }

  showToastMultiple(): void {
    this.toastNotificationService.success('[Toast] First notification - Success!');
    setTimeout(() => {
      this.toastNotificationService.warning('[Toast] Second notification - Warning!');
    }, 500);
    setTimeout(() => {
      this.toastNotificationService.info('[Toast] Third notification - Info');
    }, 1000);
  }

  showToastLong(): void {
    const longMessage = '[Toast] This is a longer notification message to test how the Toast notification system handles text wrapping and layout with more content. It should display nicely without breaking the layout.';
    this.toastNotificationService.info(longMessage);
  }

  showMultipleNotifications(): void {
    this.notificationService.success('First notification - Success!');
    setTimeout(() => {
      this.notificationService.warning('Second notification - Warning!');
    }, 500);
    setTimeout(() => {
      this.notificationService.info('Third notification - Info');
    }, 1000);
  }

  showLongMessageNotification(): void {
    const longMessage = 'This is a longer notification message to test how the notification system handles text wrapping and layout with more content. It should display nicely without breaking the layout.';
    this.notificationService.info(longMessage);
  }

  saveIntegrationsSettings(): void {
    this.notificationService.success('Integration settings saved successfully');
    // TODO: Implement actual API call
  }

  // Integration Methods
  openMetadataProvidersConfig(): void {
    const dialogRef = this.dialog.open(MetadataProvidersConfigComponent, {
      width: '600px',
      disableClose: false
    });
  }

  openAIProvidersConfig(): void {
    const dialogRef = this.dialog.open(AIProvidersConfigComponent, {
      width: '600px',
      disableClose: false
    });
  }
}
