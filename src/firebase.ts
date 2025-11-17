import firebase from "firebase/compat/app";
import "firebase/compat/auth";
import "firebase/compat/database";

export const firebaseConfig = {
  apiKey: "AIzaSyB5oCKc-6_KGOwx-K7-g575ycFcI-V9vyU",
  authDomain: "rinit-46f8c.firebaseapp.com",
  databaseURL: "https://rinit-46f8c-default-rtdb.firebaseio.com",
  projectId: "rinit-46f8c",
  storageBucket: "rinit-46f8c.appspot.com",
  messagingSenderId: "271382143725",
  appId: "1:271382143725:web:e7214b1325b409e985e2e4",
  measurementId: "G-E2XV2SXFDQ"
};

firebase.initializeApp(firebaseConfig);

if (!firebaseConfig.databaseURL) {
  throw new Error("Missing firebaseConfig.databaseURL — open Firebase Console → Realtime Database and copy the exact URL.");
}

export const db = firebase.database();
export const auth = firebase.auth();

export async function ensureAnonAuth() {
  await auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL);
  if (!auth.currentUser) {
    await auth.signInAnonymously();
  }
  return auth.currentUser;
}
