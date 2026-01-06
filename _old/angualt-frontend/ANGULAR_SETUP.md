# Angular Frontend Setup Guide

## Overview

This document covers the setup and development of the Angular frontend for Readloom. The Angular application communicates with the Flask backend API to manage manga/comics collections.

## Quick Start

### Prerequisites
- Node.js 18+ (LTS recommended)
- npm 9+
- Flask backend running on `http://localhost:7227`

### Installation

1. Navigate to the Angular project directory:
```bash
cd frontend-angular
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:4200`

## Development Server

The Angular development server includes:
- Hot module reloading (HMR)
- Automatic browser refresh on file changes
- Source maps for debugging
- TypeScript compilation

### Running the Dev Server

```bash
npm start
```

Or with custom port:
```bash
ng serve --port 4300
```

## Project Structure

```
frontend-angular/
├── src/
│   ├── app/
│   │   ├── components/           # Reusable UI components
│   │   │   ├── navbar/          # Top navigation bar
│   │   │   └── sidebar/         # Side navigation
│   │   ├── pages/               # Page-level components
│   │   │   ├── dashboard/       # Dashboard page
│   │   │   ├── library/         # Series/books library
│   │   │   ├── calendar/        # Release calendar
│   │   │   ├── collections/     # Collections management
│   │   │   ├── authors/         # Authors list
│   │   │   └── settings/        # Application settings
│   │   ├── services/            # API and business logic services
│   │   │   ├── api.service.ts   # Base HTTP client
│   │   │   ├── auth.service.ts  # Authentication
│   │   │   └── ...
│   │   ├── models/              # TypeScript interfaces
│   │   ├── app.component.ts     # Root component
│   │   ├── app.routes.ts        # Route configuration
│   │   └── app.component.html   # Root template
│   ├── environments/            # Environment-specific configs
│   │   ├── environment.ts       # Development
│   │   └── environment.prod.ts  # Production
│   ├── styles.css              # Global styles
│   ├── index.html              # HTML entry point
│   └── main.ts                 # Application bootstrap
├── angular.json                # Angular CLI config
├── tsconfig.json               # TypeScript config
├── package.json                # Dependencies
└── README.md                   # Project README
```

## API Integration

### Base API Service

The `ApiService` provides a base HTTP client for all API calls:

```typescript
import { ApiService } from '@app/services/api.service';

constructor(private api: ApiService) {}

// GET request
this.api.get('/series').subscribe(data => {
  console.log(data);
});

// POST request
this.api.post('/series', { name: 'New Series' }).subscribe(response => {
  console.log(response);
});
```

### API Endpoints

All endpoints are prefixed with `/api`:

- **Series**
  - `GET /api/series` - List all series
  - `GET /api/series/:id` - Get series details
  - `POST /api/series` - Create new series
  - `PUT /api/series/:id` - Update series
  - `DELETE /api/series/:id` - Delete series

- **Collections**
  - `GET /api/collections` - List all collections
  - `POST /api/collections` - Create collection
  - `PUT /api/collections/:id` - Update collection
  - `DELETE /api/collections/:id` - Delete collection

- **Authors**
  - `GET /api/authors` - List all authors
  - `GET /api/authors/:id` - Get author details
  - `POST /api/authors` - Create author
  - `PUT /api/authors/:id` - Update author

- **Calendar**
  - `GET /api/calendar` - Get calendar events
  - `POST /api/calendar` - Create event

See Flask backend documentation for complete API reference.

## Environment Configuration

### Development Environment

