import { useEffect, useState } from "react";

type Language = "am" | "en";
const text = {
  am: {
    brand: "MaaleNex", eyebrow: "የተሳፋሪ መጓጓዣ · የልማት ቅድመ እይታ",
    title: "ጉዞዎን በኃላፊነት ያቅዱ።",
    intro: "MaaleNex ለተሳፋሪ መጓጓዣ የሚዘጋጅ መድረክ ነው። ይህ የህዝብ እንግዳ ቅድመ እይታ ብቻ ነው።",
    guest: "እንደ እንግዳ ይቀጥሉ", guestText: "የህዝብ መረጃን ያለ መለያ ይመልከቱ።",
    scope: "የአሁኑ ወሰን", scopeText: "የተሳፋሪ ምርት ዝግጅት ብቻ፤ የተረጋገጡ የጉዞ መርሐ ግብሮች፣ ታሪፎች ወይም የሚሰሩ አገልግሎቶች አልተገለጹም።",
    safety: "ይህ ማሳያ ነው። የመለያ መግቢያ፣ ምዝገባ፣ የግል መረጃ ማስገቢያ፣ ቦታ ማስያዣ፣ ክፍያ ወይም ትኬት አይኖርም።",
    future: "የወደፊት ወሰን", futureText: "የሹፌር፣ የጭነት እና የፍሊት ስራዎች በተለየ የወደፊት ደረጃ ይገመገማሉ፤ በዚህ የህዝብ ምርት ውስጥ አይገኙም።",
    language: "Switch language to English", footer: "የልማት ቅድመ እይታ · እውነተኛ የመጓጓዣ አገልግሎት አይደለም"
  },
  en: {
    brand: "MaaleNex", eyebrow: "PASSENGER MOBILITY · DEVELOPMENT PREVIEW",
    title: "Plan your journey responsibly.",
    intro: "MaaleNex is being prepared as a passenger mobility platform. This is a public guest preview only.",
    guest: "Continue as guest", guestText: "Explore public information without creating an account.",
    scope: "Current scope", scopeText: "Passenger product preparation only. No verified schedules, fares, or operating services are being represented.",
    safety: "Demonstration only. There is no sign-in, registration, personal-data form, booking, payment, or ticketing in this preview.",
    future: "Future scope", futureText: "Driver, cargo, and fleet capabilities are reserved for separately governed future phases and are not part of this public product.",
    language: "ቋንቋውን ወደ አማርኛ ቀይር", footer: "Development preview · not a live transport service"
  }
} as const;

export default function App() {
  const [language, setLanguage] = useState<Language>("am");
  const [guest, setGuest] = useState(false);
  const t = text[language];
  useEffect(() => { document.documentElement.lang = language; }, [language]);
  return <main className="page" lang={language}>
    <a className="skip-link" href="#main-content">{language === "am" ? "ወደ ዋና ይዘት ዝለል" : "Skip to main content"}</a>
    <header className="topbar">
      <a className="brand" href="/" aria-label="MaaleNex home">
        <img src="/brand/maalenex-symbol.svg" alt="" width="38" height="38" />
        <span>{t.brand}</span>
      </a>
      <button className="language" type="button" aria-label={t.language}
        onClick={() => setLanguage(language === "am" ? "en" : "am")}>{language === "am" ? "EN" : "አማ"}</button>
    </header>
    <section id="main-content" className="hero">
      <p className="eyebrow">{t.eyebrow}</p>
      <h1>{t.title}</h1>
      <p className="subtitle">{t.intro}</p>
      <section className="guest-panel" aria-labelledby="guest-title">
        <h2 id="guest-title">{t.guest}</h2>
        <p>{t.guestText}</p>
        <button className="search-button" type="button" onClick={() => setGuest(true)}>{t.guest}</button>
        {guest && <p className="notice" role="status">{t.guestText}</p>}
      </section>
      <section className="scope-panel">
        <h2>{t.scope}</h2><p>{t.scopeText}</p>
      </section>
      <p className="notice" role="note">{t.safety}</p>
      <section className="future-panel">
        <h2>{t.future}</h2><p>{t.futureText}</p>
      </section>
    </section>
    <footer><span>{t.footer}</span><span>© MaaleNex</span></footer>
  </main>;
}
