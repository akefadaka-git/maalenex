import type { Language } from "./types";

type AboutPageProps = {
  language: Language;
  onBack: () => void;
};

const profile = {
  name: "Akefa Ayele Daka",
  phone: "0916546488",
  email: "akefaayele@gmail.com",
  facebook: "https://www.facebook.com/akefa.ayele",
  telegram: "https://t.me/akefaayle",
  youtube: "https://www.youtube.com/@akefaayele6547",
};

export default function AboutPage({ language, onBack }: AboutPageProps) {
  const am = language === "am";

  return (
    <section className="about-page" aria-labelledby="about-title">
      <div className="about-heading">
        <p className="eyebrow">{am ? "ስለ መድረኩ" : "ABOUT THE PLATFORM"}</p>
        <h1 id="about-title">{am ? "ስለ MaaleNex" : "About MaaleNex"}</h1>
        <p className="subtitle">
          {am
            ? "ለኢትዮጵያ የተገነባ፣ ከክልላዊ የተሳፋሪ ጉዞ የሚጀምር የመጓጓዣ ቴክኖሎጂ መድረክ።"
            : "An Ethiopian mobility technology platform, beginning with regional passenger journeys."}
        </p>
      </div>

      <div className="about-grid">
        <article className="about-card about-intro">
          <p className="about-kicker">{am ? "የMaaleNex ራዕይ" : "THE MAALENEX VISION"}</p>
          <h2>{am ? "ጉዞን ቀላል፣ ግልጽ እና የተደራጀ ማድረግ" : "Making mobility easier to discover, understand and manage"}</h2>
          <p>
            {am
              ? "MaaleNex የተሳፋሪ ጉዞ መረጃን እና የቦታ ማስያዣ ሂደቶችን ለማሻሻል እየተገነባ ያለ የቴክኖሎጂ መድረክ ነው። የመጀመሪያው ትኩረት በጂንካ እና በደቡብ ኦሞ አካባቢ ያሉ የክልል ጉዞዎች ላይ ነው።"
              : "MaaleNex is being developed to improve how passengers discover journeys and manage reservation workflows. Its initial focus is regional travel around Jinka and South Omo, with a foundation designed to support broader mobility services over time."}
          </p>
        </article>

        <article className="about-card">
          <p className="about-kicker">{am ? "የመተግበሪያው ባህሪያት" : "ABOUT THE APP"}</p>
          <h2>{am ? "የተሳፋሪ ጉዞ ማስተዳደር" : "Passenger journey tools"}</h2>
          <ul>
            <li>{am ? "የታተሙ የጉዞ መርሐ ግብሮችን መፈለግ" : "Search published journey schedules"}</li>
            <li>{am ? "የወንበር መገኘትን ማየት እና መምረጥ" : "View availability and select seats"}</li>
            <li>{am ? "ጊዜያዊ የቦታ ይዞታ እና የማስያዣ ማጣቀሻ" : "Temporary reservation holds and references"}</li>
            <li>{am ? "የቦታ ማስያዣ መዳረሻን ማስተዳደር" : "Manage reservation access and support requests"}</li>
          </ul>
        </article>

        <article className="about-card about-status">
          <p className="about-kicker">{am ? "የአገልግሎት ሁኔታ" : "SERVICE STATUS"}</p>
          <h2>{am ? "በልማት እና በሙከራ ላይ" : "In development and testing"}</h2>
          <p>
            {am
              ? "ይህ ስሪት ሰው ሠራሽ የሙከራ መረጃ ብቻ ይጠቀማል። እውነተኛ ቦታ ማስያዝ፣ ክፍያ፣ የጉዞ ትኬት መስጠት እና መሳፈር አልተነቁም።"
              : "This version uses synthetic test data only. Real passenger bookings, payment collection, travel-ticket issuance and boarding are not enabled. Published schedules and availability must be verified by an authorized operator before any real journey."}
          </p>
          <span className="about-status-label">{am ? "የሙከራ አካባቢ · እውነተኛ ግብይት የለም" : "TEST ENVIRONMENT · NO LIVE TRANSACTIONS"}</span>
        </article>

        <article className="about-card about-creator">
          <p className="about-kicker">{am ? "ፈጣሪ" : "CREATOR"}</p>
          <h2>{profile.name}</h2>
          <p>{am ? "የMaaleNex ፕሮጀክት ፈጣሪ።" : "Creator of the MaaleNex project."}</p>
          <div className="about-contact-list">
            <a href={`tel:${profile.phone}`}>{am ? "ስልክ" : "Phone"} · {profile.phone}</a>
            <a href={`mailto:${profile.email}`}>{profile.email}</a>
          </div>
          <div className="about-socials" aria-label={am ? "ማህበራዊ ሚዲያ" : "Social profiles"}>
            <a href={profile.facebook} target="_blank" rel="noopener noreferrer">Facebook</a>
            <a href={profile.telegram} target="_blank" rel="noopener noreferrer">Telegram</a>
            <a href={profile.youtube} target="_blank" rel="noopener noreferrer">YouTube</a>
          </div>
          <div className="about-portfolio">
            <strong>{am ? "የግል ፖርትፎሊዮ" : "Personal portfolio"}</strong>
            <p>{am ? "የፖርትፎሊዮ አድራሻው ሲሰጥ እዚህ ይጨመራል።" : "Portfolio link will be added when its URL is provided."}</p>
          </div>
        </article>
      </div>

      <div className="about-actions">
        <button className="secondary-button" type="button" onClick={onBack}>
          {am ? "ወደ ጉዞ ፍለጋ ተመለስ" : "Back to trip search"}
        </button>
      </div>
    </section>
  );
}
