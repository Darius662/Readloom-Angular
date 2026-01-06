import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject, of } from 'rxjs';
import { tap, delay, map } from 'rxjs/operators';
import { ApiService } from './api.service';
import { MockDataService } from './mock-data.service';
import { CalendarEvent, CalendarFilter } from '../models/calendar.model';

@Injectable({
  providedIn: 'root'
})
export class CalendarService {
  private events$ = new BehaviorSubject<CalendarEvent[]>([]);
  private filters$ = new BehaviorSubject<CalendarFilter>({});

  constructor(private api: ApiService, private mockData: MockDataService) {}

  /**
   * Get calendar events
   */
  getEvents(params?: any): Observable<CalendarEvent[]> {
    return of(this.mockData.getMockCalendarEvents())
      .pipe(
        delay(300),
        tap(events => this.events$.next(events))
      );
  }

  /**
   * Get events for date range
   */
  getEventsByDateRange(startDate: string, endDate: string, params?: any): Observable<CalendarEvent[]> {
    return this.api.get<{ success: boolean; events: any[] }>('/calendar', { start_date: startDate, end_date: endDate, ...params })
      .pipe(
        map(response => {
          if (!response.success || !response.events) {
            return [];
          }
          
          // Transform backend response to CalendarEvent format
          return response.events.map(event => ({
            id: event.id,
            seriesId: event.seriesId,
            seriesTitle: event.seriesTitle,
            contentType: event.contentType,
            type: 'chapter' as const, // Backend only returns chapters for now
            number: event.chapterNumber,
            title: event.title,
            releaseDate: event.releaseDate,
            is_confirmed: true, // Backend doesn't provide this field, assume confirmed
            cover_url: undefined // Backend doesn't provide cover for chapters
          }));
        }),
        tap(events => this.events$.next(events))
      );
  }

  /**
   * Get events for series
   */
  getSeriesEvents(seriesId: number): Observable<CalendarEvent[]> {
    return this.api.get<CalendarEvent[]>(`/calendar/series/${seriesId}`);
  }

  /**
   * Create calendar event
   */
  createEvent(data: Partial<CalendarEvent>): Observable<CalendarEvent> {
    return this.api.post<CalendarEvent>('/calendar', data)
      .pipe(tap(event => {
        const current = this.events$.value;
        this.events$.next([...current, event]);
      }));
  }

  /**
   * Update calendar event
   */
  updateEvent(id: number, data: Partial<CalendarEvent>): Observable<CalendarEvent> {
    return this.api.put<CalendarEvent>(`/calendar/${id}`, data)
      .pipe(tap(event => {
        const current = this.events$.value;
        const index = current.findIndex(e => e.id === id);
        if (index > -1) {
          current[index] = event;
          this.events$.next([...current]);
        }
      }));
  }

  /**
   * Delete calendar event
   */
  deleteEvent(id: number): Observable<any> {
    return this.api.delete(`/calendar/${id}`)
      .pipe(tap(() => {
        const current = this.events$.value;
        this.events$.next(current.filter(e => e.id !== id));
      }));
  }

  /**
   * Get events observable
   */
  getEventsList(): Observable<CalendarEvent[]> {
    return this.events$.asObservable();
  }

  /**
   * Set filters
   */
  setFilters(filters: CalendarFilter): void {
    this.filters$.next(filters);
  }

  /**
   * Get filters observable
   */
  getFilters(): Observable<CalendarFilter> {
    return this.filters$.asObservable();
  }
}
