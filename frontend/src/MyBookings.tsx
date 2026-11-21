import { useEffect, useState } from "react";
import { cancelMyBooking, listMyBookings, requestBookingChallenge, claimPassengerBooking, type BookingChallenge, type PassengerBooking } from "./passenger-api";

type Props = { language: "am" | "en"; onClose: () => void };
export function MyBookings({ language, onClose }: Props) {
  const am = language === "am";
  const [items,setItems] = useState<PassengerBooking[]>([]);
  const [loading,setLoading] = useState(true);
  const [error,setError] = useState("");
  const [busy,setBusy] = useState("");
  const [filter,setFilter] = useState("all");
  const [expanded,setExpanded] = useState("");
  const [claimReference,setClaimReference] = useState("");
  const [claimPhone,setClaimPhone] = useState("+251");
  const [claimCode,setClaimCode] = useState("");
  const [claimChallenge,setClaimChallenge] = useState<BookingChallenge|null>(null);
  const [claimBusy,setClaimBusy] = useState(false);
  const [claimError,setClaimError] = useState("");
  const [claimMessage,setClaimMessage] = useState("");
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
  const startClaim = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setClaimBusy(true); setClaimError(""); setClaimMessage("");
    try { const challenge = await requestBookingChallenge(claimReference.trim(),claimPhone.trim()); setClaimChallenge(challenge); }
    catch (reason) { setClaimError(reason instanceof Error ? reason.message : "Unable to start booking verification."); }
    finally { setClaimBusy(false); }
  };
  const completeClaim = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault(); if (!claimChallenge) return; setClaimBusy(true); setClaimError("");
    try { await claimPassengerBooking(claimChallenge.challenge_id,claimCode.trim()); setClaimMessage(am ? "ማስያዣው ከመለያዎ ጋር ተገናኝቷል።" : "Booking successfully linked to your passenger account."); setClaimReference(""); setClaimPhone("+251"); setClaimCode(""); setClaimChallenge(null); await refresh(); }
    catch (reason) { setClaimError(reason instanceof Error ? reason.message : "Unable to link this booking."); }
    finally { setClaimBusy(false); }
  };
  const statusLabel = (status: string) => {
    const labels: Record<string, string> = {held:"ጊዜያዊ ይዞታ",reserved:"ተረጋግጧል",expired:"ጊዜው አልፏል",cancelled:"ተሰርዟል"};
    return am ? (labels[status] ?? status) : status.replaceAll("_"," ");
  };
  const date = (value: string | null) => value
    ? new Intl.DateTimeFormat(am ? "am-ET" : "en-ET",{dateStyle:"medium",timeStyle:"short",timeZone:"Africa/Addis_Ababa"}).format(new Date(value))
    : (am ? "አልተገኘም" : "Not available");
  return <section className="content-section"><div className="panel-card bookings-panel">
    <div className="section-heading"><div><span className="section-kicker">PASSENGER ACCOUNT</span><h2>{am?"የእኔ ማስያዣዎች":"My Bookings"}</h2><p>{am?"ከመለያዎ ጋር የተገናኙ ማስያዣዎችን ይመልከቱና ያስተዳድሩ።":"View and manage bookings securely linked to your passenger account."}</p></div><button className="secondary-action" onClick={onClose}>{am?"ዝጋ":"Close"}</button></div>
    <details className="booking-claim-panel" open>
      <summary>{am?"ነባር ማስያዣን ከመለያ ጋር ያገናኙ":"Link an existing guest booking"}</summary>
      <p className="field-hint">{am?"የማስያዣ ማጣቀሻና የተመዘገበ ስልክ በመጠቀም ባለቤትነትዎን ያረጋግጡ።":"Verify control of the booking contact. Only the exact verified booking is linked; bookings are never matched by phone number alone."}</p>
      {!claimChallenge?<form onSubmit={startClaim}>
        <label>{am?"የማስያዣ ማጣቀሻ":"Booking reference"}<input required minLength={8} maxLength={64} value={claimReference} onChange={event=>setClaimReference(event.target.value)}/></label>
        <label>{am?"የተመዘገበ ስልክ":"Registered booking phone"}<input required minLength={8} maxLength={32} inputMode="tel" value={claimPhone} onChange={event=>setClaimPhone(event.target.value)}/></label>
        <button className="secondary-action" type="submit" disabled={claimBusy}>{claimBusy?(am?"በመጠየቅ ላይ…":"Requesting…"):(am?"ማረጋገጫ ጠይቅ":"Request verification")}</button>
      </form>:<form onSubmit={completeClaim}>
        {claimChallenge.synthetic_test_code&&<p className="notice-panel">{am?"የሙከራ ኮድ":"Test-only code"}: <strong>{claimChallenge.synthetic_test_code}</strong></p>}
        <label>{am?"የማረጋገጫ ኮድ":"Six-digit verification code"}<input required minLength={6} maxLength={6} inputMode="numeric" pattern="[0-9]{6}" value={claimCode} onChange={event=>setClaimCode(event.target.value.replace(/\D/g,"").slice(0,6))}/></label>
        <button className="secondary-action" type="submit" disabled={claimBusy||claimCode.length!==6}>{claimBusy?(am?"በማረጋገጥ ላይ…":"Verifying…"):(am?"አረጋግጥና አገናኝ":"Verify and link")}</button>
        <button className="text-link" type="button" onClick={()=>{setClaimChallenge(null);setClaimCode("");}}>{am?"ተመለስ":"Start over"}</button>
      </form>}
      {claimError&&<p className="support-error" role="alert">{claimError}</p>}
      {claimMessage&&<p className="notice-panel" role="status">{claimMessage}</p>}
    </details>
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
