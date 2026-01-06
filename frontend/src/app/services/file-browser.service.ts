import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface FolderItem {
  name: string;
  path: string;
  // Backend API only returns name and path for folders
  // is_directory is implied since this is a folder browser
  size?: number;
  modified?: string;
}

export interface BrowseResponse {
  success: boolean;
  current_path: string;
  folders?: FolderItem[];
  files?: FolderItem[];
  drives?: string[];
  error?: string;
}

export interface BrowseRequest {
  path?: string;
}

@Injectable({
  providedIn: 'root'
})
export class FileBrowserService {
  private readonly apiUrl = `${environment.apiUrl}/folders/browse`;

  constructor(private http: HttpClient) {}

  browseFolders(request: BrowseRequest = {}): Observable<BrowseResponse> {
    return this.http.post<BrowseResponse>(this.apiUrl, request).pipe(
      catchError(this.handleError)
    );
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An error occurred while browsing folders';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      errorMessage = error.error?.error || errorMessage;
    }
    
    console.error('FileBrowserService error:', error);
    return throwError(() => errorMessage);
  }
}
