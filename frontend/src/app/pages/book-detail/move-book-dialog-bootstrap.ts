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
import { Series } from '../../models/series.model';

export interface MoveBookDialogData {
  book: Series;
  collections: any[];
  rootFolders: any[];
}

@Component({
  selector: 'app-move-book-dialog-bootstrap',
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
    MatProgressSpinnerModule
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
            <div class="form-check">
              <input class="form-check-input" type="checkbox" id="dryRun" formControlName="dryRun">
              <label class="form-check-label" for="dryRun">
                Dry run (preview changes without executing)
              </label>
            </div>
          </div>

          <!-- Dry Run Results -->
          <div *ngIf="dryRunResults.length > 0" class="mb-3">
            <h6 class="text-muted">Dry Run Results:</h6>
            <div class="dry-run-results">
              <div *ngFor="let result of dryRunResults" class="alert alert-info">
                <strong>{{ result.action }}:</strong> {{ result.details }}
              </div>
            </div>
          </div>

          <!-- Loading State -->
          <div *ngIf="isLoading" class="text-center py-3">
            <mat-spinner diameter="40"></mat-spinner>
            <p class="mt-2 text-muted">Processing move operation...</p>
          </div>
        </form>
      </div>
      
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" (click)="onCancel()">Cancel</button>
        <button type="button" class="btn btn-primary" (click)="onDryRun()" [disabled]="isLoading">Dry Run</button>
        <button type="button" class="btn btn-success" (click)="onMove()" [disabled]="!moveForm.valid || isLoading">
          <span *ngIf="!isLoading">Move Book</span>
          <span *ngIf="isLoading">
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
export class MoveBookDialogBootstrap {
  moveForm: FormGroup;
  isLoading = false;
  dryRunResults: any[] = [];

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<MoveBookDialogBootstrap>,
    @Inject(MAT_DIALOG_DATA) public data: MoveBookDialogData
  ) {
    this.moveForm = this.fb.group({
      collection: [''],
      rootFolder: [''],
      dryRun: [false]
    });
  }

  onDryRun(): void {
    if (this.moveForm.valid) {
      this.isLoading = true;
      this.dryRunResults = [];
      
      // Simulate dry run results
      setTimeout(() => {
        this.dryRunResults = [
          { action: 'Move Book', details: `"${this.data.book.title || this.data.book.name}" will be moved to selected collection` },
          { action: 'Update Path', details: 'File path will be updated to match new collection structure' },
          { action: 'Update Metadata', details: 'Collection ID will be updated in database' }
        ];
        this.isLoading = false;
      }, 1000);
    }
  }

  onMove(): void {
    if (this.moveForm.valid) {
      this.isLoading = true;
      
      // Simulate move operation
      setTimeout(() => {
        const result = {
          collection: this.moveForm.value.collection,
          rootFolder: this.moveForm.value.rootFolder,
          dryRun: this.moveForm.value.dryRun
        };
        
        this.dialogRef.close(result);
        this.isLoading = false;
      }, 2000);
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}
