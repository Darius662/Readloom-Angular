/**
 * Collections Manager JavaScript
 * Handles loading and managing collections and root folders
 */

$(document).ready(function() {
    // Load collections and root folders
    loadCollections();
    loadRootFolders();
    window.selectedCollectionId = null;
    
    // Set up event handlers for collection actions
    $('#addCollectionBtn').click(function() {
        $('#addCollectionModal').modal('show');
    });
    
    $('#saveCollectionBtn').click(function() {
        saveCollection();
    });
    
    // Set up event handlers for root folder actions
    $('#addRootFolderBtn').click(function() {
        $('#addRootFolderModal').modal('show');
    });
    
    $('#saveRootFolderBtn').click(function() {
        saveRootFolder();
    });
});

/**
 * Load collections from the API
 */
function loadCollections() {
    $.ajax({
        url: '/api/collections',
        method: 'GET',
        success: function(response) {
            if (response.success && response.collections) {
                displayCollections(response.collections);
            } else {
                console.error('Error loading collections:', response);
                $('#collectionsTableBody').html('<tr><td colspan="7" class="text-center text-danger">Failed to load collections</td></tr>');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading collections:', error);
            $('#collectionsTableBody').html('<tr><td colspan="7" class="text-center text-danger">Failed to load collections</td></tr>');
        }
    });
    
    // Log to console for debugging
    console.log('Loading collections...');
}

/**
 * Display collections in the table
 */
function displayCollections(collections) {
    const tbody = $('#collectionsTableBody');
    tbody.empty();
    
    if (collections.length === 0) {
        tbody.html('<tr><td colspan="7" class="text-center">No collections found</td></tr>');
        return;
    }
    
    collections.forEach(function(collection) {
        const row = $('<tr>');
        
        // Name
        row.append($('<td>').text(collection.name));
        
        // Description
        row.append($('<td>').text(collection.description || '-'));

        // Type
        row.append($('<td>').text(collection.content_type || 'MANGA'));
        
        // Root Folders count
        const rootFoldersCount = (typeof collection.root_folder_count === 'number') ? collection.root_folder_count : (collection.root_folders ? collection.root_folders.length : 0);
        row.append($('<td>').text(rootFoldersCount));
        
        // Series count
        const seriesCount = (typeof collection.series_count === 'number') ? collection.series_count : (collection.series ? collection.series.length : 0);
        row.append($('<td>').text(seriesCount));
        
        // Default
        const defaultBadge = collection.is_default ? 
            '<span class="badge bg-success">Yes</span>' : 
            '<span class="badge bg-secondary">No</span>';
        row.append($('<td>').html(defaultBadge));
        
        // Actions
        const actionsCell = $('<td>');
        
        // View button
        const viewBtn = $('<button>')
            .addClass('btn btn-sm btn-info me-1')
            .html('<i class="fas fa-eye"></i>')
            .attr('title', 'View Details')
            .data('id', collection.id)
            .click(function() {
                viewCollectionDetails(collection.id);
            });
        
        // Edit button
        const editBtn = $('<button>')
            .addClass('btn btn-sm btn-primary me-1')
            .html('<i class="fas fa-edit"></i>')
            .attr('title', 'Edit')
            .data('id', collection.id)
            .click(function() {
                editCollection(collection);
            });
        
        // Delete button
        const deleteBtn = $('<button>')
            .addClass('btn btn-sm btn-danger')
            .html('<i class="fas fa-trash"></i>')
            .attr('title', 'Delete')
            .data('id', collection.id)
            .click(function() {
                confirmDeleteCollection(collection);
            });
        
        actionsCell.append(viewBtn, editBtn, deleteBtn);
        row.append(actionsCell);
        
        tbody.append(row);
    });
}

// Populate root folder choices when the Link modal is opened
$(document).on('show.bs.modal', '#linkRootFolderModal', function () {
    if (!window.selectedCollectionId) {
        // If no collection selected, prevent opening
        showError('Please view a collection first (click the eye icon).');
        $('#linkRootFolderModal').modal('hide');
        return;
    }

    // Load all root folders and those already linked to this collection
    $.when(
        $.get('/api/root-folders'),
        $.get(`/api/collections/${window.selectedCollectionId}/root-folders`)
    ).done(function(allResp, collResp) {
        const allFolders = (allResp[0].success && allResp[0].root_folders) ? allResp[0].root_folders : [];
        const collFolders = (collResp[0].success && collResp[0].root_folders) ? collResp[0].root_folders : [];

        const collIds = new Set(collFolders.map(f => f.id));
        const available = allFolders.filter(f => !collIds.has(f.id));

        const select = $('#selectRootFolder');
        select.empty();
        if (available.length === 0) {
            select.append('<option value="" disabled selected>No available root folders to link</option>');
        } else {
            available.forEach(f => {
                const label = `${f.name} — ${f.path}`;
                select.append(`<option value="${f.id}">${label}</option>`);
            });
        }
        
        // Ensure select is interactive
        select.css({
            'pointer-events': 'auto',
            'position': 'relative',
            'z-index': '1051'
        });
    }).fail(function() {
        showError('Failed to load root folders.');
    });
});

// Confirm linking selected root folder to the current collection
$(document).on('click', '#confirmLinkRootFolderBtn', function () {
    const rootFolderId = $('#selectRootFolder').val();
    if (!window.selectedCollectionId || !rootFolderId) {
        showError('Please select a root folder.');
        return;
    }

    const btn = $(this);
    const original = btn.text();
    btn.prop('disabled', true).text('Linking...');

    $.ajax({
        url: `/api/collections/${window.selectedCollectionId}/root-folders/${rootFolderId}`,
        method: 'POST',
        success: function(response) {
            if (response.success) {
                // Properly close the modal and clean up backdrop
                const modalElement = document.getElementById('linkRootFolderModal');
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
                // Remove any lingering backdrop
                $('.modal-backdrop').remove();
                $('body').removeClass('modal-open');
                
                loadCollectionRootFolders(window.selectedCollectionId);
                showSuccess('Root folder linked to collection successfully');
            } else {
                showError('Failed to link root folder: ' + (response.error || 'Unknown error'));
            }
        },
        error: function(xhr, status, error) {
            showError('Failed to link root folder: ' + error);
        },
        complete: function() {
            btn.prop('disabled', false).text(original);
        }
    });
});

// Clean up modal backdrop when modal is hidden
$(document).on('hidden.bs.modal', '#linkRootFolderModal', function () {
    // Remove any lingering backdrops
    $('.modal-backdrop').remove();
    // Ensure body doesn't have modal-open class if no modals are open
    if ($('.modal.show').length === 0) {
        $('body').removeClass('modal-open');
    }
});

/**
 * Load root folders from the API
 */
function loadRootFolders() {
    $.ajax({
        url: '/api/root-folders',
        method: 'GET',
        success: function(response) {
            if (response.success && response.root_folders) {
                displayRootFolders(response.root_folders);
            } else {
                console.error('Error loading root folders:', response);
                $('#rootFoldersTableBody').html('<tr><td colspan="5" class="text-center text-danger">Failed to load root folders</td></tr>');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading root folders:', error);
            $('#rootFoldersTableBody').html('<tr><td colspan="5" class="text-center text-danger">Failed to load root folders</td></tr>');
        }
    });
    
    // Log to console for debugging
    console.log('Loading root folders...');
}

/**
 * Display root folders in the table
 */
function displayRootFolders(rootFolders) {
    const tbody = $('#rootFoldersTableBody');
    tbody.empty();
    
    if (rootFolders.length === 0) {
        tbody.html('<tr><td colspan="5" class="text-center">No root folders found</td></tr>');
        return;
    }
    
    rootFolders.forEach(function(folder) {
        const row = $('<tr>');
        
        // Name
        row.append($('<td>').text(folder.name));
        
        // Path
        row.append($('<td>').text(folder.path));
        
        // Content Type
        row.append($('<td>').text(folder.content_type || 'MANGA'));
        
        // Status
        row.append($('<td>').html('<span class="badge bg-success">OK</span>'));
        
        // Actions
        const actionsCell = $('<td>');
        
        // Edit button
        const editBtn = $('<button>')
            .addClass('btn btn-sm btn-primary me-1')
            .html('<i class="fas fa-edit"></i>')
            .attr('title', 'Edit')
            .data('id', folder.id)
            .click(function() {
                editRootFolder(folder);
            });
        
        // Delete button
        const deleteBtn = $('<button>')
            .addClass('btn btn-sm btn-danger')
            .html('<i class="fas fa-trash"></i>')
            .attr('title', 'Delete')
            .data('id', folder.id)
            .click(function() {
                confirmDeleteRootFolder(folder);
            });
        
        actionsCell.append(editBtn, deleteBtn);
        row.append(actionsCell);
        
        tbody.append(row);
    });
}

/**
 * View collection details
 */
function viewCollectionDetails(collectionId) {
    // Show the collection details card
    $('#collectionDetailsCard').removeClass('d-none');
    window.selectedCollectionId = collectionId;
    
    // Load collection details
    $.ajax({
        url: `/api/collections/${collectionId}`,
        method: 'GET',
        success: function(response) {
            if (response.success && response.collection) {
                const collection = response.collection;
                $('#selectedCollectionName').text(collection.name);
                
                // Load root folders for this collection
                loadCollectionRootFolders(collectionId);
                
                // Load series for this collection
                loadCollectionSeries(collectionId);
            } else {
                console.error('Error loading collection details:', response);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading collection details:', error);
        }
    });
}

/**
 * Load root folders for a specific collection
 */
function loadCollectionRootFolders(collectionId) {
    $.ajax({
        url: `/api/collections/${collectionId}/root-folders`,
        method: 'GET',
        success: function(response) {
            if (response.success && response.root_folders) {
                displayCollectionRootFolders(response.root_folders, collectionId);
            } else {
                console.error('Error loading collection root folders:', response);
                $('#collectionRootFoldersTableBody').html('<tr><td colspan="3" class="text-center text-danger">Failed to load root folders</td></tr>');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading collection root folders:', error);
            $('#collectionRootFoldersTableBody').html('<tr><td colspan="3" class="text-center text-danger">Failed to load root folders</td></tr>');
        }
    });
}

/**
 * Display root folders for a specific collection
 */
function displayCollectionRootFolders(rootFolders, collectionId) {
    const tbody = $('#collectionRootFoldersTableBody');
    tbody.empty();
    
    if (rootFolders.length === 0) {
        tbody.html('<tr><td colspan="3" class="text-center">No root folders in this collection</td></tr>');
        return;
    }
    
    rootFolders.forEach(function(folder) {
        const row = $('<tr>');
        
        // Name
        row.append($('<td>').text(folder.name));
        
        // Path
        row.append($('<td>').text(folder.path));
        
        // Actions
        const actionsCell = $('<td>');
        
        // Remove button
        const removeBtn = $('<button>')
            .addClass('btn btn-sm btn-danger')
            .html('<i class="fas fa-unlink"></i>')
            .attr('title', 'Remove from Collection')
            .data('id', folder.id)
            .click(function() {
                removeRootFolderFromCollection(collectionId, folder.id);
            });
        
        actionsCell.append(removeBtn);
        row.append(actionsCell);
        
        tbody.append(row);
    });
}

/**
 * Load series for a specific collection
 */
function loadCollectionSeries(collectionId) {
    $.ajax({
        url: `/api/collections/${collectionId}/series`,
        method: 'GET',
        success: function(response) {
            if (response.success && response.series) {
                displayCollectionSeries(response.series, collectionId);
            } else {
                console.error('Error loading collection series:', response);
                $('#collectionSeriesTableBody').html('<tr><td colspan="3" class="text-center text-danger">Failed to load series</td></tr>');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading collection series:', error);
            $('#collectionSeriesTableBody').html('<tr><td colspan="3" class="text-center text-danger">Failed to load series</td></tr>');
        }
    });
}

/**
 * Display series for a specific collection
 */
function displayCollectionSeries(series, collectionId) {
    const tbody = $('#collectionSeriesTableBody');
    tbody.empty();
    
    if (series.length === 0) {
        tbody.html('<tr><td colspan="3" class="text-center">No series in this collection</td></tr>');
        return;
    }
    
    series.forEach(function(item) {
        const row = $('<tr>');
        
        // Title
        row.append($('<td>').text(item.title));
        
        // Type
        row.append($('<td>').text(item.type || 'MANGA'));
        
        // Actions
        const actionsCell = $('<td>');
        
        // View button
        const viewBtn = $('<button>')
            .addClass('btn btn-sm btn-info me-1')
            .html('<i class="fas fa-eye"></i>')
            .attr('title', 'View Series')
            .data('id', item.id)
            .click(function() {
                window.location.href = `/series/${item.id}`;
            });
        
        // Remove button
        const removeBtn = $('<button>')
            .addClass('btn btn-sm btn-danger')
            .html('<i class="fas fa-unlink"></i>')
            .attr('title', 'Remove from Collection')
            .data('id', item.id)
            .click(function() {
                removeSeriesFromCollection(collectionId, item.id);
            });
        
        actionsCell.append(viewBtn, removeBtn);
        row.append(actionsCell);
        
        tbody.append(row);
    });
}

/**
 * Save a new collection
 */
function saveCollection() {
    const name = $('#collectionName').val().trim();
    const description = $('#collectionDescription').val().trim();
    const isDefault = $('#collectionIsDefault').is(':checked');
    const contentType = $('#collectionContentType').val();
    
    // Clear previous errors
    clearCollectionErrors('add');
    
    // Validate required fields
    let hasErrors = false;
    
    if (!name) {
        showCollectionError('add', 'collectionName', 'Collection name is required');
        hasErrors = true;
    }
    
    if (!contentType) {
        showCollectionError('add', 'collectionContentType', 'Content type is required');
        hasErrors = true;
    }
    
    if (hasErrors) {
        return;
    }
    
    // Disable button and show loading
    const saveBtn = $('#saveCollectionBtn');
    const originalText = saveBtn.text();
    saveBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...');
    
    $.ajax({
        url: '/api/collections',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            name: name,
            description: description,
            is_default: isDefault,
            content_type: contentType
        }),
        success: function(response) {
            if (response.success) {
                // Reset form
                $('#collectionName').val('');
                $('#collectionDescription').val('');
                $('#collectionIsDefault').prop('checked', false);
                clearCollectionErrors('add');
                
                // Close modal
                $('#addCollectionModal').modal('hide');
                
                // Reload collections
                loadCollections();
                
                // Show success message
                showSuccess('Collection created successfully');
            } else {
                console.error('Error creating collection:', response);
                
                // Handle API errors
                if (response.error) {
                    // Check if it's a duplicate name/type error
                    if (response.error.includes('already exists') || response.error.includes('duplicate')) {
                        showCollectionError('add', 'collectionName', response.error);
                    } else {
                        showError('Failed to create collection: ' + response.error);
                    }
                } else {
                    showError('Failed to create collection: Unknown error');
                }
            }
        },
        error: function(xhr, status, error) {
            console.error('Error creating collection:', error);
            
            // Handle HTTP error responses
            if (xhr.responseJSON && xhr.responseJSON.error) {
                const errorMsg = xhr.responseJSON.error;
                if (errorMsg.includes('already exists') || errorMsg.includes('duplicate')) {
                    showCollectionError('add', 'collectionName', errorMsg);
                } else {
                    showError('Failed to create collection: ' + errorMsg);
                }
            } else {
                showError('Failed to create collection: ' + error);
            }
        },
        complete: function() {
            // Reset button
            saveBtn.prop('disabled', false).text(originalText);
        }
    });
}

/**
 * Edit a collection
 */
function editCollection(collection) {
    // Fill the edit form
    $('#editCollectionId').val(collection.id);
    $('#editCollectionName').val(collection.name);
    $('#editCollectionDescription').val(collection.description || '');
    $('#editCollectionIsDefault').prop('checked', collection.is_default);
    $('#editCollectionContentType').val(collection.content_type || 'MANGA');
    
    // Show the modal
    $('#editCollectionModal').modal('show');
}

/**
 * Update a collection
 */
function updateCollection() {
    const id = $('#editCollectionId').val();
    const name = $('#editCollectionName').val().trim();
    const description = $('#editCollectionDescription').val().trim();
    const isDefault = $('#editCollectionIsDefault').is(':checked');
    const contentType = $('#editCollectionContentType').val();
    
    // Clear previous errors
    clearCollectionErrors('edit');
    
    // Validate required fields
    let hasErrors = false;
    
    if (!name) {
        showCollectionError('edit', 'editCollectionName', 'Collection name is required');
        hasErrors = true;
    }
    
    if (!contentType) {
        showCollectionError('edit', 'editCollectionContentType', 'Content type is required');
        hasErrors = true;
    }
    
    if (hasErrors) {
        return;
    }
    
    // Disable button and show loading
    const updateBtn = $('#updateCollectionBtn');
    const originalText = updateBtn.text();
    updateBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...');
    
    $.ajax({
        url: `/api/collections/${id}`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify({
            name: name,
            description: description,
            is_default: isDefault,
            content_type: contentType
        }),
        success: function(response) {
            if (response.success) {
                // Close modal
                $('#editCollectionModal').modal('hide');
                clearCollectionErrors('edit');
                
                // Reload collections
                loadCollections();
                
                // Show success message
                showSuccess('Collection updated successfully');
            } else {
                console.error('Error updating collection:', response);
                
                // Handle API errors
                if (response.error) {
                    // Check if it's a duplicate name/type error
                    if (response.error.includes('already exists') || response.error.includes('duplicate')) {
                        showCollectionError('edit', 'editCollectionName', response.error);
                    } else {
                        showError('Failed to update collection: ' + response.error);
                    }
                } else {
                    showError('Failed to update collection: Unknown error');
                }
            }
        },
        error: function(xhr, status, error) {
            console.error('Error updating collection:', error);
            
            // Handle HTTP error responses
            if (xhr.responseJSON && xhr.responseJSON.error) {
                const errorMsg = xhr.responseJSON.error;
                if (errorMsg.includes('already exists') || errorMsg.includes('duplicate')) {
                    showCollectionError('edit', 'editCollectionName', errorMsg);
                } else {
                    showError('Failed to update collection: ' + errorMsg);
                }
            } else {
                showError('Failed to update collection: ' + error);
            }
        },
        complete: function() {
            // Reset button
            updateBtn.prop('disabled', false).text(originalText);
        }
    });
}

/**
 * Confirm delete collection
 */
async function confirmDeleteCollection(collection) {
    const confirmed = await showConfirm(`Are you sure you want to delete the collection "${collection.name}"?`);
    if (confirmed) {
        deleteCollection(collection.id);
    }
}

/**
 * Delete a collection
 */
function deleteCollection(id) {
    $.ajax({
        url: `/api/collections/${id}`,
        method: 'DELETE',
        success: function(response) {
            if (response.success) {
                // Reload collections
                loadCollections();
                
                // Show success message
                showSuccess('Collection deleted successfully');
            } else {
                console.error('Error deleting collection:', response);
                showError('Failed to delete collection: ' + (response.error || 'Unknown error'));
            }
        },
        error: function(xhr, status, error) {
            console.error('Error deleting collection:', error);
            showError('Failed to delete collection: ' + error);
        }
    });
}

/**
 * Save a new root folder
 */
function saveRootFolder() {
    const name = $('#rootFolderName').val().trim();
    const path = $('#rootFolderPath').val().trim();
    const contentType = $('#rootFolderContentType').val();
    
    if (!name || !path) {
        showError('Root folder name and path are required');
        return;
    }
    
    // Disable button and show loading
    const saveBtn = $('#saveRootFolderBtn');
    const originalText = saveBtn.text();
    saveBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...');
    
    $.ajax({
        url: '/api/root-folders',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            name: name,
            path: path,
            content_type: contentType
        }),
        success: function(response) {
            if (response.success) {
                // Reset form
                $('#rootFolderName').val('');
                $('#rootFolderPath').val('');
                $('#folderValidationStatus').empty();
                
                // Close modal
                $('#addRootFolderModal').modal('hide');
                
                // Reload root folders
                loadRootFolders();
                
                // Show success message
                showSuccess('Root folder created successfully');
            } else {
                console.error('Error creating root folder:', response);
                showError('Failed to create root folder: ' + (response.error || 'Unknown error'));
            }
        },
        error: function(xhr, status, error) {
            console.error('Error creating root folder:', error);
            let errorMsg = 'Failed to create root folder';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMsg = xhr.responseJSON.error;
            }
            showError(errorMsg);
        },
        complete: function() {
            // Reset button
            saveBtn.prop('disabled', false).text(originalText);
        }
    });
}

