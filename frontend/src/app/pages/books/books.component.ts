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
    selector: 'app-books',
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
    templateUrl: './books.component.html',
    styleUrls: ['./books.component.css']
})
export class BooksComponent implements OnInit {
  title = 'Books Library';
  error: string | null = null;
  isScanning = false;

  allBooks: Series[] = [];
  filteredBooks: Series[] = [];
  
  // Popular books properties
  popularBooks: Series[] = [];
  isLoadingPopular = false;

  sortBy = 'name';
  filterBy = '';

  constructor(
    private seriesService: SeriesService,
    private apiService: ApiService,
    private notificationService: NotificationService,
    private router: Router,
    private dialog: MatDialog,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.loadBooks();
    this.loadPopularBooks();
  }

  private loadBooks(): void {
    this.error = null;

    this.seriesService.getSeries({ content_type: 'book' }).subscribe({
      next: (series) => {
        this.allBooks = series;
        this.applyFilters();
      },
      error: (err) => {
        console.error('Error loading books:', err);
        this.error = 'Failed to load books';
        this.notificationService.error('Failed to load books');
      }
    });
  }

  private applyFilters(): void {
    let filtered = [...this.allBooks];

    if (this.filterBy) {
      filtered = filtered.filter(b => 
        b.name.toLowerCase().includes(this.filterBy.toLowerCase())
      );
    }

    this.filteredBooks = filtered;
  }

  onFilterInput(event: any): void {
    this.filterBy = event.target.value;
    this.applyFilters();
  }

  onSortChange(value: string): void {
    this.sortBy = value;
    if (this.sortBy === 'name') {
      this.filteredBooks.sort((a, b) => a.name.localeCompare(b.name));
    } else if (this.sortBy === 'rating') {
      this.filteredBooks.sort((a, b) => (b.rating || 0) - (a.rating || 0));
    }
  }

  get resultCount(): number {
    return this.filteredBooks.length;
  }

  onViewSeries(book: Series): void {
    // Check if this is a library book (has id) or a popular book (might not have id)
    if (book.id && book.id > 0) {
      // This is a library book - navigate to the book detail page
      this.router.navigate(['/books', book.id]);
    } else {
      // This is a popular book from AI - use the same logic as search
      this.openSearchDetailsModal(book);
    }
  }

  openSearchDetailsModal(book: Series): void {
    // Popular books from AI don't have metadata_id, so we need to search OpenLibrary first
    const title = book.name || book.title;
    const author = book.author;
    
    if (!title || !author) {
      // If we don't have enough info, open with basic data
      this.openModalWithBasicData(book);
      return;
    }

    console.log('=== Popular Books Debug ===');
    console.log('Searching OpenLibrary for:', title, 'by', author);

    // Search for the book in OpenLibrary first (like search system does)
    const searchQuery = `${title} ${author}`;
    const searchUrl = `http://localhost:7227/api/metadata/search/openlibrary?q=${encodeURIComponent(searchQuery)}&limit=1`;
    
    console.log('Searching OpenLibrary with URL:', searchUrl);
    
    this.http.get<any>(searchUrl).subscribe({
      next: (response) => {
        console.log('OpenLibrary search response:', response);
        
        if (response && response.success && response.results && response.results.length > 0) {
          // Found the book in OpenLibrary
          const openlibraryBook = response.results[0];
          console.log('Found book in OpenLibrary:', openlibraryBook);
          
          // Now fetch detailed information using the OpenLibrary ID
          this.fetchDetailsAndOpenModal(openlibraryBook, book);
        } else {
          // Not found with exact search, try broader search
          console.log('Not found with exact search, trying broader search...');
          this.tryBroaderSearch(book);
        }
      },
      error: (err) => {
        console.error('Error searching OpenLibrary:', err);
        // Fallback to basic data
        this.openModalWithBasicData(book);
      }
    });
  }

