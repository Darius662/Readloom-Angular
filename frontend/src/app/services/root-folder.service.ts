import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap, map } from 'rxjs/operators';
import { ApiService } from './api.service';

export interface RootFolder {
  id: number;
  name: string;
  path: string;
  content_type: string;
  created_at?: string;
  updated_at?: string;
}

@Injectable({
  providedIn: 'root'
})
export class RootFolderService {
  private rootFolders$ = new BehaviorSubject<RootFolder[]>([]);

  constructor(private api: ApiService) {}

  /**
   * Get all root folders
   */
  getRootFolders(): Observable<RootFolder[]> {
    return this.api.get<{ success: boolean; root_folders: RootFolder[] }>('/root-folders')
      .pipe(
        map(response => response.root_folders || []),
        tap(rootFolders => this.rootFolders$.next(rootFolders))
      );
  }

  /**
   * Get root folder by ID
   */
  getRootFolderById(id: number): Observable<RootFolder> {
    return this.api.get<{ success: boolean; root_folder: RootFolder }>(`/root-folders/${id}`)
      .pipe(
        map(response => response.root_folder),
        tap(rootFolder => {
          if (rootFolder) {
            const current = this.rootFolders$.value;
            const index = current.findIndex(rf => rf.id === id);
            if (index > -1) {
              current[index] = rootFolder;
            } else {
              current.push(rootFolder);
            }
            this.rootFolders$.next([...current]);
          }
        })
      );
  }

  /**
   * Create new root folder
   */
  createRootFolder(data: Partial<RootFolder>): Observable<RootFolder> {
    return this.api.post<{ success: boolean; root_folder: RootFolder }>('/root-folders', data)
      .pipe(
        map(response => response.root_folder),
        tap(rootFolder => {
          if (rootFolder) {
            const current = this.rootFolders$.value;
            this.rootFolders$.next([...current, rootFolder]);
          }
        })
      );
  }

  /**
   * Update root folder
   */
  updateRootFolder(id: number, data: Partial<RootFolder>): Observable<RootFolder> {
    return this.api.put<{ success: boolean; root_folder: RootFolder }>(`/root-folders/${id}`, data)
      .pipe(
        map(response => response.root_folder),
        tap(rootFolder => {
          if (rootFolder) {
            const current = this.rootFolders$.value;
            const index = current.findIndex(rf => rf.id === id);
            if (index > -1) {
              current[index] = rootFolder;
              this.rootFolders$.next([...current]);
            }
          }
        })
      );
  }

  /**
   * Delete root folder
   */
  deleteRootFolder(id: number): Observable<any> {
    return this.api.delete(`/root-folders/${id}`)
      .pipe(
        tap(() => {
          const current = this.rootFolders$.value;
          this.rootFolders$.next(current.filter(rf => rf.id !== id));
        })
      );
  }

  /**
   * Get root folders observable
   */
  getRootFoldersList(): Observable<RootFolder[]> {
    return this.rootFolders$.asObservable();
  }
}
