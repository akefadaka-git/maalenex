import { useEffect, useMemo, useState } from "react";

type Language = "am" | "en";
type LocationOption = { id: string; name: string; type: string };
type TripResult = {
  id: string;
  departure_at: string;
  arrival_estimate_at: string | null;
  boarding_model: string;
  available_seats: number;
  availability_as_of: string;
  fare: { amount_minor_units: number; currency_code: "ETB" };
  reservation_only: boolean;
  ticketing_enabled: false;
  payment_enabled: false;
};

const copy = {
  am: {
    eyebrow: "የተሳፋሪ መጓጓዣ",
    title: "ጉዞዎን ያቅዱ።",
    subtitle: "ከጂንካ የሚነሱ የታተሙ የጉዞ መርሐ ግብሮችን ይፈልጉ።",
    status: "የልማት አካባቢ · ሰው ሠራሽ መረጃ",
    from: "መነሻ",
    to: "መድረሻ",
    date: "የጉዞ ቀን",
    count: "ተሳፋሪዎች",
    search: "ጉዞ ፈልግ",
    loading: "በመፈለግ ላይ…",
    results: "የተገኙ ጉዞዎች",
    noResults: "ለዚህ ፍለጋ የታተመ ጉዞ አልተገኘም።",
    choose: "ይምረጡ",
    seats: "ባዶ ወንበሮች",
    departure: "መነሻ ሰዓት",
    fare: "የአንድ ተሳፋሪ ዋጋ",
    terminal: "መነሻ ቦታ",
    reservation: "የቦታ ማስያዣ ብቻ",
    disabled: "ክፍያና የጉዞ ትኬት አልተከፈቱም።",
    loadingLocations: "የመነሻና መድረሻ ቦታዎች በመጫን ላይ…",
    error: "የጉዞ መረጃን ማግኘት አልተቻለም። እንደገና ይሞክሩ።",
    emptyLocations: "ለሙከራ የታተሙ ቦታዎች ገና የሉም።",
    language: "Switch language to English",
    footer: "በሙከራ ላይ ያለ መድረክ። እውነተኛ ቦታ ማስያዝ፣ ክፍያ ወይም መሳፈር አይፈቀድም።",
  },
  en: {
    eyebrow: "PASSENGER MOBILITY",
    title: "Plan your journey.",
    subtitle: "Search published passenger schedules originating from Jinka.",
    status: "Development environment · Synthetic data",
    from: "From",
    to: "To",
    date: "Travel date",
    count: "Passengers",
    search: "Search trips",
    loading: "Searching…",
    results: "Available trips",
    noResults: "No published trips match this search.",
    choose: "Select",
    seats: "Available seats",
    departure: "Departure",
    fare: "Fare per passenger",
    terminal: "Boarding point",
    reservation: "Reservation only",
    disabled: "Payments and travel tickets are not enabled.",
    loadingLocations: "Loading origin and destination locations…",
    error: "Could not load trip information. Please try again.",
    emptyLocations: "No published locations are available in this synthetic environment yet.",
    language: "ቋንቋውን ወደ አማርኛ ቀይር",
    footer: "Development platform. Real reservations, payments and boarding are not authorized.",
  },
};

