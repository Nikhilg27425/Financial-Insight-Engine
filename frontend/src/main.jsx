// main.jsx: This is the application entry point. It's the first file that runs. 
// Its job is to "mount" your App.jsx component into the index.html file. You won't touch this often.


import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./styles.css";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);

