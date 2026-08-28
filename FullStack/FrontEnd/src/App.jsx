import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./components/LandingPage";
import Dashboard from "./Dashboard";
import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        {/* The Root Route (Antigravity Landing Page) */}
        <Route path="/" element={<LandingPage />} />

        {/* The Main Application Route */}
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
