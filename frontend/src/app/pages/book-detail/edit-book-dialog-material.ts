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
  selector: 'app-edit-book-dialog-material',
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
    <div class="edit-book-dialog">
      <h2 class="dialog-title">Edit Book</h2>
      
      <div class="dialog-content">
        <div class="form-grid">
          <!-- Left Column -->
          <div class="form-column">
            <mat-form-field appearance="outline" class="form-field">
              <mat-label class="field-label">Title</mat-label>
              <input matInput formControlName="title" required class="field-input">
            </mat-form-field>

            <mat-form-field appearance="outline" class="form-field">
              <mat-label class="field-label">Author</mat-label>
              <input matInput formControlName="author" class="field-input">
            </mat-form-field>

            <mat-form-field appearance="outline" class="form-field">
              <mat-label class="field-label">Publisher</mat-label>
              <input matInput formControlName="publisher" class="field-input">
            </mat-form-field>

            <mat-form-field appearance="outline" class="form-field">
              <mat-label class="field-label">Published Date</mat-label>
              <input matInput formControlName="publishedDate" class="field-input">
            </mat-form-field>

            <mat-form-field appearance="outline" class="form-field">
              <mat-label class="field-label">ISBN</mat-label>
              <input matInput formControlName="isbn" class="field-input">
            </mat-form-field>
          </div>

          <!-- Right Column -->
          <div class="form-column">
            <mat-form-field appearance="outline" class="form-field">
              <mat-label class="field-label">Cover URL</mat-label>
              <input matInput formControlName="coverUrl" class="field-input">
            </mat-form-field>

            <mat-form-field appearance="outline" class="form-field">
              <mat-label class="field-label">Genres (comma-separated)</mat-label>
              <input matInput formControlName="genres" class="field-input">
            </mat-form-field>

            <mat-form-field appearance="outline" class="form-field">
              <mat-label class="field-label">Collection</mat-label>
              <mat-select formControlName="collection" class="field-select">
                <mat-option value="">-- None --</mat-option>
                <mat-option *ngFor="let coll of data.collections" [value]="coll.id">
                  {{ coll.name }}
                </mat-option>
              </mat-select>
            </mat-form-field>

            <mat-form-field appearance="outline" class="form-field">
              <mat-label class="field-label">Custom Folder Path (optional)</mat-label>
              <input matInput formControlName="customPath" class="field-input">
            </mat-form-field>
          </div>
        </div>

        <!-- Description Field (Full Width) -->
        <div class="form-section">
          <mat-form-field appearance="outline" class="form-field full-width">
            <mat-label class="field-label">Description</mat-label>
            <textarea matInput formControlName="description" rows="5" class="field-textarea"></textarea>
          </mat-form-field>
        </div>
      </div>
      
      <div class="dialog-actions">
        <button class="action-btn cancel-btn" (click)="onCancel()">Cancel</button>
        <button class="action-btn save-btn" (click)="onSubmit()">Save Changes</button>
      </div>
    </div>
  `,
  styles: [`
    .edit-book-dialog {
      background: #ffffff;
      border-radius: 8px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
      min-width: 800px;
      max-width: 90vw;
      overflow: hidden;
    }

    .dialog-title {
      margin: 0;
      padding: 24px 24px 16px 24px;
      font-size: 1.5rem;
      font-weight: 600;
      color: #212529;
      border-bottom: 1px solid #dee2e6;
      background: #f8f9fa;
    }

    .dialog-content {
      padding: 24px;
      max-height: 70vh;
      overflow-y: auto;
    }

    .form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 20px;
    }

    .form-column {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .form-section {
      margin-top: 20px;
    }

    .form-field {
      width: 100%;
    }

    .full-width {
      grid-column: 1 / -1;
    }

    /* Override Angular Material form field styles to match Bootstrap */
    .form-field .mat-mdc-form-field-flex {
      background: #ffffff;
      border: 1px solid #ced4da;
      border-radius: 6px;
      padding: 0 16px;
      height: 56px;
      align-items: center;
      transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
    }

    .form-field .mat-mdc-form-field-flex:hover {
      border-color: #86b7fe;
    }

    .form-field.mat-focused .mat-mdc-form-field-flex {
      border-color: #0d6efd;
      box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
    }

    .form-field .mat-mdc-form-field-label {
      color: #6c757d;
      font-size: 0.875rem;
      font-weight: 500;
      top: 50%;
      transform: translateY(-50%);
    }

    .form-field.mat-mdc-form-field-focus .mat-mdc-form-field-label {
      color: #0d6efd;
      top: 0;
      transform: translateY(0) scale(0.75);
    }

    .form-field .mat-mdc-text-field-wrapper {
      padding: 0;
    }

    .field-input,
    .field-textarea {
      color: #212529;
      font-size: 1rem;
      font-family: system-ui, -apple-system, sans-serif;
      border: none !important;
      outline: none !important;
      background: transparent !important;
      padding: 0 !important;
      height: auto !important;
    }

    .field-input::placeholder,
    .field-textarea::placeholder {
      color: #6c757d;
      opacity: 1;
    }

    .field-select .mat-mdc-select-value {
      color: #212529;
    }

    .field-textarea {
      resize: vertical;
      min-height: 120px !important;
      padding: 16px !important;
    }

    .form-field .mat-mdc-form-field-infix {
      padding: 0;
      border-top: none;
    }

    /* Textarea specific overrides */
    .form-field textarea.mat-mdc-input-element {
      padding: 16px !important;
      height: auto !important;
    }

    .dialog-actions {
      padding: 16px 24px 24px 24px;
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      border-top: 1px solid #dee2e6;
      background: #f8f9fa;
    }

    .action-btn {
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 0.875rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s ease-in-out;
      border: 1px solid transparent;
      min-width: 100px;
    }

    .cancel-btn {
      background: #6c757d;
      color: #ffffff;
      border-color: #6c757d;
    }

    .cancel-btn:hover {
      background: #5c636a;
      border-color: #5c636a;
      transform: translateY(-1px);
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .save-btn {
      background: #0d6efd;
      color: #ffffff;
      border-color: #0d6efd;
    }

    .save-btn:hover {
      background: #0b5ed7;
      border-color: #0b5ed7;
      transform: translateY(-1px);
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .action-btn:active {
      transform: translateY(0);
      box-shadow: none;
    }

    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
      .edit-book-dialog {
        background: #212529;
        color: #ffffff;
      }

      .dialog-title {
        background: #343a40;
        color: #ffffff;
        border-bottom-color: #495057;
      }

      .dialog-content {
        background: #212529;
      }

      .form-field .mat-mdc-form-field-flex {
        background: #343a40;
        border-color: #495057;
        color: #ffffff;
      }

      .form-field .mat-mdc-form-field-flex:hover {
        border-color: #6ea8fe;
      }

      .form-field.mat-focused .mat-mdc-form-field-flex {
        border-color: #0d6efd;
        box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
      }

      .form-field .mat-mdc-form-field-label {
        color: #adb5bd;
      }

      .form-field.mat-mdc-form-field-focus .mat-mdc-form-field-label {
        color: #0d6efd;
      }

      .field-input,
      .field-textarea {
        color: #ffffff !important;
      }

      .field-select .mat-mdc-select-value {
        color: #ffffff;
      }

      .dialog-actions {
        background: #343a40;
        border-top-color: #495057;
      }
    }

    /* Responsive design */
    @media (max-width: 768px) {
      .edit-book-dialog {
        min-width: auto;
        width: 95vw;
        margin: 0;
      }

      .form-grid {
        grid-template-columns: 1fr;
        gap: 16px;
      }

      .dialog-content {
        padding: 16px;
      }

      .dialog-title {
        padding: 16px;
      }

      .dialog-actions {
        padding: 12px 16px 16px 16px;
        flex-direction: column;
      }

      .action-btn {
        width: 100%;
      }
    }
  `]
})
export class EditBookDialogMaterial {
  editForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<EditBookDialogMaterial>,
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
