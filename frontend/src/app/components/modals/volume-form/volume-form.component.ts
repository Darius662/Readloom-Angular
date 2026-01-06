import { Component, OnInit } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { ModalService } from '../../../services/modal.service';
import { ApiService } from '../../../services/api.service';
import { NotificationService } from '../../../services/notification.service';

@Component({
    selector: 'app-volume-form',
    imports: [FormsModule],
    templateUrl: './volume-form.component.html',
    styleUrls: ['./volume-form.component.css']
})
export class VolumeFormComponent implements OnInit {
  isVisible = false;
  seriesId: number | null = null;
  volumeId: number | null = null;
  isEditMode = false;
  number = '';
  title = '';
  description = '';
  releaseDate = '';
  coverUrl = '';
  isLoading = false;

  constructor(
    private modalService: ModalService,
    private api: ApiService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.modalService.registerModal('volumeModal').subscribe((config) => {
      if (config) {
        this.isVisible = true;
        this.seriesId = config.data?.seriesId || null;
        this.volumeId = config.data?.volumeId || null;
        this.isEditMode = !!this.volumeId;
        
        if (this.isEditMode) {
          this.number = config.data?.number || '';
          this.title = config.data?.title || '';
          this.description = config.data?.description || '';
          this.releaseDate = config.data?.releaseDate || '';
          this.coverUrl = config.data?.coverUrl || '';
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
    this.description = '';
    this.releaseDate = '';
    this.coverUrl = '';
  }

  onSave(): void {
    if (!this.number.trim()) {
      this.notificationService.warning('Please enter a volume number');
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
      description: this.description || null,
      release_date: this.releaseDate || null,
      cover_url: this.coverUrl || null
    };

    const endpoint = this.isEditMode
      ? `/series/${this.seriesId}/volumes/${this.volumeId}`
      : `/series/${this.seriesId}/volumes`;
    
    const request = this.isEditMode
      ? this.api.put<any>(endpoint, payload)
      : this.api.post<any>(endpoint, payload);

    request.subscribe({
      next: (response: any) => {
        this.isLoading = false;
        if (response.success) {
          const message = this.isEditMode ? 'Volume updated successfully' : 'Volume added successfully';
          this.notificationService.success(message);
          this.modalService.setModalResult('volumeModal', { action: 'save', data: response.data });
          this.closeModal();
        }
      },
      error: (err: any) => {
        this.isLoading = false;
        console.error('Error saving volume:', err);
        this.notificationService.error('Failed to save volume');
      }
    });
  }

  closeModal(): void {
    this.isVisible = false;
    this.resetForm();
    this.modalService.closeModal('volumeModal');
  }
}
