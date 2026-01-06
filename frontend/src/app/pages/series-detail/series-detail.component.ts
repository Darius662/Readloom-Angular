import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatTabsModule } from '@angular/material/tabs';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';
import { LoadingSpinnerComponent } from '../../components/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../components/error-message/error-message.component';
import { SeriesService } from '../../services/series.service';
import { NotificationService } from '../../services/notification.service';
import { ModalService } from '../../services/modal.service';
import { MangaPrepopulationService } from '../../services/manga-prepopulation.service';
import { Series, Chapter, Volume, Release } from '../../models/series.model';
import { Subscription } from 'rxjs';

@Component({
    selector: 'app-series-detail',
    imports: [CommonModule, MatCardModule, MatButtonModule, MatTabsModule, MatIconModule, MatChipsModule, MatDividerModule, LoadingSpinnerComponent, ErrorMessageComponent],
    templateUrl: './series-detail.component.html',
    styleUrls: ['./series-detail.component.css']
})
export class SeriesDetailComponent implements OnInit, OnDestroy {
  isLoading = true;
  error: string | null = null;

  series: Series | null = null;
  chapters: Chapter[] = [];
  volumes: Volume[] = [];

  activeTab = 'chapters';
  showEbookSection = false;
  isPrepopulating = false;
  isScanningCovers = false;
  isScanningEbooks = false;

  private deleteModalSubscription: Subscription | null = null;

  constructor(
    private route: ActivatedRoute,
    public seriesService: SeriesService,
    private notificationService: NotificationService,
    private modalService: ModalService,
    private mangaPrepopulationService: MangaPrepopulationService
  ) {}

  ngOnInit(): void {
    console.log('SeriesDetailComponent initialized');
    this.loadSeriesDetail();
  }

  private loadSeriesDetail(): void {
    this.isLoading = true;
    this.error = null;

    const id = this.route.snapshot.paramMap.get('id');
    console.log('Loading series detail for ID:', id);
    if (!id) {
      this.error = 'Series ID not found';
      this.isLoading = false;
      return;
    }

    this.seriesService.getSeriesById(parseInt(id)).subscribe({
      next: (series) => {
        console.log('Series loaded:', series);
        this.series = series;
        this.loadRelatedData(parseInt(id));
      },
      error: (err) => {
        console.error('Failed to load series:', err);
        this.error = 'Failed to load series';
        this.notificationService.error('Failed to load series');
        this.isLoading = false;
      }
    });
  }

  private loadRelatedData(seriesId: number): void {
    Promise.all([
      this.loadChapters(seriesId),
      this.loadVolumes(seriesId)
    ]).then(() => {
      // Check if we need to prepopulate data
      if (this.shouldPrepopulate()) {
        this.prepopulateData();
      }
    }).catch(err => {
      console.error('Error loading series data:', err);
      this.error = 'Failed to load series data';
    }).finally(() => {
      this.isLoading = false;
    });
  }

  private shouldPrepopulate(): boolean {
    // Prepopulate if we have no volumes or chapters, and the series is a manga
    if (!this.series) return false;
    
    const isManga = this.series.type === 'manga' || this.series.type === 'manwa';
    const hasNoData = this.volumes.length === 0 && this.chapters.length === 0;
    
    console.log(`Should prepopulate check:`, {
      seriesId: this.series.id,
      seriesName: this.series.title || this.series.name,
      seriesType: this.series.type,
      isManga,
      hasNoData,
      volumesCount: this.volumes.length,
      chaptersCount: this.chapters.length
    });
    
    return isManga && hasNoData;
  }

  private prepopulateData(): void {
    if (!this.series) return;
    
    this.isPrepopulating = true;
    this.notificationService.info('Prepopulating volumes and chapters from MangaDex...');
    
    this.mangaPrepopulationService.triggerPrepopulation(this.series).subscribe({
      next: (result) => {
        this.volumes = result.volumes;
        this.chapters = result.chapters;
        
        if (result.volumes.length > 0 || result.chapters.length > 0) {
          this.notificationService.success(`Prepopulated and saved ${result.volumes.length} volumes and ${result.chapters.length} chapters`);
        } else {
          this.notificationService.warning('No data found on MangaDex for this series');
        }
        
        this.isPrepopulating = false;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error prepopulating data:', error);
        this.notificationService.error('Failed to prepopulate data from MangaDex');
        this.isPrepopulating = false;
        this.isLoading = false;
      }
    });
  }

