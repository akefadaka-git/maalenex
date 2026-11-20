import { useEffect, useState } from "react";

type Language = "am" | "en";
type Page = "home" | "about" | "iroka";

const copy = {
  am: {
    brand: "MaaleNex", navHome: "መነሻ", navAbout: "ስለ እኛ", navIroka: "IROKA",
    language: "ቋንቋውን ወደ እንግሊዝኛ ቀይር",
    eyebrow: "የተሳፋሪ መጓጓዣ · የወደፊት እይታ",
    title: "መንገድዎን በእርጋታ። ወደፊትዎን በእምነት።",
    intro: "MaaleNex የኢትዮጵያን የተሳፋሪ መጓጓዣ ተሞክሮ ለማሻሻል እየተዘጋጀ ያለ ቴክኖሎጂ መድረክ ነው። ይህ የምርቱ የህዝብ ቅድመ እይታ ነው።",
    welcome: "እንኳን ወደ MaaleNex በደህና መጡ", welcomeSub: "በአካባቢያዊ ግንዛቤ የተመራ፣ በቴክኖሎጂ የተገነባ።",
    guest: "እንደ እንግዳ ይቀጥሉ", guestHint: "የህዝብ መረጃን ያለ መለያ ይመልከቱ።",
    current: "የአሁኑ ወሰን", currentText: "የተሳፋሪ ምርት ዝግጅት ብቻ። የተረጋገጡ የጉዞ መርሐ ግብሮች፣ ታሪፎች ወይም የሚሰሩ አገልግሎቶች አልተገለጹም።",
    future: "የወደፊት እይታ", futureText: "በተጠናከረ መረጃ፣ በግልጽ አሰራር እና በተጠያቂነት የተመራ የመጓጓዣ ልምድ።",
    safety: "ይህ የልማት ማሳያ ነው። መለያ፣ የግል መረጃ ማስገቢያ፣ ቦታ ማስያዣ፣ ክፍያ ወይም ትኬት አይኖርም።",
    aboutTitle: "ስለ MaaleNex", aboutLead: "ከአካባቢው የሚነሳ የመጓጓዣ ቴክኖሎጂ።",
    aboutText: "MaaleNex በኢትዮጵያ ውስጥ ለተሳፋሪዎች የተሻለ የመረጃ እና የጉዞ ዝግጅት ተሞክሮ ለመፍጠር የሚዘጋጅ መድረክ ነው። የመጀመሪያው የልማት ትኩረት በጂንካ እና በደቡብ ኦሞ አካባቢ ላይ ነው።",
    mission: "ተልዕኮ", missionText: "ተደራሽ፣ ግልጽ እና በአካባቢያዊ እውነታ የተመሠረተ የመጓጓዣ ቴክኖሎጂ መገንባት።",
    principles: "መርሆዎቻችን", principlesText: "ደህንነት፣ ግልጽነት፣ የተጠቃሚ ክብር፣ የአካባቢ ተስማሚነት እና በደረጃ የሚከናወን ልማት።",
    pilot: "የልማት አቅጣጫ", pilotText: "የመጀመሪያው የልማት አቅጣጫ ኮይቤ፣ ጂንካ እና የደቡብ ኦሞ አካባቢ ነው። ይህ የአሁኑ የስራ ቦታ እንጂ የሚሰራ የመጓጓዣ መስመር ማስታወቂያ አይደለም።",
    irokaTitle: "IROKA የኢንተለጀንስ ንብርብር", irokaText: "MaaleNex የወደፊት የኢንተለጀንስ ችሎታዎችን በተለየ እና በቁጥጥር ስር ባለ የውህደት መዋቅር ለመደገፍ IROKA የሚባለውን የተለየ የAI መሠረት ይመድባል።",
    irokaState: "የመዋቅር ዝግጅት · ገና አልተገናኘም", boundary: "የአሁኑ የውህደት ሁኔታ",
    boundaryText: "የIROKA አገልግሎት፣ API፣ ማረጋገጫ ወይም የሩጫ አካባቢ ከMaaleNex ጋር አልተገናኘም። ይህ ገጽ የታቀደውን መዋቅር ብቻ ያሳያል።",
    back: "ወደ መነሻ ተመለስ", footer: "የልማት ቅድመ እይታ · እውነተኛ የመጓጓዣ አገልግሎት አይደለም",
    status: "የልማት ሁኔታ", statusValue: "የህዝብ ቅድመ እይታ"
  },
  en: {
    brand: "MaaleNex", navHome: "Home", navAbout: "About", navIroka: "IROKA",
    language: "ቋንቋውን ወደ አማርኛ ቀይር", eyebrow: "PASSENGER MOBILITY · A NEW PERSPECTIVE",
    title: "Move with ease. Move forward with confidence.",
    intro: "MaaleNex is a technology platform being prepared to improve the passenger mobility experience in Ethiopia. This is a public preview of the product.",
    welcome: "A warm welcome to MaaleNex", welcomeSub: "Rooted in local understanding. Built with thoughtful technology.",
    guest: "Explore as a guest", guestHint: "Discover public information without creating an account.",
    current: "Current scope", currentText: "Passenger product preparation only. No verified schedules, fares, or operating services are being represented.",
    future: "A better mobility experience", futureText: "A mobility experience shaped by useful information, clear operations, and responsible technology.",
    safety: "Development preview only. There is no account, personal-data form, booking, payment, or ticketing in this experience.",
    aboutTitle: "About MaaleNex", aboutLead: "Mobility technology with local roots.",
    aboutText: "MaaleNex is being developed to create a better information and journey-planning experience for passengers in Ethiopia. The initial development focus is the Jinka and South Omo area.",
    mission: "Our mission", missionText: "Build accessible, transparent mobility technology grounded in local realities.",
    principles: "Our principles", principlesText: "Safety, transparency, user dignity, local relevance, and staged delivery.",
    pilot: "Development focus", pilotText: "The initial development direction includes Koybe, Jinka, and the South Omo area. This describes the project focus, not an announcement of an operating route.",
    irokaTitle: "IROKA intelligence layer", irokaText: "MaaleNex reserves a governed integration boundary for IROKA, a separate AI foundation, to support future intelligence capabilities.",
    irokaState: "Architecture prepared · not connected", boundary: "Current integration status",
    boundaryText: "No IROKA service, API, authentication, or runtime is connected to MaaleNex. This page describes the intended architecture only.",
    back: "Back to home", footer: "Development preview · not a live transport service",
    status: "Product status", statusValue: "Public preview"
  }
} as const;

