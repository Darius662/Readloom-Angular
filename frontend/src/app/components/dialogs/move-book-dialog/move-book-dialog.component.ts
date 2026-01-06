import { Component, Inject } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDialogModule } from '@angular/material/dialog';
import { Series } from '../../../models/series.model';

export interface MoveBookDialogData {
  book: Series;
  collections: any[];
  rootFolders: any[];
}

@Component({
  selector: 'app-move-book-dialog',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatSelectModule,
    MatCheckboxModule,
    MatDialogModule
  ],
  template: `
    <form [formGroup]="moveForm" (ngSubmit)="onSubmit()">
      <h2 mat-dialog-title>Move Book</h2>
      <mat-dialog-content>
        <mat-form-field appearance="outline" class="w-100 mb-3">
          <mat-label>Target Collection</mat-label>
          <mat-select formControlName="targetCollection">
            <mat-option *ngFor="let coll of data.collections" [value]="coll.id">
              {{ coll.name }}
            </mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline" class="w-100 mb-3">
          <mat-label>Target Root Folder (optional)</mat-label>
          <mat-select formControlName="targetRootFolder">
            <mat-option value="">Auto-select first root folder</mat-option>
            <mat-option *ngFor="let folder of data.rootFolders" [value]="folder.id">
              {{ folder.name }}
            </mat-option>
          </mat-select>
        </mat-form-field>

        <div class="mb-3">
          <mat-checkbox formControlName="moveFiles">
            Physically move files
          </mat-checkbox>
        </div>

        <div class="mb-3">
          <mat-checkbox formControlName="clearCustomPath">
            Clear custom path after move
          </mat-checkbox>
        </div>

        <div class="preview-section">
          <h3>Dry Run Preview</h3>
          <div class="preview-content">
            <small class="text-muted">Preview will appear here</small>
          </div>
        </div>
      </mat-dialog-content>
      
      <mat-dialog-actions align="end">
        <button mat-button type="button" (click)="onPreview()">Preview (Dry Run)</button>
        <button mat-button type="button" (click)="onCancel()">Cancel</button>
        <button mat-raised-button color="primary" type="submit">Execute Move</button>
      </mat-dialog-actions>
    </form>
  `,
  styles: [`
    .w-100 { width: 100%; }
    .mb-3 { margin-bottom: 1rem; }
    mat-dialog-content { padding: 20px; }
    mat-dialog-actions { padding: 20px; }
    .preview-section { margin-top: 1rem; }
    .preview-content { 
      background-color: #f5f5f5; 
      padding: 1rem; 
      border-radius: 4px; 
      min-height: 100px; 
      max-height: 200px; 
      overflow-y: auto; 
    }
    .text-muted { color: #666; }
  `]
})
export class MoveBookDialogComponent {
  moveForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<MoveBookDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: MoveBookDialogData
  ) {
    this.moveForm = this.fb.group({
      targetCollection: [''],
      targetRootFolder: [''],
      moveFiles: [false],
      clearCustomPath: [false]
    });
  }

  onSubmit(): void {
    if (this.moveForm.valid) {
      this.dialogRef.close(this.moveForm.value);
    }
  }

  onPreview(): void {
    // TODO: Implement dry run preview
    console.log('Dry run preview not implemented yet');
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}
