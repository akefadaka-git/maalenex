import { useEffect, useState } from "react";
import { cancelMyBooking, listMyBookings, type PassengerBooking } from "./passenger-api";

type Props = { language: "am" | "en"; onClose: () => void };
export function MyBookings({ language, onClose }: Props) {
  const am = language === "am";
  const [items,setItems] = useState<PassengerBooking[]>([]);
  const [loading,setLoading] = useState(true);
  const [error,setError] = useState("");
  const [busy,setBusy] = useState("");
  const [filter,setFilter] = useState("all");
  const [expanded,setExpanded] = useState("");
  const refresh = async () => {
    setLoading(true); setError("");
    try { setItems((await listMyBookings()).items); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to load bookings."); }
    finally { setLoading(false); }
  };
  useEffect(() => { void refresh(); }, []);
  const cancel = async (item: PassengerBooking) => {
    if (!item.can_cancel || !window.confirm(am ? "ይህን ጊዜያዊ የመቀመጫ ይዞታ መሰረዝ ይፈልጋሉ?" : "Cancel this unconfirmed seat hold?")) return;
    setBusy(item.booking_id); setError("");
    try { await cancelMyBooking(item.booking_id); await refresh(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Cancellation failed."); }
    finally { setBusy(""); }
  };
  const visible = items.filter(item => filter === "all" || item.status === filter);
  const statusLabel = (status: string) => am
    ? ({held:"ጊዜያዊ ይዞታ",reserved:"ተረጋግጧል",expired:"ጊዜው አልፏል",cancelled:"ተሰርዟል"}[status] ?? status)
    : status.replaceAll("_"," ");
  const date = (value: string | null) => value
    ? new Intl.DateTimeFormat(am ? "am-ET" : "en-ET",{dateStyle:"medium",timeStyle:"short",timeZone:"Africa/Addis_Ababa"}).format(new Date(value))
    : (am ? "አልተገኘም" : "Not available");
  return <section className="content-section"><div className="panel-card bookings-panel">
    <div className="section-heading"><div><span className="section-kicker">PASSENGER ACCOUNT</span><h2>{am?"የእኔ ማስያዣዎች":"My Bookings"}</h2><p>{am?"ከመለያዎ ጋር የተገናኙ ማስያዣዎችን ይመልከቱና ያስተዳድሩ።":"View and manage bookings securely linked to your passenger account."}</p></div><button className="secondary-action" onClick={onClose}>{am?"ዝጋ":"Close"}</button></div>
    <div className="booking-filters">{["all","held","reserved","expired","cancelled"].map(value=><button key={value} className={filter===value?"filter-active":"secondary-action"} onClick={()=>setFilter(value)}>{value==="all"?(am?"ሁሉም":"All"):statusLabel(value)}</button>)}</div>
    {loading&&<p role="status">{am?"ማስያዣዎችን በመጫን ላይ…":"Loading your bookings…"}</p>}
    {error&&<p role="alert" className="support-error">{error}</p>}
    {!loading&&visible.length===0&&<div className="empty-bookings"><strong>{am?"ማስያዣ አልተገኘም":"No bookings found"}</strong><p>{am?"ከዚህ መለያ ጋር የተገናኘ ማስያዣ የለም።":"Bookings verified and linked to this account will appear here."}</p></div>}
    {visible.map(item=><article className="booking-card" key={item.booking_id}>
      <div className="booking-card-top"><div><span className="section-kicker">{am?"ማጣቀሻ":"BOOKING REFERENCE"}</span><h3>{item.booking_reference}</h3></div><span className={"support-status status-"+item.status}>{statusLabel(item.status)}</span></div>
      <div className="booking-summary-grid"><div><small>{am?"መነሻ ጊዜ":"Departure"}</small><strong>{date(item.departure_at)}</strong></div><div><small>{am?"የተፈጠረበት":"Created"}</small><strong>{date(item.created_at)}</strong></div><div><small>{am?"ተሳፋሪዎች":"Passengers"}</small><strong>{item.passengers.length}</strong></div><div><small>{am?"ዋጋ":"Fare"}</small><strong>{item.fare?new Intl.NumberFormat(am?"am-ET":"en-ET",{style:"currency",currency:item.fare.currency_code}).format(item.fare.amount_minor_units/100):(am?"አልተገኘም":"Not available")}</strong></div></div>
      {item.status==="held"&&item.hold_expires_at&&<p className="booking-expiry">{am?"የይዞታ ጊዜ የሚያበቃው":"Hold expires"}: {date(item.hold_expires_at)}</p>}
      <div className="booking-card-actions"><button className="text-link" onClick={()=>setExpanded(expanded===item.booking_id?"":item.booking_id)}>{expanded===item.booking_id?(am?"ዝርዝር ደብቅ":"Hide details"):(am?"ዝርዝር አሳይ":"View details")}</button>{item.can_cancel&&<button className="secondary-action" disabled={busy===item.booking_id} onClick={()=>void cancel(item)}>{busy===item.booking_id?(am?"በመሰረዝ ላይ…":"Cancelling…"):(am?"ይዞታውን ሰርዝ":"Cancel hold")}</button>}</div>
      {expanded===item.booking_id&&<div className="booking-details"><p>{am?"የመድረሻ ግምት":"Estimated arrival"}: {date(item.arrival_estimate_at)}</p>{item.passengers.map((person,index)=><p key={index}>{person.name} · {person.seat}</p>)}{item.reservation_reference&&<p>{am?"የማስያዣ ቁጥር":"Reservation"}: {item.reservation_reference}</p>}<small>{am?"ክፍያ፣ ትኬት እና መሳፈር ፈቃድ አልተነቁም።":"Payment, ticket issuance and boarding authorization are not enabled."}</small></div>}
    </article>)}
    <p className="compliance-note">{am?"የተረጋገጡ ማስያዣዎች ብቻ ይታያሉ። የእንግዳ ማስያዣን ለማገናኘት የማስያዣ ማረጋገጫ ይጠቀሙ።":"Only bookings verified and linked to this account are shown. Guest bookings must be claimed through the booking verification flow."}</p>
  </div></section>;
}
