# In-App Notifications and Confirmations System

## Overview

The Readloom frontend now includes a comprehensive in-app notification and confirmation system that replaces browser `confirm()` dialogs and `alert()` messages with beautiful, Material Design components.

## Components

### 1. NotificationService
**Location**: `frontend/src/app/services/notification.service.ts`

Service for managing toast notifications throughout the application.

#### Methods

```typescript
// Show success notification (auto-dismisses after 5 seconds)
notificationService.success(message: string, duration?: number): void

// Show error notification
notificationService.error(message: string, duration?: number): void

// Show warning notification
notificationService.warning(message: string, duration?: number): void

// Show info notification
notificationService.info(message: string, duration?: number): void

// Remove specific notification
notificationService.removeNotification(id: string): void

// Clear all notifications
notificationService.clearAll(): void
```

#### Usage Examples

```typescript
// In any component
constructor(private notificationService: NotificationService) {}

// Show success after creating a collection
this.collectionService.createCollection(data).subscribe({
  next: () => {
    this.notificationService.success('Collection created successfully');
  },
  error: (err) => {
    this.notificationService.error('Failed to create collection');
  }
});

// Show warning
this.notificationService.warning('This action may take a while');

// Show info
this.notificationService.info('Syncing data...');
```

### 2. ConfirmationService
**Location**: `frontend/src/app/services/confirmation.service.ts`

Service for showing confirmation dialogs before destructive or important actions.

#### Methods

```typescript
// Show custom confirmation dialog
confirm(options: ConfirmationOptions): Observable<boolean>

// Show delete confirmation (pre-configured for delete actions)
confirmDelete(itemName: string): Observable<boolean>

// Show warning confirmation
confirmWarning(title: string, message: string): Observable<boolean>

// Show info confirmation
confirmInfo(title: string, message: string): Observable<boolean>
```

#### ConfirmationOptions Interface

```typescript
interface ConfirmationOptions {
  title: string;           // Dialog title
  message: string;         // Dialog message
  confirmText?: string;    // Confirm button text (default: "Confirm")
  cancelText?: string;     // Cancel button text (default: "Cancel")
  type?: 'warning' | 'danger' | 'info';  // Dialog type (default: "warning")
}
```

#### Usage Examples

```typescript
// In any component
constructor(private confirmationService: ConfirmationService) {}

// Delete confirmation
onDeleteCollection(collection: CollectionUI): void {
  this.confirmationService.confirmDelete(collection.name).subscribe(confirmed => {
    if (confirmed) {
      this.collectionService.deleteCollection(collection.id).subscribe({
        next: () => {
          this.notificationService.success('Collection deleted successfully');
        },
        error: () => {
          this.notificationService.error('Failed to delete collection');
        }
      });
    }
  });
}

// Custom warning confirmation
onDangerousAction(): void {
  this.confirmationService.confirmWarning(
    'Clear Cache',
    'This will clear all cached metadata. Continue?'
  ).subscribe(confirmed => {
    if (confirmed) {
      // Perform action
      this.notificationService.success('Cache cleared');
    }
  });
}

// Info confirmation
onShowInfo(): void {
  this.confirmationService.confirmInfo(
    'Information',
    'This series has 10 new chapters available'
  ).subscribe(confirmed => {
    if (confirmed) {
      // Handle confirmation
    }
  });
}
```

### 3. ToastNotificationComponent
**Location**: `frontend/src/app/components/notifications/toast-notification/toast-notification.component.ts`

Displays toast notifications in the top-right corner of the screen.

**Features**:
- Auto-dismisses after configurable duration
- Slide-in/out animations
- Color-coded by type (success, error, warning, info)
- Manual dismiss button
- Multiple notifications can be displayed simultaneously

### 4. ConfirmationDialogComponent
**Location**: `frontend/src/app/components/dialogs/confirmation-dialog/confirmation-dialog.component.ts`

Material Design confirmation dialog with customizable title, message, and buttons.

**Features**:
- Type-based styling (danger, warning, info)
- Appropriate icons for each type
- Customizable button text
- Modal behavior (prevents interaction with background)

## Integration Guide

### Step 1: Inject Services

```typescript
constructor(
  private notificationService: NotificationService,
  private confirmationService: ConfirmationService
) {}
```

### Step 2: Replace Browser Dialogs

**Before** (Browser confirm):
```typescript
const confirmed = confirm('Delete this item?');
if (confirmed) {
  // Delete logic
}
```

