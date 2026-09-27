'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { useTheme } from 'next-themes';
import { usePathname, useRouter } from 'next/navigation';
import { RoomEvent } from 'livekit-client';
import { useMaybeRoomContext } from '@livekit/components-react';
import { toast } from '@/components/ui/widgets/notification-card';

export type NavigationTarget = string;

export interface NavigationTargetMeta {
  type: 'section' | 'route' | 'subsection';
  destination: string;
  label: string;
  pageRoute?: string;
}

export const NAVIGATION_TARGETS: Record<string, NavigationTargetMeta> = {
  // ── Homepage Primary Sections ─────────────────────────────────────────
  home: { type: 'section', destination: 'home', label: 'Home Overview' },
  hero: { type: 'section', destination: 'home', label: 'Hero Section' },
  about: { type: 'section', destination: 'about', label: 'About & Credentials' },
  research: { type: 'section', destination: 'research', label: 'Research Papers Bento' },
  projects: { type: 'section', destination: 'projects', label: 'Featured Projects' },
  skills: { type: 'section', destination: 'skills', label: 'Skills & Tech Stack' },
  experience: { type: 'section', destination: 'experience', label: 'Career & Education Timeline' },
  certificates: { type: 'section', destination: 'certificates', label: 'Certifications & Awards' },
  resume: { type: 'section', destination: 'resume', label: 'Resume Preview' },
  contact: { type: 'section', destination: 'contact', label: 'Contact Section' },

  // ── Standalone Pages ──────────────────────────────────────────────────
  book_appointment: {
    type: 'route',
    destination: '/book-appointment',
    label: 'Schedule a Meeting',
  },

  // ── Research & Project Case Studies ───────────────────────────────────
  case_study_adaptive_governance: {
    type: 'route',
    destination: '/projects/adaptive-portfolio-governance',
    label: 'Adaptive Portfolio Governance (Elsevier EAAI)',
  },
  case_study_regime_supervisory: {
    type: 'route',
    destination: '/projects/regime-adaptive-supervisory-governance',
    label: 'Regime-Adaptive Governance (Springer Nature LNCS)',
  },
  case_study_supervisory_xai: {
    type: 'route',
    destination: '/projects/supervisory-portfolio-xai-governance',
    label: 'Supervisory Portfolio XAI (Elsevier COR)',
  },
  case_study_voice_architecture: {
    type: 'route',
    destination: '/projects/voice-agent-portfolio-architecture',
    label: 'Voice AI Portfolio Architecture',
  },
  case_study_aqi: {
    type: 'route',
    destination: '/projects/personalised-aqi-system',
    label: 'Personalised AQI System (XGBoost)',
  },
  case_study_swarm_robotics: {
    type: 'route',
    destination: '/projects/swarm-robots-agriculture',
    label: 'Autonomous Swarm Robotics (ESP32 Mesh)',
  },

  // ── Case Study Subsections (Academic Layout) ──────────────────────────
  'sec-abstract': {
    type: 'subsection',
    destination: 'sec-abstract',
    label: 'Abstract & Keywords',
  },
  'sec-intro': {
    type: 'subsection',
    destination: 'sec-intro',
    label: 'Introduction & Background',
  },
  'subsec-intro-problem': {
    type: 'subsection',
    destination: 'subsec-intro-problem',
    label: 'Problem Statement',
  },
  'subsec-intro-solution': {
    type: 'subsection',
    destination: 'subsec-intro-solution',
    label: 'Engineered Solution',
  },
  'sec-math': {
    type: 'subsection',
    destination: 'sec-math',
    label: 'Mathematical Formulation (G-CVaR & SOCP)',
  },
  'subsec-math-cvar': {
    type: 'subsection',
    destination: 'subsec-math-cvar',
    label: 'Equation (1): CVaR Loss',
  },
  'subsec-math-graph': {
    type: 'subsection',
    destination: 'subsec-math-graph',
    label: 'Equation (2): Graph Laplacian Regularizer',
  },
  'sec-arch': {
    type: 'subsection',
    destination: 'sec-arch',
    label: 'System Architecture Pipeline',
  },
  'subsec-arch-fig1': {
    type: 'subsection',
    destination: 'subsec-arch-fig1',
    label: 'Figure 1: Modular Pipeline Schematic',
  },
  'sec-eval': {
    type: 'subsection',
    destination: 'sec-eval',
    label: 'Empirical Evaluation & Backtest',
  },
  'sec-references': {
    type: 'subsection',
    destination: 'sec-references',
    label: 'Scholarly References & BibTeX',
  },
};

