import { useEffect, useMemo, useState, type FormEvent } from "react";
import {
  approveFleetSeatLayout, createFleetSeatLayout, createFleetVehicle, getFleetVehicles,
  getVehicleSeatLayouts, reviewFleetVehicle, updateDraftFleetSeatLayout, updateFleetVehicle,
  type FleetSeatLayout, type FleetVehicle,
} from "./staff-api";

type Props = { language: "am" | "en"; organizationIds: string[]; canManage: boolean; canReview: boolean };

function parseSeatRows(value: string, seatType = "standard", isSellable = true) {
  const rows = value.split("\n").map(line => line.trim()).filter(Boolean);
  if (!rows.length || rows.length > 26) return null;
  const seats = rows.flatMap((line, rowIndex) => line.split(/[\s,]+/).filter(Boolean).map((token, columnIndex) => {
    const [rawCode, rawType, rawSellability, ...extra] = token.split(":");
    const type = rawType || seatType;
    const sellability = rawSellability || "";
    if (
      extra.length || !rawCode || rawCode.length > 16 ||
      !["standard", "premium", "accessible"].includes(type) ||
      (sellability && !["sellable", "blocked"].includes(sellability))
    ) return null;
    return {
      seat_code: rawCode.toUpperCase(), row_label: String.fromCharCode(65 + rowIndex),
      column_index: columnIndex, seat_type: type,
      is_sellable: sellability ? sellability === "sellable" : isSellable,
    };
  }));
  return seats.length > 0 && seats.length <= 60 && seats.every(Boolean) &&
    rows.every(line => line.split(/[\\s,]+/).filter(Boolean).length <= 21)
    ? seats : null;
}

function formatSeatRows(layout: FleetSeatLayout) {
  const grouped = new Map<string, FleetSeatLayout["seats"]>();
  for (const seat of layout.seats) {
    const row = seat.row_label ?? "A";
    grouped.set(row, [...(grouped.get(row) ?? []), seat]);
  }
  return [...grouped.entries()].sort(([a], [b]) => a.localeCompare(b))
    .map(([, seats]) => seats.sort((a, b) => a.column_index - b.column_index).map(seat => `${seat.seat_code}:${seat.seat_type}:${seat.is_sellable ? "sellable" : "blocked"}`).join(" "))
    .join("\n");
}

