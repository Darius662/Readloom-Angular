import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

// Import dialog components (to be created)
// import { AddSubscriptionDialogComponent } from './dialogs/add-subscription-dialog.component';
// import { TestNotificationDialogComponent } from './dialogs/test-notification-dialog.component';

@Component({
    selector: 'app-notifications',
    imports: [
        CommonModule,
        FormsModule,
        MatCardModule,
        MatButtonModule,
        MatSlideToggleModule,
        MatSelectModule,
        MatFormFieldModule,
        MatInputModule,
        MatIconModule,
        MatCheckboxModule,
        MatProgressSpinnerModule,
        MatChipsModule,
        MatTooltipModule,
        MatDialogModule,
        MatSnackBarModule
    ],
    templateUrl: './notifications.component.html',
    styleUrls: ['./notifications.component.css']
})
export class NotificationsComponent implements OnInit {
    // Loading states
    isLoadingNotifications = false;
    isLoadingReleases = false;
    isLoadingSubscriptions = false;

    // Data arrays
    notifications: Notification[] = [];
    upcomingReleases: Release[] = [];
    subscriptions: Subscription[] = [];

    // Notification settings interface
    notificationSettings: NotificationSettings = {
        notifyNewVolumes: true,
        notifyNewChapters: true,
        notifyDaysBefore: '1',
        browserEnabled: false,
        emailEnabled: false,
        emailAddress: '',
        discordEnabled: false,
        discordWebhook: '',
        telegramEnabled: false,
        telegramBotToken: '',
        telegramChatId: ''
    };

    constructor(
        private dialog: MatDialog,
        private snackBar: MatSnackBar
    ) {}

    ngOnInit(): void {
        this.loadAllData();
    }

    // Load all data
    private loadAllData(): void {
        this.loadNotifications();
        this.loadUpcomingReleases();
        this.loadSubscriptions();
        this.loadNotificationSettings();
    }

    // Notifications methods
    loadNotifications(): void {
        this.isLoadingNotifications = true;
        // TODO: Implement API call
        setTimeout(() => {
            this.notifications = [
                {
                    id: 1,
                    title: 'New Volume Released',
                    message: 'One Piece Volume 105 has been released!',
                    type: 'INFO',
                    read: false,
                    created_at: new Date().toISOString()
                },
                {
                    id: 2,
                    title: 'Chapter Available',
                    message: 'Berserk Chapter 371 is now available',
                    type: 'SUCCESS',
                    read: true,
                    created_at: new Date(Date.now() - 86400000).toISOString()
                }
            ];
            this.isLoadingNotifications = false;
        }, 1000);
    }

    markAsRead(id: number): void {
        const notification = this.notifications.find(n => n.id === id);
        if (notification) {
            notification.read = true;
            // TODO: API call to mark as read
            this.snackBar.open('Notification marked as read', 'Close', { duration: 3000 });
        }
    }

    markAllRead(): void {
        this.notifications.forEach(n => n.read = true);
        // TODO: API call to mark all as read
        this.snackBar.open('All notifications marked as read', 'Close', { duration: 3000 });
    }

    deleteNotification(id: number): void {
        this.notifications = this.notifications.filter(n => n.id !== id);
        // TODO: API call to delete notification
        this.snackBar.open('Notification deleted', 'Close', { duration: 3000 });
    }

    clearAll(): void {
        this.notifications = [];
        // TODO: API call to clear all notifications
        this.snackBar.open('All notifications cleared', 'Close', { duration: 3000 });
    }

