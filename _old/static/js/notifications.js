/**
 * Centralized notification system for Readloom
 * Provides toast notifications instead of browser popups
 */

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of notification: 'success', 'error', 'warning', 'info'
 * @param {number} duration - Duration in milliseconds (0 = no auto-hide)
 */
function showToast(message, type = 'info', duration = 5000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }

    // Create a unique ID for this toast
    const toastId = 'toast-' + Date.now() + Math.random();

    // Determine the background color based on type
    let bgClass = 'bg-info';
    let icon = 'ℹ️';
    
    switch (type) {
        case 'success':
            bgClass = 'bg-success';
            icon = '✓';
            break;
        case 'error':
            bgClass = 'bg-danger';
            icon = '✕';
            break;
        case 'warning':
            bgClass = 'bg-warning text-dark';
            icon = '⚠';
            break;
        case 'info':
        default:
            bgClass = 'bg-info';
            icon = 'ℹ️';
    }

    // Create the toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center ${bgClass} text-white`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.style.minWidth = '300px';

    // Create the toast content
    const toastContent = document.createElement('div');
    toastContent.className = 'd-flex';

    // Create the toast body
    const toastBody = document.createElement('div');
    toastBody.className = 'toast-body';
    toastBody.innerHTML = `<span style="margin-right: 10px;">${icon}</span>${escapeHtml(message)}`;

    // Create the close button
    const closeButton = document.createElement('button');
    closeButton.className = 'btn-close btn-close-white me-2 m-auto';
    closeButton.setAttribute('data-bs-dismiss', 'toast');
    closeButton.setAttribute('aria-label', 'Close');

    // Assemble the toast
    toastContent.appendChild(toastBody);
    toastContent.appendChild(closeButton);
    toast.appendChild(toastContent);

    // Add the toast to the container
    toastContainer.appendChild(toast);

    // Initialize and show the toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: duration > 0,
        delay: duration
    });
    bsToast.show();

    // Remove the toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });

    return toast;
}

/**
 * Show a success notification
 * @param {string} message - The message to display
 * @param {number} duration - Duration in milliseconds
 */
function showSuccess(message, duration = 5000) {
    return showToast(message, 'success', duration);
}

/**
 * Show an error notification
 * @param {string} message - The message to display
 * @param {number} duration - Duration in milliseconds (0 = no auto-hide)
 */
function showError(message, duration = 0) {
    return showToast(message, 'error', duration);
}

/**
 * Show a warning notification
 * @param {string} message - The message to display
 * @param {number} duration - Duration in milliseconds
 */
function showWarning(message, duration = 5000) {
    return showToast(message, 'warning', duration);
}

/**
 * Show an info notification
 * @param {string} message - The message to display
 * @param {number} duration - Duration in milliseconds
 */
function showInfo(message, duration = 5000) {
    return showToast(message, 'info', duration);
}

/**
 * Show a confirmation dialog as a modal
 * @param {string} title - The title of the confirmation dialog
 * @param {string} message - The message to display
 * @param {string} confirmText - The text for the confirm button (default: "Confirm")
 * @param {string} cancelText - The text for the cancel button (default: "Cancel")
 * @returns {Promise<boolean>} - Resolves to true if confirmed, false if cancelled
 */
function showConfirm(title, message, confirmText = 'Confirm', cancelText = 'Cancel') {
    return new Promise((resolve) => {
        // Create modal if it doesn't exist
        let confirmModal = document.getElementById('confirm-modal');
        if (!confirmModal) {
            confirmModal = document.createElement('div');
            confirmModal.id = 'confirm-modal';
            confirmModal.className = 'modal fade';
            confirmModal.setAttribute('tabindex', '-1');
            confirmModal.setAttribute('aria-hidden', 'true');
            confirmModal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="confirm-modal-title"></h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body" id="confirm-modal-body"></div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" id="confirm-modal-cancel"></button>
                            <button type="button" class="btn btn-primary" id="confirm-modal-confirm"></button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(confirmModal);
        }

        // Set the content
        document.getElementById('confirm-modal-title').textContent = title;
        document.getElementById('confirm-modal-body').textContent = message;
        document.getElementById('confirm-modal-confirm').textContent = confirmText;
        document.getElementById('confirm-modal-cancel').textContent = cancelText;

        // Set up event handlers
        const confirmBtn = document.getElementById('confirm-modal-confirm');
        const cancelBtn = document.getElementById('confirm-modal-cancel');
        const modal = new bootstrap.Modal(confirmModal);

        const handleConfirm = () => {
            modal.hide();
            confirmBtn.removeEventListener('click', handleConfirm);
            cancelBtn.removeEventListener('click', handleCancel);
            confirmModal.removeEventListener('hidden.bs.modal', handleCancel);
            resolve(true);
        };

        const handleCancel = () => {
            modal.hide();
            confirmBtn.removeEventListener('click', handleConfirm);
            cancelBtn.removeEventListener('click', handleCancel);
            confirmModal.removeEventListener('hidden.bs.modal', handleCancel);
            resolve(false);
        };

        confirmBtn.addEventListener('click', handleConfirm);
        cancelBtn.addEventListener('click', handleCancel);
        confirmModal.addEventListener('hidden.bs.modal', handleCancel);

        modal.show();
    });
}

/**
 * Escape HTML special characters to prevent XSS
 * @param {string} text - The text to escape
 * @returns {string} - The escaped text
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
