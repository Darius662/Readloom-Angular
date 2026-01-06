# Readloom Angular Migration Plan

## Overview
Migrate Readloom from Flask with Jinja2 templates to a modern Angular frontend while maintaining the Flask backend API. This will provide better separation of concerns, improved performance, and a more maintainable architecture.

---

## Phase 1: Project Setup & Infrastructure (Week 1)

### 1.1 Create Angular Project Structure
- [ ] Initialize new Angular project in `frontend-angular/` directory
  - Use Angular 18+ (latest stable)
  - Configure TypeScript strict mode
  - Set up routing module
  - Configure environment files (dev, staging, prod)

### 1.2 Setup Build & Development Environment
- [ ] Configure Angular build system
  - Development server on port 4200
  - Production build optimization
  - Source maps for debugging
- [ ] Create `package.json` with dependencies:
  - Angular core libraries
  - Angular Material or ng-bootstrap for UI components
  - RxJS for reactive programming
  - HttpClient for API calls
  - ngx-translate for i18n (if needed)
  - TailwindCSS or Bootstrap for styling
- [ ] Setup development scripts in `package.json`
  - `npm start` - Run dev server
  - `npm build` - Production build
  - `npm test` - Run tests
  - `npm lint` - Code linting

### 1.3 Configure Flask Backend for CORS
- [ ] Update Flask app configuration
  - Enable CORS for Angular dev server (localhost:4200)
  - Configure CORS for production domain
  - Set proper headers for API responses
- [ ] Update `requirements.txt` if needed
  - Ensure `flask-cors` is present (already in your project)

### 1.4 Create Project Documentation
- [ ] Create `ANGULAR_MIGRATION.md` with:
  - Architecture overview
  - Development setup instructions
  - API integration guidelines
  - Component structure conventions

---

## Phase 2: Core Infrastructure & Services (Week 1-2)

### 2.1 Setup Angular Services Layer
- [ ] Create `src/app/services/` directory structure:
  - `api.service.ts` - Base HTTP client wrapper
  - `auth.service.ts` - Authentication handling
  - `storage.service.ts` - LocalStorage management
  - `notification.service.ts` - Toast/notification system
  - `error-handler.service.ts` - Global error handling

### 2.2 Create HTTP Interceptors
- [ ] Build interceptors for:
  - Authentication token injection
  - Error handling & logging
  - Request/response logging
  - Loading state management

### 2.3 Setup State Management (Optional but Recommended)
- [ ] Consider NgRx or Akita for state management
  - Or use simple RxJS services with BehaviorSubjects
  - Create store for:
    - User authentication state
    - Collections data
    - Series/books data
    - UI state (sidebar, theme, etc.)

### 2.4 Create Shared Components & Utilities
- [ ] Build reusable components:
  - Navigation/sidebar component
  - Header component
  - Footer component
  - Loading spinner
  - Error message display
  - Confirmation dialogs
- [ ] Create utility functions:
  - Date formatting
  - Number formatting
  - String utilities
  - Validation helpers

---

## Phase 3: API Integration & Mapping (Week 2-3)

### 3.1 Document Existing Flask API Endpoints
- [ ] Create comprehensive API documentation:
  - List all endpoints from `frontend/api.py` and related files
  - Document request/response formats
  - Identify authentication requirements
  - Note any special headers or parameters

### 3.2 Create Angular API Service Methods
- [ ] Map all Flask endpoints to Angular services:
  - Series/Books endpoints
  - Collections endpoints
  - Authors endpoints
  - Calendar endpoints
  - E-books endpoints
  - Settings endpoints
  - Search endpoints
  - Metadata provider endpoints

### 3.3 Create TypeScript Models/Interfaces
- [ ] Define interfaces for all data models:
  - `Series`, `Book`, `Chapter`, `Volume`
  - `Collection`, `Author`
  - `Release`, `CalendarEvent`
  - `Settings`, `User`
  - `SearchResult`, `MetadataProvider`

### 3.4 Setup API Error Handling
- [ ] Create error response models
- [ ] Implement error interceptor
- [ ] Setup user-friendly error messages

---

## Phase 4: Core Pages & Features (Week 3-5)

