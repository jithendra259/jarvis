'use client';

import React from 'react';
import { toast as sonnerToast } from 'sonner';

export type NotificationType = 'success' | 'warning' | 'error' | 'info';

interface NotificationCardProps {
  type?: NotificationType;
  title: string;
  subtitle?: string;
  onClose?: () => void;
}

const typeConfig = {
  success: {
    waveFill: 'rgba(34, 197, 94, 0.28)',
    iconBg: 'rgba(34, 197, 94, 0.2)',
    color: '#16a34a',
    darkColor: '#22c55e',
    icon: (
      <path d="M256 48a208 208 0 1 1 0 416 208 208 0 1 1 0-416zm0 464A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM369 209c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-111 111-47-47c-9.4-9.4-24.6-9.4-33.9 0s-9.4 24.6 0 33.9l64 64c9.4 9.4 24.6 9.4 33.9 0L369 209z" />
    ),
    viewBox: '0 0 512 512',
  },
  warning: {
    waveFill: 'rgba(234, 179, 8, 0.28)',
    iconBg: 'rgba(234, 179, 8, 0.2)',
    color: '#d97706',
    darkColor: '#f59e0b',
    icon: (
      <path d="M236.8,188.09,149.35,36.22h0a24.76,24.76,0,0,0-42.7,0L19.2,188.09a23.51,23.51,0,0,0,0,23.72A24.35,24.35,0,0,0,40.55,224h174.9a24.35,24.35,0,0,0,21.33-12.19A23.51,23.51,0,0,0,236.8,188.09ZM222.93,203.8a8.5,8.5,0,0,1-7.48,4.2H40.55a8.5,8.5,0,0,1-7.48-4.2,7.59,7.59,0,0,1,0-7.72L120.52,44.21a8.75,8.75,0,0,1,15,0l87.45,151.87A7.59,7.59,0,0,1,222.93,203.8ZM120,144V104a8,8,0,0,1,16,0v40a8,8,0,0,1-16,0Zm20,36a12,12,0,1,1-12-12A12,12,0,0,1,140,180Z" />
    ),
    viewBox: '0 0 256 256',
  },
  error: {
    waveFill: 'rgba(239, 68, 68, 0.28)',
    iconBg: 'rgba(239, 68, 68, 0.2)',
    color: '#dc2626',
    darkColor: '#ef4444',
    icon: (
      <path d="M256 48a208 208 0 1 1 0 416 208 208 0 1 1 0-416zm0 464A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM175 175c-9.4 9.4-9.4 24.6 0 33.9l47 47-47 47c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l47-47 47 47c9.4 9.4 24.6 9.4 33.9 0s9.4-24.6 0-33.9l-47-47 47-47c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-47 47-47-47c-9.4-9.4-24.6-9.4-33.9 0z" />
    ),
    viewBox: '0 0 512 512',
  },
  info: {
    waveFill: 'rgba(14, 165, 233, 0.28)',
    iconBg: 'rgba(14, 165, 233, 0.2)',
    color: '#0284c7',
    darkColor: '#38bdf8',
    icon: (
      <>
        <path d="M13 7.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0Zm-3 3.75a.75.75 0 0 1 .75-.75h1.5a.75.75 0 0 1 .75.75v4.25h.75a.75.75 0 0 1 0 1.5h-3a.75.75 0 0 1 0-1.5h.75V12h-.75a.75.75 0 0 1-.75-.75Z" />
        <path d="M12 1c6.075 0 11 4.925 11 11s-4.925 11-11 11S1 18.075 1 12 5.925 1 12 1ZM2.5 12a9.5 9.5 0 0 0 9.5 9.5 9.5 9.5 0 0 0 9.5-9.5A9.5 9.5 0 0 0 12 2.5 9.5 9.5 0 0 0 2.5 12Z" />
      </>
    ),
    viewBox: '0 0 24 24',
  },
};

