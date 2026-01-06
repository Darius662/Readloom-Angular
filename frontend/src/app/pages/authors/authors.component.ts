import { Component, OnInit } from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDialogModule } from '@angular/material/dialog';
import { LoadingSpinnerComponent } from '../../components/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../components/error-message/error-message.component';
import { AuthorDetailsComponent, AuthorDetailsDialogData } from '../../components/modals/author-details/author-details.component';
import { AuthorService } from '../../services/author.service';
import { ApiService } from '../../services/api.service';
import { NotificationService } from '../../services/notification.service';
import { Author, AuthorMetadata } from '../../models/author.model';
import { MatDialog } from '@angular/material/dialog';

@Component({
    selector: 'app-authors',
    imports: [
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatDialogModule,
    LoadingSpinnerComponent,
    ErrorMessageComponent
],
    templateUrl: './authors.component.html',
    styleUrls: ['./authors.component.css']
})
export class AuthorsComponent implements OnInit {
  title = 'Authors';
  isLoading = true;
  error: string | null = null;
  authors: Author[] = [];
  searchQuery = '';
  filteredAuthors: Author[] = [];

  constructor(
    private authorService: AuthorService,
    private apiService: ApiService,
    private notificationService: NotificationService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.loadAuthors();
  }

  private loadAuthors(): void {
    this.isLoading = true;
    this.error = null;

    this.authorService.getAuthors().subscribe({
      next: (authors) => {
        this.authors = authors;
        this.applyFilter();
        this.isLoading = false;
      },
      error: (err) => {
        this.error = 'Failed to load authors';
        this.notificationService.error('Failed to load authors');
        this.isLoading = false;
      }
    });
  }

  onSearch(query: string): void {
    this.searchQuery = query;
    this.applyFilter();
  }

  private applyFilter(): void {
    if (this.searchQuery.trim()) {
      const query = this.searchQuery.toLowerCase();
      this.filteredAuthors = this.authors.filter(a => 
        a.name.toLowerCase().includes(query)
      );
    } else {
      this.filteredAuthors = [...this.authors];
    }
  }

  get resultCount(): number {
    return this.filteredAuthors.length;
  }

  openAuthorDetails(author: Author): void {
    // For now, we'll pass the author without metadata
    // In the future, you might want to fetch author metadata from the backend
    const dialogData: AuthorDetailsDialogData = {
      author: author,
      metadata: undefined // You can fetch this from an API if available
    };

    const dialogRef = this.dialog.open(AuthorDetailsComponent, {
      width: '700px',
      maxWidth: '90vw',
      data: dialogData,
      panelClass: 'author-details-dialog'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        console.log('Author details dialog closed with result:', result);
      }
    });
  }

  enrichAllAuthors(): void {
    this.notificationService.info('Starting author enrichment process...');
    
    // Call the enrichment API using ApiService
    this.apiService.post<any>('/authors/enrich-all', {})
      .subscribe({
        next: (data) => {
          if (data.success) {
            const stats = data.stats;
            let message = `Author enrichment completed!\n`;
            message += `• Authors checked: ${stats.authors_checked}\n`;
            message += `• Updated from OpenLibrary: ${stats.openlibrary_updated}\n`;
            message += `• Biographies added: ${stats.biographies_added}\n`;
            message += `• Photos added: ${stats.photos_added}\n`;
            message += `• Errors: ${stats.errors}`;
            
            this.notificationService.success(message);
            
            // Reload authors to show updated data
            this.loadAuthors();
          } else {
            this.notificationService.error(`Enrichment failed: ${data.error || data.message}`);
          }
        },
        error: (error) => {
          console.error('Error enriching authors:', error);
          this.notificationService.error('Failed to enrich authors. Please try again.');
        }
      });
  }

  checkIncompleteAuthors(): void {
    this.apiService.get<any>('/authors/check-incomplete')
      .subscribe({
        next: (data) => {
          if (data.incomplete_authors > 0) {
            this.notificationService.info(
              `Found ${data.incomplete_authors} authors needing enrichment:\n` +
              `• Without biography: ${data.authors_without_biography}\n` +
              `• Without photo: ${data.authors_without_photo}`
            );
          } else {
            this.notificationService.success('All authors have complete metadata!');
          }
        },
        error: (error) => {
          console.error('Error checking incomplete authors:', error);
          this.notificationService.error('Failed to check author status.');
        }
      });
  }

  updateAllReadmeFiles(): void {
    this.notificationService.info('Updating all README.txt files...');
    
    this.apiService.post<any>('/readme/update-all', {})
      .subscribe({
        next: (data) => {
          if (data.success) {
            const stats = data.stats;
            let message = `✓ README files updated!\n`;
            message += `• Files found: ${stats.readme_files_found}\n`;
            message += `• Files updated: ${stats.readme_files_updated}\n`;
            message += `• Errors: ${stats.errors}`;
            
            this.notificationService.success(message);
          } else {
            this.notificationService.error(`Update failed: ${data.error || data.message}`);
          }
        },
        error: (error) => {
          console.error('Error updating README files:', error);
          this.notificationService.error('Failed to update README files. Please try again.');
        }
      });
  }
}
