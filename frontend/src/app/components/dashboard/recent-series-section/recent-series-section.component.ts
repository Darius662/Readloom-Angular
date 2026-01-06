import { Component, Input } from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { SeriesCardComponent } from '../../series-card/series-card.component';
import { Series } from '../../../models/series.model';

@Component({
    selector: 'app-recent-series-section',
    imports: [MatCardModule, MatButtonModule, MatIconModule, SeriesCardComponent],
    templateUrl: './recent-series-section.component.html',
    styleUrls: ['./recent-series-section.component.css']
})
export class RecentSeriesSectionComponent {
  @Input() series: Series[] = [];
}
