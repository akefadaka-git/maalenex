import { useState } from "react";
import { Badge, Button, Card } from "./components/ui";

type Language = "am" | "en";
type Role = "passenger" | "motorcycle_driver" | "heavy_load_driver" | "fleet_operator";

const copy = {
  en: {
    demo: "Illustrative interface only. These controls do not create bookings, dispatch trips, change driver availability on a server or modify operational records.",
    passengerTitle: "Passenger journey workspace",
    pickup: "Pickup area", destination: "Destination area", choose: "Choose an area",
    koybe: "Koybe", jinka: "Jinka", maale: "Maale Woreda",
    previewRide: "Open ride planner preview", savedPlaces: "Saved places",
    savedPlacesText: "Saved addresses will appear here after secure account and location services are implemented.",
    safety: "Safety and support", safetyText: "Emergency contacts and support channels will be published after verification.",
    driverTitle: "Driver operations workspace", availability: "Availability",
    available: "Available (preview)", unavailable: "Unavailable (preview)",
    toggleAvailable: "Toggle preview availability", incoming: "Sample trip offers",
    offerOne: "Koybe → Jinka", offerTwo: "Maale Woreda → Koybe",
    accept: "Preview accept", decline: "Preview decline", offerStatus: "Preview status",
    cargoTitle: "Heavy-load operations", cargoCapacity: "Vehicle capacity",
    cargoOffers: "Sample cargo requests", loadOne: "Local goods · Koybe to Jinka",
    loadTwo: "Building materials · Jinka area", delivery: "Delivery history",
    fleetTitle: "Fleet operations workspace", vehicles: "Vehicle register",
    drivers: "Driver roster", assignment: "Assignment status",
    sample: "Synthetic sample", status: "Status", noLive: "Not connected",
    adminTitle: "Administration review workspace", restricted: "Read-only demonstration",
    approvals: "Illustrative review queue", audit: "Sample audit events",
    record: "Sample record", category: "Category", action: "Review state",
    pending: "Pending verification", created: "Prototype event", reviewed: "No action available",
    metrics: "Operational metrics", metricsText: "Live counts and financial figures are intentionally not shown until trusted data sources and authorization are connected."
  },
  am: {
    demo: "የምሳሌ በይነገጽ ብቻ ነው። እነዚህ ቁጥጥሮች ትክክለኛ ቦታ ማስያዝ፣ ጉዞ ማስተላለፍ ወይም የአሠራር መዝገብ መቀየር አያደርጉም።",
    passengerTitle: "የተሳፋሪ ጉዞ ማዕከል",
    pickup: "መነሻ አካባቢ", destination: "መድረሻ አካባቢ", choose: "አካባቢ ይምረጡ",
    koybe: "ኮይቤ", jinka: "ጂንካ", maale: "ማአሌ ወረዳ",
    previewRide: "የጉዞ ቅድመ እይታ ክፈት", savedPlaces: "የተቀመጡ ቦታዎች",
    savedPlacesText: "የተቀመጡ አድራሻዎች ደህንነቱ የተጠበቀ መለያና የቦታ አገልግሎት ከተገነቡ በኋላ ይታያሉ።",
    safety: "ደህንነትና ድጋፍ", safetyText: "የአደጋ ጊዜ እና የድጋፍ መረጃ ከተረጋገጠ በኋላ ይታያል።",
    driverTitle: "የሹፌር አሠራር ማዕከል", availability: "የመገኘት ሁኔታ",
    available: "ዝግጁ (ቅድመ እይታ)", unavailable: "ዝግጁ አይደለም (ቅድመ እይታ)",
    toggleAvailable: "የቅድመ እይታ ሁኔታ ቀይር", incoming: "የምሳሌ የጉዞ ጥያቄዎች",
    offerOne: "ኮይቤ → ጂንካ", offerTwo: "ማአሌ ወረዳ → ኮይቤ",
    accept: "በምሳሌ ተቀበል", decline: "በምሳሌ አትቀበል", offerStatus: "የቅድመ እይታ ሁኔታ",
    cargoTitle: "የከባድ ጭነት አሠራር", cargoCapacity: "የተሽከርካሪ ጭነት አቅም",
    cargoOffers: "የምሳሌ የጭነት ጥያቄዎች", loadOne: "አካባቢያዊ ዕቃዎች · ኮይቤ ወደ ጂንካ",
    loadTwo: "የግንባታ ዕቃዎች · ጂንካ አካባቢ", delivery: "የማድረሻ ታሪክ",
    fleetTitle: "የተሽከርካሪ አስተዳደር ማዕከል", vehicles: "የተሽከርካሪ መዝገብ",
    drivers: "የሹፌር ዝርዝር", assignment: "የምደባ ሁኔታ",
    sample: "የምሳሌ መረጃ", status: "ሁኔታ", noLive: "አልተገናኘም",
    adminTitle: "የአስተዳደር ግምገማ ማዕከል", restricted: "ለማንበብ ብቻ የተዘጋጀ ሙከራ",
    approvals: "የምሳሌ የማረጋገጫ ዝርዝር", audit: "የምሳሌ የክስተት መዝገብ",
    record: "የምሳሌ መዝገብ", category: "ምድብ", action: "የግምገማ ሁኔታ",
    pending: "ማረጋገጫ ይጠብቃል", created: "የሙከራ ክስተት", reviewed: "ምንም እርምጃ የለም",
    metrics: "የአሠራር መለኪያዎች", metricsText: "የታመኑ የመረጃ ምንጮችና ፈቃዶች እስኪገናኙ ድረስ ቀጥታ ቁጥሮችና የገንዘብ መረጃ አይታይም።"
  }
} as const;

