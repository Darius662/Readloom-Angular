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
  selector: 'app-edit-book-dialog-simple',
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
    <div class="edit-dialog">
      <h2 mat-dialog-title>Edit Book</h2>
      <mat-dialog-content>
        <div class="form-layout">
          <div class="left-column">
            <mat-form-field appearance="outline">
              <mat-label>Title</mat-label>
              <input matInput formControlName="title" required>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Author</mat-label>
              <input matInput formControlName="author">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Publisher</mat-label>
              <input matInput formControlName="publisher">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Published Date</mat-label>
              <input matInput formControlName="publishedDate">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>ISBN</mat-label>
              <input matInput formControlName="isbn">
            </mat-form-field>
          </div>

          <div class="right-column">
            <mat-form-field appearance="outline">
              <mat-label>Cover URL</mat-label>
              <input matInput formControlName="coverUrl">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Genres (comma-separated)</mat-label>
              <input matInput formControlName="genres">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Collection</mat-label>
              <mat-select formControlName="collection">
                <mat-option value="">-- None --</mat-option>
                <mat-option *ngFor="let coll of data.collections" [value]="coll.id">
                  {{ coll.name }}
                </mat-option>
              </mat-select>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Custom Folder Path (optional)</mat-label>
              <input matInput formControlName="customPath">
            </mat-form-field>
          </div>
        </div>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Description</mat-label>
          <textarea matInput formControlName="description" rows="5"></textarea>
        </mat-form-field>
      </mat-dialog-content>
      
      <mat-dialog-actions align="end">
        <button mat-button (click)="onCancel()">Cancel</button>
        <button mat-raised-button color="primary" (click)="onSubmit()">Save Changes</button>
      </mat-dialog-actions>
    </div>
  `,
  styles: [`
    .edit-dialog {
      min-width: 800px;
    }

    .form-layout {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 20px;
    }

    .left-column,
    .right-column {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .full-width {
      grid-column: 1 / -1;
    }

    mat-form-field {
      width: 100%;
    }

    /* Custom styling to match Bootstrap appearance */
    .mat-mdc-form-field-flex {
      border-radius: 6px !important;
      border: 1px solid #ced4da !important;
      background-color: #fff !important;
    }

    .mat-mdc-form-field-flex:hover {
      border-color: #86b7fe !important;
    }

    .mat-mdc-form-field-focus .mat-mdc-form-field-flex {
      border-color: #0d6efd !important;
      box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25) !important;
    }

    .mat-mdc-form-field-label {
      color: #6c757d !important;
    }

    .mat-mdc-form-field-focus .mat-mdc-form-field-label {
      color: #0d6efd !important;
    }

    .mat-mdc-text-field-wrapper {
      padding: 0 !important;
    }

    .mat-mdc-form-field-infix {
      padding: 16px 0 !important;
      border-top: none !important;
    }

    .mat-mdc-input-element,
    .mat-mdc-select-value {
      color: #212529 !important;
      font-size: 1rem !important;
    }

    .mat-mdc-select-arrow {
      color: #6c757d !important;
    }

    textarea.mat-mdc-input-element {
      padding: 16px !important;
      resize: vertical;
    }

    /* Button styling */
    .mat-mdc-button {
      border-radius: 6px !important;
      font-weight: 500 !important;
      padding: 8px 16px !important;
    }

    .mat-mdc-raised-button {
      border-radius: 6px !important;
      font-weight: 500 !important;
      padding: 8px 16px !important;
    }

    @media (max-width: 768px) {
      .edit-dialog {
        min-width: auto;
        width: 95vw;
      }

      .form-layout {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class EditBookDialogSimple {
  editForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<EditBookDialogSimple>,
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
