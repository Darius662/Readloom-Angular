import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { HttpClient } from '@angular/common/http';
import { NotificationService } from '../../../services/notification.service';
import { SeriesService } from '../../../services/series.service';

@Component({
  selector: 'app-search-details',
  standalone: true,
  imports: [CommonModule, FormsModule, MatButtonModule, MatSelectModule],
  templateUrl: './search-details.component.html',
  styleUrls: ['./search-details.component.css']
})
export class SearchDetailsComponent {
  result: any;
  contentType: 'book' | 'manga' = 'book';
  selectedCollection = '';
  selectedRootFolder = '';
  collections: any[] = [];
  rootFolders: any[] = [];
  isAddingToCollection = false;
  isAddingToWantToRead = false;
  
  // Properties matching WantToReadDetailsComponent
  isInLibrary = false;
  isInWantToRead = false;
  seriesId?: number;
  isLoading = false;

  constructor(
    public dialogRef: MatDialogRef<SearchDetailsComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private http: HttpClient,
    private notificationService: NotificationService,
    private seriesService: SeriesService
  ) {
    this.result = data.result;
    this.contentType = data.contentType;
    
    // Debug logging
    console.log('=== SearchDetailsComponent Debug ===');
    console.log('Content Type:', this.contentType);
    console.log('Provider:', this.result.provider);
    console.log('Item ID:', this.result.id);
    console.log('Full Result Object:', this.result);
    console.log('Result Keys:', Object.keys(this.result));
    console.log('Publisher:', this.result.publisher);
    console.log('Published Date:', this.result.published_date);
    console.log('ISBN:', this.result.isbn);
    console.log('Subjects:', this.result.subjects);
    console.log('Genres:', this.result.genres);
    console.log('Description:', this.result.description);
    
    this.loadCollections();
    this.checkItemStatus();
    
    // Force 1000px width
    this.dialogRef.updateSize('1000px');
  }

  loadCollections(): void {
    this.http.get<any>('http://localhost:7227/api/collections').subscribe({
      next: (response) => {
        if (response.success && Array.isArray(response.collections)) {
          this.collections = response.collections;
          this.autoSelectDefaultCollection();
        }
      },
      error: (err) => {
        console.error('Error loading collections:', err);
      }
    });
  }

  autoSelectDefaultCollection(): void {
    const contentTypeMap: { [key: string]: string } = {
      'book': 'BOOK',
      'manga': 'MANGA'
    };
    const targetType = contentTypeMap[this.contentType] || 'MANGA';
    const defaultCollection = this.collections.find(
      c => (c.content_type || 'MANGA').toUpperCase() === targetType && c.is_default === 1
    );
    if (defaultCollection) {
      this.selectedCollection = defaultCollection.id.toString();
      this.loadRootFolders(defaultCollection.id);
    }
  }

  loadRootFolders(collectionId: number): void {
    if (!collectionId) {
      this.rootFolders = [];
      return;
    }
    this.http.get<any>(`http://localhost:7227/api/collections/${collectionId}/root-folders`).subscribe({
      next: (response) => {
        if (response.success && Array.isArray(response.root_folders)) {
          this.rootFolders = response.root_folders;
        }
      },
      error: (err) => {
        console.error('Error loading root folders:', err);
      }
    });
  }

  onCollectionChange(): void {
    const collectionId = parseInt(this.selectedCollection);
    this.loadRootFolders(collectionId);
  }

  addToCollection(): void {
    if (!this.selectedCollection) {
      this.notificationService.warning('Please select a collection');
      return;
    }

    this.isAddingToCollection = true;
    const payload = {
      content_type: this.contentType.toUpperCase(),
      collection_id: parseInt(this.selectedCollection) || null,
      root_folder_id: this.selectedRootFolder ? parseInt(this.selectedRootFolder) : null
    };

    this.http.post<any>(
      `http://localhost:7227/api/metadata/import/${this.result.provider}/${this.result.id}`,
      payload
    ).subscribe({
      next: (response) => {
        this.isAddingToCollection = false;
        if (response.success) {
          this.notificationService.success('Added to collection successfully');
          this.dialogRef.close({ action: 'added', seriesId: response.series_id });
        } else if (response.already_exists) {
          this.notificationService.info('This item is already in your collection');
          this.dialogRef.close({ action: 'exists', seriesId: response.series_id });
        } else {
          this.notificationService.error(response.message || 'Failed to add to collection');
        }
      },
      error: (err) => {
        this.isAddingToCollection = false;
        console.error('Error adding to collection:', err);
        this.notificationService.error('Failed to add to collection');
      }
    });
  }

  wantToRead(): void {
    if (!this.result.id || !this.result.provider) {
      this.notificationService.error('Cannot add to Want to Read: Missing item information');
      return;
    }

    this.isAddingToWantToRead = true;
    const contentType = this.contentType.toUpperCase();

    this.seriesService.addToWantToRead(this.result.provider, this.result.id, contentType).subscribe({
      next: (response) => {
        this.isAddingToWantToRead = false;
        if (response.success) {
          this.notificationService.success('Added to Want to Read');
          this.dialogRef.close({ action: 'want-to-read' });
        } else {
          this.notificationService.error(response.message || 'Failed to add to Want to Read');
        }
      },
      error: (err) => {
        this.isAddingToWantToRead = false;
        console.error('Error adding to want to read:', err);
        this.notificationService.error('Failed to add to Want to Read');
      }
    });
  }

