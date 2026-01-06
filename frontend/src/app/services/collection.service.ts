import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap, map } from 'rxjs/operators';
import { ApiService } from './api.service';
import { Collection, CollectionItem, CollectionStats } from '../models/collection.model';

@Injectable({
  providedIn: 'root'
})
export class CollectionService {
  private collections$ = new BehaviorSubject<Collection[]>([]);
  private selectedCollection$ = new BehaviorSubject<Collection | null>(null);

  constructor(private api: ApiService) {}

  /**
   * Get all collections
   */
  getCollections(): Observable<Collection[]> {
    return this.api.get<{ success: boolean; collections: Collection[] }>('/collections')
      .pipe(
        map(response => response.collections || []),
        tap(collections => this.collections$.next(collections))
      );
  }

  /**
   * Get collection by ID
   */
  getCollectionById(id: number): Observable<Collection> {
    return this.api.get<{ success: boolean; collection: Collection }>(`/collections/${id}`)
      .pipe(
        map(response => response.collection),
        tap(collection => {
          if (collection) {
            this.selectedCollection$.next(collection);
          }
        })
      );
  }

  /**
   * Create new collection
   */
  createCollection(data: Partial<Collection>): Observable<Collection> {
    return this.api.post<{ success: boolean; collection: Collection }>('/collections', data)
      .pipe(
        map(response => response.collection),
        tap(collection => {
          if (collection) {
            const current = this.collections$.value;
            this.collections$.next([...current, collection]);
          }
        })
      );
  }

  /**
   * Update collection
   */
  updateCollection(id: number, data: Partial<Collection>): Observable<Collection> {
    return this.api.put<{ success: boolean; collection: Collection }>(`/collections/${id}`, data)
      .pipe(
        map(response => response.collection),
        tap(collection => {
          if (collection) {
            const current = this.collections$.value;
            const index = current.findIndex(c => c.id === id);
            if (index > -1) {
              current[index] = collection;
              this.collections$.next([...current]);
            }
            if (this.selectedCollection$.value?.id === id) {
              this.selectedCollection$.next(collection);
            }
          }
        })
      );
  }

  /**
   * Delete collection
   */
  deleteCollection(id: number): Observable<any> {
    return this.api.delete(`/collections/${id}`)
      .pipe(tap(() => {
        const current = this.collections$.value;
        this.collections$.next(current.filter(c => c.id !== id));
      }));
  }

  /**
   * Get collections observable
   */
  getCollectionsList(): Observable<Collection[]> {
    return this.collections$.asObservable();
  }

  /**
   * Get selected collection observable
   */
  getSelectedCollection(): Observable<Collection | null> {
    return this.selectedCollection$.asObservable();
  }

  /**
   * Get collection items
   */
  getCollectionItems(collectionId: number): Observable<CollectionItem[]> {
    return this.api.get<{ success: boolean; series: CollectionItem[] }>(`/collections/${collectionId}/series`)
      .pipe(map(response => response.series || []));
  }

  /**
   * Add series to collection
   */
  addToCollection(collectionId: number, seriesId: number, data?: Partial<CollectionItem>): Observable<any> {
    return this.api.post<any>(`/collections/${collectionId}/series/${seriesId}`, data || {});
  }

  /**
   * Remove series from collection
   */
  removeFromCollection(collectionId: number, seriesId: number): Observable<any> {
    return this.api.delete(`/collections/${collectionId}/series/${seriesId}`);
  }

  /**
   * Update collection item
   */
  updateCollectionItem(collectionId: number, itemId: number, data: Partial<CollectionItem>): Observable<any> {
    return this.api.put<any>(`/collections/${collectionId}/items/${itemId}`, data);
  }

  /**
   * Get collection statistics
   */
  getCollectionStats(collectionId: number): Observable<CollectionStats> {
    return this.api.get<{ success: boolean; stats: CollectionStats }>(`/collections/${collectionId}/stats`)
      .pipe(map(response => response.stats));
  }

  /**
   * Get collection root folders
   */
  getCollectionRootFolders(collectionId: number): Observable<any[]> {
    return this.api.get<{ success: boolean; root_folders: any[] }>(`/collections/${collectionId}/root-folders`)
      .pipe(map(response => response.root_folders || []));
  }

  /**
   * Get series in collection
   */
  getCollectionSeries(collectionId: number): Observable<any[]> {
    return this.api.get<{ success: boolean; series: any[] }>(`/collections/${collectionId}/series`)
      .pipe(map(response => response.series || []));
  }

  /**
   * Add root folder to collection
   */
  addRootFolderToCollection(collectionId: number, rootFolderId: number): Observable<any> {
    return this.api.post<any>(`/collections/${collectionId}/root-folders/${rootFolderId}`, {});
  }

  /**
   * Link root folder to collection
   */
  linkRootFolder(collectionId: number, rootFolderId: number): Observable<any> {
    return this.addRootFolderToCollection(collectionId, rootFolderId);
  }

  /**
   * Remove root folder from collection
   */
  removeRootFolderFromCollection(collectionId: number, rootFolderId: number): Observable<any> {
    return this.api.delete(`/collections/${collectionId}/root-folders/${rootFolderId}`);
  }

  /**
   * Unlink root folder from collection
   */
  unlinkRootFolder(collectionId: number, rootFolderId: number): Observable<any> {
    return this.removeRootFolderFromCollection(collectionId, rootFolderId);
  }
}