/**
 * Edit a root folder
 */
function editRootFolder(folder) {
    // Fill the edit form
    $('#editRootFolderId').val(folder.id);
    $('#editRootFolderName').val(folder.name);
    $('#editRootFolderPath').val(folder.path);
    $('#editRootFolderContentType').val(folder.content_type || 'MANGA');
    
    // Show the modal
    $('#editRootFolderModal').modal('show');
}

/**
 * Update a root folder
 */
function updateRootFolder() {
    const id = $('#editRootFolderId').val();
    const name = $('#editRootFolderName').val().trim();
    const path = $('#editRootFolderPath').val().trim();
    const contentType = $('#editRootFolderContentType').val();
    
    if (!name || !path) {
        showError('Root folder name and path are required');
        return;
    }
    
    // Disable button and show loading
    const updateBtn = $('#updateRootFolderBtn');
    const originalText = updateBtn.text();
    updateBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...');
    
    $.ajax({
        url: `/api/root-folders/${id}`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify({
            name: name,
            path: path,
            content_type: contentType
        }),
        success: function(response) {
            if (response.success) {
                // Close modal
                $('#editRootFolderModal').modal('hide');
                
                // Reload root folders
                loadRootFolders();
                
                // Show success message
                showSuccess('Root folder updated successfully');
            } else {
                console.error('Error updating root folder:', response);
                showError('Failed to update root folder: ' + (response.error || 'Unknown error'));
            }
        },
        error: function(xhr, status, error) {
            console.error('Error updating root folder:', error);
            showError('Failed to update root folder: ' + error);
        },
        complete: function() {
            // Reset button
            updateBtn.prop('disabled', false).text(originalText);
        }
    });
}

