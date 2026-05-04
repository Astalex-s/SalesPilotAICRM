/**
 * useSSE — подключается к SSE-эндпоинту бэкенда и транслирует события
 * в useNotificationStore.
 *
 * Жизненный цикл:
 *  - mount: открывает EventSource, если пользователь авторизован
 *  - unmount / logout: закрывает соединение
 *  - reconnect: браузер сам переподключается при разрыве (стандарт SSE)
 *
 * Фильтрация по настройкам пользователя (notifLead, notifDeal и т.д.)
 * применяется здесь, а не на бэкенде.
 */
import { useEffect, useRef } from 'react';
import { useAuthStore } from '../store/useAuthStore';
import { useNotificationStore, NotificationType } from '../store/useNotificationStore';
import { useSettingsStore } from '../store/useSettingsStore';

interface SSEEvent {
  type: NotificationType;
  title_key: string;
  msg_key: string;
  params?: Record<string, string>;
  link?: string;
  timestamp: string;
}

/** Маппинг типа события → настройка уведомлений пользователя */
function isTypeEnabled(type: NotificationType, settings: ReturnType<typeof useSettingsStore.getState>): boolean {
  switch (type) {
    case 'lead':   return settings.notifLead;
    case 'deal':   return settings.notifDeal;
    case 'email':  return settings.notifEmail;
    case 'system': return settings.notifSystem;
    default:       return true;
  }
}

export function useSSE(): void {
  const token = useAuthStore((s) => s.token);
  const add = useNotificationStore((s) => s.add);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!token) {
      // Не авторизован — закрываем если было открыто
      esRef.current?.close();
      esRef.current = null;
      return;
    }

    const url = `/api/v1/notifications/stream?token=${encodeURIComponent(token)}`;
    const es = new EventSource(url);
    esRef.current = es;

    es.onmessage = (event) => {
      try {
        const data: SSEEvent = JSON.parse(event.data);
        const settings = useSettingsStore.getState();

        if (!isTypeEnabled(data.type, settings)) return;

        add({
          type: data.type,
          titleKey: data.title_key,
          msgKey: data.msg_key,
          params: data.params,
          link: data.link,
          timestamp: data.timestamp ?? new Date().toISOString(),
        });
      } catch {
        // Невалидный JSON — игнорируем
      }
    };

    es.onerror = () => {
      // EventSource автоматически переподключается — дополнительная логика не нужна
    };

    return () => {
      es.close();
      esRef.current = null;
    };
  }, [token, add]);
}
