import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

export interface LibraryFilters {
  searchQuery: string;
  selectedType: string;
  sortBy: string;
}

@Component({
    selector: 'app-search-filter-section',
    imports: [CommonModule, FormsModule],
    templateUrl: './search-filter-section.component.html',
    styleUrls: ['./search-filter-section.component.css']
})
export class SearchFilterSectionComponent {
  @Output() filtersChanged = new EventEmitter<LibraryFilters>();

  searchQuery = '';
  selectedType = '';
  sortBy = 'name';

  types = ['manga', 'manwa', 'comic', 'book'];
  sortOptions = [
    { value: 'name', label: 'Name (A-Z)' },
    { value: 'rating', label: 'Rating (High to Low)' },
    { value: 'updated', label: 'Recently Updated' }
  ];

  onSearch(): void {
    this.emitFilters();
  }

  onTypeChange(): void {
    this.emitFilters();
  }

  onSortChange(): void {
    this.emitFilters();
  }

  private emitFilters(): void {
    this.filtersChanged.emit({
      searchQuery: this.searchQuery,
      selectedType: this.selectedType,
      sortBy: this.sortBy
    });
  }
}