  private loadChapters(seriesId: number): Promise<void> {
    return new Promise((resolve) => {
      console.log(`Loading chapters for series ${seriesId}`);
      this.seriesService.getChapters(seriesId).subscribe({
        next: (chapters) => {
          console.log(`Loaded ${chapters.length} chapters:`, chapters);
          this.chapters = chapters;
          resolve();
        },
        error: (error) => {
          console.error('Failed to load chapters:', error);
          resolve();
        }
      });
    });
  }

  private loadVolumes(seriesId: number): Promise<void> {
    return new Promise((resolve) => {
      console.log(`Loading volumes for series ${seriesId}`);
      this.seriesService.getVolumes(seriesId).subscribe({
        next: (volumes) => {
          console.log(`Loaded ${volumes.length} volumes:`, volumes);
          this.volumes = volumes;
          resolve();
        },
        error: (error) => {
          console.error('Failed to load volumes:', error);
          resolve();
        }
      });
    });
  }

  onAddToCollection(): void {
    this.notificationService.info('Add to collection feature coming soon');
  }

  onEditSeries(): void {
    if (!this.series) return;
    
    this.modalService.openModal({
      id: 'seriesModal',
      title: 'Edit Series',
      data: {
        seriesId: this.series.id,
        title: this.series.title || this.series.name, // Use title first, fallback to name
        author: this.series.author || '',
        publisher: this.series.publisher || '',
        contentType: this.series.type,
        status: this.series.status || '',
        description: this.series.description || '',
        coverUrl: this.series.cover_url || '',
        customPath: '',
        importFromCustomPath: false,
        contentTypes: ['MANGA', 'MANHWA', 'MANHUA', 'COMICS', 'NOVEL', 'BOOK']
      }
    });

    this.modalService.getModalResult('seriesModal').subscribe((result) => {
      if (result?.action === 'save') {
        this.loadSeriesDetail();
      }
    });
  }

  onMoveSeries(): void {
    if (!this.series) return;
    
    this.modalService.openModal({
      id: 'moveSeriesModal',
      title: 'Move Series',
      data: {
        seriesId: this.series.id,
        seriesTitle: this.series.name
      }
    });

    this.modalService.getModalResult('moveSeriesModal').subscribe((result) => {
      if (result?.action === 'move') {
        this.loadSeriesDetail();
      }
    });
  }

  onDeleteSeries(): void {
    if (!this.series) return;
    
    // Clean up any existing subscription
    if (this.deleteModalSubscription) {
      this.deleteModalSubscription.unsubscribe();
      this.deleteModalSubscription = null;
    }
    
    const seriesTitle = this.series.title || this.series.name;
    this.modalService.openModal({
      id: 'deleteConfirmationModal',
      title: 'Confirm Delete',
      data: { 
        message: `Are you sure you want to delete "${seriesTitle}"? This will permanently remove the series and all its volumes and chapters.`,
        showEbookCheckbox: true
      }
    });

    // Create new subscription and store it
    this.deleteModalSubscription = this.modalService.getModalResult('deleteConfirmationModal').subscribe((result) => {
      if (result?.action === 'confirm' && this.series) {
        const removeEbookFiles = result.data?.removeEbookFiles || false;
        
        this.seriesService.deleteSeries(this.series.id, removeEbookFiles).subscribe({
          next: (response) => {
            // Use the backend's response message if available, otherwise fallback to default
            const message = response?.message || `Series "${seriesTitle}" ${removeEbookFiles ? 'deleted (including e-book files)' : 'deleted'} successfully`;
            this.notificationService.success(message);
            // Navigate back to the series list or library
            // You might want to inject Router and navigate to /books or /manga
            window.history.back();
          },
          error: (err) => {
            console.error('Failed to delete series:', err);
            this.notificationService.error('Failed to delete series');
          }
        });
      }
      
      // Clean up subscription after use
      if (this.deleteModalSubscription) {
        this.deleteModalSubscription.unsubscribe();
        this.deleteModalSubscription = null;
      }
    });
  }

