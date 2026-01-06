import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { CalendarEvent } from '../../../models/calendar.model';

@Component({
    selector: 'app-releases-table-section',
    imports: [CommonModule, MatCardModule, MatTableModule, MatChipsModule, MatIconModule],
    templateUrl: './releases-table-section.component.html',
    styleUrls: ['./releases-table-section.component.css']
})
export class ReleasesTableSectionComponent {
  @Input() releases: CalendarEvent[] = [];
  displayedColumns = ['date', 'series', 'release', 'type', 'status'];

  getEventColor(event: CalendarEvent): string {
    if (!event.is_confirmed) return 'warn';
    return event.type === 'chapter' ? 'primary' : 'accent';
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
