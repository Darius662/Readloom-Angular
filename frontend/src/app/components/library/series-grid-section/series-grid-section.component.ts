import { Component, Input } from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { SeriesCardComponent } from '../../series-card/series-card.component';
import { Series } from '../../../models/series.model';

@Component({
    selector: 'app-series-grid-section',
    imports: [MatCardModule, MatButtonModule, MatIconModule, SeriesCardComponent],
    templateUrl: './series-grid-section.component.html',
    styleUrls: ['./series-grid-section.component.css']
})
export class SeriesGridSectionComponent {
  @Input() series: Series[] = [];
  @Input() resultCount = 0;
}