  onAddVolume(): void {
    if (!this.series) return;
    
    this.modalService.openModal({
      id: 'volumeModal',
      title: 'Add Volume',
      data: { seriesId: this.series.id }
    });

    this.modalService.getModalResult('volumeModal').subscribe((result) => {
      if (result?.action === 'save') {
        this.loadSeriesDetail();
      }
    });
  }

  onEditVolume(volume: Volume): void {
    if (!this.series) return;
    
    this.modalService.openModal({
      id: 'volumeModal',
      title: 'Edit Volume',
      data: {
        seriesId: this.series.id,
        volumeId: volume.id,
        number: volume.volume_number,
        title: volume.title,
        description: '',
        releaseDate: volume.release_date,
        coverUrl: ''
      }
    });

    this.modalService.getModalResult('volumeModal').subscribe((result) => {
      if (result?.action === 'save') {
        this.loadSeriesDetail();
      }
    });
  }

  onDeleteVolume(volume: Volume): void {
    this.modalService.confirmDelete(`Are you sure you want to delete volume ${volume.volume_number}?`).then((confirmed) => {
      if (confirmed) {
        // Delete volume from backend
      }
    });
  }

  onAddChapter(): void {
    if (!this.series) return;
    
    this.modalService.openModal({
      id: 'chapterModal',
      title: 'Add Chapter',
      data: {
        seriesId: this.series.id,
        volumes: this.volumes
      }
    });

    this.modalService.getModalResult('chapterModal').subscribe((result) => {
      if (result?.action === 'save') {
        this.loadSeriesDetail();
      }
    });
  }

  onEditChapter(chapter: Chapter): void {
    if (!this.series) return;
    
    this.modalService.openModal({
      id: 'chapterModal',
      title: 'Edit Chapter',
      data: {
        seriesId: this.series.id,
        chapterId: chapter.id,
        number: chapter.chapter_number,
        title: chapter.title,
        volumeId: null,
        description: '',
        releaseDate: chapter.release_date,
        status: 'RELEASED',
        readStatus: 'UNREAD',
        volumes: this.volumes
      }
    });

    this.modalService.getModalResult('chapterModal').subscribe((result) => {
      if (result?.action === 'save') {
        this.loadSeriesDetail();
      }
    });
  }

  onDeleteChapter(chapter: Chapter): void {
    this.modalService.confirmDelete(`Are you sure you want to delete chapter ${chapter.chapter_number}?`).then((confirmed) => {
      if (confirmed) {
        // Delete chapter from backend
      }
    });
  }

  setActiveTab(tab: string): void {
    this.activeTab = tab;
  }

  getTabIndex(): number {
    return this.activeTab === 'chapters' ? 0 : 1;
  }

  getStatusColor(): string {
    if (!this.series?.status) return 'primary';
    switch (this.series.status) {
      case 'ongoing': return 'primary';
      case 'completed': return 'accent';
      case 'hiatus': return 'warn';
      default: return 'primary';
    }
  }

  onImageError(event: any): void {
    // Set a default cover image when the image fails to load
    event.target.src = 'assets/images/default-volume-cover.png';
  }

  onImageLoad(event: any): void {
    // Image loaded successfully - you can add any logging here if needed
    console.log('Cover loaded successfully:', event.target.src);
  }

  onManualPrepopulate(): void {
    if (!this.series) return;
    
    this.isPrepopulating = true;
    this.notificationService.info('Manually fetching data from MangaDex...');
    
    this.mangaPrepopulationService.triggerPrepopulation(this.series).subscribe({
      next: (result) => {
        // Refresh the data from backend to get the saved volumes and chapters
        this.loadRelatedData(this.series!.id);
        
        if (result.volumes.length > 0 || result.chapters.length > 0) {
          this.notificationService.success(`Manually fetched and saved ${result.volumes.length} volumes and ${result.chapters.length} chapters`);
        } else {
          this.notificationService.warning('No data found on MangaDex for this series');
        }
        
        this.isPrepopulating = false;
      },
      error: (error) => {
        console.error('Error in manual prepopulation:', error);
        this.notificationService.error('Failed to fetch data from MangaDex');
        this.isPrepopulating = false;
      }
    });
  }

