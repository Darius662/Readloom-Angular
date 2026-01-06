import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialog } from '@angular/material/dialog';
import { ErrorMessageComponent } from '../../components/error-message/error-message.component';
import { SeriesCardComponent } from '../../components/series-card/series-card.component';
import { SeriesService } from '../../services/series.service';
import { ApiService } from '../../services/api.service';
import { NotificationService } from '../../services/notification.service';
import { HttpClient } from '@angular/common/http';
import { Series } from '../../models/series.model';
import { SearchDetailsComponent } from '../../components/modals/search-details/search-details.component';

@Component({
    selector: 'app-manga',
    imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatSelectModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    ErrorMessageComponent,
    SeriesCardComponent
],
    templateUrl: './manga.component.html',
    styleUrls: ['./manga.component.css']
})
export class MangaComponent implements OnInit {
  title = 'Manga Library';
  error: string | null = null;
  isScanning = false;

  allManga: Series[] = [];
  filteredManga: Series[] = [];
  
  // Trending manga properties
  trendingManga: any[] = []; // Use any[] for trending manga with extra properties
  isLoadingTrending = false;

  sortBy = 'name';
  filterBy = '';

  constructor(
    private seriesService: SeriesService,
    private notificationService: NotificationService,
    private router: Router,
    private apiService: ApiService,
    private dialog: MatDialog,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.loadManga();
    this.loadTrendingManga();
  }

  private loadManga(): void {
    this.error = null;

    this.seriesService.getSeries({ content_type: 'manga' }).subscribe({
      next: (series) => {
        this.allManga = series;
        this.applyFilters();
      },
      error: (err) => {
        console.error('Error loading manga:', err);
        this.error = 'Failed to load manga';
        this.notificationService.error('Failed to load manga');
      }
    });
  }

  private applyFilters(): void {
    let filtered = [...this.allManga];

    if (this.filterBy) {
      filtered = filtered.filter(m => 
        m.name.toLowerCase().includes(this.filterBy.toLowerCase())
      );
    }

    this.filteredManga = filtered;
  }

  onFilterInput(event: any): void {
    this.filterBy = event.target.value;
    this.applyFilters();
  }

  onSortChange(value: string): void {
    this.sortBy = value;
    if (this.sortBy === 'name') {
      this.filteredManga.sort((a, b) => a.name.localeCompare(b.name));
    } else if (this.sortBy === 'rating') {
      this.filteredManga.sort((a, b) => (b.rating || 0) - (a.rating || 0));
    }
  }

  get resultCount(): number {
    return this.filteredManga.length;
  }

  onViewSeries(manga: Series): void {
    // Check if this is a library manga (has id) or a trending manga (might not have id)
    if (manga.id && manga.id > 0) {
      // This is a library manga - navigate to the manga detail page
      this.router.navigate(['/manga/series', manga.id]);
    } else {
      // This is a trending manga from AniList - use the same logic as search
      this.openSearchDetailsModal(manga);
    }
  }

  private loadTrendingManga(): void {
    this.isLoadingTrending = true;
    
    this.apiService.get<any>('/books/manga/trending-this-week').subscribe({
      next: (response) => {
        this.isLoadingTrending = false;
        
        if (response && response.success && response.data) {
          this.trendingManga = response.data;
          console.log('Trending manga loaded:', this.trendingManga);
        } else {
          console.log('No trending manga found');
          this.trendingManga = [];
        }
      },
      error: (err) => {
        this.isLoadingTrending = false;
        console.error('Error loading trending manga:', err);
        this.trendingManga = [];
      }
    });
  }

  openSearchDetailsModal(manga: any): void {
    // For trending manga, we have the AniList metadata_id, so we can fetch detailed info
    const anilistId = manga.metadata_id || manga.anilist_id;
    const title = manga.name || manga.title;
    
    console.log('=== Trending Manga Debug ===');
    console.log('Opening modal for manga:', title);
    console.log('AniList ID:', anilistId);

    if (!anilistId) {
      // If we don't have AniList ID, open with basic data
      this.openModalWithBasicData(manga);
      return;
    }

    // Create the result object in the format expected by SearchDetailsComponent
    const result = {
      id: anilistId,
      title: title,
      name: title,
      author: manga.author || 'Unknown',
      publisher: manga.publisher || 'Unknown',
      published_date: manga.published_date || 'Unknown',
      isbn: manga.isbn || 'Unknown',
      subjects: manga.subjects || ['Manga', 'Japanese'],
      genres: manga.subjects || ['Manga', 'Japanese'],
      description: manga.description || 'No description available',
      cover_url: manga.cover_url || '/assets/no-cover.png',
      provider: 'AniList',
      content_type: 'manga',
      alternative_titles: manga.alternative_titles || []
    };

    // Debug the final result
    console.log('=== Final Manga Result Being Sent to Modal ===');
    console.log('Title:', result.title);
    console.log('Author:', result.author);
    console.log('Publisher:', result.publisher);
    console.log('Subjects:', result.subjects);
    console.log('Description:', result.description);
    console.log('Cover URL:', result.cover_url);
    console.log('Full result object:', result);

    // Open the modal with the complete details
    this.dialog.open(SearchDetailsComponent, {
      width: '1000px',
      maxWidth: '1000px',
      data: {
        result: result,
        contentType: 'manga'
      },
      panelClass: 'search-details-dialog'
    });
  }

  openModalWithBasicData(manga: any): void {
    console.log('Opening modal with basic data:', manga);
    
    // Convert to the format expected by SearchDetailsComponent
    const result = {
      id: manga.metadata_id || manga.anilist_id,
      title: manga.name || manga.title,
      name: manga.name || manga.title,
      author: manga.author || 'Unknown',
      publisher: manga.publisher || 'Unknown',
      published_date: manga.published_date || 'Unknown',
      isbn: manga.isbn || 'Unknown',
      subjects: manga.subjects || ['Manga'],
      genres: manga.subjects || ['Manga'],
      description: manga.description || 'No description available',
      cover_url: manga.cover_url || '/assets/no-cover.png',
      provider: manga.metadata_source || 'AniList',
      content_type: 'manga',
      alternative_titles: manga.alternative_titles || []
    };

    // Open the modal with basic data
    this.dialog.open(SearchDetailsComponent, {
      width: '1000px',
      maxWidth: '1000px',
      data: {
        result: result,
        contentType: 'manga'
      },
      panelClass: 'search-details-dialog'
    });
  }

  scanForManga(): void {
    if (this.isScanning) return;
    
    this.isScanning = true;
    this.notificationService.info('Starting scan for manga...');
    
    console.log('Manga scan: Sending request with content_type: manga');
    
    this.seriesService.scanForEbooks(undefined, 'manga').subscribe({
      next: (result) => {
        this.isScanning = false;
        console.log('Manga scan result:', result);
        
        if (result.success) {
          const message = `Scan completed! Found ${result.scanned || 0} files, added ${result.added || 0} new manga.`;
          this.notificationService.success(message);
          
          // Reload the manga list to show any new additions
          this.loadManga();
        } else {
          const errorMsg = result.error || 'Scan failed';
          this.notificationService.error(errorMsg);
        }
      },
      error: (err) => {
        this.isScanning = false;
        console.error('Error scanning for manga:', err);
        this.notificationService.error('Failed to scan for manga. Please try again.');
      }
    });
  }
}
