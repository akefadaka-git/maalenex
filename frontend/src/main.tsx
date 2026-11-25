import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import PublicGeoMap from "./features/maps/PublicGeoMap";
import "./styles.css";

const Root = window.location.pathname === "/map" ? PublicGeoMap : App;

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode><Root /></React.StrictMode>,
);