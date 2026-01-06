import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, forkJoin } from 'rxjs';
import { map, catchError, switchMap } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { Series, Volume, Chapter } from '../models/series.model';
import { SeriesService } from './series.service';
import { NotificationService } from './notification.service';

export interface MangaDexCover {
  id: string;
  attributes: {
    fileName: string;
    description?: string;
    volume?: string;
    locale: string;
    version: number;
    createdAt: string;
    updatedAt: string;
  };
  relationships: {
    type: string;
    id: string;
  }[];
}

export interface MangaDexManga {
  id: string;
  type: string;
  attributes: {
    title: { [locale: string]: string };
    description?: { [locale: string]: string };
    altTitles: { [locale: string]: string }[];
    status: string;
    contentRating: string;
    tags: { id: string; type: string; attributes: { name: { [locale: string]: string } } }[];
    year?: number;
    availableTranslatedLanguages: string[];
    latestUploadedChapter?: string;
  };
  relationships: {
    type: string;
    id: string;
    attributes?: any;
  }[];
}

export interface MangaDexChapter {
  id: string;
  type: string;
  attributes: {
    title?: string;
    volume?: string;
    chapter?: string;
    translatedLanguage: string;
    publishAt: string;
    readableAt: string;
    createdAt: string;
    updatedAt: string;
    pages: number;
    version: number;
  };
  relationships: {
    type: string;
    id: string;
  }[];
}

export interface MangaDexResponse<T> {
  result: string;
  response: string;
  data: T[];
  limit: number;
  offset: number;
  total: number;
}

@Injectable({
  providedIn: 'root'
})
export class MangaPrepopulationService {
  private readonly MANGADEX_PROXY_API = environment.apiUrl;
  private readonly MANGADEX_COVER_BASE = `${environment.apiUrl}/mangadex/cover`;

  constructor(
    private http: HttpClient,
    private seriesService: SeriesService,
    private notificationService: NotificationService
  ) {}

  /**
   * Prepopulate volumes and chapters for a series using MangaDex
   */
  prepopulateSeriesData(series: Series): Observable<{ volumes: Volume[], chapters: Chapter[] }> {
    console.log(`Starting prepopulation for series:`, {
      seriesId: series.id,
      seriesName: series.title || series.name,
      seriesType: series.type
    });
    
    return this.searchMangaDex(series.title || '').pipe(
      switchMap(mangaDexData => {
        if (!mangaDexData) {
          this.notificationService.warning(`Could not find ${series.title} on MangaDex`);
          return of({ volumes: [], chapters: [] });
        }

        return forkJoin({
          volumesData: this.getVolumesFromMangaDex(series.id, mangaDexData),
          chapters: this.getChaptersFromMangaDex(series.id, mangaDexData)
        }).pipe(
          map(result => ({
            volumes: result.volumesData.volumes,
            chapters: result.chapters
          }))
        );
      }),
      catchError(error => {
        console.error('Error prepopulating series data:', error);
        this.notificationService.error('Failed to prepopulate series data');
        return of({ volumes: [], chapters: [] });
      })
    );
  }

  /**
   * Search for manga on MangaDex
   */
  private searchMangaDex(title: string): Observable<MangaDexManga | null> {
    const searchUrl = `${this.MANGADEX_PROXY_API}/mangadex/search`;
    const params = {
      title: title,
      limit: '5',
      'includes[]': ['cover_art', 'author', 'artist']
    };

    return this.http.get<MangaDexResponse<MangaDexManga>>(searchUrl, { params }).pipe(
      map(response => {
        if (response.data.length === 0) return null;
        
        // Find best match by title similarity
        const bestMatch = this.findBestTitleMatch(title, response.data);
        return bestMatch || response.data[0];
      }),
      catchError(error => {
        console.error('Error searching MangaDex:', error);
        return of(null);
      })
    );
  }