  tryBroaderSearch(book: Series): void {
    // Try searching with just the title
    const title = book.name || book.title;
    if (!title) {
      this.openModalWithBasicData(book);
      return;
    }
    
    const searchUrl = `http://localhost:7227/api/metadata/search/openlibrary?q=${encodeURIComponent(title)}&limit=5`;
    
    console.log('Trying broader search for:', title);
    
    this.http.get<any>(searchUrl).subscribe({
      next: (response) => {
        console.log('Broader search response:', response);
        
        if (response && response.success && response.results && response.results.length > 0) {
          // Find the best match by author
          const bestMatch = response.results.find((result: any) => 
            result.author && result.author.toLowerCase().includes(book.author?.toLowerCase() || '')
          ) || response.results[0];
          
          console.log('Best match found:', bestMatch);
          this.fetchDetailsAndOpenModal(bestMatch, book);
        } else {
          // Still not found, use basic data
          console.log('No results found, using basic data');
          this.openModalWithBasicData(book);
        }
      },
      error: (err) => {
        console.error('Error in broader search:', err);
        this.openModalWithBasicData(book);
      }
    });
  }

  fetchDetailsAndOpenModal(openlibraryBook: any, originalBook: Series): void {
    if (!openlibraryBook.provider || !openlibraryBook.id) {
      console.log('Missing provider or ID, using basic data');
      this.openModalWithBasicData(originalBook);
      return;
    }

    // Fetch detailed information from the metadata API (same as search system)
    const detailsUrl = `http://localhost:7227/api/metadata/details/${openlibraryBook.provider}/${openlibraryBook.id}`;
    
    console.log('Fetching detailed info from:', detailsUrl);
    
    this.http.get<any>(detailsUrl).subscribe({
      next: (response) => {
        console.log('Detailed info response:', response);
        
        // Create the result object in the format expected by SearchDetailsComponent
        let result = {
          id: openlibraryBook.id,
          title: originalBook.name || originalBook.title || openlibraryBook.title || openlibraryBook.name,
          name: originalBook.name || originalBook.title || openlibraryBook.title || openlibraryBook.name, // Add name field as fallback
          author: originalBook.author || openlibraryBook.author,
          publisher: openlibraryBook.publisher || 'Unknown',
          published_date: openlibraryBook.published_date || openlibraryBook.first_publish_date || 'Unknown',
          isbn: openlibraryBook.isbn || 'Unknown',
          subjects: openlibraryBook.subjects || openlibraryBook.genres || [],
          genres: openlibraryBook.genres || openlibraryBook.subjects || [], // Add both fields
          description: openlibraryBook.description || 'No description available',
          cover_url: openlibraryBook.cover_url || '/assets/no-cover.png',
          provider: openlibraryBook.provider,
          content_type: 'book',
          alternative_titles: openlibraryBook.alternative_titles || []
        };

        if (response && response.success && response.details) {
          // Merge with detailed information - ensure all required fields are present
          const details = response.details;
          result = { 
            ...result, 
            ...details,
            // Ensure these fields are properly set even after merge
            title: details.title || result.title,
            name: details.name || details.title || result.name,
            author: details.author || result.author,
            publisher: details.publisher || result.publisher,
            published_date: details.published_date || details.first_publish_date || result.published_date,
            isbn: details.isbn || result.isbn,
            subjects: details.subjects || details.genres || result.subjects,
            genres: details.genres || details.subjects || result.genres,
            description: details.description || result.description,
            cover_url: details.cover_url || result.cover_url,
            alternative_titles: details.alternative_titles || result.alternative_titles
          };
          console.log('Merged result with details:', result);
        } else {
          console.log('Using OpenLibrary search result without additional details');
        }

        // Debug the final result
        console.log('=== Final Result Being Sent to Modal ===');
        console.log('Title:', result.title);
        console.log('Author:', result.author);
        console.log('Publisher:', result.publisher);
        console.log('Published Date:', result.published_date);
        console.log('ISBN:', result.isbn);
        console.log('Subjects:', result.subjects);
        console.log('Genres:', result.genres);
        console.log('Description:', result.description);
        console.log('Cover URL:', result.cover_url);
        console.log('Full result object:', result);

        // Open the modal with the complete details (exact same as search system)
        this.dialog.open(SearchDetailsComponent, {
          width: '1000px',
          maxWidth: '1000px',
          data: {
            result: result,
            contentType: 'book'
          },
          panelClass: 'search-details-dialog'
        });
      },
      error: (err) => {
        console.error('Error fetching detailed info:', err);
        
        // Use OpenLibrary search result without additional details
        const result = {
          id: openlibraryBook.id,
          title: originalBook.name || originalBook.title || openlibraryBook.title || openlibraryBook.name,
          name: originalBook.name || originalBook.title || openlibraryBook.title || openlibraryBook.name,
          author: originalBook.author || openlibraryBook.author,
          publisher: openlibraryBook.publisher || 'Unknown',
          published_date: openlibraryBook.published_date || openlibraryBook.first_publish_date || 'Unknown',
          isbn: openlibraryBook.isbn || 'Unknown',
          subjects: openlibraryBook.subjects || openlibraryBook.genres || [],
          genres: openlibraryBook.genres || openlibraryBook.subjects || [],
          description: openlibraryBook.description || 'No description available',
          cover_url: openlibraryBook.cover_url || '/assets/no-cover.png',
          provider: openlibraryBook.provider,
          content_type: 'book',
          alternative_titles: openlibraryBook.alternative_titles || []
        };

        console.log('=== Final Result (Error Fallback) Being Sent to Modal ===');
        console.log('Full result object:', result);

        this.dialog.open(SearchDetailsComponent, {
          width: '1000px',
          maxWidth: '1000px',
          data: {
            result: result,
            contentType: 'book'
          },
          panelClass: 'search-details-dialog'
        });
      }
    });
  }

