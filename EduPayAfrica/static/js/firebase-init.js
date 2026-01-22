// Firebase initialization for client-side (optional)
// Note: For the Super Admin login, all authentication happens server-side
// This file is kept for future client-side Firebase features

// Get Firebase configuration from Django template context
const firebaseConfig = window.firebaseConfig;

if (firebaseConfig && firebaseConfig.apiKey) {
    console.log('Firebase configuration loaded successfully');
    console.log('Server-side authentication is active');
} else {
    console.warn('Firebase client configuration not loaded - server-side auth only');
}
