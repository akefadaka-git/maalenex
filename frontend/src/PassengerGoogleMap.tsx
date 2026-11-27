import { useEffect, useRef, useState } from "react";
import type { PassengerLocation, PassengerRoute } from "./passenger-api";
type Language = "am" | "en";

type Props={locations:PassengerLocation[];routes:PassengerRoute[];originId:string;destinationId:string;language:Language;onSelectLocation:(id:string)=>void};
type LatLng={lat:number;lng:number};
type MapInstance={panTo:(point:LatLng)=>void;fitBounds:(bounds:unknown)=>void};
type MarkerInstance={addListener:(event:string,callback:()=>void)=>void};
type MapsApi={Map:new(element:HTMLElement,options:Record<string,unknown>)=>MapInstance;Marker:new(options:Record<string,unknown>)=>MarkerInstance;Polyline:new(options:Record<string,unknown>)=>{setMap:(map:MapInstance|null)=>void};LatLngBounds:new()=>{extend:(point:LatLng)=>void;isEmpty:()=>boolean}};
declare global{interface Window{google?:{maps:MapsApi}}}
let mapsLoader:Promise<MapsApi>|null=null;
function loadGoogleMaps(key:string):Promise<MapsApi>{
 if(window.google?.maps)return Promise.resolve(window.google.maps);
 if(mapsLoader)return mapsLoader;
 const loading=new Promise<MapsApi>((resolve,reject)=>{
  const existing=document.getElementById("maalenex-google-maps") as HTMLScriptElement|null;
  const script=existing??document.createElement("script");
  const finish=()=>{if(window.google?.maps)resolve(window.google.maps);else reject(new Error("Google Maps loaded without its JavaScript API."));};
  script.addEventListener("load",finish,{once:true});script.addEventListener("error",()=>reject(new Error("Google Maps could not be loaded. Check network access, API key restrictions and billing.")),{once:true});
  if(!existing){script.id="maalenex-google-maps";script.async=true;script.defer=true;script.src=`https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(key)}&v=weekly`;document.head.appendChild(script);}
 }).catch(error=>{mapsLoader=null;throw error;});
 mapsLoader=loading;
 return loading;
}
function validPoint(value:unknown):LatLng|null{if(!value||typeof value!=="object")return null;const p=value as {latitude?:unknown;longitude?:unknown};if(typeof p.latitude!=="number"||typeof p.longitude!=="number"||!Number.isFinite(p.latitude)||!Number.isFinite(p.longitude)||Math.abs(p.latitude)>90||Math.abs(p.longitude)>180)return null;return{lat:p.latitude,lng:p.longitude};}
function geometryPoints(route:PassengerRoute|undefined):LatLng[]{const coords=route?.geometry?.coordinates;if(!Array.isArray(coords))return[];return coords.flatMap(pair=>Array.isArray(pair)&&pair.length===2&&pair.every(n=>typeof n==="number"&&Number.isFinite(n))&&Math.abs(pair[1])<=90&&Math.abs(pair[0])<=180?[{lat:pair[1],lng:pair[0]}]:[]);}
export function PassengerGoogleMap({locations,routes,originId,destinationId,language,onSelectLocation}:Props){
 const host=useRef<HTMLDivElement>(null);const mapRef=useRef<MapInstance|null>(null);const selectLocationRef=useRef(onSelectLocation);const [status,setStatus]=useState<"loading"|"ready"|"missing-key"|"missing-data"|"offline"|"error">("loading");const [message,setMessage]=useState("");const [gpsMessage,setGpsMessage]=useState("");
 const key=(import.meta.env.VITE_GOOGLE_MAPS_API_KEY??"").trim();
 const selectedRoute=routes.find(route=>route.origin.id===originId&&route.destination.id===destinationId)||routes.find(route=>route.origin.id===destinationId&&route.destination.id===originId);
 const routePoints=geometryPoints(selectedRoute);
 useEffect(()=>{selectLocationRef.current=onSelectLocation;},[onSelectLocation]);
 useEffect(()=>{
  let active=true;const available=locations.map(location=>({location,point:validPoint(location.coordinates)})).filter((item):item is {location:PassengerLocation;point:LatLng}=>item.point!==null);
  if(!key){setStatus("missing-key");setMessage("Google Maps is not configured for this build. A restricted VITE_GOOGLE_MAPS_API_KEY is required.");return()=>{active=false;};}
  if(!navigator.onLine){setStatus("offline");setMessage("You are offline. Map tiles and current route information are unavailable.");return()=>{active=false;};}
  if(available.length===0&&routePoints.length===0){setStatus("missing-data");setMessage("Published locations do not yet contain verified coordinates, and no published route geometry is available. Ask an administrator to publish source-verified map data.");return()=>{active=false;};}
  setStatus("loading");
  loadGoogleMaps(key).then(maps=>{
   if(!active||!host.current)return;
   const initial=available[0]?.point??routePoints[0];
   const map=new maps.Map(host.current,{center:initial,zoom:8,mapTypeId:"roadmap",streetViewControl:false,mapTypeControl:false,fullscreenControl:true,clickableIcons:false,gestureHandling:"greedy"});mapRef.current=map;
   const bounds=new maps.LatLngBounds();available.forEach(({location,point})=>{bounds.extend(point);const marker=new maps.Marker({map,position:point,title:location.name,label:location.name});marker.addListener("click",()=>selectLocationRef.current(location.id));});
   if(routePoints.length>1){const line=new maps.Polyline({map,path:routePoints,geodesic:true,strokeColor:"#0b8f68",strokeOpacity:.95,strokeWeight:5});void line;routePoints.forEach(point=>bounds.extend(point));}
   if(!bounds.isEmpty())map.fitBounds(bounds);
   setStatus("ready");setMessage("");
  }).catch(error=>{if(active){setStatus("error");setMessage(error instanceof Error?error.message:"Google Maps failed to initialize.");}});
  return()=>{active=false;mapRef.current=null;};
 },[key,locations,routes,originId,destinationId,routePoints.length]);
 const locate=()=>{setGpsMessage("");if(!navigator.geolocation){setGpsMessage("Location is not supported by this WebView.");return;}navigator.geolocation.getCurrentPosition(position=>{mapRef.current?.panTo({lat:position.coords.latitude,lng:position.coords.longitude});setGpsMessage("Showing your device location. This is not driver tracking.");},error=>{setGpsMessage(error.code===1?"Location permission was denied. You can still select published locations manually.":error.code===2?"Your device location is unavailable.":"Location request timed out. Try again or choose a location manually.");},{enableHighAccuracy:true,timeout:10000,maximumAge:60000});};
 const am=language==="am";
 return <section className="passenger-map" data-map-status={status} aria-label={am?"የጉዞ ካርታ":"Passenger journey map"}>
  {status==="ready"&&<button className="map-gps-action" type="button" onClick={locate}>{am?"አሁን ያለሁበትን አሳይ":"Use my location"}</button>}
  <div className="passenger-map-canvas" ref={host} role="application" aria-label="Google Map" />
  {status!=="ready"&&<div className="map-state" role="status"><strong>{status==="loading"?(am?"ካርታው በመጫን ላይ…":"Loading Google Maps…"):status==="missing-key"?(am?"የካርታ ቁልፍ አልተዋቀረም":"Google Maps key not configured"):status==="missing-data"?(am?"የተረጋገጠ የካርታ መረጃ የለም":"Verified map data not published"):status==="offline"?(am?"ከመስመር ውጭ ነዎት":"Map unavailable offline"):"Google Maps unavailable"}</strong><p>{message}</p></div>}
  {selectedRoute&&selectedRoute.geometry_status!=="published"&&<div className="map-legend-note" role="status">{am?"የዚህ መስመር የተረጋገጠ ጂኦሜትሪ ገና አልታተመም።":"No verified route geometry is published for this selection; no straight-line route is drawn."}</div>}
  {gpsMessage&&<div className="map-legend-note" role="status">{gpsMessage}</div>}
  <div className="map-legend-note">{am?"የካርታ ምልክት ላይ ይጫኑ፤ የተመረጠው የመነሻ/መድረሻ ቁልፍ ይወስናል።":"Tap a map marker to assign it to the selected origin or destination field."}</div>
 </section>;
}
