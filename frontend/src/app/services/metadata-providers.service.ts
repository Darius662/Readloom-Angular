import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface MetadataProvider {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  apiKey?: string;
  apiUrl?: string;
  priority: number;
}

@Injectable({
  providedIn: 'root'
})
export class MetadataProvidersService {
  private apiUrl = `${environment.apiUrl}/metadata`;

  constructor(private http: HttpClient) {}

  /**
   * Get all metadata providers
   */
  getProviders(): Observable<any> {
    return this.http.get(`${this.apiUrl}/providers`);
  }

  /**
   * Update a metadata provider configuration
   */
  updateProvider(name: string, enabled: boolean, settings: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/providers/${name}`, {
      enabled,
      settings
    });
  }

  /**
   * Save all metadata provider configurations
   */
  saveProviders(providers: MetadataProvider[]): Observable<any> {
    const updatePromises = providers.map(provider => {
      const settings: any = {};
      
      if (provider.apiKey) {
        settings.apiKey = provider.apiKey;
      }
      if (provider.apiUrl) {
        settings.apiUrl = provider.apiUrl;
      }
      if (provider.priority) {
        settings.priority = provider.priority;
      }

      return this.updateProvider(provider.name, provider.enabled, settings).toPromise();
    });

    return new Observable(observer => {
      Promise.all(updatePromises)
        .then(results => {
          observer.next({
            success: true,
            message: 'All providers updated successfully',
            results
          });
          observer.complete();
        })
        .catch(error => {
          observer.error({
            success: false,
            message: 'Failed to update providers',
            error
          });
        });
    });
  }
}
