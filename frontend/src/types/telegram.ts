export interface TelegramStatus {
  configured: boolean;
  webhook_url: string;
  webhook_pending_updates: number;
}

export interface TelegramWebhookSetResult {
  success: boolean;
  message: string;
}