/**
 * Confirm delete root folder
 */
async function confirmDeleteRootFolder(folder) {
    const confirmed = await showConfirm(`Are you sure you want to delete the root folder "${folder.name}"?`);
    if (confirmed) {
        deleteRootFolder(folder.id);
    }
}

/**
 * Delete a root folder
 */
function deleteRootFolder(id) {
    $.ajax({
        url: `/api/root-folders/${id}`,
        method: 'DELETE',
        success: function(response) {
            if (response.success) {
                // Reload root folders
                loadRootFolders();
                
                // Show success message
                showSuccess('Root folder deleted successfully');
            } else {
                console.error('Error deleting root folder:', response);
                showError('Failed to delete root folder: ' + (response.error || 'Unknown error'));
            }
        },
        error: function(xhr, status, error) {
            console.error('Error deleting root folder:', error);
            showError('Failed to delete root folder: ' + error);
        }
    });
}

/**
 * Remove a root folder from a collection
 */
async function removeRootFolderFromCollection(collectionId, rootFolderId) {
    const confirmed = await showConfirm('Are you sure you want to remove this root folder from the collection?');
    if (confirmed) {
        $.ajax({
            url: `/api/collections/${collectionId}/root-folders/${rootFolderId}`,
            method: 'DELETE',
            success: function(response) {
                if (response.success) {
                    // Reload collection root folders
                    loadCollectionRootFolders(collectionId);
                    
                    // Show success message
                    showSuccess('Root folder removed from collection successfully');
                } else {
                    console.error('Error removing root folder from collection:', response);
                    showError('Failed to remove root folder from collection: ' + (response.error || 'Unknown error'));
                }
            },
            error: function(xhr, status, error) {
                console.error('Error removing root folder from collection:', error);
                showError('Failed to remove root folder from collection: ' + error);
            }
        });
    }
}

