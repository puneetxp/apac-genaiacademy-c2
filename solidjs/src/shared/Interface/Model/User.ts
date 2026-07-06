export interface User {
   id: number,
   created_at: Date,
   updated_at: Date,
   enable: number,
   cognito_user_id: string, // Database compatibility field name; maps to Firebase / Identity Platform UID under the hood
   firebase_id: string, // GCP / Firebase UID
   username: string,
   name: string,
   email: string,
   phone: string,
   google_id: string | null,
   facebook_id: string | null,
   password: string | null,
   user_type: string | null,
   preferred_language: string | null,
   mfa_enabled: boolean | null,
   latitude: number | null,
   longitude: number | null,
   pincode: string | null,
   state: string | null,
   district: string | null,
   village: string | null,
   address_line: string | null,
   is_active: boolean | null,
   is_verified: boolean | null
}