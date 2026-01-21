// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAzt6kYUBdhL7VwZ4SfACISlY71uZN_Nag",
  authDomain: "edupay-africa.firebaseapp.com",
  projectId: "edupay-africa",
  storageBucket: "edupay-africa.firebasestorage.app",
  messagingSenderId: "1066626291510",
  appId: "1:1066626291510:web:49bc91fe0d2572b5fa8597",
  measurementId: "G-3TJQ91ERSR"
};

// Initialize Firebase
export const app = initializeApp(firebaseConfig);
export const analytics = getAnalytics(app);

console.log('Firebase initialized successfully');
