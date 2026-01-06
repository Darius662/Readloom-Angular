import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { LoadingSpinnerComponent } from '../../components/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../components/error-message/error-message.component';
import { SeriesService } from '../../services/series.service';
import { NotificationService } from '../../services/notification.service';
import { Series } from '../../models/series.model';

@Component({
    selector: 'app-library-items',
    imports: [
        CommonModule,
        FormsModule,
        MatCardModule,
        MatButtonModule,
        MatTableModule,
        MatSelectModule,
        MatFormFieldModule,
        MatIconModule,
        MatChipsModule,
        LoadingSpinnerComponent,
        ErrorMessageComponent
    ],
    templateUrl: './library-items.component.html',
    styleUrls: ['./library-items.component.css']
})
export class LibraryItemsComponent implements OnInit {
  title = 'Library Items';
  isLoading = true;
  error: string | null = null;
  
  allSeries: Series[] = [];
  filteredSeries: Series[] = [];
  
  // Stats
  totalSeries = 0;
  totalVolumes = 0;
  ownedVolumes = 0;
  libraryValue = 0;
  
  // Filters
  contentTypeFilter = '';
  ownershipStatusFilter = '';
  formatFilter = '';
  
  // Modal
  showModal = false;
  selectedSeries: Series | null = null;

  constructor(
    private seriesService: SeriesService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadLibraryItems();
  }

  private loadLibraryItems(): void {
    this.isLoading = true;
    this.error = null;

    this.seriesService.getSeries().subscribe({
      next: (series) => {
        this.allSeries = series;
        this.calculateStats();
        this.applyFilters();
        this.isLoading = false;
      },
      error: (err) => {
        this.error = 'Failed to load library items';
        this.notificationService.error('Failed to load library items');
        this.isLoading = false;
      }
    });
  }

  private calculateStats(): void {
    this.totalSeries = this.allSeries.length;
    this.totalVolumes = this.allSeries.length;
    this.ownedVolumes = this.allSeries.length;
    this.libraryValue = 0;
  }

  private applyFilters(): void {
    let filtered = [...this.allSeries];

    if (this.contentTypeFilter) {
      filtered = filtered.filter(s => s.type === this.contentTypeFilter);
    }

    this.filteredSeries = filtered;
  }

  onFilterChange(): void {
    this.applyFilters();
  }

  applyFiltersPublic(): void {
    this.applyFilters();
  }

  openModal(series: Series): void {
    this.selectedSeries = series;
    this.showModal = true;
  }

  closeModal(): void {
    this.showModal = false;
    this.selectedSeries = null;
  }

  viewSeries(series: Series): void {
    // Navigate to series details page
    // This would typically use Angular Router to navigate to /series/:id
    console.log('View series:', series.name, 'ID:', series.id);
    // For now, just open the modal
    this.openModal(series);
  }
}