/**
 * Normalizes any raw navigation target, slug, hash anchor, or alias into a validated metadata object.
 */
export function resolveNavigationTarget(rawTarget: string): NavigationTargetMeta | null {
  if (!rawTarget) return null;
  const clean = rawTarget.trim().toLowerCase().replace(/^#+/, '').replace(/^\/+/, '');

  // 1. Direct match in dictionary
  if (NAVIGATION_TARGETS[clean]) {
    return NAVIGATION_TARGETS[clean];
  }

  // 2. Exact match with original string (e.g. 'sec-math')
  if (NAVIGATION_TARGETS[rawTarget.trim().replace(/^#+/, '')]) {
    return NAVIGATION_TARGETS[rawTarget.trim().replace(/^#+/, '')];
  }

  // 3. Alias mapping
  const aliasMap: Record<string, string> = {
    // Contact aliases
    contact_section: 'contact',
    contact_page: 'contact',
    contact_us: 'contact',
    get_in_touch: 'contact',
    email_contact: 'contact',
    booking_contact: 'contact',

    // Booking aliases
    'book-appointment': 'book_appointment',
    book_a_call: 'book_appointment',
    schedule_meeting: 'book_appointment',
    schedule_interview: 'book_appointment',
    appointment: 'book_appointment',
    booking: 'book_appointment',

    // Section aliases
    top: 'home',
    header: 'home',
    bio: 'about',
    credentials: 'about',
    background: 'about',
    publications: 'research',
    papers: 'research',
    research_papers: 'research',
    research_bento: 'research',
    featured_projects: 'projects',
    tech_stack: 'skills',
    tech_skills: 'skills',
    technologies: 'skills',
    timeline: 'experience',
    career: 'experience',
    education: 'experience',
    certifications: 'certificates',
    awards: 'certificates',
    cv: 'resume',

    // Case studies aliases
    eaai: 'case_study_adaptive_governance',
    eaai_paper: 'case_study_adaptive_governance',
    adaptive_governance: 'case_study_adaptive_governance',
    g_cvar: 'case_study_adaptive_governance',
    lncs: 'case_study_regime_supervisory',
    lncs_paper: 'case_study_regime_supervisory',
    ijcaci: 'case_study_regime_supervisory',
    regime_supervisory: 'case_study_regime_supervisory',
    cor: 'case_study_supervisory_xai',
    cor_paper: 'case_study_supervisory_xai',
    supervisory_xai: 'case_study_supervisory_xai',
    xai: 'case_study_supervisory_xai',
    aqi: 'case_study_aqi',
    aqi_project: 'case_study_aqi',
    air_quality: 'case_study_aqi',
    swarm: 'case_study_swarm_robotics',
    swarm_robotics: 'case_study_swarm_robotics',
    swarm_robots: 'case_study_swarm_robotics',
    voice: 'case_study_voice_architecture',
    voice_agent: 'case_study_voice_architecture',
    voice_architecture: 'case_study_voice_architecture',

    // Case study subsections
    abstract: 'sec-abstract',
    intro: 'sec-intro',
    introduction: 'sec-intro',
    problem: 'subsec-intro-problem',
    problem_statement: 'subsec-intro-problem',
    solution: 'subsec-intro-solution',
    math: 'sec-math',
    mathematical_formulation: 'sec-math',
    equations: 'sec-math',
    formulation: 'sec-math',
    cvar: 'subsec-math-cvar',
    graph_risk: 'subsec-math-graph',
    architecture: 'sec-arch',
    system_architecture: 'sec-arch',
    pipeline: 'sec-arch',
    schematic: 'subsec-arch-fig1',
    evaluation: 'sec-eval',
    results: 'sec-eval',
    empirical_evaluation: 'sec-eval',
    backtest: 'sec-eval',
    references: 'sec-references',
    citations: 'sec-references',
    bibtex: 'sec-references',
  };

  if (aliasMap[clean] && NAVIGATION_TARGETS[aliasMap[clean]]) {
    return NAVIGATION_TARGETS[aliasMap[clean]];
  }

  // 4. Fallback for arbitrary element ID or route
  if (rawTarget.startsWith('/')) {
    return {
      type: 'route',
      destination: rawTarget,
      label: rawTarget.replace(/^\//, '').replace(/-/g, ' '),
    };
  }

  // Return generic element target if it looks like an ID
  const elementId = rawTarget.replace(/^#+/, '');
  return {
    type: 'section',
    destination: elementId,
    label: elementId.replace(/[-_]/g, ' '),
  };
}

/**
 * Smoothly scrolls to an HTML element, accounting for the top navbar offset and pulsing with a cyan glow.
 */
function scrollToElementWithHighlight(el: HTMLElement): void {
  const headerOffset = 80;
  const currentScroll =
    window.scrollY ||
    window.pageYOffset ||
    document.documentElement.scrollTop ||
    document.body.scrollTop ||
    0;
  const elementPosition = el.getBoundingClientRect().top;
  const offsetPosition = Math.max(0, elementPosition + currentScroll - headerOffset);

  window.scrollTo({
    top: offsetPosition,
    behavior: 'smooth',
  });
  document.documentElement.scrollTo({
    top: offsetPosition,
    behavior: 'smooth',
  });

  // Highlight pulse animation
  el.classList.add('ring-2', 'ring-cyan-400/60', 'rounded-2xl', 'transition-all', 'duration-300');
  setTimeout(() => {
    el.classList.remove(
      'ring-2',
      'ring-cyan-400/60',
      'rounded-2xl',
      'transition-all',
      'duration-300'
    );
  }, 2800);
}

export function useVoiceAutoNavigation(session?: any, messages?: any[]) {
  const router = useRouter();
  const pathname = usePathname();
  const maybeRoom = useMaybeRoomContext();
  const room = session?.room || maybeRoom;
  const { setTheme } = useTheme();
  const [activeTarget, setActiveTarget] = useState<string | null>(null);
  const [lastNavigatedAt, setLastNavigatedAt] = useState<number | null>(null);
  const cooldownRef = useRef<number>(0);

  // Check for pending scroll targets across Next.js page route transitions
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const pendingTarget = sessionStorage.getItem('pending_scroll_target');
    if (pendingTarget) {
      sessionStorage.removeItem('pending_scroll_target');
      const timer = setTimeout(() => {
        const el = document.getElementById(pendingTarget);
        if (el) {
          scrollToElementWithHighlight(el);
        }
      }, 400);
      return () => clearTimeout(timer);
    }
  }, [pathname]);

  const navigateTo = useCallback(
    (rawTarget: string, source: 'data_channel' | 'speech_intent' = 'data_channel') => {
      const now = Date.now();
      // 1.5-second cooldown to prevent rapid oscillation
      if (now - cooldownRef.current < 1500 && activeTarget === rawTarget) {
        return;
      }
      cooldownRef.current = now;

      const target = resolveNavigationTarget(rawTarget);
      if (!target) {
        console.warn(`[AutoNav Warning] Could not resolve target: "${rawTarget}"`);
        return;
      }

      setActiveTarget(target.destination);
      setLastNavigatedAt(now);

      toast.info(`🧭 Navigating: ${target.label}`, {
        description: `Voice agent navigated screen to ${target.label}`,
        duration: 3500,
      });

      // ── Handle Section or Subsection Navigation ────────────────────────
      if (target.type === 'section' || target.type === 'subsection') {
        const el = document.getElementById(target.destination);
        if (el) {
          // Element is already in the DOM on the current screen
          scrollToElementWithHighlight(el);
        } else if (pathname !== '/') {
          // Target is a homepage section, but visitor is on a case study page
          sessionStorage.setItem('pending_scroll_target', target.destination);
          router.push(`/#${target.destination}`);

          // Poll for element in case Next.js renders quickly
          const pollInterval = setInterval(() => {
            const targetEl = document.getElementById(target.destination);
            if (targetEl) {
              clearInterval(pollInterval);
              sessionStorage.removeItem('pending_scroll_target');
              scrollToElementWithHighlight(targetEl);
            }
          }, 80);
          setTimeout(() => clearInterval(pollInterval), 2500);
        } else {
          // Attempt fallback query selector
          const fallbackEl = document.querySelector(`[id*="${target.destination}"]`) as HTMLElement;
          if (fallbackEl) {
            scrollToElementWithHighlight(fallbackEl);
          }
        }
      }
      // ── Handle Full Route Transition ───────────────────────────────────
      else if (target.type === 'route') {
        if (pathname !== target.destination) {
          router.push(target.destination);
        }
      }
    },
    [pathname, router, activeTarget]
  );

  // ── Speech Intent Detection Fallback (Zero-Latency Voice Command Triggers) ──
  useEffect(() => {
    if (!messages || messages.length === 0) return;
    const latest = messages[messages.length - 1];
    const text = (latest?.message || latest?.text || '').toLowerCase().trim();
    if (!text) return;

    // 1. Direct utterance match: If agent says "Navigating to <target>"
    const agentNavMatch = text.match(/\bnavigating\s+(?:to|you to|screen to)\s+(?:the\s+)?([a-z0-9_-]+)/i);
    if (agentNavMatch && agentNavMatch[1]) {
      const extracted = agentNavMatch[1].toLowerCase();
      console.log(`[AutoNav Agent Speech] Detected navigation announcement: "${extracted}"`);
      navigateTo(extracted, 'speech_intent');
      return;
    }

    const navPatterns: Array<{ target: string; matchers: RegExp[] }> = [
      {
        target: 'research',
        matchers: [
          /\b(go to|show|view|navigate to|open|see|take me to)\s+(the\s+)?(research|recent|papers|publications)\b/i,
          /\b(research|recent)\s+(section|papers|bento)\b/i,
          /\b(show me|explore)\s+(research|recent)\b/i,
        ],
      },
      {
        target: 'projects',
        matchers: [
          /\b(go to|show|view|navigate to|open|see|take me to)\s+(the\s+)?(projects|featured projects|works)\b/i,
          /\bprojects\s+(section|bento)\b/i,
          /\b(show me|explore)\s+projects\b/i,
        ],
      },
      {
        target: 'skills',
        matchers: [
          /\b(go to|show|view|navigate to|open|see|take me to)\s+(the\s+)?(skills|tech stack|technologies)\b/i,
          /\bskills\s+section\b/i,
          /\b(show me|explore)\s+skills\b/i,
        ],
      },
      {
        target: 'experience',
        matchers: [
          /\b(go to|show|view|navigate to|open|see|take me to)\s+(the\s+)?(experience|timeline|career|education)\b/i,
          /\bexperience\s+section\b/i,
          /\b(show me|explore)\s+experience\b/i,
        ],
      },
      {
        target: 'certificates',
        matchers: [
          /\b(go to|show|view|navigate to|open|see|take me to)\s+(the\s+)?(certificates|certifications|awards)\b/i,
          /\bcertificates\s+section\b/i,
        ],
      },
      {
        target: 'resume',
        matchers: [
          /\b(go to|show|view|navigate to|open|see|download|take me to)\s+(the\s+)?(resume|cv)\b/i,
          /\bresume\s+section\b/i,
        ],
      },
      {
        target: 'contact',
        matchers: [
          /\b(go to|show|view|navigate to|open|see|take me to)\s+(the\s+)?(contact|get in touch|email)\b/i,
          /\bcontact(\s+section)?\b/i,
        ],
      },
      {
        target: 'book_appointment',
        matchers: [
          /\b(book|schedule)\s+(a\s+)?(appointment|meeting|call|interview)\b/i,
          /\bcalendar\b/i,
        ],
      },
      {
        target: 'home',
        matchers: [
          /\b(go to|back to|navigate to|show|take me to)\s+(the\s+)?(home|top|hero)\b/i,
        ],
      },
      {
        target: 'case_study_adaptive_governance',
        matchers: [
          /\b(adaptive governance|eaai|g-cvar|cvar)\b/i,
        ],
      },
      {
        target: 'case_study_regime_supervisory',
        matchers: [
          /\b(regime adaptive|supervisory governance|lncs|ijcaci)\b/i,
        ],
      },
      {
        target: 'case_study_supervisory_xai',
        matchers: [
          /\b(supervisory xai|cor paper|explainable ai)\b/i,
        ],
      },
      {
        target: 'case_study_aqi',
        matchers: [
          /\b(aqi|air quality)\b/i,
        ],
      },
      {
        target: 'case_study_swarm_robotics',
        matchers: [
          /\b(swarm|swarm robotics|agriculture robots)\b/i,
        ],
      },
    ];

    for (const { target, matchers } of navPatterns) {
      if (matchers.some((m) => m.test(text))) {
        console.log(`[AutoNav Speech Intent] Detected target '${target}' in: "${text}"`);
        navigateTo(target, 'speech_intent');
        break;
      }
    }
  }, [messages, navigateTo]);

  // ── LiveKit Data Channel Listener ──────────────────────────────────────
  useEffect(() => {
    if (!room) return;

    const handleDataReceived = (
      payload: Uint8Array,
      participant: any,
      kind: any,
      topic?: string
    ) => {
      let text = '';
      try {
        text = new TextDecoder().decode(payload);
      } catch {}

      let parsed: any = null;
      try {
        parsed = JSON.parse(text);
      } catch {}

      console.log('[AutoNav Data Channel] Packet received:', { topic, parsed, textLength: text.length });

      // 1. Assistant Action Channel (Downloads, Themes, Bookings)
      if (topic === 'assistant_action' || parsed?.type === 'download' || parsed?.type === 'theme' || parsed?.type === 'booking_confirmed') {
        try {
          const data = parsed || JSON.parse(text);
          if (data?.type === 'download' && typeof data.url === 'string') {
            const link = document.createElement('a');
            link.href = data.url;
            link.download = typeof data.filename === 'string' ? data.filename : '';
            document.body.appendChild(link);
            link.click();
            link.remove();
            toast.success(`Download started: ${data.filename || 'portfolio resource'}`);
          }
          if (data?.type === 'theme' && (data.theme === 'dark' || data.theme === 'light')) {
            setTheme(data.theme);
            toast.success(`Switched to ${data.theme} mode.`);
          }
          if (data?.type === 'booking_confirmed') {
            const details = data.booking || {};
            toast.success(`Appointment Confirmed!`, {
              description: `Reserved for ${details.name || 'visitor'} (${details.email || ''}) on ${details.date || 'Flexible'}.`,
              duration: 5000,
            });
          }
        } catch (e) {
          console.error('Failed to parse assistant action packet:', e);
        }
        return;
      }

      // 2. Navigation Channel (Zero-Latency Screen Routing & Subsection Anchors)
      if (topic === 'navigation' || topic === 'lk-navigation' || parsed?.type === 'navigate') {
        try {
          let targetStr = '';
          if (parsed && typeof parsed === 'object') {
            targetStr = parsed.target || parsed.destination || '';
          }
          if (!targetStr) {
            targetStr = text.trim();
          }

          if (targetStr && targetStr !== '[object Object]') {
            console.log(`[AutoNav Data Channel] Triggering navigateTo('${targetStr}')`);
            navigateTo(targetStr, 'data_channel');
          }
        } catch (e) {
          console.error('Failed to parse navigation data packet:', e);
        }
      }
    };

    room.on(RoomEvent.DataReceived, handleDataReceived);
    return () => {
      room.off(RoomEvent.DataReceived, handleDataReceived);
    };
  }, [room, navigateTo, setTheme]);

  return {
    activeTarget,
    lastNavigatedAt,
    navigateTo,
    currentTargetMeta: activeTarget ? resolveNavigationTarget(activeTarget) : null,
  };
}
