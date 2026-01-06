import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';

export interface CollectionStatsData {
  ownedVolumes: number;
  readVolumes: number;
  readingProgress: number;
  collectionValue: number;
}

@Component({
    selector: 'app-collection-stats-section',
    imports: [
      CommonModule, 
      MatCardModule, 
      MatProgressBarModule, 
      MatIconModule,
      MatButtonModule,
      MatDividerModule
    ],
    templateUrl: './collection-stats-section.component.html',
    styleUrls: ['./collection-stats-section.component.css']
})
export class CollectionStatsSectionComponent {
  @Input() stats: CollectionStatsData = {
    ownedVolumes: 386,
    readVolumes: 0,
    readingProgress: 0,
    collectionValue: 0
  };
}
