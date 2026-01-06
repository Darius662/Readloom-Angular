/**
 * In-App Notification System
 * Replaces browser alerts, confirms, and other popups with elegant toast notifications
 */

class NotificationManager {
    constructor() {
        this.container = null;
        this.notifications = [];
        this.pendingNotificationsKey = 'readloom_pending_notifications';
        this.initContainer();
        this.restorePersistentNotifications();
    }

    initContainer() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
            this.container = container;
        } else {
            this.container = document.getElementById('notification-container');
        }
    }

    /**
     * Restore persistent notifications from localStorage after page reload/navigation
     */
    restorePersistentNotifications() {
        try {
            const stored = localStorage.getItem(this.pendingNotificationsKey);
            if (stored) {
                const pending = JSON.parse(stored);
                pending.forEach(notif => {
                    // Calculate remaining time based on timestamp
                    let remainingDuration = notif.duration;
                    if (notif.timestamp) {
                        const elapsed = Date.now() - notif.timestamp;
                        remainingDuration = Math.max(0, notif.duration - elapsed);
                    }
                    
                    // Only show if there's still time remaining
                    if (remainingDuration > 0) {
                        // Skip animation for restored notifications (skipAnimation = true)
                        this.show(notif.message, notif.type, remainingDuration, null, false, true);
                    }
                });
                // Clear after restoring
                localStorage.removeItem(this.pendingNotificationsKey);
            }
        } catch (e) {
            console.error('Error restoring persistent notifications:', e);
        }
    }

    /**
     * Store notification in localStorage for persistence across page navigation
     * @param {string} message - Notification message
     * @param {string} type - Type: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duration in ms
     * @param {number} remainingTime - Remaining time in ms (for timer continuation)
     */
    storePersistentNotification(message, type, duration, remainingTime = null) {
        try {
            const pending = [];
            const stored = localStorage.getItem(this.pendingNotificationsKey);
            if (stored) {
                pending.push(...JSON.parse(stored));
            }
            pending.push({ 
                message, 
                type, 
                duration: remainingTime || duration,
                timestamp: Date.now()
            });
            localStorage.setItem(this.pendingNotificationsKey, JSON.stringify(pending));
        } catch (e) {
            console.error('Error storing persistent notification:', e);
        }
    }

    /**
     * Show a notification
     * @param {string} message - Notification message
     * @param {string} type - Type: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duration in ms (0 = no auto-dismiss)
     * @param {function} onClose - Callback when notification closes
     * @param {boolean} showTimer - Whether to show the timer (default: true for non-confirmation notifications)
     * @param {boolean} skipAnimation - Whether to skip the slide-in animation (for restored notifications)
     */
    show(message, type = 'info', duration = 5000, onClose = null, showTimer = true, skipAnimation = false) {
        const notification = document.createElement('div');
        const id = `notification-${Date.now()}-${Math.random()}`;
        notification.id = id;
        notification.className = `notification notification-${type}`;

        // Icon mapping
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        // Calculate timer display (only show if showTimer is true and duration > 0)
        const timerDuration = (showTimer && duration > 0) ? Math.ceil(duration / 1000) : 0;

        notification.innerHTML = `
            <div class="notification-content">
                <i class="notification-icon ${icons[type]}"></i>
                <div class="notification-body">
                    <span class="notification-message">${this.escapeHtml(message)}</span>
                    ${timerDuration > 0 ? `<div class="notification-timer"><span class="timer-value">${timerDuration}</span>s</div>` : ''}
                </div>
                <button class="notification-close" aria-label="Close notification">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Close button handler
        notification.querySelector('.notification-close').addEventListener('click', () => {
            this.dismiss(id, onClose);
        });

        // Add to container
        this.container.appendChild(notification);
        this.notifications.push(id);

        // Trigger animation (skip for restored notifications)
        if (skipAnimation) {
            notification.classList.add('show');
        } else {
            setTimeout(() => {
                notification.classList.add('show');
            }, 10);
        }

        // Timer countdown
        if (duration > 0) {
            let remaining = timerDuration;
            const timerElement = notification.querySelector('.timer-value');
            
            const countdownInterval = setInterval(() => {
                remaining--;
                if (timerElement) {
                    timerElement.textContent = remaining;
                }
                if (remaining <= 0) {
                    clearInterval(countdownInterval);
                }
            }, 1000);

            // Auto-dismiss
            setTimeout(() => {
                clearInterval(countdownInterval);
                this.dismiss(id, onClose);
            }, duration);
        }

        return id;
    }

    /**
     * Show success notification
     * @param {string} message - Notification message
     * @param {number} duration - Duration in ms (default: 5000)
     * @param {function} onClose - Callback when notification closes
     * @param {boolean} persistent - Whether to persist across page navigation (default: false)
     */
    success(message, duration = 5000, onClose = null, persistent = false) {
        if (persistent) {
            this.storePersistentNotification(message, 'success', duration);
        }
        return this.show(message, 'success', duration, onClose, false);
    }

    /**
     * Show error notification
     * @param {string} message - Notification message
     * @param {number} duration - Duration in ms (default: 5000)
     * @param {function} onClose - Callback when notification closes
     * @param {boolean} persistent - Whether to persist across page navigation (default: false)
     */
    error(message, duration = 5000, onClose = null, persistent = false) {
        if (persistent) {
            this.storePersistentNotification(message, 'error', duration);
        }
        return this.show(message, 'error', duration, onClose, false);
    }

    /**
     * Show warning notification
     * @param {string} message - Notification message
     * @param {number} duration - Duration in ms (default: 5000)
     * @param {function} onClose - Callback when notification closes
     * @param {boolean} persistent - Whether to persist across page navigation (default: false)
     */
    warning(message, duration = 5000, onClose = null, persistent = false) {
        if (persistent) {
            this.storePersistentNotification(message, 'warning', duration);
        }
        return this.show(message, 'warning', duration, onClose, false);
    }

    /**
     * Show info notification
     * @param {string} message - Notification message
     * @param {number} duration - Duration in ms (default: 5000)
     * @param {function} onClose - Callback when notification closes
     * @param {boolean} persistent - Whether to persist across page navigation (default: false)
     */
    info(message, duration = 5000, onClose = null, persistent = false) {
        if (persistent) {
            this.storePersistentNotification(message, 'info', duration);
        }
        return this.show(message, 'info', duration, onClose, false);
    }

    /**
     * Show confirmation dialog
     * @param {string} message - Confirmation message
     * @param {function} onConfirm - Callback if user confirms
     * @param {function} onCancel - Callback if user cancels
     */
    confirm(message, onConfirm = null, onCancel = null) {
        return new Promise((resolve) => {
            // Create overlay
            const overlay = document.createElement('div');
            const overlayId = `overlay-${Date.now()}-${Math.random()}`;
            overlay.id = overlayId;
            overlay.className = 'notification-overlay';

            // Create modal
            const modal = document.createElement('div');
            const id = `confirm-${Date.now()}-${Math.random()}`;
            modal.id = id;
            modal.className = 'notification-modal notification-confirm';

            modal.innerHTML = `
                <div class="notification-content">
                    <i class="notification-icon fas fa-question-circle"></i>
                    <span class="notification-message">${this.escapeHtml(message)}</span>
                    <div class="notification-actions">
                        <button class="btn btn-sm btn-secondary notification-cancel">Cancel</button>
                        <button class="btn btn-sm btn-primary notification-confirm">Confirm</button>
                    </div>
                </div>
            `;

            // Confirm button
            modal.querySelector('.notification-confirm').addEventListener('click', () => {
                this.dismissConfirm(overlayId, id);
                if (onConfirm) onConfirm();
                resolve(true);
            });

            // Cancel button
            modal.querySelector('.notification-cancel').addEventListener('click', () => {
                this.dismissConfirm(overlayId, id);
                if (onCancel) onCancel();
                resolve(false);
            });

            // Click overlay to cancel
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.dismissConfirm(overlayId, id);
                    if (onCancel) onCancel();
                    resolve(false);
                }
            });

            // Add to body
            document.body.appendChild(overlay);
            document.body.appendChild(modal);

            // Trigger animation
            setTimeout(() => {
                overlay.classList.add('show');
                modal.classList.add('show');
            }, 10);
        });
    }

    /**
     * Dismiss confirmation dialog
     */
    dismissConfirm(overlayId, modalId) {
        const overlay = document.getElementById(overlayId);
        const modal = document.getElementById(modalId);

        if (overlay) {
            overlay.classList.remove('show');
        }
        if (modal) {
            modal.classList.remove('show');
        }

        setTimeout(() => {
            if (overlay && overlay.parentNode) {
                overlay.parentNode.removeChild(overlay);
            }
            if (modal && modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    }

    /**
     * Dismiss a notification
     */
    dismiss(id, callback = null) {
        const notification = document.getElementById(id);
        if (notification) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                this.notifications = this.notifications.filter(n => n !== id);
                if (callback) callback();
            }, 300);
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Clear all notifications
     */
    clearAll() {
        this.notifications.forEach(id => {
            this.dismiss(id);
        });
    }

    /**
     * Store all active notifications before page navigation
     * Called automatically on page unload/navigation
     */
    storeActiveNotifications() {
        try {
            const active = [];
            this.notifications.forEach(id => {
                const element = document.getElementById(id);
                if (element && element.classList.contains('show')) {
                    const message = element.querySelector('.notification-message')?.textContent;
                    const type = element.className.match(/notification-(\w+)/)?.[1] || 'info';
                    const timerElement = element.querySelector('.timer-value');
                    
                    if (message) {
                        // Calculate remaining duration from timer display
                        let remainingDuration = 5000;
                        if (timerElement) {
                            const remainingSeconds = parseInt(timerElement.textContent) || 5;
                            remainingDuration = remainingSeconds * 1000;
                        }
                        
                        active.push({ 
                            message, 
                            type, 
                            duration: remainingDuration,
                            timestamp: Date.now()
                        });
                    }
                }
            });
            if (active.length > 0) {
                localStorage.setItem(this.pendingNotificationsKey, JSON.stringify(active));
            }
        } catch (e) {
            console.error('Error storing active notifications:', e);
        }
    }
}

// Global notification manager instance
const notificationManager = new NotificationManager();

// Auto-save notifications before page navigation
window.addEventListener('beforeunload', () => {
    notificationManager.storeActiveNotifications();
});

// Handle SPA navigation (for frameworks like React, Vue, etc.)
window.addEventListener('popstate', () => {
    notificationManager.storeActiveNotifications();
});

// Handle link clicks for same-domain navigation
document.addEventListener('click', (e) => {
    const link = e.target.closest('a');
    if (link && link.href && !link.target && !link.hasAttribute('data-no-persist')) {
        const url = new URL(link.href);
        const currentUrl = new URL(window.location.href);
        
        // Only store notifications for same-domain navigation
        if (url.origin === currentUrl.origin) {
            notificationManager.storeActiveNotifications();
        }
    }
}, true);

// Helper functions for easy access
function showSuccess(message, duration = 5000) {
    return notificationManager.success(message, duration);
}

function showError(message, duration = 5000) {
    return notificationManager.error(message, duration);
}

function showWarning(message, duration = 5000) {
    return notificationManager.warning(message, duration);
}

function showInfo(message, duration = 5000) {
    return notificationManager.info(message, duration);
}

function showConfirm(message, onConfirm, onCancel) {
    return notificationManager.confirm(message, onConfirm, onCancel);
}

/**
 * Show a popup notification without timer (confirmation boxes)
 */
function showPopup(message, type = 'info', onClose = null) {
    return notificationManager.show(message, type, 0, onClose, false);
}

/**
 * Show a persistent notification that survives page navigation
 * @param {string} message - Notification message
 * @param {string} type - Type: 'success', 'error', 'warning', 'info'
 * @param {number} duration - Duration in ms (default: 5000)
 */
function showPersistent(message, type = 'info', duration = 5000) {
    return notificationManager[type](message, duration, null, true);
}

// Override browser alert, confirm, and prompt
window.alert = function(message) {
    showPopup(message, 'info'); // Popup without timer
};

window.confirm = function(message) {
    return showConfirm(message);
};

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        notificationManager,
        showSuccess,
        showError,
        showWarning,
        showInfo,
        showConfirm,
        showPopup
    };
}
