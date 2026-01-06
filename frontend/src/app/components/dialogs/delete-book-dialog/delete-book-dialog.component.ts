import { Component, Inject } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDialogModule } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { CommonModule } from '@angular/common';
import { Series } from '../../../models/series.model';

export interface DeleteBookDialogData {
  book: Series;
}

@Component({
  selector: 'app-delete-book-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatCheckboxModule,
    MatDialogModule,
    MatProgressSpinnerModule,
    MatIconModule,
    MatCardModule,
    ReactiveFormsModule
  ],
  template: `
    <div class="delete-dialog-container">
      <div class="dialog-header">
        <mat-icon class="warning-icon">warning</mat-icon>
        <h2 mat-dialog-title>Delete Book</h2>
        <button mat-icon-button (click)="onCancel()" class="close-button">
          <mat-icon>close</mat-icon>
        </button>
      </div>

      <mat-dialog-content class="dialog-content">
        <!-- Warning Alert -->
        <mat-card class="warning-card" appearance="outlined">
          <mat-card-content class="warning-content">
            <div class="warning-text">
              <h3>Are you sure you want to delete this book?</h3>
              <p>This action cannot be undone and will permanently remove the book from your library.</p>
            </div>
          </mat-card-content>
        </mat-card>

        <!-- Book Preview -->
        <mat-card class="book-preview-card" appearance="outlined">
          <mat-card-content>
            <div class="book-info">
              <div class="book-cover">
                <img [src]="getCoverUrl(data.book.cover_url)" 
                     [alt]="data.book.title || data.book.name"
                     class="cover-image"
                     *ngIf="data.book.cover_url; else noCover">
                <ng-template #noCover>
                  <div class="cover-placeholder">
                    <mat-icon>book</mat-icon>
                  </div>
                </ng-template>
              </div>
              <div class="book-details">
                <h4>{{ data.book.title || data.book.name }}</h4>
                <p class="author" *ngIf="data.book.author">by {{ data.book.author }}</p>
                <div class="book-meta">
                  <span class="meta-item" *ngIf="data.book.publisher">
                    <mat-icon>business</mat-icon>
                    {{ data.book.publisher }}
                  </span>
                  <span class="meta-item" *ngIf="data.book.published_date">
                    <mat-icon>calendar_today</mat-icon>
                    {{ data.book.published_date }}
                  </span>
                  <span class="meta-item" *ngIf="data.book.isbn">
                    <mat-icon>tag</mat-icon>
                    ISBN: {{ data.book.isbn }}
                  </span>
                </div>
              </div>
            </div>
          </mat-card-content>
        </mat-card>

        <!-- Delete Options -->
        <div class="delete-options">
          <mat-checkbox formControlName="deleteFiles" class="delete-files-checkbox">
            <span class="checkbox-label">
              <mat-icon class="checkbox-icon">delete_forever</mat-icon>
              Also delete e-book files from disk
            </span>
          </mat-checkbox>
          <p class="checkbox-help">This will permanently remove all e-book files associated with this book.</p>
        </div>

        <!-- Loading State -->
        <div *ngIf="isDeleting" class="loading-state">
          <mat-spinner diameter="32"></mat-spinner>
          <p>Deleting book...</p>
        </div>
      </mat-dialog-content>

      <mat-dialog-actions align="end" class="dialog-actions">
        <button mat-button (click)="onCancel()" [disabled]="isDeleting" class="cancel-button">
          Cancel
        </button>
        <button mat-raised-button color="warn" (click)="onDelete()" [disabled]="isDeleting" class="delete-button">
          <mat-icon *ngIf="!isDeleting">delete</mat-icon>
          <mat-spinner diameter="16" *ngIf="isDeleting"></mat-spinner>
          {{ isDeleting ? 'Deleting...' : 'Delete Book' }}
        </button>
      </mat-dialog-actions>
    </div>
  `,
  styles: [`
    .delete-dialog-container {
      min-width: 500px;
      max-width: 90vw;
    }

    .dialog-header {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 20px 24px 16px;
      border-bottom: 1px solid #e0e0e0;
      background: #fafafa;
    }

    .warning-icon {
      color: #f44336;
      font-size: 24px;
    }

    .dialog-header h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 500;
      color: #d32f2f;
      flex: 1;
    }

    .close-button {
      color: #666;
    }

    .close-button:hover {
      color: #333;
    }

    .dialog-content {
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .warning-card {
      border: 1px solid #ffcdd2;
      background: #ffebee;
    }

    .warning-content {
      padding: 16px;
    }

    .warning-text h3 {
      margin: 0 0 8px 0;
      color: #d32f2f;
      font-size: 16px;
      font-weight: 500;
    }

    .warning-text p {
      margin: 0;
      color: #666;
      font-size: 14px;
    }

    .book-preview-card {
      border: 1px solid #e0e0e0;
    }

    .book-info {
      display: flex;
      gap: 16px;
      padding: 16px;
    }

    .book-cover {
      flex-shrink: 0;
    }

    .cover-image {
      width: 80px;
      height: 120px;
      object-fit: cover;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .cover-placeholder {
      width: 80px;
      height: 120px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f5f5f5;
      border-radius: 8px;
      border: 1px solid #e0e0e0;
      color: #999;
    }

    .book-details {
      flex: 1;
    }

    .book-details h4 {
      margin: 0 0 8px 0;
      font-size: 16px;
      font-weight: 500;
      color: #333;
    }

    .author {
      margin: 0 0 12px 0;
      color: #666;
      font-size: 14px;
    }

    .book-meta {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .meta-item {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: #666;
    }

    .meta-item mat-icon {
      font-size: 16px;
      height: 16px;
      width: 16px;
    }

    .delete-options {
      padding: 16px;
      background: #f8f9fa;
      border-radius: 8px;
      border: 1px solid #e9ecef;
    }

    .delete-files-checkbox {
      margin-bottom: 8px;
    }

    .checkbox-label {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 500;
    }

    .checkbox-icon {
      color: #f44336;
      font-size: 18px;
    }

    .checkbox-help {
      margin: 0;
      font-size: 12px;
      color: #666;
      margin-left: 28px;
    }

    .loading-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      padding: 20px;
      color: #666;
    }

    .dialog-actions {
      padding: 16px 24px;
      border-top: 1px solid #e0e0e0;
      background: #fafafa;
      gap: 12px;
    }

    .cancel-button {
      color: #666;
    }

    .delete-button {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 120px;
    }

    /* Dark mode support */
    :host-context(body.dark-theme) .delete-dialog-container {
      background: #1e1e1e;
      color: #fff;
    }

    :host-context(body.dark-theme) .dialog-header {
      background: #2d2d2d;
      border-bottom-color: #444;
    }

    :host-context(body.dark-theme) .dialog-header h2 {
      color: #ff6b6b;
    }

    :host-context(body.dark-theme) .warning-card {
      background: #2d1b1b;
      border-color: #5d2d2d;
    }

    :host-context(body.dark-theme) .warning-text h3 {
      color: #ff6b6b;
    }

    :host-context(body.dark-theme) .warning-text p {
      color: #ccc;
    }

    :host-context(body.dark-theme) .book-preview-card {
      background: #2d2d2d;
      border-color: #444;
    }

    :host-context(body.dark-theme) .book-details h4 {
      color: #fff;
    }

    :host-context(body.dark-theme) .author {
      color: #ccc;
    }

    :host-context(body.dark-theme) .meta-item {
      color: #ccc;
    }

    :host-context(body.dark-theme) .delete-options {
      background: #2d2d2d;
      border-color: #444;
    }

    :host-context(body.dark-theme) .checkbox-label {
      color: #fff;
    }

    :host-context(body.dark-theme) .checkbox-help {
      color: #ccc;
    }

    :host-context(body.dark-theme) .dialog-actions {
      background: #2d2d2d;
      border-top-color: #444;
    }

    :host-context(body.dark-theme) .cancel-button {
      color: #ccc;
    }

    /* Responsive */
    @media (max-width: 600px) {
      .delete-dialog-container {
        min-width: auto;
        max-width: 95vw;
      }

      .book-info {
        flex-direction: column;
        text-align: center;
      }

      .book-meta {
        align-items: center;
      }

      .dialog-actions {
        flex-direction: column;
      }

      .cancel-button,
      .delete-button {
        width: 100%;
      }
    }
  `]
})
export class DeleteBookDialogComponent {
  deleteForm: FormGroup;
  isDeleting = false;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<DeleteBookDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: DeleteBookDialogData
  ) {
    this.deleteForm = this.fb.group({
      deleteFiles: [false]
    });
  }

  getCoverUrl(coverUrl: string | null | undefined): string {
    if (!coverUrl) return '';
    if (coverUrl.startsWith('http')) return coverUrl;
    return `/api/books/cover/${coverUrl}`;
  }

  onDelete(): void {
    if (this.isDeleting) return;
    
    this.isDeleting = true;
    
    const result = {
      deleted: true,
      deleteFiles: this.deleteForm.value.deleteFiles
    };
    
    // Simulate async operation
    setTimeout(() => {
      this.dialogRef.close(result);
      this.isDeleting = false;
    }, 1500);
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}
