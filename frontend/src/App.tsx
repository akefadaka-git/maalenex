import { useEffect, useState } from "react";

type Language = "am" | "en";

const content = {
  am: {
    eyebrow: "የሞተር ተንቀሳቃሽነት እና አገልግሎት",
    title: "ማአሌኔክስ ሞቶ",
    subtitle: "በአካባቢያችን የተገነባ፣ ለእርስዎ የተዘጋጀ የሞተር አገልግሎት መድረክ።",
    status: "የልማት ሁኔታ",
    note: "ይህ የሙከራ መሠረት ነው። እውነተኛ ተሳፋሪ፣ ሹፌር ወይም ጉዞ መረጃ አይጠቀምም።",
    cards: ["የጉዞ ጥያቄ", "የሞተር ጥገና", "የሹፌር አገልግሎት"],
    languageAction: "Switch language to English",
  },
  en: {
    eyebrow: "MOTORCYCLE MOBILITY & SERVICES",
    title: "MaaleNex Moto",
    subtitle: "A locally grounded motorcycle service platform, designed around community needs.",
    status: "Development environment",
    note: "Synthetic development foundation only. No real passenger, driver, or trip data is accepted.",
    cards: ["Ride requests", "Motorcycle maintenance", "Driver services"],
    languageAction: "ቋንቋውን ወደ አማርኛ ቀይር",
  },
};

export default function App() {
  const [language, setLanguage] = useState<Language>("am");
  const t = content[language];

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  return (
    <main className="page" lang={language}>
      <header className="topbar">
        <a className="brand" href="/" aria-label="MaaleNex Moto home">
          <span className="brand-mark" aria-hidden="true">M</span>
          MAALENEX
        </a>
        <div className="top-actions">
          <span className="environment">{t.status}</span>
          <button
            className="language"
            type="button"
            aria-label={t.languageAction}
            onClick={() => setLanguage(language === "am" ? "en" : "am")}
          >
            {language === "am" ? "EN" : "አማ"}
          </button>
        </div>
      </header>

      <section className="hero" aria-labelledby="hero-title">
        <p className="eyebrow">{t.eyebrow}</p>
        <h1 id="hero-title">{t.title}</h1>
        <p className="subtitle">{t.subtitle}</p>
        <div className="hero-rule" aria-hidden="true" />
        <div className="service-grid">
          {t.cards.map((card, index) => (
            <article className="service-card" key={card}>
              <span className="service-number">0{index + 1}</span>
              <h2>{card}</h2>
              <span className="service-arrow" aria-hidden="true">↗</span>
            </article>
          ))}
        </div>
      </section>

      <footer>
        <span>{t.note}</span>
        <span>© MaaleNex Moto · 2026</span>
      </footer>
    </main>
  );
}
