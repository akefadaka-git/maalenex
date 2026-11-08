import { useEffect, useMemo, useState, type FormEvent } from "react";

type Language = "am" | "en";
type LocationOption = { id: string; name: string; type: string };
type TripResult = {
  id: string; departure_at: string; arrival_estimate_at: string | null;
  boarding_model: string; available_seats: number; availability_as_of: string;
  fare: { amount_minor_units: number; currency_code: "ETB" };
  reservation_only: boolean; ticketing_enabled: false; payment_enabled: false;
};
type SeatOption = { trip_seat_id: string; seat_code: string; available: boolean };
type HoldResult = { booking_id: string; booking_reference: string; status: string; hold_expires_at: string };
type BookingDetails = {
  booking_id: string; booking_reference: string; status: string;
  passengers: Array<{ name: string; seat: string }>;
  fare: { amount_minor_units: number; currency_code: "ETB" } | null;
  payment_enabled: false; ticketing_enabled: false; boarding_authorized: false;
  reservation?: ReservationResult | null;
};
type ReservationResult = {
  reservation_reference: string; qr_payload_version: number; qr_payload_reference: string;
  status: string; payment_collected: false; travel_ticket_issued: false; boarding_authorized: false;
};
type SupportCase = {
  case_reference: string; category: string; subject: string; message: string;
  status: string; resolution_code: string | null; resolution_note: string | null;
};

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\\/+$/, "");\n\nfunction apiUrl(path: string): string {\n  return `${API_BASE_URL}${path}`;\n}\n\nconst copy = {
  am: {
    skip: "ወደ ዋና ይዘት ዝለል",
    eyebrow: "የተሳፋሪ መጓጓዣ", title: "ጉዞዎን ያቅዱ።",
    subtitle: "ከጂንካ የሚነሱ የታተሙ የጉዞ መርሐ ግብሮችን ይፈልጉ።",
    status: "የልማት አካባቢ · ሰው ሠራሽ መረጃ",
    from: "መነሻ", to: "መድረሻ", date: "የጉዞ ቀን", count: "ተሳፋሪዎች",
    search: "ጉዞ ፈልግ", loading: "በመፈለግ ላይ…", results: "የተገኙ ጉዞዎች",
    noResults: "ለዚህ ፍለጋ የታተመ ጉዞ አልተገኘም።", choose: "ይምረጡ",
    seats: "ባዶ ወንበሮች", departure: "መነሻ ሰዓት", fare: "የአንድ ተሳፋሪ ዋጋ",
    terminal: "መነሻ ቦታ", selectSeats: "ወንበሮችን ይምረጡ", selected: "የተመረጡ",
    contact: "የቦታ ማስያዣ አድራጊ መረጃ", contactName: "ሙሉ ስም",
    phone: "ስልክ", traveler: "የተሳፋሪ ስም", createHold: "ወንበር ያዝ",
    holdNote: "ይህ የሙከራ 10 ደቂቃ የወንበር ይዞታ ነው።",
    holdCreated: "የወንበር ይዞታ ተፈጥሯል", bookingRef: "የቦታ ማስያዣ ቁጥር",
    expires: "የይዞታ ማብቂያ", verifyContact: "የስልክ ማረጋገጫ ኮድ ይጠይቁ",
    challenge: "ማረጋገጫ", code: "የማረጋገጫ ኮድ", verify: "አረጋግጥ",
    syntheticCode: "የሙከራ ኮድ", reserve: "ቦታ ማስያዣውን አረጋግጥ",
    reservation: "የቦታ ማስያዣ ማረጋገጫ", reservationRef: "የማስያዣ ማጣቀሻ",
    qrRef: "የQR ማጣቀሻ ይዘት", qrCode: "የቦታ ማስያዣ QR ኮድ", notTicket: "ይህ ትኬት አይደለም፤ መሳፈርን አያስፈቅድም።",
    disabled: "ክፍያና የጉዞ ትኬት አልተከፈቱም።",
    loadingLocations: "የመነሻና መድረሻ ቦታዎች በመጫን ላይ…",
    error: "የጉዞ መረጃን ማግኘት አልተቻለም። እንደገና ይሞክሩ።",
    emptyLocations: "ለሙከራ የታተሙ ቦታዎች ገና የሉም።",
    language: "Switch language to English",\n    navHome: "Home", navSearch: "Find trips", navHelp: "Help", helpTitle: "Test information", helpBody: "This is a test application. Trip listings are supplied by the configured test API.",\n    navHome: "መነሻ", navSearch: "ጉዞ ፈልግ", navHelp: "እገዛ", helpTitle: "የሙከራ መረጃ", helpBody: "ይህ የሙከራ መተግበሪያ ነው። የጉዞ ዝርዝሮች ከሙከራ አገልጋይ ይመጣሉ።",
    revokeAccess: "Revoke booking access",
    accessRevoked: "Booking access was revoked.",
    support: "የድጋፍ ጥያቄ",
    supportSubject: "ርዕስ",
    supportMessage: "መልዕክት",
    supportSubmit: "ጥያቄ ላክ",
    supportCases: "የድጋፍ ጥያቄዎች",
    footer: "በሙከራ ላይ ያለ መድረክ። እውነተኛ ቦታ ማስያዝ፣ ክፍያ ወይም መሳፈር አይፈቀድም።",
  },
  en: {
    skip: "Skip to main content",
    eyebrow: "PASSENGER MOBILITY", title: "Plan your journey.",
    subtitle: "Search published passenger schedules originating from Jinka.",
    status: "Development environment · Synthetic data",
    from: "From", to: "To", date: "Travel date", count: "Passengers",
    search: "Search trips", loading: "Searching…", results: "Available trips",
    noResults: "No published trips match this search.", choose: "Select",
    seats: "Available seats", departure: "Departure", fare: "Fare per passenger",
    terminal: "Boarding point", selectSeats: "Choose seats", selected: "Selected",
    contact: "Booking contact", contactName: "Full name", phone: "Phone",
    traveler: "Passenger name", createHold: "Hold seats",
    holdNote: "This is a synthetic 10-minute seat hold for testing.",
    holdCreated: "Seat hold created", bookingRef: "Booking reference",
    expires: "Hold expires", verifyContact: "Request contact verification code",
    challenge: "Contact verification", code: "Verification code", verify: "Verify",
    syntheticCode: "Synthetic test code", reserve: "Confirm reservation",
    reservation: "Reservation confirmation", reservationRef: "Reservation reference",
    qrRef: "QR payload reference", qrCode: "Reservation QR code", notTicket: "This is not a travel ticket and does not authorize boarding.",
    disabled: "Payments and travel tickets are not enabled.",
    loadingLocations: "Loading origin and destination locations…",
    error: "Could not load trip information. Please try again.",
    emptyLocations: "No published locations are available in this synthetic environment yet.",
    language: "ቋንቋውን ወደ አማርኛ ቀይር",\n    navHome: "Home", navSearch: "Find trips", navHelp: "Help", helpTitle: "Test information", helpBody: "This is a test application. Trip listings are supplied by the configured test API.",
    revokeAccess: "የቦታ ማስያዣ መዳረሻን ዝጋ",
    accessRevoked: "የቦታ ማስያዣ መዳረሻ ተዘግቷል።",
    support: "Support request",
    supportSubject: "Subject",
    supportMessage: "Message",
    supportSubmit: "Submit request",
    supportCases: "Support cases",
    footer: "Development platform. Real reservations, payments and boarding are not authorized.",
  },
};

