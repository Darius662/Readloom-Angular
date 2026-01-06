import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { StorageService } from './storage.service';

export type Theme = 'light' | 'dark';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private theme$ = new BehaviorSubject<Theme>('dark');
  private readonly THEME_KEY = 'readloom-theme';

  constructor(private storage: StorageService) {
    this.initializeTheme();
  }

  private initializeTheme(): void {
    const savedTheme = this.storage.getItem<Theme>(this.THEME_KEY);

    if (savedTheme) {
      this.setTheme(savedTheme);
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.setTheme(prefersDark ? 'dark' : 'light');
    }
  }

  getTheme(): Observable<Theme> {
    return this.theme$.asObservable();
  }

  getCurrentTheme(): Theme {
    return this.theme$.value;
  }

  isDarkMode(): boolean {
    return this.theme$.value === 'dark';
  }

  setTheme(theme: Theme): void {
    this.theme$.next(theme);
    this.storage.setItem(this.THEME_KEY, theme);
    this.applyTheme(theme);
  }

  toggleTheme(): void {
    const newTheme = this.theme$.value === 'dark' ? 'light' : 'dark';
    this.setTheme(newTheme);
  }

  private applyTheme(theme: Theme): void {
    const body = document.body;

    if (theme === 'light') {
      body.classList.add('light-theme');
    } else {
      body.classList.remove('light-theme');
    }
  }
}
