import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface ToastNotification {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

@Injectable({
  providedIn: 'root'
})
export class ToastNotificationService {
  private notifications$ = new BehaviorSubject<ToastNotification[]>([]);
  private notificationIdCounter = 0;

  constructor() {}

  /**
   * Get notifications observable
   */
  getNotifications(): Observable<ToastNotification[]> {
    return this.notifications$.asObservable();
  }

  /**
   * Show success notification
   */
  success(message: string, duration: number = 5000): void {
    this.addNotification(message, 'success', duration);
  }

  /**
   * Show error notification
   */
  error(message: string, duration: number = 5000): void {
    this.addNotification(message, 'error', duration);
  }

  /**
   * Show warning notification
   */
  warning(message: string, duration: number = 5000): void {
    this.addNotification(message, 'warning', duration);
  }

  /**
   * Show info notification
   */
  info(message: string, duration: number = 5000): void {
    this.addNotification(message, 'info', duration);
  }

  /**
   * Add notification
   */
  private addNotification(message: string, type: 'success' | 'error' | 'warning' | 'info', duration: number): void {
    const id = `toast-notification-${this.notificationIdCounter++}`;
    const notification: ToastNotification = { id, message, type, duration };

    const currentNotifications = this.notifications$.value;
    this.notifications$.next([...currentNotifications, notification]);

    if (duration > 0) {
      setTimeout(() => this.removeNotification(id), duration);
    }
  }

  /**
   * Remove notification
   */
  removeNotification(id: string): void {
    const currentNotifications = this.notifications$.value;
    this.notifications$.next(currentNotifications.filter(n => n.id !== id));
  }

  /**
   * Clear all notifications
   */
  clearAll(): void {
    this.notifications$.next([]);
  }
}
