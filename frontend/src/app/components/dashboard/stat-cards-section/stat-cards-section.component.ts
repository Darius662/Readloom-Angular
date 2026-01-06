import { Component, Input, OnInit } from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

export interface DashboardStats {
  totalSeries: number;
  totalBooks: number;
  totalAuthors: number;
  todayReleases: number;
}

@Component({
    selector: 'app-stat-cards-section',
    imports: [MatCardModule, MatIconModule],
    templateUrl: './stat-cards-section.component.html',
    styleUrls: ['./stat-cards-section.component.css']
})
export class StatCardsSectionComponent implements OnInit {
  @Input() stats!: DashboardStats;

  statCards: Array<{ label: string; value: number; icon: string; color: string }> = [
    { label: 'Manga Series', value: 0, icon: 'library_books', color: 'primary' },
    { label: 'Books', value: 0, icon: 'bookmark', color: 'success' },
    { label: 'Authors', value: 0, icon: 'person', color: 'info' },
    { label: "Today's Releases", value: 0, icon: 'calendar_today', color: 'warning' }
  ];

  ngOnInit(): void {
    if (this.stats) {
      this.statCards[0].value = this.stats.totalSeries;
      this.statCards[1].value = this.stats.totalBooks;
      this.statCards[2].value = this.stats.totalAuthors;
      this.statCards[3].value = this.stats.todayReleases;
    }
  }
}
