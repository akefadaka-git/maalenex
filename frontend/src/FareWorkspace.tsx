import { useEffect, useState, type FormEvent } from "react";
import {
  createFareProposal, getFareOptions, getOperatorFares, getPlatformFares,
  publishFareVersion, reviewFareVersion, submitFareVersion,
  type FareOptions, type FareRecord,
} from "./staff-api";

type Props = {
  language: "am" | "en"; organizationIds: string[]; currentUserId: string;
  canPropose: boolean; canApprove: boolean; canPublish: boolean;
};

export function FareWorkspace({ language, organizationIds, currentUserId, canPropose, canApprove, canPublish }: Props) {
  const am = language === "am";
  const [organizationId, setOrganizationId] = useState(organizationIds[0] ?? "");
  const [options, setOptions] = useState<FareOptions | null>(null);
  const [fares, setFares] = useState<FareRecord[]>([]);
  const [routeId, setRouteId] = useState("");
  const [tripId, setTripId] = useState("");
  const [amount, setAmount] = useState("");
  const [effectiveFrom, setEffectiveFrom] = useState("");
  const [effectiveTo, setEffectiveTo] = useState("");
  const [reviewReason, setReviewReason] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const refresh = async () => {
    if (canApprove) {
      const all = await getPlatformFares();
      setFares(organizationId ? all.filter(item => item.organization_id === organizationId) : all);
    } else if (canPropose && organizationId) setFares(await getOperatorFares(organizationId));
    if (canPropose && organizationId) setOptions(await getFareOptions(organizationId));
  };
  useEffect(() => {
    let active = true;
    setLoading(true); setError("");
    const load = async () => {
      if (canApprove) {
        const all = await getPlatformFares();
        if (active) setFares(organizationId ? all.filter(item => item.organization_id === organizationId) : all);
      } else if (canPropose && organizationId) {
        if (active) setFares(await getOperatorFares(organizationId));
      } else if (!canApprove && !canPropose) {
        if (active) setError("No fare-management permission is assigned.");
      }
      if (canPropose && organizationId) {
        const result = await getFareOptions(organizationId);
        if (active) setOptions(result);
      } else if (active) setOptions(null);
    };
    void load().catch(reason => { if (active) setError(reason instanceof Error ? reason.message : "Fare data could not be loaded."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [organizationId, canApprove, canPropose]);
  const run = async (action: () => Promise<unknown>, success: string) => {
    setBusy(true); setError(""); setMessage("");
    try { await action(); await refresh(); setMessage(success); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Fare action failed."); }
    finally { setBusy(false); }
  };
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!organizationId || !routeId || !amount || !effectiveFrom) return;
    if (!/^\d+(\.\d{1,2})?$/.test(amount)) {
      setError(am ? "የETB ዋጋን እስከ ሁለት የአስርዮሽ ቦታ ያስገቡ።" : "Enter an ETB amount with up to two decimal places.");
      return;
    }
    const amountMinor = Math.round(Number(amount) * 100);
    if (!Number.isSafeInteger(amountMinor) || amountMinor < 0) {
      setError(am ? "የዋጋ መጠኑ ትክክል አይደለም።" : "Fare amount is invalid.");
      return;
    }
    const start = new Date(effectiveFrom);
    const end = effectiveTo ? new Date(effectiveTo) : null;
    if (Number.isNaN(start.getTime()) || (end && (Number.isNaN(end.getTime()) || end <= start))) {
      setError(am ? "የዋጋ ተፈጻሚነት ጊዜን ያረጋግጡ።" : "Check the fare effective period.");
      return;
    }
    await run(() => createFareProposal(organizationId, {
      route_id: routeId, trip_id: tripId || null, amount_minor_units: amountMinor,
      effective_from: start.toISOString(), effective_to: end?.toISOString() ?? null,
    }), am ? "የETB ዋጋ ረቂቅ ተፈጥሯል።" : "ETB fare proposal created as a draft.");
    setAmount(""); setEffectiveFrom(""); setEffectiveTo(""); setTripId("");
  };
  const status = (value: string) => <span className={"support-status status-" + value}>{value.replaceAll("_", " ")}</span>;
  const formatMoney = (minor: number) => new Intl.NumberFormat(am ? "am-ET" : "en-ET", {
    style: "currency", currency: "ETB", minimumFractionDigits: 2,
  }).format(minor / 100);
  const formatDate = (value: string | null) => value ? new Date(value).toLocaleString(am ? "am-ET" : "en-ET") : "—";
  const availableTrips = options?.trips.filter(item => item.route_id === routeId) ?? [];

  return <div className="access-panel">
    <div className="staff-heading"><div><h3>{am ? "የዋጋ አስተዳደር" : "Fare management"}</h3>
      <p>{am ? "የETB ዋጋዎችን ያቅርቡ፣ ያጽድቁ እና በተለየ ፈቃድ ያትሙ።" : "Propose ETB route or trip fares, review versions and publish approved effective rates."}</p></div>
      <button className="secondary-action" disabled={busy || loading} onClick={() => void refresh()}>{am ? "አድስ" : "Refresh"}</button></div>
    {(canApprove || canPublish) && <label>{am ? "የኦፕሬተር ማጣሪያ" : "Operator filter"}<select value={organizationId} onChange={event => setOrganizationId(event.target.value)}>
      <option value="">{am ? "ሁሉም ኦፕሬተሮች" : "All operators"}</option>
      {organizationIds.map(id => <option key={id} value={id}>{id}</option>)}
    </select></label>}
    {error && <p className="support-error" role="alert">{error}</p>}
    {message && <p className="notice-panel" role="status">{message}</p>}
    {canPropose && organizationId && <section className="staff-module"><h4>{am ? "አዲስ የዋጋ ረቂቅ" : "Propose fare version"}</h4>
      <form className="role-assignment-form" onSubmit={submit}>
        <label>{am ? "መስመር" : "Published route"}<select required value={routeId} onChange={event => { setRouteId(event.target.value); setTripId(""); }}><option value="">{am ? "መስመር ይምረጡ" : "Select route"}</option>{options?.routes.map(item => <option key={item.id} value={item.id}>{item.code}</option>)}</select></label>
        <label>{am ? "የተለየ ጉዞ (አማራጭ)" : "Trip-specific fare (optional)"}<select value={tripId} onChange={event => setTripId(event.target.value)}><option value="">{am ? "ለሁሉም ጉዞዎች" : "Route-wide fare"}</option>{availableTrips.map(item => <option key={item.id} value={item.id}>{formatDate(item.departure_at)} · {item.status}</option>)}</select></label>
        <label>{am ? "ዋጋ (ETB)" : "Fare amount (ETB)"}<input required inputMode="decimal" placeholder="125.00" value={amount} onChange={event => setAmount(event.target.value)} /></label>
        <label>{am ? "ተፈጻሚ ከ" : "Effective from"}<input required type="datetime-local" value={effectiveFrom} onChange={event => setEffectiveFrom(event.target.value)} /></label>
        <label>{am ? "ተፈጻሚ እስከ (አማራጭ)" : "Effective until (optional)"}<input type="datetime-local" value={effectiveTo} onChange={event => setEffectiveTo(event.target.value)} /></label>
        <button className="primary-action" disabled={busy || !routeId || !amount || !effectiveFrom}>{am ? "ረቂቅ አስቀምጥ" : "Save fare draft"}</button>
      </form>
    </section>}
    {loading ? <p role="status">{am ? "በመጫን ላይ…" : "Loading fares…"}</p> : <>
      <div className="staff-stat-grid">
        <div className="staff-stat"><small>{am ? "የዋጋ መዝገቦች" : "Fare records"}</small><strong>{fares.length}</strong></div>
        <div className="staff-stat"><small>{am ? "ግምገማ የሚጠብቁ" : "Awaiting review"}</small><strong>{fares.reduce((n, fare) => n + fare.versions.filter(v => v.status === "submitted").length, 0)}</strong></div>
        <div className="staff-stat"><small>{am ? "የታተሙ ስሪቶች" : "Published versions"}</small><strong>{fares.reduce((n, fare) => n + fare.versions.filter(v => v.status === "published").length, 0)}</strong></div>
      </div>
      <h4>{am ? "የዋጋ መዝገብ" : "Fare register"}</h4>
      {fares.map(fare => <article className="staff-module" key={fare.id}>
        <div className="staff-heading"><div><strong>{fare.route_code}{fare.trip_id ? " · " + formatDate(fare.trip_departure_at) : ""}</strong><small>{fare.organization_name} · {fare.status}</small></div></div>
        {fare.versions.map((version, index) => {
          const previousVersion = fare.versions[index + 1];
          const change = previousVersion ? version.amount_minor_units - previousVersion.amount_minor_units : null;
          const changePercent = previousVersion && previousVersion.amount_minor_units > 0
            ? (change! / previousVersion.amount_minor_units) * 100 : null;
          return <div className="staff-user-row" key={version.id}>
          <div><strong>v{version.version_number} · {formatMoney(version.amount_minor_units)}</strong>
            <small>{formatDate(version.effective_from)} → {formatDate(version.effective_to)}</small>
            {previousVersion && <small>{am ? `ለውጥ ከ v${previousVersion.version_number}: ` : `Change vs v${previousVersion.version_number}: `}{change !== null && change > 0 ? "+" : ""}{formatMoney(change ?? 0)}{changePercent !== null ? ` (${changePercent > 0 ? "+" : ""}${changePercent.toFixed(2)}%)` : ""}</small>}
            {version.approval_history.map(approval => <small key={approval.id}>
              {approval.decision.toUpperCase()} · {formatDate(approval.decided_at)} · {approval.reason}
            </small>)}
          </div>
          {status(version.status)}
          {canPropose && organizationIds.includes(fare.organization_id) && version.status === "draft" && version.proposed_by === currentUserId &&
            <button className="text-link" disabled={busy} onClick={() => void run(() => submitFareVersion(fare.id, version.id), am ? "ዋጋው ለግምገማ ተልኳል።" : "Fare submitted for review.")}>{am ? "ለግምገማ ላክ" : "Submit"}</button>}
          {canApprove && version.status === "submitted" && version.proposed_by !== currentUserId && <>
            <button className="text-link" disabled={busy || reviewReason.trim().length < 3} onClick={() => void run(() => reviewFareVersion(fare.id, version.id, "approved", reviewReason.trim()), am ? "ዋጋው ጸድቋል።" : "Fare approved.")}>{am ? "አጽድቅ" : "Approve"}</button>
            <button className="text-link" disabled={busy || reviewReason.trim().length < 3} onClick={() => void run(() => reviewFareVersion(fare.id, version.id, "rejected", reviewReason.trim()), am ? "ዋጋው ውድቅ ተደርጓል።" : "Fare rejected.")}>{am ? "ውድቅ አድርግ" : "Reject"}</button>
          </>}
          {canPublish && version.status === "approved" && version.approved_by !== currentUserId &&
            <button className="text-link" disabled={busy} onClick={() => void run(() => publishFareVersion(fare.id, version.id), am ? "ዋጋው ታትሟል።" : "Fare published.")}>{am ? "አትም" : "Publish"}</button>}
        </div>;
        })}
      </article>)}
      {canApprove && fares.some(fare => fare.versions.some(v => v.status === "submitted" && v.proposed_by !== currentUserId)) &&
        <label>{am ? "የግምገማ ምክንያት" : "Review reason"}<input minLength={3} maxLength={500} value={reviewReason} onChange={event => setReviewReason(event.target.value)} /></label>}
    </>}
    <p className="compliance-note">{am ? "የዋጋ ማተም የዋጋ መዝገብን ብቻ ያዘምናል። ክፍያ፣ የኪስ ቦርሳ ወይም የገንዘብ እንቅስቃሴ አይፈጽምም።" : "Publishing a fare changes the effective price record only. It does not collect payment, debit a wallet or move money."}</p>
  </div>;
}
