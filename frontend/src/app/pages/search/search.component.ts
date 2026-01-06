import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { MatDialog } from '@angular/material/dialog';
import { ModalService } from '../../services/modal.service';
import { ApiService } from '../../services/api.service';
import { NotificationService } from '../../services/notification.service';
import { SeriesService } from '../../services/series.service';
import { Series } from '../../models/series.model';
import { SearchDetailsComponent } from '../../components/modals/search-details/search-details.component';

// Angular Material imports
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';

@Component({
  selector: 'app-search',
  imports: [
    CommonModule, 
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatChipsModule
  ],
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css'],
  providers: []
})
export class SearchComponent implements OnInit {
  contentType: 'book' | 'manga' = 'book';
  searchQuery = '';
  selectedProvider = '';
  providers: any[] = [];
  searchResults: any[] = [];
  hasSearched = false;
  isLoading = false;
  noResults = false;

  constructor(
    private http: HttpClient,
    private dialog: MatDialog,
    private modalService: ModalService,
    private apiService: ApiService,
    private notificationService: NotificationService,
    private seriesService: SeriesService
  ) { }

  ngOnInit(): void {
    this.loadProviders();
  }

  setContentType(type: 'book' | 'manga'): void {
    this.contentType = type;
    this.onContentTypeChange();
  }

  getSearchPlaceholder(): string {
    return this.contentType === 'book' ? 'Enter book title...' : 'Enter manga title...';
  }

  onContentTypeChange(): void {
    this.searchQuery = '';
    this.searchResults = [];
    this.hasSearched = false;
    this.noResults = false;
    this.selectedProvider = '';
    this.filterProvidersForContentType();
  }

  loadProviders(): void {
    this.http.get<any>('http://localhost:7227/api/metadata/providers').subscribe({
      next: (response) => {
        if (response.providers && Array.isArray(response.providers)) {
          this.filterProvidersForContentType();
        }
      },
      error: (err) => {
        console.error('Error loading providers:', err);
      }
    });
  }

  filterProvidersForContentType(): void {
    const bookProviders = ['GoogleBooks', 'OpenLibrary', 'ISBNdb', 'WorldCat'];
    const mangaProviders = ['MangaDex', 'AniList', 'MyAnimeList', 'MangaFire', 'MangaAPI', 'Jikan'];

    this.http.get<any>('http://localhost:7227/api/metadata/providers').subscribe({
      next: (response) => {
        if (response.providers && Array.isArray(response.providers)) {
          const filtered = response.providers.filter((p: any) => {
            if (this.contentType === 'book') {
              return bookProviders.includes(p.name) && p.enabled;
            } else {
              return mangaProviders.includes(p.name) && p.enabled;
            }
          });
          this.providers = filtered;
        }
      }
    });
  }

  onSearch(): void {
    if (!this.searchQuery.trim()) {
      this.notificationService.warning('Please enter a search term');
      return;
    }

    this.hasSearched = true;
    this.isLoading = true;
    this.noResults = false;
    this.searchResults = [];

    const contentTypeParam = this.contentType === 'book' ? 'BOOK' : 'MANGA';
    let url = `http://localhost:7227/api/metadata/search?query=${encodeURIComponent(this.searchQuery)}&search_type=title&content_type=${contentTypeParam}`;
    
    if (this.selectedProvider) {
      url += `&provider=${this.selectedProvider}`;
    }

    this.http.get<any>(url).subscribe({
      next: (response) => {
        this.isLoading = false;
        
        if (response.results) {
          let totalResults = 0;
          Object.keys(response.results).forEach(providerName => {
            const providerResults = response.results[providerName];
            if (providerResults && Array.isArray(providerResults)) {
              totalResults += providerResults.length;
              providerResults.forEach((result: any) => {
                result.provider = providerName;
                this.searchResults.push(result);
              });
            }
          });

          if (totalResults === 0) {
            this.noResults = true;
          }
        } else {
          this.noResults = true;
        }
      },
      error: (err) => {
        this.isLoading = false;
        this.noResults = true;
        console.error('Search error:', err);
        this.notificationService.error('Search failed. Please try again.');
      }
    });
  }

  viewDetails(result: any): void {
    // Debug logging for search result
    console.log('=== Search Result Debug ===');
    console.log('Provider:', result.provider);
    console.log('ID:', result.id);
    console.log('Title:', result.title);
    console.log('Full search result:', result);
    
    // For books, fetch full details before opening modal
    if (this.contentType === 'book' && result.provider && result.id) {
      this.isLoading = true;
      
      // Fetch full book details from the backend
      const url = `http://localhost:7227/api/metadata/details/${result.provider}/${result.id}`;
      
      console.log('Fetching details from:', url);
      
      this.http.get<any>(url).subscribe({
        next: (response) => {
          this.isLoading = false;
          
          console.log('Details API response:', response); // Debug log
          
          if (response && response.success && response.details) {
            // Merge the search result with detailed information
            const detailedResult = { ...result, ...response.details };
            
            console.log('Merged result:', detailedResult); // Debug log
            
            // Open the modal with the complete details
            this.dialog.open(SearchDetailsComponent, {
              width: '1000px',
              maxWidth: '1000px',
              data: {
                result: detailedResult,
                contentType: this.contentType
              },
              panelClass: 'search-details-dialog'
            });
          } else {
            console.log('Using original result - details fetch failed'); // Debug log
            // If details fetch fails, open with original result
            this.dialog.open(SearchDetailsComponent, {
              width: '1000px',
              maxWidth: '1000px',
              data: {
                result: result,
                contentType: this.contentType
              },
              panelClass: 'search-details-dialog'
            });
          }
        },
        error: (err) => {
          this.isLoading = false;
          console.error('Error fetching book details:', err);
          
          // If details fetch fails, open with original result
          this.dialog.open(SearchDetailsComponent, {
            width: '1000px',
            maxWidth: '1000px',
            data: {
              result: result,
              contentType: this.contentType
            },
            panelClass: 'search-details-dialog'
          });
        }
      });
    } else {
      // For manga or if provider/id missing, open with original result
      this.dialog.open(SearchDetailsComponent, {
        width: '1000px',
        maxWidth: '1000px',
        data: {
          result: result,
          contentType: this.contentType
        },
        panelClass: 'search-details-dialog'
      });
    }
  }

  getCoverUrl(coverUrl: string): string {
    if (!coverUrl) return '/assets/no-cover.png';
    return coverUrl;
  }
}
