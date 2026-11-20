import { useEffect, useState, type FormEvent } from "react";
import {
  acceptGuestReservation,
  createBookingHold,
  getGuestBooking,
  listTripSeats,
  requestBookingChallenge,
  verifyBookingChallenge,
  type BookingChallenge,
  type BookingDetails,
  type PassengerSeat,
  type PassengerTrip,
} from "./passenger-api";

type Props = {
  trip: PassengerTrip;
  passengerCount: number;
  language: "am" | "en";
  onClose: () => void;
};

type Stage = "seats" | "verify" | "review" | "done";

export function BookingFlow({ trip, passengerCount, language, onClose }: Props) {
  const am = language === "am";
  const [stage, setStage] = useState<Stage>("seats");
  const [seats, setSeats] = useState<PassengerSeat[]>([]);
  const [selectedSeats, setSelectedSeats] = useState<string[]>([]);
  const [contactName, setContactName] = useState("");
  const [contactPhone, setContactPhone] = useState("+251");
  const [passengerNames, setPassengerNames] = useState<string[]>(Array.from({ length: passengerCount }, () => ""));
  const [hold, setHold] = useState<Awaited<ReturnType<typeof createBookingHold>> | null>(null);
  const [challenge, setChallenge] = useState<BookingChallenge | null>(null);
  const [verificationCode, setVerificationCode] = useState("");
  const [booking, setBooking] = useState<BookingDetails | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    listTripSeats(trip.id).then(items => {
      if (active) setSeats(items);
    }).catch(reason => {
      if (active) setError(reason instanceof Error ? reason.message : "Unable to load seat availability.");
    });
    return () => { active = false; };
  }, [trip.id]);

  const toggleSeat = (seatId: string) => {
    setSelectedSeats(current => current.includes(seatId)
      ? current.filter(id => id !== seatId)
      : current.length < passengerCount ? [...current, seatId] : current);
  };

  const createHold = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    if (selectedSeats.length !== passengerCount) {
      setError(am ? "ለእያንዳንዱ ተሳፋሪ አንድ መቀመጫ ይምረጡ።" : "Select exactly one seat for each passenger.");
      return;
    }
    if (passengerNames.some(name => !name.trim())) {
      setError(am ? "የእያንዳንዱን ተሳፋሪ ስም ያስገቡ።" : "Enter the name of every passenger.");
      return;
    }
    setBusy(true);
    try {
      const idempotencyKey = crypto.randomUUID();
      const created = await createBookingHold({
        trip_id: trip.id,
        booking_contact_name: contactName.trim(),
        booking_contact_phone: contactPhone.trim(),
        passengers: passengerNames.map(name => ({ name: name.trim() })),
        seat_ids: selectedSeats,
      }, idempotencyKey);
      setHold(created);
      setStage("verify");
      const challengeResponse = await requestBookingChallenge(created.booking_reference, contactPhone.trim());
      setChallenge(challengeResponse);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to create a reservation hold.");
    } finally {
      setBusy(false);
    }
  };

  const verify = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!challenge) return;
    setBusy(true);
    setError("");
    try {
      const verified = await verifyBookingChallenge(challenge.challenge_id, verificationCode.trim());
      const details = await getGuestBooking(verified.booking_id);
      setBooking(details);
      setStage("review");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Booking verification failed.");
    } finally {
      setBusy(false);
    }
  };

  const confirmReservation = async () => {
    if (!booking) return;
    setBusy(true);
    setError("");
    try {
      await acceptGuestReservation(booking.booking_id);
      setBooking(await getGuestBooking(booking.booking_id));
      setStage("done");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to confirm this reservation.");
    } finally {
      setBusy(false);
    }
  };

  const money = (minor: number) => new Intl.NumberFormat(am ? "am-ET" : "en-ET", {
    style: "currency", currency: "ETB",
  }).format(minor / 100);

  return (
    <section className="form-card booking-flow" aria-live="polite">
      <div className="section-heading">
        <h2>{am ? "የቦታ ማስያዣ" : "Reserve seats"}</h2>
        <button type="button" className="text-link" onClick={onClose}>{am ? "ዝጋ" : "Close"}</button>
      </div>
      <p>{new Intl.DateTimeFormat(am ? "am-ET" : "en-ET", {
        dateStyle: "medium", timeStyle: "short", timeZone: "Africa/Addis_Ababa",
      }).format(new Date(trip.departure_at))}</p>
      {stage === "seats" && (
        <form onSubmit={createHold}>
          <h3>{am ? "መቀመጫዎችን ይምረጡ" : "Choose available seats"}</h3>
          {seats.length === 0 && <p>{am ? "የሚገኝ መቀመጫ መረጃ የለም።" : "No seat inventory is currently available."}</p>}
          <div className="seat-grid">
            {seats.map(seat => (
              <label className={seat.available ? "seat-option" : "seat-option seat-unavailable"} key={seat.trip_seat_id}>
                <input
                  type="checkbox"
                  disabled={!seat.available || (selectedSeats.length >= passengerCount && !selectedSeats.includes(seat.trip_seat_id))}
                  checked={selectedSeats.includes(seat.trip_seat_id)}
                  onChange={() => toggleSeat(seat.trip_seat_id)}
                />
                <span>{seat.seat_code}</span>
              </label>
            ))}
          </div>
          <p>{am ? "የተመረጡ መቀመጫዎች" : "Selected seats"}: {selectedSeats.length}/{passengerCount}</p>
          <label>{am ? "የተጠያቂ ስም" : "Booking contact name"}
            <input required minLength={2} maxLength={160} value={contactName} onChange={e => setContactName(e.target.value)} />
          </label>
          <label>{am ? "የስልክ ቁጥር" : "Contact phone"}
            <input required minLength={8} maxLength={32} inputMode="tel" value={contactPhone} onChange={e => setContactPhone(e.target.value)} />
          </label>
          <h3>{am ? "የተሳፋሪዎች ስም" : "Passenger names"}</h3>
          {passengerNames.map((name, index) => (
            <label key={index}>{am ? `ተሳፋሪ ${index + 1}` : `Passenger ${index + 1}`}
              <input required minLength={2} maxLength={160} value={name} onChange={e => setPassengerNames(current => current.map((item, i) => i === index ? e.target.value : item))} />
            </label>
          ))}
          <button className="primary-action" type="submit" disabled={busy || seats.length === 0}>
            {busy ? (am ? "በመስራት ላይ…" : "Working…") : (am ? "መቀመጫ ያስይዙ" : "Hold selected seats")}
          </button>
        </form>
      )}
      {stage === "verify" && hold && (
        <div>
          <h3>{am ? "የቦታ ማስያዣ ማረጋገጫ" : "Verify booking contact"}</h3>
          {!challenge && (
            <button type="button" className="primary-action" disabled={busy} onClick={async()=>{
              setBusy(true);setError("");
              try{setChallenge(await requestBookingChallenge(hold.booking_reference,contactPhone.trim()));}
              catch(reason){setError(reason instanceof Error?reason.message:"Unable to request a verification challenge.");}
              finally{setBusy(false);}
            }}>{am ? "እንደገና ኮድ ጠይቅ" : "Retry verification request"}</button>
          )}
          {challenge && <form onSubmit={verify}>
          <p>{am ? "የማስያዣ ማጣቀሻ" : "Booking reference"}: <strong>{hold.booking_reference}</strong></p>
          <p>{am ? "መቀመጫዎች ለ10 ደቂቃ ተይዘዋል።" : "Seats are held for up to 10 minutes."}</p>
          {challenge?.synthetic_test_code
            ? <p className="notice-panel">{am ? "የሙከራ ኮድ (ለማሳያ አካባቢ ብቻ)" : "Synthetic test code (development/test only)"}: <strong>{challenge.synthetic_test_code}</strong></p>
            : <p className="field-hint">{am ? "የSMS ማረጋገጫ አቅራቢ ገና አልተዋቀረም።" : "SMS verification delivery is not configured in this environment. This booking cannot be verified yet."}</p>}
          <label>{am ? "የማረጋገጫ ኮድ" : "Verification code"}
            <input required minLength={6} maxLength={6} inputMode="numeric" value={verificationCode} onChange={e => setVerificationCode(e.target.value.replace(/\D/g, "").slice(0, 6))} />
          </label>
          <button className="primary-action" type="submit" disabled={busy || !challenge.synthetic_test_code}>
            {busy ? (am ? "በማረጋገጥ ላይ…" : "Verifying…") : (am ? "አረጋግጥ" : "Verify contact")}
          </button>
          </form>}
        </div>
      )}
      {(stage === "review" || stage === "done") && booking && (
        <div>
          <h3>{stage === "done" ? (am ? "ማስያዣው ተረጋግጧል" : "Reservation confirmed") : (am ? "የማስያዣ ማጠቃለያ" : "Review reservation")}</h3>
          <p>{am ? "ማጣቀሻ" : "Reference"}: <strong>{booking.booking_reference}</strong></p>
          {booking.passengers.map((person, index) => <p key={index}>{person.name} — {person.seat}</p>)}
          {booking.fare && <p>{am ? "ጠቅላላ ዋጋ" : "Total fare"}: {money(booking.fare.amount_minor_units)}</p>}
          {stage === "review" && <button className="primary-action" onClick={confirmReservation} disabled={busy}>{busy ? (am ? "በማረጋገጥ ላይ…" : "Confirming…") : (am ? "ማስያዣን አረጋግጥ" : "Confirm reservation")}</button>}
          {stage === "done" && booking.reservation && <p className="notice-panel">{am ? "የተረጋገጠ ማስያዣ ቁጥር" : "Reservation reference"}: <strong>{booking.reservation.reservation_reference}</strong></p>}
          <p className="field-hint">{am ? "ክፍያ አልተፈጸመም፤ የጉዞ ትኬት አልተሰጠም።" : "No payment was collected and no travel ticket was issued."}</p>
        </div>
      )}
      {error && <p className="notice-panel" role="alert">{error}</p>}
    </section>
  );
}
