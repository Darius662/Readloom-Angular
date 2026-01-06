import { Component, OnInit } from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { LoadingSpinnerComponent } from '../../components/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../components/error-message/error-message.component';
import { ReleasesTableSectionComponent } from '../../components/calendar/releases-table-section/releases-table-section.component';
import { CalendarGridSectionComponent } from '../../components/calendar/calendar-grid-section/calendar-grid-section.component';
import { CalendarService } from '../../services/calendar.service';
import { NotificationService } from '../../services/notification.service';
import { CalendarEvent } from '../../models/calendar.model';

@Component({
    selector: 'app-calendar',
    imports: [MatCardModule, MatProgressSpinnerModule, LoadingSpinnerComponent, ErrorMessageComponent, ReleasesTableSectionComponent, CalendarGridSectionComponent],
    templateUrl: './calendar.component.html',
    styleUrls: ['./calendar.component.css']
})
export class CalendarComponent implements OnInit {
  title = 'Calendar';
  isLoading = true;
  error: string | null = null;
  events: CalendarEvent[] = [];
  currentDate = new Date();

  constructor(
    private calendarService: CalendarService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadEvents();
  }

  private loadEvents(): void {
    this.isLoading = true;
    this.error = null;

    // Get upcoming releases only (from today to 3 months in the future)
    const today = new Date();
    const startDate = today.toISOString().split('T')[0]; // Start from today
    const endDate = new Date(today.getFullYear(), today.getMonth() + 3, 0).toISOString().split('T')[0]; // 3 months from now

    this.calendarService.getEventsByDateRange(startDate, endDate).subscribe({
      next: (events) => {
        // Filter out past releases (only keep today and future)
        const todayStr = startDate;
        this.events = events
          .filter(event => event.releaseDate >= todayStr)
          .sort((a, b) => 
            new Date(a.releaseDate).getTime() - new Date(b.releaseDate).getTime()
          );
        this.isLoading = false;
        
        console.log(`Loaded ${this.events.length} upcoming releases from ${startDate} to ${endDate}`);
      },
      error: (err) => {
        console.error('Calendar API error:', err);
        this.error = 'Failed to load calendar events';
        this.notificationService.error('Failed to load calendar events');
        this.isLoading = false;
      }
    });
  }

  getEventColor(event: CalendarEvent): string {
    if (!event.is_confirmed) return 'warning';
    return event.type === 'chapter' ? 'primary' : 'secondary';
  }

  getEventLabel(event: CalendarEvent): string {
    return event.type === 'chapter' ? `Ch. ${event.number}` : `Vol. ${event.number}`;
  }

  getEventDate(event: CalendarEvent): string {
    return new Date(event.releaseDate).toLocaleDateString();
  }

  getContentTypeIcon(contentType: string): string {
    switch (contentType) {
      case 'MANGA': return 'book';
      case 'COMIC': return 'menu_book';
      case 'BOOK': return 'auto_stories';
      case 'MANWA': return 'import_contacts';
      default: return 'book';
    }
  }
}
