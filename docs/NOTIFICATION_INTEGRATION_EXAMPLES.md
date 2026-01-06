# Notification Integration Examples

## Quick Start Template

Use this template when adding notifications to any component:

```typescript
import { NotificationService } from '../../services/notification.service';
import { ConfirmationService } from '../../services/confirmation.service';

export class MyComponent {
  constructor(
    private notificationService: NotificationService,
    private confirmationService: ConfirmationService,
    private apiService: MyApiService
  ) {}

  // Create operation
  onCreate(data: any): void {
    this.apiService.create(data).subscribe({
      next: () => {
        this.notificationService.success('Item created successfully');
        this.loadData();
      },
      error: (err) => {
        this.notificationService.error('Failed to create item');
        console.error('Error:', err);
      }
    });
  }

  // Update operation
  onUpdate(id: number, data: any): void {
    this.apiService.update(id, data).subscribe({
      next: () => {
        this.notificationService.success('Item updated successfully');
        this.loadData();
      },
      error: (err) => {
        this.notificationService.error('Failed to update item');
        console.error('Error:', err);
      }
    });
  }

  // Delete operation (with confirmation)
  onDelete(id: number, name: string): void {
    this.confirmationService.confirmDelete(name).subscribe(confirmed => {
      if (confirmed) {
        this.apiService.delete(id).subscribe({
          next: () => {
            this.notificationService.success('Item deleted successfully');
            this.loadData();
          },
          error: (err) => {
            this.notificationService.error('Failed to delete item');
            console.error('Error:', err);
          }
        });
      }
    });
  }
}
```

## Component-Specific Examples

### Dashboard Component

```typescript
// Sync data
onSyncData(): void {
  this.notificationService.info('Syncing data...');
  this.dashboardService.syncData().subscribe({
    next: () => {
      this.notificationService.success('Data synced successfully');
      this.loadDashboard();
    },
    error: (err) => {
      this.notificationService.error('Failed to sync data');
    }
  });
}

// Clear cache
onClearCache(): void {
  this.confirmationService.confirmWarning(
    'Clear Cache',
    'This will clear all cached metadata. This action cannot be undone.'
  ).subscribe(confirmed => {
    if (confirmed) {
      this.dashboardService.clearCache().subscribe({
        next: () => {
          this.notificationService.success('Cache cleared successfully');
        },
        error: (err) => {
          this.notificationService.error('Failed to clear cache');
        }
      });
    }
  });
}
```

### Series Management Component

```typescript
// Add series to collection
onAddToCollection(series: SeriesUI, collectionId: number): void {
  this.seriesService.addToCollection(series.id, collectionId).subscribe({
    next: () => {
      this.notificationService.success(`"${series.title}" added to collection`);
      this.loadSeries();
    },
    error: (err) => {
      this.notificationService.error('Failed to add series to collection');
    }
  });
}

// Mark as read
onMarkAsRead(series: SeriesUI): void {
  this.seriesService.markAsRead(series.id).subscribe({
    next: () => {
      this.notificationService.success(`"${series.title}" marked as read`);
      this.loadSeries();
    },
    error: (err) => {
      this.notificationService.error('Failed to mark series as read');
    }
  });
}

// Remove from library
onRemoveFromLibrary(series: SeriesUI): void {
  this.confirmationService.confirmDelete(series.title).subscribe(confirmed => {
    if (confirmed) {
      this.seriesService.removeFromLibrary(series.id).subscribe({
        next: () => {
          this.notificationService.success('Series removed from library');
          this.loadSeries();
        },
        error: (err) => {
          this.notificationService.error('Failed to remove series');
        }
      });
    }
  });
}
```

### Author Management Component

```typescript
// Add author
onAddAuthor(authorData: any): void {
  this.authorService.createAuthor(authorData).subscribe({
    next: () => {
      this.notificationService.success('Author added successfully');
      this.loadAuthors();
    },
    error: (err) => {
      this.notificationService.error('Failed to add author');
    }
  });
}

// Update author
onUpdateAuthor(id: number, authorData: any): void {
  this.authorService.updateAuthor(id, authorData).subscribe({
    next: () => {
      this.notificationService.success('Author updated successfully');
      this.loadAuthors();
    },
    error: (err) => {
      this.notificationService.error('Failed to update author');
    }
  });
}

// Delete author
onDeleteAuthor(author: AuthorUI): void {
  this.confirmationService.confirmDelete(author.name).subscribe(confirmed => {
    if (confirmed) {
      this.authorService.deleteAuthor(author.id).subscribe({
        next: () => {
          this.notificationService.success('Author deleted successfully');
          this.loadAuthors();
        },
        error: (err) => {
          this.notificationService.error('Failed to delete author');
        }
      });
    }
  });
}
```

### Import/Export Component