File: `src/environments/environment.ts`

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:7227/api',
  wsUrl: 'ws://localhost:7227'
};
```

### Production Environment

File: `src/environments/environment.prod.ts`

```typescript
export const environment = {
  production: true,
  apiUrl: '/api',
  wsUrl: 'wss://' + window.location.host
};
```

## Building for Production

### Build Command

```bash
npm run build:prod
```

### Build Output

Production build artifacts are generated in `dist/readloom-angular/`

### Build Optimization

The production build includes:
- Minification and uglification
- Tree-shaking of unused code
- Ahead-of-time (AOT) compilation
- Bundle size optimization
- Source map generation (optional)

## Testing

### Unit Tests

Run unit tests with Jasmine/Karma:

```bash
npm test
```

### E2E Tests

Run end-to-end tests with Cypress:

```bash
npm run e2e
```

### Test Coverage

Generate coverage report:

```bash
ng test --code-coverage
```

## Code Quality

### Linting

Run ESLint to check code quality:

```bash
npm run lint
```

### TypeScript Strict Mode

The project uses TypeScript strict mode for type safety:
- `strict: true` - Enables all strict type checking options
- `noImplicitAny: true` - Error on implicit any types
- `strictNullChecks: true` - Strict null/undefined checks
- `strictFunctionTypes: true` - Strict function type checking

## Styling

### Global Styles

Global CSS is defined in `src/styles.css`

### Component Styles

Each component has its own CSS file:
- `component.component.css` - Component-specific styles

### CSS Framework

The project uses:
- Bootstrap 5 for responsive grid and components
- TailwindCSS for utility-first styling (optional)
- Custom CSS for component-specific styles

## Routing

Routes are configured in `src/app/app.routes.ts`:

```typescript
export const routes: Routes = [
  {
    path: 'dashboard',
    loadComponent: () => import('./pages/dashboard/dashboard.component')
      .then(m => m.DashboardComponent)
  },
  // ... more routes
];
```

### Lazy Loading

Routes use lazy loading to reduce initial bundle size:

```typescript
loadComponent: () => import('./pages/library/library.component')
  .then(m => m.LibraryComponent)
```

## Standalone Components

The project uses Angular standalone components (Angular 14+):

```typescript
@Component({
  selector: 'app-example',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './example.component.html',
  styleUrls: ['./example.component.css']
})
export class ExampleComponent {}
```

## Error Handling

### HTTP Error Interceptor

Errors from API calls are handled by the HTTP error interceptor:

```typescript
// Automatic error handling
this.api.get('/series').subscribe({
  next: (data) => console.log(data),
  error: (error) => console.error('Error:', error)
});
```

### User Notifications

Errors are displayed to users via the notification service:

```typescript
this.notification.error('Failed to load series');
```

## Development Workflow

### Creating a New Component

```bash
ng generate component components/my-component
```

### Creating a New Service

```bash
ng generate service services/my-service
```

### Creating a New Page

```bash
ng generate component pages/my-page
```

## Debugging

### Browser DevTools

1. Open Chrome DevTools (F12)
2. Go to Sources tab
3. Navigate to `webpack://` → `src/app/`
4. Set breakpoints and debug

### Angular DevTools

Install Angular DevTools browser extension for enhanced debugging:
- Component tree inspection
- Change detection profiling
- Service debugging

## Performance Optimization

### Bundle Analysis

Analyze bundle size:

```bash
ng build --stats-json
npm install -g webpack-bundle-analyzer
webpack-bundle-analyzer dist/readloom-angular/stats.json
```

### Lazy Loading Routes

Routes are lazy loaded to reduce initial bundle size.

### OnPush Change Detection

Use `ChangeDetectionStrategy.OnPush` for better performance:

```typescript
@Component({
  selector: 'app-example',
  changeDetection: ChangeDetectionStrategy.OnPush,
  // ...
})
```

## Deployment

### Docker Deployment

A Dockerfile is provided for containerized deployment:

```bash
docker build -t readloom-angular .
docker run -p 4200:4200 readloom-angular
```

### Static Hosting

The production build can be hosted on any static file server:

```bash
# Build
npm run build:prod

# Serve dist/ directory
python -m http.server --directory dist/readloom-angular 8000
```

## Troubleshooting

### Port 4200 Already in Use

```bash
ng serve --port 4300
```

### CORS Errors

Ensure Flask backend has CORS enabled:
- Check `backend/internals/server.py` for CORS configuration
- Verify Flask is running on correct port (default: 7227)

### Module Not Found

```bash
npm install
npm cache clean --force
```

### TypeScript Errors

Clear Angular cache:

```bash
rm -rf .angular/cache
ng serve
```

## Contributing

When contributing to the Angular frontend:

1. Follow Angular style guide
2. Use standalone components
3. Implement proper error handling
4. Add unit tests for new features
5. Keep components focused and reusable
6. Use TypeScript strict mode
7. Document complex logic

## Resources

- [Angular Documentation](https://angular.io/docs)
- [Angular Style Guide](https://angular.io/guide/styleguide)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)

## Support

For issues or questions:
1. Check existing GitHub issues
2. Review Angular documentation
3. Check Flask backend logs
4. Enable debug logging in browser console

## License

MIT License - See LICENSE file for details