### 4.1 Dashboard Page
- [ ] Create dashboard component
  - Statistics cards (series count, books count, authors count, today's releases)
  - Recent releases widget
  - Quick stats display
  - Responsive grid layout

### 4.2 Collections Management
- [ ] Create collections list page
  - Display all collections
  - Add/edit/delete collection modals
  - Collection statistics
  - Filter and search functionality
- [ ] Create collection detail page
  - Show series in collection
  - Add/remove series
  - Collection settings

### 4.3 Series/Books Library
- [ ] Create library page
  - Grid/list view toggle
  - Search and filter functionality
  - Sorting options
  - Pagination
  - Series detail modal/page
- [ ] Create series detail page
  - Series information
  - Chapters/volumes list
  - Release calendar
  - Add to collection functionality
  - Edit series metadata

### 4.4 Calendar View
- [ ] Create calendar component
  - Month/week/list view modes
  - Filter by type and series
  - Click to add releases
  - Color coding for release types
  - Responsive design

### 4.5 Authors Management
- [ ] Create authors list page
  - Search and filter
  - Author cards with photos
  - Author detail page
- [ ] Create author detail page
  - Biography and metadata
  - Bibliography
  - Subject categorization
  - External links

---

## Phase 5: Advanced Features (Week 5-6)

### 5.1 Search Functionality
- [ ] Implement global search
  - Search across series, books, authors
  - Multi-source search (AniList, MangaDex, etc.)
  - Search result display and filtering

### 5.2 E-book Management
- [ ] Create e-books management page
  - Browse e-book folders
  - Scan for new files
  - File organization view

### 5.3 Settings Page
- [ ] Create settings component
  - Calendar settings
  - E-book settings
  - Theme/appearance settings
  - Notification preferences
  - API provider configuration

### 5.4 Integrations
- [ ] Create integrations page
  - Home Assistant integration setup
  - Homarr integration setup
  - API key management

---

## Phase 6: UI/UX Polish & Styling (Week 6-7)

### 6.1 Design System Implementation
- [ ] Setup TailwindCSS or Bootstrap
- [ ] Create design tokens
- [ ] Implement color scheme (dark/light theme)
- [ ] Create consistent spacing and typography

### 6.2 Responsive Design
- [ ] Test on mobile, tablet, desktop
- [ ] Implement mobile-first approach
- [ ] Create responsive navigation
- [ ] Optimize touch interactions

### 6.3 Accessibility
- [ ] ARIA labels and semantic HTML
- [ ] Keyboard navigation
- [ ] Color contrast compliance
- [ ] Screen reader testing

### 6.4 Performance Optimization
- [ ] Lazy loading for routes
- [ ] Image optimization
- [ ] Bundle size optimization
- [ ] Caching strategies

---

## Phase 7: Testing & Quality Assurance (Week 7-8)

### 7.1 Unit Tests
- [ ] Write unit tests for services
- [ ] Write unit tests for components
- [ ] Aim for 70%+ code coverage
- [ ] Use Jasmine/Karma test framework

### 7.2 Integration Tests
- [ ] Test API integration
- [ ] Test component interactions
- [ ] Test routing

### 7.3 E2E Tests
- [ ] Create E2E tests with Cypress or Playwright
- [ ] Test critical user workflows:
  - Add series to collection
  - Search and import
  - Calendar interactions
  - Settings management

### 7.4 Manual Testing
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] Mobile device testing
- [ ] Performance testing
- [ ] Accessibility testing

---

## Phase 8: Deployment & Migration (Week 8-9)

### 8.1 Build Configuration
- [ ] Configure production build
- [ ] Setup environment-specific configurations
- [ ] Optimize bundle size
- [ ] Configure base href for URL routing

### 8.2 Docker Integration
- [ ] Create Dockerfile for Angular app
- [ ] Update docker-compose.yml
  - Add Angular service
  - Configure nginx reverse proxy
  - Setup volume mounts
- [ ] Update entrypoint scripts

### 8.3 Deployment Strategy
- [ ] Blue-green deployment approach
  - Keep old Flask+Jinja2 running
  - Deploy Angular alongside
  - Switch traffic gradually
- [ ] Create deployment documentation
- [ ] Setup CI/CD pipeline (GitHub Actions)

