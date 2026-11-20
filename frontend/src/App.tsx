import { useEffect, useState } from "react";
import {
  getCurrentPassenger,
  loginPassenger,
  logoutPassenger,
  registerPassenger,
  updatePassengerProfile,
  type PassengerSession,
} from "./passenger-api";
import { Icon } from "./components/nexus-icons";

type Language = "am" | "en";
type Page = "dashboard" | "map" | "wallet" | "profile" | "help" | "report" | "login" | "register" | "forgot" | "about";
const labels = {
  am: { dashboard:"ዳሽቦርድ", map:"ካርታ", wallet:"ቦርሳ", profile:"መገለጫ", help:"እገዛ", report:"ሪፖርት", login:"ግባ", register:"መለያ ፍጠር", about:"ስለ እኛ", welcome:"ወደ MaaleNex እንኳን በደህና መጡ", subtitle:"የጉዞዎን ቀጣይ እርምጃ በአንድ ቦታ ያቀናብሩ።", search:"መነሻ ወይም መድረሻ ይፈልጉ", quick:"ፈጣን አገልግሎቶች", journeys:"የጉዞ መረጃ", empty:"የተረጋገጠ የጉዞ መረጃ ሲገኝ እዚህ ይታያል።", balance:"የቦርሳ ቀሪ ሂሳብ", demo:"የማሳያ ሁኔታ", noFunds:"የእውነተኛ ገንዘብ ግብይት አልነቃም።", mapNote:"ካርታው የአካባቢ ማሳያ ነው፤ የተረጋገጡ መስመሮች ገና አልታተሙም።", name:"ሙሉ ስም", phone:"ስልክ ቁጥር", password:"የይለፍ ቃል", email:"ኢሜይል", submit:"ቀጥል", coming:"ይህ ባህሪ ከደህንነት እና ከአገልግሎት ማገናኛ ማረጋገጫ በኋላ ይነቃል።", support:"እንዴት ልንርዳዎ?", reportTitle:"ችግር ሪፖርት ያድርጉ", message:"መልዕክትዎ", send:"ሪፖርት ላክ", sent:"የማሳያ ሪፖርት ተመዝግቧል። አሁንም ወደ ድጋፍ ሰርቨር አልተላከም።", account:"መለያዎን ያስተዳድሩ", language:"ቋንቋ", notifications:"ማሳወቂያዎች", signout:"ውጣ", noLogin:"አሁን የማሳያ ሁኔታ ብቻ ነው።" },
  en: { dashboard:"Dashboard", map:"Map", wallet:"Wallet", profile:"Profile", help:"Help", report:"Report", login:"Log in", register:"Create account", about:"About", welcome:"Welcome to MaaleNex", subtitle:"Your mobility tools, information and support in one place.", search:"Search origin or destination", quick:"Quick access", journeys:"Journey information", empty:"Verified journey information will appear here when published.", balance:"Wallet balance", demo:"DEMO MODE", noFunds:"Real-money transactions are not enabled.", mapNote:"This is a map preview. No verified operating routes have been published yet.", name:"Full name", phone:"Phone number", password:"Password", email:"Email", submit:"Continue", coming:"This capability will activate after security and service-provider verification.", support:"How can we help?", reportTitle:"Report an issue", message:"Your message", send:"Submit report", sent:"Demo report captured locally. It has not been sent to a support server.", account:"Manage your account", language:"Language", notifications:"Notifications", signout:"Sign out", noLogin:"This is currently a demonstration session only." }
} as const;

type NavPage = Exclude<Page, "login" | "register" | "forgot" | "about">;
const nav: NavPage[] = ["dashboard","map","wallet","profile","help","report"];
const iconFor: Record<Page, "home"|"map"|"wallet"|"user"|"help"|"flag"|"compass"|"globe"|"shield"|"route"|"arrow"> = {
 dashboard:"home", map:"map", wallet:"wallet", profile:"user", help:"help", report:"flag", login:"user", register:"user", forgot:"shield", about:"compass"
};

