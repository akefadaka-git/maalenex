import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import TrackingMap from "./features/tracking/TrackingMap";
import "./styles.css";

const Root = window.location.pathname === "/tracking-demo" ? TrackingMap : App;

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode><Root /></React.StrictMode>,
);
