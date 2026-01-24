(function () {
  'use strict';
  var config = (typeof window !== 'undefined' && window.firebaseConfig) ? window.firebaseConfig : null;
  if (!config || !config.apiKey) { console.warn('Firebase client configuration not loaded - server-side auth only'); return; }
  if (typeof firebase === 'undefined') { console.warn('Firebase SDK not loaded. Ensure firebase-app and firebase-auth scripts are included on the page.'); return; }
  try {
    if (!firebase.apps || firebase.apps.length === 0) { firebase.initializeApp(config); console.log('Firebase initialized (client).'); } else { console.log('Firebase already initialized; skipping initializeApp.'); }
    if (firebase.auth) {
      firebase.auth().onAuthStateChanged(function(user) {
        if (user) {
          console.log('Firebase user signed in:', user.email || user.uid);
        } else {
          console.log('No Firebase user signed in.');
        }
      });
    } else { console.warn('firebase.auth() is not available.'); }
  } catch (err) { console.error('Error initializing Firebase client:', err); }
})();