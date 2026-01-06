import { Component, OnInit } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { ModalService } from '../../../services/modal.service';
import { ApiService } from '../../../services/api.service';
import { NotificationService } from '../../../services/notification.service';

@Component({
    selector: 'app-edit-root-folder',
    imports: [FormsModule],
    templateUrl: './edit-root-folder.component.html',
    styleUrls: ['./edit-root-folder.component.css']
})
export class EditRootFolderComponent implements OnInit {
  isVisible = false;
  folderId: number | null = null;
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
    this.modalService.registerModal('editRootFolderModal').subscribe((config) => {
      if (config) {
        this.isVisible = true;
        this.folderId = config.data?.folderId || null;
        this.name = config.data?.name || '';
        this.path = config.data?.path || '';
        this.contentType = config.data?.contentType || 'MANGA';
      } else {
        this.isVisible = false;
      }
    });
  }

  onBrowseFolder(): void {
    const fileInput = document.getElementById('edit-folder-picker') as HTMLInputElement;
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
        this.path = pathParts.slice(0, -1).join('/');
      }
    }
  }

  onUpdate(): void {
    if (!this.name.trim()) {
      this.notificationService.warning('Please enter a folder name');
      return;
    }

    if (!this.path.trim()) {
      this.notificationService.warning('Please enter or select a folder path');
      return;
    }

    if (!this.folderId) {
      this.notificationService.error('Folder ID is missing');
      return;
    }

    this.isLoading = true;
    const payload = {
      name: this.name,
      path: this.path,
      content_type: this.contentType
    };

    this.api.put<any>(`/root-folders/${this.folderId}`, payload).subscribe({
      next: (response: any) => {
        this.isLoading = false;
        if (response.success) {
          this.notificationService.success('Root folder updated successfully');
          this.modalService.setModalResult('editRootFolderModal', { action: 'update', data: response.data });
          this.closeModal();
        }
      },
      error: (err: any) => {
        this.isLoading = false;
        console.error('Error updating root folder:', err);
        this.notificationService.error('Failed to update root folder');
      }
    });
  }

  closeModal(): void {
    this.isVisible = false;
    this.modalService.closeModal('editRootFolderModal');
  }
}
