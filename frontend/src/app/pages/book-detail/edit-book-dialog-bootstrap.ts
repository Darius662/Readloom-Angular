import { Component, Inject } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDialogModule } from '@angular/material/dialog';
import { Series } from '../../models/series.model';

export interface EditBookDialogData {
  book: Series;
  collections: any[];
}

@Component({
  selector: 'app-edit-book-dialog-bootstrap',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatDialogModule
  ],
  template: `
    <div class="bootstrap-dialog">
      <div class="modal-header">
        <h5 class="modal-title">Edit Book</h5>
        <button type="button" class="btn-close" (click)="onCancel()">&times;</button>
      </div>
      
      <div class="modal-body">
        <form [formGroup]="editForm" class="bootstrap-form">
          <div class="row">
            <div class="col-md-6">
              <div class="mb-3">
                <label for="title" class="form-label">Title</label>
                <input type="text" class="form-control" id="title" formControlName="title" required>
              </div>

              <div class="mb-3">
                <label for="author" class="form-label">Author</label>
                <input type="text" class="form-control" id="author" formControlName="author">
              </div>

              <div class="mb-3">
                <label for="publisher" class="form-label">Publisher</label>
                <input type="text" class="form-control" id="publisher" formControlName="publisher">
              </div>

              <div class="mb-3">
                <label for="publishedDate" class="form-label">Published Date</label>
                <input type="text" class="form-control" id="publishedDate" formControlName="publishedDate">
              </div>

              <div class="mb-3">
                <label for="isbn" class="form-label">ISBN</label>
                <input type="text" class="form-control" id="isbn" formControlName="isbn">
              </div>
            </div>

            <div class="col-md-6">
              <div class="mb-3">
                <label for="coverUrl" class="form-label">Cover URL</label>
                <input type="text" class="form-control" id="coverUrl" formControlName="coverUrl">
              </div>

              <div class="mb-3">
                <label for="genres" class="form-label">Genres (comma-separated)</label>
                <input type="text" class="form-control" id="genres" formControlName="genres">
              </div>

              <div class="mb-3">
                <label for="collection" class="form-label">Collection</label>
                <select class="form-select" id="collection" formControlName="collection">
                  <option value="">-- None --</option>
                  <option *ngFor="let coll of data.collections" [value]="coll.id">
                    {{ coll.name }}
                  </option>
                </select>
              </div>

              <div class="mb-3">
                <label for="customPath" class="form-label">Custom Folder Path (optional)</label>
                <input type="text" class="form-control" id="customPath" formControlName="customPath">
              </div>
            </div>
          </div>

          <div class="mb-3">
            <label for="description" class="form-label">Description</label>
            <textarea class="form-control" id="description" rows="5" formControlName="description"></textarea>
          </div>
        </form>
      </div>
      
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" (click)="onCancel()">Cancel</button>
        <button type="button" class="btn btn-primary" (click)="onSubmit()">Save Changes</button>
      </div>
    </div>
  `,
  styles: [`
    .bootstrap-dialog {
      background: #ffffff;
      border-radius: 0.375rem;
      box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
      overflow: hidden;
      width: 600px;
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

    /* Bootstrap form styles */
    .bootstrap-form {
      margin: 0;
    }

    .mb-3 {
      margin-bottom: 1rem !important;
    }

    .form-label {
      margin-bottom: 0.5rem;
      font-weight: 500;
      color: #212529;
      font-size: 0.875rem;
    }

    .form-control {
      display: block;
      width: 100%;
      padding: 0.375rem 0.75rem;
      font-size: 1rem;
      font-weight: 400;
      line-height: 1.5;
      color: #212529;
      background-color: #fff;
      background-image: none;
      border: 1px solid #ced4da;
      border-radius: 0.375rem;
      transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
    }

    .form-control:focus {
      color: #212529;
      background-color: #fff;
      border-color: #86b7fe;
      outline: 0;
      box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
    }

    .form-select {
      display: block;
      width: 100%;
      padding: 0.375rem 2.25rem 0.375rem 0.75rem;
      font-size: 1rem;
      font-weight: 400;
      line-height: 1.5;
      color: #212529;
      background-color: #fff;
      background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23343a40' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='m1 6 7 7 7-7'/%3e%3c/svg%3e");
      background-repeat: no-repeat;
      background-position: right 0.75rem center;
      background-size: 16px 12px;
      border: 1px solid #ced4da;
      border-radius: 0.375rem;
      transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
      appearance: none;
    }

    .form-select:focus {
      border-color: #86b7fe;
      outline: 0;
      box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
    }

    textarea.form-control {
      resize: vertical;
      min-height: 120px;
    }

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

    .btn-primary {
      color: #fff;
      background-color: #0d6efd;
      border-color: #0d6efd;
    }

    .btn-primary:hover {
      color: #fff;
      background-color: #0b5ed7;
      border-color: #0a58ca;
    }

    .btn-primary:focus {
      color: #fff;
      background-color: #0d6efd;
      border-color: #0d6efd;
      box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
    }

    /* Grid system */
    .row {
      display: flex;
      flex-wrap: wrap;
      margin-right: -0.75rem;
      margin-left: -0.75rem;
    }

    .col-md-6 {
      flex: 0 0 auto;
      width: 50%;
      padding-right: 0.75rem;
      padding-left: 0.75rem;
    }

    /* Responsive */
    @media (max-width: 1200px) {
      .bootstrap-dialog {
        width: 550px;
      }
    }

    @media (max-width: 992px) {
      .bootstrap-dialog {
        width: 500px;
      }
    }

    @media (max-width: 768px) {
      .bootstrap-dialog {
        width: 95vw;
        margin: 0;
      }

      .col-md-6 {
        width: 100%;
      }

      .modal-footer {
        justify-content: stretch;
      }

      .btn {
        flex: 1;
      }
    }

    @media (max-width: 576px) {
      .bootstrap-dialog {
        width: 98vw;
      }

      .modal-header,
      .modal-body,
      .modal-footer {
        padding: 0.75rem;
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

    body.dark-theme .bootstrap-dialog .form-label,
    :host-context(body.dark-theme) .bootstrap-dialog .form-label {
      color: #ffffff;
    }

    body.dark-theme .bootstrap-dialog .form-control,
    :host-context(body.dark-theme) .bootstrap-dialog .form-control {
      background-color: #343a40;
      border-color: #495057;
      color: #ffffff;
    }

    body.dark-theme .bootstrap-dialog .form-control:focus,
    :host-context(body.dark-theme) .bootstrap-dialog .form-control:focus {
      background-color: #343a40;
      border-color: #0d6efd;
      color: #ffffff;
    }

    body.dark-theme .bootstrap-dialog .form-select,
    :host-context(body.dark-theme) .bootstrap-dialog .form-select {
      background-color: #343a40;
      border-color: #495057;
      color: #ffffff;
    }

    body.dark-theme .bootstrap-dialog .form-select:focus,
    :host-context(body.dark-theme) .bootstrap-dialog .form-select:focus {
      background-color: #343a40;
      border-color: #0d6efd;
      color: #ffffff;
    }

    body.dark-theme .bootstrap-dialog textarea.form-control,
    :host-context(body.dark-theme) .bootstrap-dialog textarea.form-control {
      background-color: #343a40;
      color: #ffffff;
    }
  `]
})
export class EditBookDialogBootstrap {
  editForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<EditBookDialogBootstrap>,
    @Inject(MAT_DIALOG_DATA) public data: EditBookDialogData
  ) {
    this.editForm = this.fb.group({
      title: [''],
      author: [''],
      publisher: [''],
      publishedDate: [''],
      isbn: [''],
      coverUrl: [''],
      genres: [''],
      collection: [''],
      customPath: [''],
      description: ['']
    });
  }

  ngOnInit(): void {
    const book = this.data.book;
    const subjects = (book as any).subjects;
    const genres = Array.isArray(subjects) ? subjects.join(', ') : (subjects || '');

    this.editForm.patchValue({
      title: book.title || book.name || '',
      author: book.author || '',
      publisher: book.publisher || '',
      publishedDate: (book as any).published_date || '',
      isbn: (book as any).isbn || '',
      coverUrl: book.cover_url || '',
      genres: genres,
      collection: (book as any).collection_id || '',
      customPath: (book as any).folder_path || '',
      description: book.description || ''
    });
  }

  onSubmit(): void {
    if (this.editForm.valid) {
      const formValue = this.editForm.value;
      const updateData = {
        title: formValue.title,
        author: formValue.author,
        publisher: formValue.publisher,
        published_date: formValue.publishedDate,
        isbn: formValue.isbn,
        cover_url: formValue.coverUrl,
        subjects: formValue.genres,
        collection_id: formValue.collection,
        folder_path: formValue.customPath,
        description: formValue.description
      };

      this.dialogRef.close(updateData);
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}
