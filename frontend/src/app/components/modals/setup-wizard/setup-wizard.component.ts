import { Component, OnInit } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { ModalService } from '../../../services/modal.service';
import { ApiService } from '../../../services/api.service';
import { NotificationService } from '../../../services/notification.service';

@Component({
    selector: 'app-setup-wizard',
    imports: [FormsModule],
    templateUrl: './setup-wizard.component.html',
    styleUrls: ['./setup-wizard.component.css']
})
export class SetupWizardComponent implements OnInit {
  isVisible = false;
  currentStep = 1;
  isLoading = false;

  // Step 1: Collection
  collectionName = 'My Collection';
  collectionDescription = 'My first collection';

  // Step 2: Root Folder
  rootFolderName = 'Manga Library';
  rootFolderPath = '';
  contentType = 'MANGA';
  contentTypes = ['MANGA', 'MANHWA', 'MANHUA', 'COMICS', 'NOVEL', 'BOOK', 'OTHER'];

  constructor(
    private modalService: ModalService,
    private api: ApiService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.modalService.registerModal('setupWizardModal').subscribe((config) => {
      if (config) {
        this.isVisible = true;
        this.currentStep = 1;
        this.resetForm();
      } else {
        this.isVisible = false;
      }
    });
  }

  resetForm(): void {
    this.collectionName = 'My Collection';
    this.collectionDescription = 'My first collection';
    this.rootFolderName = 'Manga Library';
    this.rootFolderPath = '';
    this.contentType = 'MANGA';
  }

  onNextStep1(): void {
    if (!this.collectionName.trim()) {
      this.notificationService.warning('Please enter a collection name');
      return;
    }
    this.currentStep = 2;
  }

  onPrevStep2(): void {
    this.currentStep = 1;
  }

  onNextStep2(): void {
    if (!this.rootFolderName.trim()) {
      this.notificationService.warning('Please enter a root folder name');
      return;
    }
    if (!this.rootFolderPath.trim()) {
      this.notificationService.warning('Please enter a root folder path');
      return;
    }
    this.currentStep = 3;
  }

  onPrevStep3(): void {
    this.currentStep = 2;
  }

  onBrowseFolder(): void {
    const fileInput = document.getElementById('setup-folder-picker') as HTMLInputElement;
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
        this.rootFolderPath = pathParts.slice(0, -1).join('/');
      }
    }
  }

  onFinishSetup(): void {
    this.isLoading = true;

    // Create collection first
    const collectionPayload = {
      name: this.collectionName,
      description: this.collectionDescription
    };

    this.api.post<any>('/collections', collectionPayload).subscribe({
      next: (collectionResponse: any) => {
        if (collectionResponse.success) {
          const collectionId = collectionResponse.data.id;

          // Then create root folder
          const rootFolderPayload = {
            name: this.rootFolderName,
            path: this.rootFolderPath,
            content_type: this.contentType
          };

          this.api.post<any>('/root-folders', rootFolderPayload).subscribe({
            next: (folderResponse: any) => {
              if (folderResponse.success) {
                const rootFolderId = folderResponse.data.id;

                // Finally, link root folder to collection
                const linkPayload = {
                  root_folder_id: rootFolderId
                };

                this.api.post<any>(`/collections/${collectionId}/root-folders`, linkPayload).subscribe({
                  next: (linkResponse: any) => {
                    this.isLoading = false;
                    if (linkResponse.success) {
                      this.notificationService.success('Setup completed successfully!');
                      this.modalService.setModalResult('setupWizardModal', {
                        action: 'finish',
                        data: {
                          collectionId,
                          rootFolderId
                        }
                      });
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
            },
            error: (err: any) => {
              this.isLoading = false;
              console.error('Error creating root folder:', err);
              this.notificationService.error('Failed to create root folder');
            }
          });
        }
      },
      error: (err: any) => {
        this.isLoading = false;
        console.error('Error creating collection:', err);
        this.notificationService.error('Failed to create collection');
      }
    });
  }

  closeModal(): void {
    this.isVisible = false;
    this.currentStep = 1;
    this.resetForm();
    this.modalService.closeModal('setupWizardModal');
  }
}
