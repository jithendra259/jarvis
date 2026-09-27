import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';
import { App as VoiceAgentApp } from '@/components/voice-agent/app';
import { APP_CONFIG_DEFAULTS } from '@/app-config';
import { ThemeProvider } from '@/components/theme/theme-provider';
import { Toaster } from 'sonner';
import { getStyles } from '@/lib/utils';
import { cn } from '@/lib/utils';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'JARVIS | Desktop AI Assistant',
  description: 'Personal desktop AI assistant powered by LiveKit WebRTC and OmniRoute',
};

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  const appConfig = APP_CONFIG_DEFAULTS;
  const styles = getStyles(appConfig);

  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={cn(
        geistSans.variable,
        geistMono.variable,
        'dark scroll-smooth font-sans antialiased'
      )}
    >
      <head>{styles && <style>{styles}</style>}</head>
      <body suppressHydrationWarning className="overflow-x-hidden bg-background text-foreground">
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem={false}
          disableTransitionOnChange
        >
          <VoiceAgentApp appConfig={APP_CONFIG_DEFAULTS}>{children}</VoiceAgentApp>
          <Toaster position="top-center" />
        </ThemeProvider>
      </body>
    </html>
  );
}
