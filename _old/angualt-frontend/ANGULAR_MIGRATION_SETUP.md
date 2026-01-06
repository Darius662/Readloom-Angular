# Angular Migration Setup Documentation

## Overview

This document describes the setup and configuration of the Angular frontend migration for Readloom. The migration maintains the Flask backend while replacing the Jinja2 templates with a modern Angular 18+ frontend.

## Architecture

### Before Migration
```
Client → Flask Server (Port 7227)
         ├── Jinja2 Templates
         ├── Static Files (CSS, JS)
         └── API Endpoints
```

### After Migration
```
Angular Dev Server (Port 4200) → Flask API Server (Port 7227)
                                 ├── API Endpoints
                                 └── Static Files (if needed)
```

## Setup Instructions

### 1. Prerequisites

- Node.js 18+ (LTS)
- npm 9+
- Python 3.8+
- Flask backend running

### 2. Angular Project Location

The Angular project is located in: `frontend-angular/`

### 3. Installation Steps

#### Step 1: Install Angular Dependencies

```bash
cd frontend-angular
npm install
```

#### Step 2: Configure Environment

The environment is pre-configured to use:
- Development: `http://localhost:7227/api`
- Production: `/api` (relative path)

To customize, edit `src/environments/environment.ts`

#### Step 3: Start Development Server

```bash
npm start
```

The Angular app will be available at `http://localhost:4200`

#### Step 4: Verify Flask Backend

Ensure Flask backend is running:

```bash
# In the root directory
python Readloom.py
```

Flask should be running on `http://localhost:7227`

### 4. CORS Configuration

CORS is configured in `backend/internals/server.py` to allow:

- `http://localhost:4200` - Angular dev server
- `http://127.0.0.1:4200` - Angular dev server (localhost)
- `http://localhost:7227` - Readloom production
- `http://127.0.0.1:7227` - Readloom production (localhost)

#### Allowed Methods
- GET, POST, PUT, DELETE, PATCH, OPTIONS

#### Allowed Headers
- Content-Type
- Authorization
- X-Requested-With

#### Exposed Headers
- Content-Type
- X-Total-Count

### 5. Development Workflow

#### Terminal 1: Flask Backend

```bash
# In root directory
python Readloom.py
```

#### Terminal 2: Angular Frontend

```bash
# In frontend-angular directory
npm start
```

Both servers will run simultaneously:
- Angular: `http://localhost:4200`
- Flask: `http://localhost:7227`

## Project Structure

### Angular Project (`frontend-angular/`)

```
frontend-angular/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── navbar/
│   │   │   └── sidebar/
│   │   ├── pages/
│   │   │   ├── dashboard/
│   │   │   ├── library/
│   │   │   ├── calendar/
│   │   │   ├── collections/
│   │   │   ├── authors/
│   │   │   └── settings/
│   │   ├── services/
│   │   ├── models/
│   │   ├── app.component.ts
│   │   ├── app.routes.ts
│   │   └── app.component.html
│   ├── environments/
│   ├── styles.css
│   ├── index.html
│   └── main.ts
├── angular.json
├── tsconfig.json
├── package.json
└── README.md
```

### Flask Backend (Unchanged)

```
backend/
├── features/
├── internals/
│   └── server.py (CORS configured here)
└── base/

frontend/
├── api.py (API endpoints)
├── api_*.py (Feature-specific APIs)
├── templates/ (Old Jinja2 templates - can be removed later)
└── static/ (Static files)
```

## API Integration

### Base API Service

All API calls go through `ApiService` in `src/app/services/api.service.ts`

### Example API Call

```typescript
// In a component
constructor(private api: ApiService) {}

ngOnInit() {
  this.api.get('/series').subscribe(
    (data) => {
      this.series = data;
    },
    (error) => {
      console.error('Error loading series:', error);
    }
  );
}
```

### API Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Optional message"
}
```

## Environment Configuration

### Development (`src/environments/environment.ts`)

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:7227/api',
  wsUrl: 'ws://localhost:7227'
};
```