    // Upcoming releases methods
    loadUpcomingReleases(): void {
        this.isLoadingReleases = true;
        // TODO: Implement API call
        setTimeout(() => {
            this.upcomingReleases = [
                {
                    id: 1,
                    title: 'One Piece Vol. 105',
                    description: 'New volume release',
                    type: 'VOLUME_RELEASE',
                    date: new Date(Date.now() + 86400000).toISOString().split('T')[0],
                    series: {
                        id: 1,
                        title: 'One Piece',
                        cover_url: '/assets/images/covers/one-piece.jpg'
                    }
                },
                {
                    id: 2,
                    title: 'Berserk Chapter 371',
                    description: 'New chapter release',
                    type: 'CHAPTER_RELEASE',
                    date: new Date(Date.now() + 172800000).toISOString().split('T')[0],
                    series: {
                        id: 2,
                        title: 'Berserk',
                        cover_url: '/assets/images/covers/berserk.jpg'
                    }
                }
            ];
            this.isLoadingReleases = false;
        }, 1500);
    }

    checkReleases(): void {
        this.loadUpcomingReleases();
        this.snackBar.open('Checking for new releases...', 'Close', { duration: 3000 });
    }

    get groupedReleases() {
        const grouped: { [key: string]: Release[] } = {};
        this.upcomingReleases.forEach(release => {
            if (!grouped[release.date]) {
                grouped[release.date] = [];
            }
            grouped[release.date].push(release);
        });
        return Object.keys(grouped).map(date => ({
            date,
            releases: grouped[date]
        }));
    }

    // Subscriptions methods
    loadSubscriptions(): void {
        this.isLoadingSubscriptions = true;
        // TODO: Implement API call
        setTimeout(() => {
            this.subscriptions = [
                {
                    id: 1,
                    series_id: 1,
                    series_title: 'One Piece',
                    series_author: 'Eiichiro Oda',
                    series_cover_url: '/assets/images/covers/one-piece.jpg',
                    notify_new_volumes: true,
                    notify_new_chapters: true
                },
                {
                    id: 2,
                    series_id: 2,
                    series_title: 'Berserk',
                    series_author: 'Kentaro Miura',
                    series_cover_url: '/assets/images/covers/berserk.jpg',
                    notify_new_volumes: true,
                    notify_new_chapters: false
                }
            ];
            this.isLoadingSubscriptions = false;
        }, 800);
    }

    openAddSubscriptionDialog(): void {
        // TODO: Implement add subscription dialog
        this.snackBar.open('Add subscription dialog coming soon', 'Close', { duration: 3000 });
    }

    unsubscribe(seriesId: number): void {
        this.subscriptions = this.subscriptions.filter(s => s.series_id !== seriesId);
        // TODO: API call to unsubscribe
        this.snackBar.open('Unsubscribed successfully', 'Close', { duration: 3000 });
    }

    // Settings methods
    loadNotificationSettings(): void {
        // TODO: Load settings from API
        // For now using default values
    }

    saveNotificationSettings(): void {
        // TODO: Save settings to API
        this.snackBar.open('Notification settings saved', 'Close', { duration: 3000 });
    }

    // Utility methods
    formatDate(dateString: string): string {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffHours < 1) {
            return 'Just now';
        } else if (diffHours < 24) {
            return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        } else if (diffDays < 7) {
            return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    processImageUrl(url: string): string {
        // TODO: Implement proper image URL processing
        return url || '/assets/images/default-cover.jpg';
    }
}

// Interfaces
interface Notification {
    id: number;
    title: string;
    message: string;
    type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR';
    read: boolean;
    created_at: string;
}

interface Release {
    id: number;
    title: string;
    description: string;
    type: 'VOLUME_RELEASE' | 'CHAPTER_RELEASE';
    date: string;
    series: {
        id: number;
        title: string;
        cover_url: string;
    };
}

interface Subscription {
    id: number;
    series_id: number;
    series_title: string;
    series_author: string;
    series_cover_url: string;
    notify_new_volumes: boolean;
    notify_new_chapters: boolean;
}

interface NotificationSettings {
    notifyNewVolumes: boolean;
    notifyNewChapters: boolean;
    notifyDaysBefore: string;
    browserEnabled: boolean;
    emailEnabled: boolean;
    emailAddress: string;
    discordEnabled: boolean;
    discordWebhook: string;
    telegramEnabled: boolean;
    telegramBotToken: string;
    telegramChatId: string;
}