  close(): void {
    this.dialogRef.close();
  }

  checkItemStatus(): void {
    if (!this.result.id || !this.result.provider) {
      console.log('=== SearchDetailsComponent: Missing ID or provider ===');
      console.log('ID:', this.result.id, 'Provider:', this.result.provider);
      return;
    }

    console.log('=== SearchDetailsComponent: Checking item status ===');
    console.log('Provider:', this.result.provider);
    console.log('Item ID:', this.result.id);

    this.isLoading = true;
    
    // Check if item is in library
    const existsUrl = `http://localhost:7227/api/metadata/exists/${this.result.provider}/${this.result.id}`;
    console.log('=== Checking library existence ===');
    console.log('URL:', existsUrl);
    
    this.http.get<any>(existsUrl).subscribe({
      next: (response) => {
        console.log('=== Library check response ===');
        console.log('Response:', response);
        
        if (response.exists) {
          this.isInLibrary = true;
          this.seriesId = response.series_id;
          console.log('=== Item is in library ===');
          console.log('Series ID:', this.seriesId);
        } else {
          console.log('=== Item is NOT in library ===');
        }
        
        // Check if item is in want-to-read list
        this.checkWantToReadStatus();
      },
      error: (err) => {
        console.error('=== Error checking library status ===');
        console.error('Error:', err);
        this.checkWantToReadStatus();
      }
    });
  }

  checkWantToReadStatus(): void {
    if (!this.result.id || !this.result.provider) {
      console.log('=== SearchDetailsComponent: Missing ID or provider for want-to-read check ===');
      this.isLoading = false;
      return;
    }

    console.log('=== SearchDetailsComponent: Checking want-to-read status ===');
    console.log('Provider:', this.result.provider);
    console.log('Item ID:', this.result.id);

    // Get want-to-read items and check if current item is in the list
    this.seriesService.getWantToReadItems().subscribe({
      next: (items: any[]) => {
        console.log('=== Want-to-read items received ===');
        console.log('Items count:', items.length);
        console.log('Items:', items);
        
        // Match by provider and metadata_id (now standardized)
        const isInList = items.some(item => 
          item.provider === this.result.provider && item.metadata_id === this.result.id
        );
        
        this.isInWantToRead = isInList;
        this.isLoading = false;
        
        console.log('=== Want-to-read check result ===');
        console.log('Is in want-to-read:', this.isInWantToRead);
        console.log('Final Status:', {
          isInLibrary: this.isInLibrary,
          isInWantToRead: this.isInWantToRead,
          seriesId: this.seriesId
        });
      },
      error: (err: any) => {
        console.error('=== Error checking want-to-read status ===');
        console.error('Error:', err);
        this.isLoading = false;
      }
    });
  }

  get primaryButtonText(): string {
    if (this.isInLibrary && this.seriesId) {
      const contentType = this.contentType || 'manga';
      const isBook = ['BOOK', 'NOVEL'].includes(contentType.toUpperCase());
      return isBook ? 'Go to Book' : 'Go to Series';
    }
    return 'Add to Collection';
  }

  get secondaryButtonText(): string {
    if (this.isInWantToRead) {
      return 'Remove from Want to Read';
    }
    return 'Want to Read';
  }

  get secondaryButtonClass(): string {
    if (this.isInWantToRead) {
      return 'btn btn-outline-danger w-100';
    }
    return 'btn btn-outline-warning w-100';
  }

  handlePrimaryAction(): void {
    if (this.isInLibrary && this.seriesId) {
      // Navigate to the item in library
      const contentType = this.contentType || 'manga';
      const isBook = ['BOOK', 'NOVEL'].includes(contentType.toUpperCase());
      const goToUrl = isBook ? `/books/${this.seriesId}` : `/manga/series/${this.seriesId}`;
      
      console.log('Navigating to:', goToUrl);
      
      // Close modal and navigate
      this.dialogRef.close('navigated');
      window.location.href = goToUrl;
    } else {
      // Add to collection
      this.addToCollection();
    }
  }

  handleSecondaryAction(): void {
    if (this.isInWantToRead) {
      this.removeFromWantToRead();
    } else {
      this.wantToRead();
    }
  }

  removeFromWantToRead(): void {
    if (!this.result.id || !this.result.provider) {
      this.notificationService.error('Cannot remove from Want to Read: Missing item information');
      return;
    }

    this.isAddingToWantToRead = true;

    this.seriesService.removeFromWantToRead(this.result.provider, this.result.id).subscribe({
      next: (response: any) => {
        this.isAddingToWantToRead = false;
        if (response.success) {
          this.notificationService.success('Removed from Want to Read');
          this.isInWantToRead = false;
          this.dialogRef.close({ action: 'removed-from-want-to-read' });
        } else {
          this.notificationService.error(response.message || 'Failed to remove from Want to Read');
        }
      },
      error: (err: any) => {
        this.isAddingToWantToRead = false;
        console.error('Error removing from want to read:', err);
        this.notificationService.error('Failed to remove from Want to Read');
      }
    });
  }

  getCoverUrl(coverUrl: string): string {
    if (!coverUrl) return '/assets/no-cover.png';
    return coverUrl;
  }
}
