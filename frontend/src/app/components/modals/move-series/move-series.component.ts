import { Component, OnInit } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { ModalService } from '../../../services/modal.service';
import { ApiService } from '../../../services/api.service';
import { NotificationService } from '../../../services/notification.service';

@Component({
    selector: 'app-move-series',
    imports: [FormsModule],
    templateUrl: './move-series.component.html',
    styleUrls: ['./move-series.component.css']
})
export class MoveSeriesComponent implements OnInit {
  isVisible = false;
  seriesId: number | null = null;
  seriesTitle = '';
  collections: any[] = [];
  rootFolders: any[] = [];
  selectedCollection: number | null = null;
  selectedRootFolder: number | null = null;
  moveFiles = false;
  clearCustomPath = false;
  dryRunOutput = 'No plan yet';
  isLoading = false;
  isDryRunning = false;

  constructor(
    private modalService: ModalService,
    private api: ApiService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.modalService.registerModal('moveSeriesModal').subscribe((config) => {
      if (config) {
        this.isVisible = true;
        this.seriesId = config.data?.seriesId || null;
        this.seriesTitle = config.data?.seriesTitle || '';
        this.selectedCollection = null;
        this.selectedRootFolder = null;
        this.moveFiles = false;
        this.clearCustomPath = false;
        this.dryRunOutput = 'No plan yet';
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
          this.collections = response.collections;
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

  onDryRun(): void {
    if (!this.selectedCollection || !this.seriesId) {
      this.notificationService.warning('Please select a target collection');
      return;
    }

    this.isDryRunning = true;
    const payload = {
      target_collection_id: this.selectedCollection,
      target_root_folder_id: this.selectedRootFolder || null,
      move_files: this.moveFiles,
      clear_custom_path: this.clearCustomPath,
      dry_run: true
    };

    this.api.post<any>(`/series/${this.seriesId}/move`, payload).subscribe({
      next: (response: any) => {
        this.isDryRunning = false;
        if (response.success) {
          this.dryRunOutput = response.plan || 'Move plan generated successfully';
        }
      },
      error: (err: any) => {
        this.isDryRunning = false;
        console.error('Error running dry run:', err);
        this.notificationService.error('Failed to generate move plan');
      }
    });
  }

  onExecuteMove(): void {
    if (!this.selectedCollection || !this.seriesId) {
      this.notificationService.warning('Please select a target collection');
      return;
    }

    this.isLoading = true;
    const payload = {
      target_collection_id: this.selectedCollection,
      target_root_folder_id: this.selectedRootFolder || null,
      move_files: this.moveFiles,
      clear_custom_path: this.clearCustomPath,
      dry_run: false
    };

    this.api.post<any>(`/series/${this.seriesId}/move`, payload).subscribe({
      next: (response: any) => {
        this.isLoading = false;
        if (response.success) {
          this.notificationService.success('Series moved successfully');
          this.modalService.setModalResult('moveSeriesModal', { action: 'move', data: response.data });
          this.closeModal();
        }
      },
      error: (err: any) => {
        this.isLoading = false;
        console.error('Error moving series:', err);
        this.notificationService.error('Failed to move series');
      }
    });
  }

  closeModal(): void {
    this.isVisible = false;
    this.modalService.closeModal('moveSeriesModal');
  }
}
