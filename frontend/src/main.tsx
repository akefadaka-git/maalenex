import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import PublicGeoMap from "./features/maps/PublicGeoMap";
import InternalGeoMap from "./features/maps/InternalGeoMap";
import "./styles.css";

const path = window.location.pathname;
const Root = path === "/map/internal" ? InternalGeoMap : path === "/map" ? PublicGeoMap : App;

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode><Root /></React.StrictMode>,
);