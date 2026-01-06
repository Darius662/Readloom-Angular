import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { trigger, transition, style, animate } from '@angular/animations';
import { ToastNotificationService, ToastNotification } from '../../../services/toast-notification.service';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-toast-notification',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatButtonModule],
  template: `
    <div class="toast-container">
      <div 
        *ngFor="let notification of notifications"
        [@slideIn]
        [ngClass]="'toast-' + notification.type"
        class="toast-notification">
        <div class="toast-content">
          <mat-icon class="toast-icon">{{ getIcon(notification.type) }}</mat-icon>
          <span class="toast-message">{{ notification.message }}</span>
        </div>
        <button 
          mat-icon-button 
          (click)="closeNotification(notification.id)"
          class="toast-close">
          <mat-icon>close</mat-icon>
        </button>
      </div>
    </div>
  `,
  styles: [`
    .toast-container {
      position: fixed;
      top: 80px;
      right: 20px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 16px;
      max-width: 420px;
      pointer-events: none;
    }

    .toast-notification {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 18px;
      border-radius: 6px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
      animation: slideIn 0.3s ease-out;
      min-height: 52px;
      pointer-events: auto;
      max-width: 420px;
    }

    .toast-content {
      display: flex;
      align-items: center;
      gap: 12px;
      flex: 1;
    }

    .toast-icon {
      flex-shrink: 0;
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    .toast-message {
      font-size: 14px;
      line-height: 1.4;
      word-break: break-word;
    }

    .toast-close {
      flex-shrink: 0;
      margin-left: 12px;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      border-radius: 4px;
      transition: background-color 0.2s;
    }

    .toast-close:hover {
      background-color: rgba(255, 255, 255, 0.2);
    }

    /* Success */
    .toast-success {
      background-color: #4caf50;
      color: white;
    }

    .toast-success .toast-close {
      color: rgba(255, 255, 255, 0.8);
    }

    .toast-success .toast-close:hover {
      background-color: rgba(255, 255, 255, 0.25);
    }

    /* Error */
    .toast-error {
      background-color: #f44336;
      color: white;
    }

    .toast-error .toast-close {
      color: rgba(255, 255, 255, 0.8);
    }

    .toast-error .toast-close:hover {
      background-color: rgba(255, 255, 255, 0.25);
    }

    /* Warning */
    .toast-warning {
      background-color: #ff9800;
      color: white;
    }

    .toast-warning .toast-close {
      color: rgba(255, 255, 255, 0.8);
    }

    .toast-warning .toast-close:hover {
      background-color: rgba(255, 255, 255, 0.25);
    }

    /* Info */
    .toast-info {
      background-color: #2196f3;
      color: white;
    }

    .toast-info .toast-close {
      color: rgba(255, 255, 255, 0.8);
    }

    .toast-info .toast-close:hover {
      background-color: rgba(255, 255, 255, 0.25);
    }

    @keyframes slideIn {
      from {
        transform: translateX(450px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
  `],
  animations: [
    trigger('slideIn', [
      transition(':enter', [
        style({ transform: 'translateX(400px)', opacity: 0 }),
        animate('300ms ease-out', style({ transform: 'translateX(0)', opacity: 1 }))
      ]),
      transition(':leave', [
        animate('300ms ease-in', style({ transform: 'translateX(400px)', opacity: 0 }))
      ])
    ])
  ]
})
export class ToastNotificationComponent implements OnInit, OnDestroy {
  notifications: ToastNotification[] = [];
  private destroy$ = new Subject<void>();

  constructor(private toastNotificationService: ToastNotificationService) {}

  ngOnInit(): void {
    this.toastNotificationService.getNotifications()
      .pipe(takeUntil(this.destroy$))
      .subscribe(notifications => {
        this.notifications = notifications;
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  closeNotification(id: string): void {
    this.toastNotificationService.removeNotification(id);
  }

  getIcon(type: string): string {
    switch (type) {
      case 'success':
        return 'check_circle';
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'notifications';
    }
  }
}
