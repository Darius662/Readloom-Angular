import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDialogModule } from '@angular/material/dialog';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { Series } from '../../models/series.model';

export interface MoveBookDialogData {
  book: Series;
  collections: any[];
  rootFolders: any[];
}

@Component({
  selector: 'app-move-book-dialog-material',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatDialogModule,
    MatCheckboxModule,
    MatProgressSpinnerModule,
    MatIconModule
  ],
  template: `
    <div class="bootstrap-dialog">
      <div class="modal-header">
        <h5 class="modal-title">Move Book</h5>
        <button type="button" class="btn-close" (click)="onCancel()">&times;</button>
      </div>
      
      <div class="modal-body">
        <form [formGroup]="moveForm" class="bootstrap-form">
          <div class="mb-3">
            <label for="collection" class="form-label">Target Collection</label>
            <select class="form-select" id="collection" formControlName="collection">
              <option value="">-- Select Collection --</option>
              <option *ngFor="let coll of data.collections" [value]="coll.id">
                {{ coll.name }}
              </option>
            </select>
          </div>

          <div class="mb-3">
            <label for="rootFolder" class="form-label">Root Folder</label>
            <select class="form-select" id="rootFolder" formControlName="rootFolder">
              <option value="">-- Select Root Folder --</option>
              <option *ngFor="let folder of data.rootFolders" [value]="folder.id">
                {{ folder.name }} ({{ folder.path }})
              </option>
            </select>
          </div>

          <div class="mb-3">
            <div class="custom-toggle">
              <input type="checkbox" id="physicallyMoveFiles" formControlName="physicallyMoveFiles" class="toggle-input">
              <label for="physicallyMoveFiles" class="toggle-label">
                <span class="toggle-slider"></span>
                <span class="toggle-text">Physically move files</span>
              </label>
            </div>
          </div>

          <div class="mb-3">
            <div class="custom-toggle">
              <input type="checkbox" id="clearCustomPath" formControlName="clearCustomPath" class="toggle-input">
              <label for="clearCustomPath" class="toggle-label">
                <span class="toggle-slider"></span>
                <span class="toggle-text">Clear custom path after move</span>
              </label>
            </div>
          </div>

          <!-- Dry Run Preview Box -->
          <div class="dry-run-preview">
            <h6 class="preview-title">
              <mat-icon class="preview-icon">preview</mat-icon>
              Dry Run Preview
            </h6>
            <div class="preview-content">
              @if (isDryRunning) {
                <div class="preview-loading">
                  <mat-progress-spinner diameter="24"></mat-progress-spinner>
                  <span class="loading-text">Analyzing move operation...</span>
                </div>
              }
              
              @if (dryRunResults.length > 0 && !isDryRunning) {
                <div class="preview-results">
                  <div *ngFor="let result of dryRunResults; let i = index" class="result-item">
                    <div class="result-header">
                      <mat-icon class="result-icon">{{ getResultIcon(result.action) }}</mat-icon>
                      <span class="result-action">{{ result.action }}</span>
                    </div>
                    <div class="result-details">{{ result.details }}</div>
                  </div>
                </div>
              }
              
              @if (!isDryRunning && dryRunResults.length === 0) {
                <div class="preview-placeholder">
                  <mat-icon class="placeholder-icon">info_outline</mat-icon>
                  <span>Click "Dry Run" to preview what will happen</span>
                </div>
              }
            </div>
          </div>

          <!-- Loading State -->
          <div *ngIf="isMoving" class="text-center py-3">
            <mat-spinner diameter="40"></mat-spinner>
            <p class="mt-2 text-muted">Moving book...</p>
          </div>
        </form>
      </div>
      
      <div class="modal-footer">
        <button type="button" class="btn btn-primary" (click)="onDryRun()" [disabled]="isDryRunning || isMoving">Dry Run</button>
        <button type="button" class="btn btn-success" (click)="onMove()" [disabled]="!moveForm.valid || isDryRunning || isMoving">
          <span *ngIf="!isMoving">Move Book</span>
          <span *ngIf="isMoving">
            <mat-spinner diameter="16"></mat-spinner> Moving...
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

    /* Bootstrap form styles */
    .bootstrap-form {
      margin: 0;
    }

    .mb-3 {
      margin-bottom: 0.75rem !important;
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

    .btn-success {
      color: #fff;
      background-color: #198754;
      border-color: #198754;
    }

    .btn-success:hover {
      color: #fff;
      background-color: #157347;
      border-color: #146c43;
    }

    .btn-success:focus {
      color: #fff;
      background-color: #198754;
      border-color: #198754;
      box-shadow: 0 0 0 0.25rem rgba(25, 135, 84, 0.25);
    }

    .btn:disabled {
      opacity: 0.65;
      cursor: not-allowed;
    }

    .alert {
      position: relative;
      padding: 0.75rem 1.25rem;
      margin-bottom: 1rem;
      border: 1px solid transparent;
      border-radius: 0.375rem;
    }

    .alert-info {
      color: #084298;
      background-color: #cff4fc;
      border-color: #b6effb;
    }

    .text-muted {
      color: #6c757d !important;
    }

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

    /* Dry run results */
    .dry-run-results {
      max-height: 200px;
      overflow-y: auto;
    }

    /* Custom Toggle Switches */
    .custom-toggle {
      display: flex;
      align-items: center;
      margin-bottom: 0.5rem;
    }

    .toggle-input {
      display: none;
    }

    .toggle-label {
      display: flex;
      align-items: center;
      cursor: pointer;
      font-size: 0.875rem;
      color: #212529;
      user-select: none;
    }

    .toggle-slider {
      position: relative;
      display: inline-block;
      width: 36px;
      height: 18px;
      margin-right: 8px;
      background-color: #ccc;
      border-radius: 9px;
      transition: background-color 0.2s ease;
    }

    .toggle-slider::before {
      content: "";
      position: absolute;
      top: 1px;
      left: 1px;
      width: 16px;
      height: 16px;
      background-color: white;
      border-radius: 50%;
      transition: transform 0.2s ease;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }

    .toggle-input:checked + .toggle-label .toggle-slider {
      background-color: #0d6efd;
    }

    .toggle-input:checked + .toggle-label .toggle-slider::before {
      transform: translateX(18px);
    }

    .toggle-text {
      font-weight: 400;
    }

    /* Dry Run Preview Box - Much More Subtle */
    .dry-run-preview {
      margin-top: 0.75rem;
      padding: 0.5rem;
      border: 1px solid #f0f0f0;
      border-radius: 0.25rem;
      background-color: #fafafa;
    }

    .preview-title {
      display: flex;
      align-items: center;
      gap: 4px;
      margin: 0 0 0.25rem 0;
      font-size: 0.75rem;
      font-weight: 400;
      color: #999;
      text-transform: none;
      letter-spacing: normal;
    }

    .preview-icon {
      color: #999;
      font-size: 12px;
    }

    .preview-content {
      min-height: 60px;
    }

    .preview-loading {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 0.5rem;
      color: #999;
      font-size: 0.75rem;
    }

    .loading-text {
      font-size: 0.75rem;
    }

    .preview-results {
      max-height: 120px;
      overflow-y: auto;
    }

    .result-item {
      background: #ffffff;
      border-left: 1px solid #ddd;
      padding: 0.4rem;
      margin-bottom: 0.2rem;
      border-radius: 0.2rem;
      box-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);
    }

    .result-header {
      display: flex;
      align-items: center;
      gap: 4px;
      margin-bottom: 0.2rem;
    }

    .result-icon {
      color: #666;
      font-size: 10px;
    }

    .result-action {
      font-weight: 400;
      color: #666;
      font-size: 0.75rem;
    }

    .result-details {
      color: #999;
      font-size: 0.7rem;
      line-height: 1.2;
    }

    .preview-placeholder {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      padding: 1rem;
      color: #999;
      font-size: 0.75rem;
    }

    .placeholder-icon {
      color: #ccc;
      font-size: 14px;
    }

    /* Responsive */
    @media (max-width: 1200px) {
      .bootstrap-dialog {
        width: 480px;
      }
    }

    @media (max-width: 992px) {
      .bootstrap-dialog {
        width: 450px;
      }
    }

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

    body.dark-theme .bootstrap-dialog .form-check-label,
    :host-context(body.dark-theme) .bootstrap-dialog .form-check-label {
      color: #ffffff;
    }

    body.dark-theme .bootstrap-dialog .text-muted,
    :host-context(body.dark-theme) .bootstrap-dialog .text-muted {
      color: #adb5bd !important;
    }

    body.dark-theme .bootstrap-dialog .alert-info,
    :host-context(body.dark-theme) .bootstrap-dialog .alert-info {
      color: #b7ecff;
      background-color: #051933;
      border-color: #0c3d66;
    }
  `]
})
export class MoveBookDialogMaterial {
  moveForm: FormGroup;
  isLoading = false;
  dryRunResults: any[] = [];
  isDryRunning = false;
  isMoving = false;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<MoveBookDialogMaterial>,
    @Inject(MAT_DIALOG_DATA) public data: MoveBookDialogData
  ) {
    this.moveForm = this.fb.group({
      collection: [''],
      rootFolder: [''],
      physicallyMoveFiles: [false],
      clearCustomPath: [false]
    });
  }

  getResultIcon(action: string): string {
    switch (action) {
      case 'Move Book': return 'folder_move';
      case 'Update Path': return 'update';
      case 'Update Metadata': return 'data_info';
      case 'Physical Move': return 'drive_file_move';
      case 'Clear Path': return 'clear';
      default: return 'info';
    }
  }

  onDryRun(): void {
    if (this.moveForm.valid) {
      this.isDryRunning = true;
      this.dryRunResults = [];
      
      // Simulate dry run process with steps
      setTimeout(() => {
        const formValues = this.moveForm.value;
        const results = [
          { action: 'Move Book', details: `"${this.data.book.title || this.data.book.name}" will be moved to selected collection` },
          { action: 'Update Path', details: 'File path will be updated to match new collection structure' },
          { action: 'Update Metadata', details: 'Collection ID will be updated in database' }
        ];

        if (formValues.physicallyMoveFiles) {
          results.push({ action: 'Physical Move', details: 'Files will be physically moved to new location' });
        }

        if (formValues.clearCustomPath) {
          results.push({ action: 'Clear Path', details: 'Custom path will be cleared after move' });
        }

        this.dryRunResults = results;
        this.isDryRunning = false;
      }, 1500);
    }
  }

  onMove(): void {
    if (this.moveForm.valid) {
      this.isMoving = true;
      
      // Simulate move operation
      setTimeout(() => {
        const result = {
          collection: this.moveForm.value.collection,
          rootFolder: this.moveForm.value.rootFolder,
          physicallyMoveFiles: this.moveForm.value.physicallyMoveFiles,
          clearCustomPath: this.moveForm.value.clearCustomPath
        };
        
        this.dialogRef.close(result);
        this.isMoving = false;
      }, 2000);
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}
