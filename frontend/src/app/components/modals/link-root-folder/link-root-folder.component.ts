import { Component, OnInit } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { ModalService } from '../../../services/modal.service';
import { ApiService } from '../../../services/api.service';
import { NotificationService } from '../../../services/notification.service';

@Component({
    selector: 'app-link-root-folder',
    imports: [FormsModule],
    templateUrl: './link-root-folder.component.html',
    styleUrls: ['./link-root-folder.component.css']
})
export class LinkRootFolderComponent implements OnInit {
  isVisible = false;
  collectionId: number | null = null;
  selectedRootFolder: number | null = null;
  rootFolders: any[] = [];
  isLoading = false;

  constructor(
    private modalService: ModalService,
    private api: ApiService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.modalService.registerModal('linkRootFolderModal').subscribe((config) => {
      if (config) {
        this.isVisible = true;
        this.collectionId = config.data?.collectionId || null;
        this.selectedRootFolder = null;
        this.loadRootFolders();
      } else {
        this.isVisible = false;
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
        this.notificationService.error('Failed to load root folders');
      }
    });
  }

  onLink(): void {
    if (!this.selectedRootFolder) {
      this.notificationService.warning('Please select a root folder');
      return;
    }

    if (!this.collectionId) {
      this.notificationService.error('Collection ID is missing');
      return;
    }

    this.isLoading = true;
    const payload = {
      root_folder_id: this.selectedRootFolder
    };

    this.api.post<any>(`/collections/${this.collectionId}/root-folders`, payload).subscribe({
      next: (response: any) => {
        this.isLoading = false;
        if (response.success) {
          this.notificationService.success('Root folder linked to collection');
          this.modalService.setModalResult('linkRootFolderModal', { action: 'link', data: response.data });
          this.closeModal();
        }
      },
      error: (err: any) => {
        this.isLoading = false;
        console.error('Error linking root folder:', err);
        this.notificationService.error('Failed to link root folder to collection');
      }
    });
  }

  closeModal(): void {
    this.isVisible = false;
    this.selectedRootFolder = null;
    this.modalService.closeModal('linkRootFolderModal');
  }
}
