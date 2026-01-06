import { Component, Output, EventEmitter } from '@angular/core';

import { FormsModule } from '@angular/forms';

@Component({
    selector: 'app-author-search-section',
    imports: [FormsModule],
    templateUrl: './author-search-section.component.html',
    styleUrls: ['./author-search-section.component.css']
})
export class AuthorSearchSectionComponent {
  @Output() searchChanged = new EventEmitter<string>();

  searchQuery = '';

  onSearch(): void {
    this.searchChanged.emit(this.searchQuery);
  }
}
