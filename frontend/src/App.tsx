import { useEffect, useState, type FormEvent } from "react";
import {
  getCurrentPassenger,
  loginPassenger,
  logoutPassenger,
  registerPassenger,
  updatePassengerProfile,
  type PassengerSession,
  listPassengerLocations,
  listPassengerRoutes,
  searchPassengerTrips,
  type PassengerLocation,
  type PassengerRoute,
  type PassengerTrip,
  listPassengerSupportFaqs,
  listPassengerSupportCases,
  createPassengerSupportCase,
  type PassengerSupportFaq,
  type PassengerSupportCase,
  listPassengerReports,
  createPassengerReport,
  uploadPassengerReportAttachment,
  type PassengerReport,
  passengerReportAttachmentUrl,
  getPassengerWallet,
  type PassengerWallet,
  getPassengerNotifications,
  markPassengerNotificationRead,
  markAllPassengerNotificationsRead,
  getPassengerNotificationPreferences,
  updatePassengerNotificationPreferences,
  type PassengerNotificationPreferences,
  type PassengerNotification,
} from "./passenger-api";
import { BookingFlow } from "./BookingFlow";
import { PassengerGoogleMap } from "./PassengerGoogleMap";
import { MyBookings } from "./MyBookings";
import { StaffConsole } from "./StaffConsole";
import { Icon } from "./components/nexus-icons";

type Language = "am" | "en";
type Page = "dashboard" | "map" | "wallet" | "bookings" | "notifications" | "profile" | "help" | "report" | "login" | "register" | "forgot" | "about" | "staff";
const labels = {
  am: { dashboard:"ዳሽቦርድ", map:"ካርታ", wallet:"ቦርሳ", profile:"መገለጫ", help:"እገዛ", report:"ሪፖርት", login:"ግባ", register:"መለያ ፍጠር", about:"ስለ እኛ", welcome:"ወደ MaaleNex እንኳን በደህና መጡ", subtitle:"የጉዞዎን ቀጣይ እርምጃ በአንድ ቦታ ያቀናብሩ።", search:"መነሻ ወይም መድረሻ ይፈልጉ", quick:"ፈጣን አገልግሎቶች", journeys:"የጉዞ መረጃ", empty:"የተረጋገጠ የጉዞ መረጃ ሲገኝ እዚህ ይታያል።", balance:"የቦርሳ ቀሪ ሂሳብ", demo:"የማሳያ ሁኔታ", noFunds:"የእውነተኛ ገንዘብ ግብይት አልነቃም።", mapNote:"ካርታው የታተመና የተረጋገጠ የመስመር ጂኦሜትሪ ብቻ ያሳያል።", name:"ሙሉ ስም", phone:"ስልክ ቁጥር", password:"የይለፍ ቃል", email:"ኢሜይል", submit:"ቀጥል", coming:"ይህ ባህሪ ከደህንነት እና ከአገልግሎት ማገናኛ ማረጋገጫ በኋላ ይነቃል።", support:"እንዴት ልንርዳዎ?", reportTitle:"ችግር ሪፖርት ያድርጉ", message:"መልዕክትዎ", send:"ሪፖርት ላክ", sent:"የማሳያ ሪፖርት ተመዝግቧል። አሁንም ወደ ድጋፍ ሰርቨር አልተላከም።", account:"መለያዎን ያስተዳድሩ", language:"ቋንቋ", notifications:"ማሳወቂያዎች", bookings:"ማስያዣዎች", staff:"የሰራተኛ ማዕከል", signout:"ውጣ", noLogin:"አሁን የማሳያ ሁኔታ ብቻ ነው።" },
  en: { dashboard:"Dashboard", map:"Map", wallet:"Wallet", profile:"Profile", help:"Help", report:"Report", login:"Log in", register:"Create account", about:"About", welcome:"Welcome to MaaleNex", subtitle:"Your mobility tools, information and support in one place.", search:"Search origin or destination", quick:"Quick access", journeys:"Journey information", empty:"Verified journey information will appear here when published.", balance:"Wallet balance", demo:"DEMO MODE", noFunds:"Real-money transactions are not enabled.", mapNote:"The map draws only published, verified route geometry; it never infers a route from endpoints.", name:"Full name", phone:"Phone number", password:"Password", email:"Email", submit:"Continue", coming:"This capability will activate after security and service-provider verification.", support:"How can we help?", reportTitle:"Report an issue", message:"Your message", send:"Submit report", sent:"Demo report captured locally. It has not been sent to a support server.", account:"Manage your account", language:"Language", notifications:"Notifications", bookings:"My Bookings", staff:"Staff workspace", signout:"Sign out", noLogin:"This is currently a demonstration session only." }
} as const;

type NavPage = Exclude<Page, "login" | "register" | "forgot" | "about">;
const nav: NavPage[] = ["dashboard","map","wallet","bookings","notifications","staff","profile","help","report"];
const iconFor: Record<Page, "home"|"map"|"wallet"|"user"|"help"|"flag"|"compass"|"globe"|"shield"|"route"|"arrow"|"bell"> = {
 dashboard:"home", map:"map", wallet:"wallet", bookings:"route", notifications:"bell", staff:"shield", profile:"user", help:"help", report:"flag", login:"user", register:"user", forgot:"shield", about:"compass"
};

function Tile({title,detail,onClick,icon}:{title:string;detail:string;onClick:()=>void;icon:Page}) {
 return <button className="service-tile" onClick={onClick}><span className="tile-icon"><Icon name={iconFor[icon]}/></span><span><strong>{title}</strong><small>{detail}</small></span><Icon name="arrow"/></button>;
}

