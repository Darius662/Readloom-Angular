import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { CalendarEvent } from '../../../models/calendar.model';
import { MatDividerModule } from '@angular/material/divider';

@Component({
    selector: 'app-upcoming-releases-section',
    imports: [CommonModule, MatCardModule, MatChipsModule, MatIconModule,MatDividerModule],
    templateUrl: './upcoming-releases-section.component.html',
    styleUrls: ['./upcoming-releases-section.component.css']
})
export class UpcomingReleasesSectionComponent {
  @Input() releases: CalendarEvent[] = [];

  getEventColor(event: CalendarEvent): string {
    if (!event.is_confirmed) return 'warning';
    return event.type === 'chapter' ? 'primary' : 'secondary';
  }
}