### 8.4 Data Migration
- [ ] Ensure database compatibility
- [ ] Test API endpoints with new frontend
- [ ] Verify all data is accessible

### 8.5 Rollback Plan
- [ ] Document rollback procedures
- [ ] Keep old frontend available
- [ ] Monitor for issues post-deployment

---

## Phase 9: Cleanup & Optimization (Week 9-10)

### 9.1 Remove Old Frontend
- [ ] Archive old `frontend/` directory
- [ ] Remove old Jinja2 templates
- [ ] Remove old static files
- [ ] Update Flask to serve only API endpoints

### 9.2 Documentation Updates
- [ ] Update README.md
- [ ] Update installation instructions
- [ ] Update development setup guide
- [ ] Create migration guide for users

### 9.3 Performance Monitoring
- [ ] Setup monitoring for:
  - Page load times
  - API response times
  - Error rates
  - User interactions

### 9.4 Post-Launch Support
- [ ] Monitor for bugs
- [ ] Gather user feedback
- [ ] Plan improvements

---

## Technical Stack Summary

### Frontend (Angular)
- **Framework**: Angular 18+
- **Language**: TypeScript
- **Styling**: TailwindCSS or Bootstrap
- **HTTP Client**: Angular HttpClient
- **State Management**: RxJS Services or NgRx
- **Testing**: Jasmine/Karma (unit), Cypress/Playwright (E2E)
- **Build Tool**: Angular CLI

### Backend (Flask) - Unchanged
- **Framework**: Flask 3.0.0
- **Server**: Waitress
- **Database**: SQLite (existing)
- **CORS**: flask-cors

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions (recommended)
- **Reverse Proxy**: Nginx (for production)

---

## Key Considerations

### 1. API Compatibility
- Ensure Flask API endpoints remain stable
- Add versioning if breaking changes occur
- Maintain backward compatibility during transition

### 2. Authentication
- Implement JWT or session-based auth in Angular
- Ensure secure token storage
- Handle token refresh gracefully

### 3. Performance
- Lazy load routes and modules
- Implement virtual scrolling for large lists
- Cache API responses appropriately
- Optimize bundle size

### 4. Browser Support
- Target modern browsers (Chrome, Firefox, Safari, Edge)
- Consider graceful degradation for older browsers
- Test on mobile browsers

### 5. Data Persistence
- Use LocalStorage for user preferences
- Cache collection/series data appropriately
- Implement offline support if needed

### 6. Accessibility
- Follow WCAG 2.1 AA standards
- Test with screen readers
- Ensure keyboard navigation

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| API breaking changes | Version API endpoints, maintain compatibility |
| Performance degradation | Profile and optimize early, use lazy loading |
| User adoption | Provide clear migration guide, maintain old UI temporarily |
| Data loss | Backup database before migration, test thoroughly |
| Browser compatibility | Test on multiple browsers, use polyfills if needed |
| Security vulnerabilities | Follow Angular security best practices, sanitize inputs |

---

## Success Criteria

- [ ] All existing features working in Angular
- [ ] Performance equal or better than Flask+Jinja2
- [ ] 70%+ unit test coverage
- [ ] All E2E tests passing
- [ ] Mobile responsive design
- [ ] Accessibility compliance (WCAG 2.1 AA)
- [ ] Zero data loss during migration
- [ ] Documentation complete and up-to-date
- [ ] Deployment successful with zero downtime
- [ ] User feedback positive

---

## Timeline Estimate

- **Total Duration**: 8-10 weeks
- **Phase 1**: 1 week
- **Phase 2**: 1-2 weeks
- **Phase 3**: 1-2 weeks
- **Phase 4**: 2-3 weeks
- **Phase 5**: 1-2 weeks
- **Phase 6**: 1-2 weeks
- **Phase 7**: 1-2 weeks
- **Phase 8**: 1-2 weeks
- **Phase 9**: 1 week

---

## Next Steps

1. Review and approve this migration plan
2. Set up Angular project structure (Phase 1)
3. Configure Flask backend for CORS (Phase 1.3)
4. Begin service layer development (Phase 2)
5. Create API documentation (Phase 3.1)

