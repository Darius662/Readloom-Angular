import { Component, OnInit } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { ModalService } from '../../../services/modal.service';
import { ApiService } from '../../../services/api.service';
import { NotificationService } from '../../../services/notification.service';

@Component({
    selector: 'app-manga-details',
    imports: [FormsModule],
    templateUrl: './manga-details.component.html',
    styleUrls: ['./manga-details.component.css']
})
export class MangaDetailsComponent implements OnInit {
  isVisible = false;
  manga: any = {};
  collections: any[] = [];
  rootFolders: any[] = [];
  selectedContentType = 'MANGA';
  selectedCollection: number | null = null;
  selectedRootFolder: number | null = null;
  isLoading = false;
  showChapters = false;
  chapters: any[] = [];
  loadingChapters = false;

  constructor(
    private modalService: ModalService,
    private api: ApiService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.modalService.registerModal('mangaDetailsModal').subscribe((config) => {
      if (config) {
        this.isVisible = true;
        this.manga = config.data?.manga || {};
        this.selectedContentType = this.manga.content_type || 'MANGA';
        this.loadCollections();
      } else {
        this.isVisible = false;
        this.showChapters = false;
      }
    });
  }

  loadCollections(): void {
    this.api.get<any>('/collections').subscribe({
      next: (response: any) => {
        if (response.success && Array.isArray(response.collections)) {
          this.collections = response.collections.filter((c: any) => {
            const type = (c.type || '').toUpperCase();
            return type === 'MANGA' || type === 'MANHWA' || type === 'MANHUA' || type === 'COMICS';
          });
          if (this.collections.length > 0) {
            this.selectedCollection = this.collections[0].id;
            this.loadRootFolders();
          }
        }
      },
      error: (err: any) => {
        console.error('Error loading collections:', err);
        this.notificationService.error('Failed to load collections');
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
      title: this.manga.title,
      author: this.manga.author,
      cover_url: this.manga.cover_url,
      content_type: this.selectedContentType,
      collection_id: this.selectedCollection,
      root_folder_id: this.selectedRootFolder || null,
      provider: this.manga.provider
    };

    this.api.post<any>('/series', payload).subscribe({
      next: (response: any) => {
        this.isLoading = false;
        if (response.success) {
          this.notificationService.success('Manga added to collection');
          this.modalService.showImportSuccess('Manga has been added to your collection', '/library');
          this.closeModal();
        }
      },
      error: (err: any) => {
        this.isLoading = false;
        console.error('Error adding manga:', err);
        this.notificationService.error('Failed to add manga to collection');
      }
    });
  }

  onWantToRead(): void {
    this.notificationService.info('Added to Want to Read list');
  }

  onViewChapters(): void {
    this.showChapters = true;
    this.loadChapters();
  }

  loadChapters(): void {
    if (!this.manga.id) return;
    
    this.loadingChapters = true;
    this.api.get<any>(`/metadata/manga/${this.manga.id}/chapters`).subscribe({
      next: (response: any) => {
        this.loadingChapters = false;
        if (response.success && Array.isArray(response.chapters)) {
          this.chapters = response.chapters;
        }
      },
      error: (err: any) => {
        this.loadingChapters = false;
        console.error('Error loading chapters:', err);
        this.notificationService.error('Failed to load chapters');
      }
    });
  }

  closeModal(): void {
    this.isVisible = false;
    this.showChapters = false;
    this.modalService.closeModal('mangaDetailsModal');
  }
}
