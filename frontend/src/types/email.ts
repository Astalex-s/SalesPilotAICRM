export type EmailDirection = 'inbound' | 'outbound';

export interface EmailMessage {
  id: string;
  gmail_message_id: string;
  gmail_thread_id: string;
  from_address: string;
  to_addresses: string[];
  subject: string;
  body: string;
  direction: EmailDirection;
  received_at: string;
  lead_id: string | null;
  created_at: string;
}

export interface GmailAuthStatus {
  authorized: boolean;
  message: string;
}

export interface GmailAuthUrl {
  auth_url: string;
  message: string;
}

export interface SendEmailPayload {
  to: string;
  subject: string;
  body: string;
  performed_by_id: string;
  lead_id?: string;
  thread_id?: string;
}