function Notice({ children }: { children: string }) {
  return <p className="mn-workspace-notice" role="note">{children}</p>;
}

function PassengerWorkspace({ language, onRidePreview }: { language: Language; onRidePreview: (pickup?: string, destination?: string) => void }) {
  const t = copy[language];
  const [pickup, setPickup] = useState("koybe");
  const [destination, setDestination] = useState("jinka");
  return <section className="mn-workspace" aria-labelledby="mn-passenger-workspace">
    <h2 id="mn-passenger-workspace">{t.passengerTitle}</h2>
    <Card className="mn-workspace-card">
      <div className="mn-workspace-fields">
        <label>{t.pickup}<select className="mn-field" value={pickup} onChange={e => setPickup(e.target.value)}>
          <option value="koybe">{t.koybe}</option><option value="jinka">{t.jinka}</option><option value="maale">{t.maale}</option>
        </select></label>
        <label>{t.destination}<select className="mn-field" value={destination} onChange={e => setDestination(e.target.value)}>
          <option value="koybe">{t.koybe}</option><option value="jinka">{t.jinka}</option><option value="maale">{t.maale}</option>
        </select></label>
      </div>
      <Button onClick={() => onRidePreview(pickup, destination)} disabled={pickup === destination}>{t.previewRide}</Button>
    </Card>
    <div className="mn-workspace-grid">
      <Card><h3>{t.savedPlaces}</h3><p>{t.savedPlacesText}</p><Badge tone="warning">{t.noLive}</Badge></Card>
      <Card><h3>{t.safety}</h3><p>{t.safetyText}</p><Badge tone="warning">{t.noLive}</Badge></Card>
    </div>
    <Notice>{t.demo}</Notice>
  </section>;
}

function DriverWorkspace({ language, cargo = false }: { language: Language; cargo?: boolean }) {
  const t = copy[language];
  const [available, setAvailable] = useState(false);
  const [offerStates, setOfferStates] = useState<Record<string, string>>({});
  const title = cargo ? t.cargoTitle : t.driverTitle;
  const offers = cargo ? [t.loadOne, t.loadTwo] : [t.offerOne, t.offerTwo];
  return <section className="mn-workspace" aria-labelledby="mn-driver-workspace">
    <h2 id="mn-driver-workspace">{title}</h2>
    <Card className="mn-workspace-card">
      <div className="mn-workspace-heading"><div><h3>{t.availability}</h3><p>{cargo ? t.cargoCapacity : t.availability}</p></div>
        <Badge tone={available ? "success" : "warning"}>{available ? t.available : t.unavailable}</Badge>
      </div>
      <Button variant="secondary" onClick={() => setAvailable(v => !v)}>{t.toggleAvailable}</Button>
    </Card>
    <h3>{cargo ? t.cargoOffers : t.incoming}</h3>
    <div className="mn-workspace-grid">{offers.map((offer, index) => <Card key={offer}>
      <h3>{offer}</h3><Badge tone="info">{t.sample}</Badge>
      <p>{t.offerStatus}: {offerStates[String(index)] || t.noLive}</p>
      <div className="mn-workspace-actions">
        <Button size="small" disabled={!available} onClick={() => setOfferStates(s => ({ ...s, [index]: t.accept }))}>{t.accept}</Button>
        <Button size="small" variant="secondary" onClick={() => setOfferStates(s => ({ ...s, [index]: t.decline }))}>{t.decline}</Button>
      </div>
    </Card>)}</div>
    {cargo && <Card><h3>{t.delivery}</h3><Badge tone="warning">{t.noLive}</Badge></Card>}
    <Notice>{t.demo}</Notice>
  </section>;
}