### Production (`src/environments/environment.prod.ts`)

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
cd frontend-angular
npm run build:prod
```

### Build Output

Production build is generated in `dist/readloom-angular/`

### Deployment Options

#### Option 1: Serve from Flask

Copy the build output to Flask static directory:

```bash
cp -r dist/readloom-angular/* ../frontend/static/
```

Then update Flask to serve the Angular app.

#### Option 2: Separate Angular Server

Deploy Angular and Flask separately:
- Angular: Netlify, Vercel, or static hosting
- Flask: Traditional server or Docker

#### Option 3: Docker

Create a Docker image with both Angular and Flask:

```dockerfile
# Build Angular
FROM node:18 as angular-build
WORKDIR /app
COPY frontend-angular .
RUN npm install && npm run build:prod

# Flask with Angular
FROM python:3.11
COPY --from=angular-build /app/dist/readloom-angular /app/frontend/static/angular
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "Readloom.py"]
```

## Troubleshooting

### CORS Errors

**Error**: `Access to XMLHttpRequest at 'http://localhost:7227/api/series' from origin 'http://localhost:4200' has been blocked by CORS policy`

**Solution**:
1. Verify Flask backend has CORS enabled in `backend/internals/server.py`
2. Check that Flask is running on port 7227
3. Verify Angular is using correct API URL in `environment.ts`

### Port Already in Use

**Error**: `Port 4200 is already in use`

**Solution**:
```bash
ng serve --port 4300
```

### Module Not Found

**Error**: `Cannot find module '@angular/core'`

**Solution**:
```bash
cd frontend-angular
npm install
npm cache clean --force
```

### API Calls Returning 404

**Error**: `GET http://localhost:7227/api/series 404 (Not Found)`

**Solution**:
1. Verify Flask backend is running
2. Check API endpoint exists in Flask
3. Verify API URL in `environment.ts` is correct

## Migration Phases

### Phase 1: Setup (COMPLETED ✅)
- [x] Initialize Angular project
- [x] Configure build environment
- [x] Setup CORS in Flask
- [x] Create documentation

### Phase 2: Core Infrastructure (NEXT)
- [ ] Create API services
- [ ] Setup state management
- [ ] Create shared components
- [ ] Implement error handling

### Phase 3: API Integration
- [ ] Map all Flask endpoints
- [ ] Create TypeScript models
- [ ] Implement API service methods

### Phase 4: Core Pages
- [ ] Dashboard page
- [ ] Collections management
- [ ] Series/Books library
- [ ] Calendar view
- [ ] Authors management

### Phase 5: Advanced Features
- [ ] Search functionality
- [ ] E-book management
- [ ] Settings page
- [ ] Integrations

### Phase 6: UI/UX Polish
- [ ] Design system
- [ ] Responsive design
- [ ] Accessibility
- [ ] Performance optimization

### Phase 7: Testing & QA
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests
- [ ] Manual testing

### Phase 8: Deployment
- [ ] Build configuration
- [ ] Docker integration
- [ ] CI/CD pipeline
- [ ] Deployment strategy

### Phase 9: Cleanup
- [ ] Remove old frontend
- [ ] Update documentation
- [ ] Performance monitoring
- [ ] Post-launch support

## Next Steps

1. **Verify Setup**
   ```bash
   # Terminal 1: Flask
   python Readloom.py
   
   # Terminal 2: Angular
   cd frontend-angular
   npm start
   ```

2. **Test API Connection**
   - Open `http://localhost:4200`
   - Check browser console for errors
   - Verify API calls in Network tab

3. **Begin Phase 2**
   - Create API services
   - Setup state management
   - Create shared components

## Resources

- [Angular Documentation](https://angular.io)
- [Flask Documentation](https://flask.palletsprojects.com)
- [CORS Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## Support

For issues:
1. Check browser console for errors
2. Check Flask server logs
3. Verify CORS configuration
4. Review API endpoint documentation
5. Check network requests in DevTools

## License

MIT License - See LICENSE file for details
