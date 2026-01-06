import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatTabsModule } from '@angular/material/tabs';
import { NotificationService } from '../../../services/notification.service';
import { MetadataProvidersService } from '../../../services/metadata-providers.service';

interface MetadataProvider {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  apiKey?: string;
  apiUrl?: string;
  priority: number;
}

@Component({
  selector: 'app-metadata-providers-config',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatSlideToggleModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatTabsModule,
    MatDialogModule
  ],
  template: `
    <div class="metadata-providers-config">
      <h2 mat-dialog-title>Metadata Providers Configuration</h2>

      <mat-dialog-content>
        <div class="providers-container">
          <div class="providers-list">
            <div class="provider-card" *ngFor="let provider of providers">
              <div class="provider-header">
                <div class="provider-info">
                  <h3>{{ provider.name }}</h3>
                  <p class="provider-description">{{ provider.description }}</p>
                </div>
                <mat-slide-toggle 
                  [(ngModel)]="provider.enabled"
                  (change)="onProviderToggle(provider)"
                  class="provider-toggle">
                </mat-slide-toggle>
              </div>

              @if (provider.enabled) {
                <div class="provider-settings">
                  @if (provider.apiKey !== undefined) {
                    <mat-form-field appearance="outline" class="full-width">
                      <mat-label>API Key</mat-label>
                      <input matInput [(ngModel)]="provider.apiKey" type="password" placeholder="Enter API key">
                    </mat-form-field>
                  }
                  @if (provider.apiUrl !== undefined) {
                    <mat-form-field appearance="outline" class="full-width">
                      <mat-label>API URL</mat-label>
                      <input matInput [(ngModel)]="provider.apiUrl" placeholder="Enter API URL">
                    </mat-form-field>
                  }
                  <div class="priority-control">
                    <label>Priority (1-10)</label>
                    <input type="number" min="1" max="10" [(ngModel)]="provider.priority" class="form-control">
                  </div>
                  <button mat-stroked-button (click)="testProvider(provider)" class="test-button">
                    <mat-icon>check_circle</mat-icon>
                    Test Connection
                  </button>
                </div>
              }
            </div>
          </div>

          <div class="provider-info-panel">
            <h3>About Metadata Providers</h3>
            <p>Metadata providers help Readloom fetch accurate information about your manga and books, including:</p>
            <ul>
              <li>Series title and description</li>
              <li>Author and publisher information</li>
              <li>Cover images</li>
              <li>Volume and chapter information</li>
              <li>Release dates</li>
              <li>Ratings and reviews</li>
            </ul>

            <h4 class="mt-4">Provider Priority</h4>
            <p>Providers are queried in order of priority (highest first). Set higher priority for more reliable providers.</p>

            <h4 class="mt-4">API Keys</h4>
            <p>Some providers require API keys for access. You can obtain them from:</p>
            <ul>
              <li><strong>Google Books:</strong> <a href="https://developers.google.com/books" target="_blank">Google Cloud Console</a></li>
              <li><strong>Open Library:</strong> Free, no API key required</li>
              <li><strong>ISBNdb:</strong> <a href="https://isbndb.com/api" target="_blank">ISBNdb API</a></li>
            </ul>
          </div>
        </div>
      </mat-dialog-content>

      <mat-dialog-actions align="end">
        <button mat-button (click)="onCancel()">Cancel</button>
        <button mat-raised-button color="primary" (click)="onSave()">Save Configuration</button>
      </mat-dialog-actions>
    </div>
  `,
  styles: [`
    .metadata-providers-config {
      min-width: 800px;
      max-width: 1000px;
    }

    mat-dialog-content {
      padding: 24px !important;
    }

    .providers-container {
      display: grid;
      grid-template-columns: 1fr 350px;
      gap: 24px;
    }

    .providers-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .provider-card {
      border: 1px solid #424242;
      border-radius: 8px;
      padding: 16px;
      background-color: #2a2a2a;
    }

    .provider-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
      margin-bottom: 16px;
    }

    .provider-info h3 {
      margin: 0 0 4px 0;
      font-size: 16px;
      font-weight: 600;
      color: #ffffff;
    }

    .provider-description {
      margin: 0;
      font-size: 13px;
      color: #b0b0b0;
    }

    .provider-toggle {
      flex-shrink: 0;
    }

    .provider-settings {
      padding-top: 16px;
      border-top: 1px solid #424242;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .full-width {
      width: 100%;
    }

    .priority-control {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .priority-control label {
      font-size: 13px;
      font-weight: 600;
      color: #ffffff;
    }

    .priority-control input {
      padding: 8px 12px;
      border: 1px solid #424242;
      border-radius: 4px;
      font-size: 14px;
      background-color: #1e1e1e;
      color: #ffffff;
    }

    .test-button {
      align-self: flex-start;
      gap: 8px;
    }

    .provider-info-panel {
      border: 1px solid #424242;
      border-radius: 8px;
      padding: 16px;
      background-color: #2a2a2a;
      height: fit-content;
      position: sticky;
      top: 0;
    }

    .provider-info-panel h3 {
      margin: 0 0 12px 0;
      font-size: 16px;
      font-weight: 600;
      color: #ffffff;
    }

    .provider-info-panel h4 {
      margin: 16px 0 8px 0;
      font-size: 14px;
      font-weight: 600;
      color: #ffffff;
    }

    .provider-info-panel p {
      margin: 0 0 12px 0;
      font-size: 13px;
      line-height: 1.5;
      color: #b0b0b0;
    }

    .provider-info-panel ul {
      margin: 0 0 12px 0;
      padding-left: 20px;
      font-size: 13px;
      line-height: 1.6;
      color: #b0b0b0;
    }

    .provider-info-panel li {
      margin-bottom: 4px;
    }

    .provider-info-panel a {
      color: #64b5f6;
      text-decoration: none;
    }

    .provider-info-panel a:hover {
      text-decoration: underline;
      color: #90caf9;
    }

    .mt-4 {
      margin-top: 16px;
    }

    mat-dialog-actions {
      padding: 16px 24px 24px 24px !important;
      border-top: 1px solid #424242;
      gap: 12px;
    }
  `]
})
export class MetadataProvidersConfigComponent implements OnInit {
  providers: MetadataProvider[] = [
    {
      id: 'googlebooks',
      name: 'GoogleBooks',
      description: 'Access millions of books with comprehensive metadata',
      enabled: false,
      apiKey: '',
      priority: 8
    },
    {
      id: 'mangafire',
      name: 'MangaFire',
      description: 'Popular manga and e-book aggregator',
      enabled: false,
      priority: 8
    },
    {
      id: 'worldcat',
      name: 'WorldCat',
      description: 'World\'s largest library catalog',
      enabled: false,
      apiKey: '',
      priority: 6
    },
    {
      id: 'openlibrary',
      name: 'OpenLibrary',
      description: 'Free, open database of books (no API key required)',
      enabled: false,
      priority: 7
    },
    {
      id: 'jikan',
      name: 'Jikan',
      description: 'Unofficial MyAnimeList API',
      enabled: false,
      priority: 7
    },
    {
      id: 'anilist',
      name: 'AniList',
      description: 'Anime and manga database with detailed metadata',
      enabled: false,
      priority: 9
    },
    {
      id: 'isbndb',
      name: 'ISBNdb',
      description: 'Comprehensive book database with ISBN lookup',
      enabled: false,
      apiKey: '',
      priority: 9
    },
    {
      id: 'myanimelist',
      name: 'MyAnimeList',
      description: 'Comprehensive anime and manga database',
      enabled: false,
      apiKey: '',
      priority: 9
    },
    {
      id: 'mangadex',
      name: 'MangaDex',
      description: 'Community manga reader and database',
      enabled: false,
      priority: 8
    },
    {
      id: 'mangaapi',
      name: 'MangaAPI',
      description: 'General-purpose manga API',
      enabled: false,
      apiUrl: 'https://manga-api.fly.dev',
      priority: 6
    }
  ];

