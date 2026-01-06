import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { NotificationService } from '../../../services/notification.service';
import { ConfirmationService } from '../../../services/confirmation.service';

@Component({
  selector: 'app-notification-manager',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    FormsModule
  ],
  template: `
    <div class="notification-manager-container">
      <h1>Notification System Demo</h1>
      <p class="subtitle">Test the custom in-app notification and confirmation system</p>

      <div class="demo-grid">
        <!-- Toast Notifications Section -->
        <mat-card class="demo-card">
          <mat-card-header>
            <mat-card-title>Toast Notifications</mat-card-title>
            <mat-card-subtitle>Display temporary notifications</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <div class="button-group">
              <button mat-raised-button color="primary" (click)="showSuccess()">
                <mat-icon>check_circle</mat-icon>
                Success Notification
              </button>
              <button mat-raised-button color="warn" (click)="showError()">
                <mat-icon>error</mat-icon>
                Error Notification
              </button>
              <button mat-raised-button color="accent" (click)="showWarning()">
                <mat-icon>warning</mat-icon>
                Warning Notification
              </button>
              <button mat-raised-button (click)="showInfo()">
                <mat-icon>info</mat-icon>
                Info Notification
              </button>
            </div>

            <div class="custom-message-section">
              <mat-form-field class="full-width">
                <mat-label>Custom Message</mat-label>
                <input matInput [(ngModel)]="customMessage" placeholder="Enter custom message">
              </mat-form-field>
              <div class="custom-buttons">
                <button mat-stroked-button (click)="showCustomSuccess()">
                  Custom Success
                </button>
                <button mat-stroked-button (click)="showCustomError()">
                  Custom Error
                </button>
              </div>
            </div>

            <div class="duration-section">
              <mat-form-field>
                <mat-label>Duration (ms)</mat-label>
                <input matInput type="number" [(ngModel)]="customDuration" placeholder="5000">
              </mat-form-field>
              <button mat-stroked-button (click)="showWithCustomDuration()">
                Show with Custom Duration
              </button>
            </div>
          </mat-card-content>
        </mat-card>

        <!-- Confirmation Dialogs Section -->
        <mat-card class="demo-card">
          <mat-card-header>
            <mat-card-title>Confirmation Dialogs</mat-card-title>
            <mat-card-subtitle>Confirm important actions</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <div class="button-group">
              <button mat-raised-button color="warn" (click)="showDeleteConfirmation()">
                <mat-icon>delete</mat-icon>
                Delete Confirmation
              </button>
              <button mat-raised-button color="accent" (click)="showWarningConfirmation()">
                <mat-icon>warning</mat-icon>
                Warning Confirmation
              </button>
              <button mat-raised-button (click)="showInfoConfirmation()">
                <mat-icon>info</mat-icon>
                Info Confirmation
              </button>
            </div>

            <div class="custom-confirmation-section">
              <mat-form-field class="full-width">
                <mat-label>Confirmation Title</mat-label>
                <input matInput [(ngModel)]="confirmTitle" placeholder="Enter title">
              </mat-form-field>
              <mat-form-field class="full-width">
                <mat-label>Confirmation Message</mat-label>
                <input matInput [(ngModel)]="confirmMessage" placeholder="Enter message">
              </mat-form-field>
              <button mat-stroked-button (click)="showCustomConfirmation()">
                Show Custom Confirmation
              </button>
            </div>
          </mat-card-content>
        </mat-card>

        <!-- Combined Demo Section -->
        <mat-card class="demo-card">
          <mat-card-header>
            <mat-card-title>Combined Demo</mat-card-title>
            <mat-card-subtitle>Confirmation + Notification workflow</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <div class="button-group">
              <button mat-raised-button color="warn" (click)="simulateDelete()">
                <mat-icon>delete</mat-icon>
                Simulate Delete Action
              </button>
              <button mat-raised-button color="primary" (click)="simulateCreate()">
                <mat-icon>add</mat-icon>
                Simulate Create Action
              </button>
              <button mat-raised-button color="accent" (click)="simulateUpdate()">
                <mat-icon>edit</mat-icon>
                Simulate Update Action
              </button>
            </div>

            <div class="info-box">
              <p><strong>Last Action:</strong> {{ lastAction }}</p>
              <p><strong>Result:</strong> {{ lastResult }}</p>
            </div>
          </mat-card-content>
        </mat-card>

        <!-- Notification Types Reference -->
        <mat-card class="demo-card reference-card">
          <mat-card-header>
            <mat-card-title>Notification Types</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="type-reference">
              <div class="type-item success">
                <strong>Success</strong>
                <p>Use for successful operations (create, update, delete)</p>
              </div>
              <div class="type-item error">
                <strong>Error</strong>
                <p>Use for failed operations and errors</p>
              </div>
              <div class="type-item warning">
                <strong>Warning</strong>
                <p>Use for warnings and cautions</p>
              </div>
              <div class="type-item info">
                <strong>Info</strong>
                <p>Use for informational messages</p>
              </div>
            </div>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .notification-manager-container {
      padding: 24px;
      max-width: 1200px;
      margin: 0 auto;
    }

    h1 {
      font-size: 28px;
      font-weight: 600;
      margin-bottom: 8px;
      color: #212121;
    }

    .subtitle {
      font-size: 14px;
      color: #666;
      margin-bottom: 32px;
    }

    .demo-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
      gap: 24px;
    }

    .demo-card {
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    mat-card-header {
      margin-bottom: 16px;
    }

    mat-card-title {
      font-size: 18px;
      font-weight: 600;
    }

    mat-card-subtitle {
      font-size: 13px;
      color: #999;
    }

    .button-group {
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 24px;
    }

    button {
      justify-content: flex-start;
      gap: 8px;
    }

    .custom-message-section,
    .custom-confirmation-section,
    .duration-section {
      padding-top: 16px;
      border-top: 1px solid #e0e0e0;
      margin-top: 16px;
    }

    .full-width {
      width: 100%;
      margin-bottom: 12px;
    }

    .custom-buttons {
      display: flex;
      gap: 8px;
    }

    .custom-buttons button {
      flex: 1;
    }

    .duration-section {
      display: flex;
      gap: 12px;
      align-items: flex-end;
    }

    .duration-section mat-form-field {
      flex: 1;
    }

    .duration-section button {
      flex: 1;
    }

    .info-box {
      background-color: #f5f5f5;
      padding: 16px;
      border-radius: 4px;
      margin-top: 16px;
      border-left: 4px solid #2196f3;
    }

    .info-box p {
      margin: 8px 0;
      font-size: 14px;
    }

    .info-box strong {
      color: #212121;
    }

    .reference-card {
      grid-column: 1 / -1;
    }

    .type-reference {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
    }

    .type-item {
      padding: 16px;
      border-radius: 4px;
      border-left: 4px solid;
    }

    .type-item strong {
      display: block;
      margin-bottom: 8px;
      font-size: 15px;
    }

    .type-item p {
      margin: 0;
      font-size: 13px;
      color: #666;
      line-height: 1.4;
    }

    .type-item.success {
      background-color: #f1f8e9;
      border-left-color: #4caf50;
      color: #2e7d32;
    }

    .type-item.error {
      background-color: #ffebee;
      border-left-color: #f44336;
      color: #c62828;
    }

    .type-item.warning {
      background-color: #fff3e0;
      border-left-color: #ff9800;
      color: #e65100;
    }

    .type-item.info {
      background-color: #e3f2fd;
      border-left-color: #2196f3;
      color: #1565c0;
    }

    mat-form-field {
      width: 100%;
    }
  `]
})
export class NotificationManagerComponent {
  customMessage = 'Operation completed successfully!';
  customDuration = 5000;
  confirmTitle = 'Confirm Action';
  confirmMessage = 'Are you sure you want to proceed?';
  lastAction = 'None';
  lastResult = 'Waiting for action...';

