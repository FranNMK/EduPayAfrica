const firebaseConfig = window.firebaseConfig || {};

if (firebaseConfig && firebaseConfig.apiKey) {
  // Initialize Firebase (compat)
  firebase.initializeApp(firebaseConfig);
  console.log('Firebase initialized (client).');

  // Example: enable sign-in state listener
  firebase.auth().onAuthStateChanged(user => {
    if (user) {
      console.log('User signed in:', user.email || user.uid);
      // If you use server-side verification, get ID token and POST to server:
      user.getIdToken().then(idToken => {
        // send idToken to your backend for verification (example)
        // fetch('/auth/firebase-login/', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({idToken})})
      });
    } else {
      console.log('No Firebase user signed in.');
    }
  });

  // You can wire up sign-in buttons: e.g. Google popup
  // const provider = new firebase.auth.GoogleAuthProvider();
  // firebase.auth().signInWithPopup(provider).then(...)
} else {
  console.warn('Firebase client configuration not loaded - server-side auth only');
}
