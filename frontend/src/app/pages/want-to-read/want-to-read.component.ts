import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog } from '@angular/material/dialog';
import { LoadingSpinnerComponent } from '../../components/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../components/error-message/error-message.component';
import { WantToReadDetailsModule } from '../../components/modals/want-to-read-details/want-to-read-details.module';
import { SeriesService } from '../../services/series.service';
import { NotificationService } from '../../services/notification.service';
import { Series } from '../../models/series.model';

// Import the component from the module
import { WantToReadDetailsComponent } from '../../components/modals/want-to-read-details/want-to-read-details.component';

@Component({
    selector: 'app-want-to-read',
    imports: [
      CommonModule,
      FormsModule,
      MatCardModule,
      MatButtonModule,
      MatIconModule,
      MatFormFieldModule,
      MatSelectModule,
      MatInputModule,
      MatChipsModule,
      LoadingSpinnerComponent,
      ErrorMessageComponent,
      WantToReadDetailsModule
    ],
    templateUrl: './want-to-read.component.html',
    styleUrls: ['./want-to-read.component.css']
})
export class WantToReadComponent implements OnInit {
  title = 'Want to Read';
  isLoading = true;
  error: string | null = null;
  allSeries: Series[] = [];
  filteredSeries: Series[] = [];
  
  // Statistics
  totalCount = 0;
  mangaCount = 0;
  bookCount = 0;
  
  // Filters and Sorting
  filterType = '';
  sortBy = 'added';
  searchTerm = '';

  constructor(
    private seriesService: SeriesService,
    private notificationService: NotificationService,
    private dialog: MatDialog,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.loadWantToRead();
  }

  private loadWantToRead(): void {
    this.isLoading = true;
    this.error = null;

    this.seriesService.getWantToReadItems().subscribe({
      next: (items) => {
        this.allSeries = items;
        this.calculateStatistics();
        this.applyFiltersAndSort();
        this.isLoading = false;
      },
      error: (err) => {
        this.error = 'Failed to load want to read list';
        this.notificationService.error('Failed to load want to read list');
        this.isLoading = false;
      }
    });
  }

  private calculateStatistics(): void {
    this.totalCount = this.allSeries.length;
    this.mangaCount = this.allSeries.filter(item => 
      ['MANGA', 'MANHWA', 'MANHUA', 'COMIC'].includes((item.content_type || '').toUpperCase())
    ).length;
    this.bookCount = this.allSeries.filter(item => 
      ['BOOK', 'NOVEL'].includes((item.content_type || '').toUpperCase())
    ).length;
  }

  applyFiltersAndSort(): void {
    let filtered = [...this.allSeries];

    // Apply type filter
    if (this.filterType) {
      filtered = filtered.filter(item => 
        (item.content_type || '').toUpperCase() === this.filterType.toUpperCase()
      );
    }

    // Apply search
    if (this.searchTerm) {
      const searchLower = this.searchTerm.toLowerCase();
      filtered = filtered.filter(item => 
        (item.name || '').toLowerCase().includes(searchLower) ||
        (item.title || '').toLowerCase().includes(searchLower) ||
        (item.author || '').toLowerCase().includes(searchLower)
      );
    }

    // Apply sort
    switch(this.sortBy) {
      case 'title':
        filtered.sort((a, b) => (a.name || a.title || '').localeCompare(b.name || b.title || ''));
        break;
      case 'title-desc':
        filtered.sort((a, b) => (b.name || b.title || '').localeCompare(a.name || a.title || ''));
        break;
      case 'author':
        filtered.sort((a, b) => (a.author || '').localeCompare(b.author || ''));
        break;
      case 'added':
      default:
        // Keep original order (recently added)
        break;
    }

    this.filteredSeries = filtered;
  }

  refreshItems(): void {
    this.loadWantToRead();
  }

  viewDetails(item: Series): void {
    console.log('viewDetails called for item:', item.name || item.title);
    
    // Get the provider and metadata ID for API calls
    const provider = item.metadata_source || item.provider || 'unknown';
    const metadataId = item.metadata_id || item.id?.toString();
    
    if (!metadataId) {
      this.notificationService.error('Cannot open details: Missing item information');
      return;
    }
    
    // Call the backend to get detailed item information including library status
    this.http.get(`http://localhost:7227/api/want-to-read/${metadataId}/details`).subscribe({
      next: (response: any) => {
        console.log('API response:', response);
        if (response.success && response.item) {
          // Open modal with real data from backend
          console.log('Opening modal with real data:', response.item);
          this.dialog.open(WantToReadDetailsComponent, {
            width: '1000px',
            maxWidth: '1000px',
            data: {
              item: response.item,
              inLibrary: response.in_library || false,
              seriesId: response.series_id
            },
            panelClass: 'want-to-read-details-dialog'
          }).afterClosed().subscribe(result => {
            console.log('Modal closed with result:', result);
            if (result === 'removed') {
              // Item was removed from want to read, refresh the list
              this.refreshItems();
            } else if (result === 'added') {
              // Item was added to collection, could refresh or show notification
              this.notificationService.success('Item added to collection');
            }
          });
        } else {
          this.notificationService.error('Failed to load item details');
        }
      },
      error: (err) => {
        console.error('Error fetching item details:', err);
        
        // If the endpoint doesn't exist, fall back to mock data with proper status checking
        console.log('Backend endpoint not available, using fallback logic');
        this.openModalWithFallback(item);
      }
    });
  }

  private openModalWithFallback(item: Series): void {
    // For items already in want-to-read, we can infer some status
    // but we should still try to determine library status
    const mockItem = {
      ...item,
      alternative_titles: item.alternative_titles || ['Alternative Title 1', 'Alternative Title 2'],
      genres: item.genres || ['Action', 'Adventure', 'Fantasy'],
      description: item.description || 'This is a detailed description of the item. It contains information about the plot, characters, and setting that would normally be fetched from the backend API.',
      rating: item.rating || 4.5,
      status: item.status || 'Ongoing'
    };
    
    // Try to determine if item is in library by checking existing series
    this.seriesService.getSeries().subscribe({
      next: (allSeries) => {
        const existingSeries = allSeries.find(s => s.name === item.name || s.title === item.title);
        const isInLibrary = !!existingSeries;
        
        console.log('Fallback - found existing series:', existingSeries);
        console.log('Fallback - isInLibrary:', isInLibrary);
        
        const mockResponse = {
          success: true,
          item: mockItem,
          in_library: isInLibrary,
          series_id: existingSeries?.id || item.id
        };
        
        this.dialog.open(WantToReadDetailsComponent, {
          width: '1000px',
          maxWidth: '1000px',
          data: {
            item: mockResponse.item,
            inLibrary: mockResponse.in_library || false,
            seriesId: mockResponse.series_id
          },
          panelClass: 'want-to-read-details-dialog'
        }).afterClosed().subscribe(result => {
          console.log('Modal closed with result:', result);
          if (result === 'removed') {
            this.refreshItems();
          } else if (result === 'added') {
            this.notificationService.success('Item added to collection');
          }
        });
      },
      error: (err) => {
        console.error('Error checking library status:', err);
        // Final fallback - assume not in library
        this.dialog.open(WantToReadDetailsComponent, {
          width: '1000px',
          maxWidth: '1000px',
          data: {
            item: mockItem,
            inLibrary: false,
            seriesId: item.id
          },
          panelClass: 'want-to-read-details-dialog'
        });
      }
    });
  }
}
