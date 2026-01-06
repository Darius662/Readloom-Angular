# Phase 4: Testing & QA Guide

## Testing Strategy

### 1. Manual Testing Checklist

#### Dashboard Page
- [ ] Statistics cards display correct counts
- [ ] Recent series grid loads and displays 6 items
- [ ] Upcoming releases table shows next 7 days
- [ ] Loading spinner appears during data fetch
- [ ] Error message displays on API failure
- [ ] Dark mode styling correct
- [ ] Responsive on mobile (1 column), tablet (2 columns), desktop (4 columns)

#### Library Page
- [ ] All series load and display in grid
- [ ] Search filters series by name in real-time
- [ ] Type filter works (manga, manwa, comic, book)
- [ ] Sort options work (name, rating, updated)
- [ ] Results count updates correctly
- [ ] No results message displays when appropriate
- [ ] Series cards show cover, name, type, rating
- [ ] Dark mode styling correct
- [ ] Responsive grid layout works

#### Collections Page
- [ ] Collections load and display as cards
- [ ] Add collection button triggers action
- [ ] Edit button triggers action
- [ ] Delete button triggers action
- [ ] Collection type and description display
- [ ] No collections message shows when empty
- [ ] Dark mode styling correct
- [ ] Responsive layout works

#### Calendar Page
- [ ] Events load for next 30 days
- [ ] Table displays date, series, release, type, status
- [ ] Type badges show (chapter/volume)
- [ ] Status badges show (confirmed/predicted)
- [ ] Events sorted by date
- [ ] No events message shows when empty
- [ ] Dark mode styling correct
- [ ] Table responsive on mobile

#### Authors Page
- [ ] Authors load and display as cards
- [ ] Search filters by author name
- [ ] Author photos display or fallback icon shows
- [ ] Author name, nationality, bio preview display
- [ ] Results count updates
- [ ] No results message shows when appropriate
- [ ] Dark mode styling correct
- [ ] Responsive grid layout works

#### Navigation & Layout
- [ ] Navbar displays correctly
- [ ] Sidebar toggles on/off
- [ ] Theme toggle switches dark/light mode
- [ ] User dropdown menu works
- [ ] Active route highlighted in sidebar
- [ ] All routes accessible from sidebar
- [ ] Responsive on mobile (sidebar collapses)

#### Notifications
- [ ] Success notifications appear and auto-dismiss
- [ ] Error notifications appear and auto-dismiss
- [ ] Warning notifications appear and auto-dismiss
- [ ] Info notifications appear and auto-dismiss
- [ ] Multiple notifications stack correctly
- [ ] Close button removes notification

### 2. API Integration Testing

```bash
# Test each endpoint manually
curl http://localhost:7227/api/series
curl http://localhost:7227/api/collections
curl http://localhost:7227/api/authors
curl http://localhost:7227/api/calendar
```

Verify:
- [ ] CORS headers present in response
- [ ] Response format matches expected models
- [ ] Error responses handled gracefully
- [ ] Loading states work correctly

### 3. Browser Compatibility Testing

Test on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

Verify:
- [ ] All pages load without errors
- [ ] Styling consistent across browsers
- [ ] No console errors
- [ ] Dark mode works in all browsers

### 4. Mobile Testing

Test on:
- [ ] iPhone (iOS Safari)
- [ ] Android (Chrome)
- [ ] iPad (iOS Safari)
- [ ] Android tablet

Verify:
- [ ] Layout responsive
- [ ] Touch interactions work
- [ ] Sidebar collapse/expand works
- [ ] Forms usable on mobile
- [ ] No horizontal scrolling

### 5. Performance Testing

```bash
# Build production bundle
npm run build:prod

# Check bundle size
ls -lh dist/readloom-angular/
```

Verify:
- [ ] Main bundle < 500KB
- [ ] Lazy-loaded chunks < 100KB each
- [ ] Initial load time < 3 seconds
- [ ] Page transitions smooth
- [ ] No memory leaks in DevTools

### 6. Accessibility Testing

Verify:
- [ ] Keyboard navigation works
- [ ] Tab order logical
- [ ] Form labels associated with inputs
- [ ] Color contrast sufficient
- [ ] ARIA labels present where needed
- [ ] Screen reader compatible

## Running Tests

### Unit Tests
```bash
cd frontend-angular
npm test
```

### E2E Tests
```bash
npm run e2e
```

### Build Test
```bash
npm run build:prod
```

### Lint Check
```bash
npm run lint
```

## Known Issues & Workarounds

### Issue: CORS Errors
**Cause**: Flask backend CORS not configured  
**Fix**: Verify `backend/internals/server.py` has CORS enabled

### Issue: API 404 Errors
**Cause**: Flask backend not running or endpoint doesn't exist  
**Fix**: Start Flask server on port 7227

### Issue: Dark Mode Not Persisting
**Cause**: LocalStorage not available  
**Fix**: Check browser allows LocalStorage

## Test Results Template

```
Date: ___________
Tester: ___________
Browser: ___________
OS: ___________

Dashboard: ✓ / ✗
Library: ✓ / ✗
Collections: ✓ / ✗
Calendar: ✓ / ✗
Authors: ✓ / ✗
Navigation: ✓ / ✗
Notifications: ✓ / ✗
Dark Mode: ✓ / ✗
Responsive: ✓ / ✗
Performance: ✓ / ✗

Issues Found:
1. ___________
2. ___________
3. ___________

Notes:
___________
```

## Sign-Off

All tests passed: _____ (Date: _____)
Ready for deployment: _____ (Date: _____)
