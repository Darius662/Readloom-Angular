import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatChipsModule } from '@angular/material/chips';
import { HttpClient } from '@angular/common/http';
import { NotificationService } from '../../../services/notification.service';
import { SeriesService } from '../../../services/series.service';
import { Series } from '../../../models/series.model';

export interface WantToReadDetailsData {
  item: Series;
  inLibrary: boolean;
  seriesId?: number;
}

@Component({
  selector: 'app-want-to-read-details',
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    MatChipsModule
  ],
  templateUrl: './want-to-read-details.component.html',
  styleUrls: ['./want-to-read-details.component.css']
})
export class WantToReadDetailsComponent {
  item: Series;
  isInLibrary = false;
  seriesId?: number;
  isLoading = false;

  constructor(
    private dialogRef: MatDialogRef<WantToReadDetailsComponent>,
    @Inject(MAT_DIALOG_DATA) public data: WantToReadDetailsData,
    private http: HttpClient,
    private notificationService: NotificationService,
    private seriesService: SeriesService
  ) {
    console.log('Modal constructor - data received:', JSON.stringify(this.data, null, 2));
    console.log('Modal constructor - data.inLibrary:', this.data.inLibrary, 'type:', typeof this.data.inLibrary);
    
    this.item = data.item;
    this.isInLibrary = data.inLibrary;
    this.seriesId = data.seriesId;
    
    console.log('Modal constructor - this.isInLibrary:', this.isInLibrary);
    console.log('Modal constructor - this.seriesId:', this.seriesId);
  }

  get primaryButtonText(): string {
    if (this.isInLibrary && this.seriesId) {
      const contentType = this.item?.content_type || 'MANGA';
      const isBook = ['BOOK', 'NOVEL'].includes(contentType.toUpperCase());
      return isBook ? 'Go to Book' : 'Go to Series';
    }
    return 'Add to Collection';
  }

  closeModal(): void {
    this.dialogRef.close();
  }

  handlePrimaryAction(): void {
    if (this.isInLibrary && this.seriesId) {
      // Navigate to the item in library
      const contentType = this.item.content_type || 'MANGA';
      const isBook = ['BOOK', 'NOVEL'].includes(contentType.toUpperCase());
      const goToUrl = isBook ? `/books/${this.seriesId}` : `/manga/series/${this.seriesId}`;
      
      console.log('Navigating to:', goToUrl);
      
      // Close modal and navigate
      this.dialogRef.close('navigated');
      // Navigate to the item
      window.location.href = goToUrl;
    } else {
      // Add to collection
      this.addToCollection();
    }
  }

  addToCollection(): void {
    if (!this.item) return;

    this.isLoading = true;
    
    // Use the same API endpoint as search details modal
    const provider = this.item.metadata_source || this.item.provider || 'unknown';
    const itemId = this.item.metadata_id || this.item.id;
    
    if (!itemId) {
      this.notificationService.error('Cannot add to collection: Missing item information');
      this.isLoading = false;
      return;
    }

    const payload = {
      content_type: this.item.content_type?.toUpperCase() || 'MANGA',
      collection_id: null, // Will use default collection
      root_folder_id: null // Will use default root folder
    };

    this.http.post<any>(
      `http://localhost:7227/api/metadata/import/${provider}/${itemId}`,
      payload
    ).subscribe({
      next: (response) => {
        this.isLoading = false;
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
        this.isLoading = false;
        console.error('Error adding to collection:', err);
        this.notificationService.error('Failed to add to collection');
      }
    });
  }

  removeFromWantToRead(): void {
    if (!this.item) return;

    this.isLoading = true;
    const provider = this.item.metadata_source || this.item.provider || 'unknown';
    const metadataId = this.item.metadata_id || this.item.id?.toString();
    
    console.log('Removing from want-to-read:', {
      provider,
      metadataId,
      itemName: this.item.name || this.item.title
    });

    // Use SeriesService for proper cleanup
    this.seriesService.removeFromWantToRead(provider, metadataId).subscribe({
      next: (response: any) => {
        this.isLoading = false;
        console.log('Remove from want-to-read response:', response);
        
        if (response.success) {
          this.notificationService.success('Item removed from your want to read list');
          
          // Additional cleanup: if item was only in want-to-read (not in library),
          // we might need to clean up any cached metadata
          if (!this.isInLibrary) {
            console.log('Item was only in want-to-read, performing additional cleanup');
            this.performAdditionalCleanup(provider, metadataId);
          }
          
          this.dialogRef.close('removed');
        } else {
          this.notificationService.error(response.message || 'Failed to remove item from want to read list');
        }
      },
      error: (err) => {
        this.isLoading = false;
        console.error('Error removing from want to read:', err);
        
        // Show proper error message - no fallbacks
        if (err.status === 404) {
          this.notificationService.error('Backend endpoint not found. Please ensure the backend server is running.');
        } else if (err.status === 0) {
          this.notificationService.error('Unable to connect to backend server. Please check if the server is running.');
        } else {
          this.notificationService.error('Failed to remove item from want to read list. Please try again.');
        }
      }
    });
  }

  private performAdditionalCleanup(provider: string, metadataId: string): void {
    // Additional cleanup for items that are only in want-to-read
    // This could include:
    // - Cleaning up cached metadata
    // - Removing any temporary files
    // - Clearing any related cache entries
    
    console.log('Performing additional cleanup for:', { provider, metadataId });
    
    // For now, we'll just log this, but you can add more cleanup calls here
    // Example: this.http.delete(`/api/metadata/cache/${provider}/${metadataId}`).subscribe(...)
  }
}