export default function App() {
 const [language,setLanguage]=useState<Language>("am");
 const [page,setPage]=useState<Page>("dashboard");
 const [notice,setNotice]=useState("");
 const [report,setReport]=useState("");
 const [reportType,setReportType]=useState<PassengerReport["report_type"]>("report");
 const [reportCategory,setReportCategory]=useState<PassengerReport["category"]>("app_issue");
 const [reportSeverity,setReportSeverity]=useState<PassengerReport["severity"]>("normal");
 const [reportSubject,setReportSubject]=useState("");
 const [reportAttachments,setReportAttachments]=useState<File[]>([]);
 const [reportCases,setReportCases]=useState<PassengerReport[]>([]);
 const [reportLoading,setReportLoading]=useState(false);
 const [reportSubmitting,setReportSubmitting]=useState(false);
 const [reportError,setReportError]=useState("");
 const [supportFaqs,setSupportFaqs]=useState<PassengerSupportFaq[]>([]);
 const [supportCases,setSupportCases]=useState<PassengerSupportCase[]>([]);
 const [supportCategory,setSupportCategory]=useState<PassengerSupportCase["category"]>("general");
 const [supportSubject,setSupportSubject]=useState("");
 const [supportMessage,setSupportMessage]=useState("");
 const [supportLoading,setSupportLoading]=useState(false);
 const [supportSubmitting,setSupportSubmitting]=useState(false);
 const [supportError,setSupportError]=useState("");
 const [passwordVisible,setPasswordVisible]=useState(false);
 const [profileEditing,setProfileEditing]=useState(false);
 const [profileName,setProfileName]=useState("");
 const [profilePhone,setProfilePhone]=useState("");
 const [profileEmail,setProfileEmail]=useState("");
 const [profileSaved,setProfileSaved]=useState(false);
 const [isOnline,setIsOnline]=useState(true);
 const [passenger,setPassenger]=useState<PassengerSession|null>(null);
 const [walletData,setWalletData]=useState<PassengerWallet|null>(null);
 const [walletLoading,setWalletLoading]=useState(false);
 const [walletError,setWalletError]=useState("");
 const [notificationItems,setNotificationItems]=useState<PassengerNotification[]>([]);
 const [notificationUnread,setNotificationUnread]=useState(0);
 const [notificationLoading,setNotificationLoading]=useState(false);
 const [notificationError,setNotificationError]=useState("");
 const [notificationFilter,setNotificationFilter]=useState("all");
 const [notificationPreferences,setNotificationPreferences]=useState<PassengerNotificationPreferences|null>(null);
 const [notificationPreferenceBusy,setNotificationPreferenceBusy]=useState(false);
 const [authIdentifier,setAuthIdentifier]=useState("");
 const [authName,setAuthName]=useState("");
 const [authPassword,setAuthPassword]=useState("");
 const [authConfirmPassword,setAuthConfirmPassword]=useState("");
 const [authBusy,setAuthBusy]=useState(false);
 const [locations,setLocations]=useState<PassengerLocation[]>([]);
 const [routes,setRoutes]=useState<PassengerRoute[]>([]);
 const [mapPickTarget,setMapPickTarget]=useState<"origin"|"destination">("origin");
 const [originId,setOriginId]=useState("");
 const [destinationId,setDestinationId]=useState("");
 const [travelDate,setTravelDate]=useState(()=>{const now=new Date();return new Date(now.getTime()-now.getTimezoneOffset()*60000).toISOString().slice(0,10);});
 const [passengerCount,setPassengerCount]=useState(1);
 const [tripResults,setTripResults]=useState<PassengerTrip[]>([]);
 const [tripLoading,setTripLoading]=useState(false);
 const [tripError,setTripError]=useState("");
 const [selectedTrip,setSelectedTrip]=useState<PassengerTrip|null>(null);
 const todayLocal=(()=>{const now=new Date();return new Date(now.getTime()-now.getTimezoneOffset()*60000).toISOString().slice(0,10);})();
 const t=labels[language];
 useEffect(()=>{document.documentElement.lang=language;},[language]);

 useEffect(()=>{
  if(page!=="notifications")return;
  if(!passenger){setNotificationItems([]);setNotificationUnread(0);setNotificationError("");return;}
  let active=true;
  setNotificationLoading(true);setNotificationError("");
  Promise.all([getPassengerNotifications(),getPassengerNotificationPreferences().catch(()=>({in_app_enabled:true,email_enabled:false,sms_enabled:false,email_delivery_available:false,sms_delivery_available:false}))]).then(([result,prefs])=>{
   if(active){setNotificationItems(result.items);setNotificationUnread(result.unread_count);setNotificationPreferences(prefs);}
  }).catch(error=>{
   if(active)setNotificationError(error instanceof Error?error.message:"Unable to load notifications.");
  }).finally(()=>{if(active)setNotificationLoading(false);});
  return()=>{active=false;};
 },[page,passenger]);
 const markAllRead=async()=>{try{await markAllPassengerNotificationsRead();setNotificationItems(current=>current.map(item=>({...item,read:true})));setNotificationUnread(0);}catch(error){setNotificationError(error instanceof Error?error.message:"Unable to update notifications.");}};
 const toggleInAppNotifications=async()=>{if(!notificationPreferences)return;setNotificationPreferenceBusy(true);try{const updated=await updatePassengerNotificationPreferences(!notificationPreferences.in_app_enabled);setNotificationPreferences(updated);}catch(error){setNotificationError(error instanceof Error?error.message:"Unable to update preferences.");}finally{setNotificationPreferenceBusy(false);}};
 const markRead=async(item:PassengerNotification)=>{
  if(item.read)return;
  try{
   const updated=await markPassengerNotificationRead(item.id);
   setNotificationItems(current=>current.map(row=>row.id===updated.id?updated:row));
   setNotificationUnread(current=>Math.max(0,current-1));
  }catch(error){setNotificationError(error instanceof Error?error.message:"Unable to update notification.");}
 };


 useEffect(()=>{
  if(page!=="wallet")return;
  if(!passenger){setWalletData(null);setWalletError("");setWalletLoading(false);return;}
  let active=true;
  setWalletLoading(true);setWalletError("");
  getPassengerWallet().then(result=>{if(active)setWalletData(result);})
   .catch(error=>{if(active)setWalletError(error instanceof Error?error.message:"Unable to load the wallet ledger.");})
   .finally(()=>{if(active)setWalletLoading(false);});
  return()=>{active=false;};
 },[page,passenger]);

 useEffect(()=>{
  if(page!=="map")return;
  let active=true;
  Promise.all([listPassengerLocations(),listPassengerRoutes()]).then(([items,routeItems])=>{
   if(!active)return;
   setLocations(items);setRoutes(routeItems);
   setOriginId(current=>current||items[0]?.id||"");
   setDestinationId(current=>current||items.find(item=>item.id!==items[0]?.id)?.id||"");
  }).catch(error=>{if(active)setTripError(error instanceof Error?error.message:"Unable to load published locations and routes.");});
  return()=>{active=false;};
 },[page]);
 useEffect(()=>{
  if(page!=="help")return;
  let active=true;
  setSupportLoading(true);setSupportError("");
  Promise.all([
   listPassengerSupportFaqs(language),
   passenger?listPassengerSupportCases():Promise.resolve([] as PassengerSupportCase[]),
  ]).then(([faqResponse,cases])=>{
   if(!active)return;
   setSupportFaqs(faqResponse.items);setSupportCases(cases);
  }).catch(error=>{
   if(active)setSupportError(error instanceof Error?error.message:"Unable to load Help and Support.");
  }).finally(()=>{if(active)setSupportLoading(false);});
  return()=>{active=false;};
 },[page,language,passenger]);
 useEffect(()=>{
  if(page!=="report"||!passenger)return;
  let active=true;
  setReportLoading(true);setReportError("");
  listPassengerReports().then(result=>{if(active)setReportCases(result.items);})
   .catch(error=>{if(active)setReportError(error instanceof Error?error.message:"Unable to load reports and complaints.");})
   .finally(()=>{if(active)setReportLoading(false);});
  return()=>{active=false;};
 },[page,passenger]);
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
 const submitAuth=async(e:FormEvent<HTMLFormElement>)=>{
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
 const submitTripSearch=async(e:FormEvent<HTMLFormElement>)=>{
  e.preventDefault();setTripError("");setTripResults([]);
  if(!originId||!destinationId||originId===destinationId){setTripError(language==="am"?"የተለያዩ መነሻ እና መድረሻ ይምረጡ።":"Choose different origin and destination locations.");return;}
  if(!navigator.onLine){setTripError(language==="am"?"የኢንተርኔት ግንኙነት የለም። ጉዞ ለመፈለግ ግንኙነት ያስፈልጋል።":"You are offline. Reconnect to search current trips.");return;}
  setTripLoading(true);
  try{const results=await searchPassengerTrips({origin_id:originId,destination_id:destinationId,travel_date:travelDate,passenger_count:passengerCount});setTripResults(results);}
  catch(error){setTripError(error instanceof Error?error.message:"Journey search is temporarily unavailable.");}
  finally{setTripLoading(false);}
 };
 const submitReport=async(e:FormEvent<HTMLFormElement>)=>{
  e.preventDefault();
  if(!passenger){go("login");setNotice(language==="am"?"ሪፖርት ወይም ቅሬታ ለመላክ መለያዎን ይግቡ።":"Sign in to submit a report or complaint.");return;}
  setReportSubmitting(true);setReportError("");setNotice("");
  let created:PassengerReport|undefined;
  try{
   created=await createPassengerReport({
    report_type:reportType,category:reportCategory,severity:reportSeverity,
    subject:reportSubject.trim(),description:report.trim(),
   });
   setReportCases(current=>[created!,...current]);
   if(reportAttachments.length){
    const uploaded=[];
    const failures=[];
    for(const file of reportAttachments){
     try{uploaded.push(await uploadPassengerReportAttachment(created.report_reference,file));}
     catch(error){failures.push(error instanceof Error?error.message:"Evidence upload failed.");}
    }
    created={...created,attachments:[...created.attachments,...uploaded]};
    setReportCases(current=>current.map(item=>item.report_reference===created!.report_reference?created!:item));
    if(failures.length){
     setReportError((language==="am"?"ሪፖርቱ ተመዝግቧል፤ አንዳንድ ማስረጃዎች አልተጫኑም። ":"The report was saved, but one or more evidence uploads failed. ")+created.report_reference+" · "+failures.join("; "));
    }else{
     setNotice(language==="am"?"ሪፖርትዎ ከማስረጃ ፋይሎች ጋር ተልኳል። ማጣቀሻ: "+created.report_reference:"Report submitted with evidence. Reference: "+created.report_reference);
    }
   }else{
    setNotice(language==="am"?"ሪፖርትዎ ተልኳል። ማጣቀሻ: "+created.report_reference:"Report submitted. Reference: "+created.report_reference);
   }
   setReport("");setReportSubject("");setReportAttachments([]);
   const fileInput=document.getElementById("report-evidence") as HTMLInputElement|null;
   if(fileInput)fileInput.value="";
  }catch(error){setReportError(error instanceof Error?error.message:"Report or complaint could not be submitted.");}
  finally{setReportSubmitting(false);}
 };
 const submitSupportCase=async(e:FormEvent<HTMLFormElement>)=>{
  e.preventDefault();
  if(!passenger){go("login");setNotice(language==="am"?"የድጋፍ ጥያቄ ለመላክ መለያዎን ይግቡ።":"Sign in to submit a support request.");return;}
  setSupportSubmitting(true);setSupportError("");setNotice("");
  try{
   const created=await createPassengerSupportCase({category:supportCategory,subject:supportSubject.trim(),message:supportMessage.trim()});
   setSupportCases(current=>[created,...current]);
   setSupportSubject("");setSupportMessage("");
   setNotice(language==="am"?"የድጋፍ ጥያቄዎ ተልኳል። ማጣቀሻ: "+created.case_reference:"Support request submitted. Reference: "+created.case_reference);
  }catch(error){setSupportError(error instanceof Error?error.message:"Support request could not be submitted.");}
  finally{setSupportSubmitting(false);}
 };
 const formatTripTime=(value:string)=>new Intl.DateTimeFormat(language==="am"?"am-ET":"en-ET",{dateStyle:"medium",timeStyle:"short",timeZone:"Africa/Addis_Ababa"}).format(new Date(value));
 const formatTripFare=(minor:number,currency:string)=>new Intl.NumberFormat(language==="am"?"am-ET":"en-ET",{style:"currency",currency}).format(minor/100);
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
   <div className="header-context"><span className={isOnline?"online-dot":"online-dot offline-dot"}/><span>{!isOnline?(language==="am"?"ከመስመር ውጭ":"Offline"):page==="staff"?(language==="am"?"የሰራተኛ ማዕከል":"Staff workspace"):(language==="am"?"የተጠቃሚ ማዕከል":"Passenger hub")}</span></div>
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

    {page==="staff"&&<StaffConsole language={language}/>}
    {page==="notifications"&&<section className="content-section">
     <div className="panel-card notification-panel">
      <div className="notification-heading"><div><h2>{language==="am"?"ማሳወቂያዎች":"Notifications"}</h2><p>{language==="am"?"ያልተነበቡ ":""}{notificationUnread}{language==="am"?"":" unread"}</p></div><Icon name="bell"/></div>
      {!passenger&&<p className="notice-panel">{language==="am"?"ማሳወቂያዎችን ለማየት ይግቡ።":"Sign in to view your notifications."} <button className="text-link" onClick={()=>go("login")}>{t.login}</button></p>}
      {passenger&&<div className="notification-controls"><div className="booking-filters">{["all","unread","booking","security","support"].map(value=><button key={value} className={notificationFilter===value?"filter-active":"secondary-action"} onClick={()=>setNotificationFilter(value)}>{value==="all"?(language==="am"?"ሁሉም":"All"):value==="unread"?(language==="am"?"ያልተነበቡ":"Unread"):value==="booking"?(language==="am"?"ማስያዣ":"Bookings"):value==="security"?(language==="am"?"ደህንነት":"Security"):(language==="am"?"ድጋፍ":"Support")}</button>)}</div><div className="notification-actions"><button className="text-link" disabled={notificationUnread===0} onClick={()=>void markAllRead()}>{language==="am"?"ሁሉንም ተነብበዋል ብለው ምልክት":"Mark all read"}</button><label className="notification-toggle"><input type="checkbox" checked={notificationPreferences?.in_app_enabled??true} disabled={notificationPreferenceBusy} onChange={()=>void toggleInAppNotifications()}/><span>{language==="am"?"የውስጥ ማሳወቂያዎች":"In-app alerts"}</span></label></div></div>}
      {notificationLoading&&<p role="status">{language==="am"?"በመጫን ላይ…":"Loading notifications…"}</p>}
      {notificationError&&<p role="alert" className="support-error">{notificationError}</p>}
      {passenger&&!notificationLoading&&notificationItems.length===0&&<p>{language==="am"?"አዲስ ማሳወቂያ የለም።":"You have no notifications yet."}</p>}
      {notificationItems.filter(item=>notificationFilter==="all"||(notificationFilter==="unread"&&!item.read)||(notificationFilter==="booking"&&item.notification_type.startsWith("booking"))||(notificationFilter==="security"&&item.notification_type.includes("security"))||(notificationFilter==="support"&&(item.notification_type.includes("support")||item.notification_type.includes("report")))).map(item=><article className={item.read?"notification-item":"notification-item unread"} key={item.id}>
       <div><span className={"notification-priority priority-"+(item.notification_type.includes("security")?"high":"normal")}>{item.notification_type.replaceAll("_"," ")}</span><strong>{item.title}</strong><p>{item.body}</p><small>{new Date(item.created_at).toLocaleString(language==="am"?"am-ET":"en-ET")}{item.resource_reference?" · "+item.resource_reference:""}</small></div>
       <div className="notification-actions">{item.resource_type==="booking"&&<button className="text-link" onClick={()=>go("bookings")}>{language==="am"?"ማስያዣ ክፈት":"Open booking"}</button>}{!item.read&&<button className="secondary-action" onClick={()=>markRead(item)}>{language==="am"?"ተነብቧል":"Mark read"}</button>}</div>
      </article>)}
      {passenger&&notificationPreferences&&<p className="field-hint">{language==="am"?"ኢሜይልና SMS ማድረሻ ገና አልነቁም፤ የውስጥ ማሳወቂያ ብቻ ይገኛል።":"Email and SMS delivery remain disabled until provider, consent and security reviews are complete."}</p>}
     </div>
    </section>}
    {page==="dashboard"&&<>
      <section className="dashboard-hero"><div><span className="hero-kicker">{language==="am"?"የጉዞ ማዕከል":"MOBILITY COMMAND CENTER"}</span><h2>{language==="am"?"ቀጣይ ጉዞዎ ከዚህ ይጀምራል":"Your next journey starts here."}</h2><p>{language==="am"?"የጉዞ መረጃ፣ ካርታ እና ድጋፍ በቀላሉ ያግኙ።":"Discover journey information, maps and passenger support."}</p><button className="primary-action" onClick={()=>go("map")}>{language==="am"?"ካርታውን ይመልከቱ":"Explore map"}<Icon name="arrow"/></button></div><div className="hero-emblem"><img src="./brand/maalenex-nexus-emblem.svg" alt=""/></div></section>
      <section className="stat-grid"><button type="button" className="stat-card stat-action" onClick={()=>go("wallet")}><span>{t.balance}</span><strong>— ETB</strong><small>{t.noFunds} · {language==="am"?"ዝርዝር ይመልከቱ":"Open wallet"}</small></button><button type="button" className="stat-card stat-action" onClick={()=>go("map")}><span>{t.journeys}</span><strong>0</strong><small>{t.empty} · {language==="am"?"ጉዞ ይፈልጉ":"Explore journeys"}</small></button><button type="button" className="stat-card stat-action" onClick={()=>go("profile")}><span>{language==="am"?"የመለያ ሁኔታ":"Account status"}</span><strong>{language==="am"?"እንግዳ":"Guest"}</strong><small>{t.noLogin} · {language==="am"?"መገለጫ":"Open profile"}</small></button></section>
      <section className="content-section"><div className="section-heading"><div><span className="section-kicker">DISCOVER</span><h2>{t.quick}</h2></div></div><div className="service-grid">
       <Tile title={language==="am"?"ማስያዣዎቼ":"My Bookings"} detail={language==="am"?"የተገናኙ ማስያዣዎችን ያስተዳድሩ":"View and manage linked bookings"} icon="bookings" onClick={()=>go("bookings")}/>
       <Tile title={t.map} detail={language==="am"?"አካባቢያዊ ካርታ እና ፍለጋ":"Explore locations"} icon="map" onClick={()=>go("map")}/>
       <Tile title={t.wallet} detail={language==="am"?"ቀሪ ሂሳብ እና ግብይቶች":"Balance and transactions"} icon="wallet" onClick={()=>go("wallet")}/>
       <Tile title={t.profile} detail={language==="am"?"የግል ቅንብሮች":"Personal settings"} icon="profile" onClick={()=>go("profile")}/>
       <Tile title={t.help} detail={language==="am"?"መመሪያ እና ድጋፍ":"Guides and support"} icon="help" onClick={()=>go("help")}/>
      </div></section>
      <section className="journey-panel"><div><span className="section-kicker">LIVE INFORMATION</span><h2>{t.journeys}</h2><p>{t.empty}</p></div><span className="empty-orbit"><Icon name="route"/></span></section>
    </>}
    {page==="map" && (
      <section className="content-section">
        <form className="form-card journey-search-form" onSubmit={submitTripSearch}>
          <h2>{language==="am" ? "የጉዞ ፍለጋ" : "Find a journey"}</h2>
          <label>
            {language==="am" ? "መነሻ ቦታ" : "Origin"}
            <select required value={originId} onChange={e=>setOriginId(e.target.value)}>
              <option value="">{language==="am" ? "መነሻ ይምረጡ" : "Choose origin"}</option>
              {locations.map(item=><option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
          </label>
          <label>
            {language==="am" ? "መድረሻ ቦታ" : "Destination"}
            <select required value={destinationId} onChange={e=>setDestinationId(e.target.value)}>
              <option value="">{language==="am" ? "መድረሻ ይምረጡ" : "Choose destination"}</option>
              {locations.filter(item=>item.id!==originId).map(item=><option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
          </label>
          <div className="journey-search-fields">
            <label>
              {language==="am" ? "የጉዞ ቀን" : "Travel date"}
              <input type="date" required min={todayLocal} value={travelDate} onChange={e=>setTravelDate(e.target.value)} />
            </label>
            <label>
              {language==="am" ? "ተሳፋሪዎች" : "Passengers"}
              <select value={passengerCount} onChange={e=>setPassengerCount(Number(e.target.value))}>
                {Array.from({length:10},(_,i)=>i+1).map(n=><option key={n} value={n}>{n}</option>)}
              </select>
            </label>
          </div>
          <button className="primary-action" type="submit" disabled={tripLoading||locations.length<2}>
            {tripLoading ? (language==="am" ? "በመፈለግ ላይ…" : "Searching…") : (language==="am" ? "ጉዞ ፈልግ" : "Search journeys")}
            <Icon name="arrow"/>
          </button>
          <p className="field-hint">{language==="am" ? "የታተሙ መስመሮችና ጉዞዎች ብቻ ይታያሉ።" : "Only published routes and trips with current ETB fares are shown."}</p>
        </form>
        {tripError && <p className="notice-panel" role="alert">{tripError}</p>}
        {selectedTrip && <BookingFlow trip={selectedTrip} passengerCount={passengerCount} language={language} onClose={()=>setSelectedTrip(null)} />}
        {tripResults.length>0 && (
          <div className="trip-results">
            <div className="section-heading">
              <h2>{language==="am" ? "የተገኙ ጉዞዎች" : "Available journeys"} ({tripResults.length})</h2>
            </div>
            {tripResults.map(trip=>(
              <article className="panel-card trip-result" key={trip.id}>
                <div className="trip-result-heading">
                  <div>
                    <span className="section-kicker">{language==="am" ? "የጉዞ መነሻ" : "DEPARTURE"}</span>
                    <h3>{formatTripTime(trip.departure_at)}</h3>
                  </div>
                  <strong>{formatTripFare(trip.fare.amount_minor_units,trip.fare.currency_code)}</strong>
                </div>
                <p>{language==="am" ? "መሳፈሪያ" : "Boarding point"}: {trip.boarding_model}</p>
                <p>{language==="am" ? "የተገኙ መቀመጫዎች" : "Available seats"}: {trip.available_seats}</p>
                {trip.arrival_estimate_at && <p>{language==="am" ? "የመድረሻ ግምት" : "Estimated arrival"}: {formatTripTime(trip.arrival_estimate_at)}</p>}
                <span className="wallet-badge">{language==="am" ? "የቦታ ማስያዣ ብቻ" : "Reservation only"}</span>
                <p className="field-hint">{language==="am" ? "ክፍያና ትኬት ገና አልነቁም።" : "Payment and ticket issuance are not enabled."}</p><button type="button" className="primary-action" onClick={()=>setSelectedTrip(trip)}>{language==="am" ? "መቀመጫ ምረጥ" : "Choose seats"}</button>
              </article>
            ))}
          </div>
        )}
        {!tripLoading && tripResults.length===0 && !tripError && (
          <p className="muted-copy">
            {locations.length<2
              ? (language==="am" ? "የታተሙ ቦታዎች ገና አልተገኙም።" : "No published locations are available yet.")
              : (language==="am" ? "ጉዞ ለማግኘት መነሻና መድረሻ ይምረጡ።" : "Choose an origin and destination to search published trips.")}
          </p>
        )}
        <div className="map-pick-controls" role="group" aria-label={language==="am"?"ከካርታ ቦታ ይምረጡ":"Choose a location from the map"}>
          <button type="button" className={mapPickTarget==="origin"?"map-pick active":"map-pick"} aria-pressed={mapPickTarget==="origin"} onClick={()=>setMapPickTarget("origin")}>{language==="am"?"መነሻ ምረጥ":"Pick origin"}</button>
          <button type="button" className={mapPickTarget==="destination"?"map-pick active":"map-pick"} aria-pressed={mapPickTarget==="destination"} onClick={()=>setMapPickTarget("destination")}>{language==="am"?"መድረሻ ምረጥ":"Pick destination"}</button>
        </div>
        <PassengerGoogleMap locations={locations} routes={routes} originId={originId} destinationId={destinationId} language={language} onSelectLocation={id=>{if(mapPickTarget==="origin"){setOriginId(id);if(id===destinationId)setDestinationId("");}else{setDestinationId(id);if(id===originId)setOriginId("");}}}/>
        <p className="map-legend-note">{t.mapNote}</p>
        <p className="muted-copy">{language==="am"?"ካርታው የታተሙ እና የተረጋገጡ የቦታ መረጃዎችን ብቻ ያሳያል።":"The map displays only published, source-backed location and route geometry. Missing data is never fabricated."}</p>
      </section>
    )}{page==="wallet"&&<section className="content-section wallet-view">
     <article className="wallet-card">
      <span>{t.balance}</span>
      <strong>{passenger&&walletData?formatTripFare(walletData.balance_minor_units,walletData.currency_code):"—"} <small>ETB</small></strong>
      <span className="wallet-badge">{walletData?.account_status==="frozen"?(language==="am"?"ታግዷል":"FROZEN"):walletData?.account_status==="closed"?(language==="am"?"ተዘግቷል":"CLOSED"):(language==="am"?"የሂሳብ መዝገብ":"LEDGER ACCOUNT")}</span>
      <p>{language==="am"?"ቀሪ ሂሳቡ ከተመዘገቡ የሂሳብ መዝገብ ግቤቶች ይሰላል። እውነተኛ ገንዘብ ግብይት አልነቃም።":"Balance is derived from posted double-entry ledger records. Real-money transactions are not enabled."}</p>
     </article>
     {!passenger&&<div className="notice-panel">{language==="am"?"የቦርሳ ሂሳብዎን ለማየት ይግቡ።":"Sign in to view your wallet account."} <button type="button" className="text-link" onClick={()=>go("login")}>{t.login}</button></div>}
     {walletLoading&&<p role="status">{language==="am"?"የቦርሳ ሂሳብ በመጫን ላይ…":"Loading wallet ledger…"}</p>}
     {walletError&&<p className="notice-panel" role="alert">{walletError}</p>}
     <div className="wallet-actions">
      <button onClick={()=>setNotice(t.coming)} title={language==="am"?"የክፍያ አጋር እስኪፈቀድ ድረስ አይነቃም":"Unavailable until a licensed payment partner is approved"}><Icon name="plus"/> {language==="am"?"ገንዘብ ጨምር":"Add funds"}</button>
      <button onClick={()=>setNotice(t.coming)} title={language==="am"?"የክፍያ አጋር እስኪፈቀድ ድረስ አይነቃም":"Unavailable until a licensed payment partner is approved"}><Icon name="arrow"/> {language==="am"?"ገንዘብ አውጣ":"Withdraw"}</button>
      <button disabled={!walletData||walletData.history.length===0} onClick={()=>document.getElementById("wallet-transactions")?.scrollIntoView({behavior:"smooth"})}><Icon name="receipt"/> {language==="am"?"ግብይቶች":"Transactions"}</button>
     </div>
     <div className="panel-card" id="wallet-transactions">
      <h2>{language==="am"?"የግብይት ታሪክ":"Transaction history"}</h2>
      {!passenger?<p>{language==="am"?"ለመቀጠል ይግቡ።":"Sign in to view transactions."}</p>:walletLoading?<p>{language==="am"?"በመጫን ላይ…":"Loading…"}</p>:walletData?.history.length?walletData.history.map(item=><article className="support-case" key={item.reference}>
       <div><strong>{item.description}</strong><small>{item.reference} · {item.transaction_type}</small></div>
       <span className="wallet-badge">{item.status}</span>
       <strong>{item.direction==="debit"?"−":item.direction==="credit"?"+":""}{formatTripFare(item.amount_minor_units,item.currency_code)}</strong>
       <small>{new Date(item.posted_at).toLocaleString(language==="am"?"am-ET":"en-ET")}</small>
      </article>):<p>{language==="am"?"ገና የተመዘገቡ ግብይቶች የሉም።":"No posted ledger transactions yet."}</p>}
     </div>
     <p className="compliance-note">{language==="am"?"ገንዘብ መጨመር፣ ማውጣት እና ማስተላለፍ የቁጥጥር ፈቃድና የባንክ/ክፍያ አጋር ማረጋገጫ እስኪገኝ ድረስ ተዘግተዋል።":"Funding, withdrawals and transfers remain disabled pending regulatory clearance and verified banking/payment partners."}</p>
    </section>}
    {page==="profile"&&<section className="content-section"><div className="panel-card profile-panel"><span className="large-avatar">{profileName.trim()?profileName.trim().charAt(0).toUpperCase():"M"}</span><h2>{profileName||(passenger?(language==="am"?"ተሳፋሪ":"Passenger"):(language==="am"?"የእንግዳ መገለጫ":"Guest profile"))}</h2><p>{passenger?.login_identifier||profilePhone||t.noLogin}</p><div className="form-actions"><button className="primary-action" onClick={()=>{setProfileEditing(!profileEditing);setProfileSaved(false);}}>{profileEditing?(language==="am"?"ዝጋ":"Close"):(language==="am"?"መገለጫ አርትዕ":"Edit profile")}<Icon name="arrow"/></button>{!passenger&&<button className="secondary-action" onClick={()=>go("login")}>{t.login}</button>}</div></div>{profileEditing&&<form className="form-card" onSubmit={saveProfile}><h2>{language==="am"?"የመገለጫ መረጃ":"Edit profile"}</h2><label>{t.name}<input value={profileName} onChange={e=>setProfileName(e.target.value)} required minLength={2} maxLength={120} autoComplete="name"/></label><label>{t.phone}<input value={profilePhone} onChange={e=>setProfilePhone(e.target.value)} inputMode="tel" autoComplete="tel" disabled={Boolean(passenger)}/></label><label>{t.email}<input type="email" value={profileEmail} onChange={e=>setProfileEmail(e.target.value)} autoComplete="email" disabled={Boolean(passenger)}/></label><p className="field-hint">{passenger?(language==="am"?"የሙሉ ስም ለውጥ ወደ መለያዎ ይቀመጣል።":"Your display name is saved to your passenger account. Contact changes require verification."):(language==="am"?"ይህ የእንግዳ ማሳያ ነው፤ ለማስቀመጥ ይግቡ።":"Guest profile edits are preview-only until you sign in.")}</p><button className="primary-action" type="submit">{language==="am"?"አስቀምጥ":"Save profile"}</button></form>}<div className="panel-card settings-list"><h2>{t.account}</h2><button onClick={()=>setLanguage(language==="am"?"en":"am")}>{t.language}<span>{language==="am"?"አማርኛ":"English"}</span></button><button onClick={()=>setNotice(t.coming)}>{t.notifications}<span>›</span></button><button onClick={()=>go("forgot")}>{language==="am"?"የይለፍ ቃል መቀየር":"Password and security"}<span>›</span></button><button onClick={()=>go("help")}>{t.help}<span>›</span></button>{passenger&&<button onClick={signOut}>{t.signout}<span>↗</span></button>}</div>{profileSaved&&<p className="notice-panel" role="status">{language==="am"?"መገለጫው ተዘምኗል":"Profile updated"}</p>}</section>}{(page==="login"||page==="register"||page==="forgot")&&<section className="content-section"><form className="form-card" onSubmit={submitAuth} aria-busy={authBusy}><h2>{page==="login"?t.login:page==="register"?t.register:(language==="am"?"የይለፍ ቃል መመለስ":"Recover password")}</h2>{page==="register"&&<label>{t.name}<input required minLength={2} maxLength={120} autoComplete="name" value={authName} onChange={e=>setAuthName(e.target.value)} placeholder={language==="am"?"ሙሉ ስም":"Enter your full name"}/></label>}{page!=="forgot"&&<label>{language==="am"?"ኢሜይል ወይም ዓለም አቀፍ ስልክ ቁጥር":"Email or international phone number"}<input required minLength={5} maxLength={254} autoComplete="username" value={authIdentifier} onChange={e=>setAuthIdentifier(e.target.value)} placeholder="+2519… or name@example.com"/></label>}{page!=="forgot"&&<label>{t.password}<div className="password-field"><input required minLength={page==="register"?6:1} maxLength={128} type={passwordVisible?"text":"password"} value={authPassword} onChange={e=>setAuthPassword(e.target.value)} autoComplete={page==="login"?"current-password":"new-password"}/><button type="button" className="secondary-action" aria-label={passwordVisible?(language==="am"?"ደብቅ":"Hide password"):(language==="am"?"አሳይ":"Show password")} onClick={()=>setPasswordVisible(!passwordVisible)}>{passwordVisible?(language==="am"?"ደብቅ":"Hide"):(language==="am"?"አሳይ":"Show")}</button></div></label>}{page==="register"&&<><label>{language==="am"?"የይለፍ ቃል ድገም":"Confirm password"}<input required minLength={6} maxLength={128} type={passwordVisible?"text":"password"} value={authConfirmPassword} onChange={e=>setAuthConfirmPassword(e.target.value)} autoComplete="new-password"/></label><label className="consent-row"><input type="checkbox" required/><span>{language==="am"?"የአጠቃቀም ውሎችን እና የግላዊነት መመሪያን ተቀብያለሁ":"I agree to the Terms of Use and Privacy Notice."}</span></label></>}{page==="forgot"&&<><label>{language==="am"?"ኢሜይል ወይም ስልክ ቁጥር":"Email or phone number"}<input required minLength={5} maxLength={254} value={authIdentifier} onChange={e=>setAuthIdentifier(e.target.value)}/></label><p className="field-hint">{language==="am"?"የመለያ መመለሻ ማድረሻ አገልግሎት ገና አልተገናኘም።":"Password recovery delivery is not configured yet. No reset email or SMS will be sent."}</p></>}{page!=="forgot"&&<p className="field-hint">{page==="register"?(language==="am"?"የምዝገባ እና የግባ አገልግሎት ከመለያ ሰርቨር ጋር ይገናኛል።":"Your account will be created by the passenger account service. Contact verification is not yet configured."):(language==="am"?"የተሳፋሪ መለያዎን ይጠቀሙ።":"Sign in with your passenger account credentials.")}</p>}<button className="primary-action" type="submit" disabled={authBusy}>{authBusy?(language==="am"?"በመጫን ላይ…":"Working…"):page==="forgot"?(language==="am"?"መመለሻ ጀምር":"Start recovery"):t.submit}<Icon name="arrow"/></button>{page==="login"&&<button type="button" className="text-link" onClick={()=>go("forgot")}>{language==="am"?"የይለፍ ቃል ረሳሁ":"Forgot password?"}</button>}<button type="button" className="text-link" onClick={()=>{setAuthPassword("");setAuthConfirmPassword("");go(page==="login"?"register":"login");}}>{page==="login"?t.register:t.login}</button></form></section>}{page==="help"&&<section className="content-section support-layout">
     <div className="panel-card support-panel">
      <h2>{t.support}</h2>
      <p>{language==="am"?"የMaaleNex አገልግሎቶችን ለመጠቀም መረጃ ያግኙ ወይም የድጋፍ ጥያቄ ይላኩ።":"Find answers about MaaleNex services or send a support request. Your requests are saved to your account."}</p>
      {!passenger&&<div className="notice-panel">{language==="am"?"የጥያቄዎችን ሁኔታ ለማየትና አዲስ ጥያቄ ለመላክ ይግቡ።":"Sign in to submit a request and track its status."} <button className="text-link" type="button" onClick={()=>go("login")}>{language==="am"?"ግባ":"Sign in"}</button></div>}
      <h3>{language==="am"?"ተደጋጋሚ ጥያቄዎች":"Frequently asked questions"}</h3>
      {supportLoading&&<p role="status">{language==="am"?"በመጫን ላይ…":"Loading Help and Support…"}</p>}
      {supportFaqs.map(item=><details className="support-faq" key={item.id}><summary>{item.question}</summary><p>{item.answer}</p></details>)}
      {supportError&&<p className="support-error" role="alert">{supportError}</p>}
     </div>
     <div className="form-card support-form-card">
      <h2>{language==="am"?"ድጋፍን ያግኙ":"Contact support"}</h2>
      <form onSubmit={submitSupportCase}>
       <label>{language==="am"?"የጥያቄ ምድብ":"Request category"}
        <select value={supportCategory} onChange={e=>setSupportCategory(e.target.value as PassengerSupportCase["category"])}>
         <option value="general">{language==="am"?"አጠቃላይ":"General"}</option>
         <option value="account">{language==="am"?"መለያ":"Account"}</option>
         <option value="booking">{language==="am"?"ቦታ ማስያዣ":"Booking"}</option>
         <option value="journey">{language==="am"?"ጉዞ":"Journey"}</option>
         <option value="wallet">{language==="am"?"ቦርሳ":"Wallet"}</option>
         <option value="safety">{language==="am"?"ደህንነት":"Safety"}</option>
         <option value="accessibility">{language==="am"?"ተደራሽነት":"Accessibility"}</option>
         <option value="technical">{language==="am"?"ቴክኒካዊ ችግር":"Technical issue"}</option>
        </select>
       </label>
       <label>{language==="am"?"ርዕስ":"Subject"}<input required minLength={3} maxLength={160} value={supportSubject} onChange={e=>setSupportSubject(e.target.value)}/></label>
       <label>{language==="am"?"ዝርዝር መልዕክት":"Message"}<textarea required minLength={10} maxLength={4000} rows={5} value={supportMessage} onChange={e=>setSupportMessage(e.target.value)}/></label>
       <p className="support-hint">{language==="am"?"ከፍተኛ 4,000 ቁምፊ። ፋይል ማያያዝ ገና አልተነቃም።":"Maximum 4,000 characters. File attachments are not enabled yet."}</p>
       <button className="primary-action" type="submit" disabled={supportSubmitting||!passenger}>{supportSubmitting?(language==="am"?"በመላክ ላይ…":"Submitting…"):(language==="am"?"ጥያቄ ላክ":"Submit request")}<Icon name="arrow"/></button>
      </form>
     </div>
     <div className="panel-card support-panel">
      <h2>{language==="am"?"የድጋፍ ጥያቄዎቼ":"My support requests"}</h2>
      {!passenger?<p>{language==="am"?"የጥያቄዎችን ታሪክ ለማየት ይግቡ።":"Sign in to view your support history."}</p>:supportCases.length===0?<p>{language==="am"?"ገና የተላከ ጥያቄ የለም።":"You have no support requests yet."}</p>:supportCases.map(item=><article className="support-case" key={item.case_reference}><div><strong>{item.subject}</strong><small>{item.case_reference} · {item.category}</small></div><span className={"support-status status-"+item.status}>{language==="am"?({open:"ክፍት",in_progress:"በሂደት ላይ",resolved:"ተፈትቷል",closed:"ተዘግቷል"} as const)[item.status]:item.status.replace("_"," ")}</span>{item.resolution_note&&<p>{item.resolution_note}</p>}</article>)}
     </div>
    </section>}
    {page==="report"&&<section className="content-section support-layout">
     <div className="form-card support-form-card">
      <h2>{language==="am"?"ሪፖርት እና ቅሬታ ያቅርቡ":"Reports and Complaints"}</h2>
      <p>{language==="am"?"የአገልግሎት ችግርን ወይም ቅሬታን በተለየ ሁኔታ ያስገቡ። ማጣቀሻ ቁጥር ይቀበላሉ።":"Submit a service report or a formal complaint. Each submission receives a reference and can be tracked separately from Help requests."}</p>
      {!passenger&&<div className="notice-panel">{language==="am"?"ሪፖርት ለማቅረብ ይግቡ።":"Sign in to submit and track a report."} <button type="button" className="text-link" onClick={()=>go("login")}>{t.login}</button></div>}
      {reportError&&<p className="support-error" role="alert">{reportError}</p>}
      <form onSubmit={submitReport}>
       <label>{language==="am"?"የማቅረቢያ አይነት":"Submission type"}
        <select aria-label="Submission type" value={reportType} onChange={e=>setReportType(e.target.value as PassengerReport["report_type"])}>
         <option value="report">{language==="am"?"ሪፖርት":"Report"}</option>
         <option value="complaint">{language==="am"?"መደበኛ ቅሬታ":"Formal complaint"}</option>
        </select>
       </label>
       <label>{language==="am"?"ምድብ":"Category"}
        <select aria-label="Report category" value={reportCategory} onChange={e=>setReportCategory(e.target.value as PassengerReport["category"])}>
         <option value="app_issue">{language==="am"?"የመተግበሪያ ችግር":"App issue"}</option>
         <option value="journey">{language==="am"?"የጉዞ መረጃ":"Journey information"}</option>
         <option value="booking">{language==="am"?"ቦታ ማስያዣ":"Booking"}</option>
         <option value="wallet">{language==="am"?"ቦርሳ":"Wallet"}</option>
         <option value="payment">{language==="am"?"ክፍያ":"Payment"}</option>
         <option value="safety">{language==="am"?"ደህንነት":"Safety"}</option>
         <option value="driver_vehicle">{language==="am"?"ሹፌር ወይም ተሽከርካሪ":"Driver or vehicle"}</option>
         <option value="accessibility">{language==="am"?"ተደራሽነት":"Accessibility"}</option>
         <option value="fraud">{language==="am"?"ማጭበርበር":"Fraud or scam"}</option>
         <option value="other">{language==="am"?"ሌላ":"Other"}</option>
        </select>
       </label>
       <label>{language==="am"?"አስቸኳይነት":"Severity"}
        <select aria-label="Severity" value={reportSeverity} onChange={e=>setReportSeverity(e.target.value as PassengerReport["severity"])}>
         <option value="low">{language==="am"?"ዝቅተኛ":"Low"}</option>
         <option value="normal">{language==="am"?"መደበኛ":"Normal"}</option>
         <option value="high">{language==="am"?"ከፍተኛ":"High"}</option>
         <option value="urgent">{language==="am"?"አስቸኳይ":"Urgent"}</option>
        </select>
       </label>
       <label>{language==="am"?"ርዕስ":"Subject"}<input required minLength={3} maxLength={160} value={reportSubject} onChange={e=>setReportSubject(e.target.value)}/></label>
       <label>{language==="am"?"የችግሩ ዝርዝር":"Description"}<textarea required minLength={10} maxLength={5000} value={report} onChange={e=>setReport(e.target.value)} rows={6}/></label>
       <label>{language==="am"?"ማስረጃ ፋይል (አማራጭ)":"Evidence attachment (optional)"}
        <input id="report-evidence" type="file" multiple accept=".pdf,.jpg,.jpeg,.png,.webp,application/pdf,image/jpeg,image/png,image/webp" onChange={e=>{const files=Array.from(e.target.files??[]);if(files.length>3||files.some(file=>file.size>5*1024*1024||!["application/pdf","image/jpeg","image/png","image/webp"].includes(file.type))){setReportError(language==="am"?"እስከ 3 PDF፣ JPG፣ PNG ወይም WebP ፋይሎችን፣ እያንዳንዱን እስከ 5 MB ይምረጡ።":"Choose up to three PDF, JPG, PNG or WebP files, each no larger than 5 MB.");e.target.value="";setReportAttachments([]);}else{setReportError("");setReportAttachments(files);}}}/>
       </label>
       <p className="support-hint">{language==="am"?"እስከ 3 ፋይሎች፣ እያንዳንዱ እስከ 5 MB።":"Up to three files per case, 5 MB each."}</p>
       <button className="primary-action" type="submit" disabled={!passenger||reportSubmitting}>{reportSubmitting?(language==="am"?"በመላክ ላይ…":"Submitting…"):(language==="am"?"ሪፖርት አስገባ":"Submit report")}<Icon name="arrow"/></button>
      </form>
     </div>
     <div className="panel-card support-panel">
      <h2>{language==="am"?"የእኔ ሪፖርቶች እና ቅሬታዎች":"My reports and complaints"}</h2>
      {reportLoading&&<p role="status">{language==="am"?"በመጫን ላይ…":"Loading reports…"}</p>}
      {!passenger?<p>{language==="am"?"ታሪክዎን ለማየት ይግቡ።":"Sign in to view your submissions."}</p>:reportCases.length===0&&!reportLoading?<p>{language==="am"?"ገና ሪፖርት ወይም ቅሬታ የለም።":"No reports or complaints submitted yet."}</p>:reportCases.map(item=><article className="support-case" key={item.report_reference}><div><strong>{item.subject}</strong><small>{item.report_reference} · {item.report_type} · {item.category}</small></div><span className={"support-status status-"+item.status}>{language==="am"?({submitted:"ተልኳል",under_review:"በግምገማ ላይ",action_required:"ተጨማሪ እርምጃ ያስፈልጋል",resolved:"ተፈትቷል",dismissed:"ተዘግቷል"} as const)[item.status]:item.status.replace("_"," ")}</span><small>{item.severity} · {item.attachments.length} {language==="am"?"ማስረጃ":"evidence file(s)"}</small>{item.resolution_note&&<p>{item.resolution_note}</p>}{item.attachments.map(file=><a className="text-link" key={file.id} href={passengerReportAttachmentUrl(item.report_reference,file.id)} download>{file.file_name}</a>)}</article>)}
     </div>
    </section>}
    {page==="about"&&<section className="content-section"><div className="panel-card"><h2>MaaleNex</h2><p>{language==="am"?"በኢትዮጵያ ውስጥ የተሳፋሪ ተሞክሮን ለማሻሻል የሚገነባ የመጓጓዣ ቴክኖሎጂ መድረክ።":"Mobility technology designed to improve the passenger experience in Ethiopia."}</p></div></section>}
    <footer className="platform-footer"><span>© MaaleNex</span><span>{language==="am"?"በአካባቢያዊ ግንዛቤ የተመራ":"Built with local understanding"}</span><span>{t.demo}</span></footer>
   </main>
  </div>
 </div>;
}