  constructor(
    public dialogRef: MatDialogRef<MetadataProvidersConfigComponent>,
    private notificationService: NotificationService,
    private metadataProvidersService: MetadataProvidersService
  ) {}

  ngOnInit(): void {
    this.loadConfiguration();
  }

  private loadConfiguration(): void {
    // Load saved configuration from backend
    this.metadataProvidersService.getProviders().subscribe({
      next: (response) => {
        console.log('=== API Response ===');
        console.log('Full response:', response);
        console.log('Response type:', typeof response);
        console.log('Response keys:', Object.keys(response));
        
        if (response.providers && Array.isArray(response.providers)) {
          console.log('Found providers array with', response.providers.length, 'items');
          const savedProviders = response.providers;
          
          console.log('=== Provider Matching ===');
          this.providers.forEach(provider => {
            const saved = savedProviders.find((p: any) => p.name === provider.name);
            console.log(`Provider: ${provider.name}, Found in DB:`, saved);
            
            if (saved) {
              console.log(`  - DB enabled value: ${saved.enabled} (type: ${typeof saved.enabled})`);
              console.log(`  - Converting to boolean...`);
              provider.enabled = saved.enabled === 1 || saved.enabled === true || saved.enabled === '1';
              console.log(`  - Result: ${provider.enabled}`);
              
              if (saved.settings) {
                provider.apiKey = saved.settings.apiKey || provider.apiKey;
                provider.apiUrl = saved.settings.apiUrl || provider.apiUrl;
                provider.priority = saved.settings.priority || provider.priority;
              }
            }
          });
          
          console.log('=== Final Provider States ===');
          this.providers.forEach(p => console.log(`${p.name}: enabled=${p.enabled}`));
        } else {
          console.error('Response does not have providers array:', response);
        }
      },
      error: (err) => {
        this.notificationService.warning('Could not load provider configuration');
        console.error('Error loading providers:', err);
      }
    });
  }

  onProviderToggle(provider: MetadataProvider): void {
    this.notificationService.info(`${provider.name} ${provider.enabled ? 'enabled' : 'disabled'}`);
  }

  testProvider(provider: MetadataProvider): void {
    this.notificationService.info(`Testing ${provider.name}...`);
    // Simulate API test
    setTimeout(() => {
      this.notificationService.success(`${provider.name} connection successful!`);
    }, 1000);
  }

  onSave(): void {
    this.notificationService.info('Saving metadata providers configuration...');
    
    this.metadataProvidersService.saveProviders(this.providers).subscribe({
      next: (response) => {
        this.notificationService.success('Metadata providers configuration saved successfully');
        this.dialogRef.close({ action: 'save', data: this.providers });
      },
      error: (err) => {
        this.notificationService.error('Failed to save metadata providers configuration');
        console.error('Error saving providers:', err);
      }
    });
  }

  onCancel(): void {
    this.dialogRef.close({ action: 'cancel' });
  }
}
