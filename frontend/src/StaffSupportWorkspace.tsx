import { useCallback, useEffect, useState } from "react";
import {
  claimStaffSupportItem, getStaffSession, getStaffSupportQueues, resolveStaffSupportItem, reviewStaffSupportReport,
  type StaffPassengerReport, type StaffSupportCase,
} from "./staff-api";

type Props = { language: "am" | "en" };
type QueueKind = "booking" | "passenger" | "report";

export function StaffSupportWorkspace({ language }: Props) {
  const am = language === "am";
  const [currentStaffId, setCurrentStaffId] = useState("");
  const [bookingCases, setBookingCases] = useState<StaffSupportCase[]>([]);
  const [passengerCases, setPassengerCases] = useState<StaffSupportCase[]>([]);
  const [reports, setReports] = useState<StaffPassengerReport[]>([]);
  const [filter, setFilter] = useState("open");
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [codes, setCodes] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setError("");
    try {
      const [queues, session] = await Promise.all([getStaffSupportQueues(), getStaffSession()]);
      setCurrentStaffId(session.id);
      setBookingCases(queues.bookingCases);
      setPassengerCases(queues.passengerCases);
      setReports(queues.reports);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to load support queues.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  const claim = async (kind: QueueKind, id: string) => {
    const key = kind + ":" + id;
    setBusy(key); setError(""); setMessage("");
    try {
      await claimStaffSupportItem(kind, id);
      setMessage(am ? "ጉዳዩ ለእርስዎ ተመድቧል።" : "Case claimed by your staff account.");
      await refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to claim this item.");
    } finally { setBusy(""); }
  };

  const resolve = async (kind: "booking" | "passenger", item: StaffSupportCase) => {
    const key = kind + ":" + item.id;
    const note = (notes[key] ?? "").trim();
    const code = (codes[key] ?? "").trim();
    if (code.length < 3 || note.length < 3) {
      setError(am ? "የውሳኔ ኮድና ማብራሪያ ያስፈልጋሉ።" : "Enter a resolution code and a note (at least 3 characters each).");
      return;
    }
    setBusy(key); setError(""); setMessage("");
    try {
      await resolveStaffSupportItem(kind, item.id, { resolution_code: code, resolution_note: note });
      setMessage(am ? "ጉዳዩ ተፈትቷል።" : "Case resolved and audited.");
      setNotes(current => ({ ...current, [key]: "" }));
      setCodes(current => ({ ...current, [key]: "" }));
      await refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to resolve this item.");
    } finally { setBusy(""); }
  };

  const reviewReport = async (item: StaffPassengerReport, status: "action_required" | "resolved" | "dismissed") => {
    const key = "report:" + item.id;
    const note = (notes[key] ?? "").trim();
    if (note.length < 3) {
      setError(am ? "የግምገማ ማስታወሻ ያስገቡ።" : "Enter a review note of at least 3 characters.");
      return;
    }
    setBusy(key); setError(""); setMessage("");
    try {
      await reviewStaffSupportReport(item.id, { status, resolution_note: note });
      setMessage(am ? "የሪፖርቱ ሁኔታ ተዘምኗል።" : "Report review status updated and audited.");
      setNotes(current => ({ ...current, [key]: "" }));
      await refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to update report.");
    } finally { setBusy(""); }
  };

  const visible = (status: string) => filter === "all" || status === filter ||
    (filter === "open" && status === "submitted");
  const date = (value: string) => new Date(value).toLocaleString(am ? "am-ET" : "en-ET");
  const label = (value: string) => value.replaceAll("_", " ");

  const renderCase = (kind: "booking" | "passenger", item: StaffSupportCase) => {
    const key = kind + ":" + item.id;
    const isOpen = item.status === "open" || item.status === "in_progress";
    return <article className="staff-user-row" key={key}>
      <div className="staff-support-item">
        <div className="staff-heading"><div><strong>{item.case_reference} · {item.subject}</strong><small>{item.category} · {label(item.status)} · {date(item.created_at)}</small></div><span className="support-status">{item.assigned_to ? "Assigned" : "Unassigned"}</span></div>
        <p>{item.message}</p>
        <small>{kind === "booking" ? "Booking case" : "Passenger support"} · {item.assigned_to ? "Assigned to staff" : "Available to claim"}</small>
        {isOpen && <div className="role-assignment-form">
          {!item.assigned_to && <button className="secondary-action" disabled={busy === key || !!busy} onClick={() => void claim(kind, item.id)}>{am ? "ጉዳዩን ውሰድ" : "Claim case"}</button>}
          <label>{am ? "የውሳኔ ኮድ" : "Resolution code"}<input value={codes[key] ?? ""} maxLength={80} onChange={event => setCodes(current => ({ ...current, [key]: event.target.value }))} /></label>
          <label>{am ? "የመፍትሄ ማብራሪያ" : "Resolution note"}<textarea value={notes[key] ?? ""} maxLength={1000} onChange={event => setNotes(current => ({ ...current, [key]: event.target.value }))} /></label>
          <button className="primary-action" disabled={!!busy || item.assigned_to !== currentStaffId} onClick={() => void resolve(kind, item)}>{am ? "መፍትሄ መዝግብ" : "Resolve case"}</button>
        </div>}
      </div>
    </article>;
  };

  if (loading) return <p role="status">{am ? "የድጋፍ ጉዳዮችን በመጫን ላይ…" : "Loading support and safety queues…"}</p>;
  return <div className="access-panel">
    <div className="staff-heading"><div><h3>{am ? "ድጋፍ፣ ቅሬታ እና ደህንነት" : "Support, reports and safety"}</h3><p>{am ? "ጉዳዮችን ይመልከቱ፣ ይውሰዱ፣ በማስረጃ የተመሰረተ ውሳኔ ይመዝግቡ።" : "Review queues, claim work, and record an auditable resolution."}</p></div><button className="secondary-action" disabled={!!busy} onClick={() => void refresh()}>{am ? "አድስ" : "Refresh queues"}</button></div>
    <label>{am ? "የማጣሪያ ሁኔታ" : "Queue filter"}<select value={filter} onChange={event => setFilter(event.target.value)}><option value="open">{am ? "ክፍት / የቀረበ" : "Open / submitted"}</option><option value="in_progress">{am ? "በሂደት ላይ" : "In progress / under review"}</option><option value="resolved">{am ? "ተፈትቷል" : "Resolved"}</option><option value="all">{am ? "ሁሉም" : "All statuses"}</option></select></label>
    {error && <p className="support-error" role="alert">{error}</p>}
    {message && <p className="notice-panel" role="status">{message}</p>}
    <h4>{am ? "የቦታ ማስያዣ ድጋፍ" : "Booking support"} ({bookingCases.filter(item => visible(item.status)).length})</h4>
    {bookingCases.filter(item => visible(item.status)).map(item => renderCase("booking", item))}
    <h4>{am ? "የተሳፋሪ ድጋፍ" : "Passenger support"} ({passengerCases.filter(item => visible(item.status)).length})</h4>
    {passengerCases.filter(item => visible(item.status)).map(item => renderCase("passenger", item))}
    <h4>{am ? "ሪፖርቶች እና ቅሬታዎች" : "Reports and complaints"} ({reports.filter(item => visible(item.status)).length})</h4>
    {reports.filter(item => visible(item.status)).map(item => {
      const key = "report:" + item.id;
      const isOpen = item.status !== "resolved" && item.status !== "dismissed";
      return <article className="staff-user-row" key={key}><div className="staff-support-item">
        <div className="staff-heading"><div><strong>{item.report_reference} · {item.subject}</strong><small>{item.report_type} · {item.category} · {item.severity} · {label(item.status)} · {date(item.created_at)}</small></div></div>
        <p>{item.description}</p>
        <small>{item.attachments.length} private evidence attachment(s) · {item.assigned_to ? "Assigned" : "Unassigned"}</small>
        {isOpen && <div className="role-assignment-form">
          {!item.assigned_to && <button className="secondary-action" disabled={!!busy} onClick={() => void claim("report", item.id)}>{am ? "ለምርመራ ውሰድ" : "Claim for review"}</button>}
          <label>{am ? "የግምገማ ማስታወሻ" : "Review note"}<textarea value={notes[key] ?? ""} maxLength={1000} onChange={event => setNotes(current => ({ ...current, [key]: event.target.value }))} /></label>
          <div className="staff-tabs"><button className="secondary-action" disabled={!!busy || item.assigned_to !== currentStaffId} onClick={() => void reviewReport(item, "action_required")}>{am ? "ተጨማሪ እርምጃ" : "Action required"}</button><button className="primary-action" disabled={!!busy || item.assigned_to !== currentStaffId} onClick={() => void reviewReport(item, "resolved")}>{am ? "ፈታ" : "Resolve"}</button><button className="secondary-action" disabled={!!busy || item.assigned_to !== currentStaffId} onClick={() => void reviewReport(item, "dismissed")}>{am ? "ውድቅ አድርግ" : "Dismiss"}</button></div>
        </div>}
      </div></article>;
    })}
    <p className="compliance-note">{am ? "የማስረጃ ፋይሎች በግል የተጠበቁ ናቸው፤ ይህ ስራ የፋይል ማስወረድ አያነቃም።" : "Evidence files remain private. This workspace does not expose public file URLs or enable downloads."}</p>
  </div>;
}
