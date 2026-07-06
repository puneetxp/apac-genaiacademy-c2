export interface Notification {
    id: number;
    updated_at: Date;
    created_at: Date;
    title: string;
    message: string;
    type: 'alert' | 'info' | 'general';
    is_read: boolean;
    user_id: number;
}
