import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject, of } from 'rxjs';
import { tap, delay, map } from 'rxjs/operators';
import { ApiService } from './api.service';
import { MockDataService } from './mock-data.service';
import { Author, AuthorMetadata } from '../models/author.model';

@Injectable({
  providedIn: 'root'
})
export class AuthorService {
  private authors$ = new BehaviorSubject<Author[]>([]);
  private selectedAuthor$ = new BehaviorSubject<Author | null>(null);

  constructor(private api: ApiService, private mockData: MockDataService) {}

  /**
   * Get all authors
   */
  getAuthors(params?: any): Observable<Author[]> {
    return this.api.get<{ success: boolean; authors: Author[] }>('/authors')
      .pipe(
        map(response => response.authors || []),
        tap(authors => this.authors$.next(authors))
      );
  }

  /**
   * Get author by ID
   */
  getAuthorById(id: number): Observable<Author> {
    return this.api.get<Author>(`/authors/${id}`)
      .pipe(tap(author => this.selectedAuthor$.next(author)));
  }

  /**
   * Create new author
   */
  createAuthor(data: Partial<Author>): Observable<Author> {
    return this.api.post<Author>('/authors', data)
      .pipe(tap(author => {
        const current = this.authors$.value;
        this.authors$.next([...current, author]);
      }));
  }

  /**
   * Update author
   */
  updateAuthor(id: number, data: Partial<Author>): Observable<Author> {
    return this.api.put<Author>(`/authors/${id}`, data)
      .pipe(tap(author => {
        const current = this.authors$.value;
        const index = current.findIndex(a => a.id === id);
        if (index > -1) {
          current[index] = author;
          this.authors$.next([...current]);
        }
        if (this.selectedAuthor$.value?.id === id) {
          this.selectedAuthor$.next(author);
        }
      }));
  }

  /**
   * Delete author
   */
  deleteAuthor(id: number): Observable<any> {
    return this.api.delete(`/authors/${id}`)
      .pipe(tap(() => {
        const current = this.authors$.value;
        this.authors$.next(current.filter(a => a.id !== id));
      }));
  }

  /**
   * Get authors observable
   */
  getAuthorsList(): Observable<Author[]> {
    return this.authors$.asObservable();
  }

  /**
   * Get selected author observable
   */
  getSelectedAuthor(): Observable<Author | null> {
    return this.selectedAuthor$.asObservable();
  }

  /**
   * Get author metadata
   */
  getAuthorMetadata(id: number): Observable<AuthorMetadata> {
    return this.api.get<AuthorMetadata>(`/authors/${id}/metadata`);
  }

  /**
   * Search authors
   */
  searchAuthors(query: string): Observable<Author[]> {
    return this.api.get<Author[]>('/authors/search', { q: query });
  }
}