  constructor(
    private notificationService: NotificationService,
    private confirmationService: ConfirmationService
  ) {}

  // Toast Notification Methods
  showSuccess(): void {
    this.notificationService.success('Operation completed successfully!');
  }

  showError(): void {
    this.notificationService.error('An error occurred. Please try again.');
  }

  showWarning(): void {
    this.notificationService.warning('Please review this action carefully.');
  }

  showInfo(): void {
    this.notificationService.info('Here is some useful information for you.');
  }

  showCustomSuccess(): void {
    this.notificationService.success(this.customMessage);
  }

  showCustomError(): void {
    this.notificationService.error(this.customMessage);
  }

  showWithCustomDuration(): void {
    this.notificationService.success(this.customMessage, this.customDuration);
  }

  // Confirmation Dialog Methods
  showDeleteConfirmation(): void {
    this.confirmationService.confirmDelete('Test Item').subscribe(confirmed => {
      if (confirmed) {
        this.notificationService.success('Item deleted successfully');
        this.lastAction = 'Delete Confirmation';
        this.lastResult = 'Confirmed - Item deleted';
      } else {
        this.notificationService.info('Delete action cancelled');
        this.lastAction = 'Delete Confirmation';
        this.lastResult = 'Cancelled';
      }
    });
  }

  showWarningConfirmation(): void {
    this.confirmationService.confirmWarning(
      'Important Action',
      'This action may have consequences. Do you want to continue?'
    ).subscribe(confirmed => {
      if (confirmed) {
        this.notificationService.success('Action completed');
        this.lastAction = 'Warning Confirmation';
        this.lastResult = 'Confirmed - Action completed';
      } else {
        this.notificationService.info('Action cancelled');
        this.lastAction = 'Warning Confirmation';
        this.lastResult = 'Cancelled';
      }
    });
  }