  // Helper methods
  getCoverUrl(coverUrl: string | null | undefined): string {
    if (!coverUrl) return '';
    if (coverUrl.startsWith('http')) return coverUrl;
    return `/api/books/cover/${coverUrl}`;
  }

  getSubjects(): string[] {
    if (!this.series?.subjects) return [];
    if (typeof this.series.subjects === 'string') {
      return this.series.subjects.split(',').map((s: string) => s.trim());
    }
    if (Array.isArray(this.series.subjects)) {
      return this.series.subjects.filter((s: string) => s);
    }
    return [];
  }

  getStatusClass(): string {
    if (!this.series?.status) return 'bg-secondary';
    switch (this.series.status.toLowerCase()) {
      case 'ongoing':
        return 'bg-success';
      case 'completed':
        return 'bg-primary';
      case 'hiatus':
        return 'bg-warning';
      default:
        return 'bg-secondary';
    }
  }

  // E-book Management
  toggleEbookSection(): void {
    this.showEbookSection = !this.showEbookSection;
  }

  scanForEbooks(): void {
    this.isScanningEbooks = true;
    this.notificationService.info('Scanning for e-books...');
    
    // Call the backend API to scan for e-books
    this.seriesService.scanForEbooks(this.series?.id).subscribe({
      next: (response: any) => {
        this.isScanningEbooks = false;
        
        if (response.success) {
          const stats = response.scan_result || response;
          const message = `Scan completed! Scanned ${stats.scanned} files, added ${stats.added} new e-books, skipped ${stats.skipped} files.`;
          this.notificationService.success(message);
          
          // Refresh the series data to show new e-books
          if (this.series) {
            this.loadSeriesDetail();
          }
        } else {
          const errorMsg = response.error || 'E-book scan failed';
          this.notificationService.error(errorMsg);
        }
      },
      error: (error) => {
        this.isScanningEbooks = false;
        console.error('Error scanning for e-books:', error);
        this.notificationService.error('Failed to scan for e-books');
      }
    });
  }

  openUploadModal(): void {
    this.notificationService.info('Upload e-book feature coming soon');
  }

  scanForCovers(): void {
    this.isScanningCovers = true;
    this.notificationService.info('Scanning for manual covers...');
    
    // Call the backend API to scan for covers
    this.seriesService.scanForCovers().subscribe({
      next: (response: any) => {
        this.isScanningCovers = false;
        
        if (response.success) {
          const results = response.results;
          const message = `Scan completed! Found ${results.covers_found} covers, linked ${results.covers_linked} new covers.`;
          this.notificationService.success(message);
          
          // Refresh the volumes to show new covers
          if (this.series) {
            this.loadVolumes(this.series.id);
          }
        } else {
          this.notificationService.error('Cover scan failed');
        }
      },
      error: (err: any) => {
        this.isScanningCovers = false;
        console.error('Error scanning for covers:', err);
        this.notificationService.error('Failed to scan for covers');
      }
    });
  }

  // Volume and Chapter Interactions
  checkForCovers(): void {
    this.scanForCovers();
  }

  onVolumeClick(volume: Volume): void {
    console.log('Volume clicked:', volume);
    // TODO: Navigate to volume reader or show volume details
    this.notificationService.info(`Opening Volume ${volume.volume_number}`);
  }

  onChapterClick(chapter: Chapter): void {
    console.log('Chapter clicked:', chapter);
    // TODO: Navigate to chapter reader or show chapter details
    this.notificationService.info(`Opening Chapter ${chapter.chapter_number}`);
  }

  getVolumeCoverUrl(volume: Volume): string | null {
    // First try local cover path
    if (volume.cover_path) {
      return `http://localhost:7227/api/cover-art/volume/${volume.id}`;
    }
    
    // Fallback to cover_url (MangaDex URL)
    if (volume.cover_url) {
      return volume.cover_url;
    }
    
    // No cover available
    return null;
  }

  ngOnDestroy(): void {
    // Clean up modal subscription to prevent memory leaks
    if (this.deleteModalSubscription) {
      this.deleteModalSubscription.unsubscribe();
      this.deleteModalSubscription = null;
    }
  }
}