/**
 * Remove a series from a collection
 */
async function removeSeriesFromCollection(collectionId, seriesId) {
    const confirmed = await showConfirm('Are you sure you want to remove this series from the collection?');
    if (confirmed) {
        $.ajax({
            url: `/api/collections/${collectionId}/series/${seriesId}`,
            method: 'DELETE',
            success: function(response) {
                if (response.success) {
                    // Reload collection series
                    loadCollectionSeries(collectionId);
                    
                    // Show success message
                    showSuccess('Series removed from collection successfully');
                } else {
                    console.error('Error removing series from collection:', response);
                    showError('Failed to remove series from collection: ' + (response.error || 'Unknown error'));
                }
            },
            error: function(xhr, status, error) {
                console.error('Error removing series from collection:', error);
                showError('Failed to remove series from collection: ' + error);
            }
        });
    }
}

// Set up event handlers for collection update
$(document).ready(function() {
    $('#updateCollectionBtn').click(function() {
        updateCollection();
    });
    
    // Set up event handlers for root folder update
    $('#updateRootFolderBtn').click(function() {
        updateRootFolder();
    });
});

/**
 * Show inline error message for a collection form field
 * @param {string} formType - 'add' or 'edit'
 * @param {string} fieldId - The ID of the input field
 * @param {string} message - The error message to display
 */
