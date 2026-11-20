import type { ReactNode } from "react";

export type NexusIconName = "home" | "compass" | "spark" | "arrow" | "shield" | "globe";

const paths: Record<NexusIconName, ReactNode> = {
  home: <path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z" />,
  compass: <><circle cx="12" cy="12" r="9" /><path d="m15.8 8.2-2.6 5-5 2.6 2.6-5z" /></>,
  spark: <><path d="m12 3 1.9 5.8L20 11l-6.1 2.2L12 19l-1.9-5.8L4 11l6.1-2.2z" /><path d="m19 15 1 2 2 1-2 1-1 2-1-2-2-1 2-1z" /></>,
  arrow: <path d="M5 12h14M13 6l6 6-6 6" />,
  shield: <><path d="M12 3 20 6v5c0 5-3.4 8.4-8 10-4.6-1.6-8-5-8-10V6z" /><path d="m8.5 12 2.2 2.2 4.8-5" /></>,
  globe: <><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18" /></>
};

export function Icon({ name }: { name: NexusIconName }) {
  return <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">{paths[name]}</svg>;
}
