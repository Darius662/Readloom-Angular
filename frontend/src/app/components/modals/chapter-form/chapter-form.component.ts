import { Component, OnInit } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { ModalService } from '../../../services/modal.service';
import { ApiService } from '../../../services/api.service';
import { NotificationService } from '../../../services/notification.service';

@Component({
    selector: 'app-chapter-form',
    imports: [FormsModule],
    templateUrl: './chapter-form.component.html',
    styleUrls: ['./chapter-form.component.css']
})
export class ChapterFormComponent implements OnInit {
  isVisible = false;
  seriesId: number | null = null;
  chapterId: number | null = null;
  isEditMode = false;
  number = '';
  title = '';
  volumeId: number | null = null;
  description = '';
  releaseDate = '';
  status = 'RELEASED';
  readStatus = 'UNREAD';
  volumes: any[] = [];
  isLoading = false;

  statusOptions = ['ANNOUNCED', 'RELEASED', 'DELAYED', 'CANCELLED'];
  readStatusOptions = ['UNREAD', 'READING', 'READ'];

  constructor(
    private modalService: ModalService,
    private api: ApiService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.modalService.registerModal('chapterModal').subscribe((config) => {
      if (config) {
        this.isVisible = true;
        this.seriesId = config.data?.seriesId || null;
        this.chapterId = config.data?.chapterId || null;
        this.isEditMode = !!this.chapterId;
        this.volumes = config.data?.volumes || [];
        
        if (this.isEditMode) {
          this.number = config.data?.number || '';
          this.title = config.data?.title || '';
          this.volumeId = config.data?.volumeId || null;
          this.description = config.data?.description || '';
          this.releaseDate = config.data?.releaseDate || '';
          this.status = config.data?.status || 'RELEASED';
          this.readStatus = config.data?.readStatus || 'UNREAD';
        } else {
          this.resetForm();
        }
      } else {
        this.isVisible = false;
      }
    });
  }

  resetForm(): void {
    this.number = '';
    this.title = '';
    this.volumeId = null;
    this.description = '';
    this.releaseDate = '';
    this.status = 'RELEASED';
    this.readStatus = 'UNREAD';
  }

  onSave(): void {
    if (!this.number.trim()) {
      this.notificationService.warning('Please enter a chapter number');
      return;
    }

    if (!this.seriesId) {
      this.notificationService.error('Series ID is missing');
      return;
    }

    this.isLoading = true;
    const payload = {
      number: this.number,
      title: this.title || null,
      volume_id: this.volumeId || null,
      description: this.description || null,
      release_date: this.releaseDate || null,
      status: this.status,
      read_status: this.readStatus
    };

    const endpoint = this.isEditMode
      ? `/series/${this.seriesId}/chapters/${this.chapterId}`
      : `/series/${this.seriesId}/chapters`;
    
    const request = this.isEditMode
      ? this.api.put<any>(endpoint, payload)
      : this.api.post<any>(endpoint, payload);

    request.subscribe({
      next: (response: any) => {
        this.isLoading = false;
        if (response.success) {
          const message = this.isEditMode ? 'Chapter updated successfully' : 'Chapter added successfully';
          this.notificationService.success(message);
          this.modalService.setModalResult('chapterModal', { action: 'save', data: response.data });
          this.closeModal();
        }
      },
      error: (err: any) => {
        this.isLoading = false;
        console.error('Error saving chapter:', err);
        this.notificationService.error('Failed to save chapter');
      }
    });
  }

  closeModal(): void {
    this.isVisible = false;
    this.resetForm();
    this.modalService.closeModal('chapterModal');
  }
}