function Icon({ name }: { name: "home" | "compass" | "spark" | "arrow" | "shield" | "globe" }) {
  const paths = {
    home: <><path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z" /></>,
    compass: <><circle cx="12" cy="12" r="9" /><path d="m15.8 8.2-2.6 5-5 2.6 2.6-5z" /></>,
    spark: <><path d="m12 3 1.9 5.8L20 11l-6.1 2.2L12 19l-1.9-5.8L4 11l6.1-2.2z" /><path d="m19 15 1 2 2 1-2 1-1 2-1-2-2-1 2-1z" /></>,
    arrow: <><path d="M5 12h14M13 6l6 6-6 6" /></>,
    shield: <><path d="M12 3 20 6v5c0 5-3.4 8.4-8 10-4.6-1.6-8-5-8-10V6z" /><path d="m8.5 12 2.2 2.2 4.8-5" /></>,
    globe: <><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18" /></>
  };
  return <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">{paths[name]}</svg>;
}

export default function App() {
  const [language, setLanguage] = useState<Language>("am");
  const [page, setPage] = useState<Page>("home");
  const [guestNotice, setGuestNotice] = useState(false);
  const t = copy[language];
  useEffect(() => { document.documentElement.lang = language; }, [language]);
  const navigate = (next: Page) => {
    setPage(next);
    setGuestNotice(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return <div className="app-shell" lang={language}>
    <a className="skip-link" href="#main-content">{language === "am" ? "ወደ ዋና ይዘት ዝለል" : "Skip to main content"}</a>
    <header className="site-header">
      <button className="brand-lockup" type="button" onClick={() => navigate("home")} aria-label="MaaleNex home">
        <img src="./brand/maalenex-symbol.svg" alt="" width="42" height="42" /><span>MaaleNex</span>
      </button>
      <nav className="main-nav" aria-label={language === "am" ? "ዋና ማሰሻ" : "Main navigation"}>
        <button type="button" className={page === "home" ? "nav-link active" : "nav-link"} onClick={() => navigate("home")} aria-current={page === "home" ? "page" : undefined}><Icon name="home" />{t.navHome}</button>
        <button type="button" className={page === "about" ? "nav-link active" : "nav-link"} onClick={() => navigate("about")} aria-current={page === "about" ? "page" : undefined}><Icon name="compass" />{t.navAbout}</button>
        <button type="button" className={page === "iroka" ? "nav-link active" : "nav-link"} onClick={() => navigate("iroka")} aria-current={page === "iroka" ? "page" : undefined}><Icon name="spark" />{t.navIroka}</button>
      </nav>
      <button className="language-switch" type="button" aria-label={t.language} onClick={() => setLanguage(language === "am" ? "en" : "am")}><Icon name="globe" />{language === "am" ? "EN" : "አማ"}</button>
    </header>

    <main id="main-content" tabIndex={-1}>
      {page === "home" && <div className="home-page">
        <section className="welcome-hero">
          <div className="hero-orbit orbit-one" /><div className="hero-orbit orbit-two" /><div className="hero-grid" />
          <div className="hero-copy">
            <p className="eyebrow"><span className="eyebrow-dot" />{t.eyebrow}</p>
            <h1>{t.title}</h1><p className="hero-intro">{t.intro}</p>
            <div className="welcome-note"><span className="welcome-mark">✦</span><div><strong>{t.welcome}</strong><span>{t.welcomeSub}</span></div></div>
            <button className="primary-action" type="button" onClick={() => setGuestNotice(true)}>{t.guest}<Icon name="arrow" /></button>
            <p className="action-caption">{t.guestHint}</p>
            {guestNotice && <p className="inline-status" role="status">{t.guestHint}</p>}
          </div>
          <div className="hero-art" aria-hidden="true">
            <div className="art-ring ring-a" /><div className="art-ring ring-b" /><div className="art-core"><img src="./brand/maalenex-symbol.svg" alt="" /></div>
            <span className="art-node node-a" /><span className="art-node node-b" /><span className="art-node node-c" />
            <div className="art-label label-a">LOCAL ROOTS</div><div className="art-label label-b">CONNECTED FUTURE</div>
          </div>
          <div className="hero-bottom"><span>MAALENEX / 01</span><span>{t.status} · {t.statusValue}</span></div>
        </section>
        <section className="intro-grid">
          <article className="info-card feature-card"><span className="card-icon"><Icon name="compass" /></span><p className="card-kicker">01 / {t.current}</p><h2>{t.current}</h2><p>{t.currentText}</p></article>
          <article className="info-card feature-card"><span className="card-icon"><Icon name="spark" /></span><p className="card-kicker">02 / {t.future}</p><h2>{t.future}</h2><p>{t.futureText}</p></article>
          <article className="info-card safety-card"><span className="card-icon"><Icon name="shield" /></span><p className="card-kicker">03 / RESPONSIBLE BY DESIGN</p><h2>{language === "am" ? "ደህንነት ከመጀመሪያ" : "Responsibility first"}</h2><p>{t.safety}</p></article>
        </section>
      </div>}
      {page === "about" && <section className="content-page">
        <p className="eyebrow"><span className="eyebrow-dot" />MAALENEX / ABOUT</p><h1>{t.aboutTitle}</h1><p className="page-lead">{t.aboutLead}</p><p className="body-copy">{t.aboutText}</p>
        <div className="about-grid">
          <article className="info-card"><span className="card-icon"><Icon name="compass" /></span><h2>{t.mission}</h2><p>{t.missionText}</p></article>
          <article className="info-card"><span className="card-icon"><Icon name="shield" /></span><h2>{t.principles}</h2><p>{t.principlesText}</p></article>
          <article className="info-card"><span className="card-icon"><Icon name="globe" /></span><h2>{t.pilot}</h2><p>{t.pilotText}</p></article>
        </div>
        <button className="text-action" type="button" onClick={() => navigate("home")}>{t.back}<Icon name="arrow" /></button>
      </section>}
      {page === "iroka" && <section className="content-page iroka-page">
        <p className="eyebrow"><span className="eyebrow-dot" />MAALENEX / INTELLIGENCE ARCHITECTURE</p><h1>{t.irokaTitle}</h1><p className="page-lead">{t.irokaText}</p>
        <div className="iroka-status"><span className="status-indicator" /><div><strong>{t.irokaState}</strong><span>{t.boundary}</span></div></div>
        <div className="architecture-flow" aria-label="Planned IROKA integration architecture">
          <div className="architecture-node"><span>01</span><strong>MaaleNex UI</strong><small>Passenger experience</small></div><div className="flow-connector"><i /></div>
          <div className="architecture-node"><span>02</span><strong>Integration adapter</strong><small>Typed capability contract</small></div><div className="flow-connector dashed"><i /></div>
          <div className="architecture-node pending"><span>03</span><strong>IROKA backbone</strong><small>Separate intelligence runtime</small></div>
        </div>
        <div className="boundary-note"><strong>{t.boundary}</strong><p>{t.boundaryText}</p></div>
        <button className="text-action" type="button" onClick={() => navigate("home")}>{t.back}<Icon name="arrow" /></button>
      </section>}
    </main>
    <footer className="site-footer"><div className="footer-brand"><img src="./brand/maalenex-symbol.svg" alt="" width="26" height="26" /><strong>MaaleNex</strong></div><span>{t.footer}</span><span>© MaaleNex Technologies</span></footer>
  </div>;
}
