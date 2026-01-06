import { Injectable } from '@angular/core';
import { Observable, of, BehaviorSubject } from 'rxjs';
import { tap, delay, map } from 'rxjs/operators';
import { ApiService } from './api.service';
import { MockDataService } from './mock-data.service';
import { Series, Chapter, Volume, Release } from '../models/series.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SeriesService {
  private seriesList$ = new BehaviorSubject<Series[]>([]);
  private selectedSeries$ = new BehaviorSubject<Series | null>(null);

  constructor(private api: ApiService, private mockData: MockDataService) {}

  /**
   * Get all series
   */
  getSeries(params?: any): Observable<Series[]> {
    return this.api.get<{ series: Series[] }>('/series', params)
      .pipe(
        map(response => response.series || []),
        tap(series => this.seriesList$.next(series))
      );
  }

  /**
   * Get series by ID
   */
  getSeriesById(id: number): Observable<Series> {
    return this.api.get<{ series: Series }>(`/series/${id}`)
      .pipe(
        map(response => response.series),
        tap(series => this.selectedSeries$.next(series))
      );
  }

  /**
   * Create new series
   */
  createSeries(data: Partial<Series>): Observable<Series> {
    return this.api.post<Series>('/series', data)
      .pipe(tap(series => {
        const current = this.seriesList$.value;
        this.seriesList$.next([...current, series]);
      }));
  }

  /**
   * Update series
   */
  updateSeries(id: number, data: Partial<Series>): Observable<Series> {
    return this.api.put<Series>(`/series/${id}`, data)
      .pipe(tap(series => {
        const current = this.seriesList$.value;
        const index = current.findIndex(s => s.id === id);
        if (index > -1) {
          current[index] = series;
          this.seriesList$.next([...current]);
        }
        if (this.selectedSeries$.value?.id === id) {
          this.selectedSeries$.next(series);
        }
      }));
  }

  /**
   * Delete series
   */
  deleteSeries(id: number, removeEbookFiles: boolean = false): Observable<any> {
    const body = { remove_files: removeEbookFiles };
    
    return this.api.delete(`/series/${id}`, body)
      .pipe(tap(() => {
        const current = this.seriesList$.value;
        const updated = current.filter(series => series.id !== id);
        this.seriesList$.next(updated);
      }));
  }

  /**
   * Get series list observable
   */
  getSeriesList(): Observable<Series[]> {
    return this.seriesList$.asObservable();
  }

  /**
   * Get selected series observable
   */
  getSelectedSeries(): Observable<Series | null> {
    return this.selectedSeries$.asObservable();
  }

  /**
   * Get chapters for series
   */
  getChapters(seriesId: number): Observable<Chapter[]> {
    return this.api.get<Chapter[]>(`/series/${seriesId}/chapters`);
  }

  /**
   * Get volumes for series
   */
  getVolumes(seriesId: number): Observable<Volume[]> {
    return this.api.get<Volume[]>(`/series/${seriesId}/volumes`);
  }

  /**
   * Search series
   */
  searchSeries(query: string): Observable<Series[]> {
    return this.api.get<Series[]>('/series/search', { q: query });
  }

  /**
   * Get want-to-read items from cache
   */
  getWantToReadItems(): Observable<any[]> {
    return this.api.get<{ items: any[] }>('/collection/want-to-read')
      .pipe(
        map(response => response.items || [])
      );
  }

  /**
   * Add series to want-to-read cache
   */
  addToWantToRead(provider: string, metadataId: string, contentType: string = 'BOOK'): Observable<any> {
    return this.api.post(`/metadata/want-to-read/${provider}/${metadataId}`, {
      content_type: contentType
    });
  }

  /**
   * Remove series from want-to-read cache
   */
  removeFromWantToRead(provider: string, metadataId: string): Observable<any> {
    return this.api.delete(`/metadata/want-to-read/${provider}/${metadataId}`);
  }

  /**
   * Update volume cover
   */
  updateVolumeCover(volumeId: number, coverUrl: string): Observable<any> {
    return this.api.put(`/manga-prepopulation/volume/${volumeId}/cover`, {
      cover_url: coverUrl
    });
  }

  /**
   * Delete volume cover
   */
  deleteVolumeCover(volumeId: number): Observable<any> {
    return this.api.delete(`/manga-prepopulation/volume/${volumeId}/cover`);
  }

  /**
   * Scan for manual covers and link them to volumes
   */
  scanForCovers(): Observable<any> {
    return this.api.post('/cover-art/scan', {});
  }

  /**
   * Scan for e-books in the data directory
   */
  scanForEbooks(seriesId?: number, contentType?: string): Observable<any> {
    if (seriesId) {
      // Scan for specific series
      return this.api.post(`/series/${seriesId}/scan`, {});
    } else {
      // Global scan with optional content type filter
      const body = contentType ? { content_type: contentType } : {};
      return this.api.post('/series/scan', body);
    }
  }

  /**
   * Get volume cover URL (prioritizes local covers)
   */
  getVolumeCoverUrl(volume: Volume): string | null {
    // First try local cover path
    if (volume.cover_path) {
      return `${environment.apiUrl.replace('/api', '')}/api/cover-art/volume/${volume.id}`;
    }
    
    // Fallback to cover_url (MangaDex URL)
    if (volume.cover_url) {
      return volume.cover_url;
    }
    
    // No cover available
    return null;
  }
}
