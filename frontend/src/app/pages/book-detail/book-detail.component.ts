import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { LoadingSpinnerComponent } from '../../components/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../components/error-message/error-message.component';
import { SeriesService } from '../../services/series.service';
import { NotificationService } from '../../services/notification.service';
import { Series } from '../../models/series.model';
import { MatDialog } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatBadgeModule } from '@angular/material/badge';
import { MatRadioModule } from '@angular/material/radio';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { EditBookDialogBootstrap } from './edit-book-dialog-bootstrap';
import { MoveBookDialogMaterial } from './move-book-dialog-material';
import { DeleteBookDialogMaterial } from './delete-book-dialog-material';
import { DeleteBookDialogComponent } from '../../components/dialogs/delete-book-dialog/delete-book-dialog.component';
import { ModalService } from '../../services/modal.service';

@Component({
  selector: 'app-book-detail',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCheckboxModule,
    MatProgressSpinnerModule,
    MatBadgeModule,
    MatRadioModule,
    MatTooltipModule,
    MatChipsModule,
    MatButtonToggleModule,
    LoadingSpinnerComponent,
    ErrorMessageComponent
  ],
  templateUrl: './book-detail.component.html',
  styleUrls: ['./book-detail.component.css']
})
export class BookDetailComponent implements OnInit {
  book: Series | null = null;
  isLoading = true;
  error: string | null = null;
  starRating = 0;
  private _readingProgress = 0;
  userNotes = '';
  showEbookSection = false;
  isInWantToRead = false;
  isWantToReadLoading = false;

  // Getter to ensure readingProgress is always a valid number
  get readingProgress(): number {
    return this._readingProgress;
  }

  // Setter with validation
  set readingProgress(value: number) {
    this._readingProgress = (value !== undefined && value !== null && !isNaN(value)) ? value : 0;
  }

