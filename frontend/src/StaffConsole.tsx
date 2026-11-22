import { useEffect, useMemo, useState, type FormEvent } from "react";
import { StaffSupportWorkspace } from "./StaffSupportWorkspace";
import { CatalogWorkspace } from "./CatalogWorkspace";
import { FleetWorkspace } from "./FleetWorkspace";
import { DispatchWorkspace } from "./DispatchWorkspace";
import {
  assignStaffRole, createStaffInvitation, getSchedulerStatus, getStaffAudit, getStaffDashboard,
  getStaffInvitations, getStaffOrganizations, getStaffRoles, getStaffSession, getStaffUsers,
  revokeStaffInvitation, revokeStaffRole, runSchedulerOnce, staffLogin, staffLogout,
  type AuditItem, type SchedulerStatus, type StaffDashboard,
  type StaffInvitation, type StaffOrganization, type StaffRoleDefinition, type StaffSession, type StaffUser,
} from "./staff-api";

type Props = { language: "am" | "en" };
export function StaffConsole({ language }: Props) {
  const am = language === "am";
  const [session,setSession] = useState<StaffSession|null>(null);
  const [dashboard,setDashboard] = useState<StaffDashboard|null>(null);
  const [scheduler,setScheduler] = useState<SchedulerStatus|null>(null);
  const [roles,setRoles] = useState<StaffRoleDefinition[]>([]);
  const [users,setUsers] = useState<StaffUser[]>([]);
  const [organizations,setOrganizations] = useState<StaffOrganization[]>([]);
  const [invitations,setInvitations] = useState<StaffInvitation[]>([]);
  const [audit,setAudit] = useState<AuditItem[]>([]);
  const [login,setLogin] = useState("");
  const [password,setPassword] = useState("");
  const [selectedUser,setSelectedUser] = useState("");
  const [selectedRole,setSelectedRole] = useState("");
  const [organizationId,setOrganizationId] = useState("");
  const [inviteOrganizationId,setInviteOrganizationId] = useState("");
  const [inviteRole,setInviteRole] = useState("");
  const [inviteName,setInviteName] = useState("");
  const [inviteLogin,setInviteLogin] = useState("");
  const [inviteToken,setInviteToken] = useState("");
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState("");
  const [message,setMessage] = useState("");
  const [tab,setTab] = useState("overview");
  const [loading,setLoading] = useState(true);
  const permissions = useMemo(()=>new Set(dashboard?.permissions??session?.permissions??[]),[dashboard,session]);
  const fleetOrganizationIds = useMemo(() => Array.from(new Set((session?.roles ?? [])
    .filter(role => Boolean(role.organization_id) && (
      role.permissions?.includes("operator.fleet.manage") ||
      ["operator_fleet_manager", "operator_manager", "synthetic_operator_manager"].includes(role.role_code ?? "")
    )).map(role => role.organization_id as string))), [session]);
  const canManageFleet = permissions.has("operator.fleet.manage");
  const canReviewFleet = permissions.has("platform.fleet.review");
  const dispatchOrganizationIds = useMemo(() => Array.from(new Set((session?.roles ?? [])
    .filter(role => Boolean(role.organization_id) && (
      role.permissions?.includes("operator.trip.manage") ||
      ["operator_dispatcher", "operator_manager", "synthetic_operator_manager"].includes(role.role_code ?? "")
    )).map(role => role.organization_id as string))), [session]);
  const canManageTrips = permissions.has("operator.trip.manage");
  const canReviewTrips = permissions.has("platform.trip.approve");
  const canPublishTrips = permissions.has("platform.trip.publish");
  const canReadManifest = permissions.has("operator.trip.manifest.read");
  const refresh = async (current?: StaffSession) => {
    const active = current ?? await getStaffSession();
    setSession(active);
    const summary = await getStaffDashboard();
    setDashboard(summary);
    if(summary.permissions.includes("platform.scheduler.read")) {
      try { setScheduler(await getSchedulerStatus()); } catch { setScheduler(null); }
    } else setScheduler(null);
    if(summary.permissions.includes("platform.access.manage")) {
      const [roleResult,userResult,organizationResult,invitationResult] = await Promise.all([
        getStaffRoles(), getStaffUsers(), getStaffOrganizations(), getStaffInvitations(),
      ]);
      setRoles(roleResult.items); setUsers(userResult.items);
      setOrganizations(organizationResult.items); setInvitations(invitationResult.items);
    } else { setRoles([]); setUsers([]); setOrganizations([]); setInvitations([]); }
    if(summary.permissions.includes("platform.audit.read")) {
      try { setAudit(await getStaffAudit()); } catch { setAudit([]); }
    } else setAudit([]);
  };
  useEffect(()=>{let active=true;void getStaffSession().then(async current=>{if(active)await refresh(current);}).catch(()=>{if(active)setSession(null);}).finally(()=>{if(active)setLoading(false);});return()=>{active=false;};},[]);
  useEffect(()=>{if(!session||tab!=="scheduler")return;let active=true;const poll=()=>void getSchedulerStatus().then(value=>{if(active)setScheduler(value);}).catch(reason=>{if(active)setError(reason instanceof Error?reason.message:"Scheduler monitoring unavailable.");});poll();const timer=window.setInterval(poll,15000);return()=>{active=false;window.clearInterval(timer);};},[session,tab]);
  const signIn=async(event:FormEvent<HTMLFormElement>)=>{event.preventDefault();setBusy(true);setError("");try{const current=await staffLogin(login.trim(),password);setPassword("");await refresh(current);}catch(reason){setError(reason instanceof Error?reason.message:"Staff sign-in failed.");}finally{setBusy(false);}};
  const signOut=async()=>{setBusy(true);try{await staffLogout();setSession(null);setDashboard(null);setScheduler(null);setUsers([]);setRoles([]);setOrganizations([]);setInvitations([]);setAudit([]);}catch(reason){setError(reason instanceof Error?reason.message:"Unable to sign out.");}finally{setBusy(false);}};
  const assign=async(event:FormEvent<HTMLFormElement>)=>{event.preventDefault();const role=roles.find(item=>item.code===selectedRole);if(!selectedUser||!role)return;setBusy(true);setError("");setMessage("");try{await assignStaffRole(selectedUser,role.code,role.scope==="organization"?organizationId.trim():null);setMessage(am?"የሚና ፈቃድ ተመድቧል።":"Role assigned successfully.");setOrganizationId("");await refresh();}catch(reason){setError(reason instanceof Error?reason.message:"Role assignment failed.");}finally{setBusy(false);}};
  const invite=async(event:FormEvent<HTMLFormElement>)=>{event.preventDefault();setBusy(true);setError("");setMessage("");setInviteToken("");try{const result=await createStaffInvitation(inviteOrganizationId,{login_identifier:inviteLogin.trim(),display_name:inviteName.trim(),role_code:inviteRole});setInviteToken(result.synthetic_invitation_token);setMessage(am?"ግብዣው ተፈጥሯል፤ ማድረስ አልነቃም።":"Invitation created. Delivery is disabled; copy the one-time synthetic token for controlled testing.");setInviteLogin("");setInviteName("");await refresh();}catch(reason){setError(reason instanceof Error?reason.message:"Invitation creation failed.");}finally{setBusy(false);}};
  const revokeInvite=async(item:StaffInvitation)=>{if(!window.confirm(am?"ይህን ግብዣ መሻር ይፈልጋሉ?":"Revoke this invitation?"))return;setBusy(true);setError("");try{await revokeStaffInvitation(item.organization_id,item.id);await refresh();}catch(reason){setError(reason instanceof Error?reason.message:"Invitation revocation failed.");}finally{setBusy(false);}};
  const revoke=async(assignmentId:string)=>{if(!window.confirm(am?"ይህን የሚና ፈቃድ መሻር ይፈልጋሉ?":"Revoke this role assignment?"))return;setBusy(true);setError("");try{await revokeStaffRole(assignmentId);setMessage(am?"የሚና ፈቃድ ተሽሯል።":"Role assignment revoked.");await refresh();}catch(reason){setError(reason instanceof Error?reason.message:"Role revocation failed.");}finally{setBusy(false);}};
  const runOnce=async()=>{if(!window.confirm(am?"አንድ የሙከራ የይዞታ ማብቂያ ዙር ማስኬድ ይፈልጋሉ?":"Run one synthetic hold-expiry cycle?"))return;setBusy(true);setError("");try{const result=await runSchedulerOnce();setMessage(am?`ዙሩ ተጠናቋል፤ ${result.records_processed??0} መዝገቦች።`:`Cycle completed; ${result.records_processed??0} records processed.`);setScheduler(await getSchedulerStatus());}catch(reason){setError(reason instanceof Error?reason.message:"Scheduler run failed.");}finally{setBusy(false);}};
  const date=(value:string|null)=>value?new Date(value).toLocaleString(am?"am-ET":"en-ET"):(am?"የለም":"—");
  if(loading)return <section className="content-section"><div className="panel-card"><p role="status">{am?"የሰራተኛ የስራ ቦታን በመፈተሽ ላይ…":"Checking staff workspace…"}</p></div></section>;
  if(!session||!dashboard)return <section className="content-section"><form className="form-card staff-login-card" onSubmit={signIn}><span className="section-kicker">STAFF ACCESS · SEPARATE IDENTITY</span><h2>{am?"የሰራተኛ መግቢያ":"Staff sign in"}</h2><p>{am?"የሰራተኛ መለያ ከተሳፋሪ መለያ የተለየ ነው።":"Staff access uses a separate account, session cookie and role-based permissions. Passenger credentials do not work here."}</p><label>{am?"የመግቢያ መለያ":"Login identifier"}<input required autoComplete="username" value={login} onChange={event=>setLogin(event.target.value)}/></label><label>{am?"የይለፍ ቃል":"Password"}<input required type="password" autoComplete="current-password" value={password} onChange={event=>setPassword(event.target.value)}/></label>{error&&<p className="support-error" role="alert">{error}</p>}<button className="primary-action" disabled={busy}>{busy?(am?"በመግባት ላይ…":"Signing in…"):(am?"ወደ ሰራተኛ ስራ ቦታ ግባ":"Sign in to staff workspace")}</button><p className="field-hint">{am?"የአስተዳዳሪ መለያ በአካባቢያዊ እና በተፈቀደ የማስጀመሪያ ሂደት ብቻ ይፈጠራል።":"No administrator account is created automatically. Bootstrap remains a local, explicit operation."}</p></form></section>;
  const tabs=[{key:"overview",label:am?"ዋና ዳሽቦርድ":"Overview",show:true},{key:"catalog",label:am?"ካታሎግ":"Catalog",show:permissions.has("platform.catalog.manage")},{key:"fleet",label:am?"ተሽከርካሪ እና መቀመጫ":"Fleet & seats",show:canManageFleet||canReviewFleet},{key:"dispatch",label:am?"ዲስፓች እና ጉዞ":"Dispatch & trips",show:canManageTrips||canReviewTrips||canPublishTrips||canReadManifest},{key:"scheduler",label:am?"የሰሌዳ አስተዳደር":"Scheduler",show:permissions.has("platform.scheduler.read")},{key:"access",label:am?"የሚና እና ፈቃድ":"Access control",show:permissions.has("platform.access.manage")},{key:"support",label:am?"ድጋፍ እና ቅሬታ":"Support & safety",show:permissions.has("platform.support.manage")},{key:"audit",label:am?"የኦዲት መዝገብ":"Audit",show:permissions.has("platform.audit.read")}].filter(item=>item.show);
  return <section className="content-section staff-console"><div className="panel-card">
    <div className="staff-heading"><div><span className="section-kicker">MAALENEX STAFF WORKSPACE</span><h2>{am?"የሰራተኛ ዳሽቦርድ":"Staff dashboard"}</h2><p>{dashboard.staff.display_name} · {dashboard.scope==="platform"?"Platform scope":"Organization scope"}</p></div><button className="secondary-action" disabled={busy} onClick={()=>void signOut()}>{am?"ውጣ":"Sign out"}</button></div>
    <div className="staff-role-list">{dashboard.roles.map(role=><span className="staff-role-chip" key={role.assignment_id}>{role.role_code}{role.organization_id?" · "+role.organization_id.slice(0,8):" · Platform"}</span>)}</div>
    <div className="staff-tabs">{tabs.map(item=><button key={item.key} className={tab===item.key?"filter-active":"secondary-action"} onClick={()=>setTab(item.key)}>{item.label}</button>)}</div>
    {error&&<p className="support-error" role="alert">{error}</p>}{message&&<p className="notice-panel" role="status">{message}</p>}
    {tab==="overview"&&<><div className="staff-stat-grid">{Object.entries(dashboard.stats).map(([key,value])=><div className="staff-stat" key={key}><small>{key.replaceAll("_"," ")}</small><strong>{value.toLocaleString()}</strong></div>)}</div><h3>{am?"የሚናዎ የስራ ቦታዎች":"Your role workspaces"}</h3><div className="staff-module-grid">{dashboard.modules.map(module=><article className="staff-module" key={module.key}><strong>{module.label}</strong><small>{am?"በተመደቡ ፈቃዶች መሰረት የተፈቀደ":"Enabled by your active permissions"}</small><span>{module.key}</span></article>)}</div><details className="staff-permission-details"><summary>{am?"የተፈቀዱ ፈቃዶች":"Effective permissions"}</summary><div className="staff-permission-list">{dashboard.permissions.map(permission=><code key={permission}>{permission}</code>)}</div></details><p className="compliance-note">{am?"የሙከራ ውሂብ ብቻ፤ እውነተኛ ገንዘብ፣ ትኬት፣ መሳፈር እና ምርት ስራ አልተነቁም።":"Synthetic data only. Real money, ticketing, boarding and production operations are disabled."}</p></>}
    {tab==="catalog"&&<CatalogWorkspace language={language} canPublish={permissions.has("platform.catalog.publish")}/>}
    {tab==="fleet"&&<FleetWorkspace language={language} organizationIds={fleetOrganizationIds} canManage={canManageFleet} canReview={canReviewFleet}/>}
    {tab==="dispatch"&&<DispatchWorkspace language={language} organizationIds={dispatchOrganizationIds} canManage={canManageTrips} canReview={canReviewTrips} canPublish={canPublishTrips} canManifest={canReadManifest}/>}
    {tab==="scheduler"&&<div className="scheduler-panel"><div className="scheduler-health-row"><div><h3>{am?"የቦታ ይዞታ ማብቂያ ሰሌዳ":"Booking hold expiry worker"}</h3><p>{scheduler?.worker_mode??"separate_process"} · 30-second polling default</p></div><span className={"support-status status-"+(scheduler?.health??"stale")}>{scheduler?.health??"unavailable"}</span></div><div className="staff-stat-grid">{[{k:"Heartbeat age",v:scheduler?.lease?String(scheduler.lease.heartbeat_age_seconds)+" s":"—"},{k:"Due holds",v:scheduler?.backlog?.due_holds??0},{k:"Oldest overdue",v:(scheduler?.backlog?.oldest_due_age_seconds??0)+" s"},{k:"Successful batches",v:scheduler?.lease?.batches_completed??0},{k:"Records processed",v:scheduler?.lease?.records_processed??0},{k:"Consecutive failures",v:scheduler?.lease?.consecutive_failures??0},{k:"Last duration",v:scheduler?.lease?.last_duration_ms===null||scheduler?.lease?.last_duration_ms===undefined?"—":scheduler.lease.last_duration_ms+" ms"},{k:"Worker enabled",v:scheduler?.runtime.scheduler_enabled?"Yes":"No"}].map(item=><div className="staff-stat" key={item.k}><small>{item.k}</small><strong>{item.v}</strong></div>)}</div><p className="field-hint">{scheduler?.lease?.last_error_code?"Last error class: "+scheduler.lease.last_error_code:"No scheduler error recorded."} · Last success: {date(scheduler?.lease?.last_success_at??null)}</p>{permissions.has("platform.scheduler.manage")&&scheduler?.runtime.scheduler_enabled&&<button className="secondary-action" disabled={busy} onClick={()=>void runOnce()}>{am?"አንድ ዙር አስኬድ":"Run one cycle"}</button>}<h4>{am?"የቅርብ ዙሮች":"Recent executions"}</h4>{scheduler?.runs.length?scheduler.runs.map(run=><article className="scheduler-run" key={run.id}><span className={"support-status status-"+run.status}>{run.status}</span><span>{date(run.started_at)}</span><span>{run.records_processed} records</span><span>{run.duration_ms??"—"} ms</span>{run.error_code&&<small>{run.error_code}</small>}</article>):<p>{am?"ገና የሰሌዳ ዙር አልተመዘገበም።":"No scheduler runs have been recorded."}</p>}<p className="compliance-note">{am?"ሰሌዳው በነባሪ ዝግ ነው። ይህ ዳሽቦርድ ምርት አስኬድ አያነቃም።":"The worker is disabled by default. This dashboard does not enable production operation."}</p></div>}
    {tab==="access"&&<div className="access-panel"><h3>{am?"የሰራተኛ ሚና አስተዳደር":"Staff role administration"}</h3><form className="role-assignment-form" onSubmit={assign}><label>{am?"ሰራተኛ":"Staff user"}<select required value={selectedUser} onChange={event=>setSelectedUser(event.target.value)}><option value="">{am?"ምረጥ":"Select staff user"}</option>{users.filter(user=>user.status==="active"&&user.id!==session.id).map(user=><option key={user.id} value={user.id}>{user.display_name} · {user.login_identifier}</option>)}</select></label><label>{am?"ሚና":"Role"}<select required value={selectedRole} onChange={event=>setSelectedRole(event.target.value)}><option value="">{am?"ምረጥ":"Select role"}</option>{roles.filter(role=>role.code!=="synthetic_platform_admin").map(role=><option key={role.id} value={role.code}>{role.code} · {role.scope}</option>)}</select></label>{roles.find(role=>role.code===selectedRole)?.scope==="organization"&&<label>{am?"ድርጅት":"Operator organization"}<select required value={organizationId} onChange={event=>setOrganizationId(event.target.value)}><option value="">{am?"ድርጅት ምረጥ":"Select operator"}</option>{organizations.map(item=><option key={item.id} value={item.id}>{item.display_name}</option>)}</select></label>}<button className="primary-action" disabled={busy||!selectedUser||!selectedRole}>{am?"ሚና መድብ":"Assign role"}</button></form>
    <h4>{am?"አዲስ የሰራተኛ ግብዣ":"Invite operator staff"}</h4>
    <form className="role-assignment-form" onSubmit={invite}>
      <label>{am?"ድርጅት":"Operator organization"}<select required value={inviteOrganizationId} onChange={event=>setInviteOrganizationId(event.target.value)}><option value="">{am?"ድርጅት ምረጥ":"Select operator"}</option>{organizations.map(item=><option key={item.id} value={item.id}>{item.display_name}</option>)}</select></label>
      <label>{am?"ሚና":"Organization role"}<select required value={inviteRole} onChange={event=>setInviteRole(event.target.value)}><option value="">{am?"ሚና ምረጥ":"Select role"}</option>{roles.filter(role=>role.scope==="organization").map(role=><option key={role.id} value={role.code}>{role.code}</option>)}</select></label>
      <label>{am?"ሙሉ ስም":"Display name"}<input required minLength={2} maxLength={160} value={inviteName} onChange={event=>setInviteName(event.target.value)}/></label>
      <label>{am?"የመግቢያ ኢሜይል":"Staff login email"}<input required type="email" value={inviteLogin} onChange={event=>setInviteLogin(event.target.value)}/></label>
      <button className="primary-action" disabled={busy||!inviteOrganizationId||!inviteRole}>{am?"ግብዣ ፍጠር":"Create invitation"}</button>
    </form>
    {inviteToken&&<div className="notice-panel"><strong>{am?"የሙከራ ግብዣ ቶከን":"One-time synthetic invitation token"}</strong><p className="staff-token">{inviteToken}</p><small>{am?"የኢሜይል ወይም SMS ማድረስ አልተነቃም።":"No email or SMS was sent. Handle this test token as a secret."}</small></div>}
    <h4>{am?"ክፍት ግብዣዎች":"Pending invitations"}</h4>
    {invitations.map(item=><article className="staff-user-row" key={item.id}><div><strong>{item.display_name} · {item.role_code}</strong><small>{item.login_identifier} · {item.organization_name} · expires {date(item.expires_at)}</small><button className="text-link" disabled={busy} onClick={()=>void revokeInvite(item)}>{am?"ግብዣ ሻር":"Revoke invitation"}</button></div></article>)}
    <details className="staff-permission-details"><summary>{am?"ሙሉ የሚና እና ፈቃድ ሰንጠረዥ":"Role catalogue and permission matrix"}</summary>{roles.map(role=><article className="staff-role-definition" key={role.id}><strong>{role.code} · {role.scope}</strong><small>{role.description}</small><div className="staff-permission-list">{role.permissions.map(permission=><code key={permission}>{permission}</code>)}</div></article>)}</details><h4>{am?"የነባር መለያዎች":"Active staff assignments"}</h4>{users.map(user=><article className="staff-user-row" key={user.id}><div><strong>{user.display_name}</strong><small>{user.login_identifier} · {user.status}</small>{user.roles.map(role=><div className="staff-assignment" key={role.assignment_id}><span>{role.role_code} {role.organization_id?"· "+role.organization_id:"· Platform"}</span>{role.assignment_id&&user.id!==session.id&&<button className="text-link" disabled={busy} onClick={()=>void revoke(role.assignment_id!)}>{am?"ሻር":"Revoke"}</button>}</div>)}</div></article>)}</div>}
    {tab==="support"&&<StaffSupportWorkspace language={language}/>}
    {tab==="audit"&&<div className="audit-panel"><h3>{am?"የኦዲት ክስተቶች":"Redacted audit events"}</h3>{audit.map(item=><article className="scheduler-run" key={item.id}><strong>{item.event_type}</strong><span>{date(item.occurred_at)}</span><span>{item.actor_type}</span><span>{item.outcome}</span></article>)}</div>}
  </div></section>;
}