  /**
   * Get volumes from MangaDex data
   */
  private getVolumesFromMangaDex(seriesId: number, mangaDexData: MangaDexManga): Observable<{ volumes: Volume[], coverData: any }> {
    const covers = mangaDexData.relationships.filter(rel => rel.type === 'cover_art');
    const volumes: Volume[] = [];
    const coverData: any = {};

    // Extract volume information from covers
    covers.forEach(cover => {
      const coverDataItem = cover as any; // Type assertion for cover data
      if (coverDataItem.attributes) {
        const volumeNumber = coverDataItem.attributes.volume ? 
          parseInt(coverDataItem.attributes.volume) : 1;
        
        // Store cover filename for download
        coverData[volumeNumber] = coverDataItem.attributes.fileName;
        
        const volume: Volume = {
          id: 0, // Will be set by backend
          series_id: seriesId,
          volume_number: volumeNumber,
          title: `Volume ${volumeNumber}`,
          is_confirmed: false,
          cover_url: this.buildCoverUrl(mangaDexData.id, coverDataItem.attributes.fileName)
        };

        volumes.push(volume);
      }
    });

    // If no covers found, create basic volumes based on common manga structure
    if (volumes.length === 0) {
      const estimatedVolumes = this.estimateVolumeCount(mangaDexData);
      for (let i = 1; i <= estimatedVolumes; i++) {
        volumes.push({
          id: 0,
          series_id: seriesId,
          volume_number: i,
          title: `Volume ${i}`,
          is_confirmed: false
        });
      }
    }

    return of({ volumes, coverData });
  }

  /**
   * Get chapters from MangaDex data
   */
  private getChaptersFromMangaDex(seriesId: number, mangaDexData: MangaDexManga): Observable<Chapter[]> {
    const chaptersUrl = `${this.MANGADEX_PROXY_API}/mangadex/chapters/${mangaDexData.id}`;
    const params = {
      limit: '500', // Get all chapters
      'translatedLanguage[]': ['en'] // English chapters
    };

    return this.http.get<MangaDexResponse<MangaDexChapter>>(chaptersUrl, { params }).pipe(
      map(response => {
        return response.data.map(chapter => {
          const chapterNumber = chapter.attributes.chapter ? 
            parseFloat(chapter.attributes.chapter) : 0;
          
          return {
            id: 0, // Will be set by backend
            series_id: seriesId,
            chapter_number: chapterNumber,
            title: chapter.attributes.title || `Chapter ${chapterNumber}`,
            release_date: chapter.attributes.publishAt || chapter.attributes.createdAt,
            is_confirmed: false
          };
        }).sort((a, b) => a.chapter_number - b.chapter_number);
      }),
      catchError(error => {
        console.error('Error fetching chapters from MangaDex:', error);
        return of([]);
      })
    );
  }

  /**
   * Build cover URL for MangaDex
   */
  private buildCoverUrl(mangaId: string, fileName: string): string {
    return `${this.MANGADEX_COVER_BASE}/${mangaId}/${fileName}`;
  }

  /**
   * Find best title match from search results
   */
  private findBestTitleMatch(searchTitle: string, results: MangaDexManga[]): MangaDexManga | null {
    const searchLower = searchTitle.toLowerCase();
    
    let bestMatch: MangaDexManga | null = null;
    let bestScore = 0;

    results.forEach(manga => {
      const title = manga.attributes.title['en'] || Object.values(manga.attributes.title)[0] || '';
      const titleLower = title.toLowerCase();
      
      // Simple similarity scoring
      let score = 0;
      if (titleLower === searchLower) score = 100;
      else if (titleLower.includes(searchLower) || searchLower.includes(titleLower)) score = 80;
      else if (titleLower.split(' ').some(word => searchLower.includes(word))) score = 60;
      else score = this.calculateLevenshteinSimilarity(searchLower, titleLower) * 100;

      if (score > bestScore) {
        bestScore = score;
        bestMatch = manga;
      }
    });

    return bestScore > 50 ? bestMatch : null;
  }

  /**
   * Calculate simple string similarity (Levenshtein distance approximation)
   */
  private calculateLevenshteinSimilarity(str1: string, str2: string): number {
    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;
    
    if (longer.length === 0) return 1.0;
    
    const editDistance = this.levenshteinDistance(longer, shorter);
    return (longer.length - editDistance) / longer.length;
  }