  constructor(
    private route: ActivatedRoute,
    private seriesService: SeriesService,
    private notificationService: NotificationService,
    private router: Router,
    private dialog: MatDialog,
    private cd: ChangeDetectorRef,
    private modalService: ModalService
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      const id = params['id'];
      if (id) {
        this.loadBook(id);
      }
    });
  }

  private loadBook(id: number): void {
    this.isLoading = true;
    this.error = null;

    this.seriesService.getSeriesById(id).subscribe({
      next: (book) => {
        this.book = book;
        this.starRating = (book as any).star_rating || 0;
        // Use the setter to ensure readingProgress is always a valid number (0-100)
        this.readingProgress = (book as any).reading_progress;
        this.userNotes = (book as any).user_description || '';
        this.isLoading = false;
        
        // Force change detection to prevent ExpressionChangedAfterItHasBeenCheckedError
        setTimeout(() => {
          this.cd.detectChanges();
        });
      },
      error: (err) => {
        this.error = 'Failed to load book details';
        this.notificationService.error('Failed to load book details');
        this.isLoading = false;
      }
    });
  }

  setRating(rating: number): void {
    this.starRating = rating;
    this.saveBookData();
  }

  setReadingProgress(progress: number): void {
    this.readingProgress = progress;
    this.saveBookData();
  }

  saveNotes(): void {
    this.saveBookData();
  }

  resetStatus(): void {
    this.starRating = 0;
    this.readingProgress = 0;
    this.userNotes = '';
    this.saveBookData();
  }

  saveBookData(): void {
    if (!this.book) return;

    const updateData = {
      star_rating: this.starRating,
      reading_progress: this.readingProgress,
      user_description: this.userNotes
    };

    this.seriesService.updateSeries(this.book.id, updateData).subscribe({
      next: () => {
        this.notificationService.success('Book updated successfully');
      },
      error: (err) => {
        this.notificationService.error('Failed to update book');
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/books']);
  }

  getCoverUrl(url: string | undefined): string {
    return url || '/assets/no-cover.png';
  }

  getGenres(): string[] {
    if (!this.book) return [];
    const subjects = (this.book as any).subjects;
    if (!subjects) return [];
    if (typeof subjects === 'string') {
      return subjects.split(',').map(s => s.trim());
    }
    return Array.isArray(subjects) ? subjects : [];
  }

  toggleEbookSection(): void {
    this.showEbookSection = !this.showEbookSection;
  }

  openMoveModal(): void {
  const dialogRef = this.dialog.open(MoveBookDialogMaterial, {
    width: '500px',
    maxWidth: '95vw',
    data: {
      book: this.book,
      collections: [], // TODO: Load collections
      rootFolders: [] // TODO: Load root folders
    }
  });

  dialogRef.afterClosed().subscribe(result => {
    if (result && this.book) {
      // TODO: Implement move functionality
      console.log('Move book:', result);
      this.notificationService.success('Book moved successfully');
    }
  });
}

openEditModal(): void {
  const dialogRef = this.dialog.open(EditBookDialogBootstrap, {
    panelClass: 'bootstrap-dialog-container',
    width: '600px',
    maxWidth: '95vw',
    data: {
      book: this.book,
      collections: [] // TODO: Load collections
    }
  });

  dialogRef.afterClosed().subscribe(result => {
    if (result && this.book) {
      this.seriesService.updateSeries(this.book.id, result).subscribe({
        next: () => {
          this.notificationService.success('Book updated successfully');
          this.loadBook(this.book!.id);
        },
        error: (err) => {
          this.notificationService.error('Failed to update book');
        }
      });
    }
  });
}

openDeleteModal(): void {
  if (!this.book) return;
  
  const bookTitle = this.book.title || this.book.name;
  this.modalService.openModal({
    id: 'deleteConfirmationModal',
    title: 'Confirm Delete',
    data: { 
      message: `Are you sure you want to delete "${bookTitle}"? This will permanently remove the book from your library.`,
      showEbookCheckbox: true
    }
  });

  // Subscribe to modal result
  this.modalService.getModalResult('deleteConfirmationModal').subscribe((result) => {
    if (result?.action === 'confirm' && this.book) {
      const removeEbookFiles = result.data?.removeEbookFiles || false;
      this.deleteBookFromDatabase(removeEbookFiles);
    }
  });
}

private deleteBookFromDatabase(deleteFiles: boolean): void {
    if (!this.book) return;

    // Log to proper logger instead of console
    console.log('Attempting to delete book:', this.book.id, 'with deleteFiles:', deleteFiles);
    
    // First verify the book still exists by trying to get it
    this.seriesService.getSeriesById(this.book.id).subscribe({
      next: (book) => {
        if (book) {
          console.log('Book verified to exist, proceeding with deletion');
          this.performDelete(deleteFiles);
        } else {
          console.log('Book no longer exists in database');
          this.notificationService.error('This book no longer exists and cannot be deleted.');
          // Navigate back to books list since the book doesn't exist
          this.router.navigate(['/books']);
        }
      },
      error: (err) => {
        // Check if it's a 404 error (book not found)
        if (err.status === 404) {
          console.log('Book not found (404), treating as deleted');
          this.notificationService.error('This book no longer exists and cannot be deleted.');
          this.router.navigate(['/books']);
        } else {
          // Other error - show general error message
          this.notificationService.error('Failed to verify book existence. Please refresh and try again.');
        }
      }
    });
  }

  private performDelete(deleteFiles: boolean): void {
    if (!this.book) return;
    
    console.log('Performing delete for book:', this.book.id, 'with deleteFiles:', deleteFiles);
    
    this.seriesService.deleteSeries(this.book.id, deleteFiles).subscribe({
      next: (response) => {
        console.log('Delete response:', response);
        this.notificationService.success('Book deleted successfully');
        // Navigate back to books library
        this.router.navigate(['/books']);
      },
      error: (err) => {
        console.error('Error deleting book:', err);
        this.notificationService.error('Failed to delete book. Please try again.');
      }
    });
  }

  openUploadModal(): void {
    const modal = document.getElementById('uploadEbookModal');
    if (modal) {
      const bootstrapModal = (window as any).bootstrap.Modal.getOrCreateInstance(modal);
      bootstrapModal.show();
    }
  }

  saveBookChanges(): void {
    if (!this.book) return;

    const title = (document.getElementById('bookTitle') as HTMLInputElement)?.value;
    const author = (document.getElementById('bookAuthor') as HTMLInputElement)?.value;
    const publisher = (document.getElementById('bookPublisher') as HTMLInputElement)?.value;
    const publishedDate = (document.getElementById('bookPublishedDate') as HTMLInputElement)?.value;
    const isbn = (document.getElementById('bookISBN') as HTMLInputElement)?.value;
    const coverUrl = (document.getElementById('bookCoverURL') as HTMLInputElement)?.value;
    const genres = (document.getElementById('bookGenres') as HTMLInputElement)?.value.split(',').map(g => g.trim());
    const description = (document.getElementById('bookDescription') as HTMLTextAreaElement)?.value;

    const updateData = {
      title,
      author,
      publisher,
      published_date: publishedDate,
      isbn,
      cover_url: coverUrl,
      subjects: genres.join(','),
      description
    };

    this.seriesService.updateSeries(this.book.id, updateData).subscribe({
      next: () => {
        this.notificationService.success('Book updated successfully');
        const modal = document.getElementById('editBookModal');
        if (modal) {
          (window as any).bootstrap.Modal.getInstance(modal)?.hide();
        }
        this.loadBook(this.book!.id);
      },
      error: (err) => {
        this.notificationService.error('Failed to update book');
      }
    });
  }

  deleteBook(): void {
    if (!this.book) return;

    const deleteFiles = (document.getElementById('deleteFiles') as HTMLInputElement)?.checked || false;

    this.seriesService.deleteSeries(this.book.id).subscribe({
      next: () => {
        this.notificationService.success('Book deleted successfully');
        const modal = document.getElementById('deleteBookModal');
        if (modal) {
          (window as any).bootstrap.Modal.getInstance(modal)?.hide();
        }
        setTimeout(() => {
          this.router.navigate(['/books']);
        }, 1500);
      },
      error: (err) => {
        this.notificationService.error('Failed to delete book');
      }
    });
  }

  uploadEbook(): void {
    const fileInput = document.getElementById('ebookFile') as HTMLInputElement;
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
      this.notificationService.warning('Please select a file to upload');
      return;
    }

    this.notificationService.success('E-book upload functionality coming soon');
  }

  toggleWantToRead(): void {
    if (!this.book) return;

    const metadataSource = (this.book as any).metadata_source;
    const metadataId = (this.book as any).metadata_id;
    const contentType = (this.book as any).content_type || 'BOOK';

    if (!metadataSource || !metadataId) {
      this.notificationService.error('This book does not have metadata source information');
      return;
    }

    this.isWantToReadLoading = true;

    if (this.isInWantToRead) {
      this.seriesService.removeFromWantToRead(metadataSource, metadataId).subscribe({
        next: (response) => {
          this.isWantToReadLoading = false;
          if (response.success) {
            this.isInWantToRead = false;
            this.notificationService.success('Removed from Want to Read');
          } else {
            this.notificationService.error('Failed to remove from Want to Read');
          }
        },
        error: (err) => {
          this.isWantToReadLoading = false;
          this.notificationService.error('Failed to remove from Want to Read');
        }
      });
    } else {
      this.seriesService.addToWantToRead(metadataSource, metadataId, contentType).subscribe({
        next: (response) => {
          this.isWantToReadLoading = false;
          if (response.success) {
            this.isInWantToRead = true;
            this.notificationService.success('Added to Want to Read');
          } else {
            this.notificationService.error('Failed to add to Want to Read');
          }
        },
        error: (err) => {
          this.isWantToReadLoading = false;
          this.notificationService.error('Failed to add to Want to Read');
        }
      });
    }
  }
}
