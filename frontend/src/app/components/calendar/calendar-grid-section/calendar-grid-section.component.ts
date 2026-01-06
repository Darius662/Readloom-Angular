import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { CalendarEvent } from '../../../models/calendar.model';

@Component({
    selector: 'app-calendar-grid-section',
    imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule, MatChipsModule],
    templateUrl: './calendar-grid-section.component.html',
    styleUrls: ['./calendar-grid-section.component.css']
})
export class CalendarGridSectionComponent implements OnInit {
  @Input() events: CalendarEvent[] = [];

  currentDate = new Date();
  daysInMonth: (number | null)[] = [];
  weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  monthName = '';

  ngOnInit(): void {
    this.generateCalendar();
  }

  ngOnChanges(): void {
    this.generateCalendar();
  }

  private generateCalendar(): void {
    const year = this.currentDate.getFullYear();
    const month = this.currentDate.getMonth();

    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'];
    this.monthName = `${monthNames[month]} ${year}`;

    const firstDay = new Date(year, month, 1).getDay();
    const daysCount = new Date(year, month + 1, 0).getDate();

    this.daysInMonth = [];
    
    // Add empty cells for days before month starts
    for (let i = 0; i < firstDay; i++) {
      this.daysInMonth.push(null);
    }

    // Add days of the month
    for (let i = 1; i <= daysCount; i++) {
      this.daysInMonth.push(i);
    }
  }

  getEventsForDay(day: number | null): CalendarEvent[] {
    if (!day) return [];

    const year = this.currentDate.getFullYear();
    const month = this.currentDate.getMonth();
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

    return this.events.filter(e => e.releaseDate === dateStr);
  }

  previousMonth(): void {
    this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() - 1);
    this.generateCalendar();
  }

  nextMonth(): void {
    this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1);
    this.generateCalendar();
  }

  getEventBadgeClass(event: CalendarEvent): string {
    if (!event.is_confirmed) return 'warning';
    return event.type === 'chapter' ? 'primary' : 'secondary';
  }

  getEventLabel(event: CalendarEvent): string {
    return event.type === 'chapter' ? `Ch. ${event.number}` : `Vol. ${event.number}`;
  }
}
