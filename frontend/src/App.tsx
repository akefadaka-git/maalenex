import { useRef, useState } from "react";
import { Badge, BottomNavigation, Button, Card, Dialog } from "./components/ui";

type Language = "am" | "en";
const copy = {
  am: {
    brand: "ማአሌኔክስ", product: "ሞቶ", eyebrow: "የአካባቢ ተንቀሳቃሽነት · በአካባቢው የተገነባ",
    title: "ጉዞዎን በቀላሉ ያቅዱ።", subtitle: "ለማአሌ ማህበረሰብ የተዘጋጀ የሞተር ተንቀሳቃሽነትና አገልግሎት መድረክ።",
    status: "የልማት አካባቢ", pilot: "የሙከራ አካባቢ", pilotPlace: "ኮይቤ · ጂንካ",
    action: "የጉዞ ጥያቄ ይጀምሩ", actionNote: "የሙከራ ቅድመ እይታ · ትክክለኛ ጉዞ አይመዘገብም",
    services: "አገልግሎቶች", servicesNote: "የሚያስፈልግዎትን ይምረጡ",
    rides: "የጉዞ ጥያቄ", rideDesc: "የጉዞ አማራጮችን ያስሱ።",
    care: "የሞተር ጥገና", careDesc: "የጥገናና የእንክብካቤ መረጃ።",
    drivers: "የሹፌር አገልግሎት", driverDesc: "ለአገልግሎት ሰጪዎች መረጃ።",
    how: "አካባቢያዊ አገልግሎት፣ በኃላፊነት", howDesc: "በመጀመሪያ የአካባቢ ፍላጎትን እና ደህንነትን እናስቀድማለን።",
    home: "መነሻ", explore: "አገልግሎቶች", help: "እገዛ",
    dialogTitle: "የሙከራ ቅድመ እይታ", dialogText: "የጉዞ ጥያቄ ባህሪው ገና አልተከፈተም። ይህ ስሪት ለዲዛይንና ለሙከራ ብቻ ነው፤ ትክክለኛ ተሳፋሪ፣ ሹፌር፣ ክፍያ ወይም ጉዞ መረጃ አይቀበልም።",
    close: "ዝጋ", note: "የልማት ስሪት · ሰው ወይም የጉዞ መረጃ አይሰበስብም"
  },
  en: {
    brand: "MAALENEX", product: "MOTO", eyebrow: "LOCAL MOBILITY · BUILT WITH COMMUNITY",
    title: "Make your journey simpler.", subtitle: "A locally grounded motorcycle mobility and services platform designed around Maale community needs.",
    status: "Development environment", pilot: "Pilot area", pilotPlace: "Koybe · Jinka",
    action: "Explore a ride request", actionNote: "Preview only · no real trips are created",
    services: "Services", servicesNote: "Explore what you need",
    rides: "Ride requests", rideDesc: "Explore future ride options.",
    care: "Motorcycle care", careDesc: "Maintenance and care information.",
    drivers: "Driver services", driverDesc: "Information for service providers.",
    how: "Local service, responsibly", howDesc: "Community needs and safety come first.",
    home: "Home", explore: "Services", help: "Help",
    dialogTitle: "Development preview", dialogText: "Ride requesting is not enabled yet. This build is for design and testing only; it does not accept real passenger, driver, payment, or trip information.",
    close: "Close", note: "Development build · no personal or trip data collected"
  }
} as const;

export default function App() {
  const [language,setLanguage]=useState<Language>("am");
  const dialogRef=useRef<HTMLDialogElement>(null);
  const t=copy[language];
  const services=[
    {number:"01",icon:"↗",title:t.rides,description:t.rideDesc},
    {number:"02",icon:"✳",title:t.care,description:t.careDesc},
    {number:"03",icon:"⌁",title:t.drivers,description:t.driverDesc}
  ];
  return <main className="mn-app" lang={language} id="home">
    <header className="mn-app-header">
      <a className="mn-app-brand" href="#home" aria-label="MaaleNex Moto home"><span className="mn-app-symbol">M</span><span><strong>{t.brand}</strong><small>{t.product}</small></span></a>
      <div className="mn-header-actions"><Badge tone="info">{t.status}</Badge><Button variant="secondary" size="small" onClick={()=>setLanguage(language==="am"?"en":"am")} aria-label={language==="am"?"Switch language to English":"ቋንቋን ወደ አማርኛ ቀይር"}>{language==="am"?"EN":"አማ"}</Button></div>
    </header>
    <section className="mn-hero">
      <div className="mn-hero-copy"><p className="mn-eyebrow">{t.eyebrow}</p><h1>{t.title}</h1><p className="mn-lead">{t.subtitle}</p>
        <div className="mn-hero-actions"><Button size="large" onClick={()=>dialogRef.current?.showModal()}>{t.action}<span aria-hidden="true">↗</span></Button><span className="mn-action-note">{t.actionNote}</span></div>
      </div>
      <Card className="mn-location-card"><span className="mn-location-orbit" aria-hidden="true">⌖</span><div><span className="mn-overline">{t.pilot}</span><strong>{t.pilotPlace}</strong></div><Badge tone="warning">{language==="am"?"በዝግጅት ላይ":"Preparing"}</Badge></Card>
    </section>
    <section className="mn-services" id="services"><div className="mn-section-heading"><div><p className="mn-eyebrow">{language==="am"?"የማአሌኔክስ ሞቶ":"MAALENEX MOTO"}</p><h2>{t.services}</h2></div><span>{t.servicesNote}</span></div>
      <div className="mn-service-grid">{services.map(service=><Card key={service.number} className="mn-service-card"><span className="mn-service-top"><span>{service.number}</span><span className="mn-service-icon" aria-hidden="true">{service.icon}</span></span><div><h3>{service.title}</h3><p>{service.description}</p></div><span className="mn-card-arrow" aria-hidden="true">↗</span></Card>)}</div>
    </section>
    <section className="mn-community" id="help"><div className="mn-community-mark" aria-hidden="true">M</div><div><h2>{t.how}</h2><p>{t.howDesc}</p></div><Badge tone="success">{language==="am"?"ደህንነት ቅድሚያ":"Safety first"}</Badge></section>
    <footer className="mn-app-footer"><span>{t.note}</span><span>© MaaleNex Moto · 2026</span></footer>
    <BottomNavigation label={language==="am"?"ዋና ማሰሻ":"Main navigation"} items={[{href:"#home",label:t.home,icon:"⌂",current:true},{href:"#services",label:t.explore,icon:"▦"},{href:"#help",label:t.help,icon:"?"}]}/>
    <Dialog ref={dialogRef} title={t.dialogTitle} onRequestClose={()=>dialogRef.current?.close()}><p>{t.dialogText}</p><Button onClick={()=>dialogRef.current?.close()}>{t.close}</Button></Dialog>
  </main>;
}
