import { Component, OnInit } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { ModalService } from '../../../services/modal.service';
import { ApiService } from '../../../services/api.service';
import { NotificationService } from '../../../services/notification.service';

@Component({
    selector: 'app-edit-series',
    imports: [FormsModule],
    templateUrl: './edit-series.component.html',
    styleUrls: ['./edit-series.component.css']
})
export class EditSeriesComponent implements OnInit {
  isVisible = false;
  seriesId: number | null = null;
  title = '';
  author = '';
  publisher = '';
  contentType = '';
  status = 'ONGOING';
  description = '';
  coverUrl = '';
  customPath = '';
  importFromCustomPath = false;
  contentTypes: string[] = [];
  statusOptions = ['ONGOING', 'COMPLETED', 'HIATUS', 'CANCELLED', 'UNKNOWN'];
  isLoading = false;

  constructor(
    private modalService: ModalService,
    private api: ApiService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.modalService.registerModal('seriesModal').subscribe((config) => {
      if (config) {
        this.isVisible = true;
        this.seriesId = config.data?.seriesId || null;
        this.title = config.data?.title || '';
        this.author = config.data?.author || '';
        this.publisher = config.data?.publisher || '';
        this.contentType = config.data?.contentType || '';
        this.status = config.data?.status || 'ONGOING';
        this.description = config.data?.description || '';
        this.coverUrl = config.data?.coverUrl || '';
        this.customPath = config.data?.customPath || '';
        this.importFromCustomPath = config.data?.importFromCustomPath || false;
        this.contentTypes = config.data?.contentTypes || ['MANGA', 'MANHWA', 'MANHUA', 'COMICS', 'NOVEL', 'BOOK'];
      } else {
        this.isVisible = false;
      }
    });
  }

  onBrowseCustomPath(): void {
    const fileInput = document.getElementById('series-custom-path-picker') as HTMLInputElement;
    if (fileInput) {
      fileInput.click();
    }
  }

  onFolderSelected(event: any): void {
    const files = event.target.files;
    if (files && files.length > 0) {
      const filePath = files[0].webkitRelativePath || files[0].name;
      const pathParts = filePath.split('/');
      if (pathParts.length > 1) {
        this.customPath = pathParts.slice(0, -1).join('/');
      }
    }
  }

  onValidatePath(): void {
    if (!this.customPath.trim()) {
      this.notificationService.warning('Please enter a path');
      return;
    }

    this.isLoading = true;
    this.api.post<any>('/series/validate-path', { path: this.customPath }).subscribe({
      next: (response: any) => {
        this.isLoading = false;
        if (response.success) {
          this.notificationService.success('Path is valid');
        } else {
          this.notificationService.warning('Path validation failed: ' + (response.message || 'Unknown error'));
        }
      },
      error: (err: any) => {
        this.isLoading = false;
        console.error('Error validating path:', err);
        this.notificationService.error('Failed to validate path');
      }
    });
  }

  onSave(): void {
    if (!this.title.trim()) {
      this.notificationService.warning('Please enter a series title');
      return;
    }

    if (!this.seriesId) {
      this.notificationService.error('Series ID is missing');
      return;
    }

    this.isLoading = true;
    const payload = {
      title: this.title,
      author: this.author || null,
      publisher: this.publisher || null,
      content_type: this.contentType || null,
      status: this.status,
      description: this.description || null,
      cover_url: this.coverUrl || null,
      custom_path: this.customPath || null,
      import_from_custom_path: this.importFromCustomPath
    };

    this.api.put<any>(`/series/${this.seriesId}`, payload).subscribe({
      next: (response: any) => {
        this.isLoading = false;
        if (response.success) {
          this.notificationService.success('Series updated successfully');
          this.modalService.setModalResult('seriesModal', { action: 'save', data: response.data });
          this.closeModal();
        }
      },
      error: (err: any) => {
        this.isLoading = false;
        console.error('Error saving series:', err);
        this.notificationService.error('Failed to save series');
      }
    });
  }

  closeModal(): void {
    this.isVisible = false;
    this.modalService.closeModal('seriesModal');
  }
}