export function FleetWorkspace({ language, organizationIds, canManage, canReview }: Props) {
  const am = language === "am";
  const [organizationId, setOrganizationId] = useState("");
  const [vehicles, setVehicles] = useState<FleetVehicle[]>([]);
  const [selectedVehicleId, setSelectedVehicleId] = useState("");
  const [layouts, setLayouts] = useState<FleetSeatLayout[]>([]);
  const [vehicleReference, setVehicleReference] = useState("");
  const [seatRows, setSeatRows] = useState("A1 A2 A3 A4\nB1 B2 B3 B4\nC1 C2 C3 C4");
  const [seatType, setSeatType] = useState("standard");
  const [seatSellable, setSeatSellable] = useState(true);
  const [reviewReason, setReviewReason] = useState("");
  const [editingVehicleId, setEditingVehicleId] = useState("");
  const [editingVehicleReference, setEditingVehicleReference] = useState("");
  const [editingLayoutId, setEditingLayoutId] = useState("");
  const [editingSeatRows, setEditingSeatRows] = useState("");
  const [editingSeatType, setEditingSeatType] = useState("standard");
  const [editingSeatSellable, setEditingSeatSellable] = useState(true);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const selectedVehicle = vehicles.find(item => item.id === selectedVehicleId) ?? null;
  const canManageSelected = Boolean(canManage && selectedVehicle && organizationIds.includes(selectedVehicle.organization_id));
  const refresh = async () => {
    const result = await getFleetVehicles(organizationId || undefined);
    setVehicles(result);
    if (selectedVehicleId && !result.some(item => item.id === selectedVehicleId)) setSelectedVehicleId("");
  };
  useEffect(() => {
    let active = true;
    if (!canReview && !organizationId && organizationIds.length) setOrganizationId(organizationIds[0]);
    if (!canReview && !organizationIds.length) {
      setError("No organization-scoped fleet permission is assigned.");
      setLoading(false);
      return () => { active = false; };
    }
    void getFleetVehicles(canReview && !organizationId ? undefined : organizationId || organizationIds[0])
      .then(result => { if (active) setVehicles(result); })
      .catch(reason => { if (active) setError(reason instanceof Error ? reason.message : "Fleet could not be loaded."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [organizationId, canReview, organizationIds]);
  useEffect(() => {
    let active = true;
    if (!selectedVehicleId) { setLayouts([]); return () => { active = false; }; }
    void getVehicleSeatLayouts(selectedVehicleId).then(result => { if (active) setLayouts(result); })
      .catch(reason => { if (active) setError(reason instanceof Error ? reason.message : "Seat layouts could not be loaded."); });
    return () => { active = false; };
  }, [selectedVehicleId]);
  const run = async (action: () => Promise<unknown>, success: string) => {
    setBusy(true); setError(""); setMessage("");
    try { await action(); await refresh(); if (selectedVehicleId) setLayouts(await getVehicleSeatLayouts(selectedVehicleId)); setMessage(success); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Fleet action failed."); }
    finally { setBusy(false); }
  };
  const submitVehicle = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!organizationId) return;
    await run(() => createFleetVehicle(organizationId, vehicleReference.trim()), am ? "ተሽከርካሪው እንደ ረቂቅ ተመዝግቧል።" : "Vehicle saved as a draft.");
    setVehicleReference("");
  };
  const submitLayout = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedVehicle) return;
    const seats = parseSeatRows(seatRows, seatType, seatSellable);
    if (!seats) {
      setError(am ? "ከ1 እስከ 60 መቀመጫዎች፣ ከ26 ያልበለጡ ረድፎች እና በአንድ ረድፍ ከ21 ያልበለጡ መቀመጫዎች ያስገቡ።" : "Enter 1–60 seats, no more than 26 rows and no more than 21 seats per row.");
      return;
    }
    await run(() => createFleetSeatLayout(selectedVehicle.id, seats), am ? "አዲስ የመቀመጫ አቀማመጥ እንደ ረቂቅ ተፈጥሯል።" : "New seat layout version created as a draft.");
  };
  const saveVehicle = (vehicleId: string) => void run(() => updateFleetVehicle(vehicleId, editingVehicleReference.trim()),
    am ? "የተሽከርካሪ ረቂቅ ተሻሽሏል።" : "Vehicle draft updated.");
  const saveLayout = (layoutId: string) => {
    const seats = parseSeatRows(editingSeatRows, editingSeatType, editingSeatSellable);
    if (!seats) { setError(am ? "የመቀመጫ ረድፎችን ያስተካክሉ።" : "Correct the seat rows before saving."); return; }
    void run(() => updateDraftFleetSeatLayout(layoutId, seats), am ? "የመቀመጫ ረቂቅ ተሻሽሏል።" : "Seat layout draft updated.");
    setEditingLayoutId("");
  };
  const status = (value: string) => <span className={"support-status status-" + value}>{value.replaceAll("_", " ")}</span>;
  const seatRowsGrouped = useMemo(() => {
    const grouped = new Map<string, FleetSeatLayout["seats"]>();
    for (const seat of layouts.find(item => item.status === "approved")?.seats ?? layouts[0]?.seats ?? []) {
      const key = seat.row_label ?? "Seats";
      grouped.set(key, [...(grouped.get(key) ?? []), seat]);
    }
    return [...grouped.entries()].sort(([a], [b]) => a.localeCompare(b));
  }, [layouts]);

  return <div className="access-panel">
    <div className="staff-heading"><div><h3>{am ? "የተሽከርካሪ እና መቀመጫ አስተዳደር" : "Fleet and seat layouts"}</h3>
      <p>{am ? "የተሽከርካሪ መዝገቦችን ያስተዳድሩ፣ የመቀመጫ ረድፎችን ያዋቅሩ እና የማረጋገጫ ሁኔታን ይከታተሉ።" : "Manage operator vehicles, configure versioned seat rows and review fleet readiness."}</p></div>
      <button className="secondary-action" disabled={busy || loading} onClick={() => void refresh()}>{am ? "አድስ" : "Refresh"}</button></div>
    {canReview && <label>{am ? "የኦፕሬተር ድርጅት" : "Operator scope"}
      <select value={organizationId} onChange={event => setOrganizationId(event.target.value)}>
        <option value="">{am ? "ሁሉም ኦፕሬተሮች" : "All operators"}</option>
        {organizationIds.map(id => <option key={id} value={id}>{id}</option>)}
      </select>
    </label>}
    {error && <p className="support-error" role="alert">{error}</p>}
    {message && <p className="notice-panel" role="status">{message}</p>}
    {canManage && organizationIds.length > 0 && <section className="staff-module"><h4>{am ? "ተሽከርካሪ ይመዝግቡ" : "Register vehicle"}</h4>
      <form className="role-assignment-form" onSubmit={submitVehicle}>
        {!canReview && <label>{am ? "የኦፕሬተር ድርጅት" : "Operator organization"}<select required value={organizationId} onChange={event => setOrganizationId(event.target.value)}>{organizationIds.map(id => <option key={id} value={id}>{id}</option>)}</select></label>}
        <label>{am ? "የተሽከርካሪ መለያ / ሰሌዳ ቁጥር" : "Vehicle reference / registration"}<input required minLength={2} maxLength={80} value={vehicleReference} onChange={event => setVehicleReference(event.target.value)} /></label>
        <button className="primary-action" disabled={busy || !organizationId}>{am ? "ረቂቅ አስቀምጥ" : "Save vehicle draft"}</button>
      </form>
    </section>}
    {loading ? <p role="status">{am ? "በመጫን ላይ…" : "Loading fleet…"}</p> : <>
      <div className="staff-stat-grid">
        <div className="staff-stat"><small>{am ? "ተሽከርካሪዎች" : "Vehicles"}</small><strong>{vehicles.length}</strong></div>
        <div className="staff-stat"><small>{am ? "በመጠባበቅ ላይ" : "Pending review"}</small><strong>{vehicles.filter(item => item.review_status === "pending").length}</strong></div>
        <div className="staff-stat"><small>{am ? "የተፈቀዱ" : "Approved"}</small><strong>{vehicles.filter(item => item.review_status === "approved").length}</strong></div>
      </div>
      <h4>{am ? "የተሽከርካሪ መዝገብ" : "Vehicle register"}</h4>
      {vehicles.map(vehicle => <article className="staff-module" key={vehicle.id}>
        <div className="staff-user-row"><div><strong>{vehicle.vehicle_reference}</strong><small>{vehicle.organization_name} · {vehicle.id}</small></div>{status(vehicle.review_status)}{status(vehicle.status)}
          <button className="text-link" onClick={() => setSelectedVehicleId(vehicle.id)}>{am ? "ዝርዝር ክፈት" : "View layouts"}</button>
          {canManage && organizationIds.includes(vehicle.organization_id) && vehicle.status === "draft" && <button className="text-link" onClick={() => { setEditingVehicleId(vehicle.id); setEditingVehicleReference(vehicle.vehicle_reference); }}>{am ? "አስተካክል" : "Edit draft"}</button>}
          {canReview && vehicle.review_status === "pending" && <>
            <button className="text-link" disabled={busy || reviewReason.trim().length < 3} onClick={() => void run(() => reviewFleetVehicle(vehicle.id, "approved", reviewReason.trim()), am ? "ተሽከርካሪው ጸድቋል።" : "Vehicle approved.")}>{am ? "አጽድቅ" : "Approve"}</button>
            <button className="text-link" disabled={busy || reviewReason.trim().length < 3} onClick={() => void run(() => reviewFleetVehicle(vehicle.id, "rejected", reviewReason.trim()), am ? "ተሽከርካሪው ውድቅ ተደርጓል።" : "Vehicle rejected.")}>{am ? "ውድቅ አድርግ" : "Reject"}</button>
          </>}
        </div>
        <small>{vehicle.seat_layouts.length} {am ? "የመቀመጫ ስሪቶች" : "seat layout versions"}</small>
        {editingVehicleId === vehicle.id && <form className="role-assignment-form" onSubmit={event => { event.preventDefault(); void saveVehicle(vehicle.id); setEditingVehicleId(""); }}>
          <label>{am ? "የተሽከርካሪ መለያ" : "Vehicle reference"}<input required minLength={2} maxLength={80} value={editingVehicleReference} onChange={event => setEditingVehicleReference(event.target.value)} /></label>
          <div className="staff-actions"><button className="primary-action" disabled={busy}>{am ? "አስቀምጥ" : "Save"}</button><button type="button" className="secondary-action" onClick={() => setEditingVehicleId("")}>{am ? "ሰርዝ" : "Cancel"}</button></div>
        </form>}
      </article>)}
      {canReview && vehicles.some(item => item.review_status === "pending") && <label>{am ? "የግምገማ ምክንያት" : "Review reason"}<input minLength={3} maxLength={500} value={reviewReason} onChange={event => setReviewReason(event.target.value)} /></label>}
      {selectedVehicle && <section className="staff-module">
        <div className="staff-heading"><div><h4>{selectedVehicle.vehicle_reference} · {am ? "የመቀመጫ አቀማመጦች" : "Seat layouts"}</h4><small>{selectedVehicle.organization_name} · {selectedVehicle.status} / {selectedVehicle.review_status}</small></div>
          <button className="text-link" onClick={() => setSelectedVehicleId("")}>{am ? "ዝጋ" : "Close"}</button></div>
        {canManageSelected && <form className="role-assignment-form" onSubmit={submitLayout}>
          <label>{am ? "የመቀመጫ ረድፎች (በክፍተት ወይም በኮማ ይለዩ)" : "Seat rows: one row per line; use CODE:type:sellable|blocked for per-seat overrides"}
            <textarea rows={4} value={seatRows} onChange={event => setSeatRows(event.target.value)} /><small>Example: A1:standard:sellable A2:accessible:blocked. Plain seat codes use the defaults below.</small></label>
          <label>{am ? "የመቀመጫ አይነት" : "Seat type"}<select value={seatType} onChange={event => setSeatType(event.target.value)}><option value="standard">Standard</option><option value="premium">Premium</option><option value="accessible">Accessible</option></select></label>
          <label><input type="checkbox" checked={seatSellable} onChange={event => setSeatSellable(event.target.checked)} /> {am ? "ለሽያጭ የሚቀርብ" : "Sellable seats"}</label>

          <button className="primary-action" disabled={busy || selectedVehicle.review_status !== "approved"}>{am ? "አዲስ ረቂቅ አቀማመጥ ፍጠር" : "Create draft layout version"}</button>
          {selectedVehicle.review_status !== "approved" && <small>{am ? "የመቀመጫ አቀማመጥ ለመፍጠር ተሽከርካሪው መጽደቅ አለበት።" : "Vehicle must be approved before creating a seat layout."}</small>}
        </form>}
        {layouts.map(layout => <article className="staff-module" key={layout.id}><div className="staff-user-row"><div><strong>Version {layout.version_number}</strong><small>{layout.seats.length} seats</small></div>{status(layout.status)}
          {canManageSelected && layout.status === "draft" && <button className="text-link" onClick={() => { setEditingLayoutId(layout.id); setEditingSeatRows(formatSeatRows(layout)); setEditingSeatType(layout.seats[0]?.seat_type ?? "standard"); setEditingSeatSellable(layout.seats.every(seat => seat.is_sellable)); }}>{am ? "ረቂቅ አስተካክል" : "Edit draft"}</button>}
          {canReview && layout.status === "draft" && selectedVehicle.review_status === "approved" && <button className="text-link" disabled={busy} onClick={() => void run(() => approveFleetSeatLayout(layout.id), am ? "የመቀመጫ አቀማመጡ ጸድቋል።" : "Seat layout approved.")}>{am ? "አቀማመጥ አጽድቅ" : "Approve layout"}</button>}
        </div>
        {editingLayoutId === layout.id && <form className="role-assignment-form" onSubmit={event => { event.preventDefault(); saveLayout(layout.id); }}>
          <label>{am ? "የመቀመጫ ረድፎች" : "Seat rows"}<textarea rows={4} value={editingSeatRows} onChange={event => setEditingSeatRows(event.target.value)} /><small>Example: A1:standard:sellable A2:accessible:blocked. Plain seat codes use the defaults below.</small></label>
          <label>{am ? "የመቀመጫ አይነት" : "Seat type"}<select value={editingSeatType} onChange={event => setEditingSeatType(event.target.value)}><option value="standard">Standard</option><option value="premium">Premium</option><option value="accessible">Accessible</option></select></label>
          <label><input type="checkbox" checked={editingSeatSellable} onChange={event => setEditingSeatSellable(event.target.checked)} /> {am ? "ለሽያጭ የሚቀርብ" : "Sellable seats"}</label>

          <div className="staff-actions"><button className="primary-action" disabled={busy}>{am ? "ለውጦችን አስቀምጥ" : "Save layout changes"}</button><button type="button" className="secondary-action" onClick={() => setEditingLayoutId("")}>{am ? "ሰርዝ" : "Cancel"}</button></div>
        </form>}</article>)}
        <div className="seat-layout-preview">{seatRowsGrouped.map(([row, seats]) => <div className="seat-layout-row" key={row}><strong>{row}</strong>{seats.sort((a,b)=>a.column_index-b.column_index).map(seat=><span className="seat-layout-seat" key={seat.id}>{seat.seat_code}</span>)}</div>)}</div>
      </section>}
    </>}
    <p className="compliance-note">{am ? "ተሽከርካሪዎችና መቀመጫዎች በኦፕሬተር ድርጅት ይገደባሉ። የመቀመጫ አቀማመጥ መጽደቅ ብቻውን ጉዞ ወይም ትኬት አያነቃም።" : "Fleet records and seat layouts are organization-scoped. Layout approval alone does not create trips, enable ticketing or authorize commercial operation."}</p>
  </div>;
}