export function NotificationCard({
  type = 'success',
  title,
  subtitle,
  onClose,
}: NotificationCardProps) {
  const current = typeConfig[type];

  return (
    <div className="custom-notification-card-wrapper">
      <style>{`
        .custom-notification-card-wrapper .notification-card {
          width: 350px;
          max-width: calc(100vw - 32px);
          min-height: 72px;
          border-radius: 12px;
          box-sizing: border-box;
          padding: 12px 14px 12px 18px;
          background-color: #ffffff;
          box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.18), 0 0 0 1px rgba(0, 0, 0, 0.08);
          position: relative;
          overflow: hidden;
          display: flex;
          align-items: center;
          gap: 12px;
          font-family: inherit;
          transition: all 0.2s ease;
        }

        .dark .custom-notification-card-wrapper .notification-card,
        :root.dark .custom-notification-card-wrapper .notification-card,
        [data-theme='dark'] .custom-notification-card-wrapper .notification-card {
          background-color: #121316;
          box-shadow: 0 14px 36px -4px rgba(0, 0, 0, 0.65), 0 0 0 1px rgba(255, 255, 255, 0.12);
        }

        .custom-notification-card-wrapper .wave-decor {
          position: absolute;
          transform: rotate(90deg);
          left: -32px;
          top: 30px;
          width: 82px;
          pointer-events: none;
          fill: ${current.waveFill};
        }

        .custom-notification-card-wrapper .icon-container {
          width: 36px;
          height: 36px;
          display: flex;
          justify-content: center;
          align-items: center;
          background-color: ${current.iconBg};
          border-radius: 50%;
          margin-left: 6px;
          flex-shrink: 0;
        }

        .custom-notification-card-wrapper .icon {
          width: 18px;
          height: 18px;
          color: ${current.color};
          fill: currentColor;
        }

        .dark .custom-notification-card-wrapper .icon,
        :root.dark .custom-notification-card-wrapper .icon,
        [data-theme='dark'] .custom-notification-card-wrapper .icon {
          color: ${current.darkColor};
        }

        .custom-notification-card-wrapper .text-container {
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: flex-start;
          flex-grow: 1;
          min-width: 0;
        }

        .custom-notification-card-wrapper .title-text {
          margin: 0;
          color: ${current.color};
          font-size: 15px;
          font-weight: 700;
          line-height: 1.25;
          word-break: break-word;
        }

        .dark .custom-notification-card-wrapper .title-text,
        :root.dark .custom-notification-card-wrapper .title-text,
        [data-theme='dark'] .custom-notification-card-wrapper .title-text {
          color: ${current.darkColor};
        }

        .custom-notification-card-wrapper .sub-text {
          margin: 2px 0 0 0;
          font-size: 12px;
          color: #4b5563;
          line-height: 1.3;
          word-break: break-word;
        }

        .dark .custom-notification-card-wrapper .sub-text,
        :root.dark .custom-notification-card-wrapper .sub-text,
        [data-theme='dark'] .custom-notification-card-wrapper .sub-text {
          color: #9ca3af;
        }

        .custom-notification-card-wrapper .close-btn {
          width: 20px;
          height: 20px;
          color: #6b7280;
          cursor: pointer;
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 4px;
          transition: color 0.15s ease, background-color 0.15s ease;
          background: transparent;
          border: none;
          padding: 0;
        }

        .custom-notification-card-wrapper .close-btn:hover {
          color: #111827;
          background-color: rgba(0, 0, 0, 0.05);
        }

        .dark .custom-notification-card-wrapper .close-btn {
          color: #9ca3af;
        }

        .dark .custom-notification-card-wrapper .close-btn:hover {
          color: #f3f4f6;
          background-color: rgba(255, 255, 255, 0.1);
        }
      `}</style>

      <div className="notification-card">
        {/* SERRATED / WAVY TICKET EDGE DECORATION (FROM ATTACHED IMAGE) */}
        <svg className="wave-decor" viewBox="0 0 1440 320" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M0,256L11.4,240C22.9,224,46,192,69,192C91.4,192,114,224,137,234.7C160,245,183,235,206,213.3C228.6,192,251,160,274,149.3C297.1,139,320,149,343,181.3C365.7,213,389,267,411,282.7C434.3,299,457,277,480,250.7C502.9,224,526,192,549,181.3C571.4,171,594,181,617,208C640,235,663,277,686,256C708.6,235,731,149,754,122.7C777.1,96,800,128,823,165.3C845.7,203,869,245,891,224C914.3,203,937,117,960,112C982.9,107,1006,181,1029,197.3C1051.4,213,1074,171,1097,144C1120,117,1143,107,1166,133.3C1188.6,160,1211,224,1234,218.7C1257.1,213,1280,139,1303,133.3C1325.7,128,1349,192,1371,192C1394.3,192,1417,128,1429,96L1440,64L1440,320L1428.6,320C1417.1,320,1394,320,1371,320C1348.6,320,1326,320,1303,320C1280,320,1257,320,1234,320C1211.4,320,1189,320,1166,320C1142.9,320,1120,320,1097,320C1074.3,320,1051,320,1029,320C1005.7,320,983,320,960,320C937.1,320,914,320,891,320C868.6,320,846,320,823,320C800,320,777,320,754,320C731.4,320,709,320,686,320C662.9,320,640,320,617,320C594.3,320,571,320,549,320C525.7,320,503,320,480,320C457.1,320,434,320,411,320C388.6,320,366,320,343,320C320,320,297,320,274,320C251.4,320,229,320,206,320C182.9,320,160,320,137,320C114.3,320,91,320,69,320C45.7,320,23,320,11,320L0,320Z"
            fillOpacity={1}
          />
        </svg>

        {/* ICON CIRCLE BADGE */}
        <div className="icon-container">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox={current.viewBox}
            strokeWidth={0}
            fill="currentColor"
            stroke="currentColor"
            className="icon"
          >
            {current.icon}
          </svg>
        </div>

        {/* TITLE & SUBTITLE */}
        <div className="text-container">
          <p className="title-text">{title}</p>
          {subtitle && <p className="sub-text">{subtitle}</p>}
        </div>

        {/* CLOSE [X] BUTTON */}
        <button
          type="button"
          onClick={onClose}
          aria-label="Close notification"
          className="close-btn"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 15 15"
            width="14"
            height="14"
            fill="currentColor"
          >
            <path
              fill="currentColor"
              d="M11.7816 4.03157C12.0062 3.80702 12.0062 3.44295 11.7816 3.2184C11.5571 2.99385 11.193 2.99385 10.9685 3.2184L7.50005 6.68682L4.03164 3.2184C3.80708 2.99385 3.44301 2.99385 3.21846 3.2184C2.99391 3.44295 2.99391 3.80702 3.21846 4.03157L6.68688 7.49999L3.21846 10.9684C2.99391 11.193 2.99391 11.557 3.21846 11.7816C3.44301 12.0061 3.80708 12.0061 4.03164 11.7816L7.50005 8.31316L10.9685 11.7816C11.193 12.0061 11.5571 12.0061 11.7816 11.7816C12.0062 11.557 12.0062 11.193 11.7816 10.9684L8.31322 7.49999L11.7816 4.03157Z"
              clipRule="evenodd"
              fillRule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}

interface ToastOptions {
  description?: string;
  duration?: number;
}

function parseNotificationArgs(
  messageOrTitle: string,
  subtitleOrOpts?: string | ToastOptions,
  defaultTitle = 'Notification'
): { title: string; subtitle?: string; duration?: number } {
  let subtitle: string | undefined;
  let duration: number | undefined;

  if (typeof subtitleOrOpts === 'string') {
    subtitle = subtitleOrOpts;
  } else if (subtitleOrOpts && typeof subtitleOrOpts === 'object') {
    subtitle = subtitleOrOpts.description;
    duration = subtitleOrOpts.duration;
  }

  if (subtitle !== undefined) {
    return { title: messageOrTitle, subtitle, duration };
  }

  // If single string provided
  if (messageOrTitle.length <= 32 && !messageOrTitle.includes('.')) {
    return { title: messageOrTitle, subtitle: undefined, duration };
  }

  // If it's a full sentence or message
  return { title: defaultTitle, subtitle: messageOrTitle, duration };
}

/**
 * Trigger function to display a custom notification card as a toast
 */
function showNotify(type: NotificationType, title: string, subtitle?: string, duration = 4000) {
  return sonnerToast.custom(
    (t) => (
      <NotificationCard
        type={type}
        title={title}
        subtitle={subtitle}
        onClose={() => sonnerToast.dismiss(t)}
      />
    ),
    {
      duration,
    }
  );
}

export interface NotifyFunction {
  (type: NotificationType, title: string, subtitle?: string): string | number;
  success: (title: string, subtitleOrOpts?: string | ToastOptions) => string | number;
  error: (title: string, subtitleOrOpts?: string | ToastOptions) => string | number;
  warning: (title: string, subtitleOrOpts?: string | ToastOptions) => string | number;
  info: (title: string, subtitleOrOpts?: string | ToastOptions) => string | number;
}

export const notify: NotifyFunction = Object.assign(
  (type: NotificationType, title: string, subtitle?: string) => {
    return showNotify(type, title, subtitle);
  },
  {
    success: (title: string, subtitleOrOpts?: string | ToastOptions) => {
      const p = parseNotificationArgs(title, subtitleOrOpts, 'Success');
      return showNotify('success', p.title, p.subtitle, p.duration);
    },
    error: (title: string, subtitleOrOpts?: string | ToastOptions) => {
      const p = parseNotificationArgs(title, subtitleOrOpts, 'Error');
      return showNotify('error', p.title, p.subtitle, p.duration);
    },
    warning: (title: string, subtitleOrOpts?: string | ToastOptions) => {
      const p = parseNotificationArgs(title, subtitleOrOpts, 'Warning');
      return showNotify('warning', p.title, p.subtitle, p.duration);
    },
    info: (title: string, subtitleOrOpts?: string | ToastOptions) => {
      const p = parseNotificationArgs(title, subtitleOrOpts, 'Information');
      return showNotify('info', p.title, p.subtitle, p.duration);
    },
  }
);

/**
 * Drop-in replacement for sonner toast so all notifications in the app automatically use this UI
 */
export const toast = {
  success: notify.success,
  error: notify.error,
  warning: notify.warning,
  info: notify.info,
  custom: sonnerToast.custom,
  dismiss: sonnerToast.dismiss,
};

export default notify;
