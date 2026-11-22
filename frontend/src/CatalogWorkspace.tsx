import { useEffect, useState, type FormEvent } from "react";
import {
  archiveCatalogRecord, createCatalogLocation, createCatalogRoute, createCatalogTerminal,
  getCatalogSnapshot, publishCatalogLocation, publishCatalogRoute, publishCatalogTerminal,
  replaceCatalogRouteStops, updateCatalogLocation, updateCatalogRoute, updateCatalogTerminal,
  type CatalogRoute, type CatalogRouteStop, type CatalogSnapshot,
} from "./staff-api";

type Props = { language: "am" | "en"; canPublish: boolean };
type EditKind = "location" | "terminal" | "route";
type StopDraft = { location_id: string; boarding_allowed: boolean; alighting_allowed: boolean };

function RouteStopEditor({ route, locations, busy, language, onSave }: {
  route: CatalogRoute; locations: CatalogSnapshot["locations"]; busy: boolean;
  language: "am" | "en"; onSave: (stops: StopDraft[]) => Promise<void>;
}) {
  const am = language === "am";
  const [stops, setStops] = useState<StopDraft[]>(route.stops.map(stop => ({
    location_id: stop.location_id, boarding_allowed: stop.boarding_allowed,
    alighting_allowed: stop.alighting_allowed,
  })));
  useEffect(() => {
    setStops(route.stops.map(stop => ({ location_id: stop.location_id,
      boarding_allowed: stop.boarding_allowed, alighting_allowed: stop.alighting_allowed }));
  }, [route.id, route.stops]);
  const update = (index: number, patch: Partial<StopDraft>) =>
    setStops(current => current.map((stop, i) => i === index ? { ...stop, ...patch } : stop));
  const add = () => setStops(current => {
    const endpoint = current[current.length - 1];
    return [...current.slice(0, -1), { location_id: "", boarding_allowed: true, alighting_allowed: true }, endpoint];
  });
  return <form className="role-assignment-form" onSubmit={event => { event.preventDefault(); void onSave(stops); }}>
    <p>{am ? "የመነሻ እና የመድረሻ ቦታዎች በመስመሩ ይወሰናሉ። መካከለኛ ማቆሚያዎችን ያክሉ።" : "Origin and destination are fixed by the route. Add and order intermediate stops."}</p>
    {stops.map((stop, index) => <div className="staff-user-row" key={index}>
      <div><strong>{index === 0 ? (am ? "መነሻ" : "Origin") : index === stops.length - 1 ? (am ? "መድረሻ" : "Destination") : (am ? "ማቆሚያ" : "Stop")} {index + 1}</strong></div>
      <select required disabled={index === 0 || index === stops.length - 1 || busy}
        value={stop.location_id} onChange={event => update(index, { location_id: event.target.value })}>
        <option value="">{am ? "ቦታ ይምረጡ" : "Select location"}</option>
        {locations.filter(item => item.status === "published").map(item =>
          <option key={item.id} value={item.id}>{item.name}</option>)}
      </select>
      <label><input type="checkbox" checked={stop.boarding_allowed} disabled={busy}
        onChange={event => update(index, { boarding_allowed: event.target.checked })} /> {am ? "መሳፈር" : "Boarding"}</label>
      <label><input type="checkbox" checked={stop.alighting_allowed} disabled={busy}
        onChange={event => update(index, { alighting_allowed: event.target.checked })} /> {am ? "መውረድ" : "Alighting"}</label>
      {index > 0 && index < stops.length - 1 && <button type="button" className="text-link"
        disabled={busy} onClick={() => setStops(current => current.filter((_, i) => i !== index))}>
        {am ? "አስወግድ" : "Remove"}
      </button>}
    </div>)}
    <div className="staff-actions">
      <button type="button" className="secondary-action" disabled={busy || stops.length >= 100} onClick={add}>{am ? "ማቆሚያ ጨምር" : "Add stop"}</button>
      <button className="primary-action" disabled={busy || stops.some(stop => !stop.location_id)}>{am ? "ማቆሚያዎችን አስቀምጥ" : "Save stop sequence"}</button>
    </div>
  </form>;
}

export function CatalogWorkspace({ language, canPublish }: Props) {
  const am = language === "am";
  const [data, setData] = useState<CatalogSnapshot>({ locations: [], terminals: [], routes: [] });
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [locationName, setLocationName] = useState("");
  const [locationType, setLocationType] = useState("town");
  const [terminalName, setTerminalName] = useState("");
  const [terminalLocation, setTerminalLocation] = useState("");
  const [routeCode, setRouteCode] = useState("");
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [editKey, setEditKey] = useState("");
  const [editName, setEditName] = useState("");
  const [editType, setEditType] = useState("town");
  const [editCode, setEditCode] = useState("");
  const [editOrigin, setEditOrigin] = useState("");
  const [editDestination, setEditDestination] = useState("");
  const refresh = async () => setData(await getCatalogSnapshot());
  useEffect(() => {
    let active = true;
    void getCatalogSnapshot().then(value => { if (active) setData(value); })
      .catch(reason => { if (active) setError(reason instanceof Error ? reason.message : "Catalog could not be loaded."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);
  const run = async (action: () => Promise<unknown>, success: string) => {
    setBusy(true); setError(""); setMessage("");
    try { await action(); await refresh(); setMessage(success); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Catalog action failed."); }
    finally { setBusy(false); }
  };
  const submitLocation = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await run(() => createCatalogLocation({ name: locationName.trim(), location_type: locationType }), am ? "መገኛ ቦታ እንደ ረቂቅ ተመዝግቧል።" : "Location saved as a draft.");
    setLocationName("");
  };
  const submitTerminal = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await run(() => createCatalogTerminal({ location_id: terminalLocation, name: terminalName.trim() }), am ? "ተርሚናል እንደ ረቂቅ ተመዝግቧል።" : "Terminal saved as a draft.");
    setTerminalName("");
  };
  const submitRoute = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await run(() => createCatalogRoute({ code: routeCode.trim().toUpperCase(), origin_location_id: origin, destination_location_id: destination }), am ? "መስመር እንደ ረቂቅ ተመዝግቧል።" : "Route saved as a draft.");
    setRouteCode("");
  };
  const startEdit = (kind: EditKind, id: string, values: {
    name?: string; location_type?: string; code?: string; origin_location_id?: string; destination_location_id?: string;
  }) => {
    setEditKey(kind + ":" + id); setEditName(values.name ?? ""); setEditType(values.location_type ?? "town");
    setEditCode(values.code ?? ""); setEditOrigin(values.origin_location_id ?? ""); setEditDestination(values.destination_location_id ?? "");
  };
  const saveEdit = (kind: EditKind, id: string) => run(async () => {
    if (kind === "location") await updateCatalogLocation(id, { name: editName.trim(), location_type: editType });
    else if (kind === "terminal") await updateCatalogTerminal(id, { name: editName.trim() });
    else await updateCatalogRoute(id, { code: editCode.trim().toUpperCase(), origin_location_id: editOrigin, destination_location_id: editDestination });
    setEditKey("");
  }, am ? "ለውጡ ተቀምጧል።" : "Draft changes saved.");
  const publish = (kind: EditKind, id: string) => {
    const action = kind === "location" ? () => publishCatalogLocation(id)
      : kind === "terminal" ? () => publishCatalogTerminal(id) : () => publishCatalogRoute(id);
    void run(action, am ? "መዝገቡ ታትሟል።" : "Catalog record published.");
  };
  const archive = (kind: EditKind, id: string) => void run(() => archiveCatalogRecord(kind, id),
    am ? "መዝገቡ ተመዝግቦ ከአገልግሎት ወጥቷል።" : "Catalog record archived.");
  const status = (value: string) => <span className={"support-status status-" + value}>{value.replaceAll("_", " ")}</span>;
  const editForm = (kind: EditKind, id: string) => editKey === kind + ":" + id ? <form className="role-assignment-form" onSubmit={event => { event.preventDefault(); void saveEdit(kind, id); }}>
    {kind === "route" ? <>
      <label>{am ? "የመስመር ኮድ" : "Route code"}<input required minLength={2} maxLength={60} value={editCode} onChange={event => setEditCode(event.target.value)} /></label>
      <label>{am ? "መነሻ" : "Origin"}<select required value={editOrigin} onChange={event => setEditOrigin(event.target.value)}>{data.locations.filter(item => item.status === "published").map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
      <label>{am ? "መድረሻ" : "Destination"}<select required value={editDestination} onChange={event => setEditDestination(event.target.value)}>{data.locations.filter(item => item.status === "published" && item.id !== editOrigin).map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
    </> : <>
      <label>{am ? "ስም" : "Name"}<input required minLength={2} maxLength={160} value={editName} onChange={event => setEditName(event.target.value)} /></label>
      {kind === "location" && <label>{am ? "ዓይነት" : "Type"}<select value={editType} onChange={event => setEditType(event.target.value)}><option value="town">Town</option><option value="city">City</option><option value="village">Village</option><option value="region">Region</option><option value="other">Other</option></select></label>}
    </>}
    <div className="staff-actions"><button className="primary-action" disabled={busy}>{am ? "አስቀምጥ" : "Save changes"}</button><button type="button" className="secondary-action" onClick={() => setEditKey("")}>{am ? "ሰርዝ" : "Cancel"}</button></div>
  </form> : null;

  return <div className="access-panel">
    <div className="staff-heading"><div><h3>{am ? "የመጓጓዣ ካታሎግ" : "Transport catalog"}</h3>
      <p>{am ? "መገኛ ቦታዎችን፣ ተርሚናሎችን፣ መስመሮችን እና ማቆሚያዎችን ያስተዳድሩ።" : "Manage locations, terminals, routes and ordered route stops."}</p></div>
      <button className="secondary-action" disabled={busy || loading} onClick={() => void refresh()}>{am ? "አድስ" : "Refresh"}</button></div>
    {error && <p className="support-error" role="alert">{error}</p>}
    {message && <p className="notice-panel" role="status">{message}</p>}
    {loading ? <p role="status">{am ? "በመጫን ላይ…" : "Loading catalog…"}</p> : <>
      <div className="staff-stat-grid">
        <div className="staff-stat"><small>{am ? "መገኛ ቦታዎች" : "Locations"}</small><strong>{data.locations.length}</strong></div>
        <div className="staff-stat"><small>{am ? "ተርሚናሎች" : "Terminals"}</small><strong>{data.terminals.length}</strong></div>
        <div className="staff-stat"><small>{am ? "መስመሮች" : "Routes"}</small><strong>{data.routes.length}</strong></div>
      </div>
      <div className="staff-module-grid">
        <section className="staff-module"><h4>{am ? "መገኛ ቦታ ይጨምሩ" : "Add location"}</h4>
          <form className="role-assignment-form" onSubmit={submitLocation}>
            <label>{am ? "ስም" : "Name"}<input required minLength={2} maxLength={160} value={locationName} onChange={event => setLocationName(event.target.value)} /></label>
            <label>{am ? "ዓይነት" : "Type"}<select value={locationType} onChange={event => setLocationType(event.target.value)}><option value="town">Town / ከተማ</option><option value="city">City / ከተማ</option><option value="village">Village / መንደር</option><option value="region">Region / ክልል</option><option value="other">Other / ሌላ</option></select></label>
            <button className="primary-action" disabled={busy}>{am ? "ረቂቅ አስቀምጥ" : "Save draft"}</button>
          </form>
        </section>
        <section className="staff-module"><h4>{am ? "ተርሚናል ይጨምሩ" : "Add terminal"}</h4>
          <form className="role-assignment-form" onSubmit={submitTerminal}>
            <label>{am ? "የታተመ መገኛ ቦታ" : "Published location"}<select required value={terminalLocation} onChange={event => setTerminalLocation(event.target.value)}><option value="">{am ? "ይምረጡ" : "Select location"}</option>{data.locations.filter(item => item.status === "published").map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
            <label>{am ? "የተርሚናል ስም" : "Terminal name"}<input required minLength={2} maxLength={160} value={terminalName} onChange={event => setTerminalName(event.target.value)} /></label>
            <button className="primary-action" disabled={busy || !terminalLocation}>{am ? "ረቂቅ አስቀምጥ" : "Save draft"}</button>
          </form>
        </section>
        <section className="staff-module"><h4>{am ? "መስመር ይጨምሩ" : "Add route"}</h4>
          <form className="role-assignment-form" onSubmit={submitRoute}>
            <label>{am ? "የመስመር ኮድ" : "Route code"}<input required minLength={2} maxLength={60} value={routeCode} onChange={event => setRouteCode(event.target.value)} /></label>
            <label>{am ? "መነሻ" : "Origin"}<select required value={origin} onChange={event => setOrigin(event.target.value)}><option value="">{am ? "ይምረጡ" : "Select origin"}</option>{data.locations.filter(item => item.status === "published").map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
            <label>{am ? "መድረሻ" : "Destination"}<select required value={destination} onChange={event => setDestination(event.target.value)}><option value="">{am ? "ይምረጡ" : "Select destination"}</option>{data.locations.filter(item => item.status === "published" && item.id !== origin).map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
            <button className="primary-action" disabled={busy || !origin || !destination || origin === destination}>{am ? "ረቂቅ አስቀምጥ" : "Save draft"}</button>
          </form>
        </section>
      </div>
      <h4>{am ? "መገኛ ቦታዎች" : "Locations"}</h4>
      {data.locations.map(item => <article className="staff-module" key={item.id}><div className="staff-user-row"><div><strong>{item.name}</strong><small>{item.location_type}</small></div>{status(item.status)}
        {item.status === "draft" && <button className="text-link" disabled={busy} onClick={() => startEdit("location", item.id, item)}>{am ? "አስተካክል" : "Edit"}</button>}
        {item.status === "draft" && canPublish && <button className="text-link" disabled={busy} onClick={() => publish("location", item.id)}>{am ? "አትም" : "Publish"}</button>}
        {item.status !== "archived" && <button className="text-link" disabled={busy} onClick={() => archive("location", item.id)}>{am ? "ከአገልግሎት አውጣ" : "Archive"}</button>}
      </div>{editForm("location", item.id)}</article>)}
      <h4>{am ? "ተርሚናሎች" : "Terminals"}</h4>
      {data.terminals.map(item => <article className="staff-module" key={item.id}><div className="staff-user-row"><div><strong>{item.name}</strong><small>{item.location_name}</small></div>{status(item.status)}
        {item.status === "draft" && <button className="text-link" disabled={busy} onClick={() => startEdit("terminal", item.id, item)}>{am ? "አስተካክል" : "Edit"}</button>}
        {item.status === "draft" && canPublish && <button className="text-link" disabled={busy} onClick={() => publish("terminal", item.id)}>{am ? "አትም" : "Publish"}</button>}
        {item.status !== "archived" && <button className="text-link" disabled={busy} onClick={() => archive("terminal", item.id)}>{am ? "ከአገልግሎት አውጣ" : "Archive"}</button>}
      </div>{editForm("terminal", item.id)}</article>)}
      <h4>{am ? "መስመሮች እና ማቆሚያዎች" : "Routes and stops"}</h4>
      {data.routes.map(item => <article className="staff-module" key={item.id}><div className="staff-user-row"><div><strong>{item.code}</strong><small>{item.origin_name} → {item.destination_name} · {item.stops.length} {am ? "ማቆሚያዎች" : "stops"}</small></div>{status(item.status)}
        {item.status === "draft" && <button className="text-link" disabled={busy} onClick={() => startEdit("route", item.id, item)}>{am ? "አስተካክል" : "Edit"}</button>}
        {item.status === "draft" && <details><summary>{am ? "ማቆሚያዎችን አስተካክል" : "Edit stops"}</summary>
          <RouteStopEditor route={item} locations={data.locations} busy={busy} language={language}
            onSave={stops => run(() => replaceCatalogRouteStops(item.id, stops), am ? "የመስመር ማቆሚያዎች ተቀምጠዋል።" : "Route stop sequence saved.")} />
        </details>}
        {item.status === "draft" && canPublish && <button className="text-link" disabled={busy} onClick={() => publish("route", item.id)}>{am ? "አትም" : "Publish"}</button>}
        {item.status !== "archived" && <button className="text-link" disabled={busy} onClick={() => archive("route", item.id)}>{am ? "ከአገልግሎት አውጣ" : "Archive"}</button>}
      </div>{editForm("route", item.id)}
        <ol>{item.stops.map(stop => <li key={stop.id}>{stop.location_name} — {stop.boarding_allowed ? (am ? "መሳፈር" : "Board") : ""}{stop.alighting_allowed ? (am ? " መውረድ" : " · Alight") : ""}</li>)}</ol>
      </article>)}
      <p className="compliance-note">{am ? "የተጠቀሱ መዝገቦች ከማህደር አይጠፉም። በጉዞ፣ በፕሮግራም ወይም በዋጋ የተጠቀሙ መስመሮች እንዳይቋረጡ ማህደር መደረግ ይከለከላል።" : "Archiving is non-destructive. Records referenced by trips, schedules, fares, terminals or routes are protected from archival."}</p>
    </>}
  </div>;
}
