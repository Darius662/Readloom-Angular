import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';

import { MaterialNotificationService, MaterialNotification } from '../../services/material-notification.service';

@Component({
    selector: 'app-notification',
    imports: [CommonModule, MatIconModule, MatButtonModule, MatCardModule],
    templateUrl: './notification.component.html',
    styleUrls: ['./notification.component.css']
})
export class NotificationComponent implements OnInit {
  notifications: MaterialNotification[] = [];

  constructor(private materialNotificationService: MaterialNotificationService) {}

  ngOnInit(): void {
    this.materialNotificationService.getNotifications().subscribe(notifications => {
      this.notifications = notifications;
    });
  }

  removeNotification(id: string): void {
    this.materialNotificationService.removeNotification(id);
  }

  getNotificationIcon(type: string): string {
    const icons: { [key: string]: string } = {
      success: 'check_circle',
      error: 'error',
      warning: 'warning',
      info: 'info'
    };
    return icons[type] || 'info';
  }
}
