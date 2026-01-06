import { Component, OnInit } from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { LoadingSpinnerComponent } from '../../components/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../components/error-message/error-message.component';
import { CollectionService } from '../../services/collection.service';
import { RootFolderService, RootFolder } from '../../services/root-folder.service';
import { NotificationService } from '../../services/notification.service';
import { ModalService } from '../../services/modal.service';
import { Collection } from '../../models/collection.model';

@Component({
    selector: 'app-collections',
    imports: [MatCardModule, MatButtonModule, MatIconModule, LoadingSpinnerComponent, ErrorMessageComponent],
    templateUrl: './collections.component.html',
    styleUrls: ['./collections.component.css']
})
export class CollectionsComponent implements OnInit {
  title = 'Collections';
  isLoading = true;
  error: string | null = null;
  collections: Collection[] = [];
  rootFolders: RootFolder[] = [];

  constructor(
    private collectionService: CollectionService,
    private rootFolderService: RootFolderService,
    private notificationService: NotificationService,
    private modalService: ModalService
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  private loadData(): void {
    this.isLoading = true;
    this.error = null;

    this.collectionService.getCollections().subscribe({
      next: (collections) => {
        this.collections = collections;
        this.loadRootFolders();
      },
      error: (err) => {
        this.error = 'Failed to load collections';
        this.notificationService.error('Failed to load collections');
        this.isLoading = false;
      }
    });
  }

  private loadRootFolders(): void {
    this.rootFolderService.getRootFolders().subscribe({
      next: (rootFolders) => {
        this.rootFolders = rootFolders;
        this.isLoading = false;
      },
      error: (err) => {
        this.notificationService.error('Failed to load root folders');
        this.isLoading = false;
      }
    });
  }

  onAddCollection(): void {
    this.notificationService.info('Add collection feature coming soon');
  }

  onAddRootFolder(): void {
    this.modalService.openModal({
      id: 'addRootFolderModal',
      title: 'Add Root Folder'
    });

    this.modalService.getModalResult('addRootFolderModal').subscribe((result) => {
      if (result?.action === 'save') {
        this.loadData();
      }
    });
  }

  onEditCollection(collection: Collection): void {
    this.notificationService.info('Edit collection feature coming soon');
  }

  onDeleteCollection(collection: Collection): void {
    this.modalService.confirmDelete(`Are you sure you want to delete the collection "${collection.name}"?`).then((confirmed) => {
      if (confirmed) {
        this.collectionService.deleteCollection(collection.id).subscribe({
          next: () => {
            this.notificationService.success('Collection deleted successfully');
            this.loadData();
          },
          error: (err) => {
            this.notificationService.error('Failed to delete collection');
          }
        });
      }
    });
  }

  onEditRootFolder(folder: RootFolder): void {
    this.modalService.openModal({
      id: 'editRootFolderModal',
      title: 'Edit Root Folder',
      data: {
        folderId: folder.id,
        name: folder.name,
        path: folder.path,
        content_type: folder.content_type
      }
    });

    this.modalService.getModalResult('editRootFolderModal').subscribe((result) => {
      if (result?.action === 'update') {
        this.loadData();
      }
    });
  }

  onDeleteRootFolder(folder: RootFolder): void {
    this.modalService.confirmDelete(`Are you sure you want to delete the root folder "${folder.name}"?`).then((confirmed) => {
      if (confirmed) {
        this.rootFolderService.deleteRootFolder(folder.id).subscribe({
          next: () => {
            this.notificationService.success('Root folder deleted successfully');
            this.loadData();
          },
          error: (err) => {
            this.notificationService.error('Failed to delete root folder');
          }
        });
      }
    });
  }

  onLinkRootFolder(collection: Collection): void {
    this.modalService.openModal({
      id: 'linkRootFolderModal',
      title: 'Link Root Folder to Collection',
      data: { collectionId: collection.id }
    });

    this.modalService.getModalResult('linkRootFolderModal').subscribe((result) => {
      if (result?.action === 'link') {
        this.loadData();
      }
    });
  }
}