function showCollectionError(formType, fieldId, message) {
    const $field = $(`#${fieldId}`);
    const $errorDiv = $(`#${fieldId}Error`);
    
    // Add error styling to the field
    $field.addClass('is-invalid');
    
    // Display the error message
    $errorDiv.text(message).show();
}

/**
 * Clear all error messages for a collection form
 * @param {string} formType - 'add' or 'edit'
 */
function clearCollectionErrors(formType) {
    if (formType === 'add') {
        // Clear Add Collection form errors
        $('#collectionName').removeClass('is-invalid');
        $('#collectionContentType').removeClass('is-invalid');
        $('#collectionNameError').text('').hide();
        $('#collectionContentTypeError').text('').hide();
    } else if (formType === 'edit') {
        // Clear Edit Collection form errors
        $('#editCollectionName').removeClass('is-invalid');
        $('#editCollectionContentType').removeClass('is-invalid');
        $('#editCollectionNameError').text('').hide();
        $('#editCollectionContentTypeError').text('').hide();
    }
}

/**
 * Clear errors when modal is opened (fresh start)
 */
$(document).on('show.bs.modal', '#addCollectionModal', function() {
    clearCollectionErrors('add');
    // Reset form fields
    $('#addCollectionForm')[0].reset();
});

$(document).on('show.bs.modal', '#editCollectionModal', function() {
    clearCollectionErrors('edit');
});
