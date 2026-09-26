export interface Ai_usage_quota {
   id: number,
   created_at: Date,
   updated_at: Date,
   enable: number,
   user_id: number,
   date: Date,
   gps_enhanced_requests: number,
   pincode_requests: number,
   last_reset: Date,
   quota_limit: number
}