# MaaleNex NEXUS UI System v1.0

**Status:** Implemented on a feature branch; not merged or deployed.  
**Product scope:** Amharic-first passenger guest preview.

## Visual direction

The NEXUS visual language combines deep evergreen and midnight graphite foundations, luminous mint/cyan accents, geometric navigation motifs, subtle gridwork, and restrained motion. Abstract orbit lines and connected nodes express mobility and regional connection without depicting unverified routes or live vehicles.

## Color tokens

- Midnight: #071A1C
- Deep evergreen: #0B2928
- Primary mint: #B5EFCC
- Signal green: #55B98B
- Action mint: #83D9B0
- Warm focus: #F2C27C
- Muted text: #A9BEB4

## Typography

The interface requests Noto Sans Ethiopic first, followed by Noto Sans, Nyala, and system UI fallbacks. This is intended to use the platform's installed Ethiopic-capable font without external font requests. A separately packaged and license-attributed webfont remains a follow-up if cross-platform visual consistency requires it; no remote font dependency is introduced.

## Icon family

The initial NEXUS outline icon set is authored as local inline SVG and covers:
- Home
- Compass / discovery
- Intelligence / sparkle
- Direction / arrow
- Safety / shield
- Language / globe

The same geometric emblem is used for the web identity, favicon, PWA icons, Android adaptive foreground, monochrome icon, and Android 12+ splash screen.

## Page architecture

- Welcome / home: bilingual warm greeting, product introduction, guest preview entry, current-scope notice, responsible-use notice, and abstract mobility visual.
- Journey information: verified-data empty state; no routes, schedules, operators, or fares are invented.
- About: mission, principles, and accurately labelled Koybe/Jinka/South Omo development focus.
- IROKA: planned integration flow and explicit disconnected state.
- Shared shell: persistent brand, primary navigation, language switch, skip link, and footer.

## Interaction and responsive behavior

- Home, About, and IROKA pages are connected through in-app navigation.
- Amharic is the default; English is available through the language switch.
- Layout adapts for desktop, tablet, and narrow mobile widths down to 320 CSS pixels.
- Motion respects prefers-reduced-motion.
- Focus-visible styling and a skip link are retained.
- No login, personal-data capture, booking, payment, ticketing, or unsupported live-service claims are introduced.

## Android assets

Android 12+ uses the platform splash-screen API with a branded dark background and vector emblem. Adaptive launcher foreground, monochrome icon, and background use the same geometric identity. Emulator compilation and physical-device splash/launcher verification are required before acceptance.

## Acceptance boundary

The visual work is not a WCAG 2.2 AA certification. Rendered contrast, text scaling, TalkBack, physical-device behavior, and visual regression require exact-head verification. The current IROKA adapter is fail-closed and makes no network requests.