**After** (In-app confirmation):
```typescript
this.confirmationService.confirmDelete('Item Name').subscribe(confirmed => {
  if (confirmed) {
    // Delete logic
  }
});
```

### Step 3: Add Notifications to API Calls

```typescript
this.apiService.deleteItem(id).subscribe({
  next: () => {
    this.notificationService.success('Item deleted successfully');
    this.loadItems();
  },
  error: (err) => {
    this.notificationService.error('Failed to delete item');
    console.error('Error:', err);
  }
});
```

## Notification Types and Durations

| Type | Default Duration | Use Case |
|------|------------------|----------|
| success | 5000ms | Successful operations (create, update, delete) |
| error | 5000ms | Failed operations, errors |
| warning | 5000ms | Warnings, cautions |
| info | 5000ms | Informational messages |

### Custom Durations

```typescript
// Show notification for 10 seconds
this.notificationService.success('Long operation completed', 10000);

// Show permanent notification (must be manually dismissed)
this.notificationService.info('Processing...', 0);
```

## Styling

### Toast Notification Colors

- **Success**: Green (#4caf50)
- **Error**: Red (#f44336)
- **Warning**: Orange (#ff9800)
- **Info**: Blue (#2196f3)

### Confirmation Dialog Colors

- **Danger**: Red background with delete icon
- **Warning**: Orange background with warning icon
- **Info**: Blue background with info icon

## Best Practices

1. **Always provide feedback**: Show a notification after every user action
2. **Use appropriate types**: 
   - `success` for completed operations
   - `error` for failures
   - `warning` for cautions
   - `info` for informational messages
3. **Confirm destructive actions**: Always ask for confirmation before delete/clear operations
4. **Keep messages concise**: Notifications should be brief and actionable
5. **Don't overuse**: Avoid notification spam; only show when necessary

## Examples by Component

### Collections Management

```typescript
// Create collection
onAddCollection(): void {
  const dialogRef = this.dialog.open(AddCollectionModalComponent);
  dialogRef.afterClosed().subscribe((result) => {
    if (result?.action === 'save') {
      this.collectionService.createCollection(result.data).subscribe({
        next: () => {
          this.notificationService.success('Collection added successfully');
          this.loadCollections();
        },
        error: (err) => {
          this.notificationService.error('Failed to add collection');
        }
      });
    }
  });
}

// Delete collection
onDeleteCollection(collection: CollectionUI): void {
  this.confirmationService.confirmDelete(collection.name).subscribe(confirmed => {
    if (confirmed) {
      this.collectionService.deleteCollection(collection.id).subscribe({
        next: () => {
          this.notificationService.success('Collection deleted successfully');
          this.loadCollections();
        },
        error: (err) => {
          this.notificationService.error('Failed to delete collection');
        }
      });
    }
  });
}
```

### Series Management

```typescript
// Update series
onUpdateSeries(series: SeriesUI): void {
  this.seriesService.updateSeries(series.id, series).subscribe({
    next: () => {
      this.notificationService.success('Series updated successfully');
      this.loadSeries();
    },
    error: (err) => {
      this.notificationService.error('Failed to update series');
    }
  });
}

// Move series
onMoveSeries(series: SeriesUI, targetCollection: number): void {
  this.confirmationService.confirmWarning(
    'Move Series',
    `Move "${series.title}" to another collection?`
  ).subscribe(confirmed => {
    if (confirmed) {
      this.seriesService.moveSeries(series.id, targetCollection).subscribe({
        next: () => {
          this.notificationService.success('Series moved successfully');
          this.loadSeries();
        },
        error: (err) => {
          this.notificationService.error('Failed to move series');
        }
      });
    }
  });
}
```

## Migration Checklist

When updating existing components to use the new notification system:

- [ ] Inject `NotificationService` and `ConfirmationService`
- [ ] Replace all `confirm()` calls with `confirmationService.confirmDelete()` or `confirm()`
- [ ] Replace all `alert()` calls with `notificationService.info()` or appropriate type
- [ ] Add success notifications after successful API calls
- [ ] Add error notifications after failed API calls
- [ ] Test all notification types and confirmations
- [ ] Verify animations and styling

## Future Enhancements

- Notification history/log page
- Notification preferences (enable/disable by type)
- Sound alerts for important notifications
- Desktop notifications integration
- Notification persistence (save to database)
- Notification actions (undo, retry, etc.)
