import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { Series } from '../../models/series.model';

export interface DeleteBookDialogData {
  book: Series;
}

@Component({
  selector: 'app-delete-book-dialog-material',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatDialogModule,
    MatProgressSpinnerModule,
    MatIconModule
  ],
  template: `
    <div class="bootstrap-dialog">
      <div class="modal-header">
        <h5 class="modal-title">Delete Book</h5>
        <button type="button" class="btn-close" (click)="onCancel()">&times;</button>
      </div>
      
      <div class="modal-body">
        <div class="alert alert-warning" role="alert">
          <h6 class="alert-heading">
            <i class="fas fa-exclamation-triangle me-2"></i>
            Are you sure you want to delete this book?
          </h6>
          <p class="mb-0">This action cannot be undone.</p>
        </div>

        <div class="book-preview">
          <div class="row">
            <div class="col-md-3">
              <div class="book-cover">
                <img [src]="getCoverUrl(data.book.cover_url)" 
                     [alt]="data.book.title || data.book.name"
                     class="img-fluid rounded"
                     *ngIf="data.book.cover_url">
                <div class="cover-placeholder" *ngIf="!data.book.cover_url">
                  <i class="fas fa-book"></i>
                </div>
              </div>
            </div>
            <div class="col-md-9">
              <h6 class="book-title">{{ data.book.title || data.book.name }}</h6>
              <p class="book-author text-muted" *ngIf="data.book.author">by {{ data.book.author }}</p>
              <p class="book-series text-muted" *ngIf="data.book.name">{{ data.book.name }}</p>
              <p class="book-genre text-muted" *ngIf="data.book.subjects">{{ formatSubjects(data.book.subjects) }}</p>
            </div>
          </div>
        </div>

        <div class="form-check mb-3">
          <input class="form-check-input" type="checkbox" id="deleteFiles" formControlName="deleteFiles">
          <label class="form-check-label" for="deleteFiles">
            Also delete e-book files from disk
          </label>
        </div>

        <!-- Loading State -->
        <div *ngIf="isDeleting" class="text-center py-3">
          <mat-spinner diameter="32"></mat-spinner>
          <p class="mt-2 text-muted">Deleting book...</p>
        </div>
      </div>
      
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" (click)="onCancel()" [disabled]="isDeleting">Cancel</button>
        <button type="button" class="btn btn-danger" (click)="onDelete()" [disabled]="isDeleting">
          <span *ngIf="!isDeleting">Delete Book</span>
          <span *ngIf="isDeleting">
            <mat-spinner diameter="16"></mat-spinner> Deleting...
          </span>
        </button>
      </div>
    </div>
  `,
  styles: [`
    .bootstrap-dialog {
      background: #ffffff;
      border-radius: 0.375rem;
      box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
      overflow: hidden;
      width: 500px;
      max-width: 95vw;
      margin: 0;
    }

    .modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1rem 1rem;
      border-bottom: 1px solid #dee2e6;
      background: #f8f9fa;
    }

    .modal-title {
      margin: 0;
      font-size: 1.25rem;
      font-weight: 500;
      color: #212529;
    }

    .btn-close {
      background: none;
      border: none;
      font-size: 1.5rem;
      font-weight: 700;
      line-height: 1;
      color: #6c757d;
      opacity: 0.8;
      cursor: pointer;
      padding: 0;
      width: 1.5rem;
      height: 1.5rem;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: opacity 0.15s ease;
    }

    .btn-close:hover {
      opacity: 1;
      color: #000;
    }

    .modal-body {
      padding: 1rem;
      max-height: 60vh;
      overflow-y: auto;
      background: #ffffff;
    }

    .modal-footer {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: flex-end;
      padding: 0.75rem 1rem;
      border-top: 1px solid #dee2e6;
      background: #f8f9fa;
      gap: 0.5rem;
    }

    /* Bootstrap Alert Styles */
    .alert {
      position: relative;
      padding: 0.75rem 1.25rem;
      margin-bottom: 1rem;
      border: 1px solid transparent;
      border-radius: 0.375rem;
    }

    .alert-warning {
      color: #664d03;
      background-color: #fff3cd;
      border-color: #ffecb5;
    }

    .alert-heading {
      color: inherit;
      font-size: 1rem;
      font-weight: 500;
      margin-bottom: 0.5rem;
    }

    .mb-0 {
      margin-bottom: 0 !important;
    }

    /* Bootstrap Grid Styles */
    .row {
      display: flex;
      flex-wrap: wrap;
      margin-right: -0.75rem;
      margin-left: -0.75rem;
    }

    .col-md-3 {
      flex: 0 0 auto;
      width: 25%;
      padding-right: 0.75rem;
      padding-left: 0.75rem;
    }

    .col-md-9 {
      flex: 0 0 auto;
      width: 75%;
      padding-right: 0.75rem;
      padding-left: 0.75rem;
    }

    /* Book Preview Styles */
    .book-preview {
      margin-bottom: 1rem;
    }

    .book-cover {
      margin-bottom: 0.5rem;
    }

    .img-fluid {
      max-width: 100%;
      height: auto;
    }

    .rounded {
      border-radius: 0.375rem;
    }

    .cover-placeholder {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 150px;
      background-color: #e9ecef;
      border-radius: 0.375rem;
      color: #6c757d;
      font-size: 2rem;
    }

    .book-title {
      font-size: 1.125rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: #212529;
    }

    .book-author,
    .book-series,
    .book-genre {
      margin-bottom: 0.25rem;
      font-size: 0.875rem;
      line-height: 1.4;
    }

    .text-muted {
      color: #6c757d !important;
    }

    /* Bootstrap Form Styles */
    .form-check {
      display: block;
      min-height: 1.5rem;
      padding-left: 1.5em;
      margin-bottom: 0.125rem;
    }

    .form-check-input {
      margin-top: 0.25em;
      vertical-align: top;
      background-color: #fff;
      border: 1px solid rgba(0, 0, 0, 0.25);
      border-radius: 0.25em;
      transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
    }

    .form-check-input:focus {
      border-color: #86b7fe;
      outline: 0;
      box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
    }

    .form-check-input:checked {
      background-color: #0d6efd;
      border-color: #0d6efd;
    }

    .form-check-label {
      color: #212529;
      font-size: 0.875rem;
      cursor: pointer;
    }

    /* Bootstrap Button Styles */
    .btn {
      display: inline-block;
      font-weight: 400;
      line-height: 1.5;
      color: #212529;
      text-align: center;
      text-decoration: none;
      vertical-align: middle;
      cursor: pointer;
      user-select: none;
      background-color: transparent;
      border: 1px solid transparent;
      padding: 0.375rem 0.75rem;
      font-size: 0.875rem;
      border-radius: 0.375rem;
      transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
    }

    .btn:hover {
      color: #212529;
    }

    .btn:focus {
      outline: 0;
      box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
    }

    .btn-secondary {
      color: #fff;
      background-color: #6c757d;
      border-color: #6c757d;
    }

    .btn-secondary:hover {
      color: #fff;
      background-color: #5c636a;
      border-color: #565e64;
    }

    .btn-secondary:focus {
      color: #fff;
      background-color: #6c757d;
      border-color: #6c757d;
      box-shadow: 0 0 0 0.25rem rgba(108, 117, 125, 0.25);
    }

    .btn-danger {
      color: #fff;
      background-color: #dc3545;
      border-color: #dc3545;
    }

    .btn-danger:hover {
      color: #fff;
      background-color: #bb2d3b;
      border-color: #b02a37;
    }

    .btn-danger:focus {
      color: #fff;
      background-color: #dc3545;
      border-color: #dc3545;
      box-shadow: 0 0 0 0.25rem rgba(220, 53, 69, 0.25);
    }

    .btn:disabled {
      opacity: 0.65;
      cursor: not-allowed;
    }

    /* Utility Classes */
    .text-center {
      text-align: center !important;
    }

    .py-3 {
      padding-top: 1rem !important;
      padding-bottom: 1rem !important;
    }

    .mt-2 {
      margin-top: 0.5rem !important;
    }

    .mb-3 {
      margin-bottom: 1rem !important;
    }

    .me-2 {
      margin-right: 0.5rem !important;
    }

    /* Font Awesome Icons (simulated with Unicode) */
    .fas::before {
      font-family: "Font Awesome 5 Free";
      font-weight: 900;
    }

    .fa-exclamation-triangle::before {
      content: "⚠";
      font-family: sans-serif;
    }

    .fa-book::before {
      content: "📚";
      font-family: sans-serif;
    }

    /* Responsive */
    @media (max-width: 768px) {
      .bootstrap-dialog {
        width: 95vw;
        margin: 0;
      }

      .modal-footer {
        justify-content: stretch;
      }

      .btn {
        flex: 1;
      }

      .col-md-3,
      .col-md-9 {
        width: 100%;
      }

      .book-preview .row {
        flex-direction: column;
      }
    }

    /* Dark mode support */
    body.dark-theme .bootstrap-dialog,
    :host-context(body.dark-theme) .bootstrap-dialog {
      background: #212529;
      color: #ffffff;
    }

    body.dark-theme .bootstrap-dialog .modal-header,
    :host-context(body.dark-theme) .bootstrap-dialog .modal-header {
      background: #343a40;
      border-bottom-color: #495057;
    }

    body.dark-theme .bootstrap-dialog .modal-title,
    :host-context(body.dark-theme) .bootstrap-dialog .modal-title {
      color: #ffffff;
    }

    body.dark-theme .bootstrap-dialog .btn-close,
    :host-context(body.dark-theme) .bootstrap-dialog .btn-close {
      color: #adb5bd;
    }

    body.dark-theme .bootstrap-dialog .btn-close:hover,
    :host-context(body.dark-theme) .bootstrap-dialog .btn-close:hover {
      color: #ffffff;
    }

    body.dark-theme .bootstrap-dialog .modal-body,
    :host-context(body.dark-theme) .bootstrap-dialog .modal-body {
      background: #212529;
    }

    body.dark-theme .bootstrap-dialog .modal-footer,
    :host-context(body.dark-theme) .bootstrap-dialog .modal-footer {
      background: #343a40;
      border-top-color: #495057;
    }

    body.dark-theme .bootstrap-dialog .alert-warning,
    :host-context(body.dark-theme) .bootstrap-dialog .alert-warning {
      color: #ffecb5;
      background-color: #664d03;
      border-color: #5a4a00;
    }

    body.dark-theme .bootstrap-dialog .book-title,
    :host-context(body.dark-theme) .bootstrap-dialog .book-title {
      color: #ffffff;
    }

    body.dark-theme .bootstrap-dialog .text-muted,
    :host-context(body.dark-theme) .bootstrap-dialog .text-muted {
      color: #adb5bd !important;
    }

    body.dark-theme .bootstrap-dialog .form-check-label,
    :host-context(body.dark-theme) .bootstrap-dialog .form-check-label {
      color: #ffffff;
    }

    body.dark-theme .bootstrap-dialog .cover-placeholder,
    :host-context(body.dark-theme) .bootstrap-dialog .cover-placeholder {
      background-color: #495057;
      color: #6c757d;
    }
  `]
})
export class DeleteBookDialogMaterial {
  deleteForm: FormGroup;
  isDeleting = false;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<DeleteBookDialogMaterial>,
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

  formatSubjects(subjects: string | string[] | null | undefined): string {
    if (!subjects) return '';
    if (typeof subjects === 'string') {
      return subjects.split(',').map((s: string) => s.trim()).join(', ');
    }
    if (Array.isArray(subjects)) {
      return (subjects as string[]).filter((s: string) => s).join(', ');
    }
    return '';
  }

  onDelete(): void {
    this.isDeleting = true;
    
    // Simulate delete operation
    setTimeout(() => {
      const result = {
        deleted: true,
        deleteFiles: this.deleteForm.value.deleteFiles
      };
      this.dialogRef.close(result);
      this.isDeleting = false;
    }, 2000);
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}