  showInfoConfirmation(): void {
    this.confirmationService.confirmInfo(
      'Information',
      'This is an informational confirmation dialog.'
    ).subscribe(confirmed => {
      if (confirmed) {
        this.notificationService.success('Acknowledged');
        this.lastAction = 'Info Confirmation';
        this.lastResult = 'Acknowledged';
      } else {
        this.lastAction = 'Info Confirmation';
        this.lastResult = 'Dismissed';
      }
    });
  }

  showCustomConfirmation(): void {
    this.confirmationService.confirm({
      title: this.confirmTitle,
      message: this.confirmMessage,
      confirmText: 'Confirm',
      cancelText: 'Cancel',
      type: 'warning'
    }).subscribe(confirmed => {
      if (confirmed) {
        this.notificationService.success('Custom confirmation accepted');
        this.lastAction = 'Custom Confirmation';
        this.lastResult = 'Confirmed';
      } else {
        this.notificationService.info('Custom confirmation cancelled');
        this.lastAction = 'Custom Confirmation';
        this.lastResult = 'Cancelled';
      }
    });
  }

  // Combined Demo Methods
  simulateDelete(): void {
    this.lastAction = 'Simulating Delete...';
    this.lastResult = 'Waiting for confirmation...';

    this.confirmationService.confirmDelete('Sample Item').subscribe(confirmed => {
      if (confirmed) {
        this.notificationService.success('Item deleted successfully');
        this.lastAction = 'Delete Simulation';
        this.lastResult = 'Success - Item was deleted';
      } else {
        this.notificationService.info('Delete cancelled');
        this.lastAction = 'Delete Simulation';
        this.lastResult = 'Cancelled by user';
      }
    });
  }

  simulateCreate(): void {
    this.lastAction = 'Creating Item...';
    this.lastResult = 'Processing...';

    // Simulate API call delay
    setTimeout(() => {
      this.notificationService.success('New item created successfully');
      this.lastAction = 'Create Simulation';
      this.lastResult = 'Success - Item was created';
    }, 500);
  }

  simulateUpdate(): void {
    this.lastAction = 'Updating Item...';
    this.lastResult = 'Processing...';

    // Simulate API call delay
    setTimeout(() => {
      this.notificationService.success('Item updated successfully');
      this.lastAction = 'Update Simulation';
      this.lastResult = 'Success - Item was updated';
    }, 500);
  }
}
