import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { LoadingSpinnerComponent } from '../../components/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../components/error-message/error-message.component';
import { CollectionService } from '../../services/collection.service';
import { NotificationService } from '../../services/notification.service';
import { Collection, CollectionItem, CollectionStats } from '../../models/collection.model';
import { Series } from '../../models/series.model';

@Component({
    selector: 'app-collection-detail',
    imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule, LoadingSpinnerComponent, ErrorMessageComponent],
    templateUrl: './collection-detail.component.html',
    styleUrls: ['./collection-detail.component.css']
})
export class CollectionDetailComponent implements OnInit {
  isLoading = true;
  error: string | null = null;

  collection: Collection | null = null;
  items: CollectionItem[] = [];
  stats: CollectionStats | null = null;
  series: Series[] = [];

  constructor(
    private route: ActivatedRoute,
    private collectionService: CollectionService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadCollectionDetail();
  }

  private loadCollectionDetail(): void {
    this.isLoading = true;
    this.error = null;

    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.error = 'Collection ID not found';
      this.isLoading = false;
      return;
    }

    this.collectionService.getCollectionById(parseInt(id)).subscribe({
      next: (collection) => {
        this.collection = collection;
        this.loadRelatedData(parseInt(id));
      },
      error: (err) => {
        this.error = 'Failed to load collection';
        this.notificationService.error('Failed to load collection');
        this.isLoading = false;
      }
    });
  }

  private loadRelatedData(collectionId: number): void {
    Promise.all([
      this.loadItems(collectionId),
      this.loadStats(collectionId)
    ]).then(() => {
      this.isLoading = false;
    }).catch(() => {
      this.isLoading = false;
    });
  }

  private loadItems(collectionId: number): Promise<void> {
    return new Promise((resolve) => {
      this.collectionService.getCollectionItems(collectionId).subscribe({
        next: (items) => {
          this.items = items;
          resolve();
        },
        error: () => resolve()
      });
    });
  }

  private loadStats(collectionId: number): Promise<void> {
    return new Promise((resolve) => {
      this.collectionService.getCollectionStats(collectionId).subscribe({
        next: (stats) => {
          this.stats = stats;
          resolve();
        },
        error: () => resolve()
      });
    });
  }

  onRemoveItem(item: CollectionItem): void {
    if (this.collection) {
      this.notificationService.info('Remove item feature coming soon');
    }
  }

  onEditCollection(): void {
    this.notificationService.info('Edit collection feature coming soon');
  }
}
