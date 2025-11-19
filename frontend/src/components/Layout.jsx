import { useState, useEffect } from "react";
import Sidebar from "./Sidebar";

export default function Layout({ children }) {
  // Load sidebar state from localStorage, default to collapsed on mobile
  const [collapsed, setCollapsed] = useState(() => {
    const saved = localStorage.getItem("sidebarCollapsed");
    if (saved !== null) {
      return JSON.parse(saved);
    }
    // Default to collapsed on mobile screens
    return window.innerWidth < 768;
  });

  // Persist sidebar state to localStorage
  useEffect(() => {
    localStorage.setItem("sidebarCollapsed", JSON.stringify(collapsed));
  }, [collapsed]);

  // Handle window resize for responsive behavior
  useEffect(() => {
    const handleResize = () => {
      // Auto-collapse on mobile, restore saved state on desktop
      if (window.innerWidth < 768) {
        setCollapsed(true);
      } else {
        const saved = localStorage.getItem("sidebarCollapsed");
        if (saved !== null) {
          setCollapsed(JSON.parse(saved));
        }
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const toggleSidebar = () => {
    setCollapsed((prev) => !prev);
  };

  return (
    <div className="app-root">
      <Sidebar collapsed={collapsed} toggle={toggleSidebar} />
      <main className={`main-content ${collapsed ? "sidebar-collapsed" : ""}`}>
        {children}
      </main>
    </div>
  );
}