  openModalWithBasicData(book: Series): void {
    console.log('Opening modal with basic data:', book);
    
    // Convert to the format expected by SearchDetailsComponent
    const result = {
      id: book.metadata_id,
      title: book.name || book.title,
      author: book.author,
      publisher: book.publisher,
      published_date: book.published_date,
      isbn: book.isbn,
      subjects: book.subjects,
      description: book.description,
      cover_url: book.cover_url,
      provider: book.metadata_source || 'AI Generated',
      content_type: 'book'
    };

    // Open the modal with basic data
    this.dialog.open(SearchDetailsComponent, {
      width: '1000px',
      maxWidth: '1000px',
      data: {
        result: result,
        contentType: 'book'
      },
      panelClass: 'search-details-dialog'
    });
  }

  scanForBooks(): void {
    if (this.isScanning) return;
    
    this.isScanning = true;
    this.notificationService.info('Starting scan for books...');
    
    console.log('Books scan: Sending request with content_type: book');
    
    this.seriesService.scanForEbooks(undefined, 'book').subscribe({
      next: (result) => {
        this.isScanning = false;
        console.log('Books scan result:', result);
        
        if (result.success) {
          const message = `Scan completed! Found ${result.scanned || 0} files, added ${result.added || 0} new books.`;
          this.notificationService.success(message);
          
          // Reload the books list to show any new additions
          this.loadBooks();
        } else {
          const errorMsg = result.error || 'Scan failed';
          this.notificationService.error(errorMsg);
        }
      },
      error: (err) => {
        this.isScanning = false;
        console.error('Error scanning for books:', err);
        this.notificationService.error('Failed to scan for books. Please try again.');
      }
    });
  }

  private loadPopularBooks(): void {
    this.isLoadingPopular = true;
    
    this.apiService.get<any>('/books/popular-this-week').subscribe({
      next: (response) => {
        if (response.success) {
          this.popularBooks = response.popular_books || [];
          console.log('Popular books loaded:', this.popularBooks.length, 'books');
        } else {
          console.error('Failed to load popular books:', response.error);
          this.popularBooks = [];
        }
        this.isLoadingPopular = false;
      },
      error: (err) => {
        console.error('Error loading popular books:', err);
        this.popularBooks = [];
        this.isLoadingPopular = false;
      }
    });
  }
}
