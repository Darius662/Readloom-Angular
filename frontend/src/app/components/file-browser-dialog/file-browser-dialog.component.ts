import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { 
  MAT_DIALOG_DATA, 
  MatDialogRef, 
  MatDialogModule 
} from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatChipsModule } from '@angular/material/chips';
import { MatCardModule } from '@angular/material/card';
import { MatListModule } from '@angular/material/list';

import { FileBrowserService, FolderItem, BrowseResponse } from '../../services/file-browser.service';

export interface FileBrowserDialogData {
  initialPath?: string;
  title?: string;
  allowFileSelection?: boolean;
  allowFolderSelection?: boolean;
}

export interface FileBrowserDialogResult {
  selectedPath: string;
  selectedName: string;
  isDirectory: boolean;
}

@Component({
  selector: 'app-file-browser-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatToolbarModule,
    MatProgressSpinnerModule,
    MatDividerModule,
    MatTooltipModule,
    MatChipsModule,
    MatCardModule,
    MatListModule
  ],
  templateUrl: './file-browser-dialog.component.html',
  styleUrls: ['./file-browser-dialog.component.scss']
})
export class FileBrowserDialogComponent implements OnInit {
  isLoading = false;
  currentPath: string = '';
  selectedPath: string = '';
  selectedName: string = '';
  browseResponse: BrowseResponse | null = null;
  error: string = '';

  // Getter properties to handle null checks
  get drives(): string[] {
    return this.browseResponse?.drives || [];
  }

  get folders(): FolderItem[] {
    return this.browseResponse?.folders || [];
  }

  constructor(
    private dialogRef: MatDialogRef<FileBrowserDialogComponent, FileBrowserDialogResult>,
    @Inject(MAT_DIALOG_DATA) public data: FileBrowserDialogData,
    private fileBrowserService: FileBrowserService
  ) {}

  ngOnInit(): void {
    this.loadPath(this.data.initialPath || null);
  }

  loadPath(path: string | null): void {
    this.isLoading = true;
    this.error = '';
    
    this.fileBrowserService.browseFolders({ path: path || undefined }).subscribe({
      next: (response) => {
        this.browseResponse = response;
        this.currentPath = response.current_path;
        this.isLoading = false;
      },
      error: (error) => {
        this.error = error;
        this.isLoading = false;
      }
    });
  }

  navigateToFolder(folder: FolderItem): void {
    // All items from the folder browser API are directories
    this.loadPath(folder.path);
  }

  navigateToDrive(drive: string): void {
    this.loadPath(drive);
  }

  navigateUp(): void {
    if (this.currentPath) {
      // Handle both Windows and Unix paths
      const lastBackslash = this.currentPath.lastIndexOf('\\');
      const lastForwardSlash = this.currentPath.lastIndexOf('/');
      const lastSeparator = Math.max(lastBackslash, lastForwardSlash);
      
      if (lastSeparator > 0) {
        const parentPath = this.currentPath.substring(0, lastSeparator);
        this.loadPath(parentPath);
      } else if (lastSeparator === 0) {
        // We're at root, go to null (home)
        this.loadPath(null);
      }
    }
  }

  navigateHome(): void {
    this.loadPath(null);
  }

  selectItem(item: FolderItem): void {
    // All items from the folder browser API are directories
    if (this.data.allowFolderSelection) {
      this.selectedPath = item.path;
      this.selectedName = item.name;
    }
  }

  selectCurrentDirectory(): void {
    if (this.data.allowFolderSelection && this.currentPath) {
      this.selectedPath = this.currentPath;
      this.selectedName = this.currentPath.split(/[\\/]/).pop() || this.currentPath;
    }
  }

  confirm(): void {
    if (this.selectedPath) {
      const result: FileBrowserDialogResult = {
        selectedPath: this.selectedPath,
        selectedName: this.selectedName,
        isDirectory: true // For now, we're mainly supporting folder selection
      };
      this.dialogRef.close(result);
    }
  }

  cancel(): void {
    this.dialogRef.close();
  }

  canConfirm(): boolean {
    return !!this.selectedPath;
  }

  getIconForItem(item: FolderItem): string {
    // All items from the folder browser API are directories
    return 'folder';
  }

  formatFileSize(bytes?: number): string {
    if (!bytes) return '';
    
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`;
  }

  formatDate(dateString?: string): string {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch {
      return dateString;
    }
  }
}