function FleetWorkspace({ language }: { language: Language }) {
  const t = copy[language];
  return <section className="mn-workspace" aria-labelledby="mn-fleet-workspace">
    <h2 id="mn-fleet-workspace">{t.fleetTitle}</h2>
    <div className="mn-workspace-grid">
      <Card><h3>{t.vehicles}</h3><div className="mn-table-wrap"><table className="mn-data-table">
        <thead><tr><th>{t.record}</th><th>{t.category}</th><th>{t.status}</th></tr></thead>
        <tbody><tr><td>MN-DEMO-01</td><td>Motorcycle</td><td><Badge tone="warning">{t.noLive}</Badge></td></tr><tr><td>MN-DEMO-02</td><td>Heavy-load</td><td><Badge tone="warning">{t.noLive}</Badge></td></tr></tbody>
      </table></div></Card>
      <Card><h3>{t.drivers}</h3><div className="mn-table-wrap"><table className="mn-data-table">
        <thead><tr><th>{t.record}</th><th>{t.category}</th><th>{t.status}</th></tr></thead>
        <tbody><tr><td>Demo driver A</td><td>Motorcycle</td><td><Badge tone="warning">{t.noLive}</Badge></td></tr><tr><td>Demo driver B</td><td>Heavy-load</td><td><Badge tone="warning">{t.noLive}</Badge></td></tr></tbody>
      </table></div></Card>
    </div>
    <Card><h3>{t.assignment}</h3><Badge tone="warning">{t.noLive}</Badge></Card>
    <Notice>{t.demo}</Notice>
  </section>;
}

export function RoleWorkspace({ role, language, onRidePreview }: { role: Role; language: Language; onRidePreview: (pickup?: string, destination?: string) => void }) {
  if (role === "passenger") return <PassengerWorkspace language={language} onRidePreview={onRidePreview} />;
  if (role === "motorcycle_driver") return <DriverWorkspace language={language} />;
  if (role === "heavy_load_driver") return <DriverWorkspace language={language} cargo />;
  return <FleetWorkspace language={language} />;
}

export function AdminWorkspace({ language }: { language: Language }) {
  const t = copy[language];
  return <section className="mn-workspace" aria-labelledby="mn-admin-workspace">
    <div className="mn-workspace-heading"><h2 id="mn-admin-workspace">{t.adminTitle}</h2><Badge tone="danger">{t.restricted}</Badge></div>
    <Card><h3>{t.approvals}</h3><div className="mn-table-wrap"><table className="mn-data-table">
      <thead><tr><th>{t.record}</th><th>{t.category}</th><th>{t.action}</th></tr></thead>
      <tbody><tr><td>DEMO-APPLICATION-01</td><td>Driver</td><td><Badge tone="warning">{t.pending}</Badge></td></tr><tr><td>DEMO-FLEET-02</td><td>Fleet</td><td><Badge tone="warning">{t.pending}</Badge></td></tr></tbody>
    </table></div></Card>
    <Card><h3>{t.audit}</h3><div className="mn-table-wrap"><table className="mn-data-table">
      <thead><tr><th>{t.record}</th><th>{t.category}</th><th>{t.action}</th></tr></thead>
      <tbody><tr><td>DEMO-EVENT-001</td><td>{t.created}</td><td>{t.reviewed}</td></tr></tbody>
    </table></div></Card>
    <Card><h3>{t.metrics}</h3><p>{t.metricsText}</p></Card>
    <Notice>{t.demo}</Notice>
  </section>;
}
