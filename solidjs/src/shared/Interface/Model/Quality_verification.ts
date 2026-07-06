export interface Quality_verification {
   id: number,
   created_at: Date,
   updated_at: Date,
   enable: number,
   booking_id: number,
   verification_date: Date,
   verifier_type: string,
   quality_grade: string,
   quality_metrics: text | null,
   photos: text | null,
   passed: boolean,
   notes: text | null,
   active_role_id: number
}