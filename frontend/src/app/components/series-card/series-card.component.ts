import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { Series } from '../../models/series.model';

@Component({
    selector: 'app-series-card',
    imports: [CommonModule, RouterModule, MatCardModule, MatIconModule, MatButtonModule, MatChipsModule],
    templateUrl: './series-card.component.html',
    styleUrls: ['./series-card.component.css']
})
export class SeriesCardComponent {
  @Input() series!: Series;

  constructor(private router: Router) {}

  navigateToSeries(): void {
    // Determine the correct route based on the series type
    const contentType = this.series.content_type || this.series.type || 'manga';
    const isBook = ['BOOK', 'NOVEL'].includes(contentType.toUpperCase());
    
    if (isBook) {
      // Books use /books/:id route
      this.router.navigate(['/books', this.series.id]);
    } else {
      // Manga uses /manga/series/:id route
      this.router.navigate(['/manga/series', this.series.id]);
    }
  }
}
