# Modular Components Structure - Development Guide

## Overview

The Angular frontend is organized into modular, reusable sub-components that make it easy for developers to work independently on different sections and merge code without conflicts.

## Component Organization

### Dashboard Components
```
src/app/components/dashboard/
├── stat-cards-section/
│   ├── stat-cards-section.component.ts
│   ├── stat-cards-section.component.html
│   └── stat-cards-section.component.css
├── recent-series-section/
│   ├── recent-series-section.component.ts
│   ├── recent-series-section.component.html
│   └── recent-series-section.component.css
└── upcoming-releases-section/
    ├── upcoming-releases-section.component.ts
    ├── upcoming-releases-section.component.html
    └── upcoming-releases-section.component.css
```

### Library Components
```
src/app/components/library/
├── search-filter-section/
│   ├── search-filter-section.component.ts
│   ├── search-filter-section.component.html
│   └── search-filter-section.component.css
└── series-grid-section/
    ├── series-grid-section.component.ts
    ├── series-grid-section.component.html
    └── series-grid-section.component.css
```

### Collections Components
```
src/app/components/collections/
└── collection-cards-section/
    ├── collection-cards-section.component.ts
    ├── collection-cards-section.component.html
    └── collection-cards-section.component.css
```

### Calendar Components
```
src/app/components/calendar/
└── releases-table-section/
    ├── releases-table-section.component.ts
    ├── releases-table-section.component.html
    └── releases-table-section.component.css
```

### Authors Components
```
src/app/components/authors/
├── author-search-section/
│   ├── author-search-section.component.ts
│   ├── author-search-section.component.html
│   └── author-search-section.component.css
└── author-grid-section/
    ├── author-grid-section.component.ts
    ├── author-grid-section.component.html
    └── author-grid-section.component.css
```

## Page Components (Orchestrators)

Each page component is now a clean orchestrator that composes sub-components:

### Dashboard Page
```typescript
// Imports sub-components
import { StatCardsSectionComponent } from '../../components/dashboard/stat-cards-section/...';
import { RecentSeriesSectionComponent } from '../../components/dashboard/recent-series-section/...';
import { UpcomingReleasesSectionComponent } from '../../components/dashboard/upcoming-releases-section/...';

// Template simply composes them
<app-stat-cards-section [stats]="stats"></app-stat-cards-section>
<app-recent-series-section [series]="recentSeries"></app-recent-series-section>
<app-upcoming-releases-section [releases]="upcomingReleases"></app-upcoming-releases-section>
```

## Development Workflow

### Adding a New Feature to a Section

1. **Identify the section** (e.g., "Add filter by author to Library")
2. **Find the relevant sub-component** (e.g., `search-filter-section`)
3. **Modify only that component's files** (.ts, .html, .css)
4. **No need to touch the page component** unless adding a new section
5. **Easy to merge** - changes are isolated to one component

### Example: Add Author Filter to Library

**File**: `src/app/components/library/search-filter-section/search-filter-section.component.ts`

```typescript
// Add author filter to existing component
selectedAuthor = '';
authors = []; // from service

onAuthorChange(): void {
  this.emitFilters(); // Already handles emitting all filters
}
```

**File**: `src/app/components/library/search-filter-section/search-filter-section.component.html`

```html
<!-- Add author dropdown -->
<div class="col-md-3">
  <label class="form-label">Author</label>
  <select [(ngModel)]="selectedAuthor" (change)="onAuthorChange()">
    <option value="">All Authors</option>
    <option *ngFor="let author of authors" [value]="author.id">
      {{ author.name }}
    </option>
  </select>
</div>
```

## Benefits of This Structure

✅ **Isolation**: Each component is independent  
✅ **Reusability**: Components can be used in multiple pages  
✅ **Testability**: Easy to unit test individual components  
✅ **Maintainability**: Changes are localized  
✅ **Collaboration**: Multiple developers can work on different components simultaneously  
✅ **Merging**: Minimal merge conflicts since changes are in separate files  
✅ **Scalability**: Easy to add new features without touching existing code  

## Component Communication

### Parent to Child (Input)
```typescript
// Parent passes data to child
<app-stat-cards-section [stats]="stats"></app-stat-cards-section>

// Child receives data
@Input() stats!: DashboardStats;
```

### Child to Parent (Output)
```typescript
// Child emits events to parent
@Output() filtersChanged = new EventEmitter<LibraryFilters>();
this.filtersChanged.emit(filters);

// Parent listens to events
<app-search-filter-section (filtersChanged)="onFiltersChanged($event)"></app-search-filter-section>
```

## Styling Guidelines

Each component has its own CSS file with:
- Component-specific styles
- Dark mode support (`[data-bs-theme="dark"]`)
- Responsive design
- No global style pollution

## Next Components to Create

### Settings Page Sub-Components
- `user-preferences-section/` - Theme, language, notifications
- `account-settings-section/` - Profile, password, email
- `collection-management-section/` - Default collection, sorting

### Detail View Pages
- `series-detail/` - Series info, chapters, volumes, releases
- `author-detail/` - Author info, bibliography, metadata
- `collection-detail/` - Collection items, statistics, management

## File Naming Convention

- **Component files**: `{feature}-{section}.component.ts`
- **Template files**: `{feature}-{section}.component.html`
- **Style files**: `{feature}-{section}.component.css`
- **Folder names**: kebab-case (e.g., `search-filter-section`)
- **Component class names**: PascalCase (e.g., `SearchFilterSectionComponent`)

## Testing Sub-Components

Each sub-component can be tested independently:

```typescript
// Example unit test
describe('StatCardsSectionComponent', () => {
  it('should display correct stats', () => {
    const stats = { totalSeries: 10, totalBooks: 5, totalAuthors: 3, todayReleases: 2 };
    component.stats = stats;
    fixture.detectChanges();
    expect(component.stats.totalSeries).toBe(10);
  });
});
```

## Summary

This modular structure makes the Angular frontend:
- **Easy to develop** - Developers can work on isolated components
- **Easy to maintain** - Changes are localized and don't affect other parts
- **Easy to test** - Each component can be tested independently
- **Easy to merge** - Minimal conflicts when multiple developers work simultaneously
- **Easy to scale** - New features can be added without touching existing code

All components follow the same patterns and conventions, making the codebase consistent and predictable.
