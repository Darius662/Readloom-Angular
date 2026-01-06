/**
 * Folder Browser Module
 * Provides folder browsing functionality across the application
 */

class FolderBrowser {
    constructor(options = {}) {
        this.currentPath = null;
        this.selectedPath = null;
        this.targetInputId = options.targetInputId || null;
        this.targetNameInputId = options.targetNameInputId || null;
        this.browseBtnId = options.browseBtnId || null;
        this.pickerInputId = options.pickerInputId || null;
        this.modalId = options.modalId || 'folderBrowserModal';
        this.onSelect = options.onSelect || null;
    }

    /**
     * Initialize the folder browser
     */
    init() {
        if (this.browseBtnId) {
            const browseBtn = document.getElementById(this.browseBtnId);
            if (browseBtn) {
                browseBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.open();
                });
            }
        }
    }

    /**
     * Open the folder browser modal
     */
    open() {
        this.selectedPath = null;
        this.browseFolders(null);
        
        // Show modal if it exists
        const modal = document.getElementById(this.modalId);
        if (modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        }
    }

    /**
     * Browse folders at a specific path
     */
    browseFolders(path) {
        fetch('/api/folders/browse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ path: path })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.currentPath = data.current_path;
                // If we can't go up, disable the up button
                if (!data.can_go_up) {
                    data.can_go_up = false;
                }
                this.updateBrowserUI(data);
            } else {
                alert('Error browsing folders: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error browsing folders:', error);
            alert('Failed to browse folders');
        });
    }

    /**
     * Update the browser UI with folder data
     */
    updateBrowserUI(data) {
        // Update current path display
        const currentPathInput = document.getElementById('browser-current-path');
        if (currentPathInput) {
            currentPathInput.value = data.current_path;
        }

        // Update drives/root list
        const drivesContainer = document.getElementById('browser-drives');
        if (drivesContainer) {
            if (data.drives && data.drives.length > 0) {
                drivesContainer.style.display = 'block';
                const drivesList = document.getElementById('drives-list');
                drivesList.innerHTML = '';
                data.drives.forEach(drive => {
                    const btn = document.createElement('button');
                    btn.className = 'btn btn-sm btn-outline-secondary';
                    // Display drive letter or root symbol
                    btn.textContent = drive === '/' ? 'Root (/)' : drive;
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        this.browseFolders(drive);
                    });
                    drivesList.appendChild(btn);
                });
            } else {
                drivesContainer.style.display = 'none';
            }
        }

        // Update up button state
        const upBtn = document.getElementById('browser-up-btn');
        if (upBtn) {
            upBtn.disabled = !data.can_go_up;
        }

        // Update folders list
        const foldersList = document.getElementById('browser-folders-list');
        if (foldersList) {
            foldersList.innerHTML = '';

            if (data.folders && data.folders.length > 0) {
                data.folders.forEach(folder => {
                    const btn = document.createElement('button');
                    btn.className = 'list-group-item list-group-item-action text-start';
                    btn.innerHTML = '<i class="fas fa-folder me-2"></i>' + folder.name;
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        this.browseFolders(folder.path);
                    });
                    foldersList.appendChild(btn);
                });

                // Add option to select current folder
                const selectBtn = document.createElement('button');
                selectBtn.className = 'list-group-item list-group-item-action text-start bg-light border-top mt-2';
                selectBtn.innerHTML = '<i class="fas fa-check me-2"></i><strong>Select this folder</strong>';
                selectBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.selectFolder(data.current_path);
                });
                foldersList.appendChild(selectBtn);
            } else {
                foldersList.innerHTML = '<div class="text-center text-muted py-3">No folders found</div>';

                // Still allow selecting current folder if empty
                const selectBtn = document.createElement('button');
                selectBtn.className = 'list-group-item list-group-item-action text-start bg-light';
                selectBtn.innerHTML = '<i class="fas fa-check me-2"></i><strong>Select this folder</strong>';
                selectBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.selectFolder(data.current_path);
                });
                foldersList.appendChild(selectBtn);
            }
        }
    }

    /**
     * Select a folder
     */
    selectFolder(path) {
        this.selectedPath = path;

        // Update selected path display
        const selectedPathInput = document.getElementById('browser-selected-path');
        if (selectedPathInput) {
            selectedPathInput.value = path;
        }

        // Enable select button
        const selectBtn = document.getElementById('browser-select-btn');
        if (selectBtn) {
            selectBtn.disabled = false;
        }
    }

    /**
     * Confirm selection and fill the target input
     */
    confirmSelection() {
        if (this.selectedPath && this.targetInputId) {
            const targetInput = document.getElementById(this.targetInputId);
            if (targetInput) {
                targetInput.value = this.selectedPath;

                // Auto-fill name if provided
                if (this.targetNameInputId) {
                    const nameInput = document.getElementById(this.targetNameInputId);
                    if (nameInput && !nameInput.value) {
                        const folderName = this.selectedPath.split('/').pop() || this.selectedPath.split('\\').pop();
                        nameInput.value = folderName;
                    }
                }

                // Call custom callback if provided
                if (this.onSelect) {
                    this.onSelect(this.selectedPath);
                }
            }

            // Close modal
            const modal = document.getElementById(this.modalId);
            if (modal) {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            }
        }
    }
}

/**
 * Setup folder browser for a specific input
 */
function setupFolderBrowser(options) {
    const browser = new FolderBrowser(options);
    browser.init();
    return browser;
}

/**
 * Global folder browser instances
 */
const folderBrowsers = {};

/**
 * Initialize all folder browsers on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Setup select button handler
    const selectBtn = document.getElementById('browser-select-btn');
    if (selectBtn) {
        selectBtn.addEventListener('click', function() {
            // Find the active browser instance
            // For now, we'll use a simple approach - the last created browser
            if (window.activeFolderBrowser) {
                window.activeFolderBrowser.confirmSelection();
            }
        });
    }

    // Setup navigation buttons
    const homeBtn = document.getElementById('browser-home-btn');
    if (homeBtn) {
        homeBtn.addEventListener('click', function() {
            if (window.activeFolderBrowser) {
                window.activeFolderBrowser.browseFolders(null);
            }
        });
    }

    const upBtn = document.getElementById('browser-up-btn');
    if (upBtn) {
        upBtn.addEventListener('click', function() {
            if (window.activeFolderBrowser && window.activeFolderBrowser.currentPath) {
                const parentPath = window.activeFolderBrowser.currentPath.substring(0, window.activeFolderBrowser.currentPath.lastIndexOf('/'));
                window.activeFolderBrowser.browseFolders(parentPath || '/');
            }
        });
    }
});
