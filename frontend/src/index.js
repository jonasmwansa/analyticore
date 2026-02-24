import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";

// 🔎 Load client logger only in development
if (process.env.NODE_ENV === "development") {
  require("@/debug/preview-logger");
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);