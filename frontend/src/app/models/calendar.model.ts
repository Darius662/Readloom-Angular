export interface CalendarEvent {
  id: number;
  seriesId: number;
  seriesTitle: string;
  contentType: 'MANGA' | 'COMIC' | 'BOOK' | 'MANWA';
  type: 'chapter' | 'volume';
  number: number;
  title?: string;
  releaseDate: string;
  is_confirmed?: boolean;
  cover_url?: string;
}

export interface CalendarFilter {
  type?: 'manga' | 'manwa' | 'comic' | 'book';
  series_id?: number;
  confirmed_only?: boolean;
  start_date?: string;
  end_date?: string;
}
