import { Component, OnInit } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { ModalService } from '../../../services/modal.service';
import { ApiService } from '../../../services/api.service';
import { NotificationService } from '../../../services/notification.service';

@Component({
    selector: 'app-book-details',
    imports: [FormsModule],
    templateUrl: './book-details.component.html',
    styleUrls: ['./book-details.component.css']
})
export class BookDetailsComponent implements OnInit {
  isVisible = false;
  book: any = {};
  collections: any[] = [];
  rootFolders: any[] = [];
  selectedCollection: number | null = null;
  selectedRootFolder: number | null = null;
  isLoading = false;

  constructor(
    private modalService: ModalService,
    private api: ApiService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.modalService.registerModal('bookDetailsModal').subscribe((config) => {
      if (config) {
        this.isVisible = true;
        this.book = config.data?.book || {};
        this.loadCollections();
      } else {
        this.isVisible = false;
      }
    });
  }

  loadCollections(): void {
    this.api.get<any>('/collections').subscribe({
      next: (response: any) => {
        if (response.success && Array.isArray(response.collections)) {
          this.collections = response.collections.filter((c: any) =>
            (c.type || '').toUpperCase() === 'BOOK' || (c.type || '').toUpperCase() === 'NOVEL'
          );
          if (this.collections.length > 0) {
            this.selectedCollection = this.collections[0].id;
            this.loadRootFolders();
          }
        }
      },
      error: (err: any) => {
        console.error('Error loading collections:', err);
        this.collections = [];
        this.notificationService.info('Collections not available (backend not connected)');
      }
    });
  }

  loadRootFolders(): void {
    this.api.get<any>('/root-folders').subscribe({
      next: (response: any) => {
        if (response.success && Array.isArray(response.root_folders)) {
          this.rootFolders = response.root_folders;
        }
      },
      error: (err: any) => {
        console.error('Error loading root folders:', err);
      }
    });
  }

  onAddToCollection(): void {
    if (!this.selectedCollection) {
      this.notificationService.warning('Please select a collection');
      return;
    }

    this.isLoading = true;
    const payload = {
      title: this.book.title,
      author: this.book.author,
      cover_url: this.book.cover_url,
      collection_id: this.selectedCollection,
      root_folder_id: this.selectedRootFolder || null,
      provider: this.book.provider
    };

    this.api.post<any>('/series', payload).subscribe({
      next: (response: any) => {
        this.isLoading = false;
        if (response.success) {
          this.notificationService.success('Book added to collection');
          this.modalService.showImportSuccess('Book has been added to your collection', '/library');
          this.closeModal();
        }
      },
      error: (err: any) => {
        this.isLoading = false;
        console.error('Error adding book:', err);
        this.notificationService.error('Failed to add book to collection');
      }
    });
  }

  onWantToRead(): void {
    this.notificationService.info('Added to Want to Read list');
    this.closeModal();
  }

  closeModal(): void {
    this.isVisible = false;
    this.modalService.closeModal('bookDetailsModal');
  }
}
