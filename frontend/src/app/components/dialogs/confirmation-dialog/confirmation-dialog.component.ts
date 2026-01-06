import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-confirmation-dialog',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule, MatDialogModule],
  template: `
    <div class="confirmation-dialog">
      <div class="dialog-header" [ngClass]="'type-' + data.type">
        <mat-icon class="dialog-icon">
          {{ getIcon() }}
        </mat-icon>
        <h2 mat-dialog-title class="dialog-title">{{ data.title }}</h2>
      </div>

      <mat-dialog-content class="dialog-content">
        <p class="dialog-message">{{ data.message }}</p>
      </mat-dialog-content>

      <mat-dialog-actions align="end" class="dialog-actions">
        <button mat-stroked-button (click)="onCancel()" class="cancel-button">
          {{ data.cancelText }}
        </button>
        <button 
          mat-raised-button 
          [color]="getButtonColor()"
          (click)="onConfirm()"
          class="confirm-button">
          {{ data.confirmText }}
        </button>
      </mat-dialog-actions>
    </div>
  `,
  styles: [`
    .confirmation-dialog {
      min-width: 480px;
      max-width: 600px;
      width: 100%;
    }

    .dialog-header {
      display: flex;
      align-items: flex-start;
      gap: 18px;
      padding: 25px;
      border-radius: 4px 4px 0 0;
      margin: -24px -24px 0 -24px;
    }

    .dialog-header.type-danger {
      background-color: #d32f2f;
      color: #ffffff;
    }

    .dialog-header.type-warning {
      background-color: #f57c00;
      color: #ffffff;
    }

    .dialog-header.type-info {
      background-color: #1976d2;
      color: #ffffff;
    }

    .dialog-icon {
      font-size: 36px;
      width: 36px;
      height: 36px;
      flex-shrink: 0;
      margin-top: 0;
    }

    .dialog-title {
      margin: 0;
      font-size: 22px;
      font-weight: 700;
      line-height: 1.3;
      color: #ffffff;
    }

    .dialog-content {
      padding: 28px !important;
      min-height: 90px;
      display: flex;
      align-items: center;
      background-color: #fafafa;
    }

    .dialog-message {
      margin: 0;
      color: #212121;
      line-height: 1.7;
      font-size: 16px;
      word-break: break-word;
    }

    .dialog-actions {
      padding: 20px 28px 28px 28px !important;
      margin: 0 !important;
      border-top: 1px solid #e0e0e0;
      gap: 12px;
      display: flex;
      justify-content: flex-end;
      background-color: #ffffff;
    }

    .cancel-button {
      min-width: 110px;
      font-size: 15px;
      font-weight: 600;
    }

    .confirm-button {
      min-width: 110px;
      font-size: 15px;
      font-weight: 600;
    }

    /* Ensure text is readable in all themes */
    :host ::ng-deep .mat-mdc-dialog-container {
      background-color: #ffffff;
    }

    :host ::ng-deep .mat-mdc-button-base {
      text-transform: none;
      font-weight: 600;
      letter-spacing: 0.5px;
    }

    :host ::ng-deep .mat-mdc-raised-button {
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    :host ::ng-deep .mat-mdc-stroked-button {
      border-width: 2px;
    }
  `]
})
export class ConfirmationDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<ConfirmationDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  onConfirm(): void {
    this.dialogRef.close(true);
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }

  getIcon(): string {
    switch (this.data.type) {
      case 'danger':
        return 'delete_outline';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'help_outline';
    }
  }

  getButtonColor(): string {
    switch (this.data.type) {
      case 'danger':
        return 'warn';
      case 'warning':
        return 'accent';
      default:
        return 'primary';
    }
  }
}
