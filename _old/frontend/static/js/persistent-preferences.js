/**
 * Persistent Preferences Manager
 * Handles saving and restoring user preferences like sorting options using localStorage
 */

class PersistentPreferences {
    constructor() {
        this.storagePrefix = 'readloom_prefs_';
    }

    /**
     * Save a preference to localStorage
     * @param {string} key - The preference key
     * @param {*} value - The value to save
     */
    save(key, value) {
        try {
            const fullKey = this.storagePrefix + key;
            localStorage.setItem(fullKey, JSON.stringify(value));
        } catch (e) {
            console.warn(`Failed to save preference ${key}:`, e);
        }
    }

    /**
     * Load a preference from localStorage
     * @param {string} key - The preference key
     * @param {*} defaultValue - Default value if not found
     * @returns {*} The saved value or default
     */
    load(key, defaultValue = null) {
        try {
            const fullKey = this.storagePrefix + key;
            const value = localStorage.getItem(fullKey);
            return value ? JSON.parse(value) : defaultValue;
        } catch (e) {
            console.warn(`Failed to load preference ${key}:`, e);
            return defaultValue;
        }
    }

    /**
     * Remove a preference from localStorage
     * @param {string} key - The preference key
     */
    remove(key) {
        try {
            const fullKey = this.storagePrefix + key;
            localStorage.removeItem(fullKey);
        } catch (e) {
            console.warn(`Failed to remove preference ${key}:`, e);
        }
    }

    /**
     * Clear all preferences
     */
    clearAll() {
        try {
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith(this.storagePrefix)) {
                    localStorage.removeItem(key);
                }
            });
        } catch (e) {
            console.warn('Failed to clear all preferences:', e);
        }
    }
}

// Create global instance
const preferences = new PersistentPreferences();
