/**
 * PWA Initialization Script
 * Handles service worker registration, install prompts, and PWA features
 */

class PWAManager {
  constructor() {
    this.deferredPrompt = null;
    this.isInstalled = false;
    this.init();
  }

  /**
   * Initialize PWA features
   */
  init() {
    this.registerServiceWorker();
    this.setupInstallPrompt();
    this.checkIfInstalled();
    this.setupOfflineDetection();
  }

  /**
   * Register service worker
   */
  registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/service-worker.js')
          .then(registration => {
            console.log('Service Worker registered successfully:', registration);
            this.setupServiceWorkerUpdates(registration);
          })
          .catch(error => {
            console.error('Service Worker registration failed:', error);
          });
      });
    }
  }

  /**
   * Check for service worker updates
   */
  setupServiceWorkerUpdates(registration) {
    registration.addEventListener('updatefound', () => {
      const newWorker = registration.installing;
      newWorker.addEventListener('statechange', () => {
        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
          // New service worker available, show update notification
          this.showUpdateNotification();
        }
      });
    });

    // Check for updates periodically
    setInterval(() => {
      registration.update();
    }, 60000); // Check every minute
  }

  /**
   * Show update notification
   */
  showUpdateNotification() {
    if (typeof notificationManager !== 'undefined') {
      notificationManager.info(
        'App Update Available',
        'A new version of Readloom is available. Refresh to update.',
        {
          duration: 0,
          dismissible: true
        }
      );
    }
  }

  /**
   * Setup install prompt
   */
  setupInstallPrompt() {
    window.addEventListener('beforeinstallprompt', event => {
      // Prevent the mini-infobar from appearing
      event.preventDefault();
      // Store the event for later use
      this.deferredPrompt = event;
      // Show install button
      this.showInstallButton();
    });

    window.addEventListener('appinstalled', () => {
      console.log('PWA was installed');
      this.isInstalled = true;
      this.hideInstallButton();
    });
  }

  /**
   * Show install button
   */
  showInstallButton() {
    const installBtn = document.getElementById('pwa-install-btn');
    if (installBtn) {
      installBtn.style.display = 'block';
      installBtn.addEventListener('click', () => this.installApp());
    }
  }

  /**
   * Hide install button
   */
  hideInstallButton() {
    const installBtn = document.getElementById('pwa-install-btn');
    if (installBtn) {
      installBtn.style.display = 'none';
    }
  }

  /**
   * Install the app
   */
  installApp() {
    if (!this.deferredPrompt) {
      return;
    }

    this.deferredPrompt.prompt();
    this.deferredPrompt.userChoice.then(choiceResult => {
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the install prompt');
        if (typeof notificationManager !== 'undefined') {
          notificationManager.success('App Installed', 'Readloom has been installed successfully!');
        }
      } else {
        console.log('User dismissed the install prompt');
      }
      this.deferredPrompt = null;
    });
  }

  /**
   * Check if app is installed
   */
  checkIfInstalled() {
    if (window.matchMedia('(display-mode: standalone)').matches) {
      this.isInstalled = true;
      this.hideInstallButton();
    }

    window.matchMedia('(display-mode: standalone)').addEventListener('change', e => {
      this.isInstalled = e.matches;
      if (this.isInstalled) {
        this.hideInstallButton();
      }
    });
  }

  /**
   * Setup offline detection
   */
  setupOfflineDetection() {
    window.addEventListener('online', () => {
      console.log('Back online');
      if (typeof notificationManager !== 'undefined') {
        notificationManager.success('Back Online', 'Your connection has been restored.');
      }
      this.syncQueuedActions();
    });

    window.addEventListener('offline', () => {
      console.log('Gone offline');
      if (typeof notificationManager !== 'undefined') {
        notificationManager.warning('Offline Mode', 'You are now offline. Changes will be synced when you\'re back online.');
      }
    });
  }

  /**
   * Queue an action for sync when offline
   */
  queueAction(url, method = 'POST', body = null, headers = {}) {
    if (navigator.onLine) {
      // If online, execute immediately
      return fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...headers
        },
        body: body ? JSON.stringify(body) : undefined
      });
    }

    // If offline, queue the action
    const queue = JSON.parse(localStorage.getItem('readloom_sync_queue') || '[]');
    queue.push({
      url,
      method,
      body,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      timestamp: Date.now()
    });
    localStorage.setItem('readloom_sync_queue', JSON.stringify(queue));

    if (typeof notificationManager !== 'undefined') {
      notificationManager.info('Queued', 'Your action has been queued and will sync when you\'re back online.');
    }

    return Promise.resolve();
  }

  /**
   * Sync queued actions
   */
  syncQueuedActions() {
    const queue = JSON.parse(localStorage.getItem('readloom_sync_queue') || '[]');
    
    if (queue.length === 0) {
      return;
    }

    console.log(`Syncing ${queue.length} queued actions...`);

    Promise.all(queue.map(action => {
      return fetch(action.url, {
        method: action.method,
        headers: action.headers,
        body: action.body ? JSON.stringify(action.body) : undefined
      });
    }))
    .then(() => {
      localStorage.removeItem('readloom_sync_queue');
      if (typeof notificationManager !== 'undefined') {
        notificationManager.success('Synced', 'All queued actions have been synced successfully.');
      }
    })
    .catch(error => {
      console.error('Error syncing queued actions:', error);
      if (typeof notificationManager !== 'undefined') {
        notificationManager.error('Sync Failed', 'Some actions could not be synced. They will be retried later.');
      }
    });
  }

  /**
   * Request notification permission
   */
  requestNotificationPermission() {
    if ('Notification' in window) {
      if (Notification.permission === 'granted') {
        return Promise.resolve();
      }
      if (Notification.permission !== 'denied') {
        return Notification.requestPermission();
      }
    }
    return Promise.reject('Notifications not supported');
  }

  /**
   * Subscribe to push notifications
   */
  subscribeToPushNotifications() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
      console.log('Push notifications not supported');
      return Promise.reject('Push notifications not supported');
    }

    return this.requestNotificationPermission()
      .then(() => navigator.serviceWorker.ready)
      .then(registration => {
        return registration.pushManager.getSubscription()
          .then(subscription => {
            if (subscription) {
              return subscription;
            }
            // Subscribe to push notifications
            return registration.pushManager.subscribe({
              userVisibleOnly: true,
              applicationServerKey: this.urlBase64ToUint8Array(window.VAPID_PUBLIC_KEY)
            });
          });
      })
      .then(subscription => {
        console.log('Push subscription successful:', subscription);
        return subscription;
      })
      .catch(error => {
        console.error('Push subscription failed:', error);
        throw error;
      });
  }

  /**
   * Convert VAPID key from base64 to Uint8Array
   */
  urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }
}

// Initialize PWA manager when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.pwaManager = new PWAManager();
  });
} else {
  window.pwaManager = new PWAManager();
}