  /**
   * Calculate Levenshtein distance
   */
  private levenshteinDistance(str1: string, str2: string): number {
    const matrix = Array(str2.length + 1).fill(null).map(() => Array(str1.length + 1).fill(null));
    
    for (let i = 0; i <= str1.length; i++) matrix[0][i] = i;
    for (let j = 0; j <= str2.length; j++) matrix[j][0] = j;
    
    for (let j = 1; j <= str2.length; j++) {
      for (let i = 1; i <= str1.length; i++) {
        const indicator = str1[i - 1] === str2[j - 1] ? 0 : 1;
        matrix[j][i] = Math.min(
          matrix[j][i - 1] + 1,
          matrix[j - 1][i] + 1,
          matrix[j - 1][i - 1] + indicator
        );
      }
    }
    
    return matrix[str2.length][str1.length];
  }

  /**
   * Estimate volume count based on manga status and other factors
   */
  private estimateVolumeCount(mangaDexData: MangaDexManga): number {
    // Basic estimation - could be enhanced with AI providers
    const status = mangaDexData.attributes.status;
    
    if (status === 'completed') return 12; // Completed series often have 10-15 volumes
    if (status === 'ongoing') return 8;   // Ongoing series typically have fewer volumes
    return 5; // Default estimate
  }

  /**
   * Save prepopulated data to backend with cover download
   */
  savePrepopulatedData(seriesId: number, volumes: Volume[], chapters: Chapter[], mangaDexId?: string, coverData?: any): Observable<any> {
    const payload = {
      series_id: seriesId,
      volumes: volumes.map(v => ({
        volume_number: v.volume_number,
        title: v.title,
        release_date: v.release_date,
        cover_url: v.cover_url,
        is_confirmed: v.is_confirmed || false
      })),
      chapters: chapters.map(c => ({
        chapter_number: c.chapter_number,
        title: c.title,
        release_date: c.release_date,
        is_confirmed: c.is_confirmed || false
      })),
      manga_dex_id: mangaDexId,
      cover_data: coverData
    };

    return this.http.post(`${environment.apiUrl}/manga-prepopulation/batch`, payload).pipe(
      map(response => {
        this.notificationService.success('Volumes and chapters saved successfully!');
        return response;
      }),
      catchError(error => {
        console.error('Error saving prepopulated data:', error);
        this.notificationService.error('Failed to save volumes and chapters');
        return of({ success: false, error: error.message });
      })
    );
  }

  /**
   * Trigger manual prepopulation for a series
   */
  triggerPrepopulation(series: Series): Observable<{ volumes: Volume[], chapters: Chapter[] }> {
    this.notificationService.info('Fetching data from MangaDex...');
    
    return this.searchMangaDex(series.title || '').pipe(
      switchMap(mangaDexData => {
        if (!mangaDexData) {
          this.notificationService.warning(`Could not find ${series.title} on MangaDex`);
          return of({ volumes: [], chapters: [] });
        }

        return forkJoin({
          volumesData: this.getVolumesFromMangaDex(series.id, mangaDexData),
          chapters: this.getChaptersFromMangaDex(series.id, mangaDexData)
        }).pipe(
          switchMap(result => {
            if (result.volumesData.volumes.length > 0 || result.chapters.length > 0) {
              // Auto-save the fetched data with cover information
              return this.savePrepopulatedData(
                series.id, 
                result.volumesData.volumes, 
                result.chapters,
                mangaDexData.id,
                result.volumesData.coverData
              ).pipe(
                map(() => ({
                  volumes: result.volumesData.volumes,
                  chapters: result.chapters
                }))
              );
            }
            return of({ volumes: [], chapters: [] });
          })
        );
      }),
      catchError(error => {
        console.error('Error prepopulating series data:', error);
        this.notificationService.error('Failed to prepopulate series data');
        return of({ volumes: [], chapters: [] });
      })
    );
  }
}
