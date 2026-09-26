import { initializeApp, type FirebaseApp } from 'firebase/app';
import {
  getAuth,
  GoogleAuthProvider,
  RecaptchaVerifier,
  signInWithPhoneNumber,
  signInWithPopup,
  signOut,
  type ConfirmationResult,
  type User,
} from 'firebase/auth';

// These values are public (they ship in every Firebase web app); they are injected at build time.
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
};

let app: FirebaseApp | null = null;
let recaptcha: RecaptchaVerifier | null = null;

export type FirebaseSession = { idToken: string; refreshToken: string };

function firebaseAuth() {
  if (!firebaseConfig.apiKey) {
    throw new Error('Firebase sign-in is not configured (VITE_FIREBASE_API_KEY missing)');
  }
  app ??= initializeApp(firebaseConfig);
  return getAuth(app);
}

async function session(user: User): Promise<FirebaseSession> {
  return { idToken: await user.getIdToken(), refreshToken: user.refreshToken };
}

export async function googleSignInPopup(): Promise<FirebaseSession> {
  const result = await signInWithPopup(firebaseAuth(), new GoogleAuthProvider());
  return session(result.user);
}

/**
 * Send an SMS code. `containerId` is the id of an element that hosts the invisible reCAPTCHA
 * Firebase requires for phone auth. `phone` must be in E.164 form, e.g. +919876543210.
 */
export async function sendPhoneOtp(phone: string, containerId: string): Promise<ConfirmationResult> {
  const auth = firebaseAuth();
  recaptcha?.clear();
  recaptcha = new RecaptchaVerifier(auth, containerId, { size: 'invisible' });
  try {
    return await signInWithPhoneNumber(auth, phone, recaptcha);
  } catch (err) {
    recaptcha.clear();
    recaptcha = null;
    throw err;
  }
}

export async function confirmPhoneOtp(confirmation: ConfirmationResult, code: string): Promise<FirebaseSession> {
  const result = await confirmation.confirm(code);
  return session(result.user);
}

export async function firebaseSignOut(): Promise<void> {
  if (app) await signOut(getAuth(app));
}
