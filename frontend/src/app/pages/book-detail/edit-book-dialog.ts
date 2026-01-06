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
  selector: 'app-edit-book-dialog',
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
    <form [formGroup]="editForm" (ngSubmit)="onSubmit()">
      <h2 mat-dialog-title>Edit Book</h2>
      <mat-dialog-content>
        <div class="row">
          <div class="col-md-6">
            <mat-form-field appearance="outline" class="w-100 mb-3">
              <mat-label>Title</mat-label>
              <input matInput formControlName="title" required>
            </mat-form-field>

            <mat-form-field appearance="outline" class="w-100 mb-3">
              <mat-label>Author</mat-label>
              <input matInput formControlName="author">
            </mat-form-field>

            <mat-form-field appearance="outline" class="w-100 mb-3">
              <mat-label>Publisher</mat-label>
              <input matInput formControlName="publisher">
            </mat-form-field>

            <mat-form-field appearance="outline" class="w-100 mb-3">
              <mat-label>Published Date</mat-label>
              <input matInput formControlName="publishedDate">
            </mat-form-field>

            <mat-form-field appearance="outline" class="w-100 mb-3">
              <mat-label>ISBN</mat-label>
              <input matInput formControlName="isbn">
            </mat-form-field>
          </div>

          <div class="col-md-6">
            <mat-form-field appearance="outline" class="w-100 mb-3">
              <mat-label>Cover URL</mat-label>
              <input matInput formControlName="coverUrl">
            </mat-form-field>

            <mat-form-field appearance="outline" class="w-100 mb-3">
              <mat-label>Genres (comma-separated)</mat-label>
              <input matInput formControlName="genres">
            </mat-form-field>

            <mat-form-field appearance="outline" class="w-100 mb-3">
              <mat-label>Collection</mat-label>
              <mat-select formControlName="collection">
                <mat-option value="">-- None --</mat-option>
                <mat-option *ngFor="let coll of data.collections" [value]="coll.id">
                  {{ coll.name }}
                </mat-option>
              </mat-select>
            </mat-form-field>

            <mat-form-field appearance="outline" class="w-100 mb-3">
              <mat-label>Custom Folder Path (optional)</mat-label>
              <input matInput formControlName="customPath">
            </mat-form-field>
          </div>
        </div>

        <mat-form-field appearance="outline" class="w-100 mb-3">
          <mat-label>Description</mat-label>
          <textarea matInput formControlName="description" rows="5"></textarea>
        </mat-form-field>
      </mat-dialog-content>
      
      <mat-dialog-actions align="end">
        <button mat-button type="button" (click)="onCancel()">Cancel</button>
        <button mat-raised-button color="primary" type="submit">Save Changes</button>
      </mat-dialog-actions>
    </form>
  `,
  styles: [`
    .w-100 { width: 100%; }
    .mb-3 { margin-bottom: 1rem; }
    mat-dialog-content { padding: 20px; }
    mat-dialog-actions { padding: 20px; }
  `]
})
export class EditBookDialog {
  editForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<EditBookDialog>,
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