function Tile({title,detail,onClick,icon}:{title:string;detail:string;onClick:()=>void;icon:Page}) {
 return <button className="service-tile" onClick={onClick}><span className="tile-icon"><Icon name={iconFor[icon]}/></span><span><strong>{title}</strong><small>{detail}</small></span><Icon name="arrow"/></button>;
}

export default function App() {
 const [language,setLanguage]=useState<Language>("am");
 const [page,setPage]=useState<Page>("dashboard");
 const [notice,setNotice]=useState("");
 const [report,setReport]=useState("");
 const [passwordVisible,setPasswordVisible]=useState(false);
 const [profileEditing,setProfileEditing]=useState(false);
 const [profileName,setProfileName]=useState("");
 const [profilePhone,setProfilePhone]=useState("");
 const [profileEmail,setProfileEmail]=useState("");
 const [profileSaved,setProfileSaved]=useState(false);
 const [isOnline,setIsOnline]=useState(true);
 const [passenger,setPassenger]=useState<PassengerSession|null>(null);
 const [authIdentifier,setAuthIdentifier]=useState("");
 const [authName,setAuthName]=useState("");
 const [authPassword,setAuthPassword]=useState("");
 const [authConfirmPassword,setAuthConfirmPassword]=useState("");
 const [authBusy,setAuthBusy]=useState(false);
 const t=labels[language];
 useEffect(()=>{document.documentElement.lang=language;},[language]);
 useEffect(()=>{
  let active=true;
  getCurrentPassenger().then(account=>{
   if(!active)return;
   setPassenger(account);setProfileName(account.display_name);
   setProfilePhone(account.login_identifier.startsWith("+")?account.login_identifier:"");
   setProfileEmail(account.login_identifier.includes("@")?account.login_identifier:"");
  }).catch(()=>undefined);
  return()=>{active=false;};
 },[]);
 useEffect(()=>{
  const syncOnline=()=>setIsOnline(navigator.onLine);
  const handleOffline=()=>{setIsOnline(false);setNotice(language==="am"?"የኢንተርኔት ግንኙነት የለም። የተቀመጡ ማያዎችን ብቻ ይጠቀሙ።":"You are offline. Only locally available screens can be used.");};
  const handleOnline=()=>{setIsOnline(true);setNotice(language==="am"?"ግንኙነት ተመልሷል። የቀድሞ ያልተላኩ ለውጦች በራስ-ሰር አልተላኩም።":"Connection restored. Previously unsent changes have not been synchronized.");};
  window.addEventListener("online",handleOnline);window.addEventListener("offline",handleOffline);syncOnline();
  return()=>{window.removeEventListener("online",handleOnline);window.removeEventListener("offline",handleOffline);};
 },[language]);
 const go=(next:Page)=>{setPage(next);setNotice("");};
 const submitAuth=async(e:React.FormEvent<HTMLFormElement>)=>{
  e.preventDefault();
  if(page==="forgot"){setNotice(t.coming);return;}
  if(page==="register"&&authPassword!==authConfirmPassword){setNotice(language==="am"?"የይለፍ ቃሎቹ አይዛመዱም።":"The passwords do not match.");return;}
  setAuthBusy(true);setNotice("");
  try{
   const account=page==="register"
    ?await registerPassenger({login_identifier:authIdentifier.trim(),display_name:authName.trim(),password:authPassword})
    :await loginPassenger({login_identifier:authIdentifier.trim(),password:authPassword});
   setPassenger(account);setProfileName(account.display_name);
   setProfilePhone(account.login_identifier.startsWith("+")?account.login_identifier:"");
   setProfileEmail(account.login_identifier.includes("@")?account.login_identifier:"");
   setAuthPassword("");setAuthConfirmPassword("");setPage("dashboard");
   setNotice(language==="am"?"መለያዎ በተሳካ ሁኔታ ተገናኝቷል።":"You are signed in to your MaaleNex account.");
  }catch(error){setNotice(error instanceof Error?error.message:(language==="am"?"የመለያ ግንኙነት አልተሳካም።":"Account request failed."));}
  finally{setAuthBusy(false);}
 };
 const signOut=async()=>{
  try{await logoutPassenger();setPassenger(null);setProfileName("");setProfilePhone("");setProfileEmail("");setPage("dashboard");setNotice(language==="am"?"ከመለያዎ ወጥተዋል።":"You have signed out.");}
  catch(error){setNotice(error instanceof Error?error.message:"Unable to sign out.");}
 };
 const saveProfile=async(e:React.FormEvent<HTMLFormElement>)=>{
  e.preventDefault();
  if(!passenger){setProfileSaved(true);setProfileEditing(false);setNotice(language==="am"?"ይህ ለውጥ በማሳያ ላይ ብቻ ነው።":"Preview changes are local only. Sign in to save a profile.");return;}
  try{const updated=await updatePassengerProfile(profileName);setPassenger(updated);setProfileName(updated.display_name);setProfileEditing(false);setProfileSaved(true);setNotice(language==="am"?"መገለጫዎ ተቀምጧል።":"Your profile has been saved.");}
  catch(error){setNotice(error instanceof Error?error.message:"Unable to save your profile.");}
 };
 const title=t[page as keyof typeof t] ?? t.dashboard;
 return <div className="app-shell platform-shell" lang={language}>
  <a className="skip-link" href="#main-content">{language==="am"?"ወደ ዋና ይዘት ዝለል":"Skip to main content"}</a>
  <header className="platform-header">
   <button className="brand-lockup" onClick={()=>go("dashboard")} aria-label="MaaleNex dashboard"><img src="./brand/maalenex-nexus-emblem.svg" alt="" width="42" height="42"/><span>MaaleNex</span></button>
   <div className="header-context"><span className={isOnline?"online-dot":"online-dot offline-dot"}/><span>{!isOnline?(language==="am"?"ከመስመር ውጭ":"Offline"):(language==="am"?"የተጠቃሚ ማዕከል":"Passenger hub")}</span></div>
   <div className="header-actions"><button className="icon-button" aria-label={t.notifications} onClick={()=>setNotice(t.coming)}><Icon name="bell"/></button><button className="language-switch" onClick={()=>setLanguage(language==="am"?"en":"am")}><Icon name="globe"/>{language==="am"?"EN":"አማ"}</button><button className="profile-chip" onClick={()=>go("profile")}><Icon name="user"/><span>{language==="am"?"መገለጫ":"Profile"}</span></button></div>
  </header>
  <div className="platform-layout">
   <nav className="side-nav" aria-label="Main navigation">
    <p className="nav-caption">{language==="am"?"ዋና ማሰሻ":"WORKSPACE"}</p>
    {nav.map(item=><button key={item} className={page===item?"side-link active":"side-link"} onClick={()=>go(item)}><Icon name={iconFor[item]}/><span>{t[item]}</span></button>)}
    <div className="side-spacer"/>
    <button className="side-link" onClick={()=>go("about")}><Icon name="compass"/><span>{t.about}</span></button>
    <div className="side-account"><span className="avatar-mark">M</span><span><strong>MaaleNex</strong><small>{language==="am"?"የእንግዳ ማሳያ":"Guest preview"}</small></span></div>
   </nav>
   <main id="main-content" className="platform-main" tabIndex={-1}>
    <div className="page-heading"><div><p className="eyebrow"><span className="eyebrow-dot"/>MAALENEX / {page.toUpperCase()}</p><h1>{page==="dashboard"?t.welcome:title}</h1><p>{page==="dashboard"?t.subtitle:""}</p></div><span className="mode-pill">{t.demo}</span></div>
    {notice&&<p className="notice-panel" role="status">{notice}</p>}
    {page==="dashboard"&&<>
      <section className="dashboard-hero"><div><span className="hero-kicker">{language==="am"?"የጉዞ ማዕከል":"MOBILITY COMMAND CENTER"}</span><h2>{language==="am"?"ቀጣይ ጉዞዎ ከዚህ ይጀምራል":"Your next journey starts here."}</h2><p>{language==="am"?"የጉዞ መረጃ፣ ካርታ እና ድጋፍ በቀላሉ ያግኙ።":"Discover journey information, maps and passenger support."}</p><button className="primary-action" onClick={()=>go("map")}>{language==="am"?"ካርታውን ይመልከቱ":"Explore map"}<Icon name="arrow"/></button></div><div className="hero-emblem"><img src="./brand/maalenex-nexus-emblem.svg" alt=""/></div></section>
      <section className="stat-grid"><button type="button" className="stat-card stat-action" onClick={()=>go("wallet")}><span>{t.balance}</span><strong>— ETB</strong><small>{t.noFunds} · {language==="am"?"ዝርዝር ይመልከቱ":"Open wallet"}</small></button><button type="button" className="stat-card stat-action" onClick={()=>go("map")}><span>{t.journeys}</span><strong>0</strong><small>{t.empty} · {language==="am"?"ጉዞ ይፈልጉ":"Explore journeys"}</small></button><button type="button" className="stat-card stat-action" onClick={()=>go("profile")}><span>{language==="am"?"የመለያ ሁኔታ":"Account status"}</span><strong>{language==="am"?"እንግዳ":"Guest"}</strong><small>{t.noLogin} · {language==="am"?"መገለጫ":"Open profile"}</small></button></section>
      <section className="content-section"><div className="section-heading"><div><span className="section-kicker">DISCOVER</span><h2>{t.quick}</h2></div></div><div className="service-grid">
       <Tile title={t.map} detail={language==="am"?"አካባቢያዊ ካርታ እና ፍለጋ":"Explore locations"} icon="map" onClick={()=>go("map")}/>
       <Tile title={t.wallet} detail={language==="am"?"ቀሪ ሂሳብ እና ግብይቶች":"Balance and transactions"} icon="wallet" onClick={()=>go("wallet")}/>
       <Tile title={t.profile} detail={language==="am"?"የግል ቅንብሮች":"Personal settings"} icon="profile" onClick={()=>go("profile")}/>
       <Tile title={t.help} detail={language==="am"?"መመሪያ እና ድጋፍ":"Guides and support"} icon="help" onClick={()=>go("help")}/>
      </div></section>
      <section className="journey-panel"><div><span className="section-kicker">LIVE INFORMATION</span><h2>{t.journeys}</h2><p>{t.empty}</p></div><span className="empty-orbit"><Icon name="route"/></span></section>
    </>}
    {page==="map"&&<section className="content-section"><div className="map-toolbar"><input aria-label={t.search} placeholder={t.search}/><button className="primary-action" onClick={()=>setNotice(t.coming)}>{language==="am"?"ፈልግ":"Search"}<Icon name="arrow"/></button></div><div className="map-canvas"><div className="map-grid-lines"/><div className="map-waterway"/><span className="map-pin pin-one">Koybe</span><span className="map-pin pin-two">Jinka</span><div className="map-center-mark"><img src="./brand/maalenex-nexus-emblem.svg" alt=""/></div><div className="map-legend"><strong>{language==="am"?"የካርታ ቅድመ እይታ":"Map preview"}</strong><span>{t.mapNote}</span></div></div><p className="muted-copy">{t.mapNote}</p></section>}
    {page==="wallet"&&<section className="content-section wallet-view"><article className="wallet-card"><span>{t.balance}</span><strong>— <small>ETB</small></strong><span className="wallet-badge">{t.demo}</span><p>{t.noFunds}</p></article><div className="wallet-actions"><button onClick={()=>setNotice(t.coming)}><Icon name="plus"/> {language==="am"?"ገንዘብ ጨምር":"Add funds"}</button><button onClick={()=>setNotice(t.coming)}><Icon name="arrow"/> {language==="am"?"ገንዘብ አውጣ":"Withdraw"}</button><button onClick={()=>setNotice(t.coming)}><Icon name="receipt"/> {language==="am"?"ደረሰኞች":"Receipts"}</button></div><div className="panel-card"><h2>{language==="am"?"የግብይት ታሪክ":"Transaction history"}</h2><p>{language==="am"?"ገና ምንም ግብይት የለም።":"No transactions yet."}</p></div><p className="compliance-note">{t.coming}</p></section>}
    {page==="profile"&&<section className="content-section"><div className="panel-card profile-panel"><span className="large-avatar">{profileName.trim()?profileName.trim().charAt(0).toUpperCase():"M"}</span><h2>{profileName||(passenger?(language==="am"?"ተሳፋሪ":"Passenger"):(language==="am"?"የእንግዳ መገለጫ":"Guest profile"))}</h2><p>{passenger?.login_identifier||profilePhone||t.noLogin}</p><div className="form-actions"><button className="primary-action" onClick={()=>{setProfileEditing(!profileEditing);setProfileSaved(false);}}>{profileEditing?(language==="am"?"ዝጋ":"Close"):(language==="am"?"መገለጫ አርትዕ":"Edit profile")}<Icon name="arrow"/></button>{!passenger&&<button className="secondary-action" onClick={()=>go("login")}>{t.login}</button>}</div></div>{profileEditing&&<form className="form-card" onSubmit={saveProfile}><h2>{language==="am"?"የመገለጫ መረጃ":"Edit profile"}</h2><label>{t.name}<input value={profileName} onChange={e=>setProfileName(e.target.value)} required minLength={2} maxLength={120} autoComplete="name"/></label><label>{t.phone}<input value={profilePhone} onChange={e=>setProfilePhone(e.target.value)} inputMode="tel" autoComplete="tel" disabled={Boolean(passenger)}/></label><label>{t.email}<input type="email" value={profileEmail} onChange={e=>setProfileEmail(e.target.value)} autoComplete="email" disabled={Boolean(passenger)}/></label><p className="field-hint">{passenger?(language==="am"?"የሙሉ ስም ለውጥ ወደ መለያዎ ይቀመጣል።":"Your display name is saved to your passenger account. Contact changes require verification."):(language==="am"?"ይህ የእንግዳ ማሳያ ነው፤ ለማስቀመጥ ይግቡ።":"Guest profile edits are preview-only until you sign in.")}</p><button className="primary-action" type="submit">{language==="am"?"አስቀምጥ":"Save profile"}</button></form>}<div className="panel-card settings-list"><h2>{t.account}</h2><button onClick={()=>setLanguage(language==="am"?"en":"am")}>{t.language}<span>{language==="am"?"አማርኛ":"English"}</span></button><button onClick={()=>setNotice(t.coming)}>{t.notifications}<span>›</span></button><button onClick={()=>go("forgot")}>{language==="am"?"የይለፍ ቃል መቀየር":"Password and security"}<span>›</span></button><button onClick={()=>go("help")}>{t.help}<span>›</span></button>{passenger&&<button onClick={signOut}>{t.signout}<span>↗</span></button>}</div>{profileSaved&&<p className="notice-panel" role="status">{language==="am"?"መገለጫው ተዘምኗል":"Profile updated"}</p>}</section>}{(page==="login"||page==="register"||page==="forgot")&&<section className="content-section"><form className="form-card" onSubmit={submitAuth} aria-busy={authBusy}><h2>{page==="login"?t.login:page==="register"?t.register:(language==="am"?"የይለፍ ቃል መመለስ":"Recover password")}</h2>{page==="register"&&<label>{t.name}<input required minLength={2} maxLength={120} autoComplete="name" value={authName} onChange={e=>setAuthName(e.target.value)} placeholder={language==="am"?"ሙሉ ስም":"Enter your full name"}/></label>}{page!=="forgot"&&<label>{language==="am"?"ኢሜይል ወይም ዓለም አቀፍ ስልክ ቁጥር":"Email or international phone number"}<input required minLength={5} maxLength={254} autoComplete="username" value={authIdentifier} onChange={e=>setAuthIdentifier(e.target.value)} placeholder="+2519… or name@example.com"/></label>}{page!=="forgot"&&<label>{t.password}<div className="password-field"><input required minLength={page==="register"?12:1} maxLength={128} type={passwordVisible?"text":"password"} value={authPassword} onChange={e=>setAuthPassword(e.target.value)} autoComplete={page==="login"?"current-password":"new-password"}/><button type="button" className="secondary-action" aria-label={passwordVisible?(language==="am"?"ደብቅ":"Hide password"):(language==="am"?"አሳይ":"Show password")} onClick={()=>setPasswordVisible(!passwordVisible)}>{passwordVisible?(language==="am"?"ደብቅ":"Hide"):(language==="am"?"አሳይ":"Show")}</button></div></label>}{page==="register"&&<><label>{language==="am"?"የይለፍ ቃል ድገም":"Confirm password"}<input required minLength={12} maxLength={128} type={passwordVisible?"text":"password"} value={authConfirmPassword} onChange={e=>setAuthConfirmPassword(e.target.value)} autoComplete="new-password"/></label><label className="consent-row"><input type="checkbox" required/><span>{language==="am"?"የአጠቃቀም ውሎችን እና የግላዊነት መመሪያን ተቀብያለሁ":"I agree to the Terms of Use and Privacy Notice."}</span></label></>}{page==="forgot"&&<><label>{language==="am"?"ኢሜይል ወይም ስልክ ቁጥር":"Email or phone number"}<input required minLength={5} maxLength={254} value={authIdentifier} onChange={e=>setAuthIdentifier(e.target.value)}/></label><p className="field-hint">{language==="am"?"የመለያ መመለሻ ማድረሻ አገልግሎት ገና አልተገናኘም።":"Password recovery delivery is not configured yet. No reset email or SMS will be sent."}</p></>}{page!=="forgot"&&<p className="field-hint">{page==="register"?(language==="am"?"የምዝገባ እና የግባ አገልግሎት ከመለያ ሰርቨር ጋር ይገናኛል።":"Your account will be created by the passenger account service. Contact verification is not yet configured."):(language==="am"?"የተሳፋሪ መለያዎን ይጠቀሙ።":"Sign in with your passenger account credentials.")}</p>}<button className="primary-action" type="submit" disabled={authBusy}>{authBusy?(language==="am"?"በመጫን ላይ…":"Working…"):page==="forgot"?(language==="am"?"መመለሻ ጀምር":"Start recovery"):t.submit}<Icon name="arrow"/></button>{page==="login"&&<button type="button" className="text-link" onClick={()=>go("forgot")}>{language==="am"?"የይለፍ ቃል ረሳሁ":"Forgot password?"}</button>}<button type="button" className="text-link" onClick={()=>{setAuthPassword("");setAuthConfirmPassword("");go(page==="login"?"register":"login");}}>{page==="login"?t.register:t.login}</button></form></section>}{page==="help"&&<section className="content-section"><div className="panel-card"><h2>{t.support}</h2>{["Account and access","Wallet and payments","Journey information","Safety and privacy"].map(x=><button className="help-row" key={x} onClick={()=>setNotice(t.coming)}><Icon name="help"/><span>{x}</span><Icon name="arrow"/></button>)}</div></section>}
    {page==="report"&&<section className="content-section"><form className="form-card" onSubmit={e=>{e.preventDefault();setNotice(t.sent);setReport("");}}><h2>{t.reportTitle}</h2><label>{language==="am"?"የሪፖርት አይነት":"Report category"}<select><option>App issue</option><option>Journey information</option><option>Wallet</option><option>Safety</option></select></label><label>{t.message}<textarea required value={report} onChange={e=>setReport(e.target.value)} rows={5}/></label><button className="primary-action" type="submit">{t.send}<Icon name="arrow"/></button></form></section>}
    {page==="about"&&<section className="content-section"><div className="panel-card"><h2>MaaleNex</h2><p>{language==="am"?"በኢትዮጵያ ውስጥ የተሳፋሪ ተሞክሮን ለማሻሻል የሚገነባ የመጓጓዣ ቴክኖሎጂ መድረክ።":"Mobility technology designed to improve the passenger experience in Ethiopia."}</p></div></section>}
    <footer className="platform-footer"><span>© MaaleNex</span><span>{language==="am"?"በአካባቢያዊ ግንዛቤ የተመራ":"Built with local understanding"}</span><span>{t.demo}</span></footer>
   </main>
  </div>
 </div>;
}
