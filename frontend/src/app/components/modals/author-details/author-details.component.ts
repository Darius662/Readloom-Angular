import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule } from '@angular/material/dialog';
import { MatCardModule } from '@angular/material/card';
import { ApiService } from '../../../services/api.service';
import { ModalService } from '../../../services/modal.service';

export interface AuthorDetailsDialogData {
  author: Author;
  metadata?: AuthorMetadata;
}

export interface Author {
  id: number;
  name: string;
  biography?: string;
  photo_url?: string;
  birth_date?: string;
  death_date?: string;
  folder_path?: string;
  last_updated?: string;
  book_count?: number;
}

export interface AuthorMetadata {
  goodreads_id?: string;
  wikipedia_url?: string;
  external_links?: string[];
  subjects?: string[];
  notable_works?: string[];
}

export interface Book {
  id: number;
  title: string;
  cover_url?: string;
  author?: string;
  content_type?: string;
  reading_progress?: number;
  star_rating?: number;
  // Additional fields for popular books
  source?: string;
  publisher?: string;
  first_publish_year?: number;
  isbn?: string;
  description?: string;
  openlibrary_key?: string;
  edition_count?: number;
}

@Component({
  selector: 'app-author-details',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule
  ],
  templateUrl: './author-details.component.html',
  styleUrls: ['./author-details.component.css']
})
export class AuthorDetailsComponent implements OnInit {
  author: Author = this.data.author;
  metadata?: AuthorMetadata = this.data.metadata;
  
  // Book data
  libraryBooks: Book[] = [];
  popularBooks: Book[] = [];
  releasedBooksCount = 0;
  libraryBooksCount = 0;
  isLoadingPopularBooks = false;
  
  constructor(
    private dialogRef: MatDialogRef<AuthorDetailsComponent>,
    private apiService: ApiService,
    private modalService: ModalService,
    @Inject(MAT_DIALOG_DATA) public data: AuthorDetailsDialogData
  ) {}

  ngOnInit(): void {
    this.loadAuthorData();
  }
  
  private loadAuthorData(): void {
    // Load author's books from library
    this.loadLibraryBooks();
    
    // Load popular books for this author
    this.loadPopularBooks();
    
    // Get released books count
    this.getReleasedBooksCount();
  }
  
  private loadLibraryBooks(): void {
    this.apiService.get<any>(`/authors/${this.author.id}/books`)
      .subscribe({
        next: (response) => {
          this.libraryBooks = response.books || [];
          this.libraryBooksCount = this.libraryBooks.length;
        },
        error: (error) => {
          console.error('Error loading library books:', error);
        }
      });
  }
  
  private loadPopularBooks(): void {
    this.isLoadingPopularBooks = true;
    this.apiService.get<any>(`/authors/${this.author.id}/popular-books`)
      .subscribe({
        next: (response) => {
          this.popularBooks = response.books || [];
          this.isLoadingPopularBooks = false;
        },
        error: (error) => {
          console.error('Error loading popular books:', error);
          this.popularBooks = [];
          this.isLoadingPopularBooks = false;
        }
      });
  }
  
  private getReleasedBooksCount(): void {
    this.apiService.get<any>(`/authors/${this.author.id}/released-count`)
      .subscribe({
        next: (response) => {
          this.releasedBooksCount = response.count || 0;
        },
        error: (error) => {
          console.error('Error getting released books count:', error);
        }
      });
  }

  formatDate(dateString: string): string {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
  
  onImageError(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.style.display = 'none';
    const placeholder = img.nextElementSibling as HTMLElement;
    if (placeholder) {
      placeholder.style.display = 'flex';
    }
  }
  
  onBookImageError(event: Event, book: Book): void {
    const img = event.target as HTMLImageElement;
    img.style.display = 'none';
    const placeholder = img.nextElementSibling as HTMLElement;
    if (placeholder) {
      placeholder.style.display = 'flex';
    }
  }

  openBookDetails(book: Book): void {
    // TODO: Implement book details modal when available
    console.log('Open book details for:', book.title);
  }

  showBookModal(book: Book): void {
    // Open the book details modal with the same functionality as library items
    const bookData = {
      ...book,
      provider: book.source === 'openlibrary' ? 'OpenLibrary' : 'AI Generated',
      // Add any missing fields that the book details modal expects
      publisher: book.publisher || 'N/A',
      published_date: book.first_publish_year?.toString() || 'N/A',
      isbn: book.isbn || 'N/A',
      description: book.description || 'No description available'
    };

    this.modalService.openModal({
      id: 'bookDetailsModal',
      title: 'Book Details',
      size: 'lg',
      data: {
        book: bookData
      }
    });
  }

  onClose(): void {
    this.dialogRef.close();
  }

  trackByBookId(index: number, book: Book): number {
    return book.id;
  }
}
