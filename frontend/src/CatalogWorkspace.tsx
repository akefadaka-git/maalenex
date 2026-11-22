import { useEffect, useState, type FormEvent } from "react";
import {
  createCatalogLocation, createCatalogRoute, createCatalogTerminal, getCatalogSnapshot,
  publishCatalogLocation, publishCatalogRoute, publishCatalogTerminal,
  type CatalogSnapshot,
} from "./staff-api";

type Props = { language: "am" | "en"; canPublish: boolean };
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
  const publish = (kind: "location" | "terminal" | "route", id: string) => {
    const action = kind === "location" ? () => publishCatalogLocation(id)
      : kind === "terminal" ? () => publishCatalogTerminal(id) : () => publishCatalogRoute(id);
    void run(action, am ? "መዝገቡ ታትሟል።" : "Catalog record published.");
  };
  const status = (value: string) => <span className={"support-status status-" + value}>{value.replaceAll("_", " ")}</span>;

  return <div className="access-panel">
    <div className="staff-heading"><div><h3>{am ? "የመጓጓዣ ካታሎግ" : "Transport catalog"}</h3>
      <p>{am ? "መገኛ ቦታዎችን፣ ተርሚናሎችን እና መስመሮችን ያስተዳድሩ። ማተም የተለየ ፈቃድ ይፈልጋል።" : "Manage locations, terminals and routes. Publishing is a separate permission-gated action."}</p></div>
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
            <label>{am ? "ስም" : "Name"}<input required minLength={2} maxLength={160} value={locationName} onChange={e => setLocationName(e.target.value)} /></label>
            <label>{am ? "ዓይነት" : "Type"}<select value={locationType} onChange={e => setLocationType(e.target.value)}><option value="town">Town / ከተማ</option><option value="city">City / ከተማ</option><option value="village">Village / መንደር</option><option value="region">Region / ክልል</option><option value="other">Other / ሌላ</option></select></label>
            <button className="primary-action" disabled={busy}>{am ? "ረቂቅ አስቀምጥ" : "Save draft"}</button>
          </form>
        </section>
        <section className="staff-module"><h4>{am ? "ተርሚናል ይጨምሩ" : "Add terminal"}</h4>
          <form className="role-assignment-form" onSubmit={submitTerminal}>
            <label>{am ? "የታተመ መገኛ ቦታ" : "Published location"}<select required value={terminalLocation} onChange={e => setTerminalLocation(e.target.value)}><option value="">{am ? "ይምረጡ" : "Select location"}</option>{data.locations.filter(item => item.status === "published").map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
            <label>{am ? "የተርሚናል ስም" : "Terminal name"}<input required minLength={2} maxLength={160} value={terminalName} onChange={e => setTerminalName(e.target.value)} /></label>
            <button className="primary-action" disabled={busy || !terminalLocation}>{am ? "ረቂቅ አስቀምጥ" : "Save draft"}</button>
          </form>
        </section>
        <section className="staff-module"><h4>{am ? "መስመር ይጨምሩ" : "Add route"}</h4>
          <form className="role-assignment-form" onSubmit={submitRoute}>
            <label>{am ? "የመስመር ኮድ" : "Route code"}<input required minLength={2} maxLength={60} value={routeCode} onChange={e => setRouteCode(e.target.value)} /></label>
            <label>{am ? "መነሻ" : "Origin"}<select required value={origin} onChange={e => setOrigin(e.target.value)}><option value="">{am ? "ይምረጡ" : "Select origin"}</option>{data.locations.filter(item => item.status === "published").map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
            <label>{am ? "መድረሻ" : "Destination"}<select required value={destination} onChange={e => setDestination(e.target.value)}><option value="">{am ? "ይምረጡ" : "Select destination"}</option>{data.locations.filter(item => item.status === "published" && item.id !== origin).map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
            <button className="primary-action" disabled={busy || !origin || !destination || origin === destination}>{am ? "ረቂቅ አስቀምጥ" : "Save draft"}</button>
          </form>
        </section>
      </div>
      <h4>{am ? "መገኛ ቦታዎች" : "Locations"}</h4>
      {data.locations.map(item => <article className="staff-user-row" key={item.id}><div><strong>{item.name}</strong><small>{item.location_type} · {item.id}</small></div>{status(item.status)}{item.status === "draft" && canPublish && <button className="text-link" disabled={busy} onClick={() => publish("location", item.id)}>{am ? "አትም" : "Publish"}</button>}</article>)}
      <h4>{am ? "ተርሚናሎች" : "Terminals"}</h4>
      {data.terminals.map(item => <article className="staff-user-row" key={item.id}><div><strong>{item.name}</strong><small>{item.location_name}</small></div>{status(item.status)}{item.status === "draft" && canPublish && <button className="text-link" disabled={busy} onClick={() => publish("terminal", item.id)}>{am ? "አትም" : "Publish"}</button>}</article>)}
      <h4>{am ? "መስመሮች" : "Routes"}</h4>
      {data.routes.map(item => <article className="staff-user-row" key={item.id}><div><strong>{item.code}</strong><small>{item.origin_name} → {item.destination_name}</small></div>{status(item.status)}{item.status === "draft" && canPublish && <button className="text-link" disabled={busy} onClick={() => publish("route", item.id)}>{am ? "አትም" : "Publish"}</button>}</article>)}
      <p className="compliance-note">{am ? "የካታሎግ ለውጦች የሙከራ መዝገቦች ናቸው። መስመር ማተም ብቻውን ጉዞ ወይም ንግድ አያነቃም።" : "Catalog records remain configuration data. Publishing a route does not create a trip or authorize commercial operation."}</p>
    </>}
  </div>;
}