```typescript
// Import from file
onImportFile(file: File): void {
  this.notificationService.info('Importing data...');
  this.importService.importFromFile(file).subscribe({
    next: (result) => {
      this.notificationService.success(
        `Successfully imported ${result.count} items`
      );
      this.loadData();
    },
    error: (err) => {
      this.notificationService.error('Failed to import data');
    }
  });
}

// Export data
onExportData(): void {
  this.notificationService.info('Exporting data...');
  this.exportService.exportData().subscribe({
    next: (blob) => {
      this.notificationService.success('Data exported successfully');
      this.downloadFile(blob, 'readloom-export.json');
    },
    error: (err) => {
      this.notificationService.error('Failed to export data');
    }
  });
}

// Clear all data
onClearAllData(): void {
  this.confirmationService.confirm({
    title: 'Clear All Data',
    message: 'This will delete all your data. This action cannot be undone.',
    confirmText: 'Clear All',
    cancelText: 'Cancel',
    type: 'danger'
  }).subscribe(confirmed => {
    if (confirmed) {
      this.dataService.clearAll().subscribe({
        next: () => {
          this.notificationService.success('All data cleared');
          this.router.navigate(['/setup']);
        },
        error: (err) => {
          this.notificationService.error('Failed to clear data');
        }
      });
    }
  });
}
```

### Settings Component

```typescript
// Save general settings
onSaveGeneralSettings(): void {
  this.settingsService.saveGeneralSettings(this.generalSettings).subscribe({
    next: () => {
      this.notificationService.success('Settings saved successfully');
    },
    error: (err) => {
      this.notificationService.error('Failed to save settings');
    }
  });
}

// Reset settings
onResetSettings(): void {
  this.confirmationService.confirmWarning(
    'Reset Settings',
    'This will reset all settings to default values.'
  ).subscribe(confirmed => {
    if (confirmed) {
      this.settingsService.resetSettings().subscribe({
        next: () => {
          this.notificationService.success('Settings reset to defaults');
          this.loadSettings();
        },
        error: (err) => {
          this.notificationService.error('Failed to reset settings');
        }
      });
    }
  });
}
```

### Search/Import Component

```typescript
// Import from search result
onImportFromSearch(result: SearchResult): void {
  this.notificationService.info(`Adding "${result.title}"...`);
  this.importService.importFromSearch(result).subscribe({
    next: () => {
      this.notificationService.success(
        `"${result.title}" added to your library`
      );
      this.loadLibrary();
    },
    error: (err) => {
      if (err.status === 409) {
        this.notificationService.warning(
          `"${result.title}" is already in your library`
        );
      } else {
        this.notificationService.error('Failed to import item');
      }
    }
  });
}

// Bulk import
onBulkImport(items: SearchResult[]): void {
  this.notificationService.info(`Importing ${items.length} items...`);
  this.importService.bulkImport(items).subscribe({
    next: (result) => {
      this.notificationService.success(
        `Successfully imported ${result.successful} of ${items.length} items`
      );
      if (result.failed > 0) {
        this.notificationService.warning(
          `${result.failed} items failed to import`
        );
      }
      this.loadLibrary();
    },
    error: (err) => {
      this.notificationService.error('Bulk import failed');
    }
  });
}
```

### Modal Components

```typescript
// In add/edit modals
onSave(): void {
  if (!this.validateForm()) {
    this.notificationService.warning('Please fill in all required fields');
    return;
  }

  this.apiService.save(this.formData).subscribe({
    next: (result) => {
      this.notificationService.success('Saved successfully');
      this.dialogRef.close({ action: 'save', data: result });
    },
    error: (err) => {
      this.notificationService.error('Failed to save');
    }
  });
}

onDelete(): void {
  this.confirmationService.confirmDelete(this.formData.name)
    .subscribe(confirmed => {
      if (confirmed) {
        this.apiService.delete(this.formData.id).subscribe({
          next: () => {
            this.notificationService.success('Deleted successfully');
            this.dialogRef.close({ action: 'delete' });
          },
          error: (err) => {
            this.notificationService.error('Failed to delete');
          }
        });
      }
    });
}
```

## Error Handling Patterns

### Specific Error Messages

```typescript
// Provide specific error messages based on error type
onCreateItem(data: any): void {
  this.apiService.create(data).subscribe({
    next: () => {
      this.notificationService.success('Item created successfully');
    },
    error: (err) => {
      if (err.status === 400) {
        this.notificationService.error('Invalid data provided');
      } else if (err.status === 409) {
        this.notificationService.error('Item already exists');
      } else if (err.status === 500) {
        this.notificationService.error('Server error. Please try again later');
      } else {
        this.notificationService.error('Failed to create item');
      }
    }
  });
}
```

### Long-Running Operations

```typescript
// Show progress for long operations
onLongOperation(): void {
  this.notificationService.info('Processing... (0%)', 0);
  
  this.apiService.longOperation().subscribe({
    next: (progress) => {
      this.notificationService.info(`Processing... (${progress}%)`, 0);
    },
    error: (err) => {
      this.notificationService.clearAll();
      this.notificationService.error('Operation failed');
    },
    complete: () => {
      this.notificationService.clearAll();
      this.notificationService.success('Operation completed successfully');
    }
  });
}
```

## Testing Notifications

```typescript
// In component tests
it('should show success notification on create', () => {
  spyOn(notificationService, 'success');
  
  component.onCreate(testData);
  
  expect(notificationService.success).toHaveBeenCalledWith(
    'Item created successfully'
  );
});

it('should show confirmation dialog on delete', () => {
  spyOn(confirmationService, 'confirmDelete').and.returnValue(
    of(true)
  );
  
  component.onDelete(1, 'Test Item');
  
  expect(confirmationService.confirmDelete).toHaveBeenCalledWith('Test Item');
});
```
