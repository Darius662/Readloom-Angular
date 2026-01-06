import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface AIProvider {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  apiKey?: string;
  apiUrl?: string;
  model?: string;
  baseUrl?: string;
  setupTime: string;
  cost: string;
}

export interface AIProviderStatus {
  available: boolean;
  configured: boolean;
}

export interface AIProvidersStatusResponse {
  providers: {
    [key: string]: AIProviderStatus;
  };
}

export interface AIProviderTestResult {
  message: string;
  metadata?: {
    title: string;
    volumes: number;
    chapters: number;
    status: string;
    confidence: number;
  };
}

@Injectable({
  providedIn: 'root'
})
export class AIProvidersService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * Get providers configuration from local JSON file (fast loading)
   */
  getProvidersConfig(): Observable<any> {
    return this.http.get(`${this.apiUrl}/ai-providers/config`);
  }

  /**
   * Get status of all AI providers
   */
  getProvidersStatus(): Observable<AIProvidersStatusResponse> {
    return this.http.get<AIProvidersStatusResponse>(`${this.apiUrl}/ai-providers/status`);
  }

  /**
   * Save AI provider configuration
   */
  saveProviderConfig(provider: string, config: Partial<AIProvider>): Observable<any> {
    const payload = {
      provider,
      api_key: config.apiKey,
      enabled: config.enabled,
      base_url: config.baseUrl,
      model: config.model
    };
    return this.http.post(`${this.apiUrl}/ai-providers/config`, payload);
  }

  /**
   * Test an AI provider
   */
  testProvider(provider: string): Observable<AIProviderTestResult> {
    return this.http.post<AIProviderTestResult>(`${this.apiUrl}/ai-providers/test`, { provider });
  }

  /**
   * Get default providers configuration
   */
  getDefaultProviders(): AIProvider[] {
    return [
      {
        id: 'groq',
        name: 'Groq',
        description: 'Fastest inference, completely free, perfect for beginners',
        enabled: false,
        apiKey: '',
        setupTime: '1 minute',
        cost: 'Free'
      },
      {
        id: 'google-gemini',
        name: 'Google Gemini',
        description: 'Powerful AI model with free tier, great for production',
        enabled: false,
        apiKey: '',
        setupTime: '2 minutes',
        cost: 'Free tier available'
      },
      {
        id: 'deepseek',
        name: 'DeepSeek',
        description: 'Good reasoning capabilities, affordable pricing',
        enabled: false,
        apiKey: '',
        setupTime: '2 minutes',
        cost: 'Free tier available'
      },
      {
        id: 'ollama',
        name: 'Ollama',
        description: 'Self-hosted, completely private, no API key needed',
        enabled: false,
        baseUrl: 'http://localhost:11434',
        model: 'mistral',
        setupTime: '5 minutes',
        cost: 'Free (self-hosted)'
      }
    ];
  }
}
