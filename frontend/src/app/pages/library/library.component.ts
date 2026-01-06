import { Component, OnInit } from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { LoadingSpinnerComponent } from '../../components/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../components/error-message/error-message.component';
import { SearchFilterSectionComponent, LibraryFilters } from '../../components/library/search-filter-section/search-filter-section.component';
import { SeriesGridSectionComponent } from '../../components/library/series-grid-section/series-grid-section.component';
import { SeriesService } from '../../services/series.service';
import { NotificationService } from '../../services/notification.service';
import { Series } from '../../models/series.model';

@Component({
    selector: 'app-library',
    imports: [
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    SearchFilterSectionComponent,
    SeriesGridSectionComponent
],
    templateUrl: './library.component.html',
    styleUrls: ['./library.component.css']
})
export class LibraryComponent implements OnInit {
  title = 'Library';
  isLoading = true;
  error: string | null = null;

  allSeries: Series[] = [];
  filteredSeries: Series[] = [];

  searchQuery = '';
  selectedType = '';
  sortBy = 'name';

  constructor(
    private seriesService: SeriesService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadSeries();
  }

  private loadSeries(): void {
    this.isLoading = true;
    this.error = null;

    this.seriesService.getSeries().subscribe({
      next: (series) => {
        this.allSeries = series;
        this.applyFilters();
        this.isLoading = false;
      },
      error: (err) => {
        this.error = 'Failed to load series';
        this.notificationService.error('Failed to load series');
        this.isLoading = false;
      }
    });
  }

  onFiltersChanged(filters: LibraryFilters): void {
    this.searchQuery = filters.searchQuery;
    this.selectedType = filters.selectedType;
    this.sortBy = filters.sortBy;
    this.applyFilters();
  }

  private applyFilters(): void {
    let filtered = [...this.allSeries];

    // Filter by search query
    if (this.searchQuery.trim()) {
      const query = this.searchQuery.toLowerCase();
      filtered = filtered.filter(s => s.name.toLowerCase().includes(query));
    }

    // Filter by type
    if (this.selectedType) {
      filtered = filtered.filter(s => s.type === this.selectedType);
    }

    // Sort
    switch (this.sortBy) {
      case 'rating':
        filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
        break;
      case 'updated':
        filtered.sort((a, b) => {
          const dateA = new Date(a.updated_at || 0).getTime();
          const dateB = new Date(b.updated_at || 0).getTime();
          return dateB - dateA;
        });
        break;
      case 'name':
      default:
        filtered.sort((a, b) => a.name.localeCompare(b.name));
    }

    this.filteredSeries = filtered;
  }

  get resultCount(): number {
    return this.filteredSeries.length;
  }
}
