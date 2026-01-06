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
import { MatSelectModule } from '@angular/material/select';
import { NotificationService } from '../../../services/notification.service';
import { AIProvidersService, AIProvider } from '../../../services/ai-providers.service';

@Component({
  selector: 'app-ai-providers-config',
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
    MatSelectModule,
    MatDialogModule
  ],
  template: `
    <div class="ai-providers-config">
      <h2 mat-dialog-title>AI Providers Configuration</h2>

      <mat-dialog-content>
        <div class="providers-container">
          <div class="providers-list">
            <div class="provider-card" *ngFor="let provider of providers">
              <div class="provider-header">
                <div class="provider-info">
                  <h3>{{ provider.name }}</h3>
                  <p class="provider-description">{{ provider.description }}</p>
                  <div class="provider-meta">
                    <span class="meta-item">
                      <mat-icon>schedule</mat-icon>
                      {{ provider.setupTime }} setup
                    </span>
                    <span class="meta-item">
                      <mat-icon>attach_money</mat-icon>
                      {{ provider.cost }}
                    </span>
                  </div>
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
                  @if (provider.baseUrl !== undefined) {
                    <mat-form-field appearance="outline" class="full-width">
                      <mat-label>Base URL</mat-label>
                      <input matInput [(ngModel)]="provider.baseUrl" placeholder="Enter base URL">
                    </mat-form-field>
                  }
                  @if (provider.model !== undefined) {
                    <mat-form-field appearance="outline" class="full-width">
                      <mat-label>Model</mat-label>
                      <input matInput [(ngModel)]="provider.model" placeholder="Enter model name">
                    </mat-form-field>
                  }
                  <div class="provider-actions">
                    <button mat-stroked-button (click)="saveProvider(provider)" class="save-button">
                      <mat-icon>save</mat-icon>
                      Save Configuration
                    </button>
                    <button mat-stroked-button (click)="testProvider(provider)" class="test-button">
                      <mat-icon>check_circle</mat-icon>
                      Test Connection
                    </button>
                  </div>
                </div>
              }
            </div>
          </div>

          <div class="provider-info-panel">
            <h3>About AI Providers</h3>
            <p>AI providers help Readloom extract accurate metadata from manga and books using advanced language models. They can:</p>
            <ul>
              <li>Extract volume and chapter information</li>
              <li>Identify release dates and schedules</li>
              <li>Parse complex metadata from images</li>
              <li>Improve search accuracy</li>
              <li>Auto-categorize content</li>
            </ul>

            <h4 class="mt-4">Setup Instructions</h4>
            <p><strong>Groq (Recommended)</strong></p>
            <ol class="setup-list">
              <li>Visit <a href="https://console.groq.com" target="_blank">console.groq.com</a></li>
              <li>Sign up for free account</li>
              <li>Create API key in settings</li>
              <li>Paste API key above</li>
            </ol>

            <p><strong>Google Gemini</strong></p>
            <ol class="setup-list">
              <li>Visit <a href="https://ai.google.dev" target="_blank">ai.google.dev</a></li>
              <li>Click "Get API Key"</li>
              <li>Create new API key</li>
              <li>Paste API key above</li>
            </ol>

            <p><strong>Ollama (Self-hosted)</strong></p>
            <ol class="setup-list">
              <li>Download from <a href="https://ollama.ai" target="_blank">ollama.ai</a></li>
              <li>Install and run locally</li>
              <li>Pull a model: <code>ollama pull mistral</code></li>
              <li>Set Base URL to <code>http://localhost:11434</code></li>
            </ol>

            <h4 class="mt-4">Privacy & Cost</h4>
            <p>All providers listed are free or have generous free tiers. No credit card required for Groq, Gemini, or Ollama.</p>
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
    .ai-providers-config {
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
      margin: 0 0 8px 0;
      font-size: 13px;
      color: #b0b0b0;
    }

    .provider-meta {
      display: flex;
      gap: 16px;
      margin-top: 8px;
    }

    .meta-item {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 12px;
      color: #90caf9;
    }

    .meta-item mat-icon {
      font-size: 14px;
      width: 14px;
      height: 14px;
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

    .provider-actions {
      display: flex;
      gap: 12px;
      align-self: flex-start;
    }

    .full-width {
      width: 100%;
    }

    .save-button {
      gap: 8px;
      background-color: #4caf50;
      color: white;
    }

    .save-button:hover {
      background-color: #45a049;
    }

    .test-button {
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

    .setup-list {
      margin: 8px 0 12px 20px !important;
      padding-left: 0 !important;
    }

    .setup-list li {
      margin-bottom: 6px;
    }

    .provider-info-panel code {
      background-color: #1e1e1e;
      color: #64b5f6;
      padding: 2px 6px;
      border-radius: 3px;
      font-family: 'Courier New', monospace;
      font-size: 12px;
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
export class AIProvidersConfigComponent implements OnInit {
  providers: AIProvider[] = [];

  constructor(
    public dialogRef: MatDialogRef<AIProvidersConfigComponent>,
    private notificationService: NotificationService,
    private aiProvidersService: AIProvidersService
  ) {}

  ngOnInit(): void {
    this.loadConfiguration();
  }

  private loadConfiguration(): void {
    // Load default providers immediately
    this.providers = this.aiProvidersService.getDefaultProviders();
    
    // Load saved configuration from backend (fast)
    this.aiProvidersService.getProvidersConfig().subscribe({
      next: (config) => {
        // Update providers with saved configuration immediately
        this.updateProvidersFromConfig(config);
      },
      error: (err) => {
        console.warn('Could not load AI providers config:', err);
        // Still try to get status even if config loading fails
        this.loadProvidersStatus();
      },
      complete: () => {
        // Load status in background for real-time updates
        this.loadProvidersStatus();
      }
    });
  }

  private updateProvidersFromConfig(config: any): void {
    // Update providers based on saved configuration
    Object.keys(config).forEach(key => {
      if (key.includes('_api_key')) {
        const providerName = key.replace('_api_key', '');
        const provider = this.providers.find(p => p.id === providerName || p.id === `google-${providerName}`);
        if (provider) {
          provider.apiKey = config[key];
          provider.enabled = !!config[key]; // Enable if API key exists
        }
      } else if (key.includes('_base_url')) {
        const providerName = key.replace('_base_url', '');
        const provider = this.providers.find(p => p.id === providerName);
        if (provider) {
          provider.baseUrl = config[key];
        }
      } else if (key.includes('_model')) {
        const providerName = key.replace('_model', '');
        const provider = this.providers.find(p => p.id === providerName);
        if (provider) {
          provider.model = config[key];
        }
      }
    });
  }

  private loadProvidersStatus(): void {
    // Load provider status in background for real-time updates
    this.aiProvidersService.getProvidersStatus().subscribe({
      next: (statusResponse) => {
        // Update provider enabled status based on backend
        Object.keys(statusResponse.providers).forEach(providerId => {
          const provider = this.providers.find(p => p.id === providerId || p.id === providerId.replace('google-', ''));
          if (provider) {
            provider.enabled = statusResponse.providers[providerId].configured;
          }
        });
      },
      error: (err) => {
        console.warn('Could not load AI providers status:', err);
      }
    });
  }

  onProviderToggle(provider: AIProvider): void {
    this.notificationService.info(`${provider.name} ${provider.enabled ? 'enabled' : 'disabled'}`);
  }

  testProvider(provider: AIProvider): void {
    this.notificationService.info(`Testing ${provider.name}...`);
    
    // Map frontend provider IDs to backend provider names
    const backendProviderName = this.mapProviderToBackend(provider.id);
    
    this.aiProvidersService.testProvider(backendProviderName).subscribe({
      next: (result) => {
        this.notificationService.success(result.message);
      },
      error: (err) => {
        this.notificationService.error(`Test failed: ${err.error?.error || err.message}`);
      }
    });
  }

  saveProvider(provider: AIProvider): void {
    this.notificationService.info(`Saving ${provider.name} configuration...`);
    
    // Map frontend provider IDs to backend provider names
    const backendProviderName = this.mapProviderToBackend(provider.id);
    
    this.aiProvidersService.saveProviderConfig(backendProviderName, provider).subscribe({
      next: (result) => {
        this.notificationService.success(`${provider.name} configuration saved successfully!`);
      },
      error: (err) => {
        this.notificationService.error(`Failed to save ${provider.name}: ${err.error?.error || err.message}`);
      }
    });
  }

  onSave(): void {
    // Save each enabled provider's configuration
    const savePromises = this.providers
      .filter(provider => provider.enabled)
      .map(provider => {
        const backendProviderName = this.mapProviderToBackend(provider.id);
        return this.aiProvidersService.saveProviderConfig(backendProviderName, provider).toPromise();
      });

    Promise.all(savePromises)
      .then(() => {
        this.notificationService.success('AI providers configuration saved');
        this.dialogRef.close({ action: 'save', data: this.providers });
      })
      .catch((error) => {
        this.notificationService.error('Failed to save configuration');
        console.error('Save error:', error);
      });
  }

  onCancel(): void {
    this.dialogRef.close({ action: 'cancel' });
  }

  private mapProviderToBackend(frontendId: string): string {
    const mapping: { [key: string]: string } = {
      'groq': 'groq',
      'google-gemini': 'gemini',
      'deepseek': 'deepseek',
      'ollama': 'ollama'
    };
    return mapping[frontendId] || frontendId;
  }
}
