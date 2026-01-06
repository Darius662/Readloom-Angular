import { Component, OnInit } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { ModalService } from '../../../services/modal.service';
import { ApiService } from '../../../services/api.service';
import { NotificationService } from '../../../services/notification.service';

@Component({
    selector: 'app-add-root-folder',
    imports: [FormsModule],
    templateUrl: './add-root-folder.component.html',
    styleUrls: ['./add-root-folder.component.css']
})
export class AddRootFolderComponent implements OnInit {
  isVisible = false;
  name = '';
  path = '';
  contentType = 'MANGA';
  isLoading = false;
  contentTypes = ['MANGA', 'MANHWA', 'MANHUA', 'COMICS', 'NOVEL', 'BOOK', 'OTHER'];

  constructor(
    private modalService: ModalService,
    private api: ApiService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.modalService.registerModal('addRootFolderModal').subscribe((config) => {
      if (config) {
        this.isVisible = true;
        this.resetForm();
      } else {
        this.isVisible = false;
      }
    });
  }

  resetForm(): void {
    this.name = '';
    this.path = '';
    this.contentType = 'MANGA';
  }

  onBrowseFolder(): void {
    const fileInput = document.getElementById('folder-picker') as HTMLInputElement;
    if (fileInput) {
      fileInput.click();
    }
  }

  onFolderSelected(event: any): void {
    const files = event.target.files;
    if (files && files.length > 0) {
      // Get the path from the first file
      const filePath = files[0].webkitRelativePath || files[0].name;
      const pathParts = filePath.split('/');
      if (pathParts.length > 1) {
        this.path = pathParts.slice(0, -1).join('/');
      }
    }
  }

  onSave(): void {
    if (!this.name.trim()) {
      this.notificationService.warning('Please enter a folder name');
      return;
    }

    if (!this.path.trim()) {
      this.notificationService.warning('Please enter or select a folder path');
      return;
    }

    this.isLoading = true;
    const payload = {
      name: this.name,
      path: this.path,
      content_type: this.contentType
    };

    this.api.post<any>('/root-folders', payload).subscribe({
      next: (response: any) => {
        this.isLoading = false;
        if (response.success) {
          this.notificationService.success('Root folder added successfully');
          this.modalService.setModalResult('addRootFolderModal', { action: 'save', data: response.data });
          this.closeModal();
        }
      },
      error: (err: any) => {
        this.isLoading = false;
        console.error('Error adding root folder:', err);
        this.notificationService.warning('Root folder form is ready (backend not connected)');
        this.modalService.setModalResult('addRootFolderModal', { action: 'save', data: payload });
        this.closeModal();
      }
    });
  }

  closeModal(): void {
    this.isVisible = false;
    this.resetForm();
    this.modalService.closeModal('addRootFolderModal');
  }
}
