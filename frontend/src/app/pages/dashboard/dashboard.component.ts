import { Component, OnInit } from '@angular/core';

import { LoadingSpinnerComponent } from '../../components/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../components/error-message/error-message.component';
import { StatCardsSectionComponent, DashboardStats } from '../../components/dashboard/stat-cards-section/stat-cards-section.component';
import { RecentSeriesSectionComponent } from '../../components/dashboard/recent-series-section/recent-series-section.component';
import { UpcomingReleasesSectionComponent } from '../../components/dashboard/upcoming-releases-section/upcoming-releases-section.component';
import { CollectionStatsSectionComponent, CollectionStatsData } from '../../components/dashboard/collection-stats-section/collection-stats-section.component';
import { SeriesService } from '../../services/series.service';
import { CollectionService } from '../../services/collection.service';
import { AuthorService } from '../../services/author.service';
import { CalendarService } from '../../services/calendar.service';
import { NotificationService } from '../../services/notification.service';
import { Series } from '../../models/series.model';
import { CalendarEvent } from '../../models/calendar.model';

@Component({
    selector: 'app-dashboard',
    imports: [
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    StatCardsSectionComponent,
    RecentSeriesSectionComponent,
    UpcomingReleasesSectionComponent,
    CollectionStatsSectionComponent
],
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  title = 'Dashboard';
  isLoading = true;
  error: string | null = null;

  stats: DashboardStats = {
    totalSeries: 0,
    totalBooks: 0,
    totalAuthors: 0,
    todayReleases: 0
  };

  recentSeries: Series[] = [];
  upcomingReleases: CalendarEvent[] = [];
  collectionStats: CollectionStatsData = {
    ownedVolumes: 386,
    readVolumes: 0,
    readingProgress: 0,
    collectionValue: 0
  };

  constructor(
    private seriesService: SeriesService,
    private collectionService: CollectionService,
    private authorService: AuthorService,
    private calendarService: CalendarService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadDashboardData();
  }

  private loadDashboardData(): void {
    this.isLoading = true;
    this.error = null;

    Promise.all([
      this.loadSeriesStats(),
      this.loadAuthorsStats(),
      this.loadRecentSeries(),
      this.loadUpcomingReleases()
    ]).then(() => {
      this.isLoading = false;
    }).catch(err => {
      this.error = 'Failed to load dashboard data';
      this.notificationService.error('Failed to load dashboard data');
      this.isLoading = false;
    });
  }

  private loadSeriesStats(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.seriesService.getSeries().subscribe({
        next: (series) => {
          this.stats.totalSeries = series.length;
          this.stats.totalBooks = series.filter(s => s.type === 'book').length;
          resolve();
        },
        error: (err) => reject(err)
      });
    });
  }

  private loadAuthorsStats(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.authorService.getAuthors().subscribe({
        next: (authors) => {
          this.stats.totalAuthors = authors.length;
          resolve();
        },
        error: (err) => reject(err)
      });
    });
  }

  private loadRecentSeries(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.seriesService.getSeries({ limit: 6 }).subscribe({
        next: (series) => {
          this.recentSeries = series.slice(0, 6);
          resolve();
        },
        error: (err) => reject(err)
      });
    });
  }

  private loadUpcomingReleases(): Promise<void> {
    return new Promise((resolve, reject) => {
      const today = new Date().toISOString().split('T')[0];
      const nextWeek = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

      this.calendarService.getEventsByDateRange(today, nextWeek).subscribe({
        next: (events) => {
          this.upcomingReleases = events;
          this.stats.todayReleases = events.filter(e => e.releaseDate === today).length;
          resolve();
        },
        error: (err) => reject(err)
      });
    });
  }
}
