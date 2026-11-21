import { useEffect, useMemo, useState, type FormEvent } from "react";
import {
  assignStaffRole, getSchedulerStatus, getStaffAudit, getStaffDashboard,
  getStaffRoles, getStaffSession, getStaffUsers, revokeStaffRole,
  runSchedulerOnce, staffLogin, staffLogout,
  type AuditItem, type SchedulerStatus, type StaffDashboard,
  type StaffRoleDefinition, type StaffSession, type StaffUser,
} from "./staff-api";

type Props = { language: "am" | "en" };
export function StaffConsole({ language }: Props) {
  const am = language === "am";
  const [session,setSession] = useState<StaffSession|null>(null);
  const [dashboard,setDashboard] = useState<StaffDashboard|null>(null);
  const [scheduler,setScheduler] = useState<SchedulerStatus|null>(null);
  const [roles,setRoles] = useState<StaffRoleDefinition[]>([]);
  const [users,setUsers] = useState<StaffUser[]>([]);
  const [audit,setAudit] = useState<AuditItem[]>([]);
  const [login,setLogin] = useState("");
  const [password,setPassword] = useState("");
  const [selectedUser,setSelectedUser] = useState("");
  const [selectedRole,setSelectedRole] = useState("");
  const [organizationId,setOrganizationId] = useState("");
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState("");
  const [message,setMessage] = useState("");
  const [tab,setTab] = useState("overview");
  const [loading,setLoading] = useState(true);
  const permissions = useMemo(()=>new Set(dashboard?.permissions??session?.permissions??[]),[dashboard,session]);
  const refresh = async (current?: StaffSession) => {
    const active = current ?? await getStaffSession();
    setSession(active);
    const summary = await getStaffDashboard();
    setDashboard(summary);
    if(summary.permissions.includes("platform.scheduler.read")) {
      try { setScheduler(await getSchedulerStatus()); } catch { setScheduler(null); }
    } else setScheduler(null);
    if(summary.permissions.includes("platform.access.manage")) {
      const [roleResult,userResult] = await Promise.all([getStaffRoles(),getStaffUsers()]);
      setRoles(roleResult.items); setUsers(userResult.items);
    } else { setRoles([]); setUsers([]); }
    if(summary.permissions.includes("platform.audit.read")) {
      try { setAudit(await getStaffAudit()); } catch { setAudit([]); }
    } else setAudit([]);
  };
  useEffect(()=>{let active=true;void getStaffSession().then(async current=>{if(active)await refresh(current);}).catch(()=>{if(active)setSession(null);}).finally(()=>{if(active)setLoading(false);});return()=>{active=false;};},[]);
  useEffect(()=>{if(!session||tab!=="scheduler")return;let active=true;const poll=()=>void getSchedulerStatus().then(value=>{if(active)setScheduler(value);}).catch(reason=>{if(active)setError(reason instanceof Error?reason.message:"Scheduler monitoring unavailable.");});poll();const timer=window.setInterval(poll,15000);return()=>{active=false;window.clearInterval(timer);};},[session,tab]);
  const signIn=async(event:FormEvent<HTMLFormElement>)=>{event.preventDefault();setBusy(true);setError("");try{const current=await staffLogin(login.trim(),password);setPassword("");await refresh(current);}catch(reason){setError(reason instanceof Error?reason.message:"Staff sign-in failed.");}finally{setBusy(false);}};
  const signOut=async()=>{setBusy(true);try{await staffLogout();setSession(null);setDashboard(null);setScheduler(null);setUsers([]);setRoles([]);setAudit([]);}catch(reason){setError(reason instanceof Error?reason.message:"Unable to sign out.");}finally{setBusy(false);}};
  const assign=async(event:FormEvent<HTMLFormElement>)=>{event.preventDefault();const role=roles.find(item=>item.code===selectedRole);if(!selectedUser||!role)return;setBusy(true);setError("");setMessage("");try{await assignStaffRole(selectedUser,role.code,role.scope==="organization"?organizationId.trim():null);setMessage(am?"የሚና ፈቃድ ተመድቧል።":"Role assigned successfully.");setOrganizationId("");await refresh();}catch(reason){setError(reason instanceof Error?reason.message:"Role assignment failed.");}finally{setBusy(false);}};
  const revoke=async(assignmentId:string)=>{if(!window.confirm(am?"ይህን የሚና ፈቃድ መሻር ይፈልጋሉ?":"Revoke this role assignment?"))return;setBusy(true);setError("");try{await revokeStaffRole(assignmentId);setMessage(am?"የሚና ፈቃድ ተሽሯል።":"Role assignment revoked.");await refresh();}catch(reason){setError(reason instanceof Error?reason.message:"Role revocation failed.");}finally{setBusy(false);}};
  const runOnce=async()=>{if(!window.confirm(am?"አንድ የሙከራ የይዞታ ማብቂያ ዙር ማስኬድ ይፈልጋሉ?":"Run one synthetic hold-expiry cycle?"))return;setBusy(true);setError("");try{const result=await runSchedulerOnce();setMessage(am?`ዙሩ ተጠናቋል፤ ${result.records_processed??0} መዝገቦች።`:`Cycle completed; ${result.records_processed??0} records processed.`);setScheduler(await getSchedulerStatus());}catch(reason){setError(reason instanceof Error?reason.message:"Scheduler run failed.");}finally{setBusy(false);}};
  const date=(value:string|null)=>value?new Date(value).toLocaleString(am?"am-ET":"en-ET"):(am?"የለም":"—");
  if(loading)return <section className="content-section"><div className="panel-card"><p role="status">{am?"የሰራተኛ የስራ ቦታን በመፈተሽ ላይ…":"Checking staff workspace…"}</p></div></section>;
  if(!session||!dashboard)return <section className="content-section"><form className="form-card staff-login-card" onSubmit={signIn}><span className="section-kicker">STAFF ACCESS · SEPARATE IDENTITY</span><h2>{am?"የሰራተኛ መግቢያ":"Staff sign in"}</h2><p>{am?"የሰራተኛ መለያ ከተሳፋሪ መለያ የተለየ ነው።":"Staff access uses a separate account, session cookie and role-based permissions. Passenger credentials do not work here."}</p><label>{am?"የመግቢያ መለያ":"Login identifier"}<input required autoComplete="username" value={login} onChange={event=>setLogin(event.target.value)}/></label><label>{am?"የይለፍ ቃል":"Password"}<input required type="password" autoComplete="current-password" value={password} onChange={event=>setPassword(event.target.value)}/></label>{error&&<p className="support-error" role="alert">{error}</p>}<button className="primary-action" disabled={busy}>{busy?(am?"በመግባት ላይ…":"Signing in…"):(am?"ወደ ሰራተኛ ስራ ቦታ ግባ":"Sign in to staff workspace")}</button><p className="field-hint">{am?"የአስተዳዳሪ መለያ በአካባቢያዊ እና በተፈቀደ የማስጀመሪያ ሂደት ብቻ ይፈጠራል።":"No administrator account is created automatically. Bootstrap remains a local, explicit operation."}</p></form></section>;
  const tabs=[{key:"overview",label:am?"ዋና ዳሽቦርድ":"Overview"},{key:"scheduler",label:am?"የሰሌዳ አስተዳደር":"Scheduler",show:permissions.has("platform.scheduler.read")},{key:"access",label:am?"የሚና እና ፈቃድ":"Access control",show:permissions.has("platform.access.manage")},{key:"audit",label:am?"የኦዲት መዝገብ":"Audit",show:permissions.has("platform.audit.read")}].filter(item=>item.show!==false);
  return <section className="content-section staff-console"><div className="panel-card">
    <div className="staff-heading"><div><span className="section-kicker">MAALENEX STAFF WORKSPACE</span><h2>{am?"የሰራተኛ ዳሽቦርድ":"Staff dashboard"}</h2><p>{dashboard.staff.display_name} · {dashboard.scope==="platform"?"Platform scope":"Organization scope"}</p></div><button className="secondary-action" disabled={busy} onClick={()=>void signOut()}>{am?"ውጣ":"Sign out"}</button></div>
    <div className="staff-role-list">{dashboard.roles.map(role=><span className="staff-role-chip" key={role.assignment_id}>{role.role_code}{role.organization_id?" · "+role.organization_id.slice(0,8):" · Platform"}</span>)}</div>
    <div className="staff-tabs">{tabs.map(item=><button key={item.key} className={tab===item.key?"filter-active":"secondary-action"} onClick={()=>setTab(item.key)}>{item.label}</button>)}</div>
    {error&&<p className="support-error" role="alert">{error}</p>}{message&&<p className="notice-panel" role="status">{message}</p>}
    {tab==="overview"&&<><div className="staff-stat-grid">{Object.entries(dashboard.stats).map(([key,value])=><div className="staff-stat" key={key}><small>{key.replaceAll("_"," ")}</small><strong>{value.toLocaleString()}</strong></div>)}</div><h3>{am?"የሚናዎ የስራ ቦታዎች":"Your role workspaces"}</h3><div className="staff-module-grid">{dashboard.modules.map(module=><article className="staff-module" key={module.key}><strong>{module.label}</strong><small>{am?"በተመደቡ ፈቃዶች መሰረት የተፈቀደ":"Enabled by your active permissions"}</small><span>{module.key}</span></article>)}</div><p className="compliance-note">{am?"የሙከራ ውሂብ ብቻ፤ እውነተኛ ገንዘብ፣ ትኬት፣ መሳፈር እና ምርት ስራ አልተነቁም።":"Synthetic data only. Real money, ticketing, boarding and production operations are disabled."}</p></>}
    {tab==="scheduler"&&<div className="scheduler-panel"><div className="scheduler-health-row"><div><h3>{am?"የቦታ ይዞታ ማብቂያ ሰሌዳ":"Booking hold expiry worker"}</h3><p>{scheduler?.worker_mode??"separate_process"} · 30-second polling default</p></div><span className={"support-status status-"+(scheduler?.health??"stale")}>{scheduler?.health??"unavailable"}</span></div><div className="staff-stat-grid">{[{k:"Heartbeat age",v:scheduler?.lease?String(scheduler.lease.heartbeat_age_seconds)+" s":"—"},{k:"Successful batches",v:scheduler?.lease?.batches_completed??0},{k:"Records processed",v:scheduler?.lease?.records_processed??0},{k:"Consecutive failures",v:scheduler?.lease?.consecutive_failures??0},{k:"Last duration",v:scheduler?.lease?.last_duration_ms===null||scheduler?.lease?.last_duration_ms===undefined?"—":scheduler.lease.last_duration_ms+" ms"},{k:"Worker enabled",v:scheduler?.runtime.scheduler_enabled?"Yes":"No"}].map(item=><div className="staff-stat" key={item.k}><small>{item.k}</small><strong>{item.v}</strong></div>)}</div><p className="field-hint">{scheduler?.lease?.last_error_code?"Last error class: "+scheduler.lease.last_error_code:"No scheduler error recorded."} · Last success: {date(scheduler?.lease?.last_success_at??null)}</p>{permissions.has("platform.scheduler.manage")&&scheduler?.runtime.scheduler_enabled&&<button className="secondary-action" disabled={busy} onClick={()=>void runOnce()}>{am?"አንድ ዙር አስኬድ":"Run one cycle"}</button>}<h4>{am?"የቅርብ ዙሮች":"Recent executions"}</h4>{scheduler?.runs.length?scheduler.runs.map(run=><article className="scheduler-run" key={run.id}><span className={"support-status status-"+run.status}>{run.status}</span><span>{date(run.started_at)}</span><span>{run.records_processed} records</span><span>{run.duration_ms??"—"} ms</span>{run.error_code&&<small>{run.error_code}</small>}</article>):<p>{am?"ገና የሰሌዳ ዙር አልተመዘገበም።":"No scheduler runs have been recorded."}</p>}<p className="compliance-note">{am?"ሰሌዳው በነባሪ ዝግ ነው። ይህ ዳሽቦርድ ምርት አስኬድ አያነቃም።":"The worker is disabled by default. This dashboard does not enable production operation."}</p></div>}
    {tab==="access"&&<div className="access-panel"><h3>{am?"የሰራተኛ ሚና አስተዳደር":"Staff role administration"}</h3><form className="role-assignment-form" onSubmit={assign}><label>{am?"ሰራተኛ":"Staff user"}<select required value={selectedUser} onChange={event=>setSelectedUser(event.target.value)}><option value="">{am?"ምረጥ":"Select staff user"}</option>{users.filter(user=>user.status==="active"&&user.id!==session.id).map(user=><option key={user.id} value={user.id}>{user.display_name} · {user.login_identifier}</option>)}</select></label><label>{am?"ሚና":"Role"}<select required value={selectedRole} onChange={event=>setSelectedRole(event.target.value)}><option value="">{am?"ምረጥ":"Select role"}</option>{roles.filter(role=>role.code!=="synthetic_platform_admin").map(role=><option key={role.id} value={role.code}>{role.code} · {role.scope}</option>)}</select></label>{roles.find(role=>role.code===selectedRole)?.scope==="organization"&&<label>{am?"የድርጅት UUID":"Operator organization UUID"}<input required value={organizationId} onChange={event=>setOrganizationId(event.target.value)} placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"/></label>}<button className="primary-action" disabled={busy||!selectedUser||!selectedRole}>{am?"ሚና መድብ":"Assign role"}</button></form><h4>{am?"የነባር መለያዎች":"Active staff assignments"}</h4>{users.map(user=><article className="staff-user-row" key={user.id}><div><strong>{user.display_name}</strong><small>{user.login_identifier} · {user.status}</small>{user.roles.map(role=><div className="staff-assignment" key={role.assignment_id}><span>{role.role_code} {role.organization_id?"· "+role.organization_id:"· Platform"}</span>{role.assignment_id&&user.id!==session.id&&<button className="text-link" disabled={busy} onClick={()=>void revoke(role.assignment_id!)}>{am?"ሻር":"Revoke"}</button>}</div>)}</div></article>)}</div>}
    {tab==="audit"&&<div className="audit-panel"><h3>{am?"የኦዲት ክስተቶች":"Redacted audit events"}</h3>{audit.map(item=><article className="scheduler-run" key={item.id}><strong>{item.event_type}</strong><span>{date(item.occurred_at)}</span><span>{item.actor_type}</span><span>{item.outcome}</span></article>)}</div>}
  </div></section>;
}
