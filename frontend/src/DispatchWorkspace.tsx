import { useEffect, useState, type FormEvent } from "react";
import {
  approveDispatchTrip, createDispatchTrip, getOperatorDispatchOptions, getOperatorTrips,
  getPlatformDispatchTrips, getTripManifest, publishDispatchTrip, submitDispatchTrip,
  type DispatchOptions, type DispatchTrip, type TripManifest,
} from "./staff-api";

type Props = { language: "am" | "en"; organizationIds: string[]; canManage: boolean; canReview: boolean; canPublish: boolean; canManifest: boolean };

export function DispatchWorkspace({ language, organizationIds, canManage, canReview, canPublish, canManifest }: Props) {
  const am = language === "am";
  const [organizationId, setOrganizationId] = useState(organizationIds[0] ?? "");
  const [options, setOptions] = useState<DispatchOptions | null>(null);
  const [trips, setTrips] = useState<DispatchTrip[]>([]);
  const [selectedRoute, setSelectedRoute] = useState("");
  const [selectedTerminal, setSelectedTerminal] = useState("");
  const [selectedVehicle, setSelectedVehicle] = useState("");
  const [selectedLayout, setSelectedLayout] = useState("");
  const [departure, setDeparture] = useState("");
  const [arrival, setArrival] = useState("");
  const [manifest, setManifest] = useState<TripManifest | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const refresh = async () => {
    if (canReview) {
      const all = await getPlatformDispatchTrips();
      setTrips(organizationId ? all.filter(item => item.organization_id === organizationId) : all);
    } else if (canManage && organizationId) {
      setTrips(await getOperatorTrips(organizationId));
    }
    if (canManage && organizationId) setOptions(await getOperatorDispatchOptions(organizationId));
  };
  useEffect(() => {
    let active = true;
    setLoading(true); setError("");
    const load = async () => {
      if (canReview) {
        const all = await getPlatformDispatchTrips();
        if (active) setTrips(organizationId ? all.filter(item => item.organization_id === organizationId) : all);
      } else if (canManage && organizationId) {
        if (active) setTrips(await getOperatorTrips(organizationId));
      } else if (!canReview && !canManage) {
        if (active) setError("No dispatch permission is assigned.");
      }
      if (canManage && organizationId) {
        const catalog = await getOperatorDispatchOptions(organizationId);
        if (active) setOptions(catalog);
      } else if (active) setOptions(null);
    };
    void load().catch(reason => { if (active) setError(reason instanceof Error ? reason.message : "Dispatch data could not be loaded."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [organizationId, canReview, canManage]);
  const run = async (action: () => Promise<unknown>, success: string) => {
    setBusy(true); setError(""); setMessage("");
    try { await action(); await refresh(); setMessage(success); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Trip operation failed."); }
    finally { setBusy(false); }
  };
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!organizationId || !selectedRoute || !selectedTerminal || !selectedVehicle || !selectedLayout || !departure) return;
    const departureAt = new Date(departure);
    const arrivalAt = arrival ? new Date(arrival) : null;
    if (Number.isNaN(departureAt.getTime()) || (arrivalAt && (Number.isNaN(arrivalAt.getTime()) || arrivalAt <= departureAt))) {
      setError(am ? "የመነሻ እና የመድረሻ ጊዜዎችን ያረጋግጡ።" : "Check departure and arrival times.");
      return;
    }
    await run(() => createDispatchTrip(organizationId, {
      route_id: selectedRoute, boarding_terminal_id: selectedTerminal,
      vehicle_id: selectedVehicle, seat_layout_version_id: selectedLayout,
      departure_at: departureAt.toISOString(), arrival_estimate_at: arrivalAt?.toISOString() ?? null,
    }), am ? "ጉዞው እንደ ረቂቅ ተፈጥሯል።" : "Trip saved as a draft.");
    setDeparture(""); setArrival("");
  };
  const status = (value: string) => <span className={"support-status status-" + value}>{value.replaceAll("_", " ")}</span>;
  const selectedRouteRecord = options?.routes.find(item => item.id === selectedRoute);
  const selectedVehicleRecord = options?.vehicles.find(item => item.id === selectedVehicle);
  const eligibleTerminals = options?.terminals.filter(item => !selectedRouteRecord || item.location_id === selectedRouteRecord.origin_location_id) ?? [];
  const formatDate = (value: string | null) => value ? new Date(value).toLocaleString(am ? "am-ET" : "en-ET") : "—";

  return <div className="access-panel">
    <div className="staff-heading"><div><h3>{am ? "የጉዞ እና ዲስፓች አስተዳደር" : "Dispatch and trip operations"}</h3>
      <p>{am ? "የኦፕሬተር ጉዞዎችን ያቅዱ፣ ያስገቡ እና የፈቃድ ሁኔታቸውን ይከታተሉ።" : "Create operator trip drafts, submit them for platform review and track publication state."}</p></div>
      <button className="secondary-action" disabled={busy || loading} onClick={() => void refresh()}>{am ? "አድስ" : "Refresh"}</button></div>
    {canReview && <label>{am ? "የኦፕሬተር ማጣሪያ" : "Operator filter"}<select value={organizationId} onChange={event => setOrganizationId(event.target.value)}>
      <option value="">{am ? "ሁሉም ኦፕሬተሮች" : "All operators"}</option>
      {organizationIds.map(id => <option key={id} value={id}>{id}</option>)}
    </select></label>}
    {error && <p className="support-error" role="alert">{error}</p>}
    {message && <p className="notice-panel" role="status">{message}</p>}
    {canManage && organizationIds.length > 0 && organizationId && <section className="staff-module">
      <h4>{am ? "አዲስ ጉዞ ይፍጠሩ" : "Create trip draft"}</h4>
      {!options?.routes.length && <p>{am ? "የታተሙ መስመሮች አልተገኙም።" : "No published routes are available for trip creation."}</p>}
      <form className="role-assignment-form" onSubmit={submit}>
        <label>{am ? "መስመር" : "Route"}<select required value={selectedRoute} onChange={event => { setSelectedRoute(event.target.value); setSelectedTerminal(""); }}><option value="">{am ? "መስመር ይምረጡ" : "Select route"}</option>{options?.routes.map(item => <option key={item.id} value={item.id}>{item.code}</option>)}</select></label>
        <label>{am ? "የመሳፈሪያ ተርሚናል" : "Boarding terminal"}<select required value={selectedTerminal} onChange={event => setSelectedTerminal(event.target.value)}><option value="">{am ? "ተርሚናል ይምረጡ" : "Select terminal"}</option>{eligibleTerminals.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
        <label>{am ? "ተሽከርካሪ" : "Approved vehicle"}<select required value={selectedVehicle} onChange={event => { setSelectedVehicle(event.target.value); setSelectedLayout(""); }}><option value="">{am ? "ተሽከርካሪ ይምረጡ" : "Select vehicle"}</option>{options?.vehicles.map(item => <option key={item.id} value={item.id}>{item.vehicle_reference}</option>)}</select></label>
        <label>{am ? "የተፈቀደ የመቀመጫ አቀማመጥ" : "Approved seat layout"}<select required value={selectedLayout} onChange={event => setSelectedLayout(event.target.value)}><option value="">{am ? "አቀማመጥ ይምረጡ" : "Select layout"}</option>{selectedVehicleRecord?.seat_layouts.map(item => <option key={item.id} value={item.id}>v{item.version_number} · {item.seat_count} seats</option>)}</select></label>
        <label>{am ? "የመነሻ ቀን እና ሰዓት" : "Departure date and time"}<input type="datetime-local" required value={departure} onChange={event => setDeparture(event.target.value)} /></label>
        <label>{am ? "የመድረሻ ግምት (አማራጭ)" : "Estimated arrival (optional)"}<input type="datetime-local" value={arrival} onChange={event => setArrival(event.target.value)} /></label>
        <button className="primary-action" disabled={busy || !selectedRoute || !selectedTerminal || !selectedVehicle || !selectedLayout}>{am ? "ጉዞ ረቂቅ አስቀምጥ" : "Save trip draft"}</button>
      </form>
    </section>}
    {loading ? <p role="status">{am ? "በመጫን ላይ…" : "Loading trips…"}</p> : <>
      <div className="staff-stat-grid">
        <div className="staff-stat"><small>{am ? "ጉዞዎች" : "Trips"}</small><strong>{trips.length}</strong></div>
        <div className="staff-stat"><small>{am ? "ረቂቆች" : "Drafts"}</small><strong>{trips.filter(item => item.status === "draft").length}</strong></div>
        <div className="staff-stat"><small>{am ? "ግምገማ የሚጠብቁ" : "Awaiting review"}</small><strong>{trips.filter(item => item.status === "submitted").length}</strong></div>
        <div className="staff-stat"><small>{am ? "የታተሙ" : "Published"}</small><strong>{trips.filter(item => item.status === "published").length}</strong></div>
      </div>
      <h4>{am ? "የጉዞ ዝርዝር" : "Trip register"}</h4>
      {trips.map(trip => <article className="staff-module" key={trip.id}>
        <div className="staff-user-row"><div><strong>{trip.route_code} · {trip.vehicle_reference}</strong><small>{trip.organization_name} · {trip.boarding_terminal_name}</small><small>{formatDate(trip.departure_at)} · {trip.seat_count} seats</small></div>{status(trip.status)}
          {canManage && organizationIds.includes(trip.organization_id) && trip.status === "draft" && <button className="text-link" disabled={busy} onClick={() => void run(() => submitDispatchTrip(trip.id), am ? "ጉዞው ለግምገማ ተልኳል።" : "Trip submitted for review.")}>{am ? "ለግምገማ ላክ" : "Submit"}</button>}
          {canReview && trip.status === "submitted" && <button className="text-link" disabled={busy} onClick={() => void run(() => approveDispatchTrip(trip.id), am ? "ጉዞው ጸድቋል።" : "Trip approved.")}>{am ? "አጽድቅ" : "Approve"}</button>}
          {canPublish && trip.status === "approved" && <button className="text-link" disabled={busy} onClick={() => void run(() => publishDispatchTrip(trip.id), am ? "ጉዞው ታትሟል።" : "Trip published.")}>{am ? "አትም" : "Publish"}</button>}
          {canManifest && organizationIds.includes(trip.organization_id) && <button className="text-link" disabled={busy} onClick={() => void getTripManifest(trip.id).then(setManifest).catch(reason => setError(reason instanceof Error ? reason.message : "Manifest unavailable."))}>{am ? "የተሳፋሪ ዝርዝር" : "Manifest"}</button>}
        </div>
        {manifest?.trip_id === trip.id && <div className="notice-panel"><strong>{am ? "የተያዙ ቦታዎች" : "Reserved passenger manifest"} · {manifest.passenger_count}</strong>
          {manifest.manifest.map(item => <p key={item.booking_reference + item.sequence}>{item.seat_code} · {item.passenger_name} · {item.booking_reference}</p>)}
          <small>{am ? "የስልክ ቁጥር አልተካተተም። መሳፈር አልተፈቀደም።" : "Contact phone is excluded. Manifest access does not authorize boarding."}</small>
          <button className="text-link" onClick={() => setManifest(null)}>{am ? "ዝጋ" : "Close"}</button>
        </div>}
      </article>)}
    </>}
    <p className="compliance-note">{am ? "የጉዞ ማተም የታተመ ETB ዋጋ ይፈልጋል። የጉዞ ማተም ብቻውን ትኬት ወይም የመሳፈር ፈቃድ አያነቃም።" : "Trip publication requires an effective published ETB fare. Publishing a trip does not issue tickets or authorize boarding."}</p>
  </div>;
}
