import "@fontsource-variable/figtree";
import "./styles.css";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { EggLayer } from "./components/Eggs";
import { applyMotionPref, CoinLayer, MeshBackdrop } from "./components/Motion";
import { ToastProvider } from "./components/UI";
import { UpdateNotice } from "./components/UpdateNotice";
import { settleLook } from "./lib/theme";

settleLook();
applyMotionPref();
// A change of the animation setting in another tab of Groschen shows up here right away.
addEventListener("storage", (e) => {
  if (e.key === "groschen.motion") applyMotionPref();
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ToastProvider>
      <MeshBackdrop />
      <App />
      <CoinLayer />
      <EggLayer />
      <UpdateNotice />
    </ToastProvider>
  </StrictMode>,
);
