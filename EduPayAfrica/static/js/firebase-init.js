// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

// Get Firebase configuration from Django template context
// This is injected from backend (see base.html)
const firebaseConfig = window.firebaseConfig;

if (!firebaseConfig || !firebaseConfig.apiKey) {
    console.error('Firebase configuration is missing. Please check your .env file and settings.');
} else {
    // Initialize Firebase
    export const app = initializeApp(firebaseConfig);
    export const analytics = getAnalytics(app);
    
    console.log('Firebase initialized successfully');
}