function localDate(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export default function App() {
  const [language, setLanguage] = useState<Language>("am");
  const [locations, setLocations] = useState<LocationOption[]>([]);
  const [originId, setOriginId] = useState("");
  const [destinationId, setDestinationId] = useState("");
  const [travelDate, setTravelDate] = useState(localDate);
  const [passengerCount, setPassengerCount] = useState(1);
  const [trips, setTrips] = useState<TripResult[]>([]);
  const [loadingLocations, setLoadingLocations] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState("");
  const [searched, setSearched] = useState(false);
  const t = copy[language];

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/v1/catalog/locations", { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error("locations");
        return response.json() as Promise<LocationOption[]>;
      })
      .then((items) => {
        setLocations(items);
        if (items.length > 0) setOriginId(items[0].id);
        if (items.length > 1) setDestinationId(items[1].id);
      })
      .catch((reason: unknown) => {
        if (!(reason instanceof DOMException && reason.name === "AbortError")) setError(t.error);
      })
      .finally(() => setLoadingLocations(false));
    return () => controller.abort();
  }, []);

  const destinations = useMemo(
    () => locations.filter((item) => item.id !== originId),
    [locations, originId],
  );

  async function searchTrips(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!originId || !destinationId || originId === destinationId) return;
    setSearching(true);
    setError("");
    setSearched(true);
    try {
      const params = new URLSearchParams({
        origin_id: originId,
        destination_id: destinationId,
        travel_date: travelDate,
        passenger_count: String(passengerCount),
      });
      const response = await fetch(`/api/v1/trips/search?${params.toString()}`);
      if (!response.ok) throw new Error("search");
      setTrips((await response.json()) as TripResult[]);
    } catch {
      setTrips([]);
      setError(t.error);
    } finally {
      setSearching(false);
    }
  }

  return (
    <main className="page" lang={language}>
      <header className="topbar">
        <a className="brand" href="/" aria-label="MaaleNex Moto home">
          <span className="brand-mark" aria-hidden="true">M</span>
          MAALE NEX MOTO
        </a>
        <div className="top-actions">
          <span className="environment">{t.status}</span>
          <button className="language" type="button" aria-label={t.language}
            onClick={() => setLanguage(language === "am" ? "en" : "am")}>
            {language === "am" ? "EN" : "አማ"}
          </button>
        </div>
      </header>

      <section className="hero" aria-labelledby="hero-title">
        <p className="eyebrow">{t.eyebrow}</p>
        <h1 id="hero-title">{t.title}</h1>
        <p className="subtitle">{t.subtitle}</p>

        <form className="search-panel" onSubmit={searchTrips}>
          <label>
            <span>{t.from}</span>
            <select value={originId} onChange={(event) => setOriginId(event.target.value)} required>
              <option value="">{t.choose}</option>
              {locations.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
          </label>
          <label>
            <span>{t.to}</span>
            <select value={destinationId} onChange={(event) => setDestinationId(event.target.value)} required>
              <option value="">{t.choose}</option>
              {destinations.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
          </label>
          <label>
            <span>{t.date}</span>
            <input type="date" min={localDate()} value={travelDate}
              onChange={(event) => setTravelDate(event.target.value)} required />
          </label>
          <label>
            <span>{t.count}</span>
            <input type="number" min="1" max="10" value={passengerCount}
              onChange={(event) => setPassengerCount(Number(event.target.value))} required />
          </label>
          <button className="search-button" type="submit" disabled={searching || loadingLocations || !originId || !destinationId}>
            {searching ? t.loading : t.search}
          </button>
        </form>

        {loadingLocations && <p className="notice">{t.loadingLocations}</p>}
        {!loadingLocations && locations.length === 0 && <p className="notice">{t.emptyLocations}</p>}
        {error && <p className="error" role="alert">{error}</p>}

        {searched && (
          <section className="results" aria-live="polite">
            <h2>{t.results}</h2>
            {!searching && trips.length === 0 && !error && <p className="notice">{t.noResults}</p>}
            <div className="trip-list">
              {trips.map((trip) => (
                <article className="trip-card" key={trip.id}>
                  <div className="trip-topline">
                    <span className="trip-tag">{t.reservation}</span>
                    <strong>{new Intl.NumberFormat(language === "am" ? "am-ET" : "en-ET", {
                      style: "currency", currency: "ETB",
                    }).format(trip.fare.amount_minor_units / 100)}</strong>
                  </div>
                  <p className="trip-time">{new Date(trip.departure_at).toLocaleString(language === "am" ? "am-ET" : "en-ET")}</p>
                  <p className="trip-meta">{t.terminal}: {trip.boarding_model} · {t.seats}: {trip.available_seats}</p>
                  <p className="trip-warning">{t.disabled}</p>
                </article>
              ))}
            </div>
          </section>
        )}
      </section>

      <footer>
        <span>{t.footer}</span>
        <span>© MaaleNex Moto · 2026</span>
      </footer>
    </main>
  );
}
