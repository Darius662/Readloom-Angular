import { Component, OnInit } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { ModalService } from '../../../services/modal.service';
import { ApiService } from '../../../services/api.service';
import { NotificationService } from '../../../services/notification.service';

@Component({
    selector: 'app-folder-browser',
    imports: [FormsModule],
    templateUrl: './folder-browser.component.html',
    styleUrls: ['./folder-browser.component.css']
})
export class FolderBrowserComponent implements OnInit {
  isVisible = false;
  currentPath: string = '';
  selectedPath: string = '';
  folders: any[] = [];
  drives: string[] = [];
  showDrives = false;
  isLoading = false;
  targetInputId: string | null = null;

  constructor(
    private modalService: ModalService,
    private api: ApiService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.modalService.registerModal('folderBrowserModal').subscribe((config) => {
      if (config) {
        this.isVisible = true;
        this.targetInputId = config.data?.targetInputId || null;
        const initialPath = config.data?.initialPath || null;
        this.loadPath(initialPath);
      } else {
        this.isVisible = false;
      }
    });
  }

  loadPath(path: string | null): void {
    this.isLoading = true;
    const payload = { path: path };

    this.api.post<any>('/folders/browse', payload).subscribe({
      next: (response: any) => {
        this.isLoading = false;
        if (response.success) {
          this.currentPath = response.current_path || '';
          this.selectedPath = this.currentPath;
          this.folders = response.folders || [];
          this.drives = response.drives || [];
          this.showDrives = this.drives.length > 0;
        }
      },
      error: (err: any) => {
        this.isLoading = false;
        console.error('Error browsing folders:', err);
        this.notificationService.error('Failed to browse folders');
      }
    });
  }

  onFolderClick(folderPath: string): void {
    this.loadPath(folderPath);
  }

  onDriveClick(drive: string): void {
    this.loadPath(drive);
  }

  onUpClick(): void {
    if (this.currentPath) {
      const lastBackslash = this.currentPath.lastIndexOf('\\');
      const lastForwardSlash = this.currentPath.lastIndexOf('/');
      const lastSeparator = Math.max(lastBackslash, lastForwardSlash);
      
      if (lastSeparator > 0) {
        const parentPath = this.currentPath.substring(0, lastSeparator);
        if (parentPath !== this.currentPath) {
          this.loadPath(parentPath);
        }
      }
    }
  }

  onHomeClick(): void {
    this.loadPath(null);
  }

  onSelectClick(): void {
    if (this.selectedPath && this.targetInputId) {
      this.modalService.setModalResult('folderBrowserModal', {
        action: 'select',
        data: { path: this.selectedPath, targetInputId: this.targetInputId }
      });
      this.closeModal();
    } else {
      this.notificationService.warning('Please select a folder');
    }
  }

  closeModal(): void {
    this.isVisible = false;
    this.modalService.closeModal('folderBrowserModal');
  }
}
