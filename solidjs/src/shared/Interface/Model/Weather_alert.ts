export interface Weather_alert {
   id: number,
   created_at: Date,
   updated_at: Date,
   enable: number,
   farm_id: number | null,
   state: string,
   district: string | null,
   alert_type: string,
   severity: string,
   message: string,
   recommendation: string | null,
   valid_from: Date,
   valid_until: Date,
   is_active: boolean | null,
   active_role_id: number
}