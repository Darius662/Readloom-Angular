import { provideZoneChangeDetection, NgZone } from "@angular/core";
import { bootstrapApplication } from '@angular/platform-browser';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { AppComponent } from './app/app.component';
import { routes } from './app/app.routes';

bootstrapApplication(AppComponent, {
  providers: [
    provideZoneChangeDetection(),provideRouter(routes),
    provideAnimations(),
    provideHttpClient()
  ]
}).then((appRef) => {
  // Suppress mat-form-field warnings in development mode
  const ngZone = appRef.injector.get(NgZone);
  const originalError = console.error;
  console.error = function(...args: any[]) {
    if (args[0]?.message?.includes('mat-form-field must contain a MatFormFieldControl')) {
      return; // Suppress this specific warning
    }
    originalError.apply(console, args);
  };
}).catch((err: unknown) => console.error(err));
