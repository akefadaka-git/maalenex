import { useEffect, useMemo, useState } from "react";
import { Button, Badge } from "./components/ui";

type Language = "am" | "en";
type Props = { language: Language; pickup: string; destination: string };
type GeoState = "idle" | "requesting" | "granted" | "denied" | "unavailable" | "error" | "unsupported";
const nodes: Record<string,{x:number;y:number;am:string;en:string}> = {
  koybe:{x:112,y:170,am:"ኮይቤ",en:"Koybe"},
  jinka:{x:328,y:92,am:"ጂንካ",en:"Jinka"},
  maale:{x:210,y:264,am:"ማአሌ ወረዳ",en:"Maale Woreda"},
  sodo:{x:420,y:205,am:"ወላይታ ሶዶ",en:"Wolaita Sodo"}
};
const edges: Record<string,string> = { "koybe:jinka":"M112 170 Q205 80 328 92", "jinka:sodo":"M328 92 Q390 115 420 205", "koybe:maale":"M112 170 Q145 230 210 264", "maale:jinka":"M210 264 Q260 150 328 92" };
export function RouteMapPreview({language,pickup,destination}:Props){
 const [zoom,setZoom]=useState(1); const [geo,setGeo]=useState<GeoState>("idle"); const [online,setOnline]=useState(typeof navigator==="undefined"?true:navigator.onLine);
 const am=language==="am";
 useEffect(()=>{const on=()=>setOnline(true),off=()=>setOnline(false);window.addEventListener("online",on);window.addEventListener("offline",off);return()=>{window.removeEventListener("online",on);window.removeEventListener("offline",off);};},[]);
 const routeKey=useMemo(()=>edges[`${pickup}:${destination}`]?"${pickup}:${destination}":edges[`${destination}:${pickup}`]?"${destination}:${pickup}`:null,[pickup,destination]);
 const routePath=routeKey?edges[routeKey]:null;
 const requestLocation=()=>{
  if(!("geolocation" in navigator)){setGeo("unsupported");return;}
  setGeo("requesting");
  navigator.geolocation.getCurrentPosition(
   _p=>{setGeo("granted");},
   e=>setGeo(e.code===1?"denied":e.code===2?"unavailable":"error"),
   {enableHighAccuracy:false,timeout:10000,maximumAge:60000}
  );
 };
 const statusText=geo==="requesting"?(am?"የቦታ ፈቃድ በመጠየቅ ላይ…":"Requesting location permission…"):
  geo==="granted"?(am?"የመሣሪያዎ ቦታ በዚህ መሣሪያ ላይ ብቻ ታይቷል።":"Device location received locally; it is not sent to a server."):
  geo==="denied"?(am?"የቦታ ፈቃድ ተከልክሏል። በመሣሪያዎ ቅንብሮች ይፍቀዱ።":"Location permission was denied. You can allow it in device settings."):
  geo==="unavailable"?(am?"የመሣሪያ ቦታ አልተገኘም።":"Device location is currently unavailable."):
  geo==="unsupported"?(am?"ይህ አሳሽ የቦታ አገልግሎትን አይደግፍም።":"This browser does not support location access."):
  geo==="error"?(am?"የቦታ ጥያቄው ጊዜው አልፎበታል ወይም አልተሳካም።":"The location request timed out or failed."):
  (am?"አማራጭ ነው፤ ከታች በመጫን ብቻ ፈቃድ ይጠይቁ።":"Optional. Location is requested only when you tap the button.");
 return <section className="mn-map-panel" aria-label={am?"የመንገድ ካርታ ቅድመ እይታ":"Route map preview"}>
  <div className="mn-map-heading"><div><p className="mn-overline">{am?"የመንገድ እይታ":"ROUTE VISUALIZATION"}</p><h3>{am?"የመንገድ ካርታ":"Route map"}</h3></div><Badge tone="warning">{am?"ምሳሌያዊ ካርታ":"Schematic map"}</Badge></div>
  <div className="mn-map-frame">
   <div className="mn-map-canvas" role="img" aria-label={am?"በኮይቤ፣ ጂንካ፣ ማአሌ ወረዳ እና ወላይታ ሶዶ መካከል ምሳሌያዊ መንገድ":"Illustrative route between Koybe, Jinka, Maale Woreda and Wolaita Sodo"}>
    <svg viewBox="0 0 520 340" aria-hidden="true" style={{"--mn-map-zoom":zoom} as React.CSSProperties}>
     <defs><pattern id="mn-grid" width="26" height="26" patternUnits="userSpaceOnUse"><path d="M26 0H0V26" fill="none" stroke="currentColor" strokeOpacity=".08" strokeWidth="1"/></pattern></defs>
     <rect width="520" height="340" fill="url(#mn-grid)"/>
     <path d="M0 45 Q95 10 170 55 T330 45 T520 55 M0 305 Q120 250 220 300 T520 280 M40 0 Q85 100 35 190 T70 340 M470 0 Q410 100 480 180 T450 340" fill="none" stroke="currentColor" strokeOpacity=".10" strokeWidth="2"/>
     {Object.entries(edges).map(([key,path])=><path key={key} d={path} fill="none" stroke={routeKey===key||routeKey===key.split(":").reverse().join(":")?"#0D9A72":"#9AAEAA"} strokeOpacity={routeKey===key||routeKey===key.split(":").reverse().join(":")?1:.42} strokeWidth={routeKey===key||routeKey===key.split(":").reverse().join(":")?6:2} strokeLinecap="round" strokeDasharray={routeKey===key||routeKey===key.split(":").reverse().join(":")?"none":"5 7"}/>)}
     {Object.entries(nodes).map(([id,n])=><g key={id} transform={`translate(${n.x} ${n.y})`}><circle r={id===pickup||id===destination?13:7} fill={id===pickup?"#F5B82E":id===destination?"#0D9A72":"#71827B"} stroke="#fff" strokeWidth="3"/><circle r="19" fill="none" stroke={id===pickup?"#F5B82E":id===destination?"#0D9A72":"#71827B"} strokeOpacity=".35"/><text x="0" y="31" textAnchor="middle" fill="currentColor" fontSize="12" fontWeight="700">{am?n.am:n.en}</text></g>)}
    </svg>
    <div className="mn-map-zoom" aria-label={am?"የካርታ ማጉያ መቆጣጠሪያዎች":"Map zoom controls"}><Button size="small" variant="secondary" aria-label={am?"አጉላ":"Zoom in"} onClick={()=>setZoom(z=>Math.min(1.6,Number((z+.15).toFixed(2))))}>+</Button><span>{Math.round(zoom*100)}%</span><Button size="small" variant="secondary" aria-label={am?"አሳንስ":"Zoom out"} onClick={()=>setZoom(z=>Math.max(.7,Number((z-.15).toFixed(2))))}>−</Button><Button size="small" variant="quiet" onClick={()=>setZoom(1)}>{am?"ዳግም":"Reset"}</Button></div>
   </div>
  </div>
  <p className="mn-map-disclaimer">{am?"ይህ ምሳሌያዊ ስዕል ነው፤ ትክክለኛ የጂኦግራፊ መጠን፣ የመንገድ ዳታ፣ የትራፊክ ወይም የአሰሳ መረጃ አይደለም።":"Illustrative only—not geographically scaled and not live map, traffic, navigation, or verified road data."}</p>
  <div className="mn-map-status" role="status"><span className={online?"mn-status-dot":"mn-status-dot is-offline"}/><span>{online?(am?"መሣሪያው ከመስመር ላይ ጋር ተገናኝቷል":"Device is online"):(am?"ከመስመር ውጭ · የምሳሌ ካርታ ብቻ ይገኛል":"Offline · schematic preview only")}</span></div>
  {!online&&<p className="mn-map-fallback">{am?"የውጭ ካርታ ንጣፎች አይገኙም። የመንገድ ማሳያው በመሣሪያው ላይ ይቀጥላል።":"External map tiles are unavailable offline. The local schematic remains visible."}</p>}
  <div className="mn-location-permission"><div><strong>{am?"የመሣሪያ ቦታ":"Device location"}</strong><p>{statusText}</p></div><Button size="small" variant="secondary" onClick={requestLocation} disabled={geo==="requesting"}>{geo==="granted"?(am?"እንደገና አዘምን":"Refresh location"):(am?"ቦታን ፍቀድ":"Allow location")}</Button></div>
 </section>;
}