function localDate(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
}

function csrfCookie(): string {
  const prefix = "mnm_booking_csrf=";
  const item = document.cookie.split("; ").find((part) => part.startsWith(prefix));
  return item ? decodeURIComponent(item.slice(prefix.length)) : "";
}

export default function App() {
  const [language, setLanguage] = useState<Language>("am");
  const [locations, setLocations] = useState<LocationOption[]>([]);
  const [originId, setOriginId] = useState("");
  const [destinationId, setDestinationId] = useState("");
  const [travelDate, setTravelDate] = useState(localDate());
  const [passengerCount, setPassengerCount] = useState(1);
  const [trips, setTrips] = useState<TripResult[]>([]);
  const [loadingLocations, setLoadingLocations] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState("");
  const [searched, setSearched] = useState(false);
  const [selectedTrip, setSelectedTrip] = useState<TripResult | null>(null);
  const [seats, setSeats] = useState<SeatOption[]>([]);
  const [selectedSeatIds, setSelectedSeatIds] = useState<string[]>([]);
  const [loadingSeats, setLoadingSeats] = useState(false);
  const [contactName, setContactName] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [passengerNames, setPassengerNames] = useState<string[]>([""]);
  const [hold, setHold] = useState<HoldResult | null>(null);
  const [challengeId, setChallengeId] = useState("");
  const [syntheticCode, setSyntheticCode] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [booking, setBooking] = useState<BookingDetails | null>(null);
  const [reservation, setReservation] = useState<ReservationResult | null>(null);
  const [supportCases, setSupportCases] = useState<SupportCase[]>([]);
  const [supportSubject, setSupportSubject] = useState("");
  const [supportMessage, setSupportMessage] = useState("");
  const [working, setWorking] = useState(false);
  const t = copy[language];

  useEffect(() => { document.documentElement.lang = language; }, [language]);

  useEffect(() => {
    const controller = new AbortController();
    fetch(apiUrl("/api/v1/catalog/locations"), { signal: controller.signal })
      .then((response) => { if (!response.ok) throw new Error("locations"); return response.json() as Promise<LocationOption[]>; })
      .then((items) => {
        setLocations(items);
        if (items.length > 0) setOriginId(items[0].id);
        if (items.length > 1) setDestinationId(items[1].id);
      })
      .catch((reason: unknown) => {
        if (!(reason instanceof DOMException && reason.name === "AbortError")) setError("error");
      })
      .finally(() => setLoadingLocations(false));
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const savedBookingId = sessionStorage.getItem("mnm_active_booking_id");
    if (!savedBookingId) return;
    const controller = new AbortController();
    fetch(apiUrl(`/api/v1/bookings/${encodeURIComponent(savedBookingId)}`), {
      credentials: "include", signal: controller.signal,
    }).then(async (response) => {
      if (!response.ok) {
        if (response.status === 401 || response.status === 404) {
          sessionStorage.removeItem("mnm_active_booking_id");
        }
        return;
      }
      const detail = await response.json() as BookingDetails;
      setBooking(detail);
      setReservation(detail.reservation ?? null);
      const casesResponse = await fetch(apiUrl(`/api/v1/bookings/${encodeURIComponent(savedBookingId)}/support-cases`), {
        credentials: "include", signal: controller.signal,
      });
      if (casesResponse.ok) setSupportCases(await casesResponse.json() as SupportCase[]);
    }).catch(() => {
      if (!controller.signal.aborted) setError("error");
    });
    return () => controller.abort();
  }, []);

  const destinations = useMemo(() => locations.filter((item) => item.id !== originId), [locations, originId]);

  async function searchTrips(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!originId || !destinationId || originId === destinationId) return;
    setSearching(true); setError(""); setSearched(true);
    setSelectedTrip(null); setSeats([]); setSelectedSeatIds([]);
    setHold(null); setChallengeId(""); setBooking(null); setReservation(null);
    try {
      const params = new URLSearchParams({
        origin_id: originId, destination_id: destinationId,
        travel_date: travelDate, passenger_count: String(passengerCount),
      });
      const response = await fetch(apiUrl(`/api/v1/trips/search?${params.toString()}`));
      if (!response.ok) throw new Error("search");
      setTrips((await response.json()) as TripResult[]);
    } catch { setTrips([]); setError("error"); }
    finally { setSearching(false); }
  }

  async function chooseTrip(trip: TripResult) {
    setSelectedTrip(trip); setSeats([]); setSelectedSeatIds([]);
    setHold(null); setChallengeId(""); setBooking(null); setReservation(null); setError("");
    setLoadingSeats(true);
    try {
      const response = await fetch(apiUrl(`/api/v1/trips/${trip.id}/seats`));
      if (!response.ok) throw new Error("seats");
      setSeats((await response.json()) as SeatOption[]);
    } catch { setError("error"); }
    finally { setLoadingSeats(false); }
  }

  function toggleSeat(seatId: string) {
    setSelectedSeatIds((current) => current.includes(seatId)
      ? current.filter((id) => id !== seatId)
      : current.length < passengerCount ? [...current, seatId] : current);
  }

  async function createHold(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedTrip || selectedSeatIds.length !== passengerCount ||
        passengerNames.some((name) => !name.trim())) return;
    setWorking(true); setError("");
    try {
      const response = await fetch(apiUrl("/api/v1/bookings/holds"), {
        method: "POST", headers: { "Content-Type": "application/json", "Idempotency-Key": crypto.randomUUID() },
        body: JSON.stringify({
          trip_id: selectedTrip.id, booking_contact_name: contactName,
          booking_contact_phone: contactPhone,
          passengers: passengerNames.map((name) => ({ name })),
          seat_ids: selectedSeatIds,
        }),
      });
      if (!response.ok) throw new Error("hold");
      setHold((await response.json()) as HoldResult);
    } catch { setError("error"); }
    finally { setWorking(false); }
  }

  async function requestChallenge() {
    if (!hold) return;
    setWorking(true); setError("");
    try {
      const response = await fetch(apiUrl("/api/v1/passenger-access/challenges"), {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ booking_reference: hold.booking_reference, contact_phone: contactPhone }),
      });
      if (!response.ok) throw new Error("challenge");
      const result = await response.json() as { challenge_id: string; synthetic_test_code?: string };
      setChallengeId(result.challenge_id);
      setSyntheticCode(result.synthetic_test_code ?? "");
    } catch { setError("error"); }
    finally { setWorking(false); }
  }

  async function verifyChallenge(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!challengeId) return;
    setWorking(true); setError("");
    try {
      const response = await fetch(apiUrl(`/api/v1/passenger-access/challenges/${challengeId}/verify`), {
        method: "POST", credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: verificationCode }),
      });
      if (!response.ok) throw new Error("verify");
      const result = await response.json() as { booking_id: string };
      sessionStorage.setItem("mnm_active_booking_id", result.booking_id);
      const detail = await fetch(apiUrl(`/api/v1/bookings/${result.booking_id}`), { credentials: "include" });
      if (!detail.ok) throw new Error("booking");
      const bookingDetails = await detail.json() as BookingDetails;
      setBooking(bookingDetails);
      setReservation(bookingDetails.reservation ?? null);
      const casesResponse = await fetch(apiUrl(`/api/v1/bookings/${result.booking_id}/support-cases`), { credentials: "include" });
      if (casesResponse.ok) setSupportCases(await casesResponse.json() as SupportCase[]);
    } catch { setError("error"); }
    finally { setWorking(false); }
  }

  async function confirmReservation() {
    if (!booking) return;
    setWorking(true); setError("");
    try {
      const response = await fetch(apiUrl(`/api/v1/bookings/${booking.booking_id}/reservation`), {
        method: "POST", credentials: "include",
        headers: { "X-CSRF-Token": csrfCookie() },
      });
      if (!response.ok) throw new Error("reservation");
      setReservation((await response.json()) as ReservationResult);
    } catch { setError("error"); }
    finally { setWorking(false); }
  }

  async function submitSupportCase(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!booking || !supportSubject.trim() || !supportMessage.trim()) return;
    setWorking(true); setError("");
    try {
      const response = await fetch(apiUrl(`/api/v1/bookings/${booking.booking_id}/support-cases`), {
        method: "POST", credentials: "include",
        headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfCookie() },
        body: JSON.stringify({
          category: "reservation_status",
          subject: supportSubject,
          message: supportMessage,
        }),
      });
      if (!response.ok) throw new Error("support");
      const casesResponse = await fetch(`/api/v1/bookings/${booking.booking_id}/support-cases`, { credentials: "include" });
      if (!casesResponse.ok) throw new Error("support-list");
      setSupportCases(await casesResponse.json() as SupportCase[]);
      setSupportSubject(""); setSupportMessage("");
    } catch { setError("error"); }
    finally { setWorking(false); }
  }

  async function revokeBookingAccess() {
    if (!booking) return;
    setWorking(true); setError("");
    try {
      const response = await fetch(apiUrl(`/api/v1/bookings/${booking.booking_id}/access/revoke`), {
        method: "POST", credentials: "include",
        headers: { "X-CSRF-Token": csrfCookie() },
      });
      if (!response.ok) throw new Error("revoke");
      sessionStorage.removeItem("mnm_active_booking_id");
      setBooking(null); setReservation(null); setHold(null); setChallengeId(""); setSupportCases([]);
      setSyntheticCode(""); setVerificationCode("");
    } catch { setError("error"); }
    finally { setWorking(false); }
  }

  return (
    <main className="page" lang={language}>
      <a className="skip-link" href="#hero-title">{t.skip}</a>
      <header className="topbar">
        <a className="brand" href="#hero-title" aria-label="MaaleNex Moto home">
          <span className="brand-mark" aria-hidden="true">M</span> MAALE NEX MOTO
        </a>
        <div className="top-actions">
          <span className="environment">{t.status}</span>
          <button className="language" type="button" aria-label={t.language}
            onClick={() => setLanguage(language === "am" ? "en" : "am")}>{language === "am" ? "EN" : "አማ"}</button>
        </div>
      </header>

      <section className="hero" aria-labelledby="hero-title">
        <p className="eyebrow">{t.eyebrow}</p>
        <h1 id="hero-title">{t.title}</h1>
        <p className="subtitle">{t.subtitle}</p>

        <form id="trip-search" className="search-panel" onSubmit={searchTrips}>
          <label><span>{t.from}</span><select value={originId} onChange={(e) => setOriginId(e.target.value)} required>
            <option value="">{t.choose}</option>{locations.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
          </select></label>
          <label><span>{t.to}</span><select value={destinationId} onChange={(e) => setDestinationId(e.target.value)} required>
            <option value="">{t.choose}</option>{destinations.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
          </select></label>
          <label><span>{t.date}</span><input type="date" min={localDate()} value={travelDate} onChange={(e) => setTravelDate(e.target.value)} required /></label>
          <label><span>{t.count}</span><input type="number" min="1" max="10" value={passengerCount}
            onChange={(e) => { const n = Number(e.target.value); setPassengerCount(n); setPassengerNames((names) => Array.from({ length: n }, (_, i) => names[i] ?? "")); }} required /></label>
          <button className="search-button" type="submit" disabled={searching || loadingLocations || !originId || !destinationId}>{searching ? t.loading : t.search}</button>
        </form>

        {loadingLocations && <p className="notice">{t.loadingLocations}</p>}
        {!loadingLocations && locations.length === 0 && <p className="notice">{t.emptyLocations}</p>}
        {error && <p className="error" role="alert">{t.error}</p>}

        {searched && <section className="results" aria-live="polite">
          <h2>{t.results}</h2>
          {!searching && trips.length === 0 && !error && <p className="notice">{t.noResults}</p>}
          <div className="trip-list">{trips.map((trip) => (
            <article className="trip-card" key={trip.id}>
              <div className="trip-topline"><span className="trip-tag">{t.reservation}</span>
                <strong>{new Intl.NumberFormat(language === "am" ? "am-ET" : "en-ET", { style: "currency", currency: "ETB" }).format(trip.fare.amount_minor_units / 100)}</strong>
              </div>
              <p className="trip-time">{new Date(trip.departure_at).toLocaleString(language === "am" ? "am-ET" : "en-ET")}</p>
              <p className="trip-meta">{t.terminal}: {trip.boarding_model} · {t.seats}: {trip.available_seats}</p>
              <p className="trip-warning">{t.disabled}</p>
              <button className="secondary-button" type="button" onClick={() => chooseTrip(trip)}>{t.selectSeats}</button>
            </article>
          ))}</div>
        </section>}

        {selectedTrip && <section className="booking-panel">
          <h2>{t.selectSeats}</h2>
          {loadingSeats ? <p className="notice">{t.loading}</p> : <div className="seat-grid">
            {seats.map((seat) => <button key={seat.trip_seat_id} type="button"
              className={`seat-button ${selectedSeatIds.includes(seat.trip_seat_id) ? "selected" : ""}`}
              disabled={!seat.available}
              aria-pressed={selectedSeatIds.includes(seat.trip_seat_id)}
              onClick={() => toggleSeat(seat.trip_seat_id)}>{seat.seat_code}</button>)}
          </div>}
          <p className="trip-meta">{t.selected}: {selectedSeatIds.length} / {passengerCount}</p>
          <form className="details-form" onSubmit={createHold}>
            <h3>{t.contact}</h3>
            <label><span>{t.contactName}</span><input value={contactName} onChange={(e) => setContactName(e.target.value)} required maxLength={160} /></label>
            <label><span>{t.phone}</span><input type="tel" value={contactPhone} onChange={(e) => setContactPhone(e.target.value)} required maxLength={32} /></label>
            {passengerNames.map((name, index) => <label key={index}><span>{t.traveler} {index + 1}</span>
              <input value={name} onChange={(e) => setPassengerNames((current) => current.map((value, i) => i === index ? e.target.value : value))} required maxLength={160} /></label>)}
            <p className="notice">{t.holdNote}</p>
            <button className="search-button" type="submit" disabled={working || loadingSeats || Boolean(hold) || selectedSeatIds.length !== passengerCount}>{working ? t.loading : t.createHold}</button>
          </form>
        </section>}

        {hold && <section className="booking-panel">
          <h2>{t.holdCreated}</h2>
          <p><strong>{t.bookingRef}:</strong> {hold.booking_reference}</p>
          <p><strong>{t.expires}:</strong> {new Date(hold.hold_expires_at).toLocaleString(language === "am" ? "am-ET" : "en-ET")}</p>
          {!challengeId && <button className="search-button" type="button" disabled={working} onClick={requestChallenge}>{t.verifyContact}</button>}
          {challengeId && <form className="details-form" onSubmit={verifyChallenge}>
            <h3>{t.challenge}</h3>
            {syntheticCode && <p className="notice">{t.syntheticCode}: <strong>{syntheticCode}</strong></p>}
            <label><span>{t.code}</span><input value={verificationCode} onChange={(e) => setVerificationCode(e.target.value)} inputMode="numeric" pattern="[0-9]{6}" maxLength={6} required /></label>
            <button className="search-button" type="submit" disabled={working || verificationCode.length !== 6}>{t.verify}</button>
          </form>}
        </section>}

        {booking && !reservation && <section className="booking-panel">
          <h2>{t.reservation}</h2>
          <p><strong>{t.bookingRef}:</strong> {booking.booking_reference}</p>
          <ul>{booking.passengers.map((p, i) => <li key={i}>{p.name} · {p.seat}</li>)}</ul>
          <p className="trip-warning">{t.notTicket}</p>
          <button className="search-button" type="button" disabled={working || booking.status !== "held"} onClick={confirmReservation}>{t.reserve}</button>
        </section>}

        {reservation && <section className="booking-panel">
          <h2>{t.reservation}</h2>
          <p><strong>{t.reservationRef}:</strong> {reservation.reservation_reference}</p>
          <p><strong>{t.qrRef}:</strong> <code>{reservation.qr_payload_reference}</code></p>
          {booking && <img
            src={apiUrl(`/api/v1/bookings/${booking.booking_id}/reservation/qr.svg`)}
            alt={t.qrCode}
            width={180}
            height={180}
            loading="lazy"
          />}
          <p className="trip-warning">{t.notTicket}</p>
          <p className="trip-warning">{t.disabled}</p>
          <button className="secondary-button" type="button" disabled={working} onClick={revokeBookingAccess}>{t.revokeAccess}</button>
        </section>}
        {booking && !reservation && <button className="secondary-button" type="button" disabled={working} onClick={revokeBookingAccess}>{t.revokeAccess}</button>}
        {booking && <section className="booking-panel" aria-labelledby="support-title">
          <h2 id="support-title">{t.support}</h2>
          <form className="details-form" onSubmit={submitSupportCase}>
            <label><span>{t.supportSubject}</span><input value={supportSubject} onChange={(e) => setSupportSubject(e.target.value)} required maxLength={160} /></label>
            <label><span>{t.supportMessage}</span><textarea value={supportMessage} onChange={(e) => setSupportMessage(e.target.value)} required minLength={10} maxLength={2000} rows={4} /></label>
            <button className="secondary-button" type="submit" disabled={working || !supportSubject.trim() || supportMessage.trim().length < 10}>{t.supportSubmit}</button>
          </form>
          {supportCases.length > 0 && <div className="support-list">
            <h3>{t.supportCases}</h3>
            <ul>{supportCases.map((item) => <li key={item.case_reference}>
              <strong>{item.case_reference}</strong> · {item.subject} · {item.status}
              {item.resolution_note && <p>{item.resolution_note}</p>}
            </li>)}</ul>
          </div>}
        </section>}
      </section>

      <footer><span>{t.footer}</span><span>© MaaleNex Moto · 2026</span></footer>
    </main>
  );
}
